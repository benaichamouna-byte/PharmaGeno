#!/usr/bin/env python3
"""
modele_final_xgb_v2.py : second avis XGBoost de l'APPLICATION v8m sur le corpus v8 (133 médicaments). Partie XGBoost de modele_final_v8.py, réglages IDENTIQUES
(identifiant de médicament one-hot, poids de classes inverses, arrêt anticipé sur la log-loss, graine 42), protocole_commun_v9 (ensemble final FIXÉ aux 138 familles, NON LU).
Sorties (dossier --out) : modele_final_v8_xgb_id.json, modele_final_v8_xgb_id_meta.json (noms attendus par moteur_v8f.py), modele_final_xgb_v2_validation_interne.json, modele_final_xgb_v2_configuration.json
Usage : python3 modele_final_xgb_v2.py --data ../data/corpus_v8/phenotype_drug_dataset_v8.csv --fp <drug_fingerprints_v2.pkl> --out ../modeles_v9x
"""
import argparse, hashlib, json, os, time
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
import protocole_commun_v9 as pc


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'fp', 'out'): ap.add_argument('--' + k, required=True)
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
    from xgboost import XGBClassifier
    X = np.hstack([G, ID]).astype(np.float32); t1 = time.time()
    m = XGBClassifier(objective='multi:softprob', num_class=K, n_estimators=30 if a.smoke else 1000, learning_rate=0.1, max_depth=6, tree_method='hist',
                      early_stopping_rounds=20, eval_metric='mlogloss', n_jobs=nj, random_state=pc.GRAINE, verbosity=0)
    m.fit(X[trn], y[trn], sample_weight=w_inv[y[trn]], eval_set=[(X[val], y[val])], verbose=False)
    Pxv = np.zeros((len(val), K), dtype=np.float32); Pxv[:, m.classes_.astype(int)] = m.predict_proba(X[val]); mx = pc.metriques(y[val], Pxv, classes)
    m.save_model(os.path.join(a.out, 'modele_final_v8_xgb_id.json'))
    json.dump(dict(genes=genes, classes=classes, medicaments=meds), open(os.path.join(a.out, 'modele_final_v8_xgb_id_meta.json'), 'w'), ensure_ascii=False)
    json.dump(dict(arbres=int(m.best_iteration) + 1, metriques_validation_interne=mx, duree_s=round(time.time() - t1)), open(os.path.join(a.out, 'modele_final_xgb_v2_validation_interne.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(dict(donnees=os.path.basename(a.data), md5_donnees=md5(a.data), empreintes=os.path.basename(a.fp), md5_empreintes=md5(a.fp), n_lignes_entrainement=int(len(trn)),
                   n_lignes_validation_interne=int(len(val)), n_lignes_ensemble_final_non_lues=int(len(final)), genes=genes, classes=classes, n_medicaments=len(meds), poids='inverses',
                   graine=pc.GRAINE, protocole='protocole_commun_v9 : StratifiedGroupKFold groupé par famille, graine 42, ensemble final fixé (138 familles)'),
              open(os.path.join(a.out, 'modele_final_xgb_v2_configuration.json'), 'w'), indent=1, ensure_ascii=False)
    print('XGBoost : validation interne', mx, '| %.0fs' % (time.time() - t1)); print('Fichiers écrits dans', a.out)


if __name__ == '__main__': main()
