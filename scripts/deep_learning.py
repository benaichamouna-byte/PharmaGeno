# deep_learning.py
# Phase 4 - Modèle Deep Learning
# Objectif : montrer les limites du DL sur données PharmGKB

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import torch
import torch.nn as nn
import warnings
warnings.filterwarnings('ignore')

# CHARGEMENT DES DONNÉES
print("Chargement des données PharmGKB...")
df = pd.read_csv('/home/mouna/projet_memoire/data/var_drug_ann.tsv', sep='\t', low_memory=False)
df = df[df['Significance'] == 'yes']
print(f"Données : {len(df)} lignes")

# PRÉPARATION
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

print(f"Classes : {len(np.unique(y))} phénotypes distincts")

# SPLIT
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Train : {len(X_train)} | Test : {len(X_test)}")

# MODÈLE DL
class PharmDLModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(PharmDLModel, self).__init__()
        self.fc1     = nn.Linear(input_size, hidden_size)
        self.relu    = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.fc2     = nn.Linear(hidden_size, hidden_size)
        self.fc3     = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

n_classes = len(np.unique(y))
model     = PharmDLModel(2, 64, n_classes)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# ENTRAÎNEMENT
print("\nEntraînement...")
X_train_t = torch.FloatTensor(X_train)
y_train_t = torch.LongTensor(y_train)
X_test_t  = torch.FloatTensor(X_test)

for epoch in range(100):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_t)
    loss    = criterion(outputs, y_train_t)
    loss.backward()
    optimizer.step()
    if (epoch+1) % 20 == 0:
        print(f"Epoch {epoch+1}/100 - Loss: {loss.item():.4f}")

# ÉVALUATION
model.eval()
with torch.no_grad():
    outputs          = model(X_test_t)
    _, predicted     = torch.max(outputs, 1)
    y_pred           = predicted.numpy()

accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy DL : {accuracy*100:.1f}%")

# CONCLUSION
print("\n" + "="*50)
if accuracy < 0.6:
    print(f"Accuracy faible ({accuracy*100:.1f}%)")
    print("Le DL n'est pas adapté à ces données.")
    print("→ Passage au Random Forest recommandé")
else:
    print(f"Accuracy : {accuracy*100:.1f}%")

# SAUVEGARDE
results = pd.DataFrame({
    'model':     ['Deep Learning'],
    'accuracy':  [accuracy],
    'n_train':   [len(X_train)],
    'n_test':    [len(X_test)],
    'n_classes': [n_classes]
})
results.to_csv('/home/mouna/projet_memoire/results/dl_results.csv', index=False)
print("Résultats sauvegardés dans dl_results.csv")
