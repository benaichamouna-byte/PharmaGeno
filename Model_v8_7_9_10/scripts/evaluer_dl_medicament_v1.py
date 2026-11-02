#!/usr/bin/env python3
"""
evaluer_dl_medicament_v1.py (2 nov. 2026) : PILIER A. Le DL, qui reçoit le profil ET des descripteurs de médicament (sans information de guideline),
prédit-il l'action (ADAPTER_DOSE / EVITER / STANDARD / SURVEILLER) pour un médicament JAMAIS VU à l'entraînement ?

Protocole fixé AVANT les résultats (aucun réglage sur le test) :
  - Lignes : (profil, médicament) étiquetées « ok » du corpus v14b ; les 138 familles de l'ensemble final sont EXCLUES (jamais lues).
  - Schéma « medicament » : validation croisée en 5 plis où un médicament (et ses quasi-doublons de nom) est entièrement hors entraînement.
    Schéma « classe_ATC » : idem, mais toute la classe ATC niveau 3 du médicament est hors entraînement (plus strict).
    Schéma « prospectif » : entraînement sur les 176 médicaments du corpus v13 gelé (étiquettes v13), test sur les médicaments ajoutés depuis (étiquettes v14b).
  - Plis : StratifiedGroupKFold (strate = médicament avec/sans ligne non STANDARD), graine 42+g. Graines g = 0..G-1.
  - Descripteurs : liens gène-médicament hors guideline (3 canaux x gènes), ATC (niveaux 1, 3, 4), empreinte de Morgan 512 bits. Colonnes ATC/empreinte retenues d'après les médicaments d'ENTRAÎNEMENT seulement.
  - DL : MLP (profil one-hot + encodeur de médicament 64) ; variante « porte » = + somme sur les gènes de (porte(médicament) x logit(gène, valeur)). Réglages fixes, poids de classes en racine + EVITER x2 (comme le DL du projet), arrêt anticipé sur 14 % des médicaments d'entraînement.
  - Références sans test : majoritaire ; prior_gene_phenotype (distribution des classes par (colonne de gène, valeur) sur les médicaments d'entraînement liés à ce gène) ; voisins (k=5, similarité empreinte/ATC/liens).
  - Mesures : exactitude, exactitude équilibrée, F1 macro, rappels par classe, AUROC et AP « action non STANDARD », AP EVITER, log-loss, ECE. IC par bootstrap SUR LES MÉDICAMENTS (l'unité de généralisation est le médicament).
Résultats rapportés tels quels, y compris négatifs.
Usage : python3 -I evaluer_dl_medicament_v1.py CORPUS_V14B CORPUS_V13 DESCRIPTEURS.npz FINAL.txt SORTIE_DIR [--graines 3] [--schemas medicament,classe_ATC,prospectif] [--variantes ...] [--essai]
"""
import sys, os, re, time, argparse, difflib, json
import numpy as np, pandas as pd, torch, torch.nn as nn
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, balanced_accuracy_score, log_loss

ap = argparse.ArgumentParser()
for k in ('corpus14', 'corpus13', 'desc', 'final', 'sortie'): ap.add_argument(k)
ap.add_argument('--graines', type=int, default=3); ap.add_argument('--schemas', default='medicament,classe_ATC,prospectif')
ap.add_argument('--variantes', default='lien,lien+atc,lien+atc+fp,porte:lien+atc+fp'); ap.add_argument('--essai', action='store_true')
ap.add_argument('--epochs', type=int, default=25)
a = ap.parse_args()
os.makedirs(a.sortie, exist_ok=True); torch.set_num_threads(2)
CL = ['ADAPTER_DOSE', 'EVITER', 'STANDARD', 'SURVEILLER']; K = 4; STD = CL.index('STANDARD'); EV = CL.index('EVITER')
NON = {'drug', 'action', 'sample_id', 'family_id', 'action_ancienne', 'action_v3', 'statut_etiquette', 'confiance', 'nb_regles_appliquees', 'origine'}

# ---------------------------------------------------------------- données
def lire(chemin):
    d = pd.read_csv(chemin); d = d[d.statut_etiquette == 'ok'].copy(); d['drug'] = d.drug.str.lower(); return d
d14, d13 = lire(a.corpus14), lire(a.corpus13)
ids = {l.strip() for l in open(a.final) if l.strip() and not l.startswith('#')}
fin = {'FAM_' + i for i in ids}; assert len(ids) == 138
n0 = len(d14); d14 = d14[~d14.family_id.isin(fin)]; d13 = d13[~d13.family_id.isin(fin)]
assert not (set(d14.family_id) & fin) and not (set(d13.family_id) & fin)
print('lignes v14b %d -> %d (hors ensemble final) | v13 %d' % (n0, len(d14), len(d13)))
cols = [c for c in d14.columns if c not in NON]
P = d14.drop_duplicates('sample_id').set_index('sample_id')[cols].sort_index()
prof = list(P.index); pi = {s: i for i, s in enumerate(prof)}; NP = len(prof)
V = np.zeros((NP, len(cols)), np.int64); off = [0]; cats = []
for j, c in enumerate(cols):
    vals = sorted(P[c].dropna().unique()); cats.append(vals)
    m = {v: i for i, v in enumerate(vals)}; nm = len(vals)      # catégorie supplémentaire = valeur manquante
    V[:, j] = [m.get(x, nm) if not pd.isna(x) else nm for x in P[c].values]
    off.append(off[-1] + nm + 1)
NCAT = off[-1]; OFF = np.array(off[:-1])
Xp = np.zeros((NP, NCAT), np.float32)
for j in range(len(cols)): Xp[np.arange(NP), V[:, j] + OFF[j]] = 1.0
meds = sorted(d14.drug.unique()); mi = {m: i for i, m in enumerate(meds)}; ND = len(meds)
def matrice(d):
    Y = -np.ones((NP, ND), np.int16)
    for s, m, y in zip(d.sample_id.values, d.drug.values, d.action.map({c: i for i, c in enumerate(CL)}).values):
        if m in mi: Y[pi[s], mi[m]] = y
    return Y
Y14 = matrice(d14); Y13 = matrice(d13)
meds13 = sorted(set(d13.drug)); nouveaux = [m for m in meds if m not in set(meds13)]
print('profils %d | colonnes %d | catégories %d | médicaments v14b %d | v13 %d | ajoutés depuis v13 %d' % (NP, len(cols), NCAT, ND, len(meds13), len(nouveaux)))

Z = np.load(a.desc, allow_pickle=True); zi = {n: i for i, n in enumerate(Z['noms'])}
ZI = np.array([zi[m] for m in meds])
FP = Z['fp'][ZI].astype(np.float32); FPC = Z['fp_couverture'][ZI]; ATC = [str(Z['atc'][i]) for i in ZI]; LINK = Z['lien'][ZI]; GEN = list(Z['genes'])
base = [re.sub(r'\*.*$', '', c) for c in cols]; gcol = np.array([GEN.index(b) for b in base])
LIENFLAT = LINK.reshape(ND, -1)
LIENANY = (LINK.max(2) > 0)[:, gcol]            # ND x ncol : médicament lié à la colonne de gène (hors guideline)
def codes(i, niv): return sorted({c.strip()[:niv] for c in ATC[i].split(',') if len(c.strip()) >= niv})

# ---------------------------------------------------------------- groupes de médicaments (quasi-doublons)
par = list(range(ND))
def trouve(x):
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
SEL = set('hydrochloride hydrobromide phosphate sodium potassium sulfate lauroxil acid plain combinations'.split())
def nu(m): return ' '.join(w for w in re.sub(r'[(),]', ' ', m).split() if w not in SEL)
for i in range(ND):
    for j in range(i + 1, ND):
        x, y = nu(meds[i]), nu(meds[j])
        if x and y and (x == y or difflib.SequenceMatcher(None, x, y).ratio() >= 0.9 or ('/' not in x and '/' not in y and (x.startswith(y) or y.startswith(x)))):
            par[trouve(i)] = trouve(j)
GMED = np.array([trouve(i) for i in range(ND)])
mult = {}
for i in range(ND): mult.setdefault(GMED[i], []).append(meds[i])
print('groupes de quasi-doublons (> 1 nom) :', [v for v in mult.values() if len(v) > 1])
_cle = ['A:' + (codes(i, 4)[0] if codes(i, 4) else 'NA_' + meds[i]) for i in range(ND)]
GATC = np.unique(_cle, return_inverse=True)[1]
YD = np.array([int(((Y14[:, i] >= 0) & (Y14[:, i] != STD)).any()) for i in range(ND)])

# ---------------------------------------------------------------- similarité entre médicaments (sans étiquettes)
def similarite():
    S = np.zeros((ND, ND), np.float32); C = np.zeros((ND, ND), np.float32)
    has = FPC > 0; inter = FP @ FP.T; un = FP.sum(1)[:, None] + FP.sum(1)[None] - inter
    tani = np.where(un > 0, inter / np.maximum(un, 1), 0); m = has[:, None] & has[None]
    S += np.where(m, tani, 0); C += m
    a3 = [set(codes(i, 4)) for i in range(ND)]
    for i in range(ND):
        for j in range(ND):
            if a3[i] and a3[j]: S[i, j] += len(a3[i] & a3[j]) / len(a3[i] | a3[j]); C[i, j] += 1
    nl = np.linalg.norm(LIENFLAT, axis=1); okl = nl > 0
    cos = (LIENFLAT @ LIENFLAT.T) / np.maximum(nl[:, None] * nl[None], 1e-9); m = okl[:, None] & okl[None]
    S += np.where(m, cos, 0); C += m
    return np.where(C > 0, S / np.maximum(C, 1), 0)
SIM = similarite()

# ---------------------------------------------------------------- descripteurs par pli (colonnes retenues d'après l'entraînement seulement)
def desc_pli(var, tr):
    parts = [LIENFLAT, (LINK.sum((1, 2)) > 0).astype(np.float32)[:, None]]
    if 'atc' in var:
        voc = sorted({c for niv in (1, 4, 5) for i in tr for c in codes(i, niv)})
        A = np.zeros((ND, len(voc) + 1), np.float32); vi = {c: k for k, c in enumerate(voc)}
        for i in range(ND):
            for niv in (1, 4, 5):
                for c in codes(i, niv):
                    if c in vi: A[i, vi[c]] = 1
            A[i, -1] = 1.0 if ATC[i] else 0.0
        parts.append(A)
    if 'fp' in var:
        keep = FP[tr].sum(0) >= 2
        parts += [FP[:, keep], (FPC > 0).astype(np.float32)[:, None]]
    return np.hstack(parts).astype(np.float32)

# ---------------------------------------------------------------- DL
class Net(nn.Module):
    def __init__(s, dd, porte, h=256, p=0.3):
        super().__init__()
        s.enc = nn.Sequential(nn.Linear(dd, 64), nn.ReLU(), nn.Dropout(p))
        s.corps = nn.Sequential(nn.Linear(NCAT + 64, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(p), nn.Linear(h, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(p), nn.Linear(h, K))
        s.porte = porte
        if porte:
            s.E = nn.Embedding(NCAT, K); nn.init.zeros_(s.E.weight); s.g = nn.Linear(64, len(cols))
    def forward(s, xp, xd, v):
        z = s.enc(xd); out = s.corps(torch.cat([xp, z], 1))
        if s.porte:
            gate = nn.functional.softplus(s.g(z))                       # B x ncol
            out = out + (gate.unsqueeze(2) * s.E(v + torch.tensor(OFF))).sum(1)
        return out

def paires(Y, ds):
    ds = np.asarray(ds); sub = Y[:, ds]; p, k = np.where(sub >= 0); return p, ds[k], sub[p, k].astype(np.int64)
def poids(y):
    f = np.bincount(y, minlength=K).astype(float) + 1; w = (1 / np.sqrt(f)); w = w / w.mean(); w[EV] *= 2; return torch.tensor(w, dtype=torch.float32)
def lot(Fd, p, d, idx): return torch.tensor(Xp[p[idx]]), torch.tensor(Fd[d[idx]]), torch.tensor(V[p[idx]])
def predire(m, Fd, p, d, bs=4096):
    m.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(p), bs):
            idx = np.arange(i, min(i + bs, len(p))); out.append(torch.softmax(m(*lot(Fd, p, d, idx)), 1).numpy())
    return np.concatenate(out)
def dl(var, Y, tr, te, graine):
    porte = var.startswith('porte:'); v = var.replace('porte:', '')
    torch.manual_seed(graine); rng = np.random.RandomState(graine)
    sk = StratifiedGroupKFold(n_splits=7, shuffle=True, random_state=graine)
    ytr_d = YD[tr]; a_, b_ = next(iter(sk.split(tr, ytr_d, GMED[tr])))
    fit, val = tr[a_], tr[b_]
    Fd = desc_pli(v, tr)
    pf, df_, yf = paires(Y, fit); pv, dv, yv = paires(Y, val); pt, dt, _ = paires(Y, te)
    w = poids(yf); lossf = nn.CrossEntropyLoss(weight=w); m = Net(Fd.shape[1], porte)
    opt = torch.optim.Adam(m.parameters(), lr=1e-3, weight_decay=1e-4); best, bs_, att = 1e9, None, 0
    for ep in range(a.epochs):
        m.train(); perm = rng.permutation(len(pf))
        for i in range(0, len(perm), 2048):
            idx = perm[i:i + 2048]
            if len(idx) < 8: continue
            opt.zero_grad(); l = lossf(m(*lot(Fd, pf, df_, idx)), torch.tensor(yf[idx])); l.backward(); opt.step()
        pv_ = predire(m, Fd, pv, dv); lv = float(nn.functional.nll_loss(torch.log(torch.tensor(pv_) + 1e-9), torch.tensor(yv), weight=w))
        if lv < best - 1e-4: best, bs_, att = lv, {k: x.clone() for k, x in m.state_dict().items()}, 0
        else:
            att += 1
            if att >= 4: break
    m.load_state_dict(bs_)
    return pt, dt, predire(m, Fd, pt, dt), ep + 1

# ---------------------------------------------------------------- références
def r_majoritaire(Y, tr, te):
    pt, dt, _ = paires(Y, te); f = np.bincount(paires(Y, tr)[2], minlength=K) + 1.0
    return pt, dt, np.tile(f / f.sum(), (len(pt), 1))
def r_prior(Y, tr, te):
    p, d, y = paires(Y, tr); glob = np.bincount(y, minlength=K) + 1.0; glob = glob / glob.sum(); T = np.tile(glob, (len(cols), NCAT, 1))
    al = 5.0
    for j in range(len(cols)):
        sel = LIENANY[d, j]
        if not sel.any(): continue
        vv = V[p[sel], j] + OFF[j]; cnt = np.zeros((NCAT, K))
        np.add.at(cnt, (vv, y[sel]), 1)
        for c in np.unique(vv): T[j, c] = (cnt[c] + al * glob) / (cnt[c].sum() + al)
    pt, dt, _ = paires(Y, te); acc = np.zeros((len(pt), K)); n = np.zeros(len(pt))
    for j in range(len(cols)):
        sel = LIENANY[dt, j]
        acc[sel] += T[j][V[pt[sel], j] + OFF[j]]; n[sel] += 1
    out = np.where(n[:, None] > 0, acc / np.maximum(n[:, None], 1), glob)
    return pt, dt, out
def r_voisins(Y, tr, te, k=5):
    pt, dt, _ = paires(Y, te); out = np.zeros((len(pt), K)); glob = np.bincount(paires(Y, tr)[2], minlength=K) + 1.0; glob /= glob.sum()
    vois = {d: tr[np.argsort(-SIM[d, tr])[:k]] for d in np.unique(dt)}
    for d, nb in vois.items():
        sel = np.where(dt == d)[0]; lab = Y[pt[sel]][:, nb]            # n x k
        cnt = np.zeros((len(sel), K))
        for c in range(K): cnt[:, c] = (lab == c).sum(1)
        tot = cnt.sum(1, keepdims=True); out[sel] = np.where(tot > 0, cnt / np.maximum(tot, 1), glob)
    return pt, dt, out

# ---------------------------------------------------------------- mesures
def ece(pr, y, bins=15):
    conf = pr.max(1); ok = (pr.argmax(1) == y).astype(float); e = np.linspace(0, 1, bins + 1); t = 0.0
    for lo, hi in zip(e[:-1], e[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any(): t += m.mean() * abs(ok[m].mean() - conf[m].mean())
    return t
def mesures(pr, y):
    pred = pr.argmax(1); act = (y != STD).astype(int); sc = 1 - pr[:, STD]
    r = dict(exactitude=(pred == y).mean(), exactitude_equilibree=balanced_accuracy_score(y, pred), f1_macro=f1_score(y, pred, average='macro', labels=list(range(K)), zero_division=0),
             auroc_non_standard=roc_auc_score(act, sc) if 0 < act.sum() < len(act) else np.nan, ap_non_standard=average_precision_score(act, sc) if act.sum() else np.nan,
             ap_eviter=average_precision_score((y == EV).astype(int), pr[:, EV]) if (y == EV).any() else np.nan,
             logloss=log_loss(y, np.clip(pr, 1e-9, 1), labels=list(range(K))), ece=ece(pr, y), part_non_standard=act.mean())
    for c in (0, 1, 3): r['rappel_' + CL[c]] = ((pred == c) & (y == c)).sum() / max((y == c).sum(), 1) if (y == c).any() else np.nan
    return r

# ---------------------------------------------------------------- exécution
def plis(schema, g):
    sk = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42 + g)
    grp = GMED if schema == 'medicament' else GATC
    return [(np.arange(ND)[x], np.arange(ND)[y]) for x, y in sk.split(np.arange(ND), YD, grp)]
variantes = a.variantes.split(','); lignes = []; oof = {}
t0 = time.time()
for schema in a.schemas.split(','):
    G = 5 if schema == 'prospectif' else a.graines
    for g in range(G):
        if schema == 'prospectif':
            tr = np.array([mi[m] for m in meds13]); te = np.array([mi[m] for m in nouveaux]); jeux = [(tr, te, Y13, Y14)]
        else:
            jeux = [(tr, te, Y14, Y14) for tr, te in plis(schema, g)]
        probs = {}
        for (tr, te, Ytr, Yte) in jeux:
            # étiquettes d'entraînement = Ytr ; étiquettes de test = Yte
            Yc = Ytr.copy(); Yc[:, te] = Yte[:, te]
            if schema != 'prospectif':
                assert not set(GMED[tr]) & set(GMED[te]) or schema == 'classe_ATC'
                if schema == 'classe_ATC': assert not set(GATC[tr]) & set(GATC[te])
            else:
                Yc[:, np.setdiff1d(np.arange(ND), np.concatenate([tr, te]))] = -1
            for nom, f in (('majoritaire', r_majoritaire), ('prior_gene_phenotype', r_prior), ('voisins_k5', r_voisins)):
                pt, dt, pr = f(Yc, tr, te); probs.setdefault(nom, []).append((pt, dt, pr))
            for var in variantes:
                if a.essai and var != variantes[0]: continue
                pt, dt, pr, ne = dl(var, Yc, tr, te, g); probs.setdefault('DL_' + var, []).append((pt, dt, pr)); print('  [%s g%d] %s : %d époques, %.0f s' % (schema, g, var, ne, time.time() - t0), flush=True)
        for nom, L in probs.items():
            pt = np.concatenate([x[0] for x in L]); dt = np.concatenate([x[1] for x in L]); pr = np.vstack([x[2] for x in L])
            y = Y14[pt, dt].astype(int); assert (y >= 0).all()
            lignes.append(dict(schema=schema, graine=g, modele=nom, lignes=len(y), medicaments=len(set(dt)), **mesures(pr, y)))
            oof.setdefault((schema, nom), []).append((pt, dt, pr, y))
        print('[%s] graine %d terminée (%.0f s)' % (schema, g, time.time() - t0), flush=True)
R = pd.DataFrame(lignes); R.to_csv(os.path.join(a.sortie, 'resultats_par_graine.csv'), index=False)
for (schema, nom), L in oof.items():
    np.savez_compressed(os.path.join(a.sortie, 'oof_%s_%s.npz' % (schema, nom.replace(':', '_').replace('+', '_'))), meds=np.array(meds),
                        pt=np.stack([x[0] for x in L]), dt=np.stack([x[1] for x in L]), pr=np.stack([x[2] for x in L]).astype(np.float32), y=np.stack([x[3] for x in L]))
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
M = R.drop(columns='graine').groupby(['schema', 'modele']).mean().round(4)
print(M.to_string())
print('\necart-type entre graines (auroc_non_standard, f1_macro):')
print(R.groupby(['schema', 'modele'])[['auroc_non_standard', 'f1_macro']].std().round(4).to_string())
json.dump(dict(medicaments=meds, nouveaux=nouveaux), open(os.path.join(a.sortie, 'medicaments.json'), 'w'))
