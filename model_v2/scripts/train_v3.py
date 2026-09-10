import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, f1_score
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import torch
import torch.nn as nn
import joblib, pickle, warnings
warnings.filterwarnings("ignore")

DATA_DIR    = "/home/mouna/projet_memoire/model_v2/data"
RESULTS_DIR = "/home/mouna/projet_memoire/model_v2/results"

# Charger le dataset
df = pd.read_csv(DATA_DIR + "/profile_drug_dataset.csv")
print("Dataset : " + str(len(df)) + " lignes")

# Features = tous les variants rsID
feature_cols = [c for c in df.columns if c.startswith("rs")]
X = df[feature_cols].values.astype(float)
X = np.nan_to_num(X, nan=0.0)

# Label = action
le = LabelEncoder()
y  = le.fit_transform(df["action"].values)
print("Classes : " + str(list(le.classes_)))
print("Features : " + str(len(feature_cols)) + " variants")

# SMOTE pour équilibrer
smote = SMOTE(random_state=42, k_neighbors=3)

# Architecture DL
class PharmDL(nn.Module):
    def __init__(self, n_in):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_in, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, 64),  nn.BatchNorm1d(64),  nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(64, 3)
        )
    def forward(self, x): return self.net(x)

def train_dl(X_tr, y_tr, epochs=100):
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

# K-Fold
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results = {"RF": [], "XGBoost": [], "DL": []}

print("")
print("=" * 55)
print("K-FOLD CROSS VALIDATION (5 folds)")
print("=" * 55)

for fold, (tr_idx, te_idx) in enumerate(kf.split(X, y)):
    X_tr, X_te = X[tr_idx], X[te_idx]
    y_tr, y_te = y[tr_idx], y[te_idx]
    X_tr_bal, y_tr_bal = smote.fit_resample(X_tr, y_tr)

    rf  = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_tr_bal, y_tr_bal)
    f1_rf = f1_score(y_te, rf.predict(X_te), average="macro")
    results["RF"].append(f1_rf)

    xgb = XGBClassifier(n_estimators=100, random_state=42, verbosity=0, eval_metric="mlogloss")
    xgb.fit(X_tr_bal, y_tr_bal)
    f1_xgb = f1_score(y_te, xgb.predict(X_te), average="macro")
    results["XGBoost"].append(f1_xgb)

    dl  = train_dl(X_tr_bal, y_tr_bal)
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

# Entraînement final
print("")
print("Entraînement final sur tout le dataset...")
X_all, y_all = smote.fit_resample(X, y)

rf_final  = RandomForestClassifier(n_estimators=200, random_state=42)
rf_final.fit(X_all, y_all)

xgb_final = XGBClassifier(n_estimators=200, random_state=42, verbosity=0, eval_metric="mlogloss")
xgb_final.fit(X_all, y_all)

dl_final  = train_dl(X_all, y_all, epochs=150)

print("")
print("Rapport RF :")
print(classification_report(y, rf_final.predict(X), target_names=le.classes_))

# Sauvegarder
joblib.dump(rf_final,  RESULTS_DIR + "/rf_v3_final.pkl")
joblib.dump(xgb_final, RESULTS_DIR + "/xgb_v3_final.pkl")
torch.save(dl_final.state_dict(), RESULTS_DIR + "/dl_v3_final.pth")
with open(RESULTS_DIR + "/label_encoder_v3.pkl","wb") as f: pickle.dump(le, f)
with open(RESULTS_DIR + "/feature_cols_v3.pkl","wb") as f: pickle.dump(feature_cols, f)

print("Modèles sauvegardés dans model_v2/results/")
