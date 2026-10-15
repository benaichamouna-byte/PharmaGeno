#!/usr/bin/env python3
"""
train_dl_v7b.py : copie de train_dl_v7.py avec UNE variante en plus (film_id). DL (PharmaGenoDL) avec le protocole commun
(protocole_commun.py) : 10 % des familles mises de côté
(non touchées ici) + validation croisée en 5 plis groupée par famille sur les ~90 % restants.

Ce script N'ÉCRASE RIEN et ne touche JAMAIS à l'ensemble final : il n'écrit que dans le dossier --out.
Variantes TOUTES rapportées (même les moins bonnes) ; les trois premières ont été fixées à l'avance :
  base : architecture de train_dl_v6.py (attention sur les gènes calculée à partir du profil seul)
  film : l'attention sur les gènes ET la première couche du réseau des gènes sont pilotées par le médicament
         (modulation FiLM, Perez et al. 2018, https://arxiv.org/abs/1709.07871)
  id   : architecture 'base' mais l'empreinte moléculaire est remplacée par un identifiant du médicament (one-hot).
         Sert de référence : mesure ce que l'empreinte apporte réellement (RQ4).
  film_id : architecture 'film' avec l'identifiant du médicament (sans empreinte). VARIANTE AJOUTÉE APRÈS avoir vu les résultats
         de base, film et id (à déclarer comme telle dans le mémoire) : elle sépare l'effet de l'architecture de celui de l'empreinte.

Usage :
  python3 train_dl_v7b.py --data phenotype_drug_dataset_v3_croise.csv --fp drug_fingerprints_v2.pkl --out resultats_dl_v7 --variante base
  ... --smoke   # essai rapide (une partie des familles, 1 pli, 2 époques) pour vérifier que tout tourne
"""
import argparse, json, os, time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
import protocole_commun as pc


class GeneAttention(nn.Module):
    def __init__(self, n):
        super().__init__(); self.attn = nn.Linear(n, n)
    def poids(self, x):
        return torch.softmax(self.attn(x), dim=-1)
    def forward(self, x):
        return x * self.poids(x)


class PharmaGenoDL(nn.Module):
    def __init__(self, n_genes, fp_dim, n_classes=4, arch='base'):
        super().__init__()
        self.arch = arch
        self.drug_branch = nn.Sequential(
            nn.Linear(fp_dim, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 64), nn.ReLU())
        if arch == 'film':
            self.attn_med = nn.Linear(64, n_genes)           # attention sur les gènes décidée par le médicament
            self.g_lin = nn.Linear(n_genes, 64); self.g_bn = nn.BatchNorm1d(64)
            self.film = nn.Linear(64, 128)                   # gamma et beta (64 + 64) décidés par le médicament
            nn.init.zeros_(self.film.weight); nn.init.zeros_(self.film.bias)   # départ = identité
            self.g_rest = nn.Sequential(nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, 32), nn.BatchNorm1d(32), nn.ReLU())
        else:
            self.gene_attention = GeneAttention(n_genes)
            self.gene_branch = nn.Sequential(
                nn.Linear(n_genes, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
                nn.Linear(64, 32), nn.BatchNorm1d(32), nn.ReLU())
        self.combined = nn.Sequential(
            nn.Linear(96, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, n_classes))

    def poids_attention(self, g, d):
        if self.arch == 'film':
            return torch.softmax(self.attn_med(self.drug_branch(d)), dim=-1)
        return self.gene_attention.poids(g)

    def forward(self, g, d):
        z = self.drug_branch(d)
        if self.arch == 'film':
            x = g * torch.softmax(self.attn_med(z), dim=-1)
            h = self.g_bn(self.g_lin(x)); gam, bet = self.film(z).chunk(2, 1)
            gv = self.g_rest(h * (1 + gam) + bet)
        else:
            gv = self.gene_branch(self.gene_attention(g))
        return self.combined(torch.cat([gv, z], 1))


def predire(model, G, D, bs=4096, attention=False):
    model.eval(); out = []; att = []
    with torch.no_grad():
        for i in range(0, len(G), bs):
            g, d = torch.from_numpy(G[i:i + bs]), torch.from_numpy(D[i:i + bs])
            out.append(torch.softmax(model(g, d), 1).numpy())
            if attention: att.append(model.poids_attention(g, d).numpy())
    return (np.concatenate(out), np.concatenate(att)) if attention else np.concatenate(out)


def entrainer(Gtr, Dtr, ytr, Gva, Dva, yva, n_classes, epochs, seed, poids, arch):
    torch.manual_seed(seed)
    model = PharmaGenoDL(Gtr.shape[1], Dtr.shape[1], n_classes, arch)
    opt = torch.optim.Adam(model.parameters(), lr=0.0005, weight_decay=0.005)
    crit = nn.CrossEntropyLoss(weight=torch.tensor(poids, dtype=torch.float32))
    Gt, Dt, yt = torch.from_numpy(Gtr), torch.from_numpy(Dtr), torch.from_numpy(ytr)
    rng = np.random.RandomState(seed); best, best_state, wait, hist = -1, None, 0, []
    for ep in range(epochs):
        model.train(); perm = rng.permutation(len(Gt)); tot = 0.0; nb = 0
        for i in range(0, len(perm) - 1, 512):
            idx = torch.from_numpy(perm[i:i + 512])
            if len(idx) < 2: continue
            opt.zero_grad(); loss = crit(model(Gt[idx], Dt[idx]), yt[idx]); loss.backward(); opt.step()
            tot += loss.item(); nb += 1
        f1v = f1_score(yva, predire(model, Gva, Dva).argmax(1), average='macro')
        hist.append((ep + 1, round(tot / max(nb, 1), 4), round(float(f1v), 4)))
        if f1v > best + 1e-4:
            best, wait = f1v, 0; best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= 8: break
    model.load_state_dict(best_state)
    return model, hist, float(best)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True); ap.add_argument('--fp', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--variante', choices=['base', 'film', 'id', 'film_id'], default='base')
    ap.add_argument('--epochs', type=int, default=60); ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); torch.set_num_threads(max(1, os.cpu_count() or 1))
    d = pc.charger(a.data, a.fp, familles_smoke=0.25 if a.smoke else None)
    df, genes, y, classes, G, groups = d['df'], d['genes'], d['y'], d['classes'], d['G'], d['groups']
    K = len(classes)
    FP = np.eye(len(d['meds']), dtype=np.float32) if a.variante in ('id', 'film_id') else d['FP']
    D = FP[d['drug_idx']]
    arch = 'film' if a.variante in ('film', 'film_id') else 'base'
    print('Variante : %s | gènes (%d) : %s' % (a.variante, len(genes), genes))
    print('Classes :', classes, np.bincount(y).tolist())
    final, folds = pc.decouper(groups, y)
    pc.ecrire_decoupage(os.path.join(a.out, 'decoupage_v7.csv'), df, final, folds)
    print('Ensemble final mis de côté : %d lignes, %d familles (NON utilisé ici)' % (len(final), len(set(groups[final]))))
    if a.smoke: folds = folds[:1]
    n_cv = sum(len(te) for _, te in folds)
    oof = np.zeros((len(y), K), dtype=np.float32); att_all = np.zeros((len(y), len(genes)), dtype=np.float32)
    fold_of = np.full(len(y), -1); lignes = []; courbes = []; t0 = time.time()
    for k, (tr, te) in enumerate(folds):
        gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE)
        a_idx, v_idx = next(gss.split(tr, groups=groups[tr])); trn, val = tr[a_idx], tr[v_idx]
        sc = StandardScaler().fit(G[trn]); Gs = lambda ix: sc.transform(G[ix]).astype(np.float32)
        cnt = np.bincount(y[trn], minlength=K).astype(float); w = len(trn) / (K * np.maximum(cnt, 1))
        model, hist, bestval = entrainer(Gs(trn), D[trn], y[trn], Gs(val), D[val], y[val], K,
                                         2 if a.smoke else a.epochs, pc.GRAINE + k, w, arch)
        P, att = predire(model, Gs(te), D[te], attention=True)
        oof[te] = P; att_all[te] = att; fold_of[te] = k
        ligne = dict(pli=k + 1, n_test=int(len(te)), epoques=len(hist), f1_val_interne=round(bestval, 4), **pc.metriques(y[te], P, classes))
        lignes.append(ligne); print(ligne, '| %.0fs' % (time.time() - t0), flush=True)
        courbes += [dict(pli=k + 1, epoque=e, perte_train=l, f1_val=f) for e, l, f in hist]
    res = pd.DataFrame(lignes); tag = 'dl_v7_' + a.variante
    res.to_csv(os.path.join(a.out, tag + '_resultats_par_pli.csv'), index=False)
    pd.DataFrame(courbes).to_csv(os.path.join(a.out, tag + '_courbes.csv'), index=False)
    m = fold_of >= 0
    glob = dict(modele='DL', variante=a.variante, protocole='ensemble final 10%% des familles à part ; StratifiedGroupKFold(%d) groupes=family_id graine=%d' % (pc.N_PLIS, pc.GRAINE),
                n_lignes_cv=int(m.sum()), n_lignes_final_non_utilisees=int(len(final)), genes=genes, classes=classes,
                f1_macro_moy=float(res.f1_macro.mean()), f1_macro_std=float(res.f1_macro.std(ddof=0)),
                f1_hors_surveiller_moy=float(res.f1_hors_surveiller.mean()),
                CER_strict_moy=float(res.CER_strict.mean()), CER_strict_std=float(res.CER_strict.std(ddof=0)),
                ECE_moy=float(res.ECE.mean()), precision_EVITER_moy=float(res.precision_EVITER.mean()),
                f1_macro_oof=float(f1_score(y[m], oof[m].argmax(1), average='macro')))
    if 'confiance' in df.columns:
        h = (df.confiance.values == 'haute') & m
        glob['f1_macro_oof_confiance_haute'] = float(f1_score(y[h], oof[h].argmax(1), average='macro'))
    glob['attention_moyenne_par_gene'] = dict(zip(genes, att_all[m].mean(0).round(4).tolist()))
    json.dump(glob, open(os.path.join(a.out, tag + '_resume.json'), 'w'), indent=1, ensure_ascii=False)
    np.savez_compressed(os.path.join(a.out, tag + '_oof.npz'), proba=oof[m], y=y[m], pli=fold_of[m], ligne=np.where(m)[0],
                        drug=df.drug.values[m].astype(str), attention=att_all[m].astype(np.float16), genes=np.array(genes))
    print('\nRÉSULTAT DL (%s) : F1 macro = %.4f +/- %.4f | CER strict = %.4f | ECE = %.4f' % (
        a.variante, glob['f1_macro_moy'], glob['f1_macro_std'], glob['CER_strict_moy'], glob['ECE_moy']))
    print('Fichiers écrits dans', a.out)


if __name__ == '__main__':
    main()
