#!/usr/bin/env python3
"""
tableau_profil_medicaments_v1.py : construit le tableau « 1 profil -> 1 recommandation par médicament » (aucun entraînement).
Lit le corpus v7. Écrit ../results/tableau_profil_medicaments_v1.csv (lignes = profils, colonnes = médicaments, cases vides = pas d'étiquette)
et ../results/tableau_profil_medicaments_v1_sortie.txt. Vérifie que le profil (colonnes de gènes) est identique sur toutes les lignes d'un même profil.
Usage : python3 tableau_profil_medicaments_v1.py --data ../data/phenotype_drug_dataset_v7.csv --out ../results
"""
import argparse, os, io
import pandas as pd

ap = argparse.ArgumentParser(); ap.add_argument('--data', required=True); ap.add_argument('--out', required=True); a = ap.parse_args()
os.makedirs(a.out, exist_ok=True); buf = io.StringIO()
def p(*x):
    s = ' '.join(str(i) for i in x); print(s); buf.write(s + '\n')

df = pd.read_csv(a.data, low_memory=False)
meta = {'sample_id', 'drug', 'action'}
genes = [c for c in df.columns if c not in meta and not c.startswith(('famille', 'family', 'groupe', 'group'))]
p('lignes :', len(df), '| profils :', df.sample_id.nunique(), '| médicaments :', df.drug.nunique())
# le profil doit être identique sur toutes les lignes d'un même profil
nun = df.groupby('sample_id')[genes].nunique(dropna=False).max()
variables = [g for g in genes if nun[g] > 1]
p('colonnes de profil :', len(genes), '| colonnes qui changent d\'une ligne à l\'autre pour un même profil :', len(variables), variables[:10])
T = df.pivot_table(index='sample_id', columns='drug', values='action', aggfunc='first')
T.to_csv(os.path.join(a.out, 'tableau_profil_medicaments_v1.csv'))
n = T.notna().sum(axis=1)
p('tableau :', T.shape[0], 'profils x', T.shape[1], 'médicaments | cases remplies :', int(T.notna().sum().sum()), 'sur', T.shape[0] * T.shape[1])
p('médicaments étiquetés par profil : min', int(n.min()), '| médiane', int(n.median()), '| max', int(n.max()))
p('\nExemple : 1 profil (la première ligne du tableau), médicaments à adapter ou à éviter :')
r = T.iloc[0]; p('  profil :', T.index[0]); p(r[r.isin(['ADAPTER_DOSE', 'EVITER', 'SURVEILLER'])].to_string())
p('\nActions par médicament (les 8 premiers par nombre de profils non STANDARD) :')
ns = (T != 'STANDARD').where(T.notna()).sum().sort_values(ascending=False).head(8); p(ns.to_string())
open(os.path.join(a.out, 'tableau_profil_medicaments_v1_sortie.txt'), 'w', encoding='utf-8').write(buf.getvalue())
