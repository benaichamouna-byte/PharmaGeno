#!/usr/bin/env python3
"""
test_invariance_genes_v8.py : le DL (et XGBoost) changent-ils leur réponse quand on modifie des gènes qui NE gouvernent PAS le médicament ?
Pour un médicament, seuls les gènes cités par ses règles (domaine_v8.json : 'genes') devraient compter. Test : pour chaque (profil, médicament), on remplace les valeurs de tous les AUTRES gènes
(et leurs indicateurs d'absence) par celles d'un autre profil tiré au hasard, et on mesure le changement de la prédiction. Aucun entraînement ; inférence seule.
Limite : les profils sont ceux de l'entraînement (les modèles les ont vus) ; on mesure une sensibilité, pas une exactitude. L'ensemble final n'est pas lu (le corpus complet est chargé,
mais les lignes de l'ensemble final sont exclues avec protocole_commun_v8.decouper).
Usage : python3 test_invariance_genes_v8.py --data corpus_v7/phenotype_drug_dataset_v7.csv --fp drug_fingerprints_v2.pkl --modeles resultats_final_v8 --domaine domaine_v8.json --n_profils 300
"""
import argparse, json
import numpy as np, pandas as pd
import protocole_commun_v8 as pc
from moteur_v8 import MoteurPGx


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'fp', 'modeles', 'domaine'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--n_profils', type=int, default=300); ap.add_argument('--graine', type=int, default=7)
    a = ap.parse_args()
    d = pc.charger(a.data, a.fp); final, _ = pc.decouper(d['groups'], d['y']); garde = np.setdiff1d(np.arange(len(d['y'])), final)
    M = MoteurPGx(a.modeles, a.domaine, 'corpus_v7/regles_v7_monogene.csv', 'regles_v2_corrigees_multigene_v7.csv')
    assert d['genes'] == M.features, 'variables du corpus != variables du modèle'
    df = d['df']; G = d['G']; rng = np.random.RandomState(a.graine)
    sample_id = df.sample_id.values if 'sample_id' in df.columns else None
    # un vecteur de variables par profil (hors ensemble final)
    prof_ids = np.unique(sample_id[garde]); choix = rng.choice(prof_ids, min(a.n_profils, len(prof_ids)), replace=False)
    premier = {s: garde[np.where(sample_id[garde] == s)[0][0]] for s in prof_ids}
    V = {s: G[premier[s]] for s in prof_ids}
    col = {f: i for i, f in enumerate(M.features)}
    lignes = []
    for m in sorted(M.dom):
        dm = M.dom[m]
        if not dm['dans_modele'] or not dm['depend_du_genotype']: continue
        req = set(dm['genes']); autres = [f for f in M.features if f.replace('_manquant', '') not in req]
        idx = [col[f] for f in autres]
        X0, X1 = [], []
        for s in choix:
            v = V[s].copy(); t = V[rng.choice(prof_ids)]; w = v.copy(); w[idx] = t[idx]
            X0.append(v); X1.append(w)
        P0, Q0 = M.probas(np.array(X0), [m] * len(X0)); P1, Q1 = M.probas(np.array(X1), [m] * len(X1))
        ev = M.classes.index('EVITER')
        lignes.append(dict(medicament=m, n=len(X0), n_genes_requis=len(req),
                           dl_action_change=float((P0.argmax(1) != P1.argmax(1)).mean()), dl_conf_change_moy=float(np.abs(P0.max(1) - P1.max(1)).mean()), dl_dP_EVITER_max=float(np.abs(P0[:, ev] - P1[:, ev]).max()),
                           xgb_action_change=float((Q0.argmax(1) != Q1.argmax(1)).mean()), xgb_conf_change_moy=float(np.abs(Q0.max(1) - Q1.max(1)).mean()), xgb_dP_EVITER_max=float(np.abs(Q0[:, ev] - Q1[:, ev]).max())))
    R = pd.DataFrame(lignes); R.to_csv('test_invariance_genes_v8_par_medicament.csv', index=False)
    w = R.n
    res = {k: float(np.average(R[k], weights=w)) for k in ('dl_action_change', 'dl_conf_change_moy', 'xgb_action_change', 'xgb_conf_change_moy')}
    res.update(medicaments=int(len(R)), profils=int(len(choix)), dl_dP_EVITER_max=float(R.dl_dP_EVITER_max.max()), xgb_dP_EVITER_max=float(R.xgb_dP_EVITER_max.max()),
               dl_medicaments_avec_changement_action=int((R.dl_action_change > 0).sum()), xgb_medicaments_avec_changement_action=int((R.xgb_action_change > 0).sum()))
    json.dump(res, open('test_invariance_genes_v8_resume.json', 'w'), indent=1); print(json.dumps(res, indent=1))
    print(R.sort_values('dl_action_change', ascending=False).head(12).to_string(index=False))

if __name__ == '__main__': main()
