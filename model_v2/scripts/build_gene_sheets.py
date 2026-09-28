"""
build_gene_sheets.py — Fiches documentaires par gene (Annexe A du memoire)

Construit une fiche par gene du panel a partir des donnees reelles du projet.
Aucune valeur n est inventee : ce qui n est pas verifiable est marque NON_DOCUMENTE.

Sources exploitees :
- phenotype_drug_dataset_complet_v2.csv : valeurs observees, medicaments associes
- vcf_genotypes_all_genes_remapped.pkl  : genes extraits des VCF 1000 Genomes
- 1kgp_pgx_combined.csv                 : genes issus de PyPGx

Sorties : docs/gene_sheets.csv, docs/gene_sheets.md
"""
import pandas as pd, pickle, os, json

DATA_DIR = '/home/mouna/projet_memoire/model_v2/data'
DOCS_DIR = '/home/mouna/projet_memoire/model_v2/docs'
os.makedirs(DOCS_DIR, exist_ok=True)

df = pd.read_csv(f'{DATA_DIR}/phenotype_drug_dataset_complet_v2.csv')
GENES = sorted([c for c in df.columns if c not in ('drug','action')])

# Genes extraits par nous depuis les VCF 1000 Genomes — variants et positions verifies
VCF_EXTRACTION = {
    'VKORC1':  ('rs9923231',  'chr16:31096368',  'CPIC niveau A — warfarine (2017)'),
    'CYP4F2':  ('rs2108622',  'chr19:15879621',  'CPIC niveau A — warfarine (2017)'),
    'G6PD':    ('rs1050828',  'chrX:154536002',  'CPIC niveau A — deficit en G6PD (2022)'),
    'NAT2':    ('rs1799930',  'chr8:18400593',   'CPIC — hydralazine'),
    'IFNL3':   ('rs12979860', 'chr19:39248147',  'CPIC — interferon / ribavirine'),
    'CYP1A2':  ('rs762551',   'chr15:74749576',  'Pas de ligne directrice CPIC niveau A'),
    'CYP2A6':  ('rs1801272',  'chr19:40848628',  'Pas de ligne directrice CPIC niveau A'),
    'CYP3A4':  ('rs2740574',  'chr7:99784473',   'Pas de ligne directrice CPIC niveau A'),
    'SLC19A1': ('rs1051266',  'chr21:45537880',  'Pas de ligne directrice CPIC niveau A'),
    'ACE':     ('rs4343 (proxy de rs1799752)', 'chr17:63488670', 'Pas de ligne directrice CPIC niveau A'),
    'ADRB2':   ('rs1042713',  'chr5:148826877',  'Pas de ligne directrice CPIC niveau A'),
    'MTHFR':   ('rs1801133',  'chr1:11796321',   'Pas de ligne directrice CPIC niveau A'),
}

# Genes dont le phenotype provient de PyPGx (Sherman, Claw & Lee, Sci Rep 2024)
PYPGX = {'CYP2D6','CYP2C19','CYP2C9','CYP2B6','CYP3A5','DPYD','TPMT','NUDT15',
         'SLCO1B1','UGT1A1','ABCG2','RYR1','CACNA1S','CFTR','F5'}

# Nature de l echelle numerique employee
ECHELLE = {
    'CYP2D6':'Score d activite (somme des deux alleles)',
    'CYP2C19':'Score d activite',
    'CYP2B6':'Score d activite',
    'CYP2C9':'Score d activite',
    'CYP3A5':'Phenotype ordinal (expresseur / non-expresseur)',
    'DPYD':'Score d activite',
    'TPMT':'Phenotype ordinal',
    'NUDT15':'Phenotype ordinal',
    'SLCO1B1':'Fonction de transport (ordinal)',
    'UGT1A1':'Phenotype ordinal',
    'ABCG2':'Fonction de transport (ordinal)',
    'RYR1':'Susceptibilite binaire (hyperthermie maligne)',
    'CACNA1S':'Susceptibilite binaire (hyperthermie maligne)',
    'CFTR':'Reponse au traitement (binaire)',
    'F5':'Reponse au traitement (binaire)',
    'VKORC1':'Code de genotype SNP (CC / CT / TT)',
    'IFNL3':'Code de genotype SNP (CC / CT / TT)',
    'CYP4F2':'Code de genotype SNP',
    'G6PD':'Code de genotype SNP (lie a l X)',
    'NAT2':'Code de genotype SNP (acetyleur)',
    'CYP1A2':'Code de genotype SNP',
    'CYP2A6':'Code de genotype SNP',
    'CYP3A4':'Code de genotype SNP',
    'SLC19A1':'Code de genotype SNP',
    'ACE':'Code de genotype SNP (proxy insertion/deletion)',
    'ADRB2':'Code de genotype SNP',
    'MTHFR':'Code de genotype SNP',
    'HLA-A':'Portage d allele a risque',
    'HLA-B':'Portage d allele a risque',
    'EGFR':'NON_DOCUMENTE',
    'MT-RNR1':'NON_DOCUMENTE',
}

# Limites connues et documentees
LIMITES = {
    'CYP2D6':'Non appelable depuis un VCF de SNP et d indels : variation structurale et nombre de copies. Phenotype fourni par PyPGx.',
    'HLA-A':'Non appelable depuis un VCF. Typage HLA requis. Quasi constant dans le jeu de donnees.',
    'HLA-B':'Non appelable depuis un VCF. Typage HLA requis. Quasi constant dans le jeu de donnees.',
    'MT-RNR1':'Gene mitochondrial, hors perimetre d un VCF nucleaire standard. Colonne constante.',
    'EGFR':'Variants pharmacogenomiques somatiques, caracterises dans le tissu tumoral. Absents d un VCF germinal. Colonne constante.',
    'ACE':'Le variant de reference rs1799752 est une insertion Alu de 287 pb, non representee dans un VCF de SNP. Le proxy rs4343 a ete utilise.',
    'G6PD':'Gene porte par le chromosome X. Les genotypes hemizygotes masculins ne sont pas traites specifiquement dans l encodage actuel.',
    'CFTR':'Cohorte 1000 Genomes composee de sujets sains : variance quasi nulle attendue.',
    'RYR1':'Cohorte de sujets sains : faible variance attendue.',
    'CACNA1S':'Cohorte de sujets sains : faible variance attendue.',
}

rows = []
for g in GENES:
    sub = df[df[g] != 1.0]
    valeurs = sorted(df[g].unique())
    n_non_normal = int(len(sub))
    pct = round(n_non_normal / len(df) * 100, 2)
    meds = sorted(sub['drug'].unique())[:8] if n_non_normal else []

    if g in VCF_EXTRACTION:
        variant, position, niveau = VCF_EXTRACTION[g]
        origine = 'Extraction directe des VCF 1000 Genomes (plages d octets HTTP)'
    elif g in PYPGX:
        variant, position = 'Diplotype (alleles etoile)', 'NON_APPLICABLE'
        niveau, origine = 'NON_DOCUMENTE', 'PyPGx — Sherman, Claw & Lee, Sci Rep 2024'
    else:
        variant = position = niveau = 'NON_DOCUMENTE'
        origine = 'Jeu de donnees initial (PharmGKB / CPIC / ClinVar / FDA)'

    rows.append({
        'gene': g,
        'variant': variant,
        'position_GRCh38': position,
        'origine_phenotype': origine,
        'echelle_numerique': ECHELLE.get(g, 'NON_DOCUMENTE'),
        'valeurs_observees': str(valeurs),
        'n_niveaux': len(valeurs),
        'n_lignes_non_normal': n_non_normal,
        'pct_non_normal': pct,
        'colonne_constante': len(valeurs) == 1,
        'niveau_CPIC': niveau,
        'medicaments_associes': ', '.join(meds) if meds else 'AUCUN',
        'limite_connue': LIMITES.get(g, ''),
    })

gs = pd.DataFrame(rows)
gs.to_csv(f'{DOCS_DIR}/gene_sheets.csv', index=False)

# Rapport markdown
n_const = int(gs['colonne_constante'].sum())
n_var = len(gs) - n_const
n_vcf = len(VCF_EXTRACTION)
n_pypgx = len([g for g in GENES if g in PYPGX])

r = ['# Annexe A — Fiches par gene', '',
     f'Panel : **{len(gs)} genes**',
     f'Colonnes porteuses de variance : **{n_var}**',
     f'Colonnes constantes : **{n_const}**', '',
     '## Origine des phenotypes', '',
     '| Origine | Genes |', '|---|---|',
     f'| Extraction directe des VCF 1000 Genomes | {n_vcf} |',
     f'| PyPGx (alleles etoile precalcules) | {n_pypgx} |',
     f'| Jeu de donnees initial (PharmGKB, CPIC, ClinVar, FDA) | {len(gs) - n_vcf - n_pypgx} |',
     '', '## Tableau de synthese', '',
     '| Gene | Variant | Niveaux | % non-normal | Echelle | Constante |',
     '|---|---|---|---|---|---|']
for _, x in gs.iterrows():
    r.append(f"| {x['gene']} | {x['variant']} | {x['n_niveaux']} | {x['pct_non_normal']} | "
             f"{x['echelle_numerique']} | {'oui' if x['colonne_constante'] else ''} |")

r += ['', '## Fiches detaillees', '']
for _, x in gs.iterrows():
    r += [f"### {x['gene']}", '',
          f"- **Variant** : {x['variant']}",
          f"- **Position (GRCh38)** : {x['position_GRCh38']}",
          f"- **Origine du phenotype** : {x['origine_phenotype']}",
          f"- **Echelle numerique** : {x['echelle_numerique']}",
          f"- **Valeurs observees** : {x['valeurs_observees']}",
          f"- **Lignes non-normales** : {x['n_lignes_non_normal']} ({x['pct_non_normal']} %)",
          f"- **Niveau CPIC** : {x['niveau_CPIC']}",
          f"- **Medicaments associes** : {x['medicaments_associes']}"]
    if x['limite_connue']:
        r.append(f"- **Limite connue** : {x['limite_connue']}")
    r.append('')

r += ['## Heterogeneite des echelles', '',
      'Les colonnes du panel ne partagent pas une echelle commune. Trois natures coexistent :', '',
      '1. **Scores d activite** — somme des contributions fonctionnelles des deux alleles ',
      '(CYP2D6, CYP2C19, CYP2B6, CYP2C9, DPYD). Grandeur additive et ordonnee.',
      '2. **Phenotypes ordinaux** — categories de fonction enzymatique ou de transport ',
      '(TPMT, NUDT15, SLCO1B1, UGT1A1, ABCG2, CYP3A5).',
      '3. **Codes de genotype SNP** — encodage du genotype a un locus unique ',
      '(VKORC1, IFNL3, CYP4F2, G6PD, NAT2 et les genes extraits des VCF). ',
      'La valeur 0,5 y designe un heterozygote, non une demi-activite.', '',
      'Une normalisation commune appliquee a l ensemble des colonnes suppose implicitement ',
      'que ces echelles sont commensurables. Cette hypothese est fausse et constitue une ',
      'limite methodologique documentee du travail.']

with open(f'{DOCS_DIR}/gene_sheets.md','w') as f:
    f.write('\n'.join(r))

print(f'Genes documentes : {len(gs)}')
print(f'  Variance observee : {n_var}')
print(f'  Colonnes constantes : {n_const}')
print()
print('Origine des phenotypes :')
print(f'  Extraction VCF 1000 Genomes : {n_vcf}')
print(f'  PyPGx : {n_pypgx}')
print(f'  Jeu de donnees initial : {len(gs) - n_vcf - n_pypgx}')
print()
print('Colonnes constantes :', ', '.join(gs[gs['colonne_constante']]['gene'].tolist()))
print()
print('Fichiers : docs/gene_sheets.csv, docs/gene_sheets.md')
