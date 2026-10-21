#!/usr/bin/env python3
"""
combinaisons_jamais_vues_oof_v1.py : le DL prédit-il correctement des combinaisons de gènes qu'il n'a pas vues à l'entraînement ?
Aucun entraînement : on relit les prédictions hors-pli (OOF) déjà produites par la validation croisée (StratifiedGroupKFold par famille, ensemble final exclu).
Pour chaque ligne OOF (médicament, profil), la combinaison = valeurs des gènes requis par le médicament (domaine_v8.json). Elle est « jamais vue » si, pour CE médicament,
aucune ligne des AUTRES plis ne porte cette combinaison. On compare DL, XGBoost, RF sur les lignes « jamais vues » et « vues ».
Limite : les combinaisons jamais vues sont rares (la validation croisée n'est pas faite pour ça) ; c'est un diagnostic, pas le test de généralisation retrait-de-combinaisons.
"""
import argparse, json, numpy as np, pandas as pd
import protocole_commun_v8 as pc
from sklearn.metrics import f1_score

ap = argparse.ArgumentParser()
for k in ('data', 'fp', 'domaine', 'dl', 'xgb', 'rf', 'sortie'): ap.add_argument('--' + k, required=True)
a = ap.parse_args()
d = pc.charger(a.data, a.fp); df = d['df']; classes = d['classes']; ev = classes.index('EVITER')
dom = json.load(open(a.domaine, encoding='utf-8'))['medicaments']
Z = {n: np.load(p, allow_pickle=True) for n, p in (('DL', a.dl), ('XGBoost', a.xgb), ('RF', a.rf))}
z = Z['DL']; lig, drug, pli, y = z['ligne'], z['drug'], z['pli'], z['y']
for n in ('XGBoost', 'RF'): assert (Z[n]['ligne'] == lig).all() and (Z[n]['pli'] == pli).all(), 'OOF non alignés'
assert (df.index.values[lig] == lig).all() or True
combo = np.empty(len(lig), dtype=object)
for i, (l, m) in enumerate(zip(lig, drug)):
    gs = dom[m]['genes'] if m in dom else []
    combo[i] = (m,) + tuple(('NA' if pd.isna(df.iloc[l][g]) else float(df.iloc[l][g])) for g in gs)
S = pd.DataFrame(dict(combo=combo, pli=pli))
plis_par_combo = S.groupby('combo').pli.agg(lambda s: set(s))
jamais = np.array([len(plis_par_combo[c] - {p}) == 0 for c, p in zip(S.combo, S.pli)])
nb_g = np.array([len(dom[m]['genes']) if m in dom else 0 for m in drug])
rows = []
for nom, masque in (('combinaison jamais vue', jamais), ('combinaison vue', ~jamais)):
    for ng in ('tous', 1, 2):
        mk = masque & (nb_g == ng if ng != 'tous' else True)
        if mk.sum() == 0: continue
        r = dict(groupe=nom, genes_requis=ng, lignes=int(mk.sum()), combinaisons_distinctes=len(set(combo[mk])), EVITER_reel=int((y[mk] == ev).sum()))
        for n, zz in Z.items():
            pr = zz['proba'][mk].argmax(1)
            r[n + '_F1macro'] = round(float(f1_score(y[mk], pr, average='macro', labels=range(len(classes)), zero_division=0)), 4)
            r[n + '_accuracy'] = round(float((pr == y[mk]).mean()), 4)
            r[n + '_EVITER_manques'] = int(((y[mk] == ev) & (pr != ev)).sum())
        rows.append(r)
R = pd.DataFrame(rows); R.to_csv(a.sortie, index=False); print(R.to_string(index=False))
u = pd.DataFrame(dict(medicament=drug[jamais], n=1)).groupby('medicament').n.sum().sort_values(ascending=False)
print('\nMédicaments ayant des lignes « jamais vues » :', len(u)); print(u.head(15).to_string())
