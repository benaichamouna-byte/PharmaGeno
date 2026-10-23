#!/usr/bin/env python3
"""
VERSION v2 (corpus v8, 23 oct. 2026) : copie de la v1 dont SEULS changent le protocole (protocole_commun_v9 : ensemble final FIXÉ aux 138 familles) et les noms de fichiers. Réglages inchangés.
train_dl_profil_v2.py : DL « profil génétique -> recommandation pour chaque médicament ».

Entrée du réseau : le profil génétique seul (les mêmes variables que le DL actuel). Sortie : 113 médicaments x 4 conseils (STANDARD, ADAPTER_DOSE, EVITER, SURVEILLER).
Le médicament n'est PLUS une entrée : c'est une sortie. Les cases sans étiquette (profil x médicament sans règle) sont ignorées dans la perte.
Aucune des anciennes versions n'est modifiée. Protocole IDENTIQUE à celui du DL actuel (protocole_commun_v8) : 10 % des familles à part (jamais lues ici),
validation croisée en 5 plis groupée par famille, graine 42, mêmes métriques (calculées sur les mêmes lignes de test : profil x médicament), pour une comparaison appariée.
Réglages fixés à l'avance, NON ajustés sur les résultats : 2 couches cachées de 256, BatchNorm, Dropout 0,3, Adam lr 1e-3, poids de classes en racine + EVITER x2 (comme le DL actuel),
arrêt anticipé sur le F1 macro de la validation interne (10 % des familles du pli d'entraînement).
Usage : python3 train_dl_profil_v2.py --data ../data/corpus_v8/phenotype_drug_dataset_v8.csv --fp <drug_fingerprints_v2.pkl> --out ../results/dl_profil_v1 [--graines 5] [--smoke]
"""
import argparse, json, os, time
import numpy as np, pandas as pd, torch, torch.nn as nn
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
import protocole_commun_v9 as pc


class DLProfil(nn.Module):
    def __init__(self, n_in, n_med, K, h=256, p=0.3):
        super().__init__(); self.n_med, self.K = n_med, K
        self.corps = nn.Sequential(nn.Linear(n_in, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(p),
                                   nn.Linear(h, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(p))
        self.sortie = nn.Linear(h, n_med * K)
    def forward(self, x):
        return self.sortie(self.corps(x)).view(-1, self.n_med, self.K)


def probas(model, X, bs=1024):
    model.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(X), bs): out.append(torch.softmax(model(torch.from_numpy(X[i:i + bs])), -1).numpy())
    return np.concatenate(out)          # (n_profils, n_med, K)


def f1_cases(P, Y, mask):
    return f1_score(Y[mask], P.argmax(-1)[mask], average='macro')


def entrainer(Xtr, Ytr, Xva, Yva, K, w, seed, epochs, patience=25, lr=1e-3):
    torch.manual_seed(seed); rng = np.random.RandomState(seed)
    model = DLProfil(Xtr.shape[1], Ytr.shape[1], K)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    crit = nn.CrossEntropyLoss(weight=torch.tensor(w, dtype=torch.float32), ignore_index=-1)
    Xt, Yt = torch.from_numpy(Xtr), torch.from_numpy(Ytr); mva = Yva >= 0
    best, state, wait, hist = -1.0, None, 0, []
    for ep in range(epochs):
        model.train(); perm = rng.permutation(len(Xt)); tot, nb = 0.0, 0
        for i in range(0, len(perm), 64):
            idx = torch.from_numpy(perm[i:i + 64])
            if len(idx) < 2: continue
            opt.zero_grad(); loss = crit(model(Xt[idx]).reshape(-1, K), Yt[idx].reshape(-1)); loss.backward(); opt.step(); tot += loss.item(); nb += 1
        f1v = f1_cases(probas(model, Xva), Yva, mva); hist.append((ep + 1, round(tot / max(nb, 1), 4), round(float(f1v), 4)))
        if f1v > best + 1e-4: best, wait, state = f1v, 0, {k: v.clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= patience: break
    model.load_state_dict(state); return model, hist, float(best)


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'fp', 'out'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--graines', type=int, default=5); ap.add_argument('--epochs', type=int, default=300); ap.add_argument('--smoke', action='store_true'); ap.add_argument('--plis', type=int, default=5, help='nombre de plis exécutés (5 = protocole complet ; moins = essai de durée)')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); torch.set_num_threads(max(1, os.cpu_count() or 1))
    d = pc.charger(a.data, a.fp, familles_smoke=0.25 if a.smoke else None)
    df, G, y, classes, groups, meds = d['df'], d['G'], d['y'], d['classes'], d['groups'], d['meds']
    K, M = len(classes), len(meds); ev = classes.index('EVITER')
    # --- tableau profil x médicament ---
    sid = df.sample_id.values; profils = pd.unique(sid); pidx = {s: i for i, s in enumerate(profils)}; pid = np.array([pidx[s] for s in sid])
    X = np.zeros((len(profils), G.shape[1]), dtype=np.float32); Y = np.full((len(profils), M), -1, dtype=np.int64)
    first = pd.Series(np.arange(len(df))).groupby(pid).first().values; X[:] = G[first]
    assert np.allclose(G, X[pid]), 'le profil n\'est pas identique sur toutes les lignes d\'un même profil'
    Y[pid, d['drug_idx']] = y; fam = groups[first]
    print('profils : %d | médicaments : %d | variables d\'entrée : %d | cases étiquetées : %d sur %d' % (len(profils), M, X.shape[1], int((Y >= 0).sum()), Y.size), flush=True)
    final, folds = pc.decouper(groups, y)
    if a.smoke: folds = folds[:1]
    folds = folds[:a.plis]
    pf = set(pid[final]); assert not any(set(pid[te]) & set(pid[tr]) for tr, te in folds) and not (pf & set(np.concatenate([pid[tr] for tr, _ in folds]))), 'fuite de profil'
    seeds = list(range(1 if a.smoke else a.graines)); rows = []; oof_sum = np.zeros((len(y), K)); t0 = time.time()
    for s in seeds:
        for k, (tr, te) in enumerate(folds):
            ptr = np.unique(pid[tr]); pte = np.unique(pid[te])
            gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE)
            ai, vi = next(gss.split(ptr, groups=fam[ptr])); ptrn, pval = ptr[ai], ptr[vi]
            sc = StandardScaler().fit(X[ptrn]); S = lambda ix: sc.transform(X[ix]).astype(np.float32)
            cnt = np.bincount(Y[ptrn][Y[ptrn] >= 0], minlength=K).astype(float); w = np.sqrt(cnt.sum() / (K * np.maximum(cnt, 1))); w = w.copy(); w[ev] *= 2.0
            model, hist, bv = entrainer(S(ptrn), Y[ptrn], S(pval), Y[pval], K, w, pc.GRAINE + 100 * s + k, 2 if a.smoke else a.epochs)
            Pc = probas(model, S(pte)); loc = {p: i for i, p in enumerate(pte)}
            Pte = Pc[[loc[p] for p in pid[te]], d['drug_idx'][te]]          # probabilités pour exactement les lignes de test du protocole
            oof_sum[te] += Pte
            r = dict(graine=s, pli=k + 1, n_test=len(te), epoques=len(hist), f1_val_interne=round(bv, 4), **pc.metriques(y[te], Pte, classes)); rows.append(r)
            print(r, '| %.0fs' % (time.time() - t0), flush=True)
    R = pd.DataFrame(rows); R.to_csv(os.path.join(a.out, 'resultats_par_graine_et_pli.csv'), index=False)
    par_graine = R.groupby('graine')[['f1_macro', 'f1_hors_surveiller', 'exactitude', 'CER_strict', 'precision_EVITER', 'ECE']].mean()
    resume = dict(modele='DL profil -> medicaments v1', graines=len(seeds), plis=len(folds), n_lignes_final_non_utilisees=int(len(final)),
                  f1_macro_moy=float(par_graine.f1_macro.mean()), f1_macro_std=float(par_graine.f1_macro.std(ddof=0)),
                  CER_strict_moy=float(par_graine.CER_strict.mean()), CER_strict_std=float(par_graine.CER_strict.std(ddof=0)),
                  precision_EVITER_moy=float(par_graine.precision_EVITER.mean()), exactitude_moy=float(par_graine.exactitude.mean()), ECE_moy=float(par_graine.ECE.mean()),
                  reference_DL_actuel_journal_19oct=dict(f1_macro='0,9980 +/- 0,0010', EVITER_manques='0,0029 +/- 0,0010', precision_EVITER='0,992 +/- 0,005', config='film, identifiant de médicament, poids racine, EVITER x2, 5 graines'))
    json.dump(resume, open(os.path.join(a.out, 'resume.json'), 'w'), indent=1, ensure_ascii=False)
    te_all = np.concatenate([te for _, te in folds]); np.savez_compressed(os.path.join(a.out, 'oof_moyenne_graines.npz'), ligne=te_all, proba=(oof_sum[te_all] / len(seeds)).astype(np.float32), y=y[te_all])
    print('\n' + par_graine.round(4).to_string()); print(json.dumps(resume, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
