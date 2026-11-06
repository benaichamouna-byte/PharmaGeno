#!/usr/bin/env python3
"""
evaluer_arbres_imbrique_v1.py (4 nov. 2026) : évaluation IMBRIQUÉE de XGBoost ou de la forêt aléatoire sur le corpus v14, SYMÉTRIQUE de evaluer_dl_imbrique_v5.py (option « choisie »).
Pour chaque pli externe k : configuration « choisie » = meilleur F1 macro de VALIDATION INTERNE de ce pli (recherche_hp_arbres_v1.py ; égalité -> plus petit indice) ; « ref » = configuration 0 (réglage de référence).
Entraînée sur l'entraînement du pli (validation interne 10 % des familles, GroupShuffleSplit GRAINE, comme le DL), 5 graines (GRAINE + 100*s + k, comme le DL), calibration par température sur la validation interne,
puis évaluée sur le pli de test (protocole_commun_v10). Métriques globales et PAR NIVEAU DE SOURCE. L'ensemble final (138 familles) n'est pas lu.
Sorties : <out>/oof_<quoi>_pli<k>_graine<s>.npz (ligne, proba calibrée, proba_brute, y) ; <out>/resultats_<quoi>_part<i>.csv.
Usage (depuis scripts/) : python3 evaluer_arbres_imbrique_v1.py --modele xgb --quoi choisie_cal --graines 5 --hp ../results/hp_arbres_v14_xgb --out ../results/eval_arbres_v14_xgb --threads 2
"""
import argparse, json, os, sys, time
import numpy as np, pandas as pd
from sklearn.metrics import f1_score
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dl_coeur_v4 as dc, protocole_commun_v10 as pc, arbres_coeur_v1 as ac
from evaluer_dl_imbrique_v5 import niveau_par_medicament


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--modele', choices=['xgb', 'rf'], required=True); ap.add_argument('--quoi', required=True, help='choisie|ref + option _cal')
    ap.add_argument('--graines', type=int, default=5); ap.add_argument('--part', type=int, default=0); ap.add_argument('--parts', type=int, default=1); ap.add_argument('--threads', type=int, default=0)
    ap.add_argument('--data', default='../data/corpus_v14/phenotype_drug_dataset_v14.csv'); ap.add_argument('--hp', default=None); ap.add_argument('--out', required=True); ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); nj = a.threads or (os.cpu_count() or 1)
    base = a.quoi.split('_')[0]; cal = 'cal' in a.quoi.split('_')
    d = dc.tableau(a.data); y = d['y']; K = len(d['classes']); ev = d['classes'].index('EVITER'); classes = d['classes']; X = ac.lignes_arbres(d)
    final, folds = pc.decouper(d['groups'], y); niv = niveau_par_medicament(); drug_niv = np.array([niv[m] for m in d['meds']])
    C = ac.configs(a.modele, 40)
    if base == 'choisie':
        assert json.load(open(os.path.join(a.hp, 'configs.json'))) == C, 'configs.json de la recherche différent des configurations attendues'
        E = pd.concat([pd.read_csv(f) for f in sorted(os.path.join(a.hp, x) for x in os.listdir(a.hp) if x.startswith('essais_part'))])
    rows = []; t0 = time.time()
    if a.smoke: folds = folds[:1]
    for k, (tr, te) in enumerate(folds):
        if base == 'choisie':
            e = E[E.pli == k + 1]; assert e.config.nunique() == len(C), 'recherche incomplète pour le pli %d' % (k + 1)
            ci = int(e.sort_values(['f1_val', 'config'], ascending=[False, True]).iloc[0].config)
        else: ci = 0
        cfg = C[ci]; trn, val = ac.decoupe_interne(d, tr, 0.10, pc.GRAINE)
        if a.smoke: trn, val, te = trn[::20], val[::20], te[::20]
        w = ac.poids_lignes(y[trn], K, ev, cfg['w_exp'], cfg['ev_x'])
        for s in range(a.graines):
            if s % a.parts != a.part: continue
            graine = pc.GRAINE + 100 * s + k; t = time.time()
            if a.modele == 'xgb':
                b, n_arbres, f1v = ac.entrainer_xgb(X[trn], y[trn], w, X[val], y[val], K, cfg, graine, nj)
                Pv = ac.probas_xgb(b, n_arbres, X[val]); Pt = ac.probas_xgb(b, n_arbres, X[te])
            else:
                m = ac.entrainer_rf(X[trn], y[trn], w, cfg, graine, nj); n_arbres = ac.N_ARBRES_RF
                Pv = m.predict_proba(X[val]).astype(np.float64); Pt = m.predict_proba(X[te]).astype(np.float64); f1v = float(f1_score(y[val], Pv.argmax(1), average='macro'))
            T = ac.temperature(Pv, y[val]) if cal else 1.0; Pc = ac.appliquer_temperature(Pt, T) if cal else Pt
            if a.smoke: print('SMOKE pli %d graine %d : %.0f s, %d arbres, T=%.3f' % (k + 1, s, time.time() - t, n_arbres, T), flush=True); continue
            np.savez_compressed(os.path.join(a.out, 'oof_%s_pli%d_graine%d.npz' % (a.quoi, k + 1, s)), ligne=te, proba=Pc.astype(np.float32), proba_brute=Pt.astype(np.float32), y=y[te])
            r = dict(modele=a.modele, quoi=a.quoi, config=ci, pli=k + 1, graine=s, arbres=n_arbres, T_cal=round(T, 3), f1_val_interne=round(f1v, 4), secondes=round(time.time() - t, 1), **pc.metriques(y[te], Pc, classes))
            rb = pc.metriques(y[te], Pt, classes); r.update(logloss_brute=rb['logloss'], ECE_brute=rb['ECE'])
            nv = drug_niv[d['drug_idx'][te]]
            for lvl in sorted(set(drug_niv)):
                mk = nv == lvl
                if mk.sum() and len(set(y[te][mk])) > 1: r['f1_macro_' + lvl] = pc.metriques(y[te][mk], Pc[mk], classes)['f1_macro']
            rows.append(r); print({k_: r[k_] for k_ in ('modele', 'quoi', 'config', 'pli', 'graine', 'arbres', 'f1_macro', 'CER_strict')}, '%.0fs' % (time.time() - t0), flush=True)
            pd.DataFrame(rows).to_csv(os.path.join(a.out, 'resultats_%s_part%d.csv' % (a.quoi, a.part)), index=False)


if __name__ == '__main__':
    main()
