# deep_learning_v2.py
# DL amélioré - 4 classes + SMOTE + learning rate scheduler

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
import torch
import torch.nn as nn
import warnings
warnings.filterwarnings('ignore')

# CHARGEMENT
print("Chargement des données...")
df = pd.read_csv('/home/mouna/projet_memoire/data/var_drug_ann.tsv', sep='\t', low_memory=False)
df = df[df['Significance'] == 'yes']
df = df[['Gene', 'Drug(s)', 'Phenotype Category']].dropna()
df.columns = ['gene', 'drug', 'phenotype']

# REGROUPEMENT EN 4 CLASSES
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
print("Distribution après regroupement :")
print(df['phenotype_grouped'].value_counts())

le_gene  = LabelEncoder()
le_drug  = LabelEncoder()
le_pheno = LabelEncoder()

df['gene_enc']  = le_gene.fit_transform(df['gene'])
df['drug_enc']  = le_drug.fit_transform(df['drug'])
df['pheno_enc'] = le_pheno.fit_transform(df['phenotype_grouped'])

X = df[['gene_enc', 'drug_enc']].values
y = df['pheno_enc'].values

print(f"\nClasses : {le_pheno.classes_}")

print("\nApplication SMOTE...")
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)
print(f"Avant SMOTE : {len(X)} | Après SMOTE : {len(X_res)}")

X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)
print(f"Train : {len(X_train)} | Test : {len(X_test)}")

class PharmDL(nn.Module):
    def __init__(self):
        super(PharmDL, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 4)
        )
    def forward(self, x):
        return self.net(x)

model     = PharmDL()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=50, gamma=0.5)

print("\nEntraînement...")
X_train_t = torch.FloatTensor(X_train)
y_train_t = torch.LongTensor(y_train)
X_test_t  = torch.FloatTensor(X_test)

for epoch in range(200):
    model.train()
    optimizer.zero_grad()
    loss = criterion(model(X_train_t), y_train_t)
    loss.backward()
    optimizer.step()
    scheduler.step()
    if (epoch+1) % 50 == 0:
        print(f"Epoch {epoch+1}/200 - Loss: {loss.item():.4f}")

model.eval()
with torch.no_grad():
    _, predicted = torch.max(model(X_test_t), 1)
    y_pred = predicted.numpy()

accuracy = accuracy_score(y_test, y_pred)
print(f"\n{'='*50}")
print(f"Accuracy DL v1 (19 classes) : 44.8%")
print(f"Accuracy DL v2 (4 classes)  : {accuracy*100:.1f}%")
print(f"Amélioration                : +{(accuracy-0.448)*100:.1f}%")
print(f"\nRapport :")
print(classification_report(y_test, y_pred, target_names=le_pheno.classes_, zero_division=0))

torch.save(model.state_dict(), '/home/mouna/projet_memoire/results/dl_v2_model.pth')
pd.DataFrame({'model': ['DL v1', 'DL v2'], 'accuracy': [0.448, accuracy]}).to_csv(
    '/home/mouna/projet_memoire/results/dl_v2_results.csv', index=False)
print("Modèle sauvegardé.")
