import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, label_binarize
from sklearn.metrics import confusion_matrix, roc_curve, auc
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import torch, torch.nn as nn
import joblib, pickle, warnings
warnings.filterwarnings("ignore")

OUTPUT = "/home/mouna/projet_memoire/model_v2/results"

df = pd.read_csv("/home/mouna/projet_memoire/model_v2/data/combined_dataset.csv")
feature_cols = [c for c in df.columns if c not in ["gene","diplotype","phenotype"]]
X = np.nan_to_num(df[feature_cols].values.astype(float), nan=1.0)
le = LabelEncoder()
y = le.fit_transform(df["phenotype"].values)
classes = le.classes_
smote = SMOTE(random_state=42, k_neighbors=3)
X_bal, y_bal = smote.fit_resample(X, y)

# Charger modeles finaux
rf  = joblib.load(OUTPUT + "/rf_final.pkl")
xgb = joblib.load(OUTPUT + "/xgb_final.pkl")

# ── MATRICE DE CONFUSION ──────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, (model, name) in zip(axes, [(rf,"Random Forest"),(xgb,"XGBoost")]):
    y_pred = model.predict(X)
    cm = confusion_matrix(y, y_pred)
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.set_title(name + " — Matrice de confusion", fontsize=13, pad=12)
    ax.set_xlabel("Phenotype predit", fontsize=11)
    ax.set_ylabel("Phenotype reel", fontsize=11)
    tick_marks = np.arange(len(classes))
    short = ["Intermediate","Normal","Poor","Ultrarapid"]
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(short, rotation=30, ha="right", fontsize=9)
    ax.set_yticklabels(short, fontsize=9)
    thresh = cm.max() / 2
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i,j]), ha="center", va="center",
                    color="white" if cm[i,j] > thresh else "black", fontsize=14, fontweight="bold")
    plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.savefig(OUTPUT + "/confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close()
print("confusion_matrix.png sauvegarde")

# ── COURBE ROC ────────────────────────────────────────
y_bin = label_binarize(y, classes=[0,1,2,3])
colors = ["#2E5F8A","#27ae60","#e67e22","#8e44ad"]
short_labels = ["Intermediate","Normal","Poor","Ultrarapid"]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, (model, name) in zip(axes, [(rf,"Random Forest"),(xgb,"XGBoost")]):
    y_prob = model.predict_proba(X)
    for i, (color, label) in enumerate(zip(colors, short_labels)):
        fpr, tpr, _ = roc_curve(y_bin[:,i], y_prob[:,i])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=color, lw=2,
                label=label + " (AUC = " + str(round(roc_auc,3)) + ")")
    ax.plot([0,1],[0,1],"k--", lw=1)
    ax.set_xlim([0,1])
    ax.set_ylim([0,1.02])
    ax.set_xlabel("Taux de faux positifs", fontsize=11)
    ax.set_ylabel("Taux de vrais positifs", fontsize=11)
    ax.set_title(name + " — Courbe ROC", fontsize=13)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT + "/roc_curves.png", dpi=150, bbox_inches="tight")
plt.close()
print("roc_curves.png sauvegarde")

# ── IMPORTANCE DES FEATURES ───────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))
importances = rf.feature_importances_
feat_imp = sorted(zip(feature_cols, importances), key=lambda x: x[1])
feats = [f[0] for f in feat_imp]
imps  = [f[1] for f in feat_imp]
colors_bar = ["#2E5F8A" if imp == max(imps) else "#7fb3d3" for imp in imps]
bars = ax.barh(feats, imps, color=colors_bar)
ax.set_xlabel("Importance (Gini)", fontsize=12)
ax.set_title("Importance des variants — Random Forest v2", fontsize=13)
for bar, imp in zip(bars, imps):
    ax.text(bar.get_width()+0.002, bar.get_y()+bar.get_height()/2,
            str(round(imp,4)), va="center", fontsize=8)
plt.tight_layout()
plt.savefig(OUTPUT + "/feature_importance.png", dpi=150, bbox_inches="tight")
plt.close()
print("feature_importance.png sauvegarde")

print("")
print("Tous les graphiques sauvegardes dans model_v2/results/")