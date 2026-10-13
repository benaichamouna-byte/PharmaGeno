#!/usr/bin/env python3
"""
train_dl_v6.py : entraînement et validation croisée du modèle DL (PharmaGenoDL) sur le corpus v3.

Ce script N'ÉCRASE RIEN : il écrit uniquement dans le dossier de sortie donné.

Protocole (commun aux trois modèles : DL, XGBoost, RF ; ne pas le modifier d'un modèle à l'autre)
  - Données   : phenotype_drug_dataset_v3_croise.csv (étiquettes issues des guidelines CPIC/DPWG, règles v2)
  - Entrées   : profil génétique (gènes qui varient réellement dans les données, hors RYR1 et CACNA1S)
                + empreinte moléculaire du médicament (518 bits)
  - Découpage : StratifiedGroupKFold, 5 plis, graine 42. Groupe = family_id (une famille entière est soit
                en entraînement, soit en test ; comme sample_id est inclus dans la famille, un même patient
                n'apparaît jamais des deux côtés).
  - Déséquilibre : perte pondérée par classe (poids calculés sur l'entraînement du pli). PAS de SMOTE :
                interpoler des empreintes binaires crée des molécules qui n'existent pas.
  - Normalisation des gènes : StandardScaler ajusté sur l'entraînement du pli uniquement.
  - Arrêt anticipé : sur 10 % des familles de l'entraînement (jamais sur le test).
  - Métriques : F1 macro, exactitude, rappel par classe, CER strict = 1 - rappel(EVITER), log-loss, ECE.

Usage :
  python3 train_dl_v6.py --data phenotype_drug_dataset_v3_croise.csv --fp drug_fingerprints_v2.pkl --out resultats_dl_v6
  python3 train_dl_v6.py ... --smoke        # essai rapide (1 pli, 2 époques) pour vérifier que tout tourne
"""
import argparse, json, os, pickle, time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import StratifiedGroupKFold, GroupShuffleSplit
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import f1_score, accuracy_score, recall_score, log_loss

GENES_31 = ['ABCG2', 'ACE', 'ADRB2', 'CACNA1S', 'CFTR', 'CYP1A2', 'CYP2A6', 'CYP2B6', 'CYP2C19', 'CYP2C9',
            'CYP2D6', 'CYP3A4', 'CYP3A5', 'CYP4F2', 'DPYD', 'EGFR', 'F5', 'G6PD', 'HLA-A', 'HLA-B', 'IFNL3',
            'MT-RNR1', 'MTHFR', 'NAT2', 'NUDT15', 'RYR1', 'SLC19A1', 'SLCO1B1', 'TPMT', 'UGT1A1', 'VKORC1']
GENES_EXCLUS = ['RYR1', 'CACNA1S']   # artefact de profil : permettent de deviner l'origine de la ligne


class GeneAttention(nn.Module):
    def __init__(self, n):
        super().__init__(); self.attn = nn.Linear(n, n)
    def poids(self, x):
        return torch.softmax(self.attn(x), dim=-1)
    def forward(self, x):
        return x * self.poids(x)


class PharmaGenoDL(nn.Module):
    """Même architecture que le modèle décrit dans le mémoire (branche gènes + attention, branche médicament)."""
    def __init__(self, n_genes, fp_dim, n_classes=4):
        super().__init__()
        self.gene_attention = GeneAttention(n_genes)
        self.gene_branch = nn.Sequential(
            nn.Linear(n_genes, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 32), nn.BatchNorm1d(32), nn.ReLU())
        self.drug_branch = nn.Sequential(
            nn.Linear(fp_dim, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 64), nn.ReLU())
        self.combined = nn.Sequential(
            nn.Linear(96, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, n_classes))
    def forward(self, g, d):
        return self.combined(torch.cat([self.gene_branch(self.gene_attention(g)), self.drug_branch(d)], 1))


def ece(proba, y, bins=15):
    conf = proba.max(1); pred = proba.argmax(1); ok = (pred == y).astype(float)
    edges = np.linspace(0, 1, bins + 1); tot = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            tot += m.mean() * abs(ok[m].mean() - conf[m].mean())
    return float(tot)


def predire(model, G, D, bs=4096):
    model.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(G), bs):
            out.append(torch.softmax(model(torch.from_numpy(G[i:i + bs]), torch.from_numpy(D[i:i + bs])), 1).numpy())
    return np.concatenate(out)


def entrainer(Gtr, Dtr, ytr, Gva, Dva, yva, n_classes, epochs, seed, poids):
    torch.manual_seed(seed)
    model = PharmaGenoDL(Gtr.shape[1], Dtr.shape[1], n_classes)
    opt = torch.optim.Adam(model.parameters(), lr=0.0005, weight_decay=0.005)
    crit = nn.CrossEntropyLoss(weight=torch.tensor(poids, dtype=torch.float32))
    Gt, Dt, yt = torch.from_numpy(Gtr), torch.from_numpy(Dtr), torch.from_numpy(ytr)
    rng = np.random.RandomState(seed); best, best_state, wait, hist = -1, None, 0, []
    for ep in range(epochs):
        model.train(); perm = rng.permutation(len(Gt)); tot = 0.0; nb = 0
        for i in range(0, len(perm) - 1, 512):
            idx = torch.from_numpy(perm[i:i + 512])
            if len(idx) < 2: continue
            opt.zero_grad(); loss = crit(model(Gt[idx], Dt[idx]), yt[idx]); loss.backward(); opt.step()
            tot += loss.item(); nb += 1
        f1v = f1_score(yva, predire(model, Gva, Dva).argmax(1), average='macro')
        hist.append((ep + 1, round(tot / max(nb, 1), 4), round(f1v, 4)))
        if f1v > best + 1e-4:
            best, wait = f1v, 0; best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= 8: break
    model.load_state_dict(best_state)
    return model, hist, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True); ap.add_argument('--fp', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--folds', type=int, default=5); ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--epochs', type=int, default=60); ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); torch.set_num_threads(max(1, os.cpu_count() or 1))
    df = pd.read_csv(a.data)
    with open(a.fp, 'rb') as f: fp = pickle.load(f)
    manq = sorted(set(df.drug) - set(fp))
    if manq: print('Médicaments sans empreinte, lignes exclues :', manq); df = df[df.drug.isin(fp)].reset_index(drop=True)
    genes = [g for g in GENES_31 if g not in GENES_EXCLUS and df[g].nunique() > 1]
    print('Gènes utilisés (%d) :' % len(genes), genes)
    le = LabelEncoder(); y = le.fit_transform(df.action); classes = list(le.classes_); K = len(classes)
    print('Classes :', classes, np.bincount(y).tolist())
    G = df[genes].values.astype(np.float32)
    meds = sorted(df.drug.unique()); idx = {m: i for i, m in enumerate(meds)}
    FP = np.stack([np.asarray(fp[m], dtype=np.float32) for m in meds]); D = FP[df.drug.map(idx).values]
    groups = df.family_id.values
    if a.smoke:
        keep = np.random.RandomState(0).rand(len(df)) < 0.15
        G, D, y, groups = G[keep], D[keep], y[keep], groups[keep]; df = df[keep].reset_index(drop=True)
    skf = StratifiedGroupKFold(n_splits=a.folds, shuffle=True, random_state=a.seed)
    oof = np.zeros((len(y), K), dtype=np.float32); fold_of = np.full(len(y), -1); lignes = []; attn = []
    t0 = time.time()
    for k, (tr, te) in enumerate(skf.split(G, y, groups)):
        assert not (set(groups[tr]) & set(groups[te])), 'fuite de famille entre entraînement et test'
        gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=a.seed)
        a_idx, v_idx = next(gss.split(tr, groups=groups[tr])); trn, val = tr[a_idx], tr[v_idx]
        sc = StandardScaler().fit(G[trn]); Gs = lambda ix: sc.transform(G[ix]).astype(np.float32)
        cnt = np.bincount(y[trn], minlength=K).astype(float); w = len(trn) / (K * np.maximum(cnt, 1))
        model, hist, bestval = entrainer(Gs(trn), D[trn], y[trn], Gs(val), D[val], y[val], K,
                                         2 if a.smoke else a.epochs, a.seed + k, w)
        P = predire(model, Gs(te), D[te]); oof[te] = P; fold_of[te] = k; pred = P.argmax(1)
        rec = recall_score(y[te], pred, average=None, labels=range(K), zero_division=0)
        ev = classes.index('EVITER')
        with torch.no_grad():
            attn.append(model.gene_attention.poids(torch.from_numpy(Gs(te))).mean(0).numpy())
        ligne = dict(pli=k + 1, n_test=len(te), epoques=len(hist), f1_val_interne=round(bestval, 4),
                     f1_macro=round(f1_score(y[te], pred, average='macro'), 4), exactitude=round(accuracy_score(y[te], pred), 4),
                     CER_strict=round(1 - rec[ev], 4), logloss=round(log_loss(y[te], P, labels=range(K)), 4), ECE=round(ece(P, y[te]), 4))
        for c, r in zip(classes, rec): ligne['rappel_' + c] = round(float(r), 4)
        lignes.append(ligne); print(ligne, '| %.0fs' % (time.time() - t0), flush=True)
    res = pd.DataFrame(lignes); res.to_csv(os.path.join(a.out, 'dl_v6_resultats_par_pli.csv'), index=False)
    m = fold_of >= 0; pred = oof[m].argmax(1)
    glob = dict(modele='DL', protocole='StratifiedGroupKFold(%d) groupes=family_id graine=%d' % (a.folds, a.seed),
                n_lignes=int(m.sum()), genes=genes, classes=classes,
                f1_macro_moy=float(res.f1_macro.mean()), f1_macro_std=float(res.f1_macro.std(ddof=0)),
                CER_strict_moy=float(res.CER_strict.mean()), ECE_moy=float(res.ECE.mean()),
                f1_macro_oof=float(f1_score(y[m], pred, average='macro')))
    if 'confiance' in df.columns:
        h = (df.confiance.values == 'haute') & m
        glob['f1_macro_oof_confiance_haute'] = float(f1_score(y[h], oof[h].argmax(1), average='macro'))
    glob['attention_moyenne_par_gene'] = dict(zip(genes, np.mean(attn, 0).round(4).tolist()))
    json.dump(glob, open(os.path.join(a.out, 'dl_v6_resume.json'), 'w'), indent=1, ensure_ascii=False)
    np.savez_compressed(os.path.join(a.out, 'dl_v6_oof.npz'), proba=oof, y=y, pli=fold_of, drug=df.drug.values.astype(str))
    print('\nRÉSULTAT DL : F1 macro = %.4f +/- %.4f | CER strict = %.4f | ECE = %.4f' % (
        glob['f1_macro_moy'], glob['f1_macro_std'], glob['CER_strict_moy'], glob['ECE_moy']))
    print('Fichiers écrits dans', a.out)


if __name__ == '__main__':
    main()
