import pandas as pd, numpy as np, pickle, warnings, gc, json, os
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier
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
SCORES      = f'{RESULTS_DIR}/groupkfold_scores.json'

with open(f'{RESULTS_DIR}/genes_pgx_v2.pkl','rb') as f: GENES = pickle.load(f)
with open(f'{DATA_DIR}/drug_fingerprints.pkl','rb') as f: drug_fp = pickle.load(f)

df = pd.read_csv(f'{DATA_DIR}/phenotype_drug_dataset_FINAL.csv')
df = df[df['drug'].isin(drug_fp)].copy()
df[GENES] = df[GENES].fillna(1.0)

X = np.hstack([df[GENES].values.astype(float),
               np.array([drug_fp[d] for d in df['drug']])])
le = LabelEncoder()
y = le.fit_transform(df['action'].values)
groups = df['sample_id'].values
n_genes, n_classes = len(GENES), len(le.classes_)

print(f'Dataset : {len(df)} lignes, {df["sample_id"].nunique()} groupes', flush=True)
print(f'Classes : {list(le.classes_)}', flush=True)

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

def train_dl(Xtr, ytr, epochs=500, batch_size=256):
    sc = StandardScaler()
    Xs = Xtr.copy(); Xs[:,n_genes:] = sc.fit_transform(Xtr[:,n_genes:])
    w = compute_class_weight('balanced', classes=np.unique(ytr), y=ytr)
    m = PharmDL(n_classes)
    opt = torch.optim.Adam(m.parameters(), lr=0.0005, weight_decay=0.005)
    sch = torch.optim.lr_scheduler.StepLR(opt, step_size=200, gamma=0.5)
    crit = nn.CrossEntropyLoss(weight=torch.FloatTensor(w))
    loader = DataLoader(TensorDataset(torch.FloatTensor(Xs), torch.LongTensor(ytr)),
                        batch_size=batch_size, shuffle=True)
    del Xs; gc.collect()
    for e in range(epochs):
        m.train()
        for Xb, yb in loader:
            opt.zero_grad(); crit(m(Xb), yb).backward()
            nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step()
        sch.step()
        if (e+1) % 100 == 0: print(f'    DL epoch {e+1}/500', flush=True)
    return m, sc

scores = json.load(open(SCORES)) if os.path.exists(SCORES) else {}
if scores: print(f'Plis deja calcules : {sorted(scores)}', flush=True)

ros = RandomOverSampler(random_state=42)
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)

print('', flush=True)
print('='*60, flush=True)
print('VALIDATION CROISEE GROUPEE PAR INDIVIDU', flush=True)
print('='*60, flush=True)

for fold, (tri, tei) in enumerate(sgkf.split(X, y, groups)):
    key = str(fold+1)
    if key in scores:
        print(f'Pli {key}/5 deja calcule : {scores[key]}', flush=True); continue

    Xtr, Xte = X[tri], X[tei]
    ytr, yte = y[tri], y[tei]
    n_ind_te = len(set(groups[tei]))
    recouvrement = len(set(groups[tri]) & set(groups[tei]))
    print('', flush=True)
    print(f'Pli {key}/5 — {len(tei)} lignes test, {n_ind_te} individus, recouvrement={recouvrement}', flush=True)

    Xb, yb = ros.fit_resample(Xtr, ytr)
    res = {}

    xgb = XGBClassifier(100, random_state=42, verbosity=0, eval_metric='mlogloss')
    xgb.fit(Xb, yb)
    res['XGBoost'] = round(float(f1_score(yte, xgb.predict(Xte), average='macro', zero_division=0)), 4)
    print(f"  XGBoost F1={res['XGBoost']}", flush=True)
    del xgb; gc.collect()

    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=2)
    rf.fit(Xb, yb)
    res['RandomForest'] = round(float(f1_score(yte, rf.predict(Xte), average='macro', zero_division=0)), 4)
    print(f"  RandomForest F1={res['RandomForest']}", flush=True)
    del rf; gc.collect()

    dl, sc = train_dl(Xb, yb)
    dl.eval()
    Xs = Xte.copy(); Xs[:,n_genes:] = sc.transform(Xte[:,n_genes:])
    with torch.no_grad():
        pred = np.argmax(torch.softmax(dl(torch.FloatTensor(Xs)), dim=1).numpy(), axis=1)
    res['DL'] = round(float(f1_score(yte, pred, average='macro', zero_division=0)), 4)
    print(f"  DL F1={res['DL']}", flush=True)
    del dl, Xb, yb, Xtr, Xte, Xs; gc.collect()

    scores[key] = res
    json.dump(scores, open(SCORES,'w'), indent=2)
    print(f'  Pli {key} enregistre', flush=True)

print('', flush=True)
print('='*60, flush=True)
print('RESULTATS — VALIDATION GROUPEE PAR INDIVIDU', flush=True)
print('='*60, flush=True)
REF = {'XGBoost': 0.954, 'RandomForest': 0.932, 'DL': 0.899}
for m in ['XGBoost','RandomForest','DL']:
    v = np.array([scores[k][m] for k in sorted(scores) if m in scores[k]])
    if len(v):
        print(f'{m:14s} {v.mean():.3f} +/- {v.std():.3f}   (non groupe : {REF[m]:.3f}, ecart {v.mean()-REF[m]:+.3f})', flush=True)
