#!/usr/bin/env python3
"""
croiser_profils_medicaments_v3.py
Construit le corpus v3 « croisé » : chaque profil génétique réel 1000 Genomes (31 gènes) est associé
à CHAQUE médicament ayant une règle utilisable, et l'étiquette est calculée par construire_corpus_v3.py.
Pourquoi : dans le corpus d'origine, les médicaments d'un échantillon sont choisis à partir de ses variants,
donc le gène « normal » n'apparaît presque jamais avec son médicament (ex. codéine : 1 ligne CYP2D6 = 1.0
sur 635). Le croisement supprime ce biais de sélection. Les profils DOC (artificiels) ne sont pas croisés.
Usage : python3 croiser_profils_medicaments_v3.py CORPUS.csv REGLES_MONO.csv REGLES_MULTI.csv SORTIE_DIR
"""
import sys, os, tempfile
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construire_corpus_v3 as c

corpus, mono_f, multi_f, outdir = sys.argv[1:5]
df = pd.read_csv(corpus)
genes = [x for x in df.columns if x not in ('drug', 'action', 'sample_id', 'family_id')]
real = df[~df.sample_id.str.startswith('DOC')]
prof = real.drop_duplicates('sample_id')
# contrôle : un même échantillon doit avoir un profil unique
chk = real.groupby('sample_id')[genes].nunique().max().max()
print('Profils 1KGP :', len(prof), '| max de valeurs distinctes par gène au sein d\'un échantillon :', chk)
assert chk == 1, "profil non unique pour au moins un échantillon"
mono = pd.read_csv(mono_f); multi = pd.read_csv(multi_f)
meds = sorted(set(mono.medicament.str.lower()) | set(multi.medicament.str.lower()))
present = set(df.drug.str.lower())
meds = [m for m in meds if m in present]
rows = []
base = prof[['sample_id', 'family_id'] + genes]
for m in meds:
    t = base.copy(); t['drug'] = m; t['action'] = 'STANDARD'  # valeur provisoire, recalculée
    rows.append(t)
cross = pd.concat(rows, ignore_index=True)[genes + ['drug', 'action', 'sample_id', 'family_id']]
tmp = os.path.join(tempfile.mkdtemp(), 'croise.csv'); cross.to_csv(tmp, index=False)
print('Croisement :', len(prof), 'profils x', len(meds), 'médicaments =', len(cross), 'lignes')
c.main(tmp, mono_f, multi_f, outdir)
os.replace(os.path.join(outdir, 'phenotype_drug_dataset_v3.csv'), os.path.join(outdir, 'phenotype_drug_dataset_v3_croise.csv'))
# la colonne action_ancienne n'a pas de sens ici (valeur provisoire) : retirée pour éviter tout mauvais usage
f = os.path.join(outdir, 'phenotype_drug_dataset_v3_croise.csv')
x = pd.read_csv(f).drop(columns=['action_ancienne']); x.to_csv(f, index=False)
for n in ('ancienne_vs_v3_croisement.csv',):
    q = os.path.join(outdir, n)
    if os.path.exists(q): os.remove(q)
print('Colonnes finales :', x.columns.tolist()[-8:])
