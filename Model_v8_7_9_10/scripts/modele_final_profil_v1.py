#!/usr/bin/env python3
"""
modele_final_profil_v1.py : entraîne et enregistre le modèle de l'APPLICATION v8f (DL « profil génétique -> conseil pour chaque médicament »).

Même principe que modele_final_v8.py : entraînement sur toutes les lignes de validation croisée (~90 %), l'ensemble final (10 % des familles) n'est PAS lu, aucune évaluation finale.
Réglages IDENTIQUES à train_dl_profil_v1.py (fixés à l'avance, non ajustés) : 2 couches de 256, BatchNorm, Dropout 0,3, Adam 1e-3, poids de classes en racine + EVITER x2,
arrêt anticipé sur le F1 macro de la validation interne (10 % des familles), graine 42.
Seuils d'abstention : quantiles de la probabilité maximale hors-plis (fichier oof_moyenne_graines.npz de train_dl_profil_v1.py), jamais l'ensemble final.

Sorties (dossier --out) : modele_final_profil_v1.pt, abstention_seuils_profil_v1.json, modele_final_profil_v1_validation_interne.json, modele_final_profil_v1_configuration.json
Usage : python3 modele_final_profil_v1.py --data ../data/phenotype_drug_dataset_v7.csv --fp <drug_fingerprints_v2.pkl> --oof ../results/dl_profil_v1/oof_moyenne_graines.npz --out <dossier_modeles> [--smoke]
"""
import argparse, hashlib, json, os, time
import numpy as np, pandas as pd, torch
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
import protocole_commun_v8 as pc
from train_dl_profil_v1 import probas, entrainer


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'fp', 'oof', 'out'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--epochs', type=int, default=300); ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); torch.set_num_threads(max(1, os.cpu_count() or 1))
    d = pc.charger(a.data, a.fp, familles_smoke=0.25 if a.smoke else None)
    df, genes, G, y, classes, groups, meds = d['df'], d['genes'], d['G'], d['y'], d['classes'], d['groups'], d['meds']
    K, M = len(classes), len(meds); ev = classes.index('EVITER')
    sid = df.sample_id.values; profils = pd.unique(sid); pidx = {s: i for i, s in enumerate(profils)}; pid = np.array([pidx[s] for s in sid])
    first = pd.Series(np.arange(len(df))).groupby(pid).first().values; X = G[first].astype(np.float32); assert np.allclose(G, X[pid]), 'profil non identique sur toutes les lignes d\'un profil'
    Y = np.full((len(profils), M), -1, dtype=np.int64); Y[pid, d['drug_idx']] = y; fam = groups[first]
    final, folds = pc.decouper(groups, y); cv = np.sort(np.concatenate([te for _, te in folds]))
    p_cv = np.unique(pid[cv]); p_fin = np.unique(pid[final])
    assert not (set(p_cv) & set(p_fin)) and not (set(fam[p_cv]) & set(fam[p_fin])), 'fuite : profil ou famille de l\'ensemble final dans l\'entraînement'
    gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE); ai, vi = next(gss.split(p_cv, groups=fam[p_cv])); ptrn, pval = p_cv[ai], p_cv[vi]
    assert not (set(fam[ptrn]) & set(fam[pval]))
    print('profils entraînement : %d | validation interne : %d | ensemble final NON LU : %d profils (%d lignes)' % (len(ptrn), len(pval), len(p_fin), len(final)), flush=True)
    sc = StandardScaler().fit(X[ptrn]); S = lambda ix: sc.transform(X[ix]).astype(np.float32)
    cnt = np.bincount(Y[ptrn][Y[ptrn] >= 0], minlength=K).astype(float); w = np.sqrt(cnt.sum() / (K * np.maximum(cnt, 1))); w = w.copy(); w[ev] *= 2.0
    t0 = time.time(); model, hist, bv = entrainer(S(ptrn), Y[ptrn], S(pval), Y[pval], K, w, pc.GRAINE, 2 if a.smoke else a.epochs)
    Pv = probas(model, S(pval)); mk = Y[pval] >= 0; mv = pc.metriques(Y[pval][mk], Pv[mk], classes)
    print('validation interne :', mv, '| %d époques | %.0fs' % (len(hist), time.time() - t0), flush=True)
    torch.save(dict(state_dict=model.state_dict(), arch='profil_v1', genes=genes, classes=classes, medicaments=meds, scaler_mean=sc.mean_.tolist(), scaler_scale=sc.scale_.tolist(),
                    n_in=len(genes), n_med=M, K=K, h=256, p=0.3), os.path.join(a.out, 'modele_final_profil_v1.pt'))
    oof = np.load(a.oof, allow_pickle=True); conf = oof['proba'].max(1)
    seuils = {('%.3f' % q): float(np.quantile(conf, q)) for q in (0.005, 0.01, 0.02, 0.05)}
    json.dump(dict(source='probabilités hors-plis de la validation croisée (train_dl_profil_v1.py, %d valeurs, moyenne des graines)' % len(conf),
                   regle='abstenir (« non décidé par le modèle ») si la probabilité maximale est <= seuil ; la fraction indiquée est la part de prédictions écartées en validation croisée',
                   seuils_confiance=seuils), open(os.path.join(a.out, 'abstention_seuils_profil_v1.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(dict(epoques=len(hist), f1_val_interne=round(bv, 4), metriques_validation_interne=mv), open(os.path.join(a.out, 'modele_final_profil_v1_validation_interne.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(dict(donnees=os.path.basename(a.data), md5_donnees=md5(a.data), empreintes=os.path.basename(a.fp), md5_empreintes=md5(a.fp), oof=os.path.basename(a.oof), md5_oof=md5(a.oof),
                   profils_entrainement=int(len(ptrn)), profils_validation_interne=int(len(pval)), lignes_ensemble_final_non_lues=int(len(final)), variables=genes, classes=classes, n_medicaments=M,
                   poids='racine, EVITER x2', graine=pc.GRAINE, protocole='protocole_commun_v8 : StratifiedGroupKFold groupé par famille, graine 42'),
              open(os.path.join(a.out, 'modele_final_profil_v1_configuration.json'), 'w'), indent=1, ensure_ascii=False)
    print('Fichiers écrits dans', a.out); print(json.dumps(seuils, indent=1))


if __name__ == '__main__':
    main()
