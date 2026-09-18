"""
train_pgx_31genes_v2.py — Reconstruction du script d'entraînement PharmaGeno (31 gènes)

Reconstruit à partir des spécifications confirmées à plusieurs reprises dans le projet
(architecture, hyperparamètres, procédure K-Fold+SMOTE) — le script original n'a jamais
été sauvegardé sur disque (même situation que generate_report.py et le script de fusion
1KGP : exécuté en ligne dans une session Claude passée, jamais persisté).

À VÉRIFIER avant de faire confiance aux résultats : que ce script reconstruit donne bien
sur le DATASET ORIGINAL les mêmes F1 déjà rapportés (DL=0.834, XGB=0.881, RF=0.795).
Si oui → la reconstruction est fidèle, les résultats sur le dataset corrigé sont fiables.
Si non → il y a une différence avec le script réel qu'il faut identifier avant de conclure.
"""

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import pickle
import joblib
from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

# ── CHEMINS — à adapter si besoin ──────────────────────────────────────
DATA_DIR = '/home/mouna/projet_memoire/model_v2/data'
RESULTS_DIR = '/home/mouna/projet_memoire/model_v2/results'
DATASET_PATH = f'{DATA_DIR}/phenotype_drug_dataset_complet.csv'
DRUG_FP_PATH = f'{RESULTS_DIR}/drug_fp_ref.pkl'  # doit couvrir les 530 medicaments du dataset corrige

GENES_31 = ['ABCG2', 'ACE', 'ADRB2', 'CACNA1S', 'CFTR', 'CYP1A2', 'CYP2A6',
            'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP2D6', 'CYP3A4', 'CYP3A5',
            'CYP4F2', 'DPYD', 'EGFR', 'F5', 'G6PD', 'HLA-A', 'HLA-B',
            'IFNL3', 'MT-RNR1', 'MTHFR', 'NAT2', 'NUDT15', 'RYR1',
            'SLC19A1', 'SLCO1B1', 'TPMT', 'UGT1A1', 'VKORC1']


# ── ARCHITECTURE DL — identique a celle confirmee dans predict_v2.py ───
class GeneAttention(nn.Module):
    def __init__(self, n_genes):
        super().__init__()
        self.attn = nn.Linear(n_genes, n_genes)

    def forward(self, x):
        w = torch.softmax(self.attn(x), dim=-1)
        return x * w


class PharmaGenoDL(nn.Module):
    def __init__(self, drug_fp_dim):
        super().__init__()
        self.gene_attention = GeneAttention(31)
        self.gene_branch = nn.Sequential(
            nn.Linear(31, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 32), nn.BatchNorm1d(32), nn.ReLU()
        )
        self.drug_branch = nn.Sequential(
            nn.Linear(drug_fp_dim, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 64), nn.ReLU()
        )
        self.combined = nn.Sequential(
            nn.Linear(96, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 4)
        )

    def forward(self, gene_x, drug_x):
        g = self.gene_attention(gene_x)
        g = self.gene_branch(g)
        d = self.drug_branch(drug_x)
        return self.combined(torch.cat([g, d], dim=1))


def entrainer_dl(X_gene_train, X_drug_train, y_train, X_gene_test, X_drug_test, y_test,
                  n_classes=4, epochs=100, class_weights=None):
    """Un fold d'entrainement DL. lr=0.0005, weight_decay=0.005, StepLR(200, 0.5), WCE."""
    model = PharmaGenoDL(drug_fp_dim=X_drug_train.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0005, weight_decay=0.005)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=200, gamma=0.5)

    if class_weights is not None:
        criterion = nn.CrossEntropyLoss(weight=torch.tensor(class_weights, dtype=torch.float32))
    else:
        criterion = nn.CrossEntropyLoss()

    Xg_tr = torch.tensor(X_gene_train, dtype=torch.float32)
    Xd_tr = torch.tensor(X_drug_train, dtype=torch.float32)
    y_tr = torch.tensor(y_train, dtype=torch.long)

    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        out = model(Xg_tr, Xd_tr)
        loss = criterion(out, y_tr)
        loss.backward()
        optimizer.step()
        scheduler.step()

    model.eval()
    with torch.no_grad():
        Xg_te = torch.tensor(X_gene_test, dtype=torch.float32)
        Xd_te = torch.tensor(X_drug_test, dtype=torch.float32)
        out = model(Xg_te, Xd_te)
        proba = torch.softmax(out, dim=1).numpy()
        pred = np.argmax(proba, axis=1)

    return model, pred, proba


def charger_donnees(dataset_path, drug_fp_path):
    df = pd.read_csv(dataset_path)
    for g in GENES_31:
        if g not in df.columns:
            df[g] = 1.0
    df[GENES_31] = df[GENES_31].fillna(1.0)

    with open(drug_fp_path, 'rb') as f:
        drug_fp = pickle.load(f)  # dict {nom_medicament: vecteur_fingerprint}

    drogues_manquantes = set(df['drug'].unique()) - set(drug_fp.keys())
    if drogues_manquantes:
        print(f"ATTENTION : {len(drogues_manquantes)} medicaments du dataset n'ont pas de fingerprint dans drug_fp_ref.pkl")
        print("Exemples :", list(drogues_manquantes)[:10])
        print("Ces lignes seront exclues de l'entrainement. Corriger drug_fp_ref.pkl pour les inclure.")
        df = df[df['drug'].isin(drug_fp.keys())].reset_index(drop=True)

    X_gene = df[GENES_31].values
    X_drug = np.array([drug_fp[d] for d in df['drug']])

    le = LabelEncoder()
    y = le.fit_transform(df['action'])

    return X_gene, X_drug, y, le


def main():
    print(f"Chargement : {DATASET_PATH}")
    X_gene, X_drug, y, le = charger_donnees(DATASET_PATH, DRUG_FP_PATH)
    print(f"Dataset : {len(y)} lignes, {X_drug.shape[1]} dimensions fingerprint, classes = {list(le.classes_)}")

    scaler = StandardScaler()
    X_gene_scaled = scaler.fit_transform(X_gene)

    class_counts = np.bincount(y)
    class_weights = len(y) / (len(class_counts) * class_counts)

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    resultats = {'DL': [], 'XGBoost': [], 'RF': []}

    print()
    print("=" * 55)
    print("K-FOLD CROSS VALIDATION (5 folds) — SMOTE dans chaque fold")
    print("=" * 55)

    for fold, (tr_idx, te_idx) in enumerate(kf.split(X_gene_scaled, y)):
        Xg_tr, Xg_te = X_gene_scaled[tr_idx], X_gene_scaled[te_idx]
        Xd_tr, Xd_te = X_drug[tr_idx], X_drug[te_idx]
        y_tr, y_te = y[tr_idx], y[te_idx]

        X_tr_combined = np.hstack([Xg_tr, Xd_tr])
        sm = SMOTE(random_state=42, k_neighbors=3)
        X_tr_bal, y_tr_bal = sm.fit_resample(X_tr_combined, y_tr)
        Xg_tr_bal = X_tr_bal[:, :31]
        Xd_tr_bal = X_tr_bal[:, 31:]

        _, pred_dl, _ = entrainer_dl(Xg_tr_bal, Xd_tr_bal, y_tr_bal, Xg_te, Xd_te, y_te,
                                      class_weights=class_weights)
        f1_dl = f1_score(y_te, pred_dl, average='macro')
        resultats['DL'].append(f1_dl)

        xgb_model = XGBClassifier(n_estimators=100, random_state=42, verbosity=0, eval_metric='mlogloss')
        xgb_model.fit(X_tr_bal, y_tr_bal)
        f1_xgb = f1_score(y_te, xgb_model.predict(np.hstack([Xg_te, Xd_te])), average='macro')
        resultats['XGBoost'].append(f1_xgb)

        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_tr_bal, y_tr_bal)
        f1_rf = f1_score(y_te, rf_model.predict(np.hstack([Xg_te, Xd_te])), average='macro')
        resultats['RF'].append(f1_rf)

        print(f"Fold {fold+1} : DL={f1_dl:.4f}  XGB={f1_xgb:.4f}  RF={f1_rf:.4f}")

    print()
    print("=" * 55)
    print("RESULTATS FINAUX (moyenne +/- ecart-type)")
    print("=" * 55)
    for nom, scores in resultats.items():
        print(f"{nom:10s} : F1-macro = {np.mean(scores):.4f} +/- {np.std(scores):.4f}")

    print()
    print("A COMPARER avec les F1 deja rapportes :")
    print("  DL=0.834+/-0.018  XGBoost=0.881+/-0.003  RF=0.795+/-0.004")


if __name__ == '__main__':
    main()
