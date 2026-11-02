#!/usr/bin/env python3
"""
analyser_dl_medicament_v1.py (2 nov. 2026) : analyse des sorties de evaluer_dl_medicament_v1.py (aucun entraînement).
 - IC à 95 % par bootstrap SUR LES MÉDICAMENTS (poids de rééchantillonnage par médicament) pour chaque modèle ; différences appariées DL - références.
 - tableau par médicament pour le test prospectif.
Usage : python3 -I analyser_dl_medicament_v1.py DOSSIER_RESULTATS [B=400] [EXCLURE=med1,med2,...]  (analyse de sensibilité : ces médicaments sont retirés du TEST uniquement ; sorties suffixées _sans_exclus)
"""
import sys, os, glob, json, re
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
D = sys.argv[1]; B = int(sys.argv[2]) if len(sys.argv) > 2 else 400
CL = ['ADAPTER_DOSE', 'EVITER', 'STANDARD', 'SURVEILLER']; STD = 2
meds = json.load(open(os.path.join(D, 'medicaments.json')))['medicaments']
EXC = set(m.strip().lower() for m in sys.argv[3].split(',')) if len(sys.argv) > 3 else set()
SUF = '_sans_exclus' if EXC else ''
EXI = {i for i, m in enumerate(meds) if m.lower() in EXC}
rng = np.random.RandomState(0)
oof = {}
for f in glob.glob(os.path.join(D, 'oof_*.npz')):
    m = re.match(r'oof_(medicament|classe_ATC|prospectif)_(.*)\.npz', os.path.basename(f)); z = np.load(f)
    oof[(m.group(1), m.group(2))] = dict(dt=z['dt'], pr=z['pr'], y=z['y'])
def stat(nom, y, pr, w):  # version de référence (scikit-learn), utilisée pour le tableau par médicament et pour vérifier la version rapide
    act = (y != STD).astype(int); sc = 1 - pr[:, STD]
    if nom == 'auroc': return roc_auc_score(act, sc, sample_weight=w)
    if nom == 'ap': return average_precision_score(act, sc, sample_weight=w)
    return f1_score(y, pr.argmax(1), average='macro', labels=[0, 1, 2, 3], sample_weight=w, zero_division=0)
def prep(y, pr, dt):  # tri des scores une seule fois ; chaque tirage bootstrap = simples sommes pondérées
    act = (y != STD).astype(float); sc = 1 - pr[:, STD]; u, g = np.unique(sc, return_inverse=True)
    return dict(act=act, g=g, ng=len(u), y=y.astype(int), pred=pr.argmax(1).astype(int), dt=dt)
def fast(nom, P, w_d):  # w_d : poids par médicament (vecteur sur tous les médicaments)
    w = w_d[P['dt']]
    if nom in ('auroc', 'ap'):
        wp = np.bincount(P['g'], w * P['act'], P['ng']); wn = np.bincount(P['g'], w * (1 - P['act']), P['ng']); Wp, Wn = wp.sum(), wn.sum()
        if Wp <= 0 or Wn <= 0: return np.nan
        if nom == 'auroc': return float((wp * (np.cumsum(wn) - wn + 0.5 * wn)).sum() / (Wp * Wn))
        tp = np.cumsum(wp[::-1]); fp = np.cumsum(wn[::-1]); den = tp + fp
        return float(((wp[::-1] / Wp) * np.where(den > 0, tp / np.where(den > 0, den, 1), 0)).sum())
    M = np.bincount(P['y'] * 4 + P['pred'], w, 16).reshape(4, 4); tp = np.diag(M); fp = M.sum(0) - tp; fn = M.sum(1) - tp; d = 2 * tp + fp + fn
    return float(np.mean(np.where(d > 0, 2 * tp / np.where(d > 0, d, 1), 0)))
lignes = []
for schema in ('medicament', 'classe_ATC', 'prospectif'):
    mods = sorted(k[1] for k in oof if k[0] == schema)
    if not mods: continue
    ref = oof[(schema, mods[0])]; Dr = np.array([d for d in np.unique(ref['dt']) if d not in EXI])
    draws = [rng.multinomial(len(Dr), np.ones(len(Dr)) / len(Dr)) for _ in range(B)]
    est = {}
    for nom in ('auroc', 'ap', 'f1'):
        for mod in mods:
            o = oof[(schema, mod)]; G = o['pr'].shape[0]
            PP = [prep(o['y'][g], o['pr'][g], o['dt'][g]) for g in range(G)]
            def une(w_d):
                w = np.zeros(len(meds)); w[Dr] = w_d
                return np.mean([fast(nom, PP[g], w) for g in range(G)])
            pt = une(np.ones(len(Dr)))
            bs = np.array([une(d) for d in draws])
            est[(nom, mod)] = (pt, bs)
            lignes.append(dict(schema=schema, mesure=nom, modele=mod, valeur=pt, ic_bas=np.percentile(bs, 2.5), ic_haut=np.percentile(bs, 97.5)))
    for nom in ('auroc', 'ap', 'f1'):
        for mod in mods:
            if not mod.startswith('DL_'): continue
            for ref_ in ('prior_gene_phenotype', 'voisins_k5'):
                if (nom, ref_) not in est: continue
                dif = est[(nom, mod)][1] - est[(nom, ref_)][1]
                lignes.append(dict(schema=schema, mesure=nom, modele=mod + ' - ' + ref_, valeur=est[(nom, mod)][0] - est[(nom, ref_)][0],
                                   ic_bas=np.percentile(dif, 2.5), ic_haut=np.percentile(dif, 97.5)))
R = pd.DataFrame(lignes); R.to_csv(os.path.join(D, 'analyse_bootstrap%s.csv' % SUF), index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
print(R.round(4).to_string(index=False))
# tableau par médicament (prospectif)
if ('prospectif', 'majoritaire') in oof:
    rows = []
    for mod in sorted(k[1] for k in oof if k[0] == 'prospectif'):
        o = oof[('prospectif', mod)]
        for d in np.unique(o['dt']):
            v = []
            for g in range(o['pr'].shape[0]):
                s = o['dt'][g] == d; y = o['y'][g][s]; pr = o['pr'][g][s]
                v.append(dict(n=s.sum(), part_non_std=(y != STD).mean(), exactitude=(pr.argmax(1) == y).mean(),
                              auroc=roc_auc_score((y != STD).astype(int), 1 - pr[:, STD]) if 0 < (y != STD).sum() < len(y) else np.nan,
                              rappel_non_std=((pr.argmax(1) != STD) & (y != STD)).sum() / max((y != STD).sum(), 1) if (y != STD).any() else np.nan))
            rows.append(dict(modele=mod, medicament=meds[d], **pd.DataFrame(v).mean().to_dict()))
    T = pd.DataFrame(rows); T.to_csv(os.path.join(D, 'prospectif_par_medicament%s.csv' % SUF), index=False)
    print('\n=== prospectif : par médicament (moyenne des graines) ===')
    print(T[T.modele.isin(['prior_gene_phenotype', 'voisins_k5', 'DL_lien_atc_fp', 'DL_porte_lien_atc_fp'])].round(3).sort_values(['medicament', 'modele']).to_string(index=False))
