#!/usr/bin/env python3
"""
exp_medicament_inconnu_v7.py : RQ5 — le modèle sait-il prédire pour un médicament JAMAIS VU à l'entraînement ?

Principe : sur les ~90 % de lignes de validation croisée (l'ensemble final de 138 familles n'est PAS touché), les plis sont
formés par MÉDICAMENT (StratifiedGroupKFold, groupe = médicament, graine 42, 5 plis) : tous les médicaments d'un pli de test
sont absents de l'entraînement. La validation interne (arrêt anticipé du DL et de XGBoost) est aussi découpée par médicament.
Seule l'EMPREINTE moléculaire permet de décrire un médicament inconnu : l'identifiant est donc exclu de cette expérience.

Modèles (réglages identiques à train_dl_v7b.py et train_arbres_v7.py, rien n'est réglé ici) :
  dl_film, dl_base, xgb, rf, et un repère sans apprentissage : 'voisin' = copie de l'étiquette du même patient pour le médicament
  d'entraînement le plus proche par similarité de Tanimoto entre empreintes. Repère 'majoritaire' = classe la plus fréquente.
Résultats rapportés sur (a) tous les médicaments et (b) les 44 médicaments dont l'étiquette dépend du profil génétique.
Aucune valeur n'est ajustée après coup : le script écrit ce qu'il mesure.

Usage : python3 exp_medicament_inconnu_v7.py --data phenotype_drug_dataset_v3_croise.csv --fp drug_fingerprints_v2.pkl --out resultats_rq5_v7
        ... --smoke   # essai rapide
"""
import argparse, json, os, time
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, accuracy_score, recall_score
import protocole_commun as pc
import train_dl_v7b as dl


def poids(y, trn, K):
    cnt = np.bincount(y[trn], minlength=K).astype(float); return len(trn) / (K * np.maximum(cnt, 1))


def run_dl(arch, G, D, y, trn, val, te, K, seed, epochs):
    sc = StandardScaler().fit(G[trn]); S = lambda ix: sc.transform(G[ix]).astype(np.float32)
    model, _, _ = dl.entrainer(S(trn), D[trn], y[trn], S(val), D[val], y[val], K, epochs, seed, poids(y, trn, K), arch)
    return dl.predire(model, S(te), D[te])


def run_arbres(nom, X, y, trn, val, te, K, seed, smoke, nj):
    sw = poids(y, trn, K)[y[trn]]
    if nom == 'xgb':
        from xgboost import XGBClassifier
        m = XGBClassifier(objective='multi:softprob', num_class=K, n_estimators=30 if smoke else 1000, learning_rate=0.1, max_depth=6,
                          tree_method='hist', early_stopping_rounds=20, eval_metric='mlogloss', n_jobs=nj, random_state=seed, verbosity=0)
        m.fit(X[trn], y[trn], sample_weight=sw, eval_set=[(X[val], y[val])], verbose=False)
    else:
        from sklearn.ensemble import RandomForestClassifier
        m = RandomForestClassifier(n_estimators=40 if smoke else 500, max_features='sqrt', n_jobs=nj, random_state=seed)
        m.fit(X[trn], y[trn], sample_weight=sw)
    P = np.zeros((len(te), K), dtype=np.float32); P[:, m.classes_.astype(int)] = m.predict_proba(X[te]); return P


def repere_voisin(df, y, d, trn, te, K):
    """Pour chaque ligne de test (patient s, médicament inconnu m) : étiquette de s pour le médicament d'entraînement le plus proche de m."""
    FP = d['FP']; meds = d['meds']; di = d['drug_idx']
    sid = pd.factorize(df.sample_id.values)[0]; Y = np.full((sid.max() + 1, len(meds)), -1)
    Y[sid[trn], di[trn]] = y[trn]
    train_drugs = np.unique(di[trn]); maj = np.bincount(y[trn], minlength=K).argmax(); pred = np.full(len(te), maj)
    inter = FP[:, :] @ FP[train_drugs].T; un = FP.sum(1)[:, None] + FP[train_drugs].sum(1)[None, :] - inter
    sim = inter / np.maximum(un, 1e-9)
    for m in np.unique(di[te]):
        rows = np.where(di[te] == m)[0]; ordre = train_drugs[np.argsort(-sim[m])]; p = np.full(len(rows), -1)
        for dd in ordre:
            ok = (p < 0) & (Y[sid[te][rows], dd] >= 0); p[ok] = Y[sid[te][rows][ok], dd]
            if (p >= 0).all(): break
        pred[rows] = np.where(p >= 0, p, maj)
    return pred


def metr_simple(y, pred, classes):
    ev = classes.index('EVITER'); rec = recall_score(y, pred, average=None, labels=range(len(classes)), zero_division=0)
    return dict(f1_macro=round(float(f1_score(y, pred, average='macro')), 4), CER_strict=round(float(1 - rec[ev]), 4),
                exactitude=round(float(accuracy_score(y, pred)), 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True); ap.add_argument('--fp', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--smoke', action='store_true'); ap.add_argument('--epochs', type=int, default=60)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); nj = os.cpu_count() or 1
    import torch; torch.set_num_threads(nj)
    d = pc.charger(a.data, a.fp, familles_smoke=0.25 if a.smoke else None)
    df, genes, y, classes, G, groups, FP = d['df'], d['genes'], d['y'], d['classes'], d['G'], d['groups'], d['FP']
    K = len(classes); drugs = df.drug.values; D = FP[d['drug_idx']]; X = np.hstack([G, D]).astype(np.float32)
    final, folds_fam = pc.decouper(groups, y)
    cv = np.sort(np.concatenate([te for _, te in folds_fam]))
    nl = pd.Series(y[cv]).groupby(drugs[cv]).nunique(); dep = set(nl.index[nl > 1])
    print('Lignes de validation croisée : %d | ensemble final non utilisé : %d | médicaments : %d dont %d dépendent du profil génétique' % (
        len(cv), len(final), len(nl), len(dep)))
    sg = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=pc.GRAINE)
    plis = [(cv[a_], cv[b_]) for a_, b_ in sg.split(cv, y[cv], drugs[cv])]
    for tr, te in plis: assert not (set(drugs[tr]) & set(drugs[te])), 'fuite : un médicament du test est dans l\'entraînement'
    if a.smoke: plis = plis[:1]
    lignes, par_med = [], []; t0 = time.time()
    for k, (tr, te) in enumerate(plis):
        g = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=pc.GRAINE); ia, iv = next(g.split(tr, groups=drugs[tr])); trn, val = tr[ia], tr[iv]
        preds = {}
        preds['majoritaire'] = np.full(len(te), np.bincount(y[trn], minlength=K).argmax())
        preds['voisin'] = repere_voisin(df, y, d, trn, te, K)
        res = {}
        for nom, arch in (('dl_film', 'film'), ('dl_base', 'base')):
            res[nom] = run_dl(arch, G, D, y, trn, val, te, K, pc.GRAINE + k, 2 if a.smoke else a.epochs)
        for nom in ('xgb', 'rf'):
            res[nom] = run_arbres(nom, X, y, trn, val, te, K, pc.GRAINE + k, a.smoke, nj)
        for nom, P in res.items(): preds[nom] = P.argmax(1)
        dep_te = np.array([m in dep for m in drugs[te]])
        for nom in preds:
            for sous, msk in (('tous', np.ones(len(te), bool)), ('dependants', dep_te)):
                if msk.sum() == 0: continue
                r = dict(pli=k + 1, modele=nom, sous_ensemble=sous, n_test=int(msk.sum()), n_medicaments=len(set(drugs[te][msk])))
                if nom in res: r.update(pc.metriques(y[te][msk], res[nom][msk], classes))
                else: r.update(metr_simple(y[te][msk], preds[nom][msk], classes))
                lignes.append(r)
        for m in sorted(set(drugs[te])):
            mk = drugs[te] == m
            for nom in preds:
                par_med.append(dict(pli=k + 1, medicament=m, depend_du_profil=m in dep, modele=nom, n=int(mk.sum()),
                                    exactitude=round(float(accuracy_score(y[te][mk], preds[nom][mk])), 4)))
        print('pli %d terminé | %d médicaments de test | %.0fs' % (k + 1, len(set(drugs[te])), time.time() - t0), flush=True)
    R = pd.DataFrame(lignes); R.to_csv(os.path.join(a.out, 'rq5_resultats_par_pli.csv'), index=False)
    pd.DataFrame(par_med).to_csv(os.path.join(a.out, 'rq5_par_medicament.csv'), index=False)
    S = R.groupby(['sous_ensemble', 'modele'])[[c for c in ['f1_macro', 'CER_strict', 'exactitude', 'ECE'] if c in R.columns]].agg(['mean', 'std']).round(4)
    S.to_csv(os.path.join(a.out, 'rq5_resume.csv')); print('\n', S.to_string())
    json.dump(dict(protocole='plis par médicament (StratifiedGroupKFold, groupe=médicament, graine %d), ensemble final non utilisé' % pc.GRAINE,
                   n_lignes_cv=int(len(cv)), n_medicaments=int(len(nl)), n_medicaments_dependants=len(dep), medicaments_dependants=sorted(dep)),
              open(os.path.join(a.out, 'rq5_description.json'), 'w'), indent=1, ensure_ascii=False)
    print('Fichiers écrits dans', a.out)


if __name__ == '__main__':
    main()
