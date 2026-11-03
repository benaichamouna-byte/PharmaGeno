#!/usr/bin/env python3
"""
modele_final_profil_v3.py (3 nov. 2026) : modèle FINAL de l'application (DL « profil génétique -> conseil pour chaque médicament ») sur le corpus v14 (189 médicaments).
Remplace modele_final_profil_v2.py (corpus v8, INTACT) : configuration 35 (choisie sur v13 par recherche imbriquée, AUCUN nouveau réglage) + calibration par température.
Protocole : mêmes familles que la validation croisée (hors ensemble final de 138 familles, JAMAIS lu) ; 10 % des familles (graine 42) servent à l'arrêt anticipé ET à la température ;
seuils d'abstention = quantiles de la probabilité maximale hors-plis de results/dl_imbrique_v14 (validation croisée config 35 + calibration), moyenne des 5 graines.
Sorties (--out) : modele_final_profil_v3.pt (arch « profil_v3 »), abstention_seuils_profil_v3.json, modele_final_profil_v3_validation_interne.json, modele_final_profil_v3_configuration.json
Usage : python3 -I modele_final_profil_v3.py --data ../data/corpus_v14/phenotype_drug_dataset_v14.csv --oof ../results/dl_imbrique_v14 --out ../modeles_v10
"""
import argparse, glob, hashlib, json, os, sys, time
import numpy as np, pandas as pd, torch
from scipy.optimize import minimize_scalar
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dl_coeur_v4 as dc, protocole_commun_v10 as pc


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'oof', 'out'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--hp', default='../results/dl_hp_v13'); ap.add_argument('--config', type=int, default=35)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); torch.set_num_threads(2)
    cfg = json.load(open(os.path.join(a.hp, 'configs.json')))[a.config]
    d = dc.tableau(a.data); X, Y, pid, fam, y = d['X'], d['Y'], d['pid'], d['fam'], d['y']; classes, genes, meds = d['classes'], d['genes'], d['meds']; K, M = len(classes), len(meds); ev = classes.index('EVITER')
    final, folds = pc.decouper(d['groups'], y); cv = np.sort(np.concatenate([te for _, te in folds]))
    p_cv = np.unique(pid[cv]); p_fin = np.unique(pid[final])
    assert not (set(p_cv) & set(p_fin)) and not (set(fam[p_cv]) & set(fam[p_fin])), "fuite : profil ou famille de l'ensemble final dans l'entraînement"
    ai, vi = next(GroupShuffleSplit(1, test_size=0.10, random_state=pc.GRAINE).split(p_cv, groups=fam[p_cv])); ptrn, pval = p_cv[ai], p_cv[vi]
    assert not (set(fam[ptrn]) & set(fam[pval]))
    print('profils entraînement : %d | validation interne : %d | ensemble final NON LU : %d profils (%d lignes) | %d médicaments | config %d : %s' % (len(ptrn), len(pval), len(p_fin), len(final), M, a.config, cfg), flush=True)
    sc = StandardScaler().fit(X[ptrn]); S = lambda ix: sc.transform(X[ix]).astype(np.float32)
    t0 = time.time(); model, hist, bv = dc.entrainer(S(ptrn), Y[ptrn], S(pval), Y[pval], K, ev, cfg, pc.GRAINE)
    Pv = dc.probas(model, S(pval)); mv = Y[pval] >= 0; lp = np.log(np.clip(Pv[mv], 1e-12, 1)); yv = Y[pval][mv]
    def nll(T):
        z = lp / T; z = z - z.max(-1, keepdims=True); q = np.exp(z); q /= q.sum(-1, keepdims=True); return -np.log(np.clip(q[np.arange(len(yv)), yv], 1e-12, 1)).mean()
    T = float(minimize_scalar(nll, bounds=(0.05, 5.0), method='bounded').x)
    z = np.log(np.clip(Pv, 1e-12, 1)) / T; z = z - z.max(-1, keepdims=True); Pc = np.exp(z); Pc /= Pc.sum(-1, keepdims=True)
    mval = pc.metriques(Y[pval][mv], Pc[mv], classes)
    print('validation interne (calibrée, T=%.3f) :' % T, mval, '| %d époques | %.0fs' % (len(hist), time.time() - t0), flush=True)
    torch.save(dict(state_dict=model.state_dict(), arch='profil_v3', genes=genes, classes=classes, medicaments=meds, scaler_mean=sc.mean_.tolist(), scaler_scale=sc.scale_.tolist(),
                    n_in=len(genes), n_med=M, K=K, cfg=cfg, temperature=T), os.path.join(a.out, 'modele_final_profil_v3.pt'))
    # seuils d'abstention : probabilité maximale hors-plis (moyenne des graines) de la validation croisée v14
    fs = sorted(glob.glob(os.path.join(a.oof, 'oof_c35_cal_pli*_graine*.npz'))); assert len(fs) == 25, 'validation croisée incomplète : %d fichiers' % len(fs)
    acc = {}
    for f in fs:
        z_ = np.load(f)
        for l, p in zip(z_['ligne'], z_['proba']): acc.setdefault(int(l), []).append(p)
    conf = np.array([np.mean(v, 0).max() for v in acc.values()])
    seuils = {('%.3f' % q): float(np.quantile(conf, q)) for q in (0.005, 0.01, 0.02, 0.05)}
    json.dump(dict(source='probabilités hors-plis calibrées de results/dl_imbrique_v14 (config 35 + calibration, %d lignes, moyenne des 5 graines)' % len(conf),
                   regle='abstenir (« non décidé par le modèle ») si la probabilité maximale est <= seuil ; la fraction indiquée est la part de prédictions écartées en validation croisée', seuils_confiance=seuils),
              open(os.path.join(a.out, 'abstention_seuils_profil_v3.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(dict(epoques=len(hist), f1_val_interne=round(bv, 4), temperature=round(T, 4), metriques_validation_interne_calibree=mval), open(os.path.join(a.out, 'modele_final_profil_v3_validation_interne.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(dict(donnees=os.path.basename(a.data), md5_donnees=md5(a.data), configuration=cfg, config_index=a.config, profils_entrainement=int(len(ptrn)), profils_validation_interne=int(len(pval)),
                   lignes_ensemble_final_non_lues=int(len(final)), variables=genes, classes=classes, n_medicaments=M, graine=pc.GRAINE, protocole='protocole_commun_v10 : StratifiedGroupKFold groupé par famille, graine 42, ensemble final fixé (138 familles)',
                   calibration='température ajustée sur la validation interne (10 % des familles)'), open(os.path.join(a.out, 'modele_final_profil_v3_configuration.json'), 'w'), indent=1, ensure_ascii=False)
    print('Fichiers écrits dans', a.out); print(json.dumps(seuils, indent=1))


if __name__ == '__main__':
    main()
