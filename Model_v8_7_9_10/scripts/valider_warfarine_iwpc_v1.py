#!/usr/bin/env python3
"""
valider_warfarine_iwpc_v1.py (2 nov. 2026) : applique docs/Protocole_pilier_B_IWPC_2nov2026.md (fixé avant toute comparaison de groupes ; bloc POST HOC et correction du bootstrap S6 ajoutés après la première exécution).
Usage : python3 -I valider_warfarine_iwpc_v1.py FICHIER_IWPC_2009.xls DOSSIER_SORTIE
Lecture seule sur les données ; aucune écriture hors du dossier de sortie.
"""
import sys, os, re
import numpy as np, pandas as pd
F, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
s = pd.read_excel(F, sheet_name='Subject Data'); s.columns = [re.sub(r'\s+', ' ', c).strip() for c in s.columns]
VAL = {'*1/*1': 1.0, '*1/*2': 0.75, '*1/*3': 0.5, '*2/*2': 0.5, '*2/*3': 0.25, '*3/*3': 0.0}
AGE = {'10 - 19': 14.5, '20 - 29': 24.5, '30 - 39': 34.5, '40 - 49': 44.5, '50 - 59': 54.5, '60 - 69': 64.5, '70 - 79': 74.5, '80 - 89': 84.5, '90+': 92.0}
log = []
def P(*a):
    t = ' '.join(str(x) for x in a); print(t); log.append(t)
P('Sujets (fichier 2009) :', len(s), '| identifiants uniques :', s['PharmGKB Subject ID'].nunique())
st = s['Subject Reached Stable Dose of Warfarin'] == 1; dose = s['Therapeutic Dose of Warfarin']; g = s['CYP2C9 consensus']
P('stable==1 :', int(st.sum()), '| avec dose :', int((st & dose.notna()).sum()))
base = st & dose.notna() & (dose > 0)
P('exclus (génotype CYP2C9 absent) :', int((base & g.isna()).sum()), '| exclus (génotype hors correspondance) :', int((base & g.notna() & ~g.isin(VAL)).sum()))
d = s[base & g.isin(VAL)].copy(); d['val'] = d['CYP2C9 consensus'].map(VAL); d['y'] = np.log(d['Therapeutic Dose of Warfarin'])
d['adapt'] = (d['val'] < 1).astype(int)
d['classe'] = np.select([d['val'] < 0.5, d['val'] < 1], ['lent', 'intermediaire'], 'normal(*1/*1)')
P('Population principale :', len(d), '| ADAPTER_DOSE (corpus) :', int(d.adapt.sum()), '| *1/*1 :', int((1 - d.adapt).sum()))
rng = np.random.RandomState(0); B = 2000; n = len(d); IDX = [rng.randint(0, n, n) for _ in range(B)]
y = d['y'].values; rows = []
def ratio(mask_a, mask_b, idx=None):
    yy, a, b = (y, mask_a, mask_b) if idx is None else (y[idx], mask_a[idx], mask_b[idx])
    return np.exp(yy[a].mean() - yy[b].mean()) if a.any() and b.any() else np.nan
def rapport(nom, ma, mb):
    pt = ratio(ma, mb); bs = np.array([ratio(ma, mb, i) for i in IDX]); lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    ra = np.median(d['Therapeutic Dose of Warfarin'].values[ma]); rb = np.median(d['Therapeutic Dose of Warfarin'].values[mb])
    rows.append(dict(analyse=nom, n_groupe=int(ma.sum()), n_reference=int(mb.sum()), ratio=pt, ic_bas=lo, ic_haut=hi, mediane_groupe=ra, mediane_ref=rb))
    P('%-34s n=%4d vs %4d | ratio %.3f [%.3f ; %.3f] | médianes %.1f vs %.1f mg/sem' % (nom, ma.sum(), mb.sum(), pt, lo, hi, ra, rb))
ref = (d['val'] == 1.0).values
P('\n== H1 (principale) =='); rapport('H1 ADAPTER_DOSE vs *1/*1', d.adapt.values == 1, ref)
P('\n== S1 par classe et par génotype ==')
for c in ('lent', 'intermediaire'): rapport('S1 classe ' + c, (d.classe == c).values, ref)
for gt in ('*1/*2', '*1/*3', '*2/*2', '*2/*3', '*3/*3'): rapport('S1 génotype ' + gt, (d['CYP2C9 consensus'] == gt).values, ref)
P('\n== S4 sensibilité : patients White seulement ==')
w = (d['Race (OMB)'] == 'White').values; yw = y.copy()
sub = d[w]; ys = sub['y'].values; a = (sub.adapt == 1).values; r = (sub.val == 1).values
rng2 = np.random.RandomState(0); bs = []
for _ in range(B):
    i = rng2.randint(0, len(sub), len(sub)); aa, rr = a[i], r[i]
    bs.append(np.exp(ys[i][aa].mean() - ys[i][rr].mean()) if aa.any() and rr.any() else np.nan)
pt = np.exp(ys[a].mean() - ys[r].mean()); lo, hi = np.nanpercentile(bs, [2.5, 97.5])
rows.append(dict(analyse='S4 White ADAPTER vs *1/*1', n_groupe=int(a.sum()), n_reference=int(r.sum()), ratio=pt, ic_bas=lo, ic_haut=hi))
P('S4 White: n=%d vs %d | ratio %.3f [%.3f ; %.3f]' % (a.sum(), r.sum(), pt, lo, hi))
# S3 : OLS HC3
def ols(X, yv):
    X = np.column_stack([np.ones(len(X)), X]); XtXi = np.linalg.pinv(X.T @ X); b = XtXi @ X.T @ yv; e = yv - X @ b; h = np.einsum('ij,jk,ik->i', X, XtXi, X)
    u = e / (1 - h); V = XtXi @ (X.T * (u ** 2)) @ X @ XtXi; r2 = 1 - (e @ e) / ((yv - yv.mean()) @ (yv - yv.mean())); return b, np.sqrt(np.diag(V)), r2
d['age'] = d['Age'].map(AGE); d['amio'] = d['Amiodarone (Cordarone)']; d['vk'] = d['VKORC1 -1639 consensus'].map({'G/G': 0, 'A/G': 1, 'A/A': 2})
for rc in ('Asian', 'Black or African American', 'Unknown'): d['r_' + rc[:5]] = (d['Race (OMB)'] == rc).astype(float)
P('\n== S3 régression ajustée (log-dose ; coefficient = effet multiplicatif exp(b)) ==')
cov = ['age', 'Height (cm)', 'Weight (kg)', 'amio']; race = ['r_Asian', 'r_Black', 'r_Unkno']
for nom, extra in (('sans VKORC1', []), ('avec VKORC1', ['vk'])):
    cols = ['adapt'] + cov + race + extra; sub = d.dropna(subset=cols + ['y'])
    b, se, r2 = ols(sub[cols].values.astype(float), sub['y'].values); k = 1
    P('S3 %s : n=%d | ADAPTER_DOSE vs *1/*1 : x%.3f [%.3f ; %.3f] | R2=%.3f' % (nom, len(sub), np.exp(b[k]), np.exp(b[k] - 1.96 * se[k]), np.exp(b[k] + 1.96 * se[k]), r2))
    rows.append(dict(analyse='S3 ' + nom, n_groupe=len(sub), ratio=np.exp(b[k]), ic_bas=np.exp(b[k] - 1.96 * se[k]), ic_haut=np.exp(b[k] + 1.96 * se[k])))
    if extra: P('   VKORC1 par allèle A : x%.3f [%.3f ; %.3f]' % (np.exp(b[-1]), np.exp(b[-1] - 1.96 * se[-1]), np.exp(b[-1] + 1.96 * se[-1])))
# S5 doses basses
P('\n== S5 dose basse (<= 21 mg/semaine) ==')
low = (d['Therapeutic Dose of Warfarin'] <= 21).values; ad = d.adapt.values == 1
def sens_spec(i): return (ad[i] & low[i]).sum() / max(low[i].sum(), 1), (~ad[i] & ~low[i]).sum() / max((~low[i]).sum(), 1), low[i][ad[i]].mean(), low[i][~ad[i]].mean()
pt = sens_spec(np.arange(n)); bs = np.array([sens_spec(i) for i in IDX])
for k, nom in enumerate(['sensibilité (ADAPTER parmi doses basses)', 'spécificité (non-ADAPTER parmi autres)', 'part de doses basses chez ADAPTER_DOSE', 'part de doses basses chez *1/*1']):
    lo, hi = np.percentile(bs[:, k], [2.5, 97.5]); P('%-44s %.3f [%.3f ; %.3f]' % (nom, pt[k], lo, hi)); rows.append(dict(analyse='S5 ' + nom, ratio=pt[k], ic_bas=lo, ic_haut=hi))
# S6 exploratoire
P('\n== S6 exploratoire : part de variance de log-dose (R2) ==')
sub = d.dropna(subset=['vk']).copy(); ys = sub['y'].values
def dum(col): return pd.get_dummies(sub[col], drop_first=True).values.astype(float)
for nom, X in (('CYP2C9 seul', dum('CYP2C9 consensus')), ('VKORC1 -1639 seul', dum('vk')), ('CYP2C9 + VKORC1', np.column_stack([dum('CYP2C9 consensus'), dum('vk')]))):
    r2 = ols(X, ys)[2]; P('S6 %-20s n=%d R2=%.3f' % (nom, len(sub), r2)); rows.append(dict(analyse='S6 R2 ' + nom, n_groupe=len(sub), ratio=r2))
for v, nm in ((1, 'A/G'), (2, 'A/A')):
    m = (sub.vk == v).values; r = (sub.vk == 0).values; pt = np.exp(ys[m].mean() - ys[r].mean())
    rg = np.random.RandomState(1); bs = []
    for _ in range(B):
        i = rg.randint(0, len(sub), len(sub)); bs.append(np.exp(ys[i][m[i]].mean() - ys[i][r[i]].mean()))
    lo, hi = np.percentile(bs, [2.5, 97.5]); P('S6 VKORC1 %s vs G/G : n=%d vs %d | ratio %.3f [%.3f ; %.3f]' % (nm, m.sum(), r.sum(), pt, lo, hi)); rows.append(dict(analyse='S6 VKORC1 ' + nm, n_groupe=int(m.sum()), n_reference=int(r.sum()), ratio=pt, ic_bas=lo, ic_haut=hi))
P('\n== POST HOC (non prévu au protocole du 2 nov. 18 h 19 ; ajouté après avoir vu S1/S4) : génotype vs *1/*1 chez les patients White ==')
wh = d[d['Race (OMB)'] == 'White']; yw_ = wh['y'].values; gw = wh['CYP2C9 consensus'].values; rg = np.random.RandomState(2); IW = [rg.randint(0, len(wh), len(wh)) for _ in range(B)]
for gt in ('*1/*2', '*1/*3', '*2/*2', '*2/*3', '*3/*3'):
    m = gw == gt; r = gw == '*1/*1'; pt = np.exp(yw_[m].mean() - yw_[r].mean())
    bs = [np.exp(yw_[i][m[i]].mean() - yw_[i][r[i]].mean()) if m[i].any() else np.nan for i in IW]; lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    P('POST HOC White %s : n=%d vs %d | ratio %.3f [%.3f ; %.3f]' % (gt, m.sum(), r.sum(), pt, lo, hi)); rows.append(dict(analyse='POSTHOC White ' + gt, n_groupe=int(m.sum()), n_reference=int(r.sum()), ratio=pt, ic_bas=lo, ic_haut=hi))
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'resultats_pilier_B_iwpc.csv'), index=False)
open(os.path.join(OUT, 'resultats_pilier_B_iwpc.txt'), 'w').write('\n'.join(log) + '\n')
