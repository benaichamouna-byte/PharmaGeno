#!/usr/bin/env python3
# couverture_risque_v2.py : analyse couverture-risque des predictions hors-pli d'un bras.
#
# Remplace couverture_risque_dl_v1.py, introuvable dans l'arborescence du projet.
# AVANT de servir a produire des chiffres nouveaux, ce script doit etre valide en
# reproduisant les valeurs publiees du corpus v14 (AUROC 0,870 ; 71,6 % des erreurs
# dans le premier centile ; tableau 6.2). Lancer donc d'abord sur dl_imbrique_v14.
#
# Usage :
#   python3 couverture_risque_v2.py <dossier_oof> [quoi]
#   python3 couverture_risque_v2.py ../results/dl_imbrique_v14 c35_cal
#   python3 couverture_risque_v2.py ../results/dl_imbrique_v15 c35_cal
#
# Conventions reprises du memoire :
#   - confiance d'une ligne = probabilite maximale calibree
#   - AUROC et tableau de couverture : calcules par graine sur l'ensemble des
#     predictions hors-pli (les 5 plis reunis), puis moyennes sur les graines
#   - seuils d'abstention du tableau 4.1 : quantiles de la probabilite maximale
#     MOYENNEE sur les graines (et non moyenne des quantiles)
#   - l'analyse des lignes acceptees retient confiance >= seuil
import sys, glob, os
import numpy as np

if len(sys.argv) < 2:
    print(__doc__); sys.exit(1)
dossier = sys.argv[1].rstrip('/')
quoi = sys.argv[2] if len(sys.argv) > 2 else 'c35_cal'

fichiers = sorted(glob.glob(f'{dossier}/oof_{quoi}_pli*_graine*.npz'))
if not fichiers:
    print(f"Aucun fichier oof_{quoi}_pli*_graine*.npz dans {dossier}"); sys.exit(1)

par_graine = {}
for f in fichiers:
    g = int(os.path.basename(f).split('graine')[1].split('.')[0])
    z = np.load(f)
    par_graine.setdefault(g, []).append((z['ligne'], z['proba'], z['y']))

A = {}
for g, parts in par_graine.items():
    lig = np.concatenate([p[0] for p in parts])
    pro = np.concatenate([p[1] for p in parts])
    y   = np.concatenate([p[2] for p in parts])
    o = np.argsort(lig)
    A[g] = (lig[o], pro[o], y[o])
graines = sorted(A)

# controle : memes lignes pour toutes les graines
ref = A[graines[0]][0]
for g in graines[1:]:
    assert np.array_equal(A[g][0], ref), f"graine {g} : lignes differentes"
n = len(ref)

# indice de la classe EVITER : deduit de son effectif, le plus petit apres SURVEILLER.
# Effectifs attendus (developpement) : STANDARD >> ADAPTER_DOSE > EVITER > SURVEILLER
y0 = A[graines[0]][2]
eff = {c: int((y0 == c).sum()) for c in range(A[graines[0]][1].shape[1])}
ordre = sorted(eff, key=lambda c: -eff[c])   # du plus frequent au moins frequent
i_eviter = ordre[2]                           # 3e par effectif = EVITER
print(f"dossier      : {dossier}   bras : {quoi}")
print(f"graines      : {graines}")
print(f"lignes       : {n}")
print(f"effectifs par classe (indice: n) : {eff}")
print(f"indice retenu pour EVITER : {i_eviter}  (n = {eff[i_eviter]})")
print()

def auroc(scores, positifs):
    # AUROC par rangs, egalites comptees pour une demi-unite (formule du memoire)
    s = np.asarray(scores, float); p = np.asarray(positifs, bool)
    r = np.empty(len(s)); o = np.argsort(s, kind='mergesort')
    sv = s[o]; i = 0
    while i < len(sv):
        j = i
        while j + 1 < len(sv) and sv[j+1] == sv[i]: j += 1
        r[o[i:j+1]] = (i + j) / 2.0 + 1
        i = j + 1
    np_, nn = p.sum(), (~p).sum()
    return (r[p].sum() - np_*(np_+1)/2.0) / (np_*nn)

SEUILS = [0.70, 0.90, 0.95, 0.99, 0.9965]
agg = {s: {'couv': [], 'exact': [], 'err': [], 'evit': [], 'ecart': []} for s in SEUILS}
aurocs, p1, p10, nerr, nevit, nfaux = [], [], [], [], [], []

for g in graines:
    _, pro, y = A[g]
    conf = pro.max(1); pred = pro.argmax(1)
    bon = (pred == y)
    aurocs.append(auroc(conf, bon))
    k1, k10 = max(1, round(0.01*n)), max(1, round(0.10*n))
    o = np.argsort(conf, kind='mergesort')
    tot_err = (~bon).sum()
    p1.append((~bon[o[:k1]]).sum() / tot_err)
    p10.append((~bon[o[:k10]]).sum() / tot_err)
    nerr.append(tot_err)
    nevit.append(((y == i_eviter) & (pred != i_eviter)).sum())
    nfaux.append(((pred == i_eviter) & (y != i_eviter)).sum())
    for s in SEUILS:
        acc = conf >= s
        agg[s]['couv'].append(acc.mean())
        agg[s]['exact'].append(bon[acc].mean())
        agg[s]['err'].append((~bon[acc]).sum())
        agg[s]['evit'].append(((y == i_eviter) & (pred != i_eviter) & acc).sum())
        agg[s]['ecart'].append((~acc).sum())

m = lambda v: float(np.mean(v)); sd = lambda v: float(np.std(v, ddof=1))
print(f"erreurs totales          : {m(nerr):.1f}")
print(f"EVITER manques           : {m(nevit):.1f}  sur {eff[i_eviter]}  ({100*m(nevit)/eff[i_eviter]:.3f} %)")
print(f"faux EVITER              : {m(nfaux):.1f}")
print(f"AUROC de la confiance    : {m(aurocs):.4f}  (ecart-type {sd(aurocs):.4f})")
print(f"erreurs dans le 1er centile  : {100*m(p1):.1f} %   ({max(1, round(0.01*n))} lignes)")
print(f"erreurs dans le 1er decile   : {100*m(p10):.1f} %")
print()
print("Tableau de couverture-risque (moyennes sur les graines)")
print(f"{'seuil':>8} | {'couverture':>10} | {'exact. selective':>16} | {'erreurs rest.':>13} | {'EVITER acceptes':>15} | {'ecartees':>9}")
for s in SEUILS:
    a = agg[s]
    print(f"{s:>8} | {m(a['couv']):>10.5f} | {m(a['exact']):>16.5f} | {m(a['err']):>13.1f} | {m(a['evit']):>15.1f} | {m(a['ecart']):>9.1f}")
print()
# Seuils du tableau 4.1 : quantiles de la probabilite maximale MOYENNEE sur les graines
pm = np.mean([A[g][1] for g in graines], axis=0)
cm = pm.max(1)
print("Seuils d'abstention (quantiles de la probabilite maximale moyennee sur les graines)")
for q in (0.005, 0.01, 0.02, 0.05):
    print(f"  part ecartee {100*q:>4.1f} %  ->  seuil {np.quantile(cm, q):.4f}")
