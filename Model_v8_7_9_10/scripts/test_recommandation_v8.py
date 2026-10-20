#!/usr/bin/env python3
"""
test_recommandation_v8.py : invariants de la couche de recommandation v8 (aucun entraînement ; ensemble final non lu).
Profils : 80 profils réels du corpus (1000 Genomes), toutes les spécialités. Les profils ont servi à l'entraînement : on teste la LOGIQUE de tri, pas la performance.
"""
import json, sys
import numpy as np, pandas as pd
from moteur_v8 import MoteurPGx
from recommandation_v8 import Recommandeur

OK = True
def verdict(nom, cond, detail=''):
    global OK; OK &= bool(cond); print(('PASS ' if cond else 'FAIL ') + nom + (' | ' + detail if detail else ''), flush=True)

M = MoteurPGx('resultats_final_v8', 'domaine_v8.json', 'corpus_v7/regles_v7_monogene.csv', 'regles_v2_corrigees_multigene_v7.csv')
R = Recommandeur('atc_mapping_medicaments_v1.csv', 'specialite_atc_v1.csv', 'alternatives_atc4_v1.csv', sorted(M.dom))
P = pd.read_csv('profils_genes_v4.csv').set_index('sample_id')
prof = lambda s: {g: (None if pd.isna(P.at[s, g]) else float(P.at[s, g])) for g in M.genes_profil}
rng = np.random.RandomState(11); ids = rng.choice(list(P.index), 80, replace=False)
n_sp = len(R.specialites()); viol = dict(partition=0, propose_evit=0, evit_sans_avis=0, alt=0, texte=0); n_fiches = 0; tot = dict(proposes=0, a_eviter=0, a_verifier=0, non_evalues=0, reference_seule=0)
for s in ids:
    res = M.predire(prof(s)); par = {r['medicament']: r for r in res}
    for sp in R.specialites():
        out = R.recommander(res, sp)
        n = len(out['proposes']) + out['autres_compatibles'] + len(out['a_eviter']) + len(out['a_verifier']) + len(out['non_evalues']) + len(out['reference_seule'])
        viol['partition'] += n != out['n_medicaments_specialite']
        for k in tot: tot[k] += len(out[k])
        for f in out['proposes']:
            viol['propose_evit'] += 'EVITER' in set(f['avis'].values())
        for f in out['a_eviter']:
            viol['evit_sans_avis'] += 'EVITER' not in set(f['avis'].values())
            for a in f['alternatives']:
                x = par[a['medicament']]; ok = x['statut'] == 'ok' and x['action_dl'] == 'STANDARD' and a['medicament'] != f['medicament']
                ok &= bool({c[:5] for c in str(R.atc.loc[f['medicament'], 'atc_codes']).split(';')} & {c[:5] for c in str(R.atc.loc[a['medicament'], 'atc_codes']).split(';')})
                viol['alt'] += not ok
        for k in ('proposes', 'a_eviter', 'a_verifier', 'non_evalues', 'reference_seule'):
            for f in out[k]:
                n_fiches += 1; viol['texte'] += not (f['texte_patient'] and f['libelle'])
verdict('I1 chaque médicament de la spécialité est dans exactement une catégorie', viol['partition'] == 0, '%d profils x %d spécialités' % (len(ids), n_sp))
verdict('I2 aucun médicament « proposé » n\'a un avis EVITER (DL, XGBoost ou règle)', viol['propose_evit'] == 0)
verdict('I3 tout médicament « à éviter » a au moins un avis EVITER', viol['evit_sans_avis'] == 0)
verdict('I4 alternatives : statut ok, STANDARD, même sous-groupe ATC, différentes du médicament évité', viol['alt'] == 0)
verdict('I5 chaque fiche a un libellé et un texte patient', viol['texte'] == 0, '%d fiches' % n_fiches)
print('INFO répartition totale des fiches (80 profils x spécialités) :', tot)
# I6 recherche
base = prof(ids[0]); res = M.predire(base)
f = R.chercher_medicament('doliprane', res); verdict('I6a nom commercial non reconnu : message clair', f['trouve'] is False)
f = R.chercher_medicament('clopidogrel', res); verdict('I6b nom international reconnu', f['trouve'] is True, f['categorie'])
# I7 sécurité : CYP2C19 poor metabolizer -> clopidogrel à éviter (règle CPIC EVITER), jamais proposé
q = dict(base); q['CYP2C19'] = 0.0; res = M.predire(q, ['clopidogrel']); f = R.chercher_medicament('clopidogrel', res)
verdict('I7 CYP2C19 = 0 : clopidogrel classé « à éviter »', f['categorie'] == 'a_eviter', 'avis=%s statut=%s' % (f['avis'], f['statut']))
ex = None
for sp in R.specialites():
    out = R.recommander(M.predire(prof(ids[1])), sp)
    if out['a_eviter'] and out['proposes']: ex = out; break
json.dump(ex or {}, open('exemple_recommandation_v8.json', 'w'), indent=1, ensure_ascii=False, default=str)
print('Exemple écrit : exemple_recommandation_v8.json (spécialité %s)' % (ex or {}).get('specialite'))
print('\nRÉSULTAT GLOBAL :', 'TOUS LES TESTS PASSENT' if OK else 'AU MOINS UN TEST ÉCHOUE')
sys.exit(0 if OK else 1)
