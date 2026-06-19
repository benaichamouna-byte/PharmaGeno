import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import torch
import torch.nn as nn
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

columns = list(X_ohe.columns)
X = X_ohe.values

le_pheno = LabelEncoder()
y = le_pheno.fit_transform(df['phenotype'])
classes = list(le_pheno.classes_)

print(f"Features : {X.shape[1]} colonnes")
print(f"Classes  : {classes}")

smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42)

input_size = X_train.shape[1]
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

model     = PharmDLv5()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=50, gamma=0.5)

print("Entraînement...")
X_train_t = torch.FloatTensor(X_train)
y_train_t = torch.LongTensor(y_train)

for epoch in range(200):
    model.train()
    optimizer.zero_grad()
    loss = criterion(model(X_train_t), y_train_t)
    loss.backward()
    optimizer.step()
    scheduler.step()
    if (epoch+1) % 50 == 0:
        print(f"Epoch {epoch+1}/200 - Loss: {loss.item():.4f}")

torch.save(model.state_dict(), '/home/mouna/projet_memoire/results/dl_v5_final.pth')
with open('/home/mouna/projet_memoire/results/dl_v5_columns.pkl', 'wb') as f:
    pickle.dump(columns, f)
with open('/home/mouna/projet_memoire/results/dl_v5_classes.pkl', 'wb') as f:
    pickle.dump(classes, f)

print(f"\nModèle sauvegardé : dl_v5_final.pth")
print(f"Colonnes : dl_v5_columns.pkl — {len(columns)} colonnes")
print(f"Classes  : dl_v5_classes.pkl — {classes}")
