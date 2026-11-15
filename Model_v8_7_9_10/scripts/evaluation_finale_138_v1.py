#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evaluation_finale_138_v1.py (15 nov. 2026) : LECTURE UNIQUE de l'ensemble final (138 profils, 23 455 lignes, corpus v15).
Protocole figé AVANT la lecture : claude/Protocole_fige_evaluation_finale_138_15nov2026.md (validé par Mouna avant exécution).
Ce script est exécuté UNE SEULE FOIS ; les résultats sont rapportés tels quels, aucune relance, aucun ajustement.

Bras évalués (modeles_v15_eval, entraînés sur 1 207 profils = 1 241 dev − 34 apparentés aux finaux, hyperparamètres inchangés, graine 42) :
  DL config 35 + température | XGBoost | forêt aléatoire. Référence = étiquettes du corpus v15 (issues des règles gelées).
Métriques (figées) : pc.metriques (F1 macro, exactitude, rappels, ECE 15 intervalles, log-loss) + EVITER manqués ;
IC bootstrap percentile par profil (10 000 tirages, graine 42) pour F1 macro et EVITER manqués, et pour les différences appariées
DL-XGB, DL-RF, XGB-RF (règle gelée : équivalence si |écart| et IC dans ±0,001).
Abstention DL : seuils FIGÉS (abstention_seuils_profil_v3.json), niveau 0,010 (celui de l'application) ; autres niveaux descriptifs.
Strates : 34 profils finaux ayant un apparenté retiré vs les 104 autres ; HG02230 et HG02620 (vecteur identique à un profil
de développement, non retirés — choix du 5 nov.) rapportés à part. Limite écrite : les paires internes HG01953/HG01954 et
HG02678/HG02679 ne sont pas traitées comme dépendantes par le bootstrap par profil.

Usage : python3 -I evaluation_finale_138_v1.py --data ../data/corpus_v15/phenotype_drug_dataset_v15.csv \
        --modeles ../modeles_v15_eval --paires ../audit/paires_final_dev_v15.csv --out ../results/evaluation_finale_138
"""
import argparse, hashlib, json, os, sys, time
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dl_coeur_v4 as dc, protocole_commun_v10 as pc

DELTA = 0.001          # règle gelée du protocole de comparaison
N_BOOT, GRAINE_BOOT = 10000, 42
IDENTIQUES = ('HG02230', 'HG02620')   # vecteur d'entrée identique à un profil de développement (5 nov.)
PAIRES_INTERNES = (('HG01953', 'HG01954'), ('HG02678', 'HG02679'))


def sha16(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()[:16]


def confusions_par_profil(y, pred, pid_lignes, profils_ordre, K):
    """(n_profils, K, K) : matrice de confusion de chaque profil."""
    C = np.zeros((len(profils_ordre), K, K), dtype=np.int64)
    pos = {p: i for i, p in enumerate(profils_ordre)}
    for i in range(len(y)):
        C[pos[pid_lignes[i]], y[i], pred[i]] += 1
    return C


def f1_macro_depuis_confusion(M):
    """M (K,K) sommée ; F1 macro, zero_division=0 (convention scikit-learn)."""
    tp = np.diag(M).astype(float); fp = M.sum(0) - tp; fn = M.sum(1) - tp
    f1 = np.where(tp > 0, 2 * tp / np.maximum(2 * tp + fp + fn, 1e-12), 0.0)
    return float(f1.mean())


def bootstrap(Cs, ev, n_profils):
    """Cs : dict bras -> (n_profils,K,K). Tirages communs à tous les bras (différences appariées)."""
    rng = np.random.RandomState(GRAINE_BOOT)
    tirages = rng.randint(0, n_profils, size=(N_BOOT, n_profils))
    out = {b: {'f1': np.empty(N_BOOT), 'ev_manques': np.empty(N_BOOT, dtype=np.int64)} for b in Cs}
    for b, C in Cs.items():
        ev_par_profil = C[:, ev, :].sum(1) - C[:, ev, ev]   # EVITER manqués de chaque profil
        for t in range(N_BOOT):
            ix = tirages[t]
            out[b]['f1'][t] = f1_macro_depuis_confusion(C[ix].sum(0))
            out[b]['ev_manques'][t] = int(ev_par_profil[ix].sum())
    return out


def ic(v):
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'modeles', 'paires', 'out'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); torch.set_num_threads(2); t0 = time.time()

    d = dc.tableau(a.data)
    X, Y, pid, y, G = d['X'], d['Y'], d['pid'], d['y'], d['G']
    classes, genes, meds, drug_idx, profils = d['classes'], d['genes'], d['meds'], d['drug_idx'], d['profils']
    K, ev = len(classes), classes.index('EVITER')
    final, _ = pc.decouper(d['groups'], y)
    lp = final                                   # indices de LIGNES de l'ensemble final
    p_fin = sorted(set(pid[lp]))                 # indices de PROFILS finaux
    noms_fin = [profils[i] for i in p_fin]
    print('LECTURE UNIQUE : %d lignes, %d profils' % (len(lp), len(p_fin)), flush=True)
    assert len(p_fin) == 138 and len(lp) == 23455, 'effectifs inattendus : %d profils, %d lignes' % (len(p_fin), len(lp))

    # ---- DL (config 35 + température) ----
    ck = torch.load(os.path.join(a.modeles, 'modele_final_profil_v3.pt'), map_location='cpu', weights_only=False)
    assert ck['genes'] == genes and ck['classes'] == classes and ck['medicaments'] == meds, 'variables/classes/médicaments differents du corpus'
    model = dc.DL(ck['n_in'], ck['n_med'], ck['K'], ck['cfg']); model.load_state_dict(ck['state_dict']); model.eval()
    sc_m, sc_s = np.array(ck['scaler_mean'], dtype=np.float32), np.array(ck['scaler_scale'], dtype=np.float32)
    Xs = ((X - sc_m) / sc_s).astype(np.float32)
    P = dc.probas(model, Xs)                     # (profils, meds, K), non calibré
    z = np.log(np.clip(P, 1e-12, 1)) / float(ck['temperature']); z -= z.max(-1, keepdims=True)
    Pc = np.exp(z); Pc /= Pc.sum(-1, keepdims=True)
    P_dl = Pc[pid[lp], drug_idx[lp]]             # (n_lignes_finales, K) calibré

    # ---- XGBoost ----
    from xgboost import XGBClassifier
    mx = XGBClassifier(); mx.load_model(os.path.join(a.modeles, 'modele_final_v8_xgb_id.json'))
    meta_x = json.load(open(os.path.join(a.modeles, 'modele_final_v8_xgb_id_meta.json')))
    assert meta_x['genes'] == genes and meta_x['classes'] == classes and meta_x['medicaments'] == meds
    ID = np.eye(len(meds), dtype=np.float32)[drug_idx[lp]]
    Xl = np.hstack([G[lp], ID]).astype(np.float32)
    P_xgb = np.zeros((len(lp), K), dtype=np.float32); P_xgb[:, mx.classes_.astype(int)] = mx.predict_proba(Xl)

    # ---- Forêt aléatoire ----
    import joblib
    mr = joblib.load(os.path.join(a.modeles, 'modele_final_rf.joblib'))
    meta_r = json.load(open(os.path.join(a.modeles, 'modele_final_rf_meta.json')))
    assert meta_r['genes'] == genes and meta_r['classes'] == classes and meta_r['medicaments'] == meds
    P_rf = np.zeros((len(lp), K), dtype=np.float32); P_rf[:, mr.classes_.astype(int)] = mr.predict_proba(Xl)

    yF = y[lp]; bras = {'DL_calibre': P_dl, 'XGBoost': P_xgb, 'Foret_aleatoire': P_rf}
    res = {'donnees': os.path.basename(a.data), 'sha256_donnees': sha16(a.data), 'modeles': a.modeles,
           'n_lignes': int(len(lp)), 'n_profils': int(len(p_fin)), 'classes': classes,
           'protocole': 'claude/Protocole_fige_evaluation_finale_138_15nov2026.md', 'bras': {}, 'comparaisons': {}, 'strates': {}}

    Cs = {}
    for b, P_ in bras.items():
        pred = P_.argmax(1)
        m = pc.metriques(yF, P_, classes)
        m['EVITER_manques'] = int(((yF == ev) & (pred != ev)).sum()); m['EVITER_total'] = int((yF == ev).sum())
        res['bras'][b] = m
        Cs[b] = confusions_par_profil(yF, pred, pid[lp], p_fin, K)
        print(b, ':', json.dumps(m, ensure_ascii=False), flush=True)

    # ---- bootstrap par profil (tirages communs) ----
    bt = bootstrap(Cs, ev, len(p_fin))
    for b in bras:
        res['bras'][b]['IC_f1_macro'] = ic(bt[b]['f1']); res['bras'][b]['IC_EVITER_manques'] = ic(bt[b]['ev_manques'])
    for a1, a2 in (('DL_calibre', 'XGBoost'), ('DL_calibre', 'Foret_aleatoire'), ('XGBoost', 'Foret_aleatoire')):
        df1 = bt[a1]['f1'] - bt[a2]['f1']; dev_ = bt[a1]['ev_manques'] - bt[a2]['ev_manques']
        ecart = res['bras'][a1]['f1_macro'] - res['bras'][a2]['f1_macro']
        icf = ic(df1)
        verdict = ('equivalents (|ecart| et IC dans ±%g)' % DELTA) if (abs(ecart) < DELTA and -DELTA <= icf[0] and icf[1] <= DELTA) \
            else (('tranche en faveur de %s' % (a1 if ecart > 0 else a2)) if (icf[0] > 0 or icf[1] < 0) and abs(ecart) >= DELTA else 'non tranche')
        res['comparaisons']['%s_moins_%s' % (a1, a2)] = {'ecart_f1_macro': round(float(ecart), 5), 'IC_f1': [round(v, 5) for v in icf],
                                                         'ecart_EVITER_manques': int(res['bras'][a1]['EVITER_manques'] - res['bras'][a2]['EVITER_manques']),
                                                         'IC_EVITER_manques': ic(dev_), 'regle_delta': DELTA, 'verdict': verdict}

    # ---- abstention DL (seuils figés) ----
    seuils = json.load(open(os.path.join(a.modeles, 'abstention_seuils_profil_v3.json')))['seuils_confiance']
    res['abstention_DL'] = {'source': 'seuils FIGES de modeles_v15 (quantiles hors-plis de la validation croisee v15)'}
    for niv, s in seuils.items():
        garde = P_dl.max(1) > s
        e = {'seuil': s, 'couverture': round(float(garde.mean()), 4), 'n_abstentions': int((~garde).sum())}
        if garde.any():
            mg = pc.metriques(yF[garde], P_dl[garde], classes)
            pg = P_dl[garde].argmax(1)
            mg['EVITER_manques'] = int(((yF[garde] == ev) & (pg != ev)).sum()); mg['EVITER_total'] = int((yF[garde] == ev).sum())
            e['metriques_sur_lignes_gardees'] = mg
        res['abstention_DL'][niv] = e
    res['abstention_DL']['niveau_application'] = '0.010'

    # ---- strates ----
    apparentes = sorted({l.split(',')[0] for l in open(a.paires).read().strip().split('\n')[1:]})
    assert len(apparentes) == 34
    i_app = [i for i in p_fin if profils[i] in apparentes]; i_aut = [i for i in p_fin if profils[i] not in apparentes]
    pos = {p: j for j, p in enumerate(p_fin)}
    for nom, sous in (('34_finaux_avec_apparente_retire', i_app), ('104_autres', i_aut)):
        masque = np.isin(pid[lp], sous)
        st = {}
        for b, P_ in bras.items():
            m = pc.metriques(yF[masque], P_[masque], classes)
            pr = P_[masque].argmax(1)
            m['EVITER_manques'] = int(((yF[masque] == ev) & (pr != ev)).sum()); m['EVITER_total'] = int((yF[masque] == ev).sum())
            st[b] = m
        res['strates'][nom] = {'n_profils': len(sous), 'n_lignes': int(masque.sum()), 'bras': st}
    det = {}
    for nomp in IDENTIQUES:
        i = profils.tolist().index(nomp) if hasattr(profils, 'tolist') else list(profils).index(nomp)
        masque = pid[lp] == i
        det[nomp] = {'n_lignes': int(masque.sum()),
                     'erreurs_par_bras': {b: int((P_[masque].argmax(1) != yF[masque]).sum()) for b, P_ in bras.items()}}
    res['strates']['2_vecteur_identique_non_retires'] = det
    res['strates']['limite_paires_internes'] = 'HG01953/HG01954 et HG02678/HG02679 (apparentees a l\'interieur de l\'ensemble final) ne sont pas traitees comme dependantes par le bootstrap par profil'

    # ---- archives ----
    import csv as csv_
    with open(os.path.join(a.out, 'predictions_138.csv'), 'w', newline='') as f:
        w = csv_.writer(f); w.writerow(['sample_id', 'medicament', 'etiquette', 'pred_DL', 'p_max_DL', 'pred_XGB', 'pred_RF'])
        pd_, px_, pr_ = P_dl.argmax(1), P_xgb.argmax(1), P_rf.argmax(1)
        for j, i in enumerate(lp):
            w.writerow([profils[pid[i]], meds[drug_idx[i]], classes[y[i]], classes[pd_[j]], round(float(P_dl[j].max()), 6), classes[px_[j]], classes[pr_[j]]])
    res['duree_s'] = round(time.time() - t0)
    json.dump(res, open(os.path.join(a.out, 'resultats_evaluation_finale_138.json'), 'w'), indent=1, ensure_ascii=False)
    print('Fichiers écrits dans', a.out, '| durée %ds' % res['duree_s'])


if __name__ == '__main__':
    main()
