#!/usr/bin/env python3
"""
importance_genes_dl_v1.py : quels gènes le DL utilise-t-il réellement pour chaque médicament ?

Méthode (inférence seule, aucun entraînement) : importance par permutation (Fisher, Rudin, Dominici 2019, arXiv:1801.01489).
Pour chaque médicament m et chaque gène g : on remplace la valeur de g (et son indicateur d'absence <g>_manquant s'il existe) par celle d'un autre profil tiré au hasard,
on laisse tous les autres gènes inchangés, et on mesure le changement de la réponse du DL :
  - dTV   : variation totale moyenne des probabilités (0,5 * somme |P_perm - P_orig| sur les 4 classes) ;
  - dAct  : part des profils dont l'action prédite change.
On compare ensuite les gènes les plus importants pour le DL aux gènes de la règle CPIC du médicament (domaine_v8.json : 'genes').
Les poids d'attention du modèle ne sont PAS utilisés comme explication (Jain et Wallace 2019, arXiv:1902.10186).

Limites déclarées : les profils sont ceux de l'entraînement (le modèle les a vus) : on mesure une sensibilité, pas une exactitude. Les lignes de l'ensemble final sont exclues
(protocole_commun_v8.decouper) et ne sont pas lues. Une permutation peut créer une combinaison rare : l'importance mesure la sensibilité du modèle, pas un effet biologique.
Usage : python3 importance_genes_dl_v1.py --data ../data/phenotype_drug_dataset_v7.csv --fp <drug_fingerprints_v2.pkl> --modeles ../results/resultats_final_v8 --domaine ../data/domaine_v8.json --sortie ../results
"""
import argparse, json, os
import numpy as np, pandas as pd
import protocole_commun_v8 as pc
from moteur_v8 import MoteurPGx


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'fp', 'modeles', 'domaine', 'sortie'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--n_profils', type=int, default=300); ap.add_argument('--repetitions', type=int, default=3); ap.add_argument('--graine', type=int, default=11)
    ap.add_argument('--mono', default='../data/regles_v7_monogene.csv'); ap.add_argument('--multi', default='../data/regles_v2_corrigees_multigene_v7.csv')
    a = ap.parse_args()
    d = pc.charger(a.data, a.fp); final, _ = pc.decouper(d['groups'], d['y']); garde = np.setdiff1d(np.arange(len(d['y'])), final)
    M = MoteurPGx(a.modeles, a.domaine, a.mono, a.multi, avec_xgb=False)
    assert d['genes'] == M.features, 'variables du corpus != variables du modèle'
    df, G = d['df'], d['G']; feats = M.features; rng = np.random.RandomState(a.graine)
    pool = G[garde]                                                     # profils disponibles pour le tirage (ensemble final exclu)
    genes = M.genes_modele; colg = {g: [feats.index(g)] + ([feats.index(g + '_manquant')] if g + '_manquant' in feats else []) for g in genes}
    lignes = []
    for m in sorted(M.dom):
        dm = M.dom[m]
        if not dm['dans_modele']: continue
        idx = garde[(df.drug.values[garde] == m)]
        if len(idx) == 0: continue
        idx = rng.choice(idx, size=min(a.n_profils, len(idx)), replace=False)
        X = G[idx]; noms = [m] * len(idx); P0, _ = M.probas(X, noms); A0 = P0.argmax(1)
        for g in genes:
            tv, ch = [], []
            for _r in range(a.repetitions):
                Xp = X.copy(); src = pool[rng.randint(0, len(pool), size=len(idx))]
                for c in colg[g]: Xp[:, c] = src[:, c]
                P1, _ = M.probas(Xp, noms)
                tv.append(0.5 * np.abs(P1 - P0).sum(1).mean()); ch.append((P1.argmax(1) != A0).mean())
            lignes.append(dict(medicament=m, gene=g, n=len(idx), dTV=float(np.mean(tv)), dAct=float(np.mean(ch)), gene_cpic=g in dm['genes'],
                               depend_du_genotype=dm['depend_du_genotype'], classes_vues='|'.join(dm['classes_vues'])))
    R = pd.DataFrame(lignes); os.makedirs(a.sortie, exist_ok=True)
    R.to_csv(os.path.join(a.sortie, 'importance_genes_dl_v1_par_gene.csv'), index=False)
    res = []
    for m, g in R.groupby('medicament'):
        g = g.sort_values('dTV', ascending=False); k = int(g.gene_cpic.sum()); tot = g.dTV.sum()
        top = list(g.gene.head(max(k, 1))); cp = list(g[g.gene_cpic].gene)
        res.append(dict(medicament=m, depend_du_genotype=bool(g.depend_du_genotype.iloc[0]), genes_cpic='|'.join(cp), top_dl='|'.join(g.gene.head(3)),
                        importance_totale=round(tot, 4), part_sur_genes_cpic=round(float(g[g.gene_cpic].dTV.sum() / tot), 3) if tot > 1e-9 else None,
                        top_k_identique_cpic=bool(set(top) == set(cp)), k=k, dTV_max=round(float(g.dTV.max()), 4)))
    S = pd.DataFrame(res).sort_values(['depend_du_genotype', 'part_sur_genes_cpic'], ascending=[False, False])
    S.to_csv(os.path.join(a.sortie, 'importance_genes_dl_v1_par_medicament.csv'), index=False)
    dep = S[S.depend_du_genotype]; seuil_info = 0.05
    inf = dep[dep.importance_totale >= seuil_info]
    resume = dict(medicaments=len(S), dependants_du_genotype=len(dep), avec_importance_totale_au_moins_0_05=len(inf),
                  top_k_identique_cpic_parmi_dependants=int(dep.top_k_identique_cpic.sum()),
                  part_moyenne_sur_genes_cpic_parmi_dependants_informatifs=float(inf.part_sur_genes_cpic.astype(float).mean()) if len(inf) else None,
                  part_mediane_sur_genes_cpic_parmi_dependants_informatifs=float(inf.part_sur_genes_cpic.astype(float).median()) if len(inf) else None,
                  independants_du_genotype=int((~S.depend_du_genotype).sum()), n_profils_par_medicament=a.n_profils, repetitions=a.repetitions, graine=a.graine)
    json.dump(resume, open(os.path.join(a.sortie, 'importance_genes_dl_v1_resume.json'), 'w'), indent=1)
    print(json.dumps(resume, indent=1)); print(S.to_string(index=False))


if __name__ == '__main__':
    main()
