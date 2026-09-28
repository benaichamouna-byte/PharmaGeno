"""
build_drug_dictionary.py — Dictionnaire documentaire des medicaments du dataset v2

Niveau A : documentation seule. Ne modifie ni le dataset ni les modeles.
Produit l'Annexe du memoire sur la couverture moleculaire.

Classification de chaque medicament :
- OK_FINGERPRINT : petite molecule avec Morgan FP disponible
- PARSING_ERROR : fragment issu d'un defaut de lecture CSV (virgules non protegees)
- CLASSE_THERAPEUTIQUE : classe et non molecule, aucune structure unique
- BIOLOGIQUE : proteine, anticorps, polymere, vaccin — hors perimetre Morgan FP
- COMBINAISON : association de plusieurs principes actifs
- PETITE_MOLECULE_MANQUANTE : structure PubChem existante, FP recuperable (perspective)

Sorties : drug_dictionary.csv, drug_coverage_report.md
"""
import pandas as pd, pickle, re, json

DATA_DIR    = '/home/mouna/projet_memoire/model_v2/data'
DOCS_DIR    = '/home/mouna/projet_memoire/model_v2/docs'
import os; os.makedirs(DOCS_DIR, exist_ok=True)

df = pd.read_csv(f'{DATA_DIR}/phenotype_drug_dataset_complet_v2.csv')
with open(f'{DATA_DIR}/drug_fingerprints.pkl','rb') as f: fp = pickle.load(f)

drugs = sorted(df['drug'].unique())

PARSING_ERROR = {
    '"1', '3', '7-dimethylxanthine"', '"caffeine"', '"ribavirin"',
    '"interferon alfa-2a', 'recombinant"', 'primaquine 5',
}

CLASSE_THERAPEUTIQUE = {
    'aminoglycoside antibacterials', 'anesthesiques', 'antidepressants',
    'antiepileptics', 'antineoplastic agents', 'antipsychotics',
    'bcr-abl tyrosine kinase inhibitors', 'dihydropyridine derivatives',
    'drugs used in nicotine dependence', 'hmg-coa reductase inhibitors',
    'non-nucleoside reverse transcriptase inhibitors', 'opioid anesthetics',
    'other general anesthetics', 'proton pump inhibitors', 'purine analogues',
    'selective serotonin reuptake inhibitors', 'sulfonamides',
    'urea derivatives', 'vitamin k and analogues', 'volatile anesthetics',
}

BIOLOGIQUE = {
    'heparin', 'tocilizumab', 'etanercept', 'pegloticase', 'rasburicase',
    'mirvetuximab soravtansine', 'sacituzumab govitecan', 'tebentafusp',
    'peginterferon alfa-2a', 'peginterferon alfa-2b', 'interferon beta-1a',
    'measles vaccines', 'rubella vaccines',
}

METABOLITE_SANS_FP = {
    '2-hydroxyatorvastatin lactone', '4-hydroxyatorvastatin lactone',
    '4-dehydrocilostazol', '6-orthoquinone', 'alpha-hydroxy sertraline ketone',
    'cotinine', 'desethyl hydroxychloroquine', 'erythro-4-hydroxyhydrobupropion',
    'threo-4-hydroxyhydrobupropion', 'losartan e-3174', 'n-desalkylquetiapine',
    'n-didesmethyltramadol', 'pentoxifylline m5', 'r-eddp', 's-eddp',
    'r-methylphenobarbital', 'r-norfluoxetine', 's-norfluoxetine',
    'raloxifene-4\u2032-glucuronide', 'thioguanosine diphosphate',
}

FORME_GALENIQUE = {'pantoprazole sodium granules'}

PETITE_MOLECULE_MANQUANTE = {
    'ambrisentan', 'amoxicillin', 'bepridil', 'caffeine', 'cilostazol',
    'donepezil', 'ivermectin', 'levonorgestrel', 'nelfinavir', 'oxaliplatin',
    'phenazepam', 'progesterone', 'sorafenib', 'tolperisone', 'tolterodine',
    'vardenafil', 'vincristine', 'mephedrone', 'vitamin k1', 'dimolegin',
    '4-methylenedioxymethamphetamine',
}

# Metabolites : molecules distinctes, NE PAS fusionner avec la molecule mere
PREFIXES_METABOLITE = ('nor', 'n-des', 'o-des', 'n-didesmethyl', 'r-', 's-',
                       '2-hydroxy', '4-hydroxy', '6-', 'erythro-', 'threo-',
                       'alpha-hydroxy', 'desethyl', 'thioguanosine')
SUFFIXES_SEL = ['hydrochloride','sodium','sulfate','maleate','tartrate','citrate',
                'mesylate','besylate','succinate','acetate','phosphate','potassium',
                'calcium','bromide','fumarate','lactate','nitrate','oxalate',
                'granules','saccharate','aspartate']

def base_saline(nom):
    """Retire uniquement le suffixe de sel. Ne touche pas aux metabolites."""
    b = nom.lower().strip()
    for s in SUFFIXES_SEL:
        if b.endswith(' ' + s):
            return b[:-(len(s)+1)].strip()
    return None

def est_metabolite(nom):
    n = nom.lower()
    return any(n.startswith(p) for p in PREFIXES_METABOLITE)

# Groupes salins (vrais doublons)
groupes_salins = {}
for d in drugs:
    b = base_saline(d)
    if b and b in [x.lower() for x in drugs]:
        groupes_salins.setdefault(b, []).append(d)

rows = []
for d in drugs:
    n_lignes = int((df['drug'] == d).sum())
    a_fp     = d in fp

    if d in PARSING_ERROR:
        statut, note = 'PARSING_ERROR', 'Fragment issu d une virgule non protegee dans le CSV source'
    elif d in CLASSE_THERAPEUTIQUE:
        statut, note = 'CLASSE_THERAPEUTIQUE', 'Classe therapeutique — aucune structure chimique unique'
    elif d in BIOLOGIQUE:
        statut, note = 'BIOLOGIQUE', 'Proteine / anticorps / polymere / vaccin — hors perimetre Morgan FP'
    elif '/' in d or ' and ' in d:
        statut, note = 'COMBINAISON', 'Association de plusieurs principes actifs'
    elif d in METABOLITE_SANS_FP:
        statut, note = 'METABOLITE_SANS_FP', 'Metabolite — structure disponible mais absente du referentiel PubChem interroge'
    elif d in FORME_GALENIQUE:
        statut, note = 'FORME_GALENIQUE', 'Forme galenique du principe actif deja present dans le dataset'
    elif d in PETITE_MOLECULE_MANQUANTE:
        statut, note = 'PETITE_MOLECULE_MANQUANTE', 'Structure PubChem disponible — FP recuperable (perspective)'
    elif a_fp:
        statut, note = 'OK_FINGERPRINT', ''
    else:
        statut, note = 'NON_CLASSE', 'A investiguer'

    bs = base_saline(d)
    forme_saline = bs if (bs and bs in groupes_salins) else ''

    rows.append({
        'medicament': d,
        'n_lignes': n_lignes,
        'fingerprint_disponible': a_fp,
        'dimension_fp': len(fp[d]) if a_fp else '',
        'statut': statut,
        'est_metabolite': est_metabolite(d),
        'forme_saline_de': forme_saline,
        'note': note,
    })

dd = pd.DataFrame(rows).sort_values(['statut','medicament'])
dd.to_csv(f'{DOCS_DIR}/drug_dictionary.csv', index=False)

# Rapport
stats = dd['statut'].value_counts().to_dict()
n_tot, n_fp = len(dd), int(dd['fingerprint_disponible'].sum())
lignes_fp  = int(dd.loc[dd['fingerprint_disponible'], 'n_lignes'].sum())
lignes_tot = int(dd['n_lignes'].sum())

r = ['# Couverture moleculaire du dataset v2', '',
     f'Medicaments distincts : **{n_tot}**',
     f'Avec Morgan Fingerprint : **{n_fp}** ({n_fp/n_tot*100:.1f} %)',
     f'Lignes couvertes : **{lignes_fp} / {lignes_tot}** ({lignes_fp/lignes_tot*100:.1f} %)',
     '', '## Repartition par statut', '',
     '| Statut | Medicaments | Lignes |', '|---|---|---|']
for s, n in sorted(stats.items(), key=lambda x: -x[1]):
    r.append(f"| {s} | {n} | {int(dd[dd['statut']==s]['n_lignes'].sum())} |")

r += ['', '## Interpretation', '',
      'Les 93 medicaments sans fingerprint ne constituent pas une lacune homogene. Quatre situations distinctes :', '',
      '1. **Classes therapeutiques** — un nom de classe ne correspond a aucune structure chimique unique. Exclusion methodologiquement justifiee.',
      '2. **Biologiques** — les Morgan Fingerprints encodent les sous-structures de petites molecules. Proteines, anticorps et polymeres sont hors du perimetre de la methode.',
      '3. **Erreurs de parsing** — fragments produits par des virgules non protegees dans le fichier source (ex. 1,3,7-trimethylxanthine scinde en trois entrees). Defaut technique identifie, corrigeable.',
      '4. **Metabolites** — produits de transformation d une molecule mere (ex. cotinine pour la nicotine, losartan E-3174 pour le losartan). Leur structure existe mais n a pas ete recuperee lors de la construction du referentiel. Molecules chimiquement distinctes de leur molecule mere : elles ne doivent pas etre fusionnees avec elle.',
      '5. **Petites molecules manquantes** — lacune reelle. Structures disponibles sur PubChem, fingerprints recuperables.',
      '', '## Formes salines', '',
      f'{len(groupes_salins)} groupes ou une molecule apparait sous forme libre et sous forme saline ',
      '(ex. warfarin / warfarin sodium). Ces paires designent le meme principe actif et pourraient etre fusionnees.',
      'Fusion non appliquee a ce stade : elle modifierait les profils et invaliderait les resultats de validation croisee.',
      '', '## Metabolites — distinction importante', '',
      'Les entrees prefixees nor-, N-des-, O-des-, R-, S-, hydroxy- designent des **metabolites**, ',
      'molecules chimiquement distinctes de la molecule mere. Elles ne doivent pas etre fusionnees.',
      f"Le dataset en contient {int(dd['est_metabolite'].sum())}.",
      '', '## Impact sur les resultats', '',
      f'Les modeles sont entraines sur les {lignes_fp} lignes disposant d un fingerprint, ',
      f'soit {lignes_fp/lignes_tot*100:.1f} % du dataset. Les entrees non couvertes sont exclues ',
      'en amont et n influencent aucune metrique rapportee.']

with open(f'{DOCS_DIR}/drug_coverage_report.md','w') as f:
    f.write('\n'.join(r))

print(f'Medicaments : {n_tot} | Avec FP : {n_fp} ({n_fp/n_tot*100:.1f}%)')
print(f'Lignes couvertes : {lignes_fp}/{lignes_tot} ({lignes_fp/lignes_tot*100:.1f}%)')
print()
for s, n in sorted(stats.items(), key=lambda x: -x[1]):
    print(f'  {s:28s} {n:3d} medicaments')
print()
print(f'Groupes de formes salines : {len(groupes_salins)}')
print(f'Metabolites identifies    : {int(dd["est_metabolite"].sum())}')
print()
print('Fichiers : docs/drug_dictionary.csv, docs/drug_coverage_report.md')
