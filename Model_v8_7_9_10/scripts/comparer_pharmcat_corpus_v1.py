#!/usr/bin/env python3
"""
comparer_pharmcat_corpus_v1.py (7 nov. 2026) : validation EXTERNE de l'étape génotype -> phénotype. LECTURE SEULE.
Compare, pour 150 profils de DÉVELOPPEMENT 1000 Genomes tirés au hasard (graine 2026 ; ensemble final de 138 profils exclu), le phénotype calculé par PharmCAT 3.0.0 (logiciel indépendant,
CPIC/ClinPGx) au codage du corpus (data/profils_genes_v6_complet.csv, lecteur PyPGx). Entrée PharmCAT : VCF multi-échantillons reconstruit depuis les VCF 1KGP par gène du pypgx-bundle
(construire_vcf_multi_pharmcat_v1.py). Règle de comparaison écrite avant lecture : on compare seulement quand PharmCAT donne un phénotype unique (ou un score d'activité pour CYP2C9) ;
« Indeterminate », diplotype ambigu ou « no call » sont comptés à part (pas de désaccord, pas d'accord). CYP2C9 : score d'activité PharmCAT contre 2 x valeur du corpus.
Usage : python3 comparer_pharmcat_corpus_v1.py DOSSIER_PHARMCAT DOSSIER_SORTIE   (DOSSIER_PHARMCAT contient dev150.<échantillon>.report.tsv)
"""
import csv, glob, os, sys
import numpy as np, pandas as pd
PC = sys.argv[1]; OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
P = pd.read_csv(os.path.join(D, 'profils_genes_v6_complet.csv')).set_index('sample_id')
cod = pd.read_csv(os.path.join(D, 'codage_pypgx_valeur_v7.csv')).set_index('phenotype_pypgx').valeur.to_dict()
cod.update({'Normal Function': 1.0, 'Decreased Function': 0.5, 'Poor Function': 0.0, 'Increased Function': 1.5, 'Intermediate Metabolizer': 0.5, 'Poor Metabolizer': 0.0, 'Normal Metabolizer': 1.0, 'Rapid Metabolizer': 1.5, 'Ultrarapid Metabolizer': 2.0, 'Possible Intermediate Metabolizer': 0.5})
def num(a):
    try: return float(str(a).strip())
    except Exception: return None
def lire(r, g):
    ph = (r['Phenotype'] or '').strip()
    if r['Source Diplotype'] == 'no call': return 'no_call', None
    if g == 'CYP2C9':
        a = num(r['Activity Score']); return ('ok', a / 2) if a is not None else ('ambigu_ou_sans_score', None)
    if not ph: return 'vide', None
    vs = []
    for p in [x.strip() for x in ph.split('/')]:
        if p == 'Indeterminate' or p not in cod or pd.isna(cod[p]): return 'indetermine', None
        vs.append(cod[p])
    return ('ok', vs[0]) if len(set(vs)) == 1 else ('ambigu_ou_sans_score', None)
rows = []
for f in sorted(glob.glob(os.path.join(PC, 'dev150.*.report.tsv'))):
    s = os.path.basename(f).split('.')[1]
    for r in csv.DictReader(open(f).read().splitlines()[1:], delimiter='\t'):
        g = r['Gene']
        if g not in P.columns: continue
        st, v = lire(r, g); rows.append(dict(sample=s, gene=g, valeur_corpus=P.at[s, g], genotype_pharmcat=r['Source Diplotype'], phenotype_pharmcat=r['Phenotype'], statut=st, valeur_pharmcat=v))
R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, 'comparaison_detail.csv'), index=False)
out = []
for g, d in R.groupby('gene'):
    ok = d[d.statut == 'ok']; c = ok[ok.valeur_corpus.notna()]; eq = np.isclose(c.valeur_corpus.astype(float), c.valeur_pharmcat.astype(float))
    out.append(dict(gene=g, profils=len(d), comparables=len(c), concordants=int(eq.sum()), discordants=int((~eq).sum()), pharmcat_indetermine=int((d.statut == 'indetermine').sum()),
                    pharmcat_ambigu_ou_sans_score=int((d.statut == 'ambigu_ou_sans_score').sum()), pharmcat_no_call_ou_vide=int(d.statut.isin(['no_call', 'vide']).sum())))
T = pd.DataFrame(out); T.to_csv(os.path.join(OUT, 'comparaison_resume.csv'), index=False); print(T.to_string(index=False))
print('\nTOTAL : comparables %d, concordants %d, discordants %d' % (T.comparables.sum(), T.concordants.sum(), T.discordants.sum()))
print('\nCAS « PharmCAT Indeterminate » : valeur que le corpus (lecteur PyPGx) attribue à ces mêmes profils')
for g in ('DPYD', 'SLCO1B1', 'UGT1A1', 'CYP2B6', 'CYP2C19', 'TPMT', 'NUDT15'):
    d = R[(R.gene == g) & (R.statut == 'indetermine')]
    if len(d): print('  %-8s %3d cas ; valeurs corpus %s ; génotypes PharmCAT fréquents %s' % (g, len(d), d.valeur_corpus.value_counts(dropna=False).to_dict(), d.genotype_pharmcat.value_counts().head(2).to_dict()))
