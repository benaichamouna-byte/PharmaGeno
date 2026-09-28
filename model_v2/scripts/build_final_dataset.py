"""
build_final_dataset.py — Reconstruction des identifiants d individu et de famille

Objectif : rattacher chaque ligne du jeu de donnees a l individu dont elle provient,
puis a sa famille, afin de permettre une validation croisee groupee (StratifiedGroupKFold).

Methode :
1. Appariement du dataset v2 avec phenotype_drug_dataset_1kg.csv, qui a conserve
   la colonne sample. Cle : 16 phenotypes geniques communs + medicament + action.
2. Rattachement de chaque individu a sa famille via 1kGP_3202_pedigree.txt.
   Un trio parent-parent-enfant recoit un identifiant de famille commun.
3. Les lignes non appariees proviennent du corpus documentaire (PharmGKB, CPIC,
   ClinVar, FDA) et ne correspondent a aucun individu sequence. Chacune recoit
   un groupe propre, ce qui les rend neutres vis-a-vis du groupement.

Sorties : data/phenotype_drug_dataset_FINAL.csv, docs/sample_family_report.md
"""
import pandas as pd, hashlib, os

DATA_DIR = '/home/mouna/projet_memoire/model_v2/data'
DOCS_DIR = '/home/mouna/projet_memoire/model_v2/docs'
PED_PATH = '/home/mouna/projet_memoire/data/1kGP_3202_pedigree.txt'
os.makedirs(DOCS_DIR, exist_ok=True)

v2 = pd.read_csv(f'{DATA_DIR}/phenotype_drug_dataset_complet_v2.csv')
kg = pd.read_csv(f'{DATA_DIR}/phenotype_drug_dataset_1kg.csv')
print(f'Dataset v2 : {len(v2)} lignes')
print(f'Source 1kg : {len(kg)} lignes, {kg["sample"].nunique()} individus')

GENES_V2 = sorted([c for c in v2.columns if c not in ('drug','action')])
GENES_KG = sorted([c for c in kg.columns if c not in ('drug','action','sample','gene','phenotype')])
COMMUNS  = sorted(set(GENES_V2) & set(GENES_KG))
print(f'Genes communs pour l appariement : {len(COMMUNS)}')

# --- 1. Appariement individu -------------------------------------------------
cle_kg = kg[COMMUNS + ['drug','action']].astype(str).agg('|'.join, axis=1)
cle_v2 = v2[COMMUNS + ['drug','action']].astype(str).agg('|'.join, axis=1)

# En cas de cle partagee par plusieurs individus, on retient le premier
mapping = {}
for k, s in zip(cle_kg, kg['sample']):
    mapping.setdefault(k, s)

v2['sample_id'] = cle_v2.map(mapping)
n_app = int(v2['sample_id'].notna().sum())
print(f'\nLignes appariees : {n_app}/{len(v2)} ({n_app/len(v2)*100:.1f} %)')
print(f'Individus identifies : {v2["sample_id"].nunique()}')

# --- 2. Rattachement familial ------------------------------------------------
ped = {}
with open(PED_PATH) as f:
    next(f)
    for line in f:
        p = line.split()
        if len(p) >= 3:
            ped[p[0]] = (p[1], p[2])   # sample -> (pere, mere)

# Un individu ayant des parents renseignes partage leur identifiant de famille.
# On prend le pere comme racine du trio, la mere sinon.
def famille(s):
    if pd.isna(s):
        return None
    pere, mere = ped.get(s, ('0','0'))
    if pere != '0':
        return f'FAM_{pere}'
    if mere != '0':
        return f'FAM_{mere}'
    return f'FAM_{s}'          # individu sans parent renseigne : famille a lui seul

v2['family_id'] = v2['sample_id'].map(famille)

# Un parent doit porter le meme family_id que son enfant
enfants = v2[v2['sample_id'].notna()]['sample_id'].unique()
parents_vers_fam = {}
for e in enfants:
    pere, mere = ped.get(e, ('0','0'))
    if pere != '0':
        parents_vers_fam[pere] = f'FAM_{pere}'
        if mere != '0':
            parents_vers_fam[mere] = f'FAM_{pere}'

mask_parent = v2['sample_id'].isin(parents_vers_fam)
v2.loc[mask_parent, 'family_id'] = v2.loc[mask_parent, 'sample_id'].map(parents_vers_fam)

# --- 3. Lignes documentaires : un groupe propre chacune -----------------------
mask_doc = v2['sample_id'].isna()
v2.loc[mask_doc, 'sample_id'] = ['DOC_' + str(i) for i in range(int(mask_doc.sum()))]
v2.loc[mask_doc, 'family_id'] = v2.loc[mask_doc, 'sample_id']

# --- 4. Mesure du risque de fuite --------------------------------------------
reels = v2[~v2['sample_id'].astype(str).str.startswith('DOC_')]
n_ind   = reels['sample_id'].nunique()
n_fam   = reels['family_id'].nunique()
tailles = reels.groupby('family_id')['sample_id'].nunique()
fam_mult = tailles[tailles > 1]
ind_app = int(fam_mult.sum())

print(f'\n--- Structure familiale ---')
print(f'Individus reels          : {n_ind}')
print(f'Familles distinctes      : {n_fam}')
print(f'Familles a plusieurs     : {len(fam_mult)}')
print(f'Individus apparentes     : {ind_app} ({ind_app/n_ind*100:.1f} % des individus)')
lignes_app = int(reels[reels['family_id'].isin(fam_mult.index)].shape[0])
print(f'Lignes concernees        : {lignes_app} ({lignes_app/len(v2)*100:.1f} % du dataset)')

# --- 5. Sauvegarde ------------------------------------------------------------
ordre = GENES_V2 + ['drug','action','sample_id','family_id']
final = v2[ordre]
out = f'{DATA_DIR}/phenotype_drug_dataset_FINAL.csv'
final.to_csv(out, index=False)

sha = hashlib.sha256(open(out,'rb').read()).hexdigest()
print(f'\nFichier : phenotype_drug_dataset_FINAL.csv')
print(f'SHA256  : {sha}')

# --- 6. Rapport ---------------------------------------------------------------
r = ['# Reconstruction des identifiants d individu et de famille', '',
     f'Jeu de donnees : **{len(final)} lignes**, {len(GENES_V2)} genes, {final["drug"].nunique()} medicaments',
     f'SHA256 : `{sha}`', '',
     '## Appariement', '',
     'Chaque ligne du jeu de donnees a ete confrontee au fichier intermediaire ',
     '`phenotype_drug_dataset_1kg.csv`, qui avait conserve la colonne `sample`. ',
     f'La cle d appariement combine les {len(COMMUNS)} phenotypes geniques communs, le medicament et l action.', '',
     '| | Lignes | Part |', '|---|---|---|',
     f'| Rattachees a un individu sequence | {n_app} | {n_app/len(v2)*100:.1f} % |',
     f'| Issues du corpus documentaire | {len(v2)-n_app} | {(len(v2)-n_app)/len(v2)*100:.1f} % |',
     '',
     'Les lignes non rattachees proviennent de PharmGKB, CPIC, ClinVar et de la FDA. ',
     'Ce sont des associations documentaires, non des profils d individus sequences : ',
     'elles ne peuvent recevoir aucun identifiant. Chacune forme un groupe a elle seule, ',
     'ce qui les rend neutres vis-a-vis du groupement lors de la validation croisee.', '',
     '## Structure familiale', '',
     '| | Valeur |', '|---|---|',
     f'| Individus sequences identifies | {n_ind} |',
     f'| Familles distinctes | {n_fam} |',
     f'| Familles comptant plusieurs membres | {len(fam_mult)} |',
     f'| Individus apparentes | {ind_app} ({ind_app/n_ind*100:.1f} %) |',
     f'| Lignes concernees | {lignes_app} ({lignes_app/len(v2)*100:.1f} %) |',
     '', '## Portee', '',
     'Un individu apparente a un autre partage une part substantielle de son genome. ',
     'Si un parent figure dans le pli d entrainement et son enfant dans le pli de test, ',
     'la performance mesuree est optimiste : le modele a deja vu un profil proche. ',
     'Les identifiants reconstruits permettent d imposer qu une famille entiere reste ',
     'du meme cote de la separation, au moyen d un `StratifiedGroupKFold` sur `family_id`.', '',
     '## Colonnes ajoutees', '',
     '- `sample_id` — identifiant de l individu 1000 Genomes, ou identifiant documentaire `DOC_n`',
     '- `family_id` — identifiant de famille ; un trio parent-parent-enfant en partage un seul']

with open(f'{DOCS_DIR}/sample_family_report.md','w') as f:
    f.write('\n'.join(r))

print('Rapport : docs/sample_family_report.md')
