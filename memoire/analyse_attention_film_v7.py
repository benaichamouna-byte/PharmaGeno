#!/usr/bin/env python3
"""
analyse_attention_film_v7.py : l'attention de la variante film se concentre-t-elle sur les gènes des règles CPIC/DPWG du médicament ?
Entrées : dl_v7_film_oof.npz (prédictions hors-pli, attention par ligne), regles_v2_monogene.csv, regles_v2_multigene.csv
Sortie  : un tableau par médicament (CSV) + un résumé à l'écran. N'écrase rien (écrit uniquement le fichier --out).
Seuls les médicaments dont l'étiquette varie dans les données (44 sur 76) sont évalués : pour les 32 autres, aucun gène ne décide.
Usage   : python3 analyse_attention_film_v7.py dl_v7_film_oof.npz regles_v2_monogene.csv regles_v2_multigene.csv attention_film_v7_par_medicament.csv
"""
import sys
import numpy as np, pandas as pd
oof, mono, multi, out = sys.argv[1:5]
z = np.load(oof, allow_pickle=True)
genes = [str(x) for x in z['genes']]; A = z['attention'].astype(np.float32); drug = z['drug'].astype(str); y = z['y']
m = pd.read_csv(mono); g = pd.read_csv(multi); rg = {}
for _, r in m[(m.ambigu == False) & (m.conflit_intra_source == False)].iterrows(): rg.setdefault(r.medicament, set()).add(r.gene)
for _, r in g[(g.ambigu == False) & (g.conflit_intra_source == False)].iterrows(): rg.setdefault(r.medicament, set()).update([r.gene_a, r.gene_b])
nl = pd.Series(y).groupby(drug).nunique(); var = [d for d in nl.index if nl[d] > 1]
rows = []
for d in var:
    a = A[drug == d].mean(0); rule = [genes.index(x) for x in rg.get(d, []) if x in genes]
    if not rule: continue
    rows.append(dict(medicament=d, genes_regle=';'.join(genes[i] for i in rule), masse_attention_sur_genes_regle=round(float(a[rule].sum()), 4),
                     masse_si_uniforme=round(len(rule) / len(genes), 4), gene_max_attention=genes[int(a.argmax())],
                     gene_max_est_gene_regle=bool(int(a.argmax()) in rule)))
df = pd.DataFrame(rows); df['rapport'] = (df.masse_attention_sur_genes_regle / df.masse_si_uniforme).round(2)
df.to_csv(out, index=False)
print('Médicaments évalués : %d (étiquette constante, non évalués : %d)' % (len(df), len(nl) - len(var)))
print('Masse d\'attention sur les gènes de règle : moyenne %.3f (uniforme : %.3f) | rapport moyen %.2f, médian %.2f' % (
    df.masse_attention_sur_genes_regle.mean(), df.masse_si_uniforme.mean(), df.rapport.mean(), df.rapport.median()))
print('Rapport > 1 : %d/%d | gène de plus forte attention = gène de règle : %d/%d' % ((df.rapport > 1).sum(), len(df), df.gene_max_est_gene_regle.sum(), len(df)))
