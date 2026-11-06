#!/usr/bin/env python3
"""
comparaison_equitable_v14_v1.py (4 nov. 2026) : analyse de la comparaison ÉQUITABLE DL / XGBoost / forêt aléatoire sur le corpus v14 (protocole écrit et haché AVANT tout résultat :
Protocole_comparaison_equitable_DL_XGB_RF_v14_4nov2026.md). Aucun modèle n'est entraîné ici : lecture des prédictions hors-pli (oof_<quoi>_pli<k>_graine<s>.npz) des trois bras.
Mêmes lignes de test pour les trois modèles (vérifié) ; l'ensemble final (138 familles) n'est PAS lu (vérifié).

Statistique principale (fixée dans le protocole) : pour chaque modèle, mesure = MOYENNE SUR LES 5 GRAINES de la mesure calculée sur l'ensemble des prédictions hors-pli (modèle unique, sans bonus d'ensemble) ;
intervalle à 95 % par bootstrap SUR LES FAMILLES (Field & Welsh 2007, J. R. Stat. Soc. B 69:369-390), mêmes familles rééchantillonnées pour tous les modèles, 2 000 rééchantillonnages, graine 42.
Critère de décision (fixé à l'avance) : marge d'équivalence pratique delta = 0,001 de F1 macro. Pour une différence A - B de F1 macro avec IC 95 % [lo ; hi] :
  A supérieur si lo > 0 ; B supérieur si hi < 0 ; A non inférieur (équivalent) si lo > -delta et hi < +delta ; sinon : non tranché.
Statistique secondaire : ensemble des 5 graines (moyenne des probabilités), mesures identiques.
Usage (depuis scripts/) : python3 comparaison_equitable_v14_v1.py --out ../results/comparaison_equitable_v14 --dl ../results/dl_imbrique_v14_equitable:choisie_cal --xgb ../results/eval_arbres_v14_xgb:choisie_cal --rf ../results/eval_arbres_v14_rf:choisie_cal [--extra "DL c35 fige=../results/dl_imbrique_v14:c35_cal"]
"""
import argparse, glob, json, os, sys
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import protocole_commun_v10 as pc
from evaluer_dl_imbrique_v5 import niveau_par_medicament

B = 2000; DELTA = 0.001


def confusion_par_famille(y, pred, fam, nf, K):
    c = np.zeros((nf, K, K), dtype=np.int64); np.add.at(c, (fam, y, pred), 1); return c


def mesures(C, ev):
    """C (K,K) vrai x prédit -> F1 macro, EVITER manqués, faux EVITER, erreurs, précision EVITER."""
    tp = np.diag(C).astype(float); fp = C.sum(0) - tp; fn = C.sum(1) - tp
    f1 = np.where(2 * tp + fp + fn > 0, 2 * tp / np.maximum(2 * tp + fp + fn, 1), 0.0)
    return np.array([f1.mean(), C[ev].sum() - C[ev, ev], C[:, ev].sum() - C[ev, ev], C.sum() - np.trace(C), C[ev, ev] / max(C[:, ev].sum(), 1)])


NOMS = ['f1_macro', 'EVITER_manques', 'faux_EVITER', 'erreurs', 'precision_EVITER']


def charger(dossier, quoi, lig_ref=None):
    """Retourne (ligne triée, y, [P_graine0..]) pour un bras."""
    fich = sorted(glob.glob(os.path.join(dossier, 'oof_%s_pli*_graine*.npz' % quoi)))
    assert fich, 'aucun fichier dans ' + dossier
    graines = sorted({int(f.split('graine')[-1].split('.')[0]) for f in fich}); plis = sorted({int(f.split('_pli')[-1].split('_')[0]) for f in fich})
    assert plis == [1, 2, 3, 4, 5], 'plis manquants dans %s : %s' % (dossier, plis)
    assert len(fich) == len(plis) * len(graines), 'fichiers incomplets dans ' + dossier
    lig = np.sort(np.concatenate([np.load(f)['ligne'] for f in fich if f.endswith('graine%d.npz' % graines[0])]))
    P = []; y = None
    for s in graines:
        L, Y, Pr = [], [], []
        for k in plis:
            z = np.load(os.path.join(dossier, 'oof_%s_pli%d_graine%d.npz' % (quoi, k, s))); L.append(z['ligne']); Y.append(z['y']); q = z['proba'].astype(np.float64); Pr.append(q / q.sum(1, keepdims=True))   # les probabilités sont stockées en float32 : renormalisation
        L = np.concatenate(L); o = np.argsort(L); assert (L[o] == lig).all(); P.append(np.concatenate(Pr)[o]); yy = np.concatenate(Y)[o]
        assert y is None or (y == yy).all(); y = yy
    return lig, y, P


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data', default='../data/corpus_v14/phenotype_drug_dataset_v14.csv'); ap.add_argument('--out', required=True)
    for k in ('dl', 'xgb', 'rf'): ap.add_argument('--' + k, required=True, help='dossier:quoi')
    ap.add_argument('--extra', action='append', default=[], help='nom=dossier:quoi (bras supplémentaire, non utilisé pour la règle de décision)')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    d = pc.charger(a.data, None); y_all, classes, groups = d['y'], d['classes'], d['groups']; K = len(classes); ev = classes.index('EVITER')
    final, folds = pc.decouper(groups, y_all)
    bras = {'DL': a.dl, 'XGBoost': a.xgb, 'Forêt aléatoire': a.rf}
    for e in a.extra: n, v = e.split('=', 1); bras[n] = v
    P = {}; lig0 = None; y0 = None
    for nom, spec in bras.items():
        dos, quoi = spec.rsplit(':', 1); lig, y, Ps = charger(dos, quoi)
        assert not (set(lig) & set(final)), 'une ligne de l\'ensemble final est dans les prédictions de ' + nom
        if lig0 is None: lig0, y0 = lig, y; assert (y0 == y_all[lig0]).all()
        assert (lig == lig0).all() and (y == y0).all(), 'lignes ou étiquettes différentes pour ' + nom
        P[nom] = Ps
    n_lignes = len(lig0); fam = pd.factorize(groups[lig0])[0]; nf = fam.max() + 1
    print('lignes %d, familles %d, graines %s' % (n_lignes, nf, {m: len(p) for m, p in P.items()}))
    principaux = ['DL', 'XGBoost', 'Forêt aléatoire']
    # confusions par famille : (modele, graine) et ensemble de graines
    CF = {m: [confusion_par_famille(y0, p.argmax(1), fam, nf, K) for p in P[m]] for m in P}
    CE = {m: confusion_par_famille(y0, np.mean(P[m], 0).argmax(1), fam, nf, K) for m in P}
    rng = np.random.RandomState(42); W = [np.bincount(rng.randint(0, nf, nf), minlength=nf) for _ in range(B)]
    def stat_graines(m, w): return np.mean([mesures(np.tensordot(w, c, axes=(0, 0)), ev) for c in CF[m]], 0)
    def stat_ens(m, w): return mesures(np.tensordot(w, CE[m], axes=(0, 0)), ev)
    ones = np.ones(nf, dtype=np.int64); res = []; diffs = []
    for tag, fonction in (('moyenne_graines', stat_graines), ('ensemble_graines', stat_ens)):
        pts = {m: fonction(m, ones) for m in P}; bs = {m: np.array([fonction(m, w) for w in W]) for m in P}
        for m in P:
            for j, n in enumerate(NOMS):
                lo, hi = np.percentile(bs[m][:, j], [2.5, 97.5]); res.append(dict(statistique=tag, modele=m, mesure=n, estimation=round(float(pts[m][j]), 5), ic95_bas=round(float(lo), 5), ic95_haut=round(float(hi), 5)))
        paires = [(x, y_) for i, x in enumerate(P) for y_ in list(P)[i + 1:]]
        for x, y_ in paires:
            for j, n in enumerate(NOMS):
                dd = bs[x][:, j] - bs[y_][:, j]; lo, hi = np.percentile(dd, [2.5, 97.5]); verdict = ''
                if n == 'f1_macro' and x in principaux and y_ in principaux:
                    verdict = (x + ' supérieur') if lo > 0 else (y_ + ' supérieur') if hi < 0 else ('équivalents (marge %.3f)' % DELTA) if (lo > -DELTA and hi < DELTA) else 'non tranché'
                diffs.append(dict(statistique=tag, comparaison='%s - %s' % (x, y_), mesure=n, difference=round(float(pts[x][j] - pts[y_][j]), 5), ic95_bas=round(float(lo), 5), ic95_haut=round(float(hi), 5), decision=verdict))
    pd.DataFrame(res).to_csv(os.path.join(a.out, 'mesures_avec_ic.csv'), index=False); pd.DataFrame(diffs).to_csv(os.path.join(a.out, 'differences_appariees.csv'), index=False)
    # dispersion entre graines et entre plis (modèle unique)
    disp = []
    for m in P:
        f1s = [mesures(c.sum(0), ev)[0] for c in CF[m]]; disp.append(dict(modele=m, f1_macro_par_graine=[round(float(v), 5) for v in f1s], sd_entre_graines=round(float(np.std(f1s, ddof=0)), 6)))
    # calibration (probabilités calibrées enregistrées, moyenne des graines)
    cal = []
    for m in P:
        ll = [pc.metriques(y0, p, classes)['logloss'] for p in P[m]]; ec = [pc.metriques(y0, p, classes)['ECE'] for p in P[m]]
        cal.append(dict(modele=m, logloss_moy=round(float(np.mean(ll)), 5), ECE_moy=round(float(np.mean(ec)), 5)))
    # F1 macro par niveau de source
    niv = niveau_par_medicament(); dn = np.array([niv[mm] for mm in d['meds']])[d['drug_idx'][lig0]]
    src = []
    for lvl in sorted(set(dn)):
        mk = dn == lvl
        if len(set(y0[mk])) < 2: continue
        row = dict(niveau=lvl, n_lignes=int(mk.sum()))
        for m in P: row[m] = round(float(np.mean([pc.metriques(y0[mk], p[mk], classes)['f1_macro'] for p in P[m]])), 4)
        src.append(row)
    # erreurs par médicament (ensemble de graines) et recouvrement
    err = {m: np.mean(P[m], 0).argmax(1) != y0 for m in P}; meds = np.array(d['meds'])[d['drug_idx'][lig0]]
    pm = pd.DataFrame({m: pd.Series(err[m]).groupby(meds).sum() for m in P}).sort_values('DL', ascending=False)
    pm.to_csv(os.path.join(a.out, 'erreurs_par_medicament_ensemble_graines.csv'))
    rec = dict(erreurs_DL=int(err['DL'].sum()), erreurs_XGBoost=int(err['XGBoost'].sum()), erreurs_RF=int(err['Forêt aléatoire'].sum()),
               communes_DL_XGB=int((err['DL'] & err['XGBoost']).sum()), communes_trois=int((err['DL'] & err['XGBoost'] & err['Forêt aléatoire']).sum()))
    json.dump(dict(n_lignes=int(n_lignes), n_familles=int(nf), bootstrap=B, delta=DELTA, dispersion=disp, calibration=cal, f1_par_niveau_source=src, recouvrement_erreurs_ensemble_graines=rec),
              open(os.path.join(a.out, 'resume_comparaison.json'), 'w'), indent=1, ensure_ascii=False)
    print(pd.DataFrame(res).to_string(index=False)); print(); print(pd.DataFrame(diffs).to_string(index=False)); print(); print(json.dumps(dict(dispersion=disp, calibration=cal, source=src, recouvrement=rec), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
