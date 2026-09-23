import pandas as pd, numpy as np, joblib, pickle, warnings
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import f1_score, classification_report
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import RandomOverSampler
from xgboost import XGBClassifier
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
warnings.filterwarnings('ignore')

DATA_DIR    = '/home/mouna/projet_memoire/model_v2/data'
RESULTS_DIR = '/home/mouna/projet_memoire/model_v2/results'

df = pd.read_csv(DATA_DIR + '/phenotype_drug_dataset_complet_v2.csv')
with open(DATA_DIR + '/drug_fingerprints.pkl','rb') as f: drug_fp = pickle.load(f)
with open(RESULTS_DIR + '/scaler_pgx_v2.pkl','rb') as f: scaler = pickle.load(f)

META = ['drug','action']
GENES = sorted([c for c in df.columns if c not in META])
df = df[df['drug'].isin(drug_fp)].copy()
df[GENES] = df[GENES].fillna(1.0)
print(f'Dataset : {len(df)} lignes, {len(GENES)} genes')

X_genes = df[GENES].values.astype(float)
X_drugs = scaler.transform(np.array([drug_fp[d] for d in df['drug']]))
X       = np.hstack([X_genes, X_drugs])

le = LabelEncoder()
y  = le.fit_transform(df['action'].values)
print(f'Classes : {list(le.classes_)}')
print(f'Distribution : {dict(zip(le.classes_, np.bincount(y)))}')

# Sauvegarder encodeurs
with open(RESULTS_DIR+'/le_pgx_v2.pkl','wb') as f: pickle.dump(le,f)
with open(RESULTS_DIR+'/genes_pgx_v2.pkl','wb') as f: pickle.dump(GENES,f)
print('Encodeurs sauvegardés')

n_genes   = len(GENES)
n_classes = len(le.classes_)

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

def train_dl_minibatch(Xtr, ytr, n_out, epochs=500, batch_size=512):
    w    = compute_class_weight('balanced',classes=np.unique(ytr),y=ytr)
    wt   = torch.FloatTensor(w)
    m    = PharmDL(n_out)
    opt  = torch.optim.Adam(m.parameters(),lr=0.0005,weight_decay=0.005)
    sch  = torch.optim.lr_scheduler.StepLR(opt,step_size=200,gamma=0.5)
    crit = nn.CrossEntropyLoss(weight=wt)
    
    ds     = TensorDataset(torch.FloatTensor(Xtr), torch.LongTensor(ytr))
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=False)
    
    for epoch in range(epochs):
        m.train()
        for Xb, yb in loader:
            opt.zero_grad()
            crit(m(Xb), yb).backward()
            nn.utils.clip_grad_norm_(m.parameters(), max_norm=1.0)
            opt.step()
        sch.step()
        if (epoch+1) % 100 == 0:
            m.eval()
            with torch.no_grad():
                preds = np.argmax(torch.softmax(m(torch.FloatTensor(Xtr)),dim=1).numpy(),axis=1)
            f1 = f1_score(ytr, preds, average='macro', zero_division=0)
            print(f'  Epoch {epoch+1}/500 — F1 train: {round(f1,3)}')
            m.train()
    return m

def pred_dl(m, Xte):
    m.eval()
    with torch.no_grad():
        return np.argmax(torch.softmax(m(torch.FloatTensor(Xte)),dim=1).numpy(),axis=1)

ros = RandomOverSampler(random_state=42)
kf  = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
res = {'RF':[], 'XGB':[], 'DL':[]}

print()
print('='*60)
print('K-FOLD 5 FOLDS — Dataset v2 CPIC validé — Mini-batches')
print('='*60)

for fold,(tri,tei) in enumerate(kf.split(X,y)):
    Xtr,Xte = X[tri],X[tei]
    ytr,yte = y[tri],y[tei]
    Xb,yb   = ros.fit_resample(Xtr,ytr)
    Xg_b    = Xb[:,:n_genes]
    Xd_b    = Xb[:,n_genes:]
    
    rf  = RandomForestClassifier(200,random_state=42,n_jobs=-1)
    rf.fit(Xb,yb)
    f1r = f1_score(yte,rf.predict(Xte),average='macro',zero_division=0)
    res['RF'].append(f1r)
    
    xgb = XGBClassifier(100,random_state=42,verbosity=0,eval_metric='mlogloss')
    xgb.fit(Xb,yb)
    f1x = f1_score(yte,xgb.predict(Xte),average='macro',zero_division=0)
    res['XGB'].append(f1x)
    
    dl  = train_dl_minibatch(Xb, yb, n_classes, epochs=500, batch_size=512)
    f1d = f1_score(yte, pred_dl(dl,Xte), average='macro', zero_division=0)
    res['DL'].append(f1d)
    
    print(f'Fold {fold+1} RF:{round(f1r,3)} XGB:{round(f1x,3)} DL:{round(f1d,3)}')

print()
print('='*60)
print('RESULTATS FINAUX K-FOLD — Dataset v2')
print('='*60)
for name,scores in res.items():
    a = np.array(scores)
    print(f'{name} F1: {round(a.mean(),3)} +/- {round(a.std(),3)}')
print('A COMPARER : DL=0.875  XGB=0.962  RF=0.940 (dataset v1 K-Fold)')

# Entrainement final
print('\nEntrainement final...')
Xall,yall = ros.fit_resample(X,y)
rf_f  = RandomForestClassifier(200,random_state=42,n_jobs=-1); rf_f.fit(Xall,yall)
joblib.dump(rf_f, RESULTS_DIR+'/rf_pgx_v2.pkl')
print('RF v2 sauvegardé')

xgb_f = XGBClassifier(200,random_state=42,verbosity=0,eval_metric='mlogloss'); xgb_f.fit(Xall,yall)
joblib.dump(xgb_f, RESULTS_DIR+'/xgb_pgx_v2.pkl')
print('XGB v2 sauvegardé')

dl_f = train_dl_minibatch(Xall, yall, n_classes, epochs=500, batch_size=512)
torch.save(dl_f.state_dict(), RESULTS_DIR+'/dl_pgx_v2.pth')
print('DL v2 sauvegardé')

print('\nRapport DL final :')
dl_f.eval()
with torch.no_grad():
    y_dl = np.argmax(torch.softmax(dl_f(torch.FloatTensor(X)),dim=1).numpy(),axis=1)
print(classification_report(y, y_dl, target_names=le.classes_, zero_division=0))
print('Tous modèles v2 sauvegardés — jamais *_31genes')
