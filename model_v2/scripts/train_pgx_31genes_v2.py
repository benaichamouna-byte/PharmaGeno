import pandas as pd, numpy as np, joblib, pickle, warnings
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import f1_score, classification_report
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import RandomOverSampler
from xgboost import XGBClassifier
import torch, torch.nn as nn
warnings.filterwarnings('ignore')

DATA_DIR    = '/home/mouna/projet_memoire/model_v2/data'
RESULTS_DIR = '/home/mouna/projet_memoire/model_v2/results'

GENES = ['ABCG2','ACE','ADRB2','CACNA1S','CFTR','CYP1A2','CYP2A6',
         'CYP2B6','CYP2C19','CYP2C9','CYP2D6','CYP3A4','CYP3A5',
         'CYP4F2','DPYD','EGFR','F5','G6PD','HLA-A','HLA-B',
         'IFNL3','MT-RNR1','MTHFR','NAT2','NUDT15','RYR1',
         'SLC19A1','SLCO1B1','TPMT','UGT1A1','VKORC1']

df = pd.read_csv(DATA_DIR + '/phenotype_drug_dataset_complet.csv')
with open(RESULTS_DIR + '/drug_fp_ref.pkl','rb') as f: drug_fp = pickle.load(f)

GENES = [g for g in GENES if g in df.columns]
df = df[df['drug'].isin(drug_fp)].copy()
df[GENES] = df[GENES].fillna(1.0)
print('Dataset : ' + str(len(df)) + ' lignes, ' + str(len(GENES)) + ' genes')

X_genes = df[GENES].values.astype(float)
X_drugs = np.array([drug_fp[d] for d in df['drug']])
scaler  = StandardScaler()
X_drugs = scaler.fit_transform(X_drugs)
X = np.hstack([X_genes, X_drugs])

le = LabelEncoder()
y  = le.fit_transform(df['action'].values)
print('Classes : ' + str(list(le.classes_)))
print('Distribution : ' + str(dict(zip(le.classes_, np.bincount(y)))))

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

def train_dl(Xtr,ytr,n_out):
    w  = compute_class_weight('balanced',classes=np.unique(ytr),y=ytr)
    wt = torch.FloatTensor(w)
    m  = PharmDL(n_out)
    opt = torch.optim.Adam(m.parameters(),lr=0.0005,weight_decay=0.005)
    sch = torch.optim.lr_scheduler.StepLR(opt,step_size=200,gamma=0.5)
    crit = nn.CrossEntropyLoss(weight=wt)
    xt,yt = torch.FloatTensor(Xtr),torch.LongTensor(ytr)
    for _ in range(500):
        m.train(); opt.zero_grad()
        crit(m(xt),yt).backward(); opt.step(); sch.step()
    return m

def pred_dl(m,Xte):
    m.eval()
    with torch.no_grad():
        probs = torch.softmax(m(torch.FloatTensor(Xte)),dim=1).numpy()
        return np.argmax(probs,axis=1), probs

ros = RandomOverSampler(random_state=42)
kf  = StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
res = {'RF':[],'XGB':[],'DL':[]}

print('')
print('='*60)
print('K-FOLD 5 FOLDS — Dataset 31 genes Morgan FP')
print('='*60)

for fold,(tri,tei) in enumerate(kf.split(X,y)):
    Xtr,Xte = X[tri],X[tei]
    ytr,yte = y[tri],y[tei]
    Xb,yb = ros.fit_resample(Xtr,ytr)
    rf  = RandomForestClassifier(200,random_state=42); rf.fit(Xb,yb)
    xgb = XGBClassifier(100,random_state=42,verbosity=0,eval_metric='mlogloss'); xgb.fit(Xb,yb)
    dl  = train_dl(Xtr,ytr,n_classes)
    f1r = f1_score(yte,rf.predict(Xte),average='macro',zero_division=0)
    f1x = f1_score(yte,xgb.predict(Xte),average='macro',zero_division=0)
    f1d = f1_score(yte,pred_dl(dl,Xte)[0],average='macro',zero_division=0)
    res['RF'].append(f1r); res['XGB'].append(f1x); res['DL'].append(f1d)
    print('Fold '+str(fold+1)+' RF:'+str(round(f1r,3))+' XGB:'+str(round(f1x,3))+' DL:'+str(round(f1d,3)))

print('')
print('='*60)
print('RESULTATS FINAUX')
print('='*60)
for name,scores in res.items():
    a = np.array(scores)
    print(name+' F1: '+str(round(a.mean(),3))+' +/- '+str(round(a.std(),3)))

print('A COMPARER : DL=0.834+/-0.018  XGB=0.881+/-0.003  RF=0.795+/-0.004')

# Entrainement final
Xall,yall = ros.fit_resample(X,y)
rf_f  = RandomForestClassifier(200,random_state=42); rf_f.fit(Xall,yall)
xgb_f = XGBClassifier(200,random_state=42,verbosity=0,eval_metric='mlogloss'); xgb_f.fit(Xall,yall)
dl_f  = train_dl(X,y,n_classes)

joblib.dump(rf_f,  RESULTS_DIR+'/rf_pgx_31genes.pkl')
joblib.dump(xgb_f, RESULTS_DIR+'/xgb_pgx_31genes.pkl')
torch.save(dl_f.state_dict(), RESULTS_DIR+'/dl_pgx_31genes.pth')
with open(RESULTS_DIR+'/le_pgx_31genes.pkl','wb') as f: pickle.dump(le,f)
with open(RESULTS_DIR+'/genes_pgx_31genes.pkl','wb') as f: pickle.dump(GENES,f)
with open(RESULTS_DIR+'/scaler_pgx_31genes.pkl','wb') as f: pickle.dump(scaler,f)
with open(RESULTS_DIR+'/drug_fp_ref.pkl','wb') as f: pickle.dump(drug_fp,f)
print('Modeles sauvegardes sous *_31genes')
