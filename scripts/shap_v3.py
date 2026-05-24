# shap_v3.py
# SHAP sur RF v3 - modèle final avec 7 features + génotype

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import shap
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# GÉNOTYPES DEPUIS VCF
print("Extraction génotypes...")
vcf_genotypes = {}
with open('/home/mouna/projet_memoire/data/pharmacat.example2.vcf', 'r') as f:
    for line in f:
        if line.startswith('#'):
            continue
        cols = line.strip().split('\t')
        vcf_genotypes[cols[2]] = cols[9].split(':')[0]

def encode_genotype(gt):
    if gt == '1/1': return 2
    elif gt == '0/1': return 1
    else: return 0

# CHARGEMENT
print("Chargement PharmGKB...")
df = pd.read_csv('/home/mouna/projet_memoire/data/var_drug_ann.tsv', sep='\t', low_memory=False)
df = df[df['Significance'] == 'yes']
df = df[['Gene', 'Drug(s)', 'Phenotype Category',
         'Variant/Haplotypes', 'Is/Is Not associated',
         'Direction of effect', 'Population types']].dropna(
         subset=['Gene', 'Drug(s)', 'Phenotype Category'])
df.columns = ['gene', 'drug', 'phenotype', 'variant', 'association', 'direction', 'population']

df['direction']  = df['direction'].fillna('unknown')
df['population'] = df['population'].fillna('unknown')
df['variant']    = df['variant'].fillna('unknown')
df['genotype']   = df['variant'].apply(lambda v: encode_genotype(vcf_genotypes.get(v, '0/0')))

def regroup(p):
    p = str(p).lower()
    if 'toxicity' in p: return 'Toxicity'
    elif 'dosage' in p: return 'Dosage'
    elif 'efficacy' in p or 'pd' in p: return 'Efficacy'
    else: return 'Metabolism'

df['phenotype_grouped'] = df['phenotype'].apply(regroup)

# FEATURES
X_df = pd.get_dummies(
    df[['gene', 'drug', 'variant', 'association', 'direction', 'population']],
    columns=['gene', 'drug', 'variant', 'association', 'direction', 'population']
)
X_genotype = df[['genotype']].reset_index(drop=True)
X_df = X_df.reset_index(drop=True)
X_full = pd.concat([X_df, X_genotype], axis=1)

le_pheno = LabelEncoder()
y = le_pheno.fit_transform(df['phenotype_grouped'])

# SMOTE
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X_full.values, y)

X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42)

# ENTRAÎNEMENT
print("Entraînement RF v3...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# SHAP
print("Calcul SHAP...")
X_sample = X_test[:100]
explainer   = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_sample, check_additivity=False)

feature_names = list(X_full.columns)

# Graphique 1 — Bar chart importance
plt.figure(figsize=(10, 5))
shap.summary_plot(shap_values, X_sample,
                  feature_names=feature_names,
                  plot_type='bar', show=False, max_display=15)
plt.title('Top 15 features les plus importantes (SHAP) — RF v3')
plt.tight_layout()
plt.savefig('/home/mouna/projet_memoire/results/shap_v3_importance.png', dpi=150)
plt.close()
print("Graphique 1 sauvegardé : shap_v3_importance.png")

# Graphique 2 — Summary plot
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_sample,
                  feature_names=feature_names,
                  show=False, max_display=15)
plt.title('SHAP Summary Plot — RF v3')
plt.tight_layout()
plt.savefig('/home/mouna/projet_memoire/results/shap_v3_summary.png', dpi=150)
plt.close()
print("Graphique 2 sauvegardé : shap_v3_summary.png")

print("\nConclusion SHAP v3 terminée.")
