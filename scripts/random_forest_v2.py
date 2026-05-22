import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

print("Chargement...")
df = pd.read_csv('/home/mouna/projet_memoire/data/var_drug_ann.tsv', sep='\t', low_memory=False)
df = df[df['Significance'] == 'yes']
df = df[['Gene', 'Drug(s)', 'Phenotype Category']].dropna()
df.columns = ['gene', 'drug', 'phenotype']

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

df['phenotype'] = df['phenotype'].apply(regroup)

# One-Hot Encoding
X = pd.get_dummies(df[['gene', 'drug']])
y = df['phenotype'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

smote = SMOTE(random_state=42)
X_train_r, y_train_r = smote.fit_resample(X_train, y_train)

print("Entraînement Random Forest V2...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_r, y_train_r)

y_pred   = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"COMPARAISON FINALE")
print(f"{'='*50}")
print(f"DL V1  (19 classes)          : 44.8%")
print(f"DL V2  (4 classes + SMOTE)   : 31.1%")
print(f"DL V3  (One-Hot + SMOTE)     : 85.1%")
print(f"RF V2  (One-Hot + SMOTE)     : {accuracy*100:.1f}%")

print(f"\nRapport Random Forest V2 :")
print(classification_report(y_test, y_pred, zero_division=0))

results = pd.DataFrame({
    'model':    ['DL V1', 'DL V2', 'DL V3', 'RF V2'],
    'accuracy': [0.448, 0.311, 0.851, accuracy]
})
results.to_csv('/home/mouna/projet_memoire/results/comparison_final.csv', index=False)
print("Résultats sauvegardés dans comparison_final.csv")
