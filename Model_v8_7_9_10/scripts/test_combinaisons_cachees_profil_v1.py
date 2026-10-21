#!/usr/bin/env python3
"""
test_combinaisons_cachees_profil_v1.py : le DL « profil -> médicaments » sait-il combiner deux gènes qu'il n'a JAMAIS vus ensemble ?

Correction d'une faille de test_combinaisons_retirees_dl_v1.py : dans l'ancien test, on cachait une combinaison pour UN médicament, mais la même combinaison de gènes restait visible à
l'entraînement sous les AUTRES médicaments (mesuré : 100 % des combinaisons cachées restaient visibles). Ici on cache le PROFIL : tous les patients portant la combinaison cachée
(et leurs familles) sont retirés de l'entraînement pour TOUS les médicaments. On teste ensuite les médicaments qui dépendent de ces deux gènes.
Les « lettres » (chaque valeur de gène prise seule) restent vues ailleurs ; seul le « mot » (la combinaison) est inconnu.
Mesures : exactitude sur les cases informatives (étiquette différente de la classe majoritaire du médicament à l'entraînement), séparées en : classe déjà vue à l'entraînement pour ce médicament / classe jamais vue
(dans ce dernier cas aucun modèle ne peut répondre : c'est un défaut de données, pas un défaut de combinaison). Référence : classe majoritaire ; une table de règles ne couvre pas une combinaison absente.
L'ensemble final (10 % des familles) n'est jamais lu. Même réglages que train_dl_profil_v1.py. Résultats rapportés tels quels, y compris négatifs.
Usage : python3 test_combinaisons_cachees_profil_v1.py --data ../data/phenotype_drug_dataset_v7.csv --fp <drug_fingerprints_v2.pkl> --domaine ../data/domaine_v8.json --out ../results/combinaisons_cachees_profil_v1 [--tirages 3] [--epochs 300]
"""
import argparse, json, os, time
import numpy as np, pandas as pd, torch
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
import protocole_commun_v8 as pc
from train_dl_profil_v1 import probas, entrainer


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'fp', 'domaine', 'out'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--tirages', type=int, default=3); ap.add_argument('--epochs', type=int, default=300); ap.add_argument('--fraction', type=float, default=0.25); ap.add_argument('--min_profils', type=int, default=8); ap.add_argument('--max_profils', type=int, default=60); ap.add_argument('--plafond', type=float, default=0.25, help='part maximale des profils cachés')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); torch.set_num_threads(max(1, os.cpu_count() or 1))
    d = pc.charger(a.data, a.fp); df, G, y, classes, groups, meds = d['df'], d['G'], d['y'], d['classes'], d['groups'], d['meds']
    K, M = len(classes), len(meds); ev = classes.index('EVITER'); dom = json.load(open(a.domaine, encoding='utf-8'))['medicaments']
    sid = df.sample_id.values; profils = pd.unique(sid); pidx = {s: i for i, s in enumerate(profils)}; pid = np.array([pidx[s] for s in sid])
    first = pd.Series(np.arange(len(df))).groupby(pid).first().values; X = G[first]; assert np.allclose(G, X[pid])
    Y = np.full((len(profils), M), -1, dtype=np.int64); Y[pid, d['drug_idx']] = y; fam = groups[first]; midx = {m: i for i, m in enumerate(meds)}
    final, _ = pc.decouper(groups, y); garde = np.setdiff1d(np.arange(len(profils)), np.unique(pid[final]))
    # valeurs de gènes par profil (NaN si non déterminé)
    def val(g):
        v = df[g].values[first].astype(float).copy()
        if g + '_manquant' in df.columns: v[df[g + '_manquant'].values[first] == 1] = np.nan
        return v
    paires = {}
    for m, v in dom.items():
        if len(v['genes']) == 2 and v['dans_modele'] and m in midx: paires.setdefault(tuple(v['genes']), []).append(m)
    print('paires de gènes et médicaments :', {'+'.join(k): v for k, v in paires.items()}, flush=True)
    lignes, par_med = [], []
    for t in range(a.tirages):
        t0 = time.time(); rng = np.random.RandomState(100 + t); cachees = {}; H = set()
        budget = int(a.plafond * len(garde)); liste_paires = list(paires.items()); rng.shuffle(liste_paires)
        for (g1, g2), meds_p in liste_paires:
            v1, v2 = val(g1), val(g2); ok = garde[~np.isnan(v1[garde]) & ~np.isnan(v2[garde])]
            comb = pd.Series(list(zip(v1[ok], v2[ok]))).value_counts()
            cands = [c for c, n in comb.items() if a.min_profils <= n <= a.max_profils]; rng.shuffle(cands)          # combinaisons ni trop rares ni trop courantes : on ne cache pas la moitié des patients
            cible = max(1, int(round(a.fraction * len(comb)))); restants = set(comb.index); pris = []
            for c in cands:
                if len(pris) >= cible: break
                autres = restants - {c}; n_c = int(comb[c])
                if len(H) + n_c > budget: continue
                if autres and all(any(o[j] == c[j] for o in autres) for j in range(2)):                                # chaque valeur reste vue dans une autre combinaison
                    pris.append(c); restants = autres; H.update(int(q) for q in ok if (v1[q], v2[q]) == c)
            cachees[(g1, g2)] = pris
        H = np.array(sorted(H)); fam_H = set(fam[H]); train_all = np.array([p for p in garde if fam[p] not in fam_H])
        assert not (set(train_all) & set(H)) and not (set(fam[train_all]) & set(fam_H)), 'fuite'
        # contrôle : aucune combinaison cachée n'est présente à l'entraînement
        presentes = 0
        for (g1, g2), pris in cachees.items():
            v1, v2 = val(g1), val(g2); tr_c = set(zip(v1[train_all], v2[train_all])); presentes += sum(c in tr_c for c in pris)
        assert presentes == 0, 'une combinaison cachée est encore présente à l\'entraînement'
        gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE); ai, vi = next(gss.split(train_all, groups=fam[train_all])); ptrn, pval = train_all[ai], train_all[vi]
        sc = StandardScaler().fit(X[ptrn]); S = lambda ix: sc.transform(X[ix]).astype(np.float32)
        cnt = np.bincount(Y[ptrn][Y[ptrn] >= 0], minlength=K).astype(float); w = np.sqrt(cnt.sum() / (K * np.maximum(cnt, 1))); w = w.copy(); w[ev] *= 2.0
        model, hist, bv = entrainer(S(ptrn), Y[ptrn], S(pval), Y[pval], K, w, pc.GRAINE + 500 + t, a.epochs)
        Ptest = probas(model, S(H)); Pval = probas(model, S(pval)); loc = {p: i for i, p in enumerate(H)}
        tot_cases = tot_inf = ok_inf = tot_inf_vue = ok_inf_vue = tot_inf_nv = tot_all = ok_all = 0; ev_reel = ev_det = 0
        for (g1, g2), pris in cachees.items():
            v1, v2 = val(g1), val(g2)
            for m in paires[(g1, g2)]:
                j = midx[m]; ym = Y[ptrn][:, j]; ym = ym[ym >= 0]
                if len(ym) == 0: continue
                maj = int(np.bincount(ym, minlength=K).argmax()); vues = set(np.unique(ym).tolist())
                ps = np.array([p for p in H if (v1[p], v2[p]) in pris and Y[p, j] >= 0])
                if len(ps) == 0: continue
                yt = Y[ps, j]; pr = Ptest[[loc[p] for p in ps], j].argmax(1); inf = yt != maj; vue = np.array([c in vues for c in yt])
                ev_reel += int((yt == ev).sum()); ev_det += int(((yt == ev) & (pr == ev)).sum())
                tot_all += len(ps); ok_all += int((pr == yt).sum()); tot_inf += int(inf.sum()); ok_inf += int((pr[inf] == yt[inf]).sum())
                tot_inf_vue += int((inf & vue).sum()); ok_inf_vue += int((pr[inf & vue] == yt[inf & vue]).sum()); tot_inf_nv += int((inf & ~vue).sum())
                par_med.append(dict(tirage=t + 1, medicament=m, genes='+'.join((g1, g2)), profils_test=len(ps), classe_majoritaire=classes[maj], informatives=int(inf.sum()),
                                    DL_exactitude=round(float((pr == yt).mean()), 4), majoritaire_exactitude=round(float((yt == maj).mean()), 4),
                                    DL_exactitude_informatives=round(float((pr[inf] == yt[inf]).mean()), 4) if inf.any() else None,
                                    informatives_classe_vue=int((inf & vue).sum()), DL_exactitude_informatives_classe_vue=round(float((pr[inf & vue] == yt[inf & vue]).mean()), 4) if (inf & vue).any() else None,
                                    informatives_classe_jamais_vue=int((inf & ~vue).sum())))
        # référence : mêmes médicaments, combinaisons VUES (profils de validation interne, familles inconnues)
        vt = vv = 0
        for (g1, g2), pris in cachees.items():
            for m in paires[(g1, g2)]:
                j = midx[m]; ps = pval[Y[pval, j] >= 0]
                if len(ps): vt += len(ps); vv += int((Pval[[list(pval).index(p) for p in ps], j].argmax(1) == Y[ps, j]).sum())
        r = dict(tirage=t + 1, paires=len(cachees), combinaisons_cachees=int(sum(len(v) for v in cachees.values())), profils_caches=int(len(H)), familles_retirees=len(fam_H), profils_entrainement=int(len(train_all)),
                 cases_test=tot_all, cases_informatives=tot_inf, DL_exactitude_informatives=round(ok_inf / tot_inf, 4) if tot_inf else None,
                 cases_informatives_classe_vue=tot_inf_vue, DL_exactitude_informatives_classe_vue=round(ok_inf_vue / tot_inf_vue, 4) if tot_inf_vue else None, cases_informatives_classe_jamais_vue=tot_inf_nv,
                 DL_exactitude_toutes_cases=round(ok_all / tot_all, 4) if tot_all else None, EVITER_reel=ev_reel, EVITER_detectes=ev_det, DL_exactitude_combinaisons_vues_memes_medicaments=round(vv / vt, 4) if vt else None,
                 reference_majoritaire_informatives=0.0, table_de_regles_couverture=0.0, combinaisons_cachees_presentes_a_l_entrainement=int(presentes), epoques=len(hist), secondes=round(time.time() - t0))
        lignes.append(r); print(r, flush=True)
    R = pd.DataFrame(lignes); R.to_csv(os.path.join(a.out, 'resume_par_tirage.csv'), index=False); pd.DataFrame(par_med).to_csv(os.path.join(a.out, 'par_medicament.csv'), index=False)
    resume = dict(tirages=len(R), DL_exactitude_informatives_classe_vue_moy=float(R.DL_exactitude_informatives_classe_vue.astype(float).mean()), DL_exactitude_informatives_moy=float(R.DL_exactitude_informatives.astype(float).mean()),
                  DL_exactitude_combinaisons_vues_moy=float(R.DL_exactitude_combinaisons_vues_memes_medicaments.astype(float).mean()), combinaisons_cachees_presentes_a_l_entrainement_max=int(R.combinaisons_cachees_presentes_a_l_entrainement.max()))
    json.dump(resume, open(os.path.join(a.out, 'resume.json'), 'w'), indent=1); print(json.dumps(resume, indent=1))
    if len(par_med):
        P = pd.DataFrame(par_med); print(P.groupby(['genes', 'medicament']).agg(DL=('DL_exactitude', 'mean'), reference=('majoritaire_exactitude', 'mean'), inf_classe_vue=('DL_exactitude_informatives_classe_vue', 'mean'), inf_jamais_vue=('informatives_classe_jamais_vue', 'sum')).round(3).to_string())


if __name__ == '__main__':
    main()
