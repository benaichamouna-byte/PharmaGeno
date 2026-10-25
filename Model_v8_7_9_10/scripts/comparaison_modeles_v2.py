#!/usr/bin/env python3
"""
comparaison_modeles_v2.py : comparaison appariée du DL « profil » (v2) avec XGBoost et la forêt aléatoire, sur le corpus v8.

corpus = le tableau de données de lignes (profil du patient x médicament -> action) sur lequel les modèles sont entraînés et testés.
Ici : corpus v8, mêmes lignes de test, mêmes plis (protocole_commun_v9, StratifiedGroupKFold groupé par famille, graine 42), mêmes 33 variables génétiques.
L'ENSEMBLE FINAL (138 familles) n'est PAS utilisé : le script vérifie qu'aucune de ses lignes n'est dans les prédictions hors-pli.

Aucun modèle n'est entraîné ici. Entrées (produites par train_dl_profil_v2.py et train_arbres_v9.py) :
  results/dl_profil_v2/oof_moyenne_graines.npz et resultats_par_graine_et_pli.csv   (DL : 5 graines x 5 plis ; prédictions hors-pli = moyenne des 5 graines)
  results/arbres_v9_xgb/arbres_v9_xgb_fp_oof.npz et ..._resultats_par_pli.csv       (XGBoost : une exécution par pli)
  results/arbres_v9_rf/arbres_v9_rf_fp_oof.npz  et ..._resultats_par_pli.csv        (forêt aléatoire : une exécution par pli)

Statistiques
  1. Intervalles à 95 % par BOOTSTRAP SUR LES FAMILLES (Field & Welsh 2007, J. R. Stat. Soc. B 69:369-390), les mêmes familles tirées pour tous les modèles
     (comparaison appariée), 2 000 rééchantillonnages, graine 42. Les différences DL moins modèle ont leur propre intervalle.
  2. Test t rééchantillonné corrigé de Nadeau & Bengio (2003, Machine Learning 52:239-281) sur les 5 plis (différence des F1 macro par pli ; rapport test/apprentissage = 1/4).
     Avec 5 plis la puissance est faible : le résultat est indicatif.
  3. Test de McNemar exact (Dietterich 1998, Neural Computation 10:1895-1923) sur les prédictions hors-pli. Il ignore la corrélation entre lignes d'une même famille :
     la valeur de p est donnée à titre indicatif ; le bootstrap par famille est le critère principal.
  Limite à connaître : les prédictions hors-pli du DL sont la moyenne de 5 graines (un ensemble de 5 réseaux), celles des arbres viennent d'une seule exécution par pli.
  Le DL est donc légèrement favorisé dans la comparaison ligne à ligne ; les moyennes par pli (sans moyenne de graines) sont aussi données.
  Référence triviale : « toujours STANDARD » (aucun profil lu).

Usage (depuis le dossier scripts/) :
  python3 comparaison_modeles_v2.py --data ../data/corpus_v8/phenotype_drug_dataset_v8.csv --fp <drug_fingerprints_v2.pkl> --res ../results --out ../results/comparaison_modeles_v2
"""
import argparse, json, os
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import protocole_commun_v9 as pc
import figures_modele_v2 as fg

B = 2000
MESURES = [('f1_macro', 'F1 macro'), ('CER_strict', 'Cas « à éviter » manqués'), ('precision_EVITER', 'Précision « à éviter »'), ('ECE', 'ECE')]
COULEURS = {'DL profil v2': fg.BLEU, 'XGBoost': fg.ORANGE, 'Forêt aléatoire': '#1baf7a', 'Toujours STANDARD': '#9b9a95'}


def charger_oof(path, lig_ref, y_ref):
    z = np.load(path, allow_pickle=True); lig = z['ligne']; P = z['proba'].astype(np.float64); y = z['y']
    o = np.argsort(lig); pos = np.searchsorted(lig[o], lig_ref)                      # remet les lignes dans l'ordre du fichier du DL
    assert len(lig) == len(lig_ref) and (lig[o][pos] == lig_ref).all(), 'lignes différentes de celles du DL : ' + path
    P, y = P[o][pos], y[o][pos]
    assert (y == y_ref).all(), 'étiquettes différentes de celles du DL : ' + path
    return P


def nadeau_bengio(d, rapport=0.25):
    k = len(d); m = d.mean(); v = d.var(ddof=1)
    if v == 0:
        return float('nan'), float('nan')
    t = m / np.sqrt((1.0 / k + rapport) * v); p = 2 * stats.t.sf(abs(t), k - 1)
    return float(t), float(p)


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'fp', 'res', 'out'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); fg.style()
    d = pc.charger(a.data, a.fp); df, y_all, classes, groups = d['df'], d['y'], d['classes'], d['groups']; K = len(classes); ev = classes.index('EVITER'); st = classes.index('STANDARD')
    final, folds = pc.decouper(groups, y_all)
    z = np.load(os.path.join(a.res, 'dl_profil_v2', 'oof_moyenne_graines.npz')); lig, y = z['ligne'], z['y']      # ordre du fichier du DL (même ordre que figures_modele_v2.py : mêmes rééchantillonnages)
    assert not (set(lig) & set(final)), "des lignes de l'ensemble final sont dans les prédictions hors-pli"
    assert (y_all[lig] == y).all()
    modeles = {'DL profil v2': z['proba'].astype(np.float64)}
    chemins = {'XGBoost': ('arbres_v9_xgb', 'arbres_v9_xgb_fp'), 'Forêt aléatoire': ('arbres_v9_rf', 'arbres_v9_rf_fp')}
    par_pli = {'DL profil v2': pd.read_csv(os.path.join(a.res, 'dl_profil_v2', 'resultats_par_graine_et_pli.csv')).groupby('pli')[[m for m, _ in MESURES]].mean()}
    for nom, (dossier, tag) in chemins.items():
        f = os.path.join(a.res, dossier, tag + '_oof.npz')
        if os.path.exists(f):
            modeles[nom] = charger_oof(f, lig, y); par_pli[nom] = pd.read_csv(os.path.join(a.res, dossier, tag + '_resultats_par_pli.csv')).set_index('pli')[[m for m, _ in MESURES]]
        else:
            print('absent (ignoré) :', f)
    triv = np.zeros((len(y), K)); triv[:, st] = 1.0; modeles['Toujours STANDARD'] = triv
    fam, noms_fam = pd.factorize(groups[lig]); F = len(noms_fam); print('lignes hors-pli : %d | familles : %d | modèles : %s' % (len(lig), F, list(modeles)))
    S = {n: fg.sommes_famille(np.clip(P, 1e-6, 1.0) if n == 'Toujours STANDARD' else P, y, fam, F, K) for n, P in modeles.items()}
    est = {n: {k: float(v) for k, v in fg.calcul(C.sum(0), E.sum(0), L.sum(), ev, classes).items()} for n, (C, E, L) in S.items()}
    rng = np.random.RandomState(42); boot = {n: {} for n in S}
    for s in range(0, B, 200):
        idx = rng.randint(0, F, (min(200, B - s), F))
        for n, (C, E, L) in S.items():
            for k, v in fg.calcul(C[idx].sum(1), E[idx].sum(1), L[idx].sum(1), ev, classes).items(): boot[n].setdefault(k, []).append(v)
    boot = {n: {k: np.concatenate(v) for k, v in b.items()} for n, b in boot.items()}
    lignes = []
    for n in modeles:
        for k, t in MESURES:
            lo, hi = np.percentile(boot[n][k], [2.5, 97.5])
            lignes.append(dict(modele=n, mesure=k, estimation=round(est[n][k], 5), ic95_bas=round(float(lo), 5), ic95_haut=round(float(hi), 5)))
    pd.DataFrame(lignes).to_csv(os.path.join(a.out, 'comparaison_modeles_v2.csv'), index=False)
    # différences appariées DL - autre modèle, tests
    diffs = []; pred_dl = modeles['DL profil v2'].argmax(1)
    for n in modeles:
        if n in ('DL profil v2', 'Toujours STANDARD'): continue
        for k, t in MESURES:
            dd = boot['DL profil v2'][k] - boot[n][k]; lo, hi = np.percentile(dd, [2.5, 97.5])
            diffs.append(dict(comparaison='DL profil v2 - ' + n, mesure=k, difference=round(est['DL profil v2'][k] - est[n][k], 5), ic95_bas=round(float(lo), 5), ic95_haut=round(float(hi), 5), ic_exclut_zero=bool(lo > 0 or hi < 0)))
        pr = modeles[n].argmax(1); b = int(((pred_dl == y) & (pr != y)).sum()); c = int(((pred_dl != y) & (pr == y)).sum())
        p_mc = float(stats.binomtest(min(b, c), b + c, 0.5).pvalue) if b + c > 0 else float('nan')
        dpli = (par_pli['DL profil v2']['f1_macro'] - par_pli[n]['f1_macro']).values; t, p = nadeau_bengio(dpli)
        diffs.append(dict(comparaison='DL profil v2 - ' + n, mesure='McNemar exact (lignes) : DL juste & autre faux / DL faux & autre juste', difference=np.nan, ic95_bas=b, ic95_haut=c, ic_exclut_zero=np.nan, p_indicatif=round(p_mc, 6)))
        diffs.append(dict(comparaison='DL profil v2 - ' + n, mesure='Nadeau-Bengio (F1 macro par pli) : t', difference=round(t, 4), p_indicatif=round(p, 4), details='différences par pli : ' + ' ; '.join('%.4f' % x for x in dpli)))
    pd.DataFrame(diffs).to_csv(os.path.join(a.out, 'differences_appariees_v2.csv'), index=False)
    # par pli (sans moyenne de graines) pour les trois modèles
    pp = pd.concat({n: t for n, t in par_pli.items()}, names=['modele']).reset_index(); pp.to_csv(os.path.join(a.out, 'comparaison_par_pli_v2.csv'), index=False)
    # figure
    vis = [n for n in modeles if n != 'Toujours STANDARD']
    lignes_fig = [vis, [n for n in vis if n in ('DL profil v2', 'XGBoost')]]      # ligne 1 : tous les modèles ; ligne 2 : zoom sur le DL et XGBoost
    fig, axs = plt.subplots(2, 4, figsize=(14, 6.4))
    for r, groupe in enumerate(lignes_fig):
        for c, (k, t) in enumerate(MESURES):
            ax = axs[r, c]
            for i, n in enumerate(groupe):
                lo, hi = np.percentile(boot[n][k], [2.5, 97.5]); y0 = len(groupe) - 1 - i
                ax.hlines(y0, lo, hi, color=COULEURS[n], lw=2.2, alpha=0.75); ax.plot(est[n][k], y0, 'o', color=COULEURS[n], ms=8, mec='white', mew=1.5, zorder=3)
            ax.set_yticks(range(len(groupe))); ax.set_yticklabels(list(reversed(groupe)) if c == 0 else [], fontsize=9); ax.set_ylim(-0.6, len(groupe) - 0.4)
            ax.set_title(t + ('' if r == 0 else ' (zoom)'), loc='left', fontsize=9.5, fontweight='bold'); ax.grid(axis='y', visible=False)
            ax.tick_params(axis='x', labelsize=8); ax.locator_params(axis='x', nbins=4)
    fig.text(0.01, 0.01, "Point = estimation sur les prédictions hors-pli ; trait = intervalle à 95 % par bootstrap sur les familles (mêmes familles pour tous les modèles). "
             "DL : moyenne de 5 graines ; arbres : une exécution par pli. Ensemble final non lu.", fontsize=8, color=fg.ENCRE2)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(os.path.join(a.out, 'fig6_comparaison_modeles.png')); plt.close(fig)
    print(pd.DataFrame(lignes).to_string(index=False)); print(pd.DataFrame(diffs).to_string(index=False)); print('Fichiers écrits dans', a.out)


if __name__ == '__main__':
    main()
