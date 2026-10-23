#!/usr/bin/env python3
"""
protocole_commun_v9.py (version pour le corpus v8 ; protocole_commun_v8.py reste INTACT) : protocole d'évaluation UNIQUE, partagé par les trois modèles (DL, XGBoost, Random Forest).
Aucun modèle ne définit son propre découpage ni ses propres métriques : tout passe par ce fichier.
Ne pas le modifier d'un modèle à l'autre.

DIFFÉRENCE UNIQUE avec protocole_commun_v8.py : l'ENSEMBLE FINAL n'est plus tiré au hasard à chaque corpus ; il est FIXÉ aux 138 familles de data/profils_ensemble_final_v1.txt
(définies avec le corpus v7 et jamais lues pour entraîner, régler ou choisir). Raison : le corpus v8 ajoute 16 médicaments ; un nouveau tirage changerait le jeu final fermé.
La validation croisée en 5 plis (StratifiedGroupKFold, graine 42, groupée par famille) porte sur le reste, comme avant.

Contenu
  charger()   : lit le corpus v3 croisé et les empreintes moléculaires (mêmes 12 gènes pour tous les modèles)
  decouper()  : 1) met de côté ~10 % des familles = ENSEMBLE FINAL (jamais utilisé pour entraîner, régler ou choisir)
                2) sur les ~90 % restants : validation croisée en 5 plis, groupée par famille
  metriques() : F1 macro, F1 hors SURVEILLER, exactitude, CER strict, précision EVITER, log-loss, ECE, rappels

Découpage : StratifiedGroupKFold, graine 42, groupe = family_id (un patient n'apparaît jamais des deux côtés).
Déséquilibre : pas de SMOTE (interpoler des empreintes binaires crée des molécules qui n'existent pas).
"""
import os, pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score, log_loss

GENES_31 = ['ABCG2', 'ACE', 'ADRB2', 'CACNA1S', 'CFTR', 'CYP1A2', 'CYP2A6', 'CYP2B6', 'CYP2C19', 'CYP2C9',
            'CYP2D6', 'CYP3A4', 'CYP3A5', 'CYP4F2', 'DPYD', 'EGFR', 'F5', 'G6PD', 'HLA-A', 'HLA-B', 'IFNL3',
            'MT-RNR1', 'MTHFR', 'NAT2', 'NUDT15', 'RYR1', 'SLC19A1', 'SLCO1B1', 'TPMT', 'UGT1A1', 'VKORC1']
GENES_HLA = ['HLA-B*15:02', 'HLA-B*57:01', 'HLA-B*58:01', 'HLA-A*31:01']   # allèles HLA utilisés par les règles v4 (dbMHC) ; 1 = porteur certain, 0.5 = possible, 0 = absent
GENES_EXCLUS = ['RYR1', 'CACNA1S']   # v4 : RYR1 n'a qu'un profil non constant et CACNA1S est constant -> aucune information
FICHIER_FINAL = os.environ.get('PHARMAGENO_FINAL', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'profils_ensemble_final_v1.txt'))
N_FAMILLES_FINAL = 138
GRAINE = 42
N_PLIS = 5
FRACTION_FINALE = 10                 # 1 groupe sur 10 = ~10 % des familles mises de côté


def charger(data, fp_path, familles_smoke=None):
    """Retourne un dict : df, genes, y, classes, G (profils), meds, FP (empreintes par médicament), drug_idx."""
    df = pd.read_csv(data)
    with open(fp_path, 'rb') as f:
        fp = pickle.load(f)
    manq = sorted(set(df.drug) - set(fp))
    if manq:
        print('Médicaments sans empreinte, lignes exclues :', manq)
        df = df[df.drug.isin(fp)].reset_index(drop=True)
    if familles_smoke:   # essai rapide : on garde une fraction des FAMILLES (jamais des lignes isolées)
        rng = np.random.RandomState(0)
        fams = df.family_id.unique()
        garde = set(rng.choice(fams, size=max(60, int(len(fams) * familles_smoke)), replace=False))
        df = df[df.family_id.isin(garde)].reset_index(drop=True)
    genes = [g for g in GENES_31 + GENES_HLA if g not in GENES_EXCLUS and df[g].nunique() > 1]
    # valeurs manquantes (gène non déterminé) : valeur 0 + colonne indicatrice <gène>_manquant (jamais traité comme « normal »)
    for g in [g for g in genes if df[g].isna().any()]:
        df[g + '_manquant'] = df[g].isna().astype(np.float32)
        df[g] = df[g].fillna(0.0)
        genes.append(g + '_manquant')
    le = LabelEncoder()
    y = le.fit_transform(df.action)
    meds = sorted(df.drug.unique())
    idx = {m: i for i, m in enumerate(meds)}
    FP = np.stack([np.asarray(fp[m], dtype=np.float32) for m in meds])
    return dict(df=df, genes=genes, y=y, classes=list(le.classes_),
                G=df[genes].values.astype(np.float32), meds=meds, FP=FP,
                drug_idx=df.drug.map(idx).values, groups=df.family_id.values)


def decouper(groups, y, graine=GRAINE, n_plis=N_PLIS):
    """Retourne (final, folds) : final = indices de l'ensemble final FIXE (138 familles du fichier) ; folds = liste de (train, test) sur le reste."""
    pos = np.arange(len(y))
    ids = {l.strip() for l in open(FICHIER_FINAL) if l.strip() and not l.startswith('#')}
    fams_final = {'FAM_' + i for i in ids}
    assert len(ids) == N_FAMILLES_FINAL, 'le fichier de l\'ensemble final ne contient pas %d profils' % N_FAMILLES_FINAL
    est_final = np.array([g in fams_final for g in groups])
    if len(set(groups)) >= 1379:   # données complètes (pas l'essai rapide --smoke, qui ne garde qu'une fraction des familles) : les 138 familles doivent toutes être présentes
        assert set(groups[est_final]) == fams_final, 'des familles de l\'ensemble final manquent dans les données'
    assert est_final.any(), 'aucune famille de l\'ensemble final dans les données'
    final = pos[est_final]; reste = pos[~est_final]
    skf = StratifiedGroupKFold(n_splits=n_plis, shuffle=True, random_state=graine)
    folds = [(reste[a], reste[b]) for a, b in skf.split(reste, y[reste], groups[reste])]
    # contrôles de non-fuite
    gf = set(groups[final])
    assert not (gf & set(groups[reste])), 'fuite : une famille de l\'ensemble final est dans la validation croisée'
    tous_te = np.concatenate([te for _, te in folds])
    assert len(set(tous_te)) == len(tous_te) == len(reste), 'les plis de test ne partitionnent pas le reste'
    for tr, te in folds:
        assert not (set(groups[tr]) & set(groups[te])), 'fuite de famille entre entraînement et test'
    return final, folds


def ecrire_decoupage(path, df, final, folds):
    """Écrit le rôle de chaque ligne (traçabilité) : final / pli1..pli5."""
    role = np.full(len(df), 'final', dtype=object)
    for k, (_, te) in enumerate(folds):
        role[te] = 'pli%d' % (k + 1)
    pd.DataFrame(dict(ligne=np.arange(len(df)), sample_id=df.sample_id.values, family_id=df.family_id.values,
                      drug=df.drug.values, role=role)).to_csv(path, index=False)


def ece(proba, y, bins=15):
    conf = proba.max(1); pred = proba.argmax(1); ok = (pred == y).astype(float)
    edges = np.linspace(0, 1, bins + 1); tot = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            tot += m.mean() * abs(ok[m].mean() - conf[m].mean())
    return float(tot)


def metriques(y, P, classes):
    """P = probabilités (n, K). Toutes les valeurs sont des float Python (pas de numpy dans les fichiers)."""
    K = len(classes); pred = P.argmax(1); ev = classes.index('EVITER'); sv = classes.index('SURVEILLER')
    rec = recall_score(y, pred, average=None, labels=range(K), zero_division=0)
    hors = [i for i in range(K) if i != sv]
    m = dict(f1_macro=f1_score(y, pred, average='macro'),
             f1_hors_surveiller=f1_score(y, pred, average='macro', labels=hors),
             exactitude=accuracy_score(y, pred), CER_strict=1 - rec[ev],
             precision_EVITER=precision_score(y, pred, labels=[ev], average=None, zero_division=0)[0],
             logloss=log_loss(y, P, labels=range(K)), ECE=ece(P, y))
    for c, r in zip(classes, rec):
        m['rappel_' + c] = r
    return {k: round(float(v), 4) for k, v in m.items()}
