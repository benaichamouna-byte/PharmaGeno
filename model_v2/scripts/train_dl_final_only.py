import pandas as pd, numpy as np, pickle, warnings
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.utils.class_weight import compute_class_weight
import torch, torch.nn as nn
warnings.filterwarnings('ignore')

DATA_DIR    = '/home/mouna/projet_memoire/model_v2/data'
RESULTS_DIR = '/home/mouna/projet_memoire/model_v2/results'

with open(RESULTS_DIR+'/le_pgx_v2.pkl','rb') as f: le = pickle.load(f)
with open(RESULTS_DIR+'/genes_pgx_v2.pkl','rb') as f: GENES = pickle.load(f)
with open(RESULTS_DIR+'/scaler_pgx_v2.pkl','rb') as f: scaler = pickle.load(f)
with open(DATA_DIR+'/drug_fingerprints.pkl','rb') as f: drug_fp = pickle.load(f)

df = pd.read_csv(DATA_DIR+'/phenotype_drug_dataset_complet_v2.csv')
df = df[df['drug'].isin(drug_fp)].copy()
df[GENES] = df[GENES].fillna(1.0)
print(f'Dataset : {len(df)} lignes, {len(GENES)} genes')

X_genes = df[GENES].values.astype(float)
X_drugs = scaler.transform(np.array([drug_fp[d] for d in df['drug']]))
X = np.hstack([X_genes, X_drugs])
y = le.transform(df['action'].values)
n_genes = len(GENES)
n_classes = len(le.classes_)
print(f'Classes : {list(le.classes_)}')

class GeneAttention(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.attn = nn.Linear(n, n)
    def forward(self, x):
        return x * torch.softmax(self.attn(x), dim=1)

class PharmDL(nn.Module):
    def __init__(self, n_out):
        super().__init__()
        self.gene_attention = GeneAttention(n_genes)
        self.gene_branch = nn.Sequential(
            nn.Linear(n_genes,64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64,32), nn.BatchNorm1d(32), nn.ReLU())
        self.drug_branch = nn.Sequential(
            nn.Linear(518,256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(256,128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128,64), nn.ReLU())
        self.combined = nn.Sequential(
            nn.Linear(96,64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64,32), nn.ReLU(), nn.Linear(32,n_out))
    def forward(self,x):
        g = self.gene_branch(self.gene_attention(x[:,:n_genes]))
        d = self.drug_branch(x[:,n_genes:])
        return self.combined(torch.cat([g,d],dim=1))

print('Entraînement DL final — 500 epochs...')
w  = compute_class_weight('balanced',classes=np.unique(y),y=y)
wt = torch.FloatTensor(w)
dl = PharmDL(n_classes)
opt = torch.optim.Adam(dl.parameters(),lr=0.0005,weight_decay=0.005)
sch = torch.optim.lr_scheduler.StepLR(opt,step_size=200,gamma=0.5)
crit = nn.CrossEntropyLoss(weight=wt)
xt,yt = torch.FloatTensor(X),torch.LongTensor(y)

for epoch in range(500):
    dl.train(); opt.zero_grad()
    loss = crit(dl(xt),yt)
    loss.backward(); opt.step(); sch.step()
    if (epoch+1) % 100 == 0:
        torch.save(dl.state_dict(), RESULTS_DIR+'/dl_pgx_v2.pth')
        dl.eval()
        with torch.no_grad():
            y_pred = np.argmax(torch.softmax(dl(xt),dim=1).numpy(),axis=1)
        from sklearn.metrics import f1_score
        f1 = f1_score(y,y_pred,average='macro',zero_division=0)
        print(f'Epoch {epoch+1}/500 — Loss: {loss.item():.4f} — F1: {round(f1,3)}')
        dl.train()

torch.save(dl.state_dict(), RESULTS_DIR+'/dl_pgx_v2.pth')
print('DL final sauvegardé — 500 epochs complets')

from sklearn.metrics import classification_report, f1_score
dl.eval()
with torch.no_grad():
    y_dl = np.argmax(torch.softmax(dl(xt),dim=1).numpy(),axis=1)
print(f'\nF1 DL final : {round(f1_score(y,y_dl,average="macro",zero_division=0),3)}')
print(classification_report(y,y_dl,target_names=le.classes_,zero_division=0))
