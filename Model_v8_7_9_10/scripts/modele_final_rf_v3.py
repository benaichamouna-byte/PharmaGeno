#!/usr/bin/env python3
"""
VERSION rf_v3 (corpus v14, 3 nov. 2026) : copie de modele_final_xgb_v3.py (INTACT) où le classifieur XGBoost est remplacé par une forêt aléatoire (Breiman 2001) ; MÊME entrée (variables du profil + identifiant de médicament one-hot), MÊME découpage (entraînement / validation interne / ensemble final NON LU), réglages fixés à l'avance, non ajustés : 100 arbres, feuilles d'au moins 2 lignes (min_samples_leaf = 2, choisi pour limiter la taille du fichier du modèle ; trois essais lus sur la validation interne, qui n'est pas l'ensemble final : 300 arbres/feuille 1 = 298 Mo, F1 macro 0,9783, écarté pour sa taille ; 100 arbres/feuille 5 = 16 Mo, F1 macro 0,8328, écarté pour sa précision EVITER de 0,58 ; 100 arbres/feuille 2 = retenu), max_features = sqrt, poids de classes « balanced_subsample », graine 42.
Le modèle est un AVIS INFORMATIF affiché à côté du DL et de XGBoost : il ne change ni les alertes ni les catégories de l'application. Validation interne seulement (aucune validation croisée refaite).
modele_final_rf_v3.py : avis Random Forest de l'APPLICATION v8r sur le corpus v14 (189 médicaments).
Sorties (dossier --out) : modele_final_rf.joblib, modele_final_rf_meta.json, modele_final_rf_v3_validation_interne.json, modele_final_rf_v3_configuration.json
Usage : python3 -I modele_final_rf_v3.py --data ../data/corpus_v14/phenotype_drug_dataset_v14.csv --out ../modeles_v10rf
"""
import argparse, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
import protocole_commun_v10 as pc


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'out'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--fp', default=None)
    ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); nj = os.cpu_count() or 1
    d = pc.charger(a.data, a.fp, familles_smoke=0.25 if a.smoke else None)
    df, genes, y, classes, G, groups, meds = d['df'], d['genes'], d['y'], d['classes'], d['G'], d['groups'], d['meds']
    K = len(classes); ID = np.eye(len(meds), dtype=np.float32)[d['drug_idx']]
    final, folds = pc.decouper(groups, y); cv = np.sort(np.concatenate([te for _, te in folds]))
    assert not (set(groups[final]) & set(groups[cv])), 'fuite : famille de l\'ensemble final dans l\'entraînement'
    ia, iv = next(GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE).split(cv, groups=groups[cv])); trn, val = cv[ia], cv[iv]
    assert not (set(groups[trn]) & set(groups[val]))
    cnt = np.bincount(y[trn], minlength=K).astype(float); w_inv = len(trn) / (K * np.maximum(cnt, 1))
    print('Entraînement : %d lignes | validation interne : %d | ensemble final (NON LU) : %d lignes' % (len(trn), len(val), len(final)), flush=True)
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    X = np.hstack([G, ID]).astype(np.float32); t1 = time.time()
    m = RandomForestClassifier(n_estimators=20 if a.smoke else 100, min_samples_leaf=2, max_features='sqrt', class_weight='balanced_subsample', n_jobs=nj, random_state=pc.GRAINE)
    m.fit(X[trn], y[trn])
    Pxv = np.zeros((len(val), K), dtype=np.float32); Pxv[:, m.classes_.astype(int)] = m.predict_proba(X[val]); mx = pc.metriques(y[val], Pxv, classes)
    joblib.dump(m, os.path.join(a.out, 'modele_final_rf.joblib'), compress=3)
    json.dump(dict(genes=genes, classes=classes, medicaments=meds), open(os.path.join(a.out, 'modele_final_rf_meta.json'), 'w'), ensure_ascii=False)
    json.dump(dict(arbres=100, metriques_validation_interne=mx, duree_s=round(time.time() - t1)), open(os.path.join(a.out, 'modele_final_rf_v3_validation_interne.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(dict(donnees=os.path.basename(a.data), md5_donnees=md5(a.data), empreintes=None, n_lignes_entrainement=int(len(trn)),
                   n_lignes_validation_interne=int(len(val)), n_lignes_ensemble_final_non_lues=int(len(final)), genes=genes, classes=classes, n_medicaments=len(meds), poids='balanced_subsample',
                   graine=pc.GRAINE, protocole='protocole_commun_v10 : StratifiedGroupKFold groupé par famille, graine 42, ensemble final fixé (138 familles)'),
              open(os.path.join(a.out, 'modele_final_rf_v3_configuration.json'), 'w'), indent=1, ensure_ascii=False)
    print('Random Forest : validation interne', mx, '| %.0fs' % (time.time() - t1)); print('Fichiers écrits dans', a.out)


if __name__ == '__main__': main()
