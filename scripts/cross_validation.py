# cross_validation.py
# Cross-validation 5-fold sur DL v5, RF v3 et XGBoost
# Objectif : prouver la stabilite des resultats

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import torch
import torch.nn as nn
import warnings
warnings.filterwarnings('ignore')

print("Chargement des donnees...")
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

X = X_ohe.values
y = df['phenotype'].values

# Encoder y en numerique pour DL
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y_enc = le.fit_transform(y)
classes = list(le.classes_)
print(f"Classes : {classes}")
print(f"Features : {X.shape[1]} colonnes")

# Modele DL
input_size = X.shape[1]
class PharmDLv5(nn.Module):
    def __init__(self):
        super(PharmDLv5, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, 4)
        )
    def forward(self, x):
        return self.net(x)

# Cross-validation 5-fold
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
smote = SMOTE(random_state=42)

rf_scores  = []
xgb_scores = []
dl_scores  = []

print("\nCross-validation 5-fold en cours...")
for fold, (train_idx, test_idx) in enumerate(kf.split(X, y_enc)):
    print(f"\nFold {fold+1}/5...")
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y_enc[train_idx], y_enc[test_idx]

    X_train_r, y_train_r = smote.fit_resample(X_train, y_train)

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train_r, y_train_r)
    rf_scores.append(accuracy_score(y_test, rf.predict(X_test)))

    # XGBoost
    xgb_model = xgb.XGBClassifier(n_estimators=100, max_depth=6,
                                    learning_rate=0.1, random_state=42,
                                    eval_metric='mlogloss', verbosity=0)
    xgb_model.fit(X_train_r, y_train_r)
    xgb_scores.append(accuracy_score(y_test, xgb_model.predict(X_test)))

    # Deep Learning
    model = PharmDLv5()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=50, gamma=0.5)

    X_train_t = torch.FloatTensor(X_train_r)
    y_train_t = torch.LongTensor(y_train_r)
    X_test_t  = torch.FloatTensor(X_test)

    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        loss = criterion(model(X_train_t), y_train_t)
        loss.backward()
        optimizer.step()
        scheduler.step()

    model.eval()
    with torch.no_grad():
        _, predicted = torch.max(model(X_test_t), 1)
        dl_scores.append(accuracy_score(y_test, predicted.numpy()))

    print(f"  RF: {rf_scores[-1]*100:.1f}% | XGB: {xgb_scores[-1]*100:.1f}% | DL: {dl_scores[-1]*100:.1f}%")

print(f"\n{'='*60}")
print(f"RESULTATS CROSS-VALIDATION 5-FOLD")
print(f"{'='*60}")
print(f"Deep Learning v5 : {np.mean(dl_scores)*100:.1f}% ± {np.std(dl_scores)*100:.1f}%")
print(f"Random Forest v3 : {np.mean(rf_scores)*100:.1f}% ± {np.std(rf_scores)*100:.1f}%")
print(f"XGBoost          : {np.mean(xgb_scores)*100:.1f}% ± {np.std(xgb_scores)*100:.1f}%")

results = pd.DataFrame({
    'fold': range(1, 6),
    'DL_v5': [round(s*100,1) for s in dl_scores],
    'RF_v3': [round(s*100,1) for s in rf_scores],
    'XGBoost': [round(s*100,1) for s in xgb_scores]
})
results.to_csv('/home/mouna/projet_memoire/results/cross_validation_results.csv', index=False)
print("\nResultats sauvegardes dans cross_validation_results.csv")
