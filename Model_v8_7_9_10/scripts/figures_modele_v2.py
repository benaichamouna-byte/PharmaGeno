#!/usr/bin/env python3
"""
figures_modele_v2.py : figures et statistiques du DL actuel (corpus v8), SANS ré-entraîner aucun modèle.

corpus = le tableau de données de lignes (profil du patient x médicament -> action) sur lequel les modèles sont entraînés et testés.
Ici : corpus v8 (152 600 lignes ; 147 200 étiquetées après retrait des 4 médicaments sans empreinte).

Entrées (déjà produites par train_dl_profil_v2.py et train_dl_choix_v2.py) :
  results/dl_profil_v2/resultats_par_graine_et_pli.csv   : 5 graines x 5 plis
  results/dl_profil_v2/oof_moyenne_graines.npz           : prédictions hors-pli (probabilités moyennées sur les 5 graines)
  results/dl_choix_v2/resultats_par_graine_et_pli.csv    : 5 graines x 5 plis
  le corpus v8 et les empreintes (uniquement pour retrouver famille et médicament de chaque ligne ; protocole_commun_v9)

L'ENSEMBLE FINAL (138 familles, 14 731 lignes) n'est PAS utilisé : le script vérifie qu'aucune ligne finale n'est dans les prédictions hors-pli.

Statistiques
  - Intervalle de confiance à 95 % par BOOTSTRAP SUR LES FAMILLES (on tire des familles avec remise, jamais des lignes isolées,
    car les lignes d'une même famille sont corrélées ; Field & Welsh 2007, J. R. Stat. Soc. B 69:369-390). 2 000 rééchantillonnages, graine 42.
  - Les estimations « poolées » sont calculées sur les prédictions hors-pli moyennées sur 5 graines (un ensemble de 5 réseaux).
    Elles diffèrent donc légèrement des moyennes « 25 exécutions » (5 graines x 5 plis) du fichier CSV ; les deux sont écrites, avec leur nature.
  - Calibration : ECE à 15 intervalles (Guo et al. 2017, ICML), même définition que protocole_commun_v9.ece.

Usage (depuis le dossier scripts/) :
  python3 figures_modele_v2.py --data ../data/corpus_v8/phenotype_drug_dataset_v8.csv --fp <drug_fingerprints_v2.pkl> --res ../results --out ../results/figures_modele_v2
"""
import argparse, json, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import protocole_commun_v9 as pc

BLEU, ORANGE, ENCRE, ENCRE2, GRILLE = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#e6e5e1'
NB_BINS = 15
B = 2000


def style():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': '#9b9a95', 'axes.linewidth': 0.8,
                         'axes.labelcolor': ENCRE2, 'xtick.color': ENCRE2, 'ytick.color': ENCRE2, 'text.color': ENCRE,
                         'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRILLE,
                         'grid.linewidth': 0.6, 'axes.axisbelow': True, 'figure.dpi': 100, 'savefig.dpi': 200,
                         'savefig.facecolor': 'white', 'figure.facecolor': 'white', 'axes.facecolor': 'white'})


def fr(x, nd=4):
    return ('%.*f' % (nd, x)).replace('.', ',')


# ---------- statistiques par famille (sommes) ----------
def sommes_famille(P, y, fam, F, K):
    pred = P.argmax(1); conf = P.max(1); ok = (pred == y).astype(float)
    C = np.zeros((F, K, K)); np.add.at(C, (fam, y, pred), 1)
    b = np.clip(np.ceil(conf * NB_BINS).astype(int) - 1, 0, NB_BINS - 1)
    E = np.zeros((F, NB_BINS, 3)); np.add.at(E, (fam, b, 0), 1); np.add.at(E, (fam, b, 1), conf); np.add.at(E, (fam, b, 2), ok)
    ll = -np.log(np.clip(P[np.arange(len(y)), y], 1e-15, 1.0)); L = np.bincount(fam, weights=ll, minlength=F)
    return C, E, L


def calcul(C, E, L, ev, classes):
    tp = np.einsum('...ii->...i', C); rec = tp / np.maximum(C.sum(-1), 1); prec = tp / np.maximum(C.sum(-2), 1)
    f1 = np.where(prec + rec > 0, 2 * prec * rec / np.maximum(prec + rec, 1e-12), 0.0)
    n = C.sum((-1, -2)); cnt = E[..., 0]
    acc = E[..., 2] / np.maximum(cnt, 1); cf = E[..., 1] / np.maximum(cnt, 1)
    out = dict(f1_macro=f1.mean(-1), exactitude=tp.sum(-1) / n, CER_strict=1 - rec[..., ev], precision_EVITER=prec[..., ev],
               ECE=(cnt * np.abs(acc - cf)).sum(-1) / n, logloss=L / n)   # L = somme des log-pertes (scalaire ou une valeur par rééchantillonnage)
    for i, c in enumerate(classes):
        out['rappel_' + c] = rec[..., i]
    return out


# ---------- figures ----------
def fig_par_pli(R, Rc, out):
    panneaux = [(R, 'f1_macro', 'F1 macro', BLEU), (R, 'CER_strict', 'Cas « à éviter » manqués (proportion)', ORANGE),
                (R, 'ECE', 'Erreur de calibration (ECE)', BLEU), (Rc, 'ensemble_exact_informatifs', 'DL choix : ensemble exact', BLEU)]
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.6))
    for ax, (D, col, titre, coul) in zip(axs.ravel(), panneaux):
        g = D.groupby('pli')[col].agg(['mean', 'min', 'max']); plis = g.index.values
        ax.vlines(plis, g['min'], g['max'], color=coul, lw=1.4, alpha=0.55)
        ax.plot(plis, g['mean'], 'o', color=coul, ms=7, mec='white', mew=1.5, zorder=3)
        m = D[col].mean(); ax.axhline(m, color=ENCRE2, lw=1, ls=(0, (4, 3)))
        ax.set_title(titre, loc='left', fontsize=10.5, fontweight='bold'); ax.set_xticks(plis)
        ax.set_xlabel('Pli de validation croisée\npointillé : moyenne des 25 exécutions = ' + fr(m), fontsize=9)
        ax.set_xlim(0.5, 5.5)
    fig.text(0.01, 0.005, "Point = moyenne des 5 graines ; trait = min–max des 5 graines ; pointillé = moyenne des 25 exécutions (5 graines x 5 plis). "
             "Ensemble final non lu.", fontsize=8.2, color=ENCRE2, ha='left', va='bottom')
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(os.path.join(out, 'fig1_metriques_par_pli.png')); plt.close(fig)


def fig_ic(est, boot, out):
    noms = [('f1_macro', 'F1 macro'), ('CER_strict', 'Cas « à éviter » manqués'), ('precision_EVITER', 'Précision « à éviter »'),
            ('ECE', 'ECE'), ('exactitude', 'Exactitude')]
    fig, axs = plt.subplots(1, 5, figsize=(14, 3.2))
    for ax, (k, t) in zip(axs, noms):
        v = boot[k]; lo, hi = np.percentile(v, [2.5, 97.5])
        ax.hist(v, bins=40, color=BLEU, alpha=0.55, edgecolor='white', linewidth=0.4)
        ax.axvspan(lo, hi, color=BLEU, alpha=0.12, lw=0); ax.axvline(est[k], color=ENCRE, lw=1.2)
        ax.set_title(t, loc='left', fontsize=10, fontweight='bold'); ax.set_yticks([]); ax.grid(False); ax.spines['left'].set_visible(False)
        ax.set_xlabel('%s  [%s ; %s]' % (fr(est[k]), fr(lo), fr(hi)), fontsize=8.5)
        ax.tick_params(axis='x', labelsize=8); ax.locator_params(axis='x', nbins=4)
    fig.text(0.01, 0.01, "Distribution de 2 000 rééchantillonnages de FAMILLES ; trait noir = estimation ; zone = intervalle à 95 %. Prédictions hors-pli moyennées sur 5 graines.",
             fontsize=8.2, color=ENCRE2)
    fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig(os.path.join(out, 'fig2_intervalles_bootstrap_familles.png')); plt.close(fig)


def fig_calibration(E_tot, ece, ece_ic, out):
    cnt, sc, sa = E_tot[:, 0], E_tot[:, 1], E_tot[:, 2]
    edges = np.linspace(0, 1, NB_BINS + 1); mil = (edges[:-1] + edges[1:]) / 2
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={'width_ratios': [1.15, 1]})
    a1.plot([0.5, 1], [0.5, 1], color=ENCRE2, lw=1, ls=(0, (4, 3)), label='calibration parfaite')
    ok = cnt >= 30
    a1.plot((sc / np.maximum(cnt, 1))[ok], (sa / np.maximum(cnt, 1))[ok], '-o', color=BLEU, lw=1.6, ms=6, mec='white', mew=1.2, label='DL profil v2')
    a1.set_xlim(0.5, 1.0); a1.set_ylim(0.5, 1.02); a1.set_xlabel('Confiance moyenne du réseau'); a1.set_ylabel('Fréquence observée de la bonne classe')
    a1.set_title('Courbe de fiabilité', loc='left', fontsize=10.5, fontweight='bold'); a1.legend(frameon=False, loc='lower right', fontsize=9)
    a1.text(0.40, 0.30, 'ECE = %s\nIC 95 %% [%s ; %s]' % (fr(ece), fr(ece_ic[0]), fr(ece_ic[1])), transform=a1.transAxes, va='top', fontsize=9.5)
    nz = cnt > 0
    a2.bar(mil[nz], cnt[nz], width=1 / NB_BINS * 0.85, color=BLEU, alpha=0.6, edgecolor='none'); a2.set_yscale('log'); a2.set_xlim(0.2, 1.0)
    a2.set_xlabel('Confiance du réseau (15 intervalles)'); a2.set_ylabel('Nombre de lignes (échelle log)')
    a2.set_title('Où se placent les prédictions', loc='left', fontsize=10.5, fontweight='bold')
    fig.text(0.01, 0.005, 'Prédictions hors-pli (%d lignes), moyennées sur 5 graines. Points tracés pour les intervalles contenant au moins 30 lignes.' % int(cnt.sum()),
             fontsize=8.2, color=ENCRE2)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(os.path.join(out, 'fig3_calibration.png')); plt.close(fig)


NOMS_CLASSES = {'ADAPTER_DOSE': 'Adapter la dose', 'EVITER': 'À éviter', 'STANDARD': 'Standard', 'SURVEILLER': 'Surveiller'}


def fig_confusion(C, classes, out):
    lab = [NOMS_CLASSES.get(c, c) for c in classes]; pct = C / np.maximum(C.sum(1, keepdims=True), 1) * 100
    fig, ax = plt.subplots(figsize=(6.4, 5.4)); ax.grid(False)
    im = ax.imshow(pct, cmap='Blues', vmin=0, vmax=100)
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, '%s %%\n(n = %d)' % (fr(pct[i, j], 2).replace(',', ',') if pct[i, j] >= 0.005 or C[i, j] == 0 else '<0,01', C[i, j]),
                    ha='center', va='center', fontsize=9, color='white' if pct[i, j] > 55 else ENCRE)
    ax.set_xticks(range(len(classes))); ax.set_xticklabels(lab, rotation=20, ha='right'); ax.set_yticks(range(len(classes))); ax.set_yticklabels(lab)
    ax.set_xlabel('Action prédite par le DL'); ax.set_ylabel('Action donnée par les règles'); ax.spines[:].set_visible(False)
    ax.set_title('Matrice de confusion (en % de chaque action réelle)', loc='left', fontsize=10.5, fontweight='bold')
    fig.text(0.01, 0.005, 'Prédictions hors-pli moyennées sur 5 graines. Ensemble final non lu.', fontsize=8.2, color=ENCRE2)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(os.path.join(out, 'fig4_matrice_confusion.png')); plt.close(fig)


def fig_medicaments(T, n_total, out):
    top = T[T.erreurs > 0].sort_values(['erreurs', 'eviter_manques'], ascending=False).head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8.6, 0.38 * max(len(top), 4) + 1.7))
    autres = top.erreurs - top.eviter_manques
    ax.barh(top.medicament, top.eviter_manques, color=ORANGE, edgecolor='white', linewidth=1.5, height=0.62, label='« À éviter » manqué')
    ax.barh(top.medicament, autres, left=top.eviter_manques, color=BLEU, edgecolor='white', linewidth=1.5, height=0.62, label='Autre erreur')
    ax.set_xlabel("Nombre de lignes mal prédites (sur l'ensemble des plis de test)"); ax.grid(axis='y', visible=False)
    ax.set_title('Médicaments concernés par les erreurs (15 premiers)', loc='left', fontsize=10.5, fontweight='bold'); ax.legend(frameon=False, loc='lower right')
    nz = int((T.erreurs == 0).sum())
    fig.text(0.01, 0.005, '%d erreurs sur %d lignes ; %d médicaments sur %d sans aucune erreur. Prédictions hors-pli moyennées sur 5 graines.' %
             (int(T.erreurs.sum()), n_total, nz, len(T)), fontsize=8.2, color=ENCRE2)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(os.path.join(out, 'fig5_erreurs_par_medicament.png')); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'fp', 'res', 'out'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); style()
    d = pc.charger(a.data, a.fp); df, y_all, classes, groups = d['df'], d['y'], d['classes'], d['groups']; K = len(classes); ev = classes.index('EVITER')
    final, folds = pc.decouper(groups, y_all)
    z = np.load(os.path.join(a.res, 'dl_profil_v2', 'oof_moyenne_graines.npz')); lig, P, y = z['ligne'], z['proba'].astype(np.float64), z['y']
    assert not (set(lig) & set(final)), "des lignes de l'ensemble final sont dans les prédictions hors-pli"
    assert set(lig) == set(np.concatenate([te for _, te in folds])), 'les lignes hors-pli ne correspondent pas au découpage du protocole'
    assert (y_all[lig] == y).all(), 'les étiquettes du fichier hors-pli ne correspondent pas au corpus'
    fam, fam_noms = pd.factorize(groups[lig]); F = len(fam_noms); print('lignes hors-pli : %d | familles : %d | classes : %s' % (len(lig), F, classes))
    C, E, L = sommes_famille(P, y, fam, F, K)
    est = {k: float(v) for k, v in calcul(C.sum(0), E.sum(0), L.sum(), ev, classes).items()}
    rng = np.random.RandomState(42); boot = {}
    for s in range(0, B, 200):
        idx = rng.randint(0, F, (min(200, B - s), F)); r = calcul(C[idx].sum(1), E[idx].sum(1), L[idx].sum(1), ev, classes)
        for k, v in r.items(): boot.setdefault(k, []).append(v)
    boot = {k: np.concatenate(v) for k, v in boot.items()}
    R = pd.read_csv(os.path.join(a.res, 'dl_profil_v2', 'resultats_par_graine_et_pli.csv')); Rc = pd.read_csv(os.path.join(a.res, 'dl_choix_v2', 'resultats_par_graine_et_pli.csv'))
    lignes = []
    for k in est:
        lo, hi = np.percentile(boot[k], [2.5, 97.5]); m25 = float(R[k].mean()) if k in R else np.nan; sd25 = float(R[k].std(ddof=0)) if k in R else np.nan
        lignes.append(dict(mesure=k, estimation_poolee_hors_pli=round(est[k], 5), ic95_bas=round(float(lo), 5), ic95_haut=round(float(hi), 5),
                           moyenne_25_executions=round(m25, 5), ecart_type_25_executions=round(sd25, 5)))
    pd.DataFrame(lignes).to_csv(os.path.join(a.out, 'statistiques_modele_v2.csv'), index=False)
    cc = Rc['ensemble_exact_informatifs']; pd.DataFrame([dict(mesure='dl_choix_ensemble_exact', moyenne_25_executions=round(float(cc.mean()), 5),
          ecart_type_25_executions=round(float(cc.std(ddof=0)), 5), min=round(float(cc.min()), 5), max=round(float(cc.max()), 5),
          reference_sans_profil=round(float(Rc['defaut_ensemble_exact_informatifs'].mean()), 5))]).to_csv(os.path.join(a.out, 'statistiques_dl_choix_v2.csv'), index=False)
    pd.DataFrame(C.sum(0).astype(int), index=classes, columns=classes).to_csv(os.path.join(a.out, 'matrice_confusion_v2.csv'))
    pred = P.argmax(1); med = df.drug.values[lig]
    T = pd.DataFrame(dict(medicament=med, lignes=1, erreurs=(pred != y).astype(int), eviter_manques=((y == ev) & (pred != ev)).astype(int), eviter_vrais=(y == ev).astype(int))).groupby('medicament').sum().reset_index()
    T.sort_values(['erreurs', 'eviter_manques'], ascending=False).to_csv(os.path.join(a.out, 'erreurs_par_medicament_v2.csv'), index=False)
    fig_par_pli(R, Rc, a.out); fig_ic(est, boot, a.out)
    fig_calibration(E.sum(0), est['ECE'], np.percentile(boot['ECE'], [2.5, 97.5]), a.out)
    fig_confusion(C.sum(0), classes, a.out); fig_medicaments(T, len(lig), a.out)
    print(pd.DataFrame(lignes).to_string(index=False)); print('Fichiers écrits dans', a.out)


if __name__ == '__main__':
    main()
