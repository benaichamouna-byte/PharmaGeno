import pandas as pd
import numpy as np
import pickle
import shutil
import subprocess
from datetime import datetime

DATA_DIR    = '/home/mouna/projet_memoire/model_v2/data'
SCRIPTS_DIR = '/home/mouna/projet_memoire/scripts'
WIN_DIR     = '/mnt/c/Users/MSI/Desktop/memoire'

print("Chargement données...")
df = pd.read_csv(f'{DATA_DIR}/phenotype_drug_dataset_complet.csv')
print(f"Dataset original : {len(df)} lignes")

with open('/home/mouna/projet_memoire/data/vcf_genotypes_all_genes.pkl','rb') as f:
    vcf_data = pickle.load(f)

print(f"Gènes VCF disponibles : {[g for g,d in vcf_data.items() if d]}")

# Backup
backup_path = f'{DATA_DIR}/phenotype_drug_dataset_complet.csv.AVANT_V2_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy(f'{DATA_DIR}/phenotype_drug_dataset_complet.csv', backup_path)
print(f"Backup créé : {backup_path}")

# Étape 1 — Mettre à jour les colonnes des 12 gènes pour les lignes 1KGP
print("\nÉtape 1 : Mise à jour des génotypes 1KGP...")
NEW_GENES = [g for g,d in vcf_data.items() if d]
updated = 0

for gene in NEW_GENES:
    if gene not in df.columns:
        df[gene] = 1.0
    gene_data = vcf_data[gene]
    if not gene_data:
        continue
    mask = df['sample'].notna() & df['sample'].isin(gene_data.keys())
    df.loc[mask, gene] = df.loc[mask, 'sample'].map(gene_data)
    updated += mask.sum()
    pct_updated = mask.sum() / len(df) * 100
    non_default = (df.loc[mask, gene] != 1.0).sum()
    print(f"  {gene}: {mask.sum()} lignes mises à jour ({pct_updated:.1f}%), {non_default} non-défaut")

print(f"\nTotal lignes mises à jour : {updated}")

# Étape 2 — Ajouter nouvelles associations gène-médicament
print("\nÉtape 2 : Ajout nouvelles associations médicamenteuses...")

GENE_DRUGS_NEW = {
    'ACE':     ['captopril','enalapril','lisinopril','ramipril','perindopril'],
    'MTHFR':   ['methotrexate','fluorouracil','capecitabine'],
    'G6PD':    ['rasburicase','dapsone','primaquine','chloroquine','nitrofurantoin'],
    'NAT2':    ['isoniazid','hydralazine','procainamide','sulfamethoxazole'],
    'CYP1A2':  ['clozapine','olanzapine','theophylline','caffeine','fluvoxamine'],
    'CYP2A6':  ['nicotine','letrozole','tegafur'],
    'CYP3A4':  ['tacrolimus','midazolam','simvastatin','atorvastatin','erythromycin'],
    'CYP4F2':  ['warfarin'],
    'IFNL3':   ['peginterferon alfa-2a','peginterferon alfa-2b','ribavirin'],
    'SLC19A1': ['methotrexate','pemetrexed'],
    'VKORC1':  ['warfarin','acenocoumarol','phenprocoumon'],
    'ADRB2':   ['salmeterol','albuterol','salbutamol'],
}

ACTION_MAP = {
    0.0: 'EVITER',
    0.5: 'ADAPTER_DOSE',
    1.0: 'STANDARD',
    1.5: 'ADAPTER_DOSE',
    2.0: 'ADAPTER_DOSE',
}

META = ['drug','action','gene','phenotype','rsid','source','level','sample']
GENES_ALL = sorted([c for c in df.columns if c not in META])

new_rows = []
for gene, drugs in GENE_DRUGS_NEW.items():
    gene_data = vcf_data.get(gene, {})
    if not gene_data:
        continue
    
    for sample, pheno_val in gene_data.items():
        if pheno_val == 1.0:
            continue  # Skip Normal — pas de recommandation spécifique
        
        # Récupérer le profil complet depuis les lignes existantes
        sample_rows = df[df['sample'] == sample]
        if len(sample_rows) == 0:
            continue
        
        gene_vector = sample_rows.iloc[0][GENES_ALL].to_dict()
        gene_vector[gene] = pheno_val
        
        action = ACTION_MAP.get(pheno_val, 'SURVEILLER')
        
        for drug in drugs:
            row = gene_vector.copy()
            row['drug'] = drug
            row['action'] = action
            row['sample'] = sample
            row['gene'] = gene
            new_rows.append(row)

if new_rows:
    df_new = pd.DataFrame(new_rows)
    df_combined = pd.concat([df, df_new], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset=GENES_ALL+['drug','action'])
    df_combined[GENES_ALL] = df_combined[GENES_ALL].fillna(1.0)
else:
    df_combined = df

print(f"Nouvelles lignes ajoutées : {len(df_combined) - len(df)}")
print(f"Dataset final : {len(df_combined)} lignes")
print("\nDistribution actions :")
print(df_combined['action'].value_counts())
print(f"\nGènes : {len(GENES_ALL)}")
print(f"Médicaments : {df_combined['drug'].nunique()}")

# Vérifier amélioration des gènes clés
print("\nVérification amélioration :")
for gene in NEW_GENES:
    if gene in df_combined.columns:
        pct_default = (df_combined[gene] == 1.0).sum() / len(df_combined) * 100
        print(f"  {gene}: {pct_default:.1f}% à 1.0 (défaut)")

# Sauvegarder
output_path = f'{DATA_DIR}/phenotype_drug_dataset_complet_v2.csv'
df_combined.to_csv(output_path, index=False)
print(f"\nSauvegardé : phenotype_drug_dataset_complet_v2.csv")

# Windows
shutil.copy(output_path, f"{WIN_DIR}/phenotype_drug_dataset_complet_v2.csv")
print("Windows OK")

# GitHub
subprocess.run(['git', '-C', '/home/mouna/projet_memoire', 'add',
    'model_v2/data/phenotype_drug_dataset_complet_v2.csv',
    'scripts/integrate_new_genes.py'])
subprocess.run(['git', '-C', '/home/mouna/projet_memoire', 'commit',
    '-m', f'dataset v2 - {len(df_combined)} lignes - 12 nouveaux genes integres depuis 1KGP VCF'])
subprocess.run(['git', '-C', '/home/mouna/projet_memoire', 'push', 'origin', 'main'])
print("GitHub OK")
print("\nDrive : uploade phenotype_drug_dataset_complet_v2.csv depuis Windows vers PharmaGeno_Memoire/Models/model_v2_final/")
