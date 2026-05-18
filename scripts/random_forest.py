# random_forest.py
# Phase 4 - ML Classique
# Comparaison avec Deep Learning

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

print("Chargement des données PharmGKB...")
df = pd.read_csv('/home/mouna/projet_memoire/data/var_drug_ann.tsv', sep='\t', low_memory=False)
df = df[df['Significance'] == 'yes']
df = df[['Gene', 'Drug(s)', 'Phenotype Category']].dropna()
df.columns = ['gene', 'drug', 'phenotype']

le_gene      = LabelEncoder()
le_drug      = LabelEncoder()
le_phenotype = LabelEncoder()

df['gene_enc']      = le_gene.fit_transform(df['gene'])
df['drug_enc']      = le_drug.fit_transform(df['drug'])
df['phenotype_enc'] = le_phenotype.fit_transform(df['phenotype'])

X = df[['gene_enc', 'drug_enc']].values
y = df['phenotype_enc'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Entraînement Random Forest...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

y_pred   = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nAccuracy Random Forest : {accuracy*100:.1f}%")
print(f"Accuracy Deep Learning : 44.8%")
print(f"\nAmélioration : +{(accuracy - 0.448)*100:.1f}%")

print("\n" + "="*50)
print("COMPARAISON DL vs RANDOM FOREST")
print("="*50)
print(f"Deep Learning  : 44.8%")
print(f"Random Forest  : {accuracy*100:.1f}%")

results = pd.DataFrame({
    'model':    ['Deep Learning', 'Random Forest'],
    'accuracy': [0.448, accuracy]
})
results.to_csv('/home/mouna/projet_memoire/results/comparison_results.csv', index=False)
print("\nRésultats sauvegardés dans comparison_results.csv")
