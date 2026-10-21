#!/usr/bin/env python3
"""
test_combinaisons_retirees_dl_v1.py : le DL combine-t-il les gènes du profil ? Test par retrait de combinaisons entières.

Principe : pour les médicaments dont la règle dépend de DEUX gènes (14 médicaments), on retire de l'entraînement des combinaisons (valeur gène A, valeur gène B) ENTIÈRES.
Chaque valeur prise séparément reste vue dans d'autres combinaisons (les « lettres » sont connues, le « mot » ne l'est pas). On entraîne le DL (configuration finale : FiLM, identifiant de
médicament, poids de classes en racine, EVITER x2) sans ces lignes, puis on mesure sa réponse sur les combinaisons retirées.
Références : (a) classe majoritaire du médicament dans l'entraînement ; (b) table de règles : couverture nulle sur une combinaison absente (elle ne peut pas répondre).
Mesure principale : exactitude sur les lignes « informatives » (étiquette différente de la classe majoritaire du médicament).
L'ensemble final (10 % des familles) n'est jamais lu : exclu par protocole_commun_v8.decouper. Résultats rapportés tels quels, y compris négatifs. Répété pour plusieurs tirages de combinaisons retirées.
Usage : python3 test_combinaisons_retirees_dl_v1.py --data ../data/phenotype_drug_dataset_v7.csv --fp <drug_fingerprints_v2.pkl> --domaine ../data/domaine_v8.json --out ../results/combinaisons_retirees_dl_v1 [--tirages 3] [--smoke]
"""
import argparse, json, os, time
import numpy as np, pandas as pd, torch
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
import protocole_commun_v8 as pc
from train_dl_v9_graines import entrainer, predire


def choisir_combinaisons(df, garde, dom, rng, fraction=0.25, min_lignes=10, exiger_classe_vue=False):
    """pour chaque médicament à 2 gènes : combinaisons à retirer (chaque valeur de gène reste vue ailleurs)"""
    retirees = {}
    for m, v in dom.items():
        if len(v['genes']) != 2 or not v['dans_modele']: continue
        sub = df.iloc[garde][df.iloc[garde].drug == m]
        gs = v['genes']; sub = sub.dropna(subset=gs)
        comb = sub.groupby(gs).size(); comb = comb[comb >= min_lignes]
        classes_de = sub.groupby(gs).action.agg(lambda x: set(x))     # classes portées par chaque combinaison
        cands = list(comb.index); rng.shuffle(cands)
        cible = max(1, int(round(fraction * len(cands)))); restants = set(cands); pris = []
        for c in cands:
            if len(pris) >= cible: break
            autres = restants - {c}
            ok_classes = (not exiger_classe_vue) or classes_de[c] <= set().union(*[classes_de[o] for o in autres]) if autres else False   # variante B : la classe reste vue pour ce médicament
            if ok_classes and all(any(o[j] == c[j] for o in autres) for j in range(2)):   # chaque valeur reste vue dans une autre combinaison
                pris.append(c); restants = autres
        if pris: retirees[m] = pris
    return retirees


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'fp', 'domaine', 'out'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--tirages', type=int, default=3); ap.add_argument('--epochs', type=int, default=60); ap.add_argument('--smoke', action='store_true'); ap.add_argument('--classe_vue', action='store_true', help="variante B : la classe d'une combinaison retirée reste vue pour ce médicament dans l'entraînement")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); torch.set_num_threads(max(1, os.cpu_count() or 1))
    d = pc.charger(a.data, a.fp); df, G, y, classes, groups, meds = d['df'], d['G'], d['y'], d['classes'], d['groups'], d['meds']
    K = len(classes); dom = json.load(open(a.domaine, encoding='utf-8'))['medicaments']
    final, _ = pc.decouper(groups, y); garde = np.setdiff1d(np.arange(len(y)), final)
    D = np.eye(len(meds), dtype=np.float32)[d['drug_idx']]; ev = classes.index('EVITER')
    rows, par_med = [], []
    for t in range(a.tirages):
        t0 = time.time(); rng = np.random.RandomState(100 + t)
        ret = choisir_combinaisons(df, garde, dom, rng, exiger_classe_vue=a.classe_vue)
        masque_ret = np.zeros(len(y), dtype=bool)
        for m, combs in ret.items():
            gs = dom[m]['genes']; dm = (df.drug.values == m)
            for c in combs: masque_ret |= dm & (df[gs[0]].values == c[0]) & (df[gs[1]].values == c[1])
        masque_ret &= np.isin(np.arange(len(y)), garde)
        test = np.where(masque_ret)[0]; train_all = np.setdiff1d(garde, test)
        assert not (set(groups[final]) & set(groups[train_all])), 'fuite'
        gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE)
        a_idx, v_idx = next(gss.split(train_all, groups=groups[train_all])); trn, val = train_all[a_idx], train_all[v_idx]
        sc = StandardScaler().fit(G[trn]); S = lambda ix: sc.transform(G[ix]).astype(np.float32)
        cnt = np.bincount(y[trn], minlength=K).astype(float); w = np.sqrt(len(trn) / (K * np.maximum(cnt, 1))); w = w.copy(); w[ev] *= 2.0
        model, hist, bestval = entrainer(S(trn), D[trn], y[trn], S(val), D[val], y[val], K, 2 if a.smoke else a.epochs, pc.GRAINE + t, w, 'film')
        P = predire(model, S(test), D[test]); pred = P.argmax(1); yt = y[test]
        # référence : classe majoritaire du médicament dans l'entraînement
        maj = {}
        for m in ret:
            ym = y[trn][df.drug.values[trn] == m]; maj[m] = int(np.bincount(ym, minlength=K).argmax()) if len(ym) else 0
        pm = np.array([maj[m] for m in df.drug.values[test]])
        inf = yt != pm                                    # lignes informatives : la classe majoritaire se trompe
        # même médicaments, combinaisons VUES mais familles inconnues (validation interne) : référence « combinaison vue »
        vm = np.isin(df.drug.values[val], list(ret))
        pv = predire(model, S(val[vm]), D[val[vm]]).argmax(1)
        r = dict(tirage=t + 1, medicaments=len(ret), combinaisons_retirees=int(sum(len(v) for v in ret.values())), lignes_test=int(len(test)), lignes_informatives=int(inf.sum()),
                 DL_exactitude=round(float((pred == yt).mean()), 4), DL_exactitude_informatives=round(float((pred[inf] == yt[inf]).mean()), 4) if inf.any() else None,
                 reference_majoritaire_exactitude=round(float((pm == yt).mean()), 4), reference_majoritaire_informatives=0.0,
                 table_de_regles_couverture=0.0,
                 DL_F1_macro=round(float(f1_score(yt, pred, average='macro', zero_division=0)), 4),
                 EVITER_reel=int((yt == ev).sum()), DL_EVITER_detectes=int(((yt == ev) & (pred == ev)).sum()),
                 DL_exactitude_combinaisons_vues_memes_medicaments=round(float((pv == y[val[vm]]).mean()), 4) if vm.any() else None, lignes_vues_ref=int(vm.sum()),
                 epoques=len(hist), secondes=round(time.time() - t0))
        rows.append(r); print(r, flush=True)
        for m in ret:
            mk = df.drug.values[test] == m
            if mk.any(): par_med.append(dict(tirage=t + 1, medicament=m, genes='+'.join(dom[m]['genes']), combinaisons_retirees=len(ret[m]), lignes=int(mk.sum()),
                                           DL_exactitude=round(float((pred[mk] == yt[mk]).mean()), 4), majoritaire_exactitude=round(float((pm[mk] == yt[mk]).mean()), 4),
                                           informatives=int(inf[mk].sum()), DL_exactitude_informatives=round(float((pred[mk & inf] == yt[mk & inf]).mean()), 4) if (mk & inf).any() else None))
    pd.DataFrame(rows).to_csv(os.path.join(a.out, 'resume_par_tirage.csv'), index=False)
    pd.DataFrame(par_med).to_csv(os.path.join(a.out, 'par_medicament.csv'), index=False)
    R = pd.DataFrame(rows)
    resume = dict(tirages=len(R), DL_exactitude_informatives_moy=float(R.DL_exactitude_informatives.mean()), DL_exactitude_informatives_min=float(R.DL_exactitude_informatives.min()),
                  DL_exactitude_moy=float(R.DL_exactitude.mean()), reference_majoritaire_moy=float(R.reference_majoritaire_exactitude.mean()),
                  DL_exactitude_combinaisons_vues_moy=float(R.DL_exactitude_combinaisons_vues_memes_medicaments.mean()))
    json.dump(resume, open(os.path.join(a.out, 'resume.json'), 'w'), indent=1); print(json.dumps(resume, indent=1))


if __name__ == '__main__':
    main()
