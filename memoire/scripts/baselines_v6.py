#!/usr/bin/env python3
"""
baselines_v6.py : points de repère (sans apprentissage profond) pour interpréter les résultats de train_dl_v6.py.
Même corpus (phenotype_drug_dataset_v3_croise.csv), même découpage que le DL : StratifiedGroupKFold(5), graine 42, groupes = family_id.
Trois repères :
  1. 'classe majoritaire'      : prédit toujours la classe la plus fréquente de l'entraînement
  2. 'medicament seul'         : prédit la classe la plus fréquente pour ce médicament (n'utilise AUCUN gène)
  3. 'table medicament+genes'  : table de consultation (médicament + valeurs des gènes cités par ses règles de guideline).
                                 Ce n'est PAS un modèle candidat : les étiquettes viennent de ces règles, donc ce repère
                                 mesure ce qu'il faut deviner (quels gènes comptent pour quel médicament).
Usage : python3 baselines_v6.py phenotype_drug_dataset_v3_croise.csv regles_v2_monogene.csv regles_v2_multigene.csv baselines_v6_resultats.csv
"""
import sys
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, recall_score

GEN = ['ABCG2','CYP2B6','CYP2C19','CYP2C9','CYP2D6','CYP3A5','DPYD','F5','NUDT15','SLCO1B1','TPMT','UGT1A1']  # mêmes 12 gènes que le DL
data, f_mono, f_multi, f_out = sys.argv[1:5]
df = pd.read_csv(data); mono = pd.read_csv(f_mono); multi = pd.read_csv(f_multi)
for t in (mono, multi): t['medicament'] = t.medicament.str.lower().str.strip()
rg = {}
for r in mono.itertuples(): rg.setdefault(r.medicament, set()).add(r.gene)
for r in multi.itertuples(): rg.setdefault(r.medicament, set()).update([r.gene_a, r.gene_b])
rg = {d: [x for x in GEN if x in s] for d, s in rg.items()}

le = LabelEncoder(); y = le.fit_transform(df.action); ev = list(le.classes_).index('EVITER')
dr = df.drug.values; cols = df[GEN].astype(str).values; gi = {x: i for i, x in enumerate(GEN)}
cle = pd.Series([d + '#' + '|'.join(cols[i][gi[x]] for x in rg.get(d.lower(), [])) for i, d in enumerate(dr)]).values

def mode(keys, yy):
    t = pd.crosstab(keys, yy); return pd.Series(t.values.argmax(1), index=t.index)

lignes = []
for k, (tr, te) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=42).split(df, y, df.family_id.values)):
    assert not (set(df.family_id.values[tr]) & set(df.family_id.values[te]))
    maj = np.bincount(y[tr]).argmax()
    dm = mode(dr[tr], y[tr]); p_drug = pd.Series(dr[te]).map(dm).fillna(maj).astype(int).values
    tm = mode(cle[tr], y[tr]); p_tab = pd.Series(cle[te]).map(tm).fillna(pd.Series(p_drug)).astype(int).values
    for nom, p in [('classe majoritaire', np.full(len(te), maj)), ('medicament seul', p_drug), ('table medicament+genes', p_tab)]:
        rec = recall_score(y[te], p, average=None, labels=range(len(le.classes_)), zero_division=0)
        lignes.append(dict(repere=nom, pli=k + 1, f1_macro=f1_score(y[te], p, average='macro'), CER_strict=1 - rec[ev]))
res = pd.DataFrame(lignes); res.to_csv(f_out, index=False)
print(res.groupby('repere')[['f1_macro', 'CER_strict']].agg(['mean', 'std']).round(4).to_string())
