#!/usr/bin/env python3
"""
recherche_hp_arbres_v1.py (4 nov. 2026) : recherche aléatoire IMBRIQUÉE d'hyperparamètres de XGBoost ou de la forêt aléatoire sur le corpus v14, SYMÉTRIQUE de recherche_hp_dl_v4.py
(Bergstra & Bengio 2012, JMLR 13:281-305, https://jmlr.org/papers/v13/bergstra12a.html). Mêmes 40 configurations (la 0 = réglage de référence), mêmes 5 plis externes (protocole_commun_v10),
même validation interne (15 % des familles de l'ENTRAÎNEMENT du pli, graine GRAINE+7, découpage fait sur les profils), même critère : F1 macro de la validation interne.
Le pli de test et l'ensemble final (138 familles) ne sont JAMAIS lus ici.
Sortie : <out>/essais_part<i>.csv (une ligne par (configuration, pli), reprise possible) et <out>/configs.json.
Usage (depuis scripts/) : python3 recherche_hp_arbres_v1.py --modele xgb --part 0 --parts 1 --data ../data/corpus_v14/phenotype_drug_dataset_v14.csv --out ../results/hp_arbres_v14_xgb --threads 2
         --smoke : essai de fonctionnement (une fraction des familles, 2 configurations, 1 pli) ; n'écrit que dans --out.
"""
import argparse, json, os, sys, time
import numpy as np, pandas as pd
from sklearn.metrics import f1_score
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dl_coeur_v4 as dc, protocole_commun_v10 as pc, arbres_coeur_v1 as ac


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--modele', choices=['xgb', 'rf'], required=True); ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--part', type=int, default=0); ap.add_argument('--parts', type=int, default=1); ap.add_argument('--threads', type=int, default=0)
    ap.add_argument('--data', default='../data/corpus_v14/phenotype_drug_dataset_v14.csv'); ap.add_argument('--out', required=True); ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); nj = a.threads or (os.cpu_count() or 1)
    d = dc.tableau(a.data); y = d['y']; K = len(d['classes']); ev = d['classes'].index('EVITER'); X = ac.lignes_arbres(d)
    final, folds = pc.decouper(d['groups'], y)
    C = ac.configs(a.modele, a.n); json.dump(C, open(os.path.join(a.out, 'configs.json'), 'w'), indent=1)
    fich = os.path.join(a.out, 'essais_part%d.csv' % a.part); deja = set()
    if os.path.exists(fich) and not a.smoke: R = pd.read_csv(fich); deja = set(zip(R.config, R.pli))
    if a.smoke: C = C[:2]; folds = folds[:1]
    t0 = time.time()
    for ci, cfg in enumerate(C):
        if ci % a.parts != a.part: continue
        for k, (tr, te) in enumerate(folds):
            if (ci, k + 1) in deja: continue
            trn, val = ac.decoupe_interne(d, tr, 0.15, pc.GRAINE + 7)
            if a.smoke: trn, val = trn[::20], val[::20]
            w = ac.poids_lignes(y[trn], K, ev, cfg['w_exp'], cfg['ev_x']); t = time.time(); graine = pc.GRAINE + 1000 + ci
            if a.modele == 'xgb':
                b, n_arbres, f1v = ac.entrainer_xgb(X[trn], y[trn], w, X[val], y[val], K, cfg, graine, nj)
            else:
                m = ac.entrainer_rf(X[trn], y[trn], w, cfg, graine, nj); n_arbres = ac.N_ARBRES_RF; f1v = float(f1_score(y[val], m.predict(X[val]), average='macro'))
            lig = dict(config=ci, pli=k + 1, f1_val=round(f1v, 5), arbres=n_arbres, secondes=round(time.time() - t, 1), n_train=len(trn), n_val=len(val), **cfg)
            if a.smoke: print('SMOKE config %d pli %d : %.0f s, %d arbres' % (ci, k + 1, time.time() - t, n_arbres), flush=True); continue
            pd.DataFrame([lig]).to_csv(fich, mode='a', header=not os.path.exists(fich), index=False)
            print('config %d pli %d F1val %.4f (%d arbres, %.0fs) | total %.0fs' % (ci, k + 1, f1v, n_arbres, time.time() - t, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
