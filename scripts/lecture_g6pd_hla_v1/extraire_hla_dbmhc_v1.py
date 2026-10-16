#!/usr/bin/env python3
"""
extraire_hla_dbmhc_v1.py : extrait de l'archive dbMHC (NCBI, Final Archive 2018) les typages HLA (A, B, C, DRB1, DQB1) des échantillons dont
l'identifiant est de type NA/HG (Coriell / 1000 Genomes). LECTURE SEULE : ne modifie aucun fichier d'entrée.
Entrées (dans le dossier courant) : ihwg_sample.txt.gz, diplotype.txt.gz, locus.txt.gz  (source : ftp.ncbi.nlm.nih.gov/pub/mhc/mhc/Final Archive/Database/Data)
Sortie : hla_1000g_dbmhc_brut_v1.csv (une ligne par échantillon x locus, provenance conservée) + copie dans le dossier Téléchargements Windows.
Attention : plusieurs projets dbMHC sont mélangés (project_id, load_info) ; nomenclature ancienne sans deux-points (B*1502 = B*15:02).
Usage : cd ~/dbmhc_archive && python3 extraire_hla_dbmhc_v1.py
"""
import os, re, shutil
import pandas as pd

R = lambda f: pd.read_csv(f + '.txt.gz', sep='|', dtype=str, low_memory=False)
s = R('ihwg_sample'); d = R('diplotype'); l = R('locus')
pat = re.compile(r'(?:NA|HG)\d{5}')


def ident(r):
    for c in ('ihwg_id', 'source_sample_id', 'submit_source_id'):
        m = pat.search(str(r[c]) if pd.notna(r[c]) else '')
        if m:
            return m.group(0)
    return None


s['id'] = s.apply(ident, axis=1)
s = s[s.id.notna()][['sample_nr', 'id', 'ihwg_id', 'source_sample_id', 'project_id']].rename(columns={'project_id': 'project_sample'})
l = l[['locus_id', 'locus_name']]
d = d.merge(s, on='sample_nr').merge(l, left_on='marker_id', right_on='locus_id', how='left')
d = d[d.locus_name.isin(['HLA-A', 'HLA-B', 'HLA-C', 'HLA-DRB1', 'HLA-DQB1'])]
cols = ['id', 'sample_nr', 'locus_name', 'allele1', 'allele2', 'marker_type', 'load_info', 'project_id', 'project_sample', 'ihwg_id', 'source_sample_id']
out = d[cols].sort_values(['id', 'locus_name', 'sample_nr'])
out.to_csv('hla_1000g_dbmhc_brut_v1.csv', index=False)

b = out[out.locus_name == 'HLA-B'].copy()
b['paire'] = [tuple(sorted([x, y])) for x, y in zip(b.allele1, b.allele2)]
print('lignes', len(out), '| identifiants distincts', out.id.nunique(), '| avec HLA-B', b.id.nunique())
print('typages HLA-B par identifiant :'); print(b.groupby('id').size().value_counts().to_string())
print('identifiants avec typages HLA-B discordants :', int((b.groupby('id').paire.nunique() > 1).sum()))
print('project_id (HLA-B) :'); print(b.project_id.value_counts().head(8).to_string())
print('load_info (HLA-B) :'); print(b.load_info.value_counts().head(8).to_string())
print('longueur du nombre allélique HLA-B :'); print(b.allele1.str.extract(r'\*(\d+)')[0].str.len().value_counts().to_string())
for a in ['B*1502', 'B*5701', 'B*5801']:
    print(a, ': identifiants porteurs =', b[b.allele1.str.startswith(a) | b.allele2.str.startswith(a)].id.nunique())
dest = '/mnt/c/Users/MSI/Downloads'
if os.path.isdir(dest):
    shutil.copy('hla_1000g_dbmhc_brut_v1.csv', dest); print('COPIE OK ->', dest)
else:
    print('Dossier Téléchargements introuvable : le CSV reste dans', os.getcwd())
