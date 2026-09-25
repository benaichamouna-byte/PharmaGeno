import pandas as pd, numpy as np, pickle, warnings, joblib
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, classification_report
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
with open(RESULTS_DIR+'/scaler_pgx_v2.pkl','rb') as f: scaler = pickle.load(f)
with open(DATA_DIR+'/drug_fingerprints.pkl','rb') as f: drug_fp = pickle.load(f)

df = pd.read_csv(DATA_DIR+'/phenotype_drug_dataset_complet_v2.csv')
df = df[df['drug'].isin(drug_fp)].copy()
df[GENES] = df[GENES].fillna(1.0)
print(f'Dataset : {len(df)} lignes')

X_genes = df[GENES].values.astype(float)
# Scaler fit dans chaque fold — pas ici (correction data leakage)
X_drugs_raw = np.array([drug_fp[d] for d in df['drug']])
X = np.hstack([X_genes, X_drugs_raw])
y = le.transform(df['action'].values)
n_genes = len(GENES)
n_classes = len(le.classes_)
print(f'Classes : {list(le.classes_)}')
print(f'Distribution : {dict(zip(le.classes_, np.bincount(y)))}')

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
    def forward(self, x):
        g = self.gene_branch(self.gene_attention(x[:,:n_genes]))
        d = self.drug_branch(x[:,n_genes:])
        return self.combined(torch.cat([g,d],dim=1))

def train_dl(Xtr, ytr, n_out, epochs=500, batch_size=512):
    from sklearn.preprocessing import StandardScaler
    # Scaler fit sur train uniquement
    sc = StandardScaler()
    Xtr_scaled = Xtr.copy()
    Xtr_scaled[:,n_genes:] = sc.fit_transform(Xtr[:,n_genes:])
    
    w = compute_class_weight('balanced',classes=np.unique(ytr),y=ytr)
    wt = torch.FloatTensor(w)
    m = PharmDL(n_out)
    opt = torch.optim.Adam(m.parameters(),lr=0.0005,weight_decay=0.005)
    sch = torch.optim.lr_scheduler.StepLR(opt,step_size=200,gamma=0.5)
    crit = nn.CrossEntropyLoss(weight=wt)
    ds = TensorDataset(torch.FloatTensor(Xtr_scaled), torch.LongTensor(ytr))
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
    Xte_scaled = Xte.copy()
    Xte_scaled[:,n_genes:] = sc.transform(Xte[:,n_genes:])
    with torch.no_grad():
        return np.argmax(torch.softmax(m(torch.FloatTensor(Xte_scaled)),dim=1).numpy(),axis=1)

ros = RandomOverSampler(random_state=42)
kf  = StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
res = {'XGB':[], 'DL':[]}

print('\n'+'='*60)
print('K-FOLD 5 FOLDS — DL + XGB uniquement (RF exclu RAM)')
print('='*60)

for fold,(tri,tei) in enumerate(kf.split(X,y)):
    Xtr,Xte = X[tri],X[tei]
    ytr,yte = y[tri],y[tei]
    Xb,yb = ros.fit_resample(Xtr,ytr)
    
    print(f'\nFold {fold+1}/5...',flush=True)
    
    xgb = XGBClassifier(100,random_state=42,verbosity=0,eval_metric='mlogloss')
    xgb.fit(Xb,yb)
    f1x = f1_score(yte,xgb.predict(Xte),average='macro',zero_division=0)
    res['XGB'].append(f1x)
    print(f'  XGB F1={round(f1x,3)}',flush=True)
    
    dl,sc = train_dl(Xb,yb,n_classes)
    f1d = f1_score(yte,pred_dl(dl,sc,Xte),average='macro',zero_division=0)
    res['DL'].append(f1d)
    print(f'  DL  F1={round(f1d,3)}',flush=True)
    print(f'Fold {fold+1} terminé — XGB:{round(f1x,3)} DL:{round(f1d,3)}',flush=True)

print('\n'+'='*60)
print('RESULTATS FINAUX K-FOLD VALIDES (sans data leakage)')
print('='*60)
for name,scores in res.items():
    a=np.array(scores)
    print(f'{name} F1: {round(a.mean(),3)} +/- {round(a.std(),3)}')
print('REFERENCE v1 : DL=0.875 XGB=0.962')
