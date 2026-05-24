# random_forest_v3.py
# RF avec génotype - mêmes conditions que DL v5

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
import joblib
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
X_onehot  = pd.get_dummies(
    df[['gene', 'drug', 'variant', 'association', 'direction', 'population']],
    columns=['gene', 'drug', 'variant', 'association', 'direction', 'population']
).values.astype(np.float32)
X_genotype = df[['genotype']].values.astype(np.float32)
X = np.hstack([X_onehot, X_genotype])

le_pheno = LabelEncoder()
y = le_pheno.fit_transform(df['phenotype_grouped'])

# SMOTE
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)
print(f"Train : {len(X_train)} | Test : {len(X_test)}")

# ENTRAÎNEMENT
print("Entraînement RF v3...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

y_pred   = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"RF v2  (6 features, sans génotype) : 89.0%")
print(f"RF v3  (7 features, avec génotype) : {accuracy*100:.1f}%")
print(f"DL v5  (7 features, avec génotype) : 88.0%")
print(f"\nRapport :")
print(classification_report(y_test, y_pred,
      target_names=le_pheno.classes_, zero_division=0))

joblib.dump(rf, '/home/mouna/projet_memoire/results/rf_v3_model.pkl')
print("Modèle sauvegardé.")
