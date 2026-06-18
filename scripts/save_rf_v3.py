import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import joblib
import pickle
import warnings
warnings.filterwarnings('ignore')

print("Chargement...")
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

# Génotypes depuis VCF
vcf_genotypes = {}
try:
    with open('/home/mouna/projet_memoire/data/pharmacat.example2.vcf', 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            cols = line.strip().split('\t')
            vcf_genotypes[cols[2]] = cols[9].split(':')[0]
except:
    pass

def encode_genotype(gt):
    if gt == '1/1': return 2
    elif gt == '0/1': return 1
    else: return 0

df['genotype'] = df['variant'].apply(lambda v: encode_genotype(vcf_genotypes.get(v, '0/0')))

def regroup(p):
    p = str(p).lower()
    if 'toxicity' in p: return 'Toxicity'
    elif 'dosage' in p: return 'Dosage'
    elif 'efficacy' in p or 'pd' in p: return 'Efficacy'
    else: return 'Metabolism'

df['phenotype'] = df['phenotype'].apply(regroup)

X_ohe = pd.get_dummies(
    df[['gene', 'drug', 'variant', 'association', 'direction', 'population']],
    columns=['gene', 'drug', 'variant', 'association', 'direction', 'population']
).astype(int)

X = pd.concat([X_ohe, df[['genotype']].reset_index(drop=True)], axis=1)
y = df['phenotype'].values

smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42)

print("Entraînement RF v3...")
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

joblib.dump(rf, '/home/mouna/projet_memoire/results/rf_v3_model.pkl')

columns = list(X.columns)
with open('/home/mouna/projet_memoire/results/rf_v3_columns.pkl', 'wb') as f:
    pickle.dump(columns, f)

classes = list(rf.classes_)
with open('/home/mouna/projet_memoire/results/rf_v3_classes.pkl', 'wb') as f:
    pickle.dump(classes, f)

print(f"Modèle sauvegardé : rf_v3_model.pkl")
print(f"Colonnes : {len(columns)} colonnes")
print(f"Classes : {classes}")
