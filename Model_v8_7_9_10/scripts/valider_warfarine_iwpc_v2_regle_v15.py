#!/usr/bin/env python3
"""
valider_warfarine_iwpc_v2_regle_v15.py : ANALYSE POST HOC (decidee apres les resultats de valider_warfarine_iwpc_v1.py).
Applique aux memes patients IWPC (memes criteres que la v1) l'etiquette de la regle warfarine du corpus v15 :
  ADAPTER_DOSE si CYP2C9 (score d'activite / 2) <= 0,5  OU  VKORC1 -1639 = A/A (rs9923231 TT) ; sinon STANDARD.
  (CYP2C9 *1/*2 = 0,75 -> STANDARD selon le texte DPWG ; VKORC1 A/G -> aucune action selon DPWG.)
  Patients avec CYP2C9 > 0,5 et VKORC1 inconnu : etiquette v15 indeterminee -> exclus et comptes.
Memes estimateurs que la v1 : rapport des moyennes geometriques, bootstrap sur les patients (2 000 tirages, graine 0) ;
dose basse <= 21 mg/semaine. L'etiquette v14 (CYP2C9 < 1) est recalculee sur les MEMES patients pour comparaison.
Usage : python3 -I valider_warfarine_iwpc_v2_regle_v15.py FICHIER_IWPC_2009.xls DOSSIER_SORTIE
Lecture seule sur les donnees ; aucune ecriture hors du dossier de sortie.
"""
import sys, os, re
import numpy as np, pandas as pd
F, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
s = pd.read_excel(F, sheet_name='Subject Data'); s.columns = [re.sub(r'\s+', ' ', c).strip() for c in s.columns]
VAL = {'*1/*1': 1.0, '*1/*2': 0.75, '*1/*3': 0.5, '*2/*2': 0.5, '*2/*3': 0.25, '*3/*3': 0.0}
log, rows = [], []
def P(*a):
    t = ' '.join(str(x) for x in a); print(t); log.append(t)
P('ANALYSE POST HOC : regle warfarine du corpus v15 (CYP2C9 DPWG + VKORC1 DPWG)')
st = s['Subject Reached Stable Dose of Warfarin'] == 1; dose = s['Therapeutic Dose of Warfarin']; g = s['CYP2C9 consensus']
base = st & dose.notna() & (dose > 0)
d = s[base & g.isin(VAL)].copy()
P('Population de la v1 (memes criteres) :', len(d), '(attendu : 5774)')
d['val'] = d['CYP2C9 consensus'].map(VAL); d['vk'] = d['VKORC1 -1639 consensus']
d['y'] = np.log(d['Therapeutic Dose of Warfarin'])
indet = (d['val'] > 0.5) & ~d['vk'].isin(['G/G', 'A/G', 'A/A'])
P('Exclus (CYP2C9 > 0,5 et VKORC1 inconnu, etiquette v15 indeterminee) :', int(indet.sum()))
d = d[~indet].copy()
d['v15'] = ((d['val'] <= 0.5) | (d['vk'] == 'A/A')).astype(int)
d['v14'] = (d['val'] < 1).astype(int)
P('Population analysee :', len(d), '| v15 ADAPTER_DOSE :', int(d.v15.sum()), '| v15 STANDARD :', int((1 - d.v15).sum()))
P('Tableau croise v14 (lignes) x v15 (colonnes), 1 = ADAPTER_DOSE :'); P(pd.crosstab(d.v14, d.v15).to_string())
P('Detail ADAPTER_DOSE v15 : CYP2C9 <= 0,5 :', int((d.val <= 0.5).sum()), '| VKORC1 A/A avec CYP2C9 > 0,5 :', int(((d.val > 0.5) & (d.vk == 'A/A')).sum()))
y = d['y'].values; n = len(d); B = 2000
rng = np.random.RandomState(0); IDX = [rng.randint(0, n, n) for _ in range(B)]
def rapport(nom, ma, mb, idxs=IDX, yy=y, dd=d):
    def r(i=None):
        a, b, v = (ma, mb, yy) if i is None else (ma[i], mb[i], yy[i])
        return np.exp(v[a].mean() - v[b].mean()) if a.any() and b.any() else np.nan
    pt = r(); bs = np.array([r(i) for i in idxs]); lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    dz = dd['Therapeutic Dose of Warfarin'].values
    rows.append(dict(analyse=nom, n_groupe=int(ma.sum()), n_reference=int(mb.sum()), ratio=pt, ic_bas=lo, ic_haut=hi, mediane_groupe=np.median(dz[ma]), mediane_ref=np.median(dz[mb])))
    P('%-46s n=%4d vs %4d | ratio %.3f [%.3f ; %.3f] | medianes %.1f vs %.1f mg/sem' % (nom, ma.sum(), mb.sum(), pt, lo, hi, np.median(dz[ma]), np.median(dz[mb])))
P('\n== H1 post hoc : ADAPTER_DOSE contre STANDARD ==')
rapport('v15 ADAPTER_DOSE vs v15 STANDARD', d.v15.values == 1, d.v15.values == 0)
rapport('v14 ADAPTER_DOSE vs v14 (*1/*1), memes patients', d.v14.values == 1, d.v14.values == 0)
P('\n== Groupes qui changent entre v14 et v15 (reference : STANDARD dans les deux versions) ==')
ref = ((d.v14 == 0) & (d.v15 == 0)).values
rapport('v14 ADAPTER -> v15 STANDARD (*1/*2 sans A/A)', ((d.v14 == 1) & (d.v15 == 0)).values, ref)
rapport('v14 STANDARD -> v15 ADAPTER (*1/*1 et A/A)', ((d.v14 == 0) & (d.v15 == 1)).values, ref)
P('\n== Patients White seulement ==')
w = (d['Race (OMB)'] == 'White').values; dw = d[w]; yw = dw['y'].values; nw = len(dw)
rw = np.random.RandomState(0); IW = [rw.randint(0, nw, nw) for _ in range(B)]
rapport('White v15 ADAPTER_DOSE vs v15 STANDARD', dw.v15.values == 1, dw.v15.values == 0, IW, yw, dw)
rapport('White v14 ADAPTER_DOSE vs *1/*1', dw.v14.values == 1, dw.v14.values == 0, IW, yw, dw)
P('\n== Dose basse (<= 21 mg/semaine) : sensibilite et specificite de l etiquette ==')
low = (d['Therapeutic Dose of Warfarin'] <= 21).values
for lab in ('v15', 'v14'):
    ad = d[lab].values == 1
    def ss(i): return (ad[i] & low[i]).sum() / max(low[i].sum(), 1), (~ad[i] & ~low[i]).sum() / max((~low[i]).sum(), 1)
    pt = ss(np.arange(n)); bs = np.array([ss(i) for i in IDX])
    for k, nom in enumerate(['sensibilite', 'specificite']):
        lo, hi = np.percentile(bs[:, k], [2.5, 97.5]); P('%s %-12s %.3f [%.3f ; %.3f]' % (lab, nom, pt[k], lo, hi))
        rows.append(dict(analyse='%s %s dose basse' % (lab, nom), ratio=pt[k], ic_bas=lo, ic_haut=hi))
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'resultats_iwpc_regle_v15.csv'), index=False)
open(os.path.join(OUT, 'resultats_iwpc_regle_v15.txt'), 'w').write('\n'.join(log) + '\n')
P('\nEcrit :', os.path.join(OUT, 'resultats_iwpc_regle_v15.txt'))
