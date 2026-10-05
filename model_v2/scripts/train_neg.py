"""
train_neg.py — Entrainement sur le corpus enrichi de paires sans association

Corpus : phenotype_drug_dataset_NEG.csv, 57 053 lignes.
La classe STANDARD y passe de 1,1 % a 20,1 % grace aux paires profil-medicament
sans association documentee dans les guidelines CPIC et DPWG.

Protocole identique a la validation groupee precedente : StratifiedGroupKFold sur
sample_id, cinq plis, scaler ajuste intra-pli, reechantillonnage sur le pli
d entrainement seul.

Les modeles sont enregistres sous le suffixe _neg. Aucun modele existant n est modifie.

Sorties : results/neg_scores.json, modeles *_neg
"""
import pandas as pd, numpy as np, pickle, warnings, gc, json, os, joblib
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import f1_score, precision_recall_fscore_support
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import RandomOverSampler
from xgboost import XGBClassifier
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
warnings.filterwarnings('ignore')

DATA_DIR    = '/home/mouna/projet_memoire/model_v2/data'
RESULTS_DIR = '/home/mouna/projet_memoire/model_v2/results'
SCORES      = f'{RESULTS_DIR}/neg_scores.json'

with open(f'{RESULTS_DIR}/genes_pgx_v2.pkl','rb') as f: GENES = pickle.load(f)
with open(f'{DATA_DIR}/drug_fingerprints.pkl','rb') as f: drug_fp = pickle.load(f)

df = pd.read_csv(f'{DATA_DIR}/phenotype_drug_dataset_NEG.csv')
df = df[df['drug'].isin(drug_fp)].copy()
df[GENES] = df[GENES].fillna(1.0)

X = np.hstack([df[GENES].values.astype(float),
               np.array([drug_fp[d] for d in df['drug']])])
le = LabelEncoder()
y = le.fit_transform(df['action'].values)
groups = df['sample_id'].values
n_genes, n_classes = len(GENES), len(le.classes_)
CLASSES = list(le.classes_)
iS = CLASSES.index('STANDARD')
iE = CLASSES.index('EVITER')

print(f'Corpus : {len(df)} lignes, {df["sample_id"].nunique()} groupes', flush=True)
print(f'Distribution : {dict(zip(CLASSES, np.bincount(y)))}', flush=True)

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

def entrainer_dl(Xa, ya, epochs=500, batch=256):
    sc = StandardScaler()
    Xs = Xa.copy(); Xs[:,n_genes:] = sc.fit_transform(Xa[:,n_genes:])
    w = compute_class_weight('balanced', classes=np.unique(ya), y=ya)
    m = PharmDL(n_classes)
    opt = torch.optim.Adam(m.parameters(), lr=0.0005, weight_decay=0.005)
    sch = torch.optim.lr_scheduler.StepLR(opt, step_size=200, gamma=0.5)
    crit = nn.CrossEntropyLoss(weight=torch.FloatTensor(w))
    loader = DataLoader(TensorDataset(torch.FloatTensor(Xs), torch.LongTensor(ya)),
                        batch_size=batch, shuffle=True)
    del Xs; gc.collect()
    for e in range(epochs):
        m.train()
        for Xb, yb in loader:
            opt.zero_grad(); crit(m(Xb), yb).backward()
            nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step()
        sch.step()
        if (e+1) % 100 == 0: print(f'      epoch {e+1}/500', flush=True)
    return m, sc

def mesures(ye, pred):
    p, r, f, _ = precision_recall_fscore_support(ye, pred, labels=range(n_classes), zero_division=0)
    n_ev = int((ye == iE).sum())
    manques = int(n_ev - ((ye == iE) & (pred == iE)).sum())
    return {
        'macro_f1':           round(float(f1_score(ye, pred, average='macro', zero_division=0)), 4),
        'standard_precision': round(float(p[iS]), 4),
        'standard_recall':    round(float(r[iS]), 4),
        'eviter_precision':   round(float(p[iE]), 4),
        'eviter_recall':      round(float(r[iE]), 4),
        'cer_strict':         round(manques / n_ev, 4) if n_ev else None,
    }

scores = json.load(open(SCORES)) if os.path.exists(SCORES) else {}
if scores: print(f'Plis deja calcules : {sorted(scores)}', flush=True)

ros  = RandomOverSampler(random_state=42)
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)

print('\n' + '='*64, flush=True)
print('ENTRAINEMENT SUR CORPUS ENRICHI — validation groupee par individu', flush=True)
print('='*64, flush=True)

for fold, (tri, tei) in enumerate(sgkf.split(X, y, groups)):
    key = str(fold+1)
    if key in scores:
        print(f'Pli {key}/5 deja calcule', flush=True); continue

    Xtr, Xte, ytr, yte = X[tri], X[tei], y[tri], y[tei]
    rec = len(set(groups[tri]) & set(groups[tei]))
    print(f'\nPli {key}/5 — {len(tei)} lignes test, recouvrement={rec}', flush=True)

    Xb, yb = ros.fit_resample(Xtr, ytr)
    res = {}

    xgb = XGBClassifier(100, random_state=42, verbosity=0, eval_metric='mlogloss')
    xgb.fit(Xb, yb)
    res['XGBoost'] = mesures(yte, xgb.predict(Xte))
    print(f"  XGBoost      F1={res['XGBoost']['macro_f1']}  "
          f"STANDARD prec={res['XGBoost']['standard_precision']}", flush=True)
    del xgb; gc.collect()

    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=2)
    rf.fit(Xb, yb)
    res['RandomForest'] = mesures(yte, rf.predict(Xte))
    print(f"  RandomForest F1={res['RandomForest']['macro_f1']}  "
          f"STANDARD prec={res['RandomForest']['standard_precision']}", flush=True)
    del rf; gc.collect()

    dl, sc = entrainer_dl(Xb, yb)
    dl.eval()
    Xs = Xte.copy(); Xs[:,n_genes:] = sc.transform(Xte[:,n_genes:])
    with torch.no_grad():
        pred = np.argmax(torch.softmax(dl(torch.FloatTensor(Xs)), dim=1).numpy(), axis=1)
    res['DL'] = mesures(yte, pred)
    print(f"  DL           F1={res['DL']['macro_f1']}  "
          f"STANDARD prec={res['DL']['standard_precision']}", flush=True)
    del dl, Xb, yb, Xtr, Xte, Xs; gc.collect()

    scores[key] = res
    json.dump(scores, open(SCORES,'w'), indent=2)
    print(f'  Pli {key} enregistre', flush=True)

# --- Modeles de production sur l ensemble du corpus --------------------------
print('\n' + '='*64, flush=True)
print('MODELES DE PRODUCTION', flush=True)
print('='*64, flush=True)

Xall, yall = ros.fit_resample(X, y)

sc_prod = StandardScaler()
Xs_all = X.copy(); Xs_all[:,n_genes:] = sc_prod.fit_transform(X[:,n_genes:])

xgb_f = XGBClassifier(200, random_state=42, verbosity=0, eval_metric='mlogloss')
xgb_f.fit(Xall, yall)
joblib.dump(xgb_f, f'{RESULTS_DIR}/xgb_pgx_neg.pkl')
print('XGBoost enregistre', flush=True)
del xgb_f; gc.collect()

rf_f = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=2)
rf_f.fit(Xall, yall)
joblib.dump(rf_f, f'{RESULTS_DIR}/rf_pgx_neg.pkl')
print('RandomForest enregistre', flush=True)
del rf_f; gc.collect()

dl_f, sc_f = entrainer_dl(Xall, yall)
torch.save(dl_f.state_dict(), f'{RESULTS_DIR}/dl_pgx_neg.pth')
with open(f'{RESULTS_DIR}/scaler_pgx_neg.pkl','wb') as f: pickle.dump(sc_f, f)
with open(f'{RESULTS_DIR}/le_pgx_neg.pkl','wb') as f: pickle.dump(le, f)
with open(f'{RESULTS_DIR}/genes_pgx_neg.pkl','wb') as f: pickle.dump(GENES, f)
print('DL et encodeurs enregistres', flush=True)

# --- Synthese ----------------------------------------------------------------
print('\n' + '='*64, flush=True)
print('RESULTATS — corpus enrichi', flush=True)
print('='*64, flush=True)
REF = {'XGBoost': 0.9554, 'RandomForest': 0.9386, 'DL': 0.8847}
for m in ['XGBoost','RandomForest','DL']:
    f1 = np.array([scores[k][m]['macro_f1'] for k in sorted(scores)])
    sp = np.array([scores[k][m]['standard_precision'] for k in sorted(scores)])
    ce = np.array([scores[k][m]['cer_strict'] for k in sorted(scores)])
    print(f'{m:14s} F1 {f1.mean():.4f} ± {f1.std():.4f}   '
          f'(corpus precedent {REF[m]:.4f}, ecart {f1.mean()-REF[m]:+.4f})', flush=True)
    print(f'{"":14s} STANDARD precision {sp.mean():.4f}   CER strict {ce.mean():.4f}', flush=True)
