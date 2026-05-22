# random_forest_v2.py
# Random Forest amélioré - mêmes conditions que DL v4
# 6 features One-Hot + 4 classes + SMOTE

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
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

def regroup(p):
    p = str(p).lower()
    if 'toxicity' in p:
        return 'Toxicity'
    elif 'dosage' in p:
        return 'Dosage'
    elif 'efficacy' in p or 'pd' in p:
        return 'Efficacy'
    else:
        return 'Metabolism'

df['phenotype_grouped'] = df['phenotype'].apply(regroup)
print("Distribution :")
print(df['phenotype_grouped'].value_counts())

print("\nOne-Hot Encoding...")
X = pd.get_dummies(df[['gene', 'drug', 'variant', 'association', 'direction', 'population']],
                   columns=['gene', 'drug', 'variant', 'association', 'direction', 'population'])
X = X.values.astype(np.float32)

le_pheno = LabelEncoder()
y = le_pheno.fit_transform(df['phenotype_grouped'])

print(f"Features : {X.shape[1]} colonnes")

print("\nSMOTE...")
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)
print(f"Après SMOTE : {len(X_res)} exemples")

X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42)
print(f"Train : {len(X_train)} | Test : {len(X_test)}")

print("\nEntraînement Random Forest...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

y_pred   = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"COMPARAISON — mêmes conditions")
print(f"{'='*50}")
print(f"Random Forest v1 (2 features, 19 classes) : 77.7%")
print(f"Random Forest v2 (6 features, 4 classes)  : {accuracy*100:.1f}%")
print(f"\nDL v4 (6 features, 4 classes)             : 87.6%")
print(f"RF v2 (6 features, 4 classes)             : {accuracy*100:.1f}%")

print(f"\nRapport :")
print(classification_report(y_test, y_pred,
      target_names=le_pheno.classes_, zero_division=0))

import joblib
joblib.dump(rf, '/home/mouna/projet_memoire/results/rf_v2_model.pkl')
print("Modèle sauvegardé.")
