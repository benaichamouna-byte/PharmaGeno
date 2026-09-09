import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import torch
import torch.nn as nn
import joblib, pickle, warnings
warnings.filterwarnings("ignore")

# Chargement
df = pd.read_csv("/home/mouna/projet_memoire/model_v2/data/combined_dataset.csv")
feature_cols = [c for c in df.columns if c not in ["gene","diplotype","phenotype"]]
X = np.nan_to_num(df[feature_cols].values.astype(float), nan=1.0)
le = LabelEncoder()
y = le.fit_transform(df["phenotype"].values)
print("Dataset : " + str(len(df)) + " exemples, " + str(len(feature_cols)) + " features")
print("Classes : " + str(list(le.classes_)))

# Architecture DL
class PharmDL(nn.Module):
    def __init__(self, n_in):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_in, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 32),   nn.BatchNorm1d(32), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(32, 4)
        )
    def forward(self, x): return self.net(x)

def train_dl(X_tr, y_tr, epochs=150):
    model = PharmDL(X_tr.shape[1])
    opt   = torch.optim.Adam(model.parameters(), lr=0.001)
    crit  = nn.CrossEntropyLoss()
    xt = torch.FloatTensor(X_tr)
    yt = torch.LongTensor(y_tr)
    for e in range(epochs):
        model.train()
        opt.zero_grad()
        loss = crit(model(xt), yt)
        loss.backward()
        opt.step()
    return model

def predict_dl(model, X_te):
    model.eval()
    with torch.no_grad():
        out = model(torch.FloatTensor(X_te))
        return torch.argmax(out, dim=1).numpy()

# K-Fold CORRECT — SMOTE applique DANS chaque fold
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
smote = SMOTE(random_state=42, k_neighbors=3)

results = {"RF": [], "XGBoost": [], "DL": []}

print("")
print("=" * 55)
print("K-FOLD CROSS VALIDATION (5 folds) — SMOTE dans chaque fold")
print("=" * 55)

for fold, (tr_idx, te_idx) in enumerate(kf.split(X, y)):
    X_tr, X_te = X[tr_idx], X[te_idx]
    y_tr, y_te = y[tr_idx], y[te_idx]
    # SMOTE seulement sur train
    X_tr_bal, y_tr_bal = smote.fit_resample(X_tr, y_tr)
    # RF
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_tr_bal, y_tr_bal)
    f1_rf = f1_score(y_te, rf.predict(X_te), average="macro")
    results["RF"].append(f1_rf)
    # XGBoost
    xgb = XGBClassifier(n_estimators=100, random_state=42, verbosity=0, eval_metric="mlogloss")
    xgb.fit(X_tr_bal, y_tr_bal)
    f1_xgb = f1_score(y_te, xgb.predict(X_te), average="macro")
    results["XGBoost"].append(f1_xgb)
    # DL
    dl = train_dl(X_tr_bal, y_tr_bal)
    f1_dl = f1_score(y_te, predict_dl(dl, X_te), average="macro")
    results["DL"].append(f1_dl)
    print("Fold " + str(fold+1) + " — RF: " + str(round(f1_rf,3)) + "  XGB: " + str(round(f1_xgb,3)) + "  DL: " + str(round(f1_dl,3)))

print("")
print("=" * 55)
print("RESULTATS FINAUX")
print("=" * 55)
for name, scores in results.items():
    arr = np.array(scores)
    print(name + " — F1 moyen: " + str(round(arr.mean(),3)) + " +/- " + str(round(arr.std(),3)))

# Entrainement final sur tout le dataset
X_all, y_all = smote.fit_resample(X, y)
rf_final = RandomForestClassifier(n_estimators=100, random_state=42)
rf_final.fit(X_all, y_all)
xgb_final = XGBClassifier(n_estimators=100, random_state=42, verbosity=0, eval_metric="mlogloss")
xgb_final.fit(X_all, y_all)
dl_final = train_dl(X_all, y_all, epochs=200)

# Rapport classification RF sur donnees originales (pas SMOTE)
print("")
print("=" * 55)
print("RAPPORT RF — donnees originales")
print("=" * 55)
print(classification_report(y, rf_final.predict(X), target_names=le.classes_))

# Importance des features
print("IMPORTANCE DES VARIANTS")
feat_imp = sorted(zip(feature_cols, rf_final.feature_importances_), key=lambda x: -x[1])
for feat, imp in feat_imp:
    bar = "#" * int(imp*50)
    print("  " + feat + " : " + str(round(imp,4)) + " " + bar)

# Sauvegarde
joblib.dump(rf_final,  "/home/mouna/projet_memoire/model_v2/results/rf_final.pkl")
joblib.dump(xgb_final, "/home/mouna/projet_memoire/model_v2/results/xgb_final.pkl")
torch.save(dl_final.state_dict(), "/home/mouna/projet_memoire/model_v2/results/dl_final.pth")
with open("/home/mouna/projet_memoire/model_v2/results/label_encoder.pkl","wb") as f: pickle.dump(le, f)
with open("/home/mouna/projet_memoire/model_v2/results/feature_cols.pkl","wb") as f: pickle.dump(feature_cols, f)
with open("/home/mouna/projet_memoire/model_v2/results/dl_input_size.pkl","wb") as f: pickle.dump(X.shape[1], f)
print("")
print("Modeles sauvegardes dans model_v2/results/")