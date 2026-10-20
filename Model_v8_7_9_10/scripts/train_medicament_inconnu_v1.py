#!/usr/bin/env python3
"""
train_medicament_inconnu_v1.py : expérience « médicament jamais vu » (leave-drug-out).

Question : un modèle entraîné sur certains médicaments peut-il prédire l'action pour un médicament ABSENT de l'entraînement ?
Seule l'empreinte moléculaire (518 bits) peut, en théorie, le permettre ; l'identifiant de médicament ne le peut pas (il est donc exclu).

Protocole (fixé AVANT de voir les résultats) :
  - L'ensemble final (10 % des familles du protocole v8) est mis de côté et NON utilisé ici.
  - Sur le reste : validation croisée en 5 plis GROUPÉE PAR MÉDICAMENT (StratifiedGroupKFold, graine 42).
    Le groupe = empreinte moléculaire identique (les 3 paires d'énantiomères à empreinte identique restent ensemble : sinon fuite).
  - Les patients (profils génétiques) peuvent apparaître des deux côtés, avec des médicaments différents : on teste le nouveau médicament, pas le nouveau patient.
  - Validation interne (arrêt anticipé) : 10 % des GROUPES de médicaments du pli d'entraînement (médicaments non vus aussi).
  - Modèles (hyperparamètres identiques aux expériences précédentes, jamais réglés ici) :
      dl        : DL film, empreinte, gènes tous, poids « racine », EVITER x2 (configuration retenue, version empreinte)
      xgb       : XGBoost, gènes + empreinte
      rf        : Random Forest, gènes + empreinte
      genes_xgb : XGBoost, gènes seuls (témoin : aucune information sur le médicament)
      majorite  : probabilités = fréquences de classes de l'entraînement (témoin)
  - Mêmes métriques que protocole_commun_v8.metriques ; en plus : résultats par médicament (fichier oof).
N'écrase rien ; n'écrit que dans --out.
"""
import argparse, json, os, time
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
import protocole_commun_v8 as pc


def groupes_medicaments(d):
    """un identifiant de groupe par empreinte distincte (empreintes identiques = même groupe)"""
    cles = {}
    g_med = []
    for i, m in enumerate(d['meds']):
        k = d['FP'][i].tobytes()
        cles.setdefault(k, len(cles)); g_med.append(cles[k])
    g_med = np.array(g_med)
    return g_med[d['drug_idx']], g_med


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True); ap.add_argument('--fp', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--modele', choices=['dl', 'xgb', 'rf', 'genes_xgb', 'majorite'], required=True)
    ap.add_argument('--epochs', type=int, default=60); ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--threads', type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); nj = a.threads or (os.cpu_count() or 1)
    d = pc.charger(a.data, a.fp, familles_smoke=0.25 if a.smoke else None)
    df, genes, y, classes, G, groups = d['df'], d['genes'], d['y'], d['classes'], d['G'], d['groups']
    K = len(classes); gmed_row, gmed = groupes_medicaments(d)
    final, _ = pc.decouper(groups, y)
    reste = np.setdiff1d(np.arange(len(y)), final)
    print('Modèle :', a.modele, '| lignes hors ensemble final :', len(reste), '| groupes de médicaments (empreintes distinctes) :', len(set(gmed)))
    skf = StratifiedGroupKFold(n_splits=pc.N_PLIS, shuffle=True, random_state=pc.GRAINE)
    plis = [(reste[x], reste[z]) for x, z in skf.split(reste, y[reste], gmed_row[reste])]
    for tr, te in plis:   # contrôles de non-fuite : aucun médicament (ni empreinte identique) des deux côtés
        assert not (set(gmed_row[tr]) & set(gmed_row[te])), 'fuite : un médicament du test est dans l\'entraînement'
        assert not (set(d['drug_idx'][tr]) & set(d['drug_idx'][te]))
    pli_med = {}
    for k, (_, te) in enumerate(plis):
        for m in sorted(set(df.drug.values[te])): pli_med[m] = k + 1
    pd.DataFrame(sorted(pli_med.items()), columns=['drug', 'pli_test']).to_csv(os.path.join(a.out, 'medicaments_par_pli.csv'), index=False)
    if a.smoke: plis = plis[:1]
    FPm = d['FP'][d['drug_idx']]
    oof = np.zeros((len(y), K), dtype=np.float32); fold_of = np.full(len(y), -1); lignes = []; t0 = time.time()
    if a.modele == 'dl':
        import train_dl_v9_graines as dl
    for k, (tr, te) in enumerate(plis):
        gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=pc.GRAINE)
        a_idx, v_idx = next(gss.split(tr, groups=gmed_row[tr])); trn, val = tr[a_idx], tr[v_idx]
        assert not (set(gmed_row[trn]) & set(gmed_row[val]))
        cnt = np.bincount(y[trn], minlength=K).astype(float); w = len(trn) / (K * np.maximum(cnt, 1))
        if a.modele == 'dl':
            w = np.sqrt(w); w = w.copy(); w[classes.index('EVITER')] *= 2.0
            sc = StandardScaler().fit(G[trn]); Gs = lambda ix: sc.transform(G[ix]).astype(np.float32)
            model, hist, bestval = dl.entrainer(Gs(trn), FPm[trn], y[trn], Gs(val), FPm[val], y[val], K,
                                                2 if a.smoke else a.epochs, pc.GRAINE + k, w, 'film')
            P = dl.predire(model, Gs(te), FPm[te]); extra = dict(epoques=len(hist), f1_val_interne=round(bestval, 4))
        elif a.modele == 'majorite':
            P = np.tile(cnt / cnt.sum(), (len(te), 1)).astype(np.float32); extra = {}
        else:
            X = (np.hstack([G, FPm]) if a.modele != 'genes_xgb' else G).astype(np.float32)
            sw = w[y[trn]]
            if a.modele in ('xgb', 'genes_xgb'):
                from xgboost import XGBClassifier
                mdl = XGBClassifier(objective='multi:softprob', num_class=K, n_estimators=30 if a.smoke else 1000, learning_rate=0.1, max_depth=6,
                                    tree_method='hist', early_stopping_rounds=20, eval_metric='mlogloss', n_jobs=nj,
                                    random_state=pc.GRAINE + k, verbosity=0)
                mdl.fit(X[trn], y[trn], sample_weight=sw, eval_set=[(X[val], y[val])], verbose=False)
                extra = dict(arbres=int(mdl.best_iteration) + 1)
            else:
                from sklearn.ensemble import RandomForestClassifier
                mdl = RandomForestClassifier(n_estimators=40 if a.smoke else 500, max_features='sqrt', n_jobs=nj, random_state=pc.GRAINE + k)
                mdl.fit(X[trn], y[trn], sample_weight=sw); extra = dict(arbres=mdl.n_estimators)
            P = np.zeros((len(te), K), dtype=np.float32); P[:, mdl.classes_] = mdl.predict_proba(X[te])
        oof[te] = P; fold_of[te] = k
        ligne = dict(pli=k + 1, n_test=int(len(te)), n_medicaments_test=int(len(set(df.drug.values[te]))), **extra, **pc.metriques(y[te], P, classes))
        lignes.append(ligne); print(ligne, '| %.0fs' % (time.time() - t0), flush=True)
    res = pd.DataFrame(lignes); res.to_csv(os.path.join(a.out, a.modele + '_resultats_par_pli.csv'), index=False)
    m = fold_of >= 0
    glob = dict(modele=a.modele, protocole='médicament jamais vu : StratifiedGroupKFold(5) groupes=empreinte identique, graine 42 ; ensemble final non utilisé',
                n_lignes=int(m.sum()), classes=classes, f1_macro_moy=float(res.f1_macro.mean()), f1_macro_std=float(res.f1_macro.std(ddof=0)),
                f1_hors_surveiller_moy=float(res.f1_hors_surveiller.mean()), exactitude_moy=float(res.exactitude.mean()),
                CER_strict_moy=float(res.CER_strict.mean()), CER_strict_std=float(res.CER_strict.std(ddof=0)),
                precision_EVITER_moy=float(res.precision_EVITER.mean()), logloss_moy=float(res.logloss.mean()), ECE_moy=float(res.ECE.mean()),
                f1_macro_oof=float(f1_score(y[m], oof[m].argmax(1), average='macro')))
    json.dump(glob, open(os.path.join(a.out, a.modele + '_resume.json'), 'w'), indent=1, ensure_ascii=False)
    np.savez_compressed(os.path.join(a.out, a.modele + '_oof.npz'), proba=oof[m], y=y[m], pli=fold_of[m], ligne=np.where(m)[0], drug=df.drug.values[m].astype(str))
    print('\nRÉSULTAT %s (médicament jamais vu) : F1 macro = %.4f +/- %.4f | exactitude = %.4f | CER strict = %.4f | précision EVITER = %.4f' % (
        a.modele, glob['f1_macro_moy'], glob['f1_macro_std'], glob['exactitude_moy'], glob['CER_strict_moy'], glob['precision_EVITER_moy']))
    print('Fichiers écrits dans', a.out)


if __name__ == '__main__':
    main()
