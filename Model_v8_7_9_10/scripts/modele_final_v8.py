#!/usr/bin/env python3
"""
modele_final_v8.py : entraîne les modèles de l'APPLICATION v8 sur toutes les lignes de validation croisée (les ~90 %, corpus v7)
et enregistre leurs fichiers. L'ensemble final (10 % des familles) n'est PAS lu ici : aucune évaluation finale, aucun verrou posé.
(modele_final_v7.py reste intact. L'évaluation finale se fera une seule fois, plus tard, par un script à part, une fois la configuration figée.)

Configuration FIGÉE par la validation croisée (5 graines, corpus v7) ; rien n'est réglé ici :
  dl_film_id : DL film, médicament = identifiant appris (one-hot), poids de classes « racine », poids EVITER x2, tous les gènes, graine 42
  xgb_id     : XGBoost, identifiant, poids de classes inverses (comme en validation croisée), arrêt anticipé sur la log-loss, graine 42
Validation interne (arrêt anticipé) : 10 % des familles de l'ensemble d'entraînement, comme en validation croisée.

Abstention : seuils de confiance (probabilité maximale) calculés sur les probabilités HORS-PLI de la validation croisée (5 graines du DL,
fichiers resultats_v9/phase2b + resultats_v9/graines), donc jamais sur l'ensemble final ; ils sont enregistrés dans abstention_seuils_v8.json.

Sorties (dossier --out) : modele_final_v8_dl_film_id.pt, modele_final_v8_xgb_id.json + _meta.json, abstention_seuils_v8.json,
                           modele_final_v8_validation_interne.json (métriques sur la validation interne seulement), modele_final_v8_configuration.json
"""
import argparse, glob, hashlib, json, os, time
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
import protocole_commun_v8 as pc
import train_dl_v9_graines as dl


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True); ap.add_argument('--fp', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--oof_dl', nargs='+', required=True, help="fichiers dl_v7_film_oof.npz (hors-plis) pour les seuils d'abstention")
    ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); nj = os.cpu_count() or 1
    import torch; torch.set_num_threads(nj)
    d = pc.charger(a.data, a.fp, familles_smoke=0.25 if a.smoke else None)
    df, genes, y, classes, G, groups, meds = d['df'], d['genes'], d['y'], d['classes'], d['G'], d['groups'], d['meds']
    K = len(classes); ID = np.eye(len(meds), dtype=np.float32)[d['drug_idx']]
    final, folds = pc.decouper(groups, y); cv = np.sort(np.concatenate([te for _, te in folds]))
    assert not (set(groups[final]) & set(groups[cv])), 'fuite : famille de l\'ensemble final dans l\'entraînement'
    gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE); ia, iv = next(gss.split(cv, groups=groups[cv])); trn, val = cv[ia], cv[iv]
    assert not (set(groups[trn]) & set(groups[val]))
    cnt = np.bincount(y[trn], minlength=K).astype(float); w_inv = len(trn) / (K * np.maximum(cnt, 1))
    w_dl = np.sqrt(w_inv).copy(); w_dl[classes.index('EVITER')] *= 2.0
    sc = StandardScaler().fit(G[trn]); S = lambda ix: sc.transform(G[ix]).astype(np.float32)
    print('Entraînement : %d lignes | validation interne : %d | ensemble final (NON LU) : %d lignes' % (len(trn), len(val), len(final)))
    t0 = time.time(); info = {}
    # --- DL ---
    model, hist, bv = dl.entrainer(S(trn), ID[trn], y[trn], S(val), ID[val], y[val], K, 2 if a.smoke else 60, pc.GRAINE, w_dl, 'film')
    Pv = dl.predire(model, S(val), ID[val]); mv = pc.metriques(y[val], Pv, classes)
    torch.save(dict(state_dict=model.state_dict(), arch='film', genes=genes, classes=classes, medicaments=meds,
                    scaler_mean=sc.mean_.tolist(), scaler_scale=sc.scale_.tolist(), n_genes=len(genes), fp_dim=len(meds)),
               os.path.join(a.out, 'modele_final_v8_dl_film_id.pt'))
    info['dl_film_id'] = dict(epoques=len(hist), f1_val_interne=round(bv, 4), metriques_validation_interne=mv, duree_s=round(time.time() - t0))
    print('DL : validation interne', mv, '| %.0fs' % (time.time() - t0), flush=True)
    # --- XGBoost (second avis) ---
    from xgboost import XGBClassifier
    X = np.hstack([G, ID]).astype(np.float32); t1 = time.time()
    m = XGBClassifier(objective='multi:softprob', num_class=K, n_estimators=30 if a.smoke else 1000, learning_rate=0.1, max_depth=6, tree_method='hist',
                      early_stopping_rounds=20, eval_metric='mlogloss', n_jobs=nj, random_state=pc.GRAINE, verbosity=0)
    m.fit(X[trn], y[trn], sample_weight=w_inv[y[trn]], eval_set=[(X[val], y[val])], verbose=False)
    Pxv = np.zeros((len(val), K), dtype=np.float32); Pxv[:, m.classes_.astype(int)] = m.predict_proba(X[val]); mx = pc.metriques(y[val], Pxv, classes)
    m.save_model(os.path.join(a.out, 'modele_final_v8_xgb_id.json'))
    json.dump(dict(genes=genes, classes=classes, medicaments=meds), open(os.path.join(a.out, 'modele_final_v8_xgb_id_meta.json'), 'w'), ensure_ascii=False)
    info['xgb_id'] = dict(arbres=int(m.best_iteration) + 1, metriques_validation_interne=mx, duree_s=round(time.time() - t1))
    print('XGBoost : validation interne', mx, '| %.0fs' % (time.time() - t1), flush=True)
    # --- seuils d'abstention (probabilités hors-plis de la validation croisée ; aucune lecture de l'ensemble final) ---
    conf = np.concatenate([np.load(p, allow_pickle=True)['proba'].max(1) for p in a.oof_dl])
    seuils = {('%.3f' % q): float(np.quantile(conf, q)) for q in (0.005, 0.01, 0.02, 0.05)}
    json.dump(dict(source='probabilités hors-plis de la validation croisée (DL, %d fichiers, %d valeurs)' % (len(a.oof_dl), len(conf)),
                   regle='abstenir (« non décidé par le modèle ») si la probabilité maximale du DL est <= seuil ; la fraction indiquée est la part de prédictions écartées en validation croisée',
                   seuils_confiance=seuils), open(os.path.join(a.out, 'abstention_seuils_v8.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(info, open(os.path.join(a.out, 'modele_final_v8_validation_interne.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(dict(donnees=os.path.basename(a.data), md5_donnees=md5(a.data), empreintes=os.path.basename(a.fp), md5_empreintes=md5(a.fp),
                   n_lignes_entrainement=int(len(trn)), n_lignes_validation_interne=int(len(val)), n_lignes_ensemble_final_non_lues=int(len(final)),
                   gènes=genes, classes=classes, n_medicaments=len(meds), poids_dl='racine, EVITER x2', poids_xgb='inverses', graine=pc.GRAINE,
                   protocole='protocole_commun_v8 : StratifiedGroupKFold groupé par famille, graine 42'),
              open(os.path.join(a.out, 'modele_final_v8_configuration.json'), 'w'), indent=1, ensure_ascii=False)
    print('Fichiers écrits dans', a.out)


if __name__ == '__main__':
    main()
