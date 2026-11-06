#!/usr/bin/env python3
"""
arbres_coeur_v1.py (4 nov. 2026) : cœur XGBoost / forêt aléatoire pour la COMPARAISON ÉQUITABLE DL / XGBoost / RF sur le corpus v14.
Symétrique de dl_coeur_v4.py (qui reste INTACT). Protocole écrit avant tout résultat : voir Protocole_comparaison_equitable_DL_XGB_RF_v14_4nov2026.md.

Ce qui est IDENTIQUE au DL (dl_coeur_v4.py / evaluer_dl_imbrique_v5.py / recherche_hp_dl_v4.py) :
  - données, plis externes, ensemble final non lu : protocole_commun_v10 ;
  - découpage interne : MÊMES familles d'entraînement et de validation que le DL (découpage fait sur les PROFILS avec GroupShuffleSplit, puis reporté sur les lignes) ;
  - poids de classes : formule de dl_coeur_v4.poids (exposant w_exp, facteur ev_x sur EVITER), recalculée sur l'entraînement ;
  - critère d'arrêt/sélection : F1 macro de la validation interne (le DL arrête sur ce critère ; XGBoost aussi, par points de contrôle tous les 25 arbres) ;
  - calibration : mise à l'échelle de la température sur la validation interne (même fonction que evaluer_dl_imbrique_v5.py) ;
  - 5 graines par pli, mêmes formules de graine que le DL : GRAINE + 100*s + k.
Ce qui DIFFÈRE par nature (documenté) : les arbres reçoivent les 34 variables d'entrée + une colonne indicatrice par médicament (une ligne = un couple profil x médicament) ;
le DL reçoit les 34 variables et prédit les 189 médicaments d'un coup.
"""
import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.metrics import f1_score
from sklearn.model_selection import GroupShuffleSplit
import protocole_commun_v10 as pc

# ---------------------------------------------------------------- espaces de recherche (aléatoire, Bergstra & Bengio 2012 ; 40 configurations comme le DL)
ESPACE_XGB = dict(max_depth=[4, 6, 8, 10, 12], eta=[0.03, 0.1, 0.3], min_child_weight=[1, 3, 10], subsample=[0.6, 0.8, 1.0], colsample_bytree=[0.5, 0.8, 1.0],
                  reg_lambda=[0.0, 1.0, 10.0], w_exp=[0.5, 0.75, 1.0], ev_x=[1.0, 2.0, 4.0])
REF_XGB = dict(max_depth=6, eta=0.1, min_child_weight=1, subsample=1.0, colsample_bytree=1.0, reg_lambda=1.0, w_exp=1.0, ev_x=1.0)   # réglage de train_arbres_v10.py (poids ~ 1/fréquence)
ESPACE_RF = dict(max_features=['sqrt', 'log2', 0.1, 0.3, 0.5], min_samples_leaf=[1, 2, 5, 10], max_depth=[None, 16, 32], criterion=['gini', 'entropy'], max_samples=[None, 0.5, 0.8],
                 w_exp=[0.5, 0.75, 1.0], ev_x=[1.0, 2.0, 4.0])
REF_RF = dict(max_features='sqrt', min_samples_leaf=1, max_depth=None, criterion='gini', max_samples=None, w_exp=1.0, ev_x=1.0)   # réglage de train_arbres_v10.py
N_ARBRES_RF = 500          # fixé (Probst & Boulesteix 2018 : plus d'arbres n'aggrave pas la performance)
N_ARBRES_XGB_MAX = 2000    # plafond ; le nombre réel est choisi par le F1 macro de validation interne
PAS_CONTROLE = 25          # XGBoost : F1 macro de validation évalué tous les 25 arbres
PATIENCE_CONTROLES = 6     # 6 contrôles sans gain > 1e-4 = 150 arbres (le DL : patience 25 époques, gain > 1e-4)


def configs(modele, n=40, graine=0):
    espace, ref = (ESPACE_XGB, REF_XGB) if modele == 'xgb' else (ESPACE_RF, REF_RF)
    rng = np.random.RandomState(graine); L = [dict(ref)]
    while len(L) < n:
        c = {k: v[rng.randint(len(v))] for k, v in espace.items()}
        if c not in L: L.append(c)
    return L


# ---------------------------------------------------------------- données
def lignes_arbres(d):
    """X des arbres : 34 variables + une colonne indicatrice par médicament (représentation 'id' de train_arbres_v10.py)."""
    return np.hstack([d['G'], np.eye(len(d['meds']), dtype=np.float32)[d['drug_idx']]]).astype(np.float32)


def decoupe_interne(d, tr, test_size, graine):
    """Même découpage interne que le DL : sur les PROFILS (pid) de l'entraînement, groupés par famille ; reporté sur les lignes. Retourne (lignes_entrainement, lignes_validation)."""
    pid, fam = d['pid'], d['fam']; ptr = np.unique(pid[tr])
    ai, vi = next(GroupShuffleSplit(1, test_size=test_size, random_state=graine).split(ptr, groups=fam[ptr]))
    a_, v_ = ptr[ai], ptr[vi]
    return tr[np.isin(pid[tr], a_)], tr[np.isin(pid[tr], v_)]


def poids_lignes(ytr, K, ev, w_exp, ev_x):
    """Formule de dl_coeur_v4.poids appliquée aux étiquettes des lignes d'entraînement ; retourne le poids de chaque ligne."""
    cnt = np.bincount(ytr, minlength=K).astype(float)
    w = (cnt.sum() / (K * np.maximum(cnt, 1))) ** w_exp; w = w.copy(); w[ev] *= ev_x
    return w[ytr]


# ---------------------------------------------------------------- modèles
def entrainer_xgb(Xtr, ytr, wtr, Xva, yva, K, cfg, graine, threads):
    """XGBoost : multi:softprob ; nombre d'arbres = point de contrôle (tous les 25) au meilleur F1 macro de validation interne ; retourne (booster, n_arbres, meilleur_F1_val)."""
    import xgboost as xgb
    dtr = xgb.DMatrix(Xtr, label=ytr, weight=wtr); dva = xgb.DMatrix(Xva, label=yva)
    suivi = dict(best=-1.0, best_it=PAS_CONTROLE, wait=0)

    class ArretF1(xgb.callback.TrainingCallback):
        def after_iteration(self, model, epoch, evals_log):
            if (epoch + 1) % PAS_CONTROLE: return False
            P = model.predict(dva, iteration_range=(0, epoch + 1)); f1 = f1_score(yva, P.argmax(1), average='macro')
            if f1 > suivi['best'] + 1e-4: suivi.update(best=float(f1), best_it=epoch + 1, wait=0)
            else: suivi['wait'] += 1
            return suivi['wait'] >= PATIENCE_CONTROLES

    p = dict(objective='multi:softprob', num_class=K, eta=cfg['eta'], max_depth=cfg['max_depth'], min_child_weight=cfg['min_child_weight'], subsample=cfg['subsample'],
             colsample_bytree=cfg['colsample_bytree'], reg_lambda=cfg['reg_lambda'], tree_method='hist', nthread=threads, seed=graine, verbosity=0)
    b = xgb.train(p, dtr, num_boost_round=N_ARBRES_XGB_MAX, callbacks=[ArretF1()], verbose_eval=False)
    return b, suivi['best_it'], suivi['best']


def probas_xgb(b, n_arbres, X):
    import xgboost as xgb
    return b.predict(xgb.DMatrix(X), iteration_range=(0, n_arbres)).astype(np.float64)


def entrainer_rf(Xtr, ytr, wtr, cfg, graine, threads):
    from sklearn.ensemble import RandomForestClassifier
    return RandomForestClassifier(n_estimators=N_ARBRES_RF, max_features=cfg['max_features'], min_samples_leaf=cfg['min_samples_leaf'], max_depth=cfg['max_depth'],
                                  criterion=cfg['criterion'], max_samples=cfg['max_samples'], n_jobs=threads, random_state=graine).fit(Xtr, ytr, sample_weight=wtr)


# ---------------------------------------------------------------- calibration (même fonction que evaluer_dl_imbrique_v5.py)
def temperature(Pv, yv):
    lp = np.log(np.clip(Pv, 1e-12, 1))
    def nll(T):
        z = lp / T; z = z - z.max(-1, keepdims=True); q = np.exp(z); q /= q.sum(-1, keepdims=True)
        return -np.log(np.clip(q[np.arange(len(yv)), yv], 1e-12, 1)).mean()
    return float(minimize_scalar(nll, bounds=(0.05, 5.0), method='bounded').x)


def appliquer_temperature(P, T):
    z = np.log(np.clip(P, 1e-12, 1)) / T; z = z - z.max(-1, keepdims=True); q = np.exp(z); return q / q.sum(-1, keepdims=True)
