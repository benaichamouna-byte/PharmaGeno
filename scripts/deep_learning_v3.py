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

df['phenotype_grouped'] = df['phenotype'].apply(regroup)

# ONE-HOT ENCODING
print("One-Hot Encoding...")
X = pd.get_dummies(df[['gene', 'drug']], columns=['gene', 'drug']).values.astype(np.float32)
le_pheno = LabelEncoder()
y = le_pheno.fit_transform(df['phenotype_grouped'])

print(f"Features : {X.shape[1]} colonnes")
print(f"Classes  : {le_pheno.classes_}")

# SMOTE
print("SMOTE...")
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)
print(f"Après SMOTE : {len(X_res)} exemples")

X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)

# MODÈLE
input_size = X_train.shape[1]
class PharmDL(nn.Module):
    def __init__(self):
        super(PharmDL, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, 4)
        )
    def forward(self, x):
        return self.net(x)

model     = PharmDL()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=50, gamma=0.5)

print("Entraînement...")
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
print(f"Accuracy DL v1 : 44.8%")
print(f"Accuracy DL v2 : 31.1%")
print(f"Accuracy DL v3 : {accuracy*100:.1f}%")
print(f"\nRapport :")
print(classification_report(y_test, y_pred, target_names=le_pheno.classes_, zero_division=0))

torch.save(model.state_dict(), '/home/mouna/projet_memoire/results/dl_v3_model.pth')
print("Modèle sauvegardé.")
