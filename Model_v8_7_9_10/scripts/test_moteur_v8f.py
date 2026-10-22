#!/usr/bin/env python3
"""
test_moteur_v8f.py : tests du moteur v8f (moteur_v8f.MoteurPGxProfil). Aucun entraînement ; l'ensemble final n'est pas lu.
À lancer depuis le dossier scripts/ :  python3 test_moteur_v8f.py --fp <drug_fingerprints_v2.pkl> [--modeles ../modeles_v8f]
Ce qui est testé : le CÂBLAGE (chaque médicament est relié à sa colonne de sortie du DL ; mêmes variables que l'entraînement ; couche de sécurité ; abstention).
Ce qui n'est PAS testé : la performance. Les profils utilisés sont ceux de l'entraînement : un accord élevé vérifie le câblage, il ne mesure pas la qualité du modèle.
"""
import argparse, os, sys
import numpy as np, pandas as pd, torch
ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI); os.chdir(ICI)
import protocole_commun_v8 as pc
from moteur_v8f import MoteurPGxProfil

ap = argparse.ArgumentParser(); ap.add_argument('--fp', required=True); ap.add_argument('--modeles', default=os.path.join(ICI, '..', 'modeles_v8f'))
ap.add_argument('--modeles-xgb', default=os.path.join(ICI, '..', 'results', 'resultats_final_v8'), dest='xgb'); a = ap.parse_args()
OK = True
def verdict(nom, cond, detail=''):
    global OK; OK &= bool(cond); print(('PASS ' if cond else 'FAIL ') + nom + (' | ' + detail if detail else ''), flush=True)

D = os.path.join(ICI, '..', 'data')
M = MoteurPGxProfil(a.modeles, os.path.join(D, 'domaine_v8.json'), os.path.join(D, 'regles_v7_monogene.csv'), os.path.join(D, 'regles_v2_corrigees_multigene_v7.csv'), dossier_xgb=a.xgb)
P = pd.read_csv(os.path.join(D, 'profils_genes_v4.csv')).set_index('sample_id')
prof = {s: {g: (None if pd.isna(P.at[s, g]) else float(P.at[s, g])) for g in M.genes_profil} for s in P.index}
d = pc.charger(os.path.join(D, 'phenotype_drug_dataset_v7.csv'), a.fp); df, G, y, classes, meds = d['df'], d['G'], d['y'], d['classes'], d['meds']

verdict('T1 variables, classes et médicaments du moteur = ceux de l\'entraînement', d['genes'] == M.features and classes == M.classes and meds == M.meds, '%d variables, %d classes, %d médicaments' % (len(M.features), len(classes), len(meds)))

# T2 : les variables construites par le moteur à partir d'un profil = celles de l'entraînement
ech = np.random.RandomState(7).choice(len(df), 600, replace=False)
diff = sum(not np.allclose(M.vecteur(prof[df.sample_id.iat[i]])[0], G[i], atol=1e-6) for i in ech)
verdict('T2 vecteur d\'entrée du moteur = variables d\'entraînement', diff == 0, '%d lignes tirées, %d différentes' % (len(ech), diff))

# T3 : câblage médicament -> colonne de sortie. Si la correspondance était fausse, l'accord avec l'étiquette du corpus s'effondrerait pour ce médicament.
Pall = M.probas_toutes(G); act = Pall[np.arange(len(G)), d['drug_idx']].argmax(1)       # (profil de la ligne, médicament de la ligne) -> sortie de ce médicament
acc = pd.Series(act == y).groupby(df.drug.values).mean()
verdict('T3 câblage : accord avec l\'étiquette du corpus >= 0,95 pour chaque médicament (lignes d\'entraînement)', acc.min() >= 0.95, 'minimum %.4f (%s), médiane %.4f, %d médicaments' % (acc.min(), acc.idxmin(), acc.median(), len(acc)))
# contre-épreuve : avec une correspondance volontairement décalée, l'accord doit s'effondrer (le test T3 sait donc détecter une erreur de câblage)
act_faux = Pall[np.arange(len(G)), (d['drug_idx'] + 1) % len(meds)].argmax(1)
verdict('T3b contre-épreuve : correspondance décalée -> accord nettement plus bas', float((act_faux == y).mean()) < float((act == y).mean()) - 0.05, 'correct %.4f | décalé %.4f' % ((act == y).mean(), (act_faux == y).mean()))

# T4 : l'interface probas(G, noms) = lecture directe de la sortie du réseau
ids = np.random.RandomState(3).choice(len(df), 300, replace=False); noms = [df.drug.iat[i] for i in ids]
Pi, Px = M.probas(G[ids], noms)
verdict('T4 probas() = sortie du DL pour le bon médicament', np.allclose(Pi, Pall[ids, d['drug_idx'][ids]], atol=1e-6) and Px is not None and Px.shape == Pi.shape, 'XGBoost second avis présent : %s' % (Px is not None))

# T5 : predire() applique la couche de sécurité puis rend la même action que le réseau
n_cmp = n_dif = n_hors = 0
for i in ids:
    r = M.predire(prof[df.sample_id.iat[i]], [df.drug.iat[i]])[0]
    if 'action_dl' not in r: n_hors += 1; continue
    n_cmp += 1; n_dif += r['action_dl'] != classes[int(Pall[i, d['drug_idx'][i]].argmax())]
verdict('T5 actions DL de predire() = lecture directe du réseau', n_dif == 0 and n_cmp > 0, '%d comparées, %d différentes, %d sans prédiction (couche de sécurité)' % (n_cmp, n_dif, n_hors))

# T6 : couche de sécurité
p = dict(prof[P.index[0]])
r = M.predire(p, ['medicament_inventé'])[0]; verdict('T6a médicament inconnu', r['statut'] == 'medicament_non_couvert')
r = M.predire(p, ['rasburicase'])[0]; verdict('T6b médicament sans empreinte', r['statut'] == 'dl_indisponible' and 'action_dl' not in r, 'statut=%s' % r['statut'])
q = dict(p); q['CYP2C19'] = None; r = M.predire(q, ['clopidogrel'])[0]
verdict('T6c gène requis manquant (jamais vu avec manquant) : pas de prédiction', r['statut'] == 'non_determine_gene' and 'action_dl' not in r, 'statut=%s' % r['statut'])
q = dict(p); q['CYP2C19'] = 0.25; r = M.predire(q, ['clopidogrel'])[0]
verdict('T6d combinaison jamais vue : pas de prédiction', r['statut'] == 'hors_domaine' and 'action_dl' not in r, 'statut=%s' % r['statut'])
rr = M.predire(prof[P.index[3]]); cnt = pd.Series([x['statut'] for x in rr]).value_counts().to_dict()
verdict('T6e profil réel : tous les médicaments reçoivent un statut', sum(cnt.values()) == len(M.dom), str(cnt))

# T7 : abstention et accords (information + une borne)
ech2 = np.random.RandomState(11).choice(len(df), 3000, replace=False); al = {'incertain': 0, 'desaccord_xgboost': 0, 'desaccord_cpic': 0}; n = 0
for i in ech2:
    r = M.predire(prof[df.sample_id.iat[i]], [df.drug.iat[i]])[0]
    if 'action_dl' in r:
        n += 1
        for x in r['alertes']: al[x] += 1
print('INFO 3000 lignes d\'entraînement : alertes sur %d prédictions DL :' % n, al)
verdict('T7 abstention : part « incertain » <= 3 %', al['incertain'] / max(n, 1) <= 0.03, '%.2f %%' % (100 * al['incertain'] / max(n, 1)))

# T8 : un profil ne contenant que des gènes inconnus du modèle ne produit aucune prédiction inventée
vide = {g: None for g in M.genes_profil}; rr = M.predire(vide); n_dl = sum('action_dl' in x for x in rr)
print('INFO profil entièrement non déterminé : %d médicaments avec prédiction DL sur %d (statuts : %s)' % (n_dl, len(rr), pd.Series([x['statut'] for x in rr]).value_counts().to_dict()))
verdict('T8 profil entièrement non déterminé : aucune prédiction DL pour un médicament dont un gène requis est absent', all(('action_dl' not in x) for x in rr if any(v is None for v in x.get('valeurs_requises', {}).values())))

print('\nRÉSULTAT GLOBAL :', 'TOUT PASSE' if OK else 'ÉCHEC'); sys.exit(0 if OK else 1)
