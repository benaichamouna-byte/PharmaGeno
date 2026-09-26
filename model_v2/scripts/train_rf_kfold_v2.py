import pandas as pd, numpy as np, pickle, warnings, gc, os, json
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from imblearn.over_sampling import RandomOverSampler
warnings.filterwarnings('ignore')

DATA_DIR     = '/home/mouna/projet_memoire/model_v2/data'
RESULTS_DIR  = '/home/mouna/projet_memoire/model_v2/results'
SCORES_PATH  = RESULTS_DIR + '/rf_kfold_v2_scores.json'

with open(RESULTS_DIR + '/le_pgx_v2.pkl', 'rb') as f:    le = pickle.load(f)
with open(RESULTS_DIR + '/genes_pgx_v2.pkl', 'rb') as f: GENES = pickle.load(f)
with open(DATA_DIR + '/drug_fingerprints.pkl', 'rb') as f: drug_fp = pickle.load(f)

df = pd.read_csv(DATA_DIR + '/phenotype_drug_dataset_complet_v2.csv')
df = df[df['drug'].isin(drug_fp)].copy()
df[GENES] = df[GENES].fillna(1.0)

X = np.hstack([df[GENES].values.astype(float),
               np.array([drug_fp[d] for d in df['drug']])])
y = le.transform(df['action'].values)
print(f'Dataset : {len(df)} lignes, {X.shape[1]} features', flush=True)
print(f'Classes : {list(le.classes_)}', flush=True)

scores = {}
if os.path.exists(SCORES_PATH):
    with open(SCORES_PATH) as f:
        scores = json.load(f)
    print(f'Folds deja calcules : {sorted(scores.keys())}', flush=True)

ros = RandomOverSampler(random_state=42)
kf  = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
folds = list(kf.split(X, y))

print('', flush=True)
print('=' * 60, flush=True)
print('RANDOM FOREST K-FOLD 5 FOLDS — Dataset v2 (200 arbres, n_jobs=2)', flush=True)
print('=' * 60, flush=True)

for fold_idx, (tri, tei) in enumerate(folds):
    key = str(fold_idx + 1)
    if key in scores:
        print(f'Fold {key}/5 — deja calcule : F1={scores[key]}', flush=True)
        continue

    print(f'Fold {key}/5 en cours...', flush=True)
    Xtr, Xte = X[tri], X[tei]
    ytr, yte = y[tri], y[tei]
    Xb, yb = ros.fit_resample(Xtr, ytr)

    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=2)
    rf.fit(Xb, yb)
    f1 = f1_score(yte, rf.predict(Xte), average='macro', zero_division=0)

    scores[key] = round(float(f1), 4)
    with open(SCORES_PATH, 'w') as f:
        json.dump(scores, f, indent=2)
    print(f'Fold {key}/5 termine — RF F1={round(f1, 3)} (sauvegarde)', flush=True)

    del rf, Xb, yb, Xtr, Xte
    gc.collect()

print('', flush=True)
print('=' * 60, flush=True)
print('RESULTATS RF K-FOLD — Dataset v2', flush=True)
print('=' * 60, flush=True)
vals = np.array([scores[str(i)] for i in range(1, 6) if str(i) in scores])
for i in range(1, 6):
    if str(i) in scores:
        print(f'Fold {i} : {scores[str(i)]}', flush=True)
print(f'RF F1-macro : {round(vals.mean(), 3)} +/- {round(vals.std(), 3)} ({len(vals)}/5 folds)', flush=True)
print('REFERENCE v1 : RF=0.940 +/- 0.001 (memes conditions, 200 arbres)', flush=True)
