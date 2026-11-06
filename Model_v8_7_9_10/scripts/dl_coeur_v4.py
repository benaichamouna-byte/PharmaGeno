#!/usr/bin/env python3
"""
dl_coeur_v4.py : cœur du DL « profil génétique -> conseil pour chaque médicament » (corpus v13, 30 oct. 2026).
Même idée que train_dl_profil_v3.py (inchangé) mais : architecture et réglages PARAMÉTRABLES (profondeur, largeur, dropout, BatchNorm, activation, lr,
décroissance des poids, taille de lot, exposant des poids de classes, facteur EVITER, lissage d'étiquettes) et journal d'apprentissage complet par époque
(perte d'entraînement, F1 macro de validation, norme du gradient) pour lire les courbes. Protocole : protocole_commun_v10 (découpage et métriques identiques à v9).
"""
import numpy as np, pandas as pd, torch, torch.nn as nn
from sklearn.metrics import f1_score
import protocole_commun_v10 as pc

CFG_V3 = dict(couches=2, largeur=256, dropout=0.3, bn=True, act='relu', lr=1e-3, wd=1e-4, lot=64, w_exp=0.5, ev_x=2.0, lissage=0.0, patience=25)


class DL(nn.Module):
    def __init__(self, n_in, n_med, K, cfg):
        super().__init__(); self.n_med, self.K = n_med, K
        act = {'relu': nn.ReLU, 'gelu': nn.GELU}[cfg['act']]; L = []; d = n_in
        for _ in range(cfg['couches']):
            L.append(nn.Linear(d, cfg['largeur']))
            if cfg['bn']: L.append(nn.BatchNorm1d(cfg['largeur']))
            L += [act(), nn.Dropout(cfg['dropout'])]; d = cfg['largeur']
        self.corps = nn.Sequential(*L); self.sortie = nn.Linear(d, n_med * K)
    def forward(self, x): return self.sortie(self.corps(x)).view(-1, self.n_med, self.K)


def tableau(data):
    """profil x médicament : X (profils, variables), Y (profils, médicaments ; -1 = pas d'étiquette), + indices par ligne."""
    d = pc.charger(data, None); df, G, y = d['df'], d['G'], d['y']
    sid = df.sample_id.values; profils = pd.unique(sid); pidx = {s: i for i, s in enumerate(profils)}; pid = np.array([pidx[s] for s in sid])
    X = np.zeros((len(profils), G.shape[1]), dtype=np.float32); Y = np.full((len(profils), len(d['meds'])), -1, dtype=np.int64)
    first = pd.Series(np.arange(len(df))).groupby(pid).first().values; X[:] = G[first]
    assert np.allclose(G, X[pid]); Y[pid, d['drug_idx']] = y
    d.update(X=X, Y=Y, pid=pid, fam=d['groups'][first], profils=profils); return d


def probas(model, X, bs=1024):
    model.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(X), bs): out.append(torch.softmax(model(torch.from_numpy(X[i:i + bs])), -1).numpy())
    return np.concatenate(out)


def poids(Y, K, ev, cfg):
    cnt = np.bincount(Y[Y >= 0], minlength=K).astype(float); w = (cnt.sum() / (K * np.maximum(cnt, 1))) ** cfg['w_exp']; w = w.copy(); w[ev] *= cfg['ev_x']; return w


def entrainer(Xtr, Ytr, Xva, Yva, K, ev, cfg, seed, epochs=300):
    torch.manual_seed(seed); rng = np.random.RandomState(seed)
    model = DL(Xtr.shape[1], Ytr.shape[1], K, cfg)
    opt = torch.optim.Adam(model.parameters(), lr=cfg['lr'], weight_decay=cfg['wd'])
    crit = nn.CrossEntropyLoss(weight=torch.tensor(poids(Ytr, K, ev, cfg), dtype=torch.float32), ignore_index=-1, label_smoothing=cfg['lissage'])
    Xt, Yt = torch.from_numpy(Xtr), torch.from_numpy(Ytr); mva = Yva >= 0
    best, state, wait, hist = -1.0, None, 0, []
    for ep in range(epochs):
        model.train(); perm = rng.permutation(len(Xt)); tot, nb, gn = 0.0, 0, 0.0
        for i in range(0, len(perm), cfg['lot']):
            idx = torch.from_numpy(perm[i:i + cfg['lot']])
            if len(idx) < 2: continue
            opt.zero_grad(); loss = crit(model(Xt[idx]).reshape(-1, K), Yt[idx].reshape(-1)); loss.backward()
            gn += float(torch.sqrt(sum((p.grad ** 2).sum() for p in model.parameters() if p.grad is not None))); opt.step(); tot += loss.item(); nb += 1
        Pv = probas(model, Xva); f1v = f1_score(Yva[mva], Pv.argmax(-1)[mva], average='macro')
        hist.append((ep + 1, tot / max(nb, 1), float(f1v), gn / max(nb, 1)))
        if f1v > best + 1e-4: best, wait, state = f1v, 0, {k: v.clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= cfg['patience']: break
    model.load_state_dict(state); return model, hist, float(best)
