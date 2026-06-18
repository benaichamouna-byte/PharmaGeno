# shap_v2.py
# SHAP sur Random Forest v2 — 6 features

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import SMOTE
import shap
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("Chargement...")
df = pd.read_csv('/home/mouna/projet_memoire/data/var_drug_ann.tsv', sep='\t', low_memory=False)
df = df[df['Significance'] == 'yes']
df = df[['Gene', 'Drug(s)', 'Phenotype Category',
         'Variant/Haplotypes', 'Is/Is Not associated',
         'Direction of effect', 'Population types']].dropna(
         subset=['Gene', 'Drug(s)', 'Phenotype Category'])
df.columns = ['gene', 'drug', 'phenotype', 'variant',
              'association', 'direction', 'population']

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

df['phenotype'] = df['phenotype'].apply(regroup)

X = pd.get_dummies(
    df[['gene', 'drug', 'variant', 'association', 'direction', 'population']],
    columns=['gene', 'drug', 'variant', 'association', 'direction', 'population']
).astype(int)

y = df['phenotype'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

smote = SMOTE(random_state=42)
X_train_r, y_train_r = smote.fit_resample(X_train, y_train)

print("Entraînement RF v2...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_r, y_train_r)

accuracy = accuracy_score(y_test, rf.predict(X_test))
print(f"Accuracy RF v2 : {accuracy*100:.1f}%")

print("Calcul SHAP...")
explainer   = shap.TreeExplainer(rf)
X_sample    = X_test.iloc[:100]
shap_values = explainer.shap_values(X_sample)

# Top 15 features les plus importantes
print("Génération graphiques SHAP...")

# Graphique 1 — Top 15 features importantes
feature_importance = np.abs(shap_values).mean(axis=(0, 2)) \
    if len(np.array(shap_values).shape) == 3 \
    else np.abs(shap_values).mean(axis=0)

top15_idx  = np.argsort(feature_importance)[-15:]
top15_names = [X_test.columns[i] for i in top15_idx]
top15_vals  = feature_importance[top15_idx]

plt.figure(figsize=(10, 6))
plt.barh(top15_names, top15_vals, color='steelblue')
plt.xlabel('mean(|SHAP value|)')
plt.title('Top 15 features importantes (SHAP) — RF v2')
plt.tight_layout()
plt.savefig('/home/mouna/projet_memoire/results/shap_v2_importance.png', dpi=150)
plt.close()
print("shap_v2_importance.png sauvegardé")

# Graphique 2 — Par catégorie de feature
categories = {'gene': 0, 'drug': 0, 'variant': 0,
              'association': 0, 'direction': 0, 'population': 0}

for i, col in enumerate(X_test.columns):
    for cat in categories:
        if col.startswith(cat):
            if len(np.array(shap_values).shape) == 3:
                categories[cat] += np.abs(shap_values).mean(axis=(0,2))[i]
            else:
                categories[cat] += np.abs(shap_values).mean(axis=0)[i]

plt.figure(figsize=(8, 5))
plt.barh(list(categories.keys()), list(categories.values()), color='steelblue')
plt.xlabel('mean(|SHAP value|) total')
plt.title('Importance par catégorie de feature (SHAP) — RF v2')
plt.tight_layout()
plt.savefig('/home/mouna/projet_memoire/results/shap_v2_categories.png', dpi=150)
plt.close()
print("shap_v2_categories.png sauvegardé")

print("\nConclusion SHAP v2 :")
top_cat = max(categories, key=categories.get)
print(f"Feature la plus importante : {top_cat}")
for cat, val in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"  {cat:15} : {val:.4f}")
