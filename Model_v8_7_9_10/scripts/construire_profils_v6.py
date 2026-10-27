#!/usr/bin/env python3
"""
construire_profils_v6.py : profils_genes_v6.csv = profils_genes_v5.csv dont 8 gènes (ABCG2, CYP2B6, CYP2C19, CYP2C9, CYP3A5, DPYD, F5, UGT1A1) sont RECALCULÉS avec exactement
la fonction de codage du lecteur de VCF de l'application (vcf_to_profile_v9.coder_gene) à partir des sorties PyPGx 0.27.0 (pgxrun/<GENE>/genotypes.zip et phenotypes.zip).
Raison : ces 8 gènes venaient du corpus v3 (valeurs d'origine) ; la concordance avec PyPGx mesurée le 15 oct. était de 92,8 % (CYP2B6) à 100 %, et un génotype INDÉTERMINÉ pour PyPGx
y était codé 1,0 (« normal »), alors que le lecteur de l'application répond « non déterminé » : l'application aurait lu un patient autrement que l'entraînement.
Désormais indéterminé = valeur manquante (NaN) + indicateur <gène>_manquant au moment de l'entraînement. Les 9 autres gènes dépendant du génotype étaient déjà identiques (0 différence, 23 oct.).
Sorties : data/profils_genes_v6.csv ; data/profils_v6_differences_vs_v5.csv (une ligne par profil et gène modifié : ancienne valeur, nouvelle valeur, génotype, phénotype PyPGx).
Usage : python3 construire_profils_v6.py --pgx /home/claude/pgxrun
"""
import argparse, io, os, sys, zipfile
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vcf_to_profile_v9 as v9
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data') + os.sep
GENES = ['ABCG2', 'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP3A5', 'DPYD', 'F5', 'UGT1A1']

def lire(z):
    zf = zipfile.ZipFile(z); return pd.read_csv(io.BytesIO(zf.read([n for n in zf.namelist() if n.endswith('data.tsv')][0])), sep='\t', index_col=0)

ap = argparse.ArgumentParser(); ap.add_argument('--pgx', required=True); a = ap.parse_args()
P = pd.read_csv(D + 'profils_genes_v5.csv')
P = P.drop(columns=[c for c in P.columns if c.endswith('_ancien_codage')])
codage = v9.v8.charger_codage(D + 'codage_pypgx_valeur_v7.csv'); tables, _ = v9.v8.charger_tables(D + 'tables_cpic_v8.json')
diffs = []
for g in GENES:
    if not os.path.exists(os.path.join(a.pgx, g, 'phenotypes.zip')):
        print('%-8s ABSENT : sortie PyPGx pas encore disponible, gène NON recalculé' % g); continue
    gt = lire(os.path.join(a.pgx, g, 'genotypes.zip'))['Genotype']; ph = lire(os.path.join(a.pgx, g, 'phenotypes.zip'))['Phenotype']
    assert set(P.sample_id) <= set(gt.index), g + ' : échantillons manquants dans la sortie PyPGx'
    new = []
    for s in P.sample_id:
        val, motif, util = v9.coder_gene(g, gt[s], ph[s], tables, codage); new.append(np.nan if val is None else val)
    new = pd.Series(new, index=P.index); old = P[g]
    ch = ~((new == old) | (new.isna() & old.isna()))
    for i in P.index[ch]: diffs.append(dict(sample_id=P.sample_id[i], gene=g, valeur_v5=old[i], valeur_v6=new[i], genotype_pypgx=gt[P.sample_id[i]], phenotype_pypgx=ph[P.sample_id[i]]))
    print('%-8s modifiés %4d | indéterminés (NaN) %3d' % (g, int(ch.sum()), int(new.isna().sum())))
    P[g] = new; P[g + '_source'] = 'pypgx_lecteur_v9'
P.to_csv(D + 'profils_genes_v6.csv', index=False); pd.DataFrame(diffs).to_csv(D + 'profils_v6_differences_vs_v5.csv', index=False)
print('profils v6 :', len(P), '| différences écrites :', len(diffs))
