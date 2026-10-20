#!/usr/bin/env python3
"""
test_moteur_v8.py : vérifie le moteur v8 (aucun entraînement ; l'ensemble final n'est pas lu). Sortie : lignes PASS / FAIL.
T1 la référence CPIC redonne les 130 578 étiquettes du corpus v7 (et rien sur les lignes non étiquetées)
T2 le vecteur de variables du moteur est identique à celui de l'entraînement (protocole_commun_v8.charger), valeurs manquantes comprises
T3 les actions DL du moteur sont identiques à un calcul indépendant (modèle chargé à part, variables de l'entraînement)
T4 couche de sécurité : médicament inconnu, médicament sans empreinte, gène requis manquant, combinaison jamais vue, abstention
T5 sensibilité aux gènes NON requis : l'action du DL change-t-elle si on remplace ces gènes par ceux d'un autre profil ? (diagnostic, pas un pass/fail)
Attention : T2/T3/T5 portent sur des lignes que le modèle a vues à l'entraînement : ils testent la mécanique, PAS la performance.
"""
import json, sys
import numpy as np, pandas as pd, torch
import protocole_commun_v8 as pc
from moteur_v8 import MoteurPGx
from regle_cpic_v8 import RegleCPIC
from train_dl_v9_graines import PharmaGenoDL, predire

OK = True
def verdict(nom, cond, detail=''):
    global OK; OK &= bool(cond); print(('PASS ' if cond else 'FAIL ') + nom + (' | ' + detail if detail else ''), flush=True)

M = MoteurPGx('resultats_final_v8', 'domaine_v8.json', 'corpus_v7/phenotype_drug_dataset_v7.csv'.replace('phenotype_drug_dataset_v7.csv', 'regles_v7_monogene.csv'), 'regles_v2_corrigees_multigene_v7.csv')
P = pd.read_csv('profils_genes_v4.csv').set_index('sample_id')
prof = {s: {g: (None if pd.isna(P.at[s, g]) else float(P.at[s, g])) for g in M.genes_profil} for s in P.index}
corpus = pd.read_csv('corpus_v7/phenotype_drug_dataset_v7.csv')

# T1
bad = sum(M.cpic.appliquer(prof[s], d)['action'] != a for s, d, a in zip(corpus.sample_id, corpus.drug, corpus.action))
lab = set(zip(corpus.sample_id, corpus.drug)); extra = sum(M.cpic.appliquer(prof[s], d)['action'] is not None for s in P.index for d in M.cpic.medicaments if (s, d) not in lab)
verdict('T1 référence CPIC = étiquettes du corpus', bad == 0 and extra == 0, '%d lignes comparées, %d différences ; lignes non étiquetées avec action : %d' % (len(corpus), bad, extra))

# T2 / T3 : lignes de l'entraînement (charger exclut les 4 médicaments sans empreinte)
d = pc.charger('corpus_v7/phenotype_drug_dataset_v7.csv', '/home/claude/drug_fingerprints_v2.pkl')
df, G, meds = d['df'], d['G'], d['meds']; assert d['genes'] == M.features, 'variables différentes de celles du modèle'
rng = np.random.RandomState(7); ech = rng.choice(len(df), 600, replace=False)
diff = 0
for i in ech:
    v, _ = M.vecteur(prof[df.sample_id.iat[i]])
    if not np.allclose(v, G[i], atol=1e-6): diff += 1
verdict('T2 variables du moteur = variables d\'entraînement', diff == 0, '%d lignes tirées, %d différentes' % (len(ech), diff))
ck = torch.load('resultats_final_v8/modele_final_v8_dl_film_id.pt', map_location='cpu', weights_only=True)
mod = PharmaGenoDL(ck['n_genes'], ck['fp_dim'], len(ck['classes']), ck['arch']); mod.load_state_dict(ck['state_dict']); mod.eval()
mu, sd = np.asarray(ck['scaler_mean'], dtype=np.float32), np.asarray(ck['scaler_scale'], dtype=np.float32)
ID = np.eye(len(meds), dtype=np.float32)[d['drug_idx'][ech]]
Pi = predire(mod, ((G[ech] - mu) / sd).astype(np.float32), ID); act_i = [ck['classes'][k] for k in Pi.argmax(1)]
n_cmp = n_dif = n_hors = 0
for i, a in zip(ech, act_i):
    r = M.predire(prof[df.sample_id.iat[i]], [df.drug.iat[i]])[0]
    if 'action_dl' not in r: n_hors += 1; continue
    n_cmp += 1; n_dif += r['action_dl'] != a
verdict('T3 actions DL du moteur = calcul indépendant', n_dif == 0, '%d comparées, %d différentes, %d sans prédiction (couche de sécurité)' % (n_cmp, n_dif, n_hors))

# T4 sécurité
p = dict(prof[P.index[0]])
r = M.predire(p, ['medicament_inventé'])[0]; verdict('T4a médicament inconnu', r['statut'] == 'medicament_non_couvert')
r = M.predire(p, ['rasburicase'])[0]; verdict('T4b médicament sans empreinte', r['statut'] == 'dl_indisponible' and 'action_dl' not in r, 'statut=%s ; action_cpic=%s' % (r['statut'], r['action_cpic']))
q = dict(p); q['CYP2C19'] = None; r = M.predire(q, ['clopidogrel'])[0]
verdict('T4c gène requis manquant (jamais vu avec manquant) : pas de prédiction', r['statut'] == 'non_determine_gene' and 'action_dl' not in r, 'statut=%s' % r['statut'])
q = dict(p); q['CYP2C19'] = 0.25; r = M.predire(q, ['clopidogrel'])[0]
verdict('T4d combinaison jamais vue : pas de prédiction', r['statut'] == 'hors_domaine' and 'action_dl' not in r, 'statut=%s' % r['statut'])
# un profil typique : répartition des statuts sur les 113 médicaments
rr = M.predire(prof[P.index[3]]); cnt = pd.Series([x['statut'] for x in rr]).value_counts().to_dict()
verdict('T4e profil réel : tous les médicaments reçoivent un statut', sum(cnt.values()) == len(M.dom), str(cnt))
# abstention : un seuil à 1 % doit écarter au plus quelques % des prédictions sur un échantillon
ech2 = rng.choice(len(df), 3000, replace=False); al = {'incertain': 0, 'desaccord_xgboost': 0, 'desaccord_cpic': 0}; n = 0; stat = {}
for i in ech2:
    r = M.predire(prof[df.sample_id.iat[i]], [df.drug.iat[i]])[0]; stat[r['statut']] = stat.get(r['statut'], 0) + 1
    if 'action_dl' in r:
        n += 1
        for a in r['alertes']: al[a] += 1
print('INFO 3000 lignes d\'entraînement : statuts', stat, '| alertes (sur %d prédictions DL)' % n, al)
verdict('T4f abstention : part « incertain » raisonnable (<= 3 %)', al['incertain'] / max(n, 1) <= 0.03, '%.2f %%' % (100 * al['incertain'] / max(n, 1)))

# T5 sensibilité aux gènes non requis (diagnostic)
changes = tot = 0; ech3 = rng.choice(len(df), 1500, replace=False); ids = list(P.index)
for i in ech3:
    s, m = df.sample_id.iat[i], df.drug.iat[i]
    if m not in M.dom or not M.dom[m]['dans_modele']: continue
    req = set(M.dom[m]['genes']); o = prof[ids[rng.randint(len(ids))]]
    hyb = {g: (prof[s][g] if g in req else o[g]) for g in M.genes_profil}
    a0 = M.predire(prof[s], [m])[0]; a1 = M.predire(hyb, [m])[0]
    if 'action_dl' in a0 and 'action_dl' in a1:
        tot += 1; changes += a0['action_dl'] != a1['action_dl']
print('INFO T5 : l\'action du DL change dans %d cas sur %d (%.2f %%) quand les gènes NON requis viennent d\'un autre profil' % (changes, tot, 100 * changes / max(tot, 1)))
print('\nRÉSULTAT GLOBAL :', 'TOUS LES TESTS PASSENT' if OK else 'AU MOINS UN TEST ÉCHOUE')
sys.exit(0 if OK else 1)
