#!/usr/bin/env python3
"""
modele_final_v7.py : entraîne les modèles RETENUS sur toutes les lignes de validation croisée (les ~90 %) et les évalue UNE SEULE FOIS
sur l'ensemble final (138 familles, jamais utilisé jusqu'ici ni pour entraîner, ni pour régler, ni pour choisir).

Modèles retenus (réglages identiques à ceux de la validation croisée, aucun réglage ici) :
  dl_film_id : DL, architecture film, médicament décrit par un identifiant (moteur de l'application)
  xgb_id     : XGBoost, identifiant (second avis dans l'application)
  rf_id      : Random Forest, identifiant (pour compléter la comparaison DL / XGBoost / RF)
Entraînement : validation interne = 10 % des familles de l'ensemble d'entraînement (arrêt anticipé), poids de classes, graine 42.

GARDE-FOU : un fichier verrou (verrou_<modèle>.txt) est créé avant la première lecture de l'ensemble final. Si le verrou existe,
le script REFUSE de réévaluer ce modèle : l'ensemble final ne sert qu'une fois par modèle.
Sorties : modele_final_v7_<modèle>_resultats.json (métriques, intervalle de confiance à 95 % par rééchantillonnage des familles, matrice de confusion),
          modele_final_v7_<modèle>_final.npz (probabilités sur l'ensemble final), fichiers du modèle pour l'application
          (DL : .pt avec gènes, classes, médicaments, normalisation ; XGBoost : .json + _meta.json).
Usage : python3 modele_final_v7.py --data phenotype_drug_dataset_v3_croise.csv --fp drug_fingerprints_v2.pkl --out resultats_final_v7
"""
import argparse, json, os, time
import numpy as np, pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, f1_score, recall_score
import protocole_commun as pc
import train_dl_v7b as dl

MODELES = ['dl_film_id', 'xgb_id', 'rf_id']


def intervalle(y, P, fams, classes, B=1000, graine=pc.GRAINE):
    """IC 95 % par rééchantillonnage des FAMILLES (un patient et ses lignes restent ensemble)."""
    rng = np.random.RandomState(graine); ev = classes.index('EVITER'); K = len(classes)
    idx = {f: np.where(fams == f)[0] for f in np.unique(fams)}; keys = list(idx); pred = P.argmax(1); f1s, cers = [], []
    for _ in range(B):
        ch = np.concatenate([idx[keys[i]] for i in rng.randint(0, len(keys), len(keys))])
        f1s.append(f1_score(y[ch], pred[ch], average='macro'))
        rec = recall_score(y[ch], pred[ch], average=None, labels=range(K), zero_division=0); cers.append(1 - rec[ev])
    q = lambda v: [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]
    return q(f1s), q(cers)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True); ap.add_argument('--fp', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--smoke', action='store_true'); ap.add_argument('--modeles', nargs='+', default=MODELES, choices=MODELES)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); nj = os.cpu_count() or 1
    import torch; torch.set_num_threads(nj)
    d = pc.charger(a.data, a.fp, familles_smoke=0.25 if a.smoke else None)
    df, genes, y, classes, G, groups, meds = d['df'], d['genes'], d['y'], d['classes'], d['G'], d['groups'], d['meds']
    K = len(classes); ID = np.eye(len(meds), dtype=np.float32)[d['drug_idx']]
    final, folds = pc.decouper(groups, y); cv = np.sort(np.concatenate([te for _, te in folds]))
    gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE); ia, iv = next(gss.split(cv, groups=groups[cv])); trn, val = cv[ia], cv[iv]
    assert not (set(groups[final]) & set(groups[cv])), 'fuite : famille de l\'ensemble final présente dans l\'entraînement'
    w = len(trn) / (K * np.maximum(np.bincount(y[trn], minlength=K).astype(float), 1)); sw = w[y[trn]]
    sc = StandardScaler().fit(G[trn]); S = lambda ix: sc.transform(G[ix]).astype(np.float32)
    print('Entraînement : %d lignes | validation interne : %d | ensemble final : %d lignes, %d familles' % (len(trn), len(val), len(final), len(set(groups[final]))))
    for nom in a.modeles:
        verrou = os.path.join(a.out, 'verrou_%s.txt' % nom)
        if os.path.exists(verrou):
            print('REFUS : %s a déjà été évalué sur l\'ensemble final (%s). Une seule évaluation par modèle.' % (nom, verrou)); continue
        t0 = time.time()
        if nom == 'dl_film_id':
            model, hist, bv = dl.entrainer(S(trn), ID[trn], y[trn], S(val), ID[val], y[val], K, 2 if a.smoke else 60, pc.GRAINE, w, 'film')
            open(verrou, 'w').write('évalué le %s\n' % time.strftime('%Y-%m-%d %H:%M:%S'))   # verrou AVANT de lire l'ensemble final
            P = dl.predire(model, S(final), ID[final])
            torch.save(dict(state_dict=model.state_dict(), arch='film', genes=genes, classes=classes, medicaments=meds,
                            scaler_mean=sc.mean_.tolist(), scaler_scale=sc.scale_.tolist(), n_genes=len(genes), fp_dim=len(meds)),
                       os.path.join(a.out, 'modele_final_v7_dl_film_id.pt'))
            info = dict(epoques=len(hist), f1_val_interne=round(bv, 4))
        else:
            X = np.hstack([G, ID]).astype(np.float32)
            if nom == 'xgb_id':
                from xgboost import XGBClassifier
                m = XGBClassifier(objective='multi:softprob', num_class=K, n_estimators=30 if a.smoke else 1000, learning_rate=0.1, max_depth=6, tree_method='hist',
                                  early_stopping_rounds=20, eval_metric='mlogloss', n_jobs=nj, random_state=pc.GRAINE, verbosity=0)
                m.fit(X[trn], y[trn], sample_weight=sw, eval_set=[(X[val], y[val])], verbose=False); info = dict(arbres=int(m.best_iteration) + 1)
                m.save_model(os.path.join(a.out, 'modele_final_v7_xgb_id.json'))
                json.dump(dict(genes=genes, classes=classes, medicaments=meds), open(os.path.join(a.out, 'modele_final_v7_xgb_id_meta.json'), 'w'), ensure_ascii=False)
            else:
                from sklearn.ensemble import RandomForestClassifier
                m = RandomForestClassifier(n_estimators=40 if a.smoke else 500, max_features='sqrt', n_jobs=nj, random_state=pc.GRAINE)
                m.fit(X[trn], y[trn], sample_weight=sw); info = dict(arbres=m.n_estimators)
            open(verrou, 'w').write('évalué le %s\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
            P = np.zeros((len(final), K), dtype=np.float32); P[:, m.classes_.astype(int)] = m.predict_proba(X[final])
        met = pc.metriques(y[final], P, classes); ic_f1, ic_cer = intervalle(y[final], P, groups[final], classes)
        cm = confusion_matrix(y[final], P.argmax(1), labels=range(K)).tolist()
        res = dict(modele=nom, ensemble='final (jamais utilisé avant)', n_lignes=int(len(final)), n_familles=int(len(set(groups[final]))), **info, metriques=met,
                   ic95_f1_macro=ic_f1, ic95_CER_strict=ic_cer, classes=classes, matrice_confusion_lignes_vraies_colonnes_predites=cm, genes=genes)
        json.dump(res, open(os.path.join(a.out, 'modele_final_v7_%s_resultats.json' % nom), 'w'), indent=1, ensure_ascii=False)
        np.savez_compressed(os.path.join(a.out, 'modele_final_v7_%s_final.npz' % nom), proba=P, y=y[final], ligne=final, drug=df.drug.values[final].astype(str))
        print('RÉSULTAT FINAL %s : F1 macro = %.4f (IC95 %s) | CER strict = %.4f (IC95 %s) | ECE = %.4f | %.0fs' % (
            nom, met['f1_macro'], ic_f1, met['CER_strict'], ic_cer, met['ECE'], time.time() - t0), flush=True)
    print('Fichiers écrits dans', a.out)


if __name__ == '__main__':
    main()
