# xgboost_model.py
# Comparaison XGBoost vs DL v5 vs RF v3
# Memes conditions : 7 features One-Hot + genotype, 4 classes, SMOTE

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import joblib
import pickle
import warnings
warnings.filterwarnings('ignore')

print("Chargement...")
df = pd.read_csv('/home/mouna/projet_memoire/data/var_drug_ann.tsv', sep='\t', low_memory=False)
df = df[df['Significance'] == 'yes']
df = df[['Gene', 'Drug(s)', 'Phenotype Category',
         'Variant/Haplotypes', 'Is/Is Not associated',
         'Direction of effect', 'Population types',
         'Alleles']].dropna(subset=['Gene', 'Drug(s)', 'Phenotype Category'])
df.columns = ['gene', 'drug', 'phenotype', 'variant',
              'association', 'direction', 'population', 'alleles']

df['direction']  = df['direction'].fillna('unknown')
df['population'] = df['population'].fillna('unknown')
df['variant']    = df['variant'].fillna('unknown')
df['alleles']    = df['alleles'].fillna('unknown')

def encode_genotype(a):
    a = str(a).lower()
    if '1/1' in a or 'hom' in a: return 2
    elif '0/1' in a or '1/0' in a or 'het' in a: return 1
    else: return 0

df['genotype_enc'] = df['alleles'].apply(encode_genotype)

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
).astype(np.float32)
X_ohe['genotype'] = df['genotype_enc'].values.astype(np.float32)

le_pheno = LabelEncoder()
y = le_pheno.fit_transform(df['phenotype'])
classes = list(le_pheno.classes_)

X = X_ohe.values
columns = list(X_ohe.columns)

smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42)

print(f"Train : {len(X_train)} | Test : {len(X_test)}")
print(f"Features : {X.shape[1]} colonnes")
print(f"Classes  : {classes}")

print("\nEntraînement XGBoost...")
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric='mlogloss',
    verbosity=0
)
model.fit(X_train, y_train)

y_pred   = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"COMPARAISON FINALE — memes conditions")
print(f"{'='*50}")
print(f"DL v5  (7 features + genotype) : 88.0%")
print(f"RF v3  (7 features + genotype) : 89.4%")
print(f"XGBoost (7 features + genotype) : {accuracy*100:.1f}%")

print(f"\nRapport XGBoost :")
print(classification_report(y_test, y_pred,
      target_names=classes, zero_division=0))

# Sauvegarder
joblib.dump(model, '/home/mouna/projet_memoire/results/xgboost_model.pkl')
with open('/home/mouna/projet_memoire/results/xgboost_columns.pkl', 'wb') as f:
    pickle.dump(columns, f)
with open('/home/mouna/projet_memoire/results/xgboost_classes.pkl', 'wb') as f:
    pickle.dump(classes, f)

print("\nModèle sauvegardé : xgboost_model.pkl")
