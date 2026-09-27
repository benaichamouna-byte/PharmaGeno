import pandas as pd, numpy as np, pickle, warnings, gc, json, os
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import RandomOverSampler
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
warnings.filterwarnings('ignore')

DATA_DIR    = '/home/mouna/projet_memoire/model_v2/data'
RESULTS_DIR = '/home/mouna/projet_memoire/model_v2/results'

with open(RESULTS_DIR+'/le_pgx_v2.pkl','rb') as f: le = pickle.load(f)
with open(RESULTS_DIR+'/genes_pgx_v2.pkl','rb') as f: GENES = pickle.load(f)
with open(DATA_DIR+'/drug_fingerprints.pkl','rb') as f: drug_fp = pickle.load(f)

df = pd.read_csv(DATA_DIR+'/phenotype_drug_dataset_complet_v2.csv')
df = df[df['drug'].isin(drug_fp)].copy()
df[GENES] = df[GENES].fillna(1.0)

X = np.hstack([df[GENES].values.astype(float),
               np.array([drug_fp[d] for d in df['drug']])])
y = le.transform(df['action'].values)
n_genes = len(GENES)
n_classes = len(le.classes_)
print(f'Dataset : {len(df)} lignes', flush=True)

class GeneAttention(nn.Module):
    def __init__(self, n):
        super().__init__(); self.attn = nn.Linear(n, n)
    def forward(self, x): return x * torch.softmax(self.attn(x), dim=1)

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
    def forward(self, x):
        g = self.gene_branch(self.gene_attention(x[:,:n_genes]))
        d = self.drug_branch(x[:,n_genes:])
        return self.combined(torch.cat([g,d],dim=1))

ros = RandomOverSampler(random_state=42)
kf = StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
folds = list(kf.split(X,y))

tri, tei = folds[4]
Xtr,Xte = X[tri],X[tei]
ytr,yte = y[tri],y[tei]
Xb,yb = ros.fit_resample(Xtr,ytr)
del Xtr, X; gc.collect()

print('FOLD 5 — DL uniquement', flush=True)

sc = StandardScaler()
Xb_s = Xb.copy()
Xb_s[:,n_genes:] = sc.fit_transform(Xb[:,n_genes:])
del Xb; gc.collect()

w = compute_class_weight('balanced',classes=np.unique(yb),y=yb)
m = PharmDL(n_classes)
opt = torch.optim.Adam(m.parameters(),lr=0.0005,weight_decay=0.005)
sch = torch.optim.lr_scheduler.StepLR(opt,step_size=200,gamma=0.5)
crit = nn.CrossEntropyLoss(weight=torch.FloatTensor(w))
ds = TensorDataset(torch.FloatTensor(Xb_s), torch.LongTensor(yb))
loader = DataLoader(ds, batch_size=256, shuffle=True)
del Xb_s; gc.collect()

for epoch in range(500):
    m.train()
    for Xbatch,ybatch in loader:
        opt.zero_grad()
        crit(m(Xbatch),ybatch).backward()
        nn.utils.clip_grad_norm_(m.parameters(),1.0)
        opt.step()
    sch.step()
    if (epoch+1)%50==0:
        print(f'  epoch {epoch+1}/500', flush=True)

m.eval()
Xte_s = Xte.copy()
Xte_s[:,n_genes:] = sc.transform(Xte[:,n_genes:])
with torch.no_grad():
    pred = np.argmax(torch.softmax(m(torch.FloatTensor(Xte_s)),dim=1).numpy(),axis=1)
f1 = f1_score(yte,pred,average='macro',zero_division=0)

print(f'FOLD 5 DL F1 = {round(f1,4)}', flush=True)
with open(RESULTS_DIR+'/dl_fold5_score.json','w') as f:
    json.dump({'fold5_dl': round(float(f1),4)}, f)
print('Score sauvegardé', flush=True)
