#!/usr/bin/env python3
"""
verif_independante_comparaison_v1.py (7 nov. 2026) : RECALCUL INDÉPENDANT de la comparaison DL / XGBoost / forêt aléatoire. LECTURE SEULE : aucun modèle entraîné,
aucun fichier du protocole modifié, ensemble final (138 profils) NON lu (seuls ses identifiants servent à vérifier qu'aucune de ses lignes n'est dans les prédictions).
N'importe AUCUN module du projet (ni protocole_commun, ni comparaison_equitable) : relit les .npz de prédictions hors-pli et le CSV du corpus, avec son propre code
(pandas, numpy, scikit-learn). Objectif : voir si une erreur de code commune aux scripts du projet aurait pu fausser la comparaison.
Contrôles : (1) lignes/étiquettes identiques pour les 3 bras et égales à celles du corpus ; (2) aucune ligne de l'ensemble final ; (3) plis recalculés (StratifiedGroupKFold, 5, graine 42)
et identiques à ceux des fichiers ; (4) aucun profil dans deux plis ; (5) probabilités valides (somme 1) ; (6) nombre d'égalités exactes au sommet des probabilités ;
(7) F1 macro recalculé avec scikit-learn, par graine puis moyenne ; (8) F1 macro par pli externe (régularité de l'ordre entre plis) ; (9) bootstrap par profil refait avec une AUTRE graine
et plus de rééchantillonnages (5 000) ; (10) rapport à comparer aux chiffres de results/log_comparaison_equitable_v14_v2.txt.
Usage (depuis scripts/) :
  python3 verif_independante_comparaison_v1.py --dl ../results/dl_imbrique_v14_equitable:choisie_cal --xgb ../results/eval_arbres_v14_xgb:choisie_cal --rf ../results/eval_arbres_v14_rf:choisie_cal
"""
import argparse, glob, os
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedGroupKFold

OK = []


def controle(nom, cond, detail=''):
    OK.append(bool(cond)); print('  [%s] %s %s' % ('OK' if cond else 'ECHEC', nom, detail))


def charger_bras(spec):
    dos, quoi = spec.rsplit(':', 1)
    fich = sorted(glob.glob(os.path.join(dos, 'oof_%s_pli*_graine*.npz' % quoi)))
    assert fich, 'aucun fichier dans ' + dos
    plis = sorted({int(f.split('_pli')[1].split('_')[0]) for f in fich}); graines = sorted({int(f.split('graine')[1].split('.')[0]) for f in fich})
    assert plis == [1, 2, 3, 4, 5] and len(fich) == len(plis) * len(graines), 'fichiers incomplets dans ' + dos
    out = {}
    for s in graines:
        for k in plis:
            z = np.load(os.path.join(dos, 'oof_%s_pli%d_graine%d.npz' % (quoi, k, s)))
            out[(k, s)] = (z['ligne'].astype(np.int64), z['y'].astype(np.int64), z['proba'].astype(np.float64))
    return out, plis, graines


def f1_depuis_confusions(C):
    """C (..., K, K) vrai x prédit -> F1 macro sur les K classes (classe sans vrai ni prédit = 0, comme sklearn avec labels fixés et zero_division=0)."""
    tp = np.einsum('...kk->...k', C).astype(float); fp = C.sum(-2) - tp; fn = C.sum(-1) - tp
    den = 2 * tp + fp + fn; f1 = np.where(den > 0, 2 * tp / np.maximum(den, 1), 0.0); return f1.mean(-1)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data', default='../data/corpus_v14/phenotype_drug_dataset_v14.csv'); ap.add_argument('--final', default='../data/profils_ensemble_final_v1.txt')
    ap.add_argument('--B', type=int, default=5000); ap.add_argument('--graine_bootstrap', type=int, default=7)
    for k in ('dl', 'xgb', 'rf'): ap.add_argument('--' + k, required=True, help='dossier:quoi')
    ap.add_argument('--sortie', default=None, help='dossier où écrire les CSV (facultatif)')
    a = ap.parse_args()
    df = pd.read_csv(a.data, usecols=['drug', 'action', 'sample_id', 'family_id'])
    classes = sorted(df.action.unique()); K = len(classes); cidx = {c: i for i, c in enumerate(classes)}; y_corpus = df.action.map(cidx).values; groupes = df.family_id.values
    ids = {l.strip() for l in open(a.final) if l.strip() and not l.startswith('#')}; fam_final = {'FAM_' + i for i in ids}
    est_final = np.isin(groupes, list(fam_final)); reste = np.where(~est_final)[0]
    print('corpus : %d lignes, %d profils ; ensemble final : %d profils (%d lignes) ; développement : %d lignes ; classes : %s' % (len(df), len(set(groupes)), len(fam_final), est_final.sum(), len(reste), classes))
    skf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    plis_recalcules = {k + 1: reste[b] for k, (_, b) in enumerate(skf.split(reste, y_corpus[reste], groupes[reste]))}
    bras = {'DL': a.dl, 'XGBoost': a.xgb, 'Forêt aléatoire': a.rf}; D = {}
    for nom, spec in bras.items(): D[nom] = charger_bras(spec)
    print('\nCONTRÔLES D\'INTÉGRITÉ')
    for nom, (out, plis, graines) in D.items():
        print(' ' + nom, '(graines %s)' % graines)
        lig_tot = np.concatenate([out[(k, graines[0])][0] for k in plis])
        controle('toutes les lignes de développement présentes une fois', len(lig_tot) == len(reste) and set(lig_tot) == set(reste))
        controle('aucune ligne de l\'ensemble final', not est_final[lig_tot].any())
        ok_y = all((out[key][1] == y_corpus[out[key][0]]).all() for key in out); controle('étiquettes des fichiers = étiquettes du corpus (toutes graines, tous plis)', ok_y)
        controle('plis des fichiers = plis recalculés indépendamment', all(set(out[(k, graines[0])][0]) == set(plis_recalcules[k]) for k in plis))
        controle('mêmes lignes de test pour toutes les graines', all((np.sort(out[(k, s)][0]) == np.sort(out[(k, graines[0])][0])).all() for k in plis for s in graines))
        sommes = np.concatenate([out[key][2].sum(1) for key in out]); controle('probabilités : somme par ligne = 1 (tolérance 1e-3)', np.abs(sommes - 1).max() < 1e-3, '(écart max %.2e)' % np.abs(sommes - 1).max())
        P = np.concatenate([out[(k, graines[0])][2] for k in plis]); top2 = np.sort(P, 1)[:, -2:]; controle('lignes avec égalité exacte des deux plus grandes probabilités (graine 0) : information', True, '%d' % int((top2[:, 0] == top2[:, 1]).sum()))
    pf = [set(groupes[plis_recalcules[k]]) for k in plis_recalcules]
    controle('aucun profil dans deux plis de test', all(not (pf[i] & pf[j]) for i in range(5) for j in range(i + 1, 5)))
    lignes0 = {n: np.concatenate([D[n][0][(k, D[n][2][0])][0] for k in D[n][1]]) for n in D}
    controle('mêmes lignes (même ordre par pli) pour les trois bras', all((lignes0[n] == lignes0['DL']).all() for n in D))
    # tableaux communs, ordre des lignes = ordre DL (plis 1..5, ordre du fichier)
    lig = lignes0['DL']; y = y_corpus[lig]; prof = pd.factorize(groupes[lig])[0]; nf = prof.max() + 1; pli_de = np.concatenate([[k] * len(D['DL'][0][(k, 0)][0]) for k in D['DL'][1]])
    pred = {}
    for n, (out, plis, graines) in D.items():
        pred[n] = []
        for s in graines:
            P = np.concatenate([out[(k, s)][2] for k in plis]); pred[n].append(P.argmax(1))
            assert (np.concatenate([out[(k, s)][0] for k in plis]) == lig).all()
    print('\nRECALCUL DU F1 MACRO (scikit-learn, labels = les %d classes ; moyenne des 5 graines)' % K)
    res = []
    for n in D:
        f1s = [f1_score(y, p, labels=list(range(K)), average='macro', zero_division=0) for p in pred[n]]
        f1_plis = [np.mean([f1_score(y[pli_de == k], p[pli_de == k], labels=list(range(K)), average='macro', zero_division=0) for p in pred[n]]) for k in range(1, 6)]
        ev = cidx['EVITER']; manq = [int(((y == ev) & (p != ev)).sum()) for p in pred[n]]; err = [int((p != y).sum()) for p in pred[n]]
        res.append(dict(modele=n, f1_macro_moy=round(float(np.mean(f1s)), 5), sd_graines=round(float(np.std(f1s)), 6), EVITER_manques_moy=round(float(np.mean(manq)), 1), erreurs_moy=round(float(np.mean(err)), 1), **{'pli%d' % k: round(float(v), 5) for k, v in zip(range(1, 6), f1_plis)}))
    R = pd.DataFrame(res); print(R.to_string(index=False))
    print('\nF1 macro par pli externe : classement des 3 bras pli par pli')
    for k in range(1, 6):
        v = {r['modele']: r['pli%d' % k] for r in res}; print('  pli %d : ' % k + ' > '.join(sorted(v, key=v.get, reverse=True)))
    # bootstrap par profil (graine et B différents de ceux du projet)
    rng = np.random.RandomState(a.graine_bootstrap); W = rng.multinomial(nf, np.ones(nf) / nf, size=a.B).astype(np.float64)
    def conf_par_profil(p): c = np.bincount(prof * K * K + y * K + p, minlength=nf * K * K).reshape(nf, K, K); return c
    CF = {n: [conf_par_profil(p) for p in pred[n]] for n in D}
    def boot(n): return np.mean([f1_depuis_confusions(np.tensordot(W, c, axes=(1, 0))) for c in CF[n]], 0)
    point = {n: np.mean([f1_depuis_confusions(c.sum(0)) for c in CF[n]]) for n in D}; BS = {n: boot(n) for n in D}
    print('\nBOOTSTRAP PAR PROFIL (%d rééchantillonnages, graine %d ; le projet : 2 000, graine 42) — F1 macro, moyenne des graines' % (a.B, a.graine_bootstrap))
    for n in D: lo, hi = np.percentile(BS[n], [2.5, 97.5]); print('  %-16s %.5f [%.5f ; %.5f]' % (n, point[n], lo, hi))
    noms = list(D); diffs = []
    for i, x in enumerate(noms):
        for y_ in noms[i + 1:]:
            d = BS[x] - BS[y_]; lo, hi = np.percentile(d, [2.5, 97.5]); dp = point[x] - point[y_]
            lect = '%s supérieur' % x if lo > 0 else '%s supérieur' % y_ if hi < 0 else 'non tranché'
            pr = ' (pratique, marge 0,001 : %s)' % (x if lo > 0.001 else y_) if (lo > 0.001 or hi < -0.001) else ' (pratique : non atteinte)'
            print('  %s - %s : %+.5f [%+.5f ; %+.5f] -> %s%s' % (x, y_, dp, lo, hi, lect, pr)); diffs.append(dict(comparaison='%s - %s' % (x, y_), difference=round(float(dp), 6), ic_bas=round(float(lo), 6), ic_haut=round(float(hi), 6), lecture=lect))
    print('\nBILAN : %d contrôles, %d échec(s).' % (len(OK), OK.count(False)))
    print('À comparer aux chiffres de results/log_comparaison_equitable_v14_v2.txt (statistique principale) : DL 0,99676 ; XGBoost 0,99941 ; RF 0,99333 ; différences DL-XGB -0,00265, DL-RF +0,00343, XGB-RF +0,00608.')
    if a.sortie:
        os.makedirs(a.sortie, exist_ok=True); R.to_csv(os.path.join(a.sortie, 'verif_independante_f1.csv'), index=False); pd.DataFrame(diffs).to_csv(os.path.join(a.sortie, 'verif_independante_differences.csv'), index=False)


if __name__ == '__main__':
    main()
