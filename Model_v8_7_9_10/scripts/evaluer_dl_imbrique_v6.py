#!/usr/bin/env python3
"""
evaluer_dl_imbrique_v6.py (12 nov. 2026) : copie de evaluer_dl_imbrique_v5.py (INTACT) pour le corpus v15 ; seule difference : les fichiers de regles servant aux niveaux de source sont des parametres (--regles_mono, --regles_multi), par defaut les regles v15, au lieu de chemins v14 ecrits en dur.
Origine (v5, 2 nov. 2026) : copie de evaluer_dl_imbrique_v4.py (INTACT) pour le corpus v14 ; différences : option base « c35 » (configuration 35 fixée, sans recherche) et niveaux de source lus dans regles_v14_monogene.csv.
Original (v4) : évaluation IMBRIQUÉE du DL sur le corpus v13.
Pour chaque pli externe k : (a) configuration « choisie » = meilleur F1 macro de VALIDATION INTERNE de ce pli (essais de recherche_hp_dl_v4.py, aucune lecture du test) ;
(b) configuration de référence v3. Chacune est entraînée sur l'entraînement du pli (validation interne 10 % pour l'arrêt anticipé, comme train_dl_profil_v3.py), sur N graines,
puis évaluée sur le pli de test (protocole_commun_v10). Métriques globales et PAR NIVEAU DE SOURCE (CPIC / DPWG / FDA / FDA-etiquette).
L'ensemble final (138 familles) n'est pas lu.
Usage : python3 evaluer_dl_imbrique_v5.py --graines 5 --part 0 --parts 2 --quoi c35_cal --data ../data/corpus_v14/phenotype_drug_dataset_v14.csv --out ../results/dl_imbrique_v14
"""
import argparse, glob, json, os, sys, time
import numpy as np, pandas as pd, torch
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dl_coeur_v4 as dc, protocole_commun_v10 as pc


def niveau_par_medicament(f_mono='../data/regles_v15_monogene.csv',
                          f_multi='../data/regles_v15_multigene.csv'):
    r = pd.read_csv(f_mono); m = pd.read_csv(f_multi)
    s = r.drop_duplicates('medicament').set_index('medicament').source.to_dict()
    for med, src in m.drop_duplicates('medicament').set_index('medicament').source.items(): s.setdefault(med, src)
    return s


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--graines', type=int, default=5); ap.add_argument('--part', type=int, default=0); ap.add_argument('--parts', type=int, default=1)
    ap.add_argument('--quoi', required=True, help="base (choisie|v3) + options séparées par _ : onehot (entrée en catégories), cal (mise à l'échelle de la température sur la validation interne)"); ap.add_argument('--data', default='../data/corpus_v15/phenotype_drug_dataset_v15.csv'); ap.add_argument('--hp', default='../results/dl_hp_v13'); ap.add_argument('--regles_mono', default='../data/regles_v15_monogene.csv'); ap.add_argument('--regles_multi', default='../data/regles_v15_multigene.csv')
    ap.add_argument('--out', default='../results/dl_imbrique_v13'); a = ap.parse_args(); torch.set_num_threads(1); os.makedirs(a.out, exist_ok=True)
    d = dc.tableau(a.data); X, Y, pid, fam, y = d['X'], d['Y'], d['pid'], d['fam'], d['y']; K = len(d['classes']); ev = d['classes'].index('EVITER'); classes = d['classes']
    final, folds = pc.decouper(d['groups'], y); niv = niveau_par_medicament(a.regles_mono, a.regles_multi); drug_niv = np.array([niv[m] for m in d['meds']])
    C = json.load(open(os.path.join(a.hp, 'configs.json')))
    base = a.quoi.split('_')[0]; onehot = 'onehot' in a.quoi.split('_'); cal = 'cal' in a.quoi.split('_')
    E = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(a.hp, 'essais_part*.csv'))]) if base == 'choisie' else None
    rows = []; t0 = time.time()
    for k, (tr, te) in enumerate(folds):
        if base == 'choisie':
            e = E[E.pli == k + 1]; assert e.config.nunique() == len(C), 'recherche incomplète pour le pli %d' % (k + 1)
            ci = int(e.sort_values(['f1_val', 'config'], ascending=[False, True]).iloc[0].config)
        else: ci = 35 if base == 'c35' else 0   # v5 : « c35 » = configuration 35 FIXÉE (choisie sur v13 par recherche imbriquée), aucun nouveau réglage sur v14
        cfg = C[ci]; ptr = np.unique(pid[tr]); pte = np.unique(pid[te])
        ai, vi = next(GroupShuffleSplit(1, test_size=0.10, random_state=pc.GRAINE).split(ptr, groups=fam[ptr])); ap_, vp_ = ptr[ai], ptr[vi]
        if onehot:
            niv_ = [np.unique(X[ap_][:, j]) for j in range(X.shape[1])]
            S = lambda i: np.concatenate([(X[i][:, [j]] == niv_[j][None, :]).astype(np.float32) for j in range(X.shape[1])], 1)
        else:
            sc = StandardScaler().fit(X[ap_]); S = lambda i: sc.transform(X[i]).astype(np.float32)
        loc = {p: i for i, p in enumerate(pte)}
        for s in range(a.graines):
            if s % a.parts != a.part: continue
            m, h, bv = dc.entrainer(S(ap_), Y[ap_], S(vp_), Y[vp_], K, ev, cfg, pc.GRAINE + 100 * s + k)
            Pc = dc.probas(m, S(pte)); Tcal = 1.0
            if cal:
                from scipy.optimize import minimize_scalar
                Pv = dc.probas(m, S(vp_)); mv = Y[vp_] >= 0; lp = np.log(np.clip(Pv[mv], 1e-12, 1)); yv = Y[vp_][mv]
                def nll(T):
                    z = lp / T; z = z - z.max(-1, keepdims=True); q = np.exp(z); q /= q.sum(-1, keepdims=True); return -np.log(np.clip(q[np.arange(len(yv)), yv], 1e-12, 1)).mean()
                Tcal = float(minimize_scalar(nll, bounds=(0.05, 5.0), method='bounded').x)
                z = np.log(np.clip(Pc, 1e-12, 1)) / Tcal; z = z - z.max(-1, keepdims=True); Pc = np.exp(z); Pc /= Pc.sum(-1, keepdims=True)
            P = Pc[[loc[p] for p in pid[te]], d['drug_idx'][te]]
            np.savez_compressed(os.path.join(a.out, 'oof_%s_pli%d_graine%d.npz' % (a.quoi, k + 1, s)), ligne=te, proba=P.astype(np.float32), y=y[te])
            json.dump(h, open(os.path.join(a.out, 'courbe_%s_pli%d_graine%d.json' % (a.quoi, k + 1, s)), 'w'))
            r = dict(quoi=a.quoi, config=ci, pli=k + 1, graine=s, epoques=len(h), T_cal=round(Tcal, 3), f1_val_interne=round(bv, 4), **pc.metriques(y[te], P, classes))
            nv = drug_niv[d['drug_idx'][te]]
            for lvl in sorted(set(drug_niv)):
                mk = nv == lvl
                if mk.sum() and len(set(y[te][mk])) > 1: r['f1_macro_' + lvl] = pc.metriques(y[te][mk], P[mk], classes)['f1_macro']
            rows.append(r); print({k_: r[k_] for k_ in ('quoi', 'config', 'pli', 'graine', 'f1_macro', 'CER_strict')}, '%.0fs' % (time.time() - t0), flush=True)
            pd.DataFrame(rows).to_csv(os.path.join(a.out, 'resultats_%s_part%d.csv' % (a.quoi, a.part)), index=False)


if __name__ == '__main__':
    main()
