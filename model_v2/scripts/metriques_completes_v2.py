"""
metriques_completes_v2.py — Metriques completes des 3 modeles sur dataset v2

Calcule pour chaque modele (DL, XGBoost, RF) :
- Macro-F1, Weighted-F1, Balanced Accuracy
- Precision / Recall / F1 par classe
- Matrice de confusion agregee sur les 5 folds
- Critical Error Rate : EVITER predit comme STANDARD ou SURVEILLER

Protocole identique au K-Fold valide : StratifiedKFold(5, shuffle=True, random_state=42),
RandomOverSampler sur train uniquement, scaler fit intra-fold.

Sorties : metriques_completes_v2.json, metriques_completes_v2.md, confusion_matrices_v2.png
"""
import pandas as pd, numpy as np, pickle, warnings, gc, json
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (f1_score, balanced_accuracy_score, confusion_matrix,
                             precision_recall_fscore_support)
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import RandomOverSampler
from xgboost import XGBClassifier
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
n_genes   = len(GENES)
n_classes = len(le.classes_)
CLASSES   = list(le.classes_)
print(f'Dataset : {len(df)} lignes, {X.shape[1]} features', flush=True)
print(f'Classes : {CLASSES}', flush=True)

IDX_EVITER     = CLASSES.index('EVITER')
IDX_STANDARD   = CLASSES.index('STANDARD')
IDX_SURVEILLER = CLASSES.index('SURVEILLER')

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
    Xtr_s = Xtr.copy()
    Xtr_s[:,n_genes:] = sc.fit_transform(Xtr[:,n_genes:])
    w = compute_class_weight('balanced', classes=np.unique(ytr), y=ytr)
    m = PharmDL(n_classes)
    opt = torch.optim.Adam(m.parameters(), lr=0.0005, weight_decay=0.005)
    sch = torch.optim.lr_scheduler.StepLR(opt, step_size=200, gamma=0.5)
    crit = nn.CrossEntropyLoss(weight=torch.FloatTensor(w))
    ds = TensorDataset(torch.FloatTensor(Xtr_s), torch.LongTensor(ytr))
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True)
    del Xtr_s; gc.collect()
    for epoch in range(epochs):
        m.train()
        for Xb, yb in loader:
            opt.zero_grad()
            crit(m(Xb), yb).backward()
            nn.utils.clip_grad_norm_(m.parameters(), 1.0)
            opt.step()
        sch.step()
        if (epoch+1) % 100 == 0:
            print(f'    DL epoch {epoch+1}/500', flush=True)
    return m, sc

ros = RandomOverSampler(random_state=42)
kf  = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Collecte des predictions out-of-fold pour chaque modele
y_true_all = []
preds = {'DL': [], 'XGBoost': [], 'RandomForest': []}

for fold, (tri, tei) in enumerate(kf.split(X, y)):
    print(f'\nFold {fold+1}/5', flush=True)
    Xtr, Xte = X[tri], X[tei]
    ytr, yte = y[tri], y[tei]
    Xb, yb = ros.fit_resample(Xtr, ytr)
    y_true_all.append(yte)

    xgb = XGBClassifier(100, random_state=42, verbosity=0, eval_metric='mlogloss')
    xgb.fit(Xb, yb)
    preds['XGBoost'].append(xgb.predict(Xte))
    print('  XGBoost OK', flush=True)
    del xgb; gc.collect()

    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=2)
    rf.fit(Xb, yb)
    preds['RandomForest'].append(rf.predict(Xte))
    print('  RandomForest OK', flush=True)
    del rf; gc.collect()

    dl, sc = train_dl(Xb, yb)
    dl.eval()
    Xte_s = Xte.copy()
    Xte_s[:,n_genes:] = sc.transform(Xte[:,n_genes:])
    with torch.no_grad():
        preds['DL'].append(np.argmax(torch.softmax(dl(torch.FloatTensor(Xte_s)), dim=1).numpy(), axis=1))
    print('  DL OK', flush=True)
    del dl, Xb, yb, Xtr, Xte, Xte_s; gc.collect()

y_true = np.concatenate(y_true_all)

# Calcul des metriques
resultats = {}
for nom in preds:
    y_pred = np.concatenate(preds[nom])
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=range(n_classes), zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=range(n_classes))

    n_eviter = int(cm[IDX_EVITER].sum())
    n_crit   = int(cm[IDX_EVITER, IDX_STANDARD] + cm[IDX_EVITER, IDX_SURVEILLER])

    resultats[nom] = {
        'macro_f1':          round(float(f1_score(y_true, y_pred, average='macro', zero_division=0)), 4),
        'weighted_f1':       round(float(f1_score(y_true, y_pred, average='weighted', zero_division=0)), 4),
        'balanced_accuracy': round(float(balanced_accuracy_score(y_true, y_pred)), 4),
        'par_classe': {CLASSES[i]: {
            'precision': round(float(p[i]), 4),
            'recall':    round(float(r[i]), 4),
            'f1':        round(float(f[i]), 4),
            'support':   int(s[i])} for i in range(n_classes)},
        'confusion_matrix': cm.tolist(),
        'critical_errors':  n_crit,
        'n_eviter':         n_eviter,
        'critical_error_rate': round(n_crit / n_eviter, 4) if n_eviter else None,
    }
    print(f"\n{nom}: macro-F1={resultats[nom]['macro_f1']}  CER={resultats[nom]['critical_error_rate']}", flush=True)

with open(RESULTS_DIR+'/metriques_completes_v2.json','w') as f:
    json.dump({'classes': CLASSES, 'resultats': resultats}, f, indent=2)

# Rapport markdown
lignes = ['# Metriques completes — Dataset v2', '',
          f'Dataset : {len(df)} lignes, {n_genes} genes, {df["drug"].nunique()} medicaments',
          'Protocole : StratifiedKFold 5 folds, scaler intra-fold, RandomOverSampler sur train',
          '', '## Vue d ensemble', '',
          '| Modele | Macro-F1 | Weighted-F1 | Balanced Acc. | Critical Error Rate |',
          '|--------|----------|-------------|---------------|---------------------|']
for nom, r in resultats.items():
    lignes.append(f"| {nom} | {r['macro_f1']} | {r['weighted_f1']} | {r['balanced_accuracy']} | "
                  f"{r['critical_error_rate']} ({r['critical_errors']}/{r['n_eviter']}) |")

lignes += ['', '## Detail par classe', '']
for nom, r in resultats.items():
    lignes += [f'### {nom}', '',
               '| Classe | Precision | Recall | F1 | Support |',
               '|--------|-----------|--------|----|---------|']
    for cl, v in r['par_classe'].items():
        lignes.append(f"| {cl} | {v['precision']} | {v['recall']} | {v['f1']} | {v['support']} |")
    lignes.append('')

lignes += ['## Critical Error Rate', '',
           'Proportion de cas EVITER predits comme STANDARD ou SURVEILLER.',
           'Erreur cliniquement grave : contre-indication non signalee au prescripteur.', '']
for nom, r in resultats.items():
    lignes.append(f"- **{nom}** : {r['critical_errors']} / {r['n_eviter']} = {r['critical_error_rate']}")

with open(RESULTS_DIR+'/metriques_completes_v2.md','w') as f:
    f.write('\n'.join(lignes))

# Figure matrices de confusion
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, (nom, r) in zip(axes, resultats.items()):
    cm = np.array(r['confusion_matrix'])
    cmn = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    im = ax.imshow(cmn, cmap='Blues', vmin=0, vmax=1)
    ax.set_title(f"{nom}\nmacro-F1 = {r['macro_f1']}")
    ax.set_xticks(range(n_classes)); ax.set_yticks(range(n_classes))
    ax.set_xticklabels(CLASSES, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(CLASSES, fontsize=8)
    ax.set_xlabel('Predit'); ax.set_ylabel('Reel')
    for i in range(n_classes):
        for j in range(n_classes):
            ax.text(j, i, f'{cm[i,j]}', ha='center', va='center', fontsize=8,
                    color='white' if cmn[i,j] > 0.5 else 'black')
plt.tight_layout()
plt.savefig(RESULTS_DIR+'/confusion_matrices_v2.png', dpi=150, bbox_inches='tight')
print('\nFichiers generes : metriques_completes_v2.json / .md / confusion_matrices_v2.png', flush=True)
