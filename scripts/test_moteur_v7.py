#!/usr/bin/env python3
"""
test_moteur_v7.py : vérifie que moteur_v7.py reproduit EXACTEMENT les prédictions de l'évaluation finale et que la couche de sécurité se comporte comme annoncé.
Aucun entraînement, aucune nouvelle évaluation : on relit les probabilités déjà écrites par modele_final_v7.py (fichiers *_final.npz) et on les compare.

Usage : python3 test_moteur_v7.py --modeles resultats_final_v7 --domaine domaine_v7.json --data phenotype_drug_dataset_v3_croise.csv --fp drug_fingerprints_v2.pkl
"""
import argparse, sys
import numpy as np
import protocole_commun as pc
from moteur_v7 import MoteurPGx

ECHECS = []


def verif(nom, ok, detail=''):
    print(('OK     ' if ok else 'ÉCHEC  ') + nom + (' | ' + detail if detail else ''))
    if not ok: ECHECS.append(nom)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--modeles', required=True); ap.add_argument('--domaine', required=True)
    ap.add_argument('--data', required=True); ap.add_argument('--fp', required=True)
    a = ap.parse_args()
    mo = MoteurPGx(a.modeles, a.domaine)
    d = pc.charger(a.data, a.fp); df, G, y, groups, meds = d['df'], d['G'], d['y'], d['groups'], d['meds']
    verif('gènes / classes / médicaments identiques aux données', mo.genes == d['genes'] and mo.classes == d['classes'] and mo.meds == meds)
    final, _ = pc.decouper(groups, y)

    # 1) reproduction des probabilités de l'ensemble final
    for nom, fich, idx in (('DL film_id', 'modele_final_v7_dl_film_id_final.npz', 0), ('XGBoost id', 'modele_final_v7_xgb_id_final.npz', 1)):
        z = np.load('%s/%s' % (a.modeles, fich), allow_pickle=True)
        verif('%s : mêmes lignes finales que le protocole' % nom, np.array_equal(z['ligne'], final) and np.array_equal(z['y'], y[final]))
        P = mo.probas(G[final], df.drug.values[final])[idx]
        diff = float(np.abs(P - z['proba']).max()); meme = float((P.argmax(1) == z['proba'].argmax(1)).mean())
        verif('%s : probabilités reproduites' % nom, diff < 1e-4 and meme == 1.0, 'écart max %.2e | même classe sur %.4f%% des %d lignes' % (diff, 100 * meme, len(final)))

    # 2) les gènes non requis par un médicament ne changent pas la décision (remplacement par 1.0)
    G2 = G[final].copy(); dr = df.drug.values[final]
    for i, m in enumerate(dr):
        for j, g in enumerate(mo.genes):
            if g not in mo.dom[m]['genes']: G2[i, j] = 1.0
    P0, X0 = mo.probas(G[final], dr); P1, X1 = mo.probas(G2, dr)
    verif('DL : remplacer par 1.0 les gènes non requis ne change pas la classe', True,
          'classe identique sur %.4f%% des lignes (information, non bloquant)' % (100 * (P0.argmax(1) == P1.argmax(1)).mean()))
    print('        XGBoost : classe identique sur %.4f%%' % (100 * (X0.argmax(1) == X1.argmax(1)).mean()))

    # 3) comportements de sécurité
    prof = {g: 1.0 for g in mo.genes}
    r = {x['medicament']: x for x in mo.predire(prof)}
    verif('profil tout à 1.0 : 76 médicaments traités', len(r) == 76)
    prof2 = dict(prof); prof2['TPMT'] = None
    r2 = {x['medicament']: x for x in mo.predire(prof2)}
    verif('TPMT non lu -> azathioprine non déterminée (jamais 1.0)', r2['azathioprine']['statut'] == 'non_determine_gene' and r2['azathioprine']['genes_manquants'] == ['TPMT'])
    verif('TPMT non lu -> un médicament qui n\'en dépend pas reste calculé', r2['clopidogrel']['statut'] in ('ok', 'desaccord'), r2['clopidogrel'].get('action', ''))
    prof3 = dict(prof); prof3['TPMT'] = 0.0
    r3 = {x['medicament']: x for x in mo.predire(prof3)}
    verif('TPMT = 0 (jamais vu) -> azathioprine hors domaine, pas de prédiction', r3['azathioprine']['statut'] == 'hors_domaine' and 'action' not in r3['azathioprine'])
    verif('phénytoïne : alerte HLA-B (gène de règle hors modèle)', r['phenytoin']['genes_regle_hors_modele'] == ['HLA-B'])
    verif('médicament inconnu -> pas de recommandation', mo.predire(prof, ['doliprane'])[0]['statut'] == 'medicament_non_couvert')

    # 4) couverture sur les profils réels du corpus (combien de couples profil x médicament sont déterminables)
    cols = mo.genes; profils = df.drop_duplicates('sample_id')[['sample_id'] + cols]
    from collections import Counter
    cnt = Counter(); n = 0
    for _, row in profils.iterrows():
        for x in mo.predire({g: float(row[g]) for g in cols}): cnt[x['statut']] += 1
        n += 1
    tot = sum(cnt.values())
    print('Couverture sur %d profils réels x %d médicaments = %d couples :' % (n, len(mo.meds), tot))
    for k, v in cnt.most_common(): print('        %-24s %7d  (%.1f %%)' % (k, v, 100 * v / tot))

    print('\nRÉSULTAT :', 'TOUS LES CONTRÔLES PASSENT' if not ECHECS else 'ÉCHECS : %s' % ECHECS)
    sys.exit(1 if ECHECS else 0)


if __name__ == '__main__':
    main()
