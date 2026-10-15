#!/usr/bin/env python3
"""
train_arbres_v7.py : XGBoost et Random Forest avec EXACTEMENT le même protocole que le DL (protocole_commun.py) :
mêmes 12 gènes, 10 % des familles mises de côté (NON touchées ici), validation croisée en 5 plis groupée par famille,
mêmes poids de classes (pas de SMOTE), mêmes métriques.

Hyperparamètres FIXÉS À L'AVANCE, jamais réglés sur les plis de test (le DL non plus n'a pas été réglé sur eux) :
  XGBoost (Chen & Guestrin 2016, https://arxiv.org/abs/1603.02754) : multi:softprob, learning_rate 0.1, max_depth 6,
          jusqu'à 1000 arbres, arrêt anticipé (20 tours) sur la log-loss de la même validation interne que le DL
          (10 % des familles du pli d'entraînement). Remarque : le DL arrête sur le F1 macro de cette validation, XGBoost sur la log-loss.
  Random Forest (Breiman 2001, https://doi.org/10.1023/A:1010933404324) : 500 arbres, max_features='sqrt', arbres non élagués.
          Le nombre d'arbres n'est pas réglé : plus d'arbres n'aggrave pas la performance en moyenne
          (Probst & Boulesteix 2018, https://jmlr.org/papers/v18/17-269.html).
Deux représentations du médicament, comme pour le DL : fp (empreinte, 518 bits) et id (identifiant, une colonne par médicament).

Ce script N'ÉCRASE RIEN et ne touche JAMAIS à l'ensemble final : il n'écrit que dans le dossier --out.
Usage :
  python3 train_arbres_v7.py --data phenotype_drug_dataset_v3_croise.csv --fp drug_fingerprints_v2.pkl --out resultats_arbres_v7 --modele xgb --repr fp
  ... --smoke   # essai rapide (une partie des familles, 1 pli, peu d'arbres)
"""
import argparse, json, os, time
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import f1_score
import protocole_commun as pc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True); ap.add_argument('--fp', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--modele', choices=['xgb', 'rf'], required=True); ap.add_argument('--repr', choices=['fp', 'id'], default='fp')
    ap.add_argument('--smoke', action='store_true'); ap.add_argument('--threads', type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); nj = a.threads or (os.cpu_count() or 1)
    d = pc.charger(a.data, a.fp, familles_smoke=0.25 if a.smoke else None)
    df, genes, y, classes, G, groups = d['df'], d['genes'], d['y'], d['classes'], d['G'], d['groups']
    K = len(classes)
    FP = np.eye(len(d['meds']), dtype=np.float32) if a.repr == 'id' else d['FP']
    X = np.hstack([G, FP[d['drug_idx']]]).astype(np.float32)   # arbres : pas de normalisation nécessaire
    tag = 'arbres_v7_%s_%s' % (a.modele, a.repr)
    print('Modèle : %s | représentation : %s | variables : %d (%d gènes + %d colonnes médicament)' % (a.modele, a.repr, X.shape[1], len(genes), FP.shape[1]))
    print('Classes :', classes, np.bincount(y).tolist())
    final, folds = pc.decouper(groups, y)
    print('Ensemble final mis de côté : %d lignes, %d familles (NON utilisé ici)' % (len(final), len(set(groups[final]))))
    if a.smoke: folds = folds[:1]
    oof = np.zeros((len(y), K), dtype=np.float32); fold_of = np.full(len(y), -1); lignes = []; t0 = time.time()
    for k, (tr, te) in enumerate(folds):
        gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE)
        a_idx, v_idx = next(gss.split(tr, groups=groups[tr])); trn, val = tr[a_idx], tr[v_idx]
        cnt = np.bincount(y[trn], minlength=K).astype(float); w = len(trn) / (K * np.maximum(cnt, 1))
        sw = w[y[trn]]
        if a.modele == 'xgb':
            from xgboost import XGBClassifier
            mdl = XGBClassifier(objective='multi:softprob', num_class=K, n_estimators=30 if a.smoke else 1000, learning_rate=0.1, max_depth=6,
                                tree_method='hist', early_stopping_rounds=20, eval_metric='mlogloss', n_jobs=nj,
                                random_state=pc.GRAINE + k, verbosity=0)
            mdl.fit(X[trn], y[trn], sample_weight=sw, eval_set=[(X[val], y[val])], verbose=False)
            n_arbres = int(mdl.best_iteration) + 1
        else:
            from sklearn.ensemble import RandomForestClassifier
            mdl = RandomForestClassifier(n_estimators=40 if a.smoke else 500, max_features='sqrt', n_jobs=nj, random_state=pc.GRAINE + k)
            mdl.fit(X[trn], y[trn], sample_weight=sw); n_arbres = mdl.n_estimators
        P = mdl.predict_proba(X[te]).astype(np.float32); oof[te] = P; fold_of[te] = k
        f1v = f1_score(y[val], mdl.predict(X[val]), average='macro')
        ligne = dict(pli=k + 1, n_test=int(len(te)), arbres=n_arbres, f1_val_interne=round(float(f1v), 4), **pc.metriques(y[te], P, classes))
        lignes.append(ligne); print(ligne, '| %.0fs' % (time.time() - t0), flush=True)
    res = pd.DataFrame(lignes); res.to_csv(os.path.join(a.out, tag + '_resultats_par_pli.csv'), index=False)
    m = fold_of >= 0
    glob = dict(modele=a.modele, representation=a.repr, protocole='ensemble final 10%% des familles à part ; StratifiedGroupKFold(%d) groupes=family_id graine=%d' % (pc.N_PLIS, pc.GRAINE),
                n_lignes_cv=int(m.sum()), n_lignes_final_non_utilisees=int(len(final)), genes=genes, classes=classes,
                f1_macro_moy=float(res.f1_macro.mean()), f1_macro_std=float(res.f1_macro.std(ddof=0)),
                f1_hors_surveiller_moy=float(res.f1_hors_surveiller.mean()), CER_strict_moy=float(res.CER_strict.mean()),
                CER_strict_std=float(res.CER_strict.std(ddof=0)), ECE_moy=float(res.ECE.mean()),
                precision_EVITER_moy=float(res.precision_EVITER.mean()), f1_macro_oof=float(f1_score(y[m], oof[m].argmax(1), average='macro')))
    json.dump(glob, open(os.path.join(a.out, tag + '_resume.json'), 'w'), indent=1, ensure_ascii=False)
    np.savez_compressed(os.path.join(a.out, tag + '_oof.npz'), proba=oof[m], y=y[m], pli=fold_of[m], ligne=np.where(m)[0], drug=df.drug.values[m].astype(str))
    print('\nRÉSULTAT %s (%s) : F1 macro = %.4f +/- %.4f | CER strict = %.4f | ECE = %.4f' % (
        a.modele.upper(), a.repr, glob['f1_macro_moy'], glob['f1_macro_std'], glob['CER_strict_moy'], glob['ECE_moy']))
    print('Fichiers écrits dans', a.out)


if __name__ == '__main__':
    main()
