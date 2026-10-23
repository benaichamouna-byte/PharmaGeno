#!/usr/bin/env python3
"""
VERSION v2 (corpus v8, 23 oct. 2026) : copie de la v1 dont SEULS changent le protocole (protocole_commun_v9 : ensemble final FIXÉ aux 138 familles) et les noms de fichiers. Réglages inchangés.
train_dl_choix_v2.py : DL « profil génétique complet -> CHOIX du médicament dans une classe thérapeutique ».

Le clinicien donne le VCF (profil de 22 gènes) et l'indication sous forme de classe de médicaments (ATC niveau 4, OMS). Le réseau reçoit le profil seul et produit un SCORE par médicament (113 scores).
Dans chaque classe, un softmax sur les médicaments de la classe donne la distribution de choix ; le médicament prédit = le plus probable.
CIBLE (convention, écrite dans la thèse, NON tirée d'une guideline) : pour un profil et une classe, parmi les médicaments ayant une étiquette CPIC/DPWG pour ce profil (au moins 2),
l'ensemble S = les médicaments de la meilleure action disponible, dans l'ordre STANDARD > SURVEILLER > ADAPTER_DOSE ; EVITER n'est jamais cible. Cible d'entraînement = loi uniforme sur S.
Aucune guideline ne dit quel médicament de S est le « meilleur » : S ne se départage pas. Ce que le DL doit apprendre : quels médicaments sortent de S selon la combinaison des gènes du profil.
Protocole IDENTIQUE à train_dl_profil_v2.py (protocole_commun_v8) : 10 % des familles à part (jamais lues ici), 5 plis groupés par famille, graine 42, 5 graines. Réglages fixés à l'avance, non ajustés :
2 x 256, BatchNorm, Dropout 0,3, Adam 1e-3, wd 1e-4, batch 64, arrêt anticipé (patience 25) sur la perte de validation interne (10 % des familles du pli d'entraînement).
Métriques (sur les profils de test, jamais vus) : choix dans S ; choix dans S sur les cas « informatifs » (S différent de l'ensemble des médicaments étiquetés) ; part de choix « à éviter » ;
comparés à 2 références sans le profil : choix au hasard, et « médicament le plus fréquent dans S sur l'entraînement » (même choix pour tous les patients).
Usage : python3 train_dl_choix_v2.py --data ../data/corpus_v8/phenotype_drug_dataset_v8.csv --fp <drug_fingerprints_v2.pkl> --out ../results/dl_choix_v1 [--graines 5] [--smoke]
"""
import argparse, json, os, time
import numpy as np, pandas as pd, torch, torch.nn as nn
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
import protocole_commun_v9 as pc

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
RANG = {'STANDARD': 0, 'SURVEILLER': 1, 'ADAPTER_DOSE': 2}     # meilleure action disponible d'abord ; EVITER exclu


def classes_atc4(meds):
    """Classes ATC4 (OMS) ayant >= 2 médicaments du modèle. Retourne liste de dict(code, nom, meds)."""
    m = pd.read_csv(os.path.join(DATA, 'atc_mapping_medicaments_v1.csv')); m = m[m.medicament.isin(meds) & m.atc_codes.notna()]
    noms = pd.read_csv(os.path.join(DATA, 'alternatives_atc4_v1.csv')).drop_duplicates('classe_atc4').set_index('classe_atc4').nom_classe_atc4.to_dict()
    cl = {}
    for _, r in m.iterrows():
        for c in str(r.atc_codes).split(';'):
            c = c.strip()[:5]
            if len(c) == 5: cl.setdefault(c, set()).add(r.medicament)
    return [dict(code=c, nom=noms.get(c, c), meds=sorted(v)) for c, v in sorted(cl.items()) if len(v) >= 2]


def cibles(Y, classes, meds, CL):
    """Y (N, M) indices d'action (-1 = pas d'étiquette). Retourne L (N, C, W) étiquetés, T (N, C, W) cible uniforme sur S (0 si pas de cible), E (N, C, W) étiqueté EVITER, IDX (C, W), PAD (C, W)."""
    C = len(CL); W = max(len(c['meds']) for c in CL); M = len(meds); mi = {m: i for i, m in enumerate(meds)}
    IDX = np.zeros((C, W), dtype=np.int64); PAD = np.ones((C, W), dtype=bool)
    for j, c in enumerate(CL):
        for k, m in enumerate(c['meds']): IDX[j, k] = mi[m]; PAD[j, k] = False
    N = len(Y); L = np.zeros((N, C, W), dtype=bool); T = np.zeros((N, C, W), dtype=np.float32); E = np.zeros((N, C, W), dtype=bool)
    code = {c: i for i, c in enumerate(classes)}; rang = np.full(len(classes), 99); [rang.__setitem__(code[a], r) for a, r in RANG.items()]
    ev = code['EVITER']
    for j in range(C):
        Yc = Y[:, IDX[j]]; lab = (Yc >= 0) & ~PAD[j][None, :]; L[:, j] = lab; E[:, j] = lab & (Yc == ev)
        r = np.where(lab, rang[np.maximum(Yc, 0)], 99); best = r.min(1)
        S = lab & (r == best[:, None]) & (best[:, None] < 99)
        ok = (lab.sum(1) >= 2) & (best < 99)
        T[:, j] = np.where(ok[:, None], S / np.maximum(S.sum(1, keepdims=True), 1), 0.0)
    return L, T, E, IDX, PAD


class DLChoix(nn.Module):
    def __init__(self, n_in, n_med, h=256, p=0.3):
        super().__init__()
        self.corps = nn.Sequential(nn.Linear(n_in, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(p), nn.Linear(h, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(p))
        self.sortie = nn.Linear(h, n_med)
    def forward(self, x): return self.sortie(self.corps(x))          # (n, 113) scores


def log_choix(scores, IDX, cand):
    """scores (n, M) ; IDX (C, W) tensor ; cand (n, C, W) bool = médicaments candidats. Retourne log-softmax (n, C, W) restreint aux candidats (-inf ailleurs)."""
    Z = scores[:, IDX]; Z = Z.masked_fill(~cand, float('-inf'))
    return torch.log_softmax(Z.masked_fill(~cand.any(-1, keepdim=True), 0.0), -1).masked_fill(~cand, float('-inf'))


def perte(scores, IDX, L, T):
    lp = log_choix(scores, IDX, L); has = T.sum(-1) > 0
    ce = -(T * torch.where(torch.isfinite(lp), lp, torch.zeros_like(lp))).sum(-1)
    return ce[has].mean() if has.any() else scores.sum() * 0


def entrainer(Xtr, Ltr, Ttr, Xva, Lva, Tva, IDX, seed, epochs, patience=25, lr=1e-3):
    torch.manual_seed(seed); rng = np.random.RandomState(seed)
    model = DLChoix(Xtr.shape[1], int(IDX.max()) + 1); opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    Xt, Lt, Tt = torch.from_numpy(Xtr), torch.from_numpy(Ltr), torch.from_numpy(Ttr); Xv, Lv, Tv = torch.from_numpy(Xva), torch.from_numpy(Lva), torch.from_numpy(Tva); I = torch.from_numpy(IDX)
    best, state, wait, hist = 1e9, None, 0, []
    for ep in range(epochs):
        model.train(); perm = rng.permutation(len(Xt)); tot, nb = 0.0, 0
        for i in range(0, len(perm), 64):
            idx = torch.from_numpy(perm[i:i + 64])
            if len(idx) < 2: continue
            opt.zero_grad(); loss = perte(model(Xt[idx]), I, Lt[idx], Tt[idx]); loss.backward(); opt.step(); tot += loss.item(); nb += 1
        model.eval()
        with torch.no_grad(): lv = float(perte(model(Xv), I, Lv, Tv))
        hist.append((ep + 1, round(tot / max(nb, 1), 4), round(lv, 4)))
        if lv < best - 1e-4: best, wait, state = lv, 0, {k: v.clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= patience: break
    model.load_state_dict(state); return model, hist, best


def scores_choix(model, X, IDX, L):
    """Log-probabilités de choix (n, C, W) parmi les candidats L (-inf ailleurs)."""
    model.eval()
    with torch.no_grad(): return log_choix(model(torch.from_numpy(X)), torch.from_numpy(IDX), torch.from_numpy(L)).numpy()


def evaluer(logp, L, T, E, q):
    """logp (n, C, W) : log-probabilités de choix du DL (-inf hors candidats). q (C, W) : part des cas d'entraînement où chaque médicament est dans S (référence qui ignore le profil).
    Ensemble prédit par le DL = médicaments dont la probabilité est >= 0,5 x la meilleure ; par la référence = médicaments avec q >= 0,5 (le même pour tous les patients ; au moins le plus fréquent)."""
    p = np.exp(logp); top = np.where(L, logp, -np.inf).argmax(-1); qq = np.where(L, q[None], -1.0); top_r = qq.argmax(-1)
    has = T.sum(-1) > 0; n = np.arange(len(top))[:, None]; C = np.arange(top.shape[1])[None, :]; S = T > 0
    Sd = L & (p >= 0.5 * p.max(-1, keepdims=True)); Sr = L & ((qq >= 0.5) | (np.arange(L.shape[-1])[None, None, :] == top_r[..., None]))
    dans, dans_r = S[n, C, top], S[n, C, top_r]; ev, ev_r = E[n, C, top], E[n, C, top_r]
    inform = has & (S.sum(-1) < L.sum(-1)); evp = has & E.any(-1); echec = inform & ~dans_r
    jac = lambda P_: (P_ & S).sum(-1) / np.maximum((P_ | S).sum(-1), 1)
    f = lambda a_, m: float(a_[m].mean()) if m.any() else float('nan')
    return dict(n_cas=int(has.sum()), n_informatifs=int(inform.sum()), n_defaut_faux=int(echec.sum()), n_avec_EVITER_dans_la_classe=int(evp.sum()),
                choix_dans_S_informatifs=f(dans, inform), defaut_dans_S_informatifs=f(dans_r, inform), choix_dans_S_si_defaut_faux=f(dans, echec),
                ensemble_exact_informatifs=f((Sd == S).all(-1), inform), defaut_ensemble_exact_informatifs=f((Sr == S).all(-1), inform),
                jaccard_informatifs=f(jac(Sd), inform), defaut_jaccard_informatifs=f(jac(Sr), inform),
                choix_EVITER_si_EVITER_possible=f(ev, evp), defaut_EVITER_si_EVITER_possible=f(ev_r, evp),
                hasard_dans_S_informatifs=f(S.sum(-1) / np.maximum(L.sum(-1), 1), inform))


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'fp', 'out'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--graines', type=int, default=5); ap.add_argument('--epochs', type=int, default=300); ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); torch.set_num_threads(max(1, os.cpu_count() or 1))
    d = pc.charger(a.data, a.fp, familles_smoke=0.25 if a.smoke else None)
    df, G, y, classes, groups, meds = d['df'], d['G'], d['y'], d['classes'], d['groups'], d['meds']; M = len(meds)
    sid = df.sample_id.values; profils = pd.unique(sid); pidx = {s: i for i, s in enumerate(profils)}; pid = np.array([pidx[s] for s in sid])
    X = np.zeros((len(profils), G.shape[1]), dtype=np.float32); Y = np.full((len(profils), M), -1, dtype=np.int64)
    first = pd.Series(np.arange(len(df))).groupby(pid).first().values; X[:] = G[first]; Y[pid, d['drug_idx']] = y; fam = groups[first]
    CL = classes_atc4(meds); L, T, E, IDX, PAD = cibles(Y, classes, meds, CL)
    json.dump([dict(code=c['code'], nom=c['nom'], medicaments=c['meds']) for c in CL], open(os.path.join(a.out, 'classes_choix.json'), 'w'), indent=1, ensure_ascii=False)
    print('profils %d | médicaments %d | classes %d | cas (profil, classe) avec cible : %d' % (len(profils), M, len(CL), int((T.sum(-1) > 0).sum())), flush=True)
    final, folds = pc.decouper(groups, y)
    if a.smoke: folds = folds[:1]
    pf = set(pid[final]); assert not any(set(pid[te]) & set(pid[tr]) for tr, te in folds) and not (pf & set(np.concatenate([pid[tr] for tr, _ in folds]))), 'fuite de profil'
    seeds = list(range(1 if a.smoke else a.graines)); rows = []; t0 = time.time()
    for s in seeds:
        for k, (tr, te) in enumerate(folds):
            ptr = np.unique(pid[tr]); pte = np.unique(pid[te])
            ai, vi = next(GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE).split(ptr, groups=fam[ptr])); ptrn, pval = ptr[ai], ptr[vi]
            sc = StandardScaler().fit(X[ptrn]); S_ = lambda ix: sc.transform(X[ix]).astype(np.float32)
            model, hist, bv = entrainer(S_(ptrn), L[ptrn], T[ptrn], S_(pval), L[pval], T[pval], IDX, pc.GRAINE + 100 * s + k, 2 if a.smoke else a.epochs)
            sc_dl = scores_choix(model, S_(pte), IDX, L[pte])
            ok = (T[ptrn].sum(-1) > 0)[..., None] & L[ptrn]; q = ((T[ptrn] > 0) & ok).sum(0) / np.maximum(ok.sum(0), 1)       # référence : part des cas d'entraînement où le médicament est dans S, profil ignoré
            r = evaluer(sc_dl, L[pte], T[pte], E[pte], q); r.update(graine=s, pli=k + 1, epoques=len(hist), perte_val_interne=round(bv, 4))
            rows.append(r); print({k_: (round(v, 4) if isinstance(v, float) else v) for k_, v in r.items()}, '| %.0fs' % (time.time() - t0), flush=True)
    R = pd.DataFrame(rows); R.to_csv(os.path.join(a.out, 'resultats_par_graine_et_pli.csv'), index=False)
    cols = [c for c in R.columns if c not in ('graine', 'pli', 'epoques', 'perte_val_interne', 'n_cas', 'n_informatifs', 'n_defaut_faux', 'n_avec_EVITER_dans_la_classe')]
    pg = R.groupby('graine')[cols].mean()
    res = {c: dict(moy=float(pg[c].mean()), std=float(pg[c].std(ddof=0))) for c in pg.columns}; res.update(graines=len(seeds), plis=len(folds), classes=len(CL), n_lignes_final_non_utilisees=int(len(final)))
    json.dump(res, open(os.path.join(a.out, 'resume.json'), 'w'), indent=1, ensure_ascii=False); print('\n' + pg.round(4).to_string()); print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
