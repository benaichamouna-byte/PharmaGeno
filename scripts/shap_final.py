import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import SMOTE
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
    if 'toxicity' in p: return 'Toxicity'
    elif 'dosage' in p: return 'Dosage'
    elif 'efficacy' in p or 'pd' in p: return 'Efficacy'
    else: return 'Metabolism'

df['phenotype'] = df['phenotype'].apply(regroup)

X = pd.get_dummies(
    df[['gene', 'drug', 'variant', 'association', 'direction', 'population']],
    columns=['gene', 'drug', 'variant', 'association', 'direction', 'population']
).astype(int)
y = df['phenotype'].values

smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42)

print("Entraînement RF...")
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
accuracy = accuracy_score(y_test, rf.predict(X_test))
print(f"Accuracy : {accuracy*100:.1f}%")

# Importance par catégorie via feature_importances_ (pas SHAP)
print("Calcul importance des features...")
importances = rf.feature_importances_
feat_names  = X_train.columns

categories = {'Gène': 0, 'Médicament': 0, 'Variant': 0,
              'Association': 0, 'Direction': 0, 'Population': 0}

mapping = {'gene': 'Gène', 'drug': 'Médicament', 'variant': 'Variant',
           'association': 'Association', 'direction': 'Direction',
           'population': 'Population'}

for i, col in enumerate(feat_names):
    for prefix, label in mapping.items():
        if col.startswith(prefix + '_'):
            categories[label] += importances[i]

# Graphique 1 — Importance par catégorie
cats_sorted = sorted(categories.items(), key=lambda x: x[1])
labels = [c[0] for c in cats_sorted]
values = [c[1] for c in cats_sorted]
colors = ['#1a5276', '#2e86c1', '#5dade2', '#85c1e9', '#aed6f1', '#d6eaf8']

plt.figure(figsize=(9, 5))
bars = plt.barh(labels, values, color=colors)
plt.xlabel("Importance moyenne (Gini)", fontsize=12)
plt.title("Importance des catégories de features — RF v3", fontsize=13)
for bar, val in zip(bars, values):
    plt.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
             f'{val:.3f}', va='center', fontsize=10)
plt.tight_layout()
plt.savefig('/home/mouna/projet_memoire/results/feature_importance_categories.png', dpi=150)
plt.close()
print("Graphique 1 sauvegardé : feature_importance_categories.png")

# Graphique 2 — Top 10 features individuelles
top10_idx    = np.argsort(importances)[-10:]
top10_names  = [feat_names[i].replace('gene_', 'Gène: ')
                             .replace('drug_', 'Drug: ')
                             .replace('variant_', 'Variant: ')
                             .replace('direction_', 'Direction: ')
                             .replace('population_', 'Population: ')
                             .replace('association_', 'Association: ')
                for i in top10_idx]
top10_values = importances[top10_idx]

plt.figure(figsize=(10, 6))
bars = plt.barh(top10_names, top10_values, color='#2e86c1')
plt.xlabel("Importance (Gini)", fontsize=12)
plt.title("Top 10 features individuelles — RF v3", fontsize=13)
for bar, val in zip(bars, top10_values):
    plt.text(bar.get_width() + 0.0001, bar.get_y() + bar.get_height()/2,
             f'{val:.4f}', va='center', fontsize=9)
plt.tight_layout()
plt.savefig('/home/mouna/projet_memoire/results/feature_importance_top10.png', dpi=150)
plt.close()
print("Graphique 2 sauvegardé : feature_importance_top10.png")

print("\nRésultats par catégorie :")
for label, val in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"  {label:15} : {val:.4f}")
print(f"\nCatégorie dominante : {max(categories, key=categories.get)}")
