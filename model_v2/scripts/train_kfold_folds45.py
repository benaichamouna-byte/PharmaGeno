import pandas as pd, numpy as np, pickle, warnings, gc
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import f1_score
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import RandomOverSampler
from xgboost import XGBClassifier
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

def train_dl(Xtr, ytr, n_out, epochs=500, batch_size=256):
    sc = StandardScaler()
    Xtr_s = Xtr.copy()
    Xtr_s[:,n_genes:] = sc.fit_transform(Xtr[:,n_genes:])
    w = compute_class_weight('balanced',classes=np.unique(ytr),y=ytr)
    m = PharmDL(n_out)
    opt = torch.optim.Adam(m.parameters(),lr=0.0005,weight_decay=0.005)
    sch = torch.optim.lr_scheduler.StepLR(opt,step_size=200,gamma=0.5)
    crit = nn.CrossEntropyLoss(weight=torch.FloatTensor(w))
    ds = TensorDataset(torch.FloatTensor(Xtr_s), torch.LongTensor(ytr))
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True)
    for epoch in range(epochs):
        m.train()
        for Xb,yb in loader:
            opt.zero_grad()
            crit(m(Xb),yb).backward()
            nn.utils.clip_grad_norm_(m.parameters(),1.0)
            opt.step()
        sch.step()
        if (epoch+1)%100==0:
            print(f'  DL epoch {epoch+1}/500', flush=True)
    return m, sc

def pred_dl(m, sc, Xte):
    m.eval()
    Xte_s = Xte.copy()
    Xte_s[:,n_genes:] = sc.transform(Xte[:,n_genes:])
    with torch.no_grad():
        return np.argmax(torch.softmax(m(torch.FloatTensor(Xte_s)),dim=1).numpy(),axis=1)

ros = RandomOverSampler(random_state=42)
kf  = StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
folds = list(kf.split(X,y))

print('FOLDS 4 et 5 uniquement', flush=True)

for fold_idx in [3, 4]:
    tri, tei = folds[fold_idx]
    Xtr,Xte = X[tri],X[tei]
    ytr,yte = y[tri],y[tei]
    Xb,yb = ros.fit_resample(Xtr,ytr)
    print(f'Fold {fold_idx+1}/5...', flush=True)
    xgb = XGBClassifier(100,random_state=42,verbosity=0,eval_metric='mlogloss')
    xgb.fit(Xb,yb)
    f1x = f1_score(yte,xgb.predict(Xte),average='macro',zero_division=0)
    print(f'  XGB F1={round(f1x,3)}', flush=True)
    del xgb; gc.collect()
    dl,sc = train_dl(Xb,yb,n_classes)
    f1d = f1_score(yte,pred_dl(dl,sc,Xte),average='macro',zero_division=0)
    print(f'  DL  F1={round(f1d,3)}', flush=True)
    print(f'Fold {fold_idx+1} termine — XGB:{round(f1x,3)} DL:{round(f1d,3)}', flush=True)
    del dl, Xb, yb; gc.collect()

print('FOLDS 4-5 TERMINES')
