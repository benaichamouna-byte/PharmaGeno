#!/usr/bin/env python3
"""
recherche_hp_dl_v4.py : recherche aléatoire d'hyperparamètres du DL (Bergstra & Bengio 2012, JMLR 13:281-305, https://jmlr.org/papers/v13/bergstra12a.html), IMBRIQUÉE.
Pour chaque pli externe k (protocole_commun_v10, identique à v9) : une validation interne (15 % des familles de l'ENTRAÎNEMENT du pli) sert seule à comparer les configurations.
Le pli de test k et l'ensemble final (138 familles) ne sont JAMAIS lus ici. Configuration 0 = réglage v3 (référence). Critère : F1 macro de la validation interne.
Sortie : results/dl_hp_v13/essais_part<i>.csv (une ligne par (configuration, pli), reprise possible).
Usage : python3 recherche_hp_dl_v4.py --n 40 --part 0 --parts 2
"""
import argparse, os, sys, time, json
import numpy as np, pandas as pd, torch
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dl_coeur_v4 as dc, protocole_commun_v10 as pc

ESPACE = dict(couches=[1, 2, 3], largeur=[128, 256, 512, 1024], dropout=[0.1, 0.2, 0.3, 0.4, 0.5], bn=[True, False], act=['relu', 'gelu'], lr=[3e-4, 1e-3, 3e-3],
              wd=[0.0, 1e-5, 1e-4, 1e-3], lot=[32, 64, 128, 256], w_exp=[0.5, 0.75, 1.0], ev_x=[1.0, 2.0, 4.0], lissage=[0.0, 0.05])


def configs(n, graine=0):
    rng = np.random.RandomState(graine); L = [dict(dc.CFG_V3)]
    while len(L) < n:
        c = {k: v[rng.randint(len(v))] for k, v in ESPACE.items()}; c['patience'] = 25
        if c not in L: L.append(c)
    return L


ESPACE2 = dict(couches=[2, 3], largeur=[1024], dropout=[0.0, 0.05, 0.1, 0.2], bn=[False], act=['relu'], lr=[5e-4, 1e-3], wd=[1e-5, 1e-4], lot=[64], w_exp=[0.5], ev_x=[1.0, 2.0], lissage=[0.05, 0.1])


def configs_tour2(n, graine=1):
    """Tour 2 : recherche locale autour de la meilleure configuration du tour 1 (config 35 : 2 couches, 1024, sans BatchNorm, dropout 0,1, lissage 0,05), qui touchait le bord de l'espace."""
    rng = np.random.RandomState(graine); L = []
    while len(L) < n:
        c = {k: v[rng.randint(len(v))] for k, v in ESPACE2.items()}; c['patience'] = 25
        if c not in L: L.append(c)
    return L


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tour2', type=int, default=0, help='nombre de configurations du tour 2 ajoutées après les 40 du tour 1'); ap.add_argument('--n', type=int, default=40); ap.add_argument('--part', type=int, default=0); ap.add_argument('--parts', type=int, default=1)
    ap.add_argument('--data', default='../data/corpus_v13/phenotype_drug_dataset_v13.csv'); ap.add_argument('--out', default='../results/dl_hp_v13'); a = ap.parse_args()
    torch.set_num_threads(1); os.makedirs(a.out, exist_ok=True)
    d = dc.tableau(a.data); X, Y, pid, fam = d['X'], d['Y'], d['pid'], d['fam']; K = len(d['classes']); ev = d['classes'].index('EVITER')
    final, folds = pc.decouper(d['groups'], d['y'])
    fich = os.path.join(a.out, 'essais_part%d.csv' % a.part); deja = set()
    if os.path.exists(fich): R = pd.read_csv(fich); deja = set(zip(R.config, R.pli))
    C = configs(a.n) + (configs_tour2(a.tour2) if a.tour2 else []); json.dump(C, open(os.path.join(a.out, 'configs.json'), 'w'), indent=1)
    t0 = time.time()
    for ci, cfg in enumerate(C):
        if ci % a.parts != a.part: continue
        for k, (tr, te) in enumerate(folds):
            if (ci, k + 1) in deja: continue
            ptr = np.unique(pid[tr]); ai, vi = next(GroupShuffleSplit(1, test_size=0.15, random_state=pc.GRAINE + 7).split(ptr, groups=fam[ptr])); ap_, vp_ = ptr[ai], ptr[vi]
            sc = StandardScaler().fit(X[ap_]); S = lambda i: sc.transform(X[i]).astype(np.float32)
            t = time.time(); m, h, b = dc.entrainer(S(ap_), Y[ap_], S(vp_), Y[vp_], K, ev, cfg, pc.GRAINE + 1000 + ci)
            pd.DataFrame([dict(config=ci, pli=k + 1, f1_val=round(b, 5), epoques=len(h), perte_fin=round(h[-1][1], 4), secondes=round(time.time() - t, 1), **cfg)]).to_csv(fich, mode='a', header=not os.path.exists(fich), index=False)
            print('config %d pli %d F1val %.4f (%d ép, %.0fs) | total %.0fs' % (ci, k + 1, b, len(h), time.time() - t, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
