#!/usr/bin/env python3
"""
test_moteur_v8g.py : tests des deux fonctions ajoutées par moteur_v8g.py (sortie_complete, genes_decisifs). Aucun entraînement ; l'ensemble final n'est pas lu.
À lancer depuis le dossier scripts/ :  python3 test_moteur_v8g.py [--modeles ../modeles_v8f]
Ce qui est testé : le CALCUL de l'analyse de sensibilité, par un chemin indépendant (substitution dans le profil, puis predire() public) ; la cohérence de sortie_complete avec predire().
Ce qui n'est PAS testé : la pertinence clinique ou biologique des gènes décisifs (c'est une description du comportement du réseau).
"""
import argparse, os, sys
import numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI); os.chdir(ICI)
from moteur_v8g import MoteurPGxProfilG
ap = argparse.ArgumentParser(); ap.add_argument('--modeles', default=os.path.join(ICI, '..', 'modeles_v8f')); a = ap.parse_args()
OK = True
def verdict(nom, cond, detail=''):
    global OK; OK &= bool(cond); print(('PASS ' if cond else 'FAIL ') + nom + (' | ' + detail if detail else ''), flush=True)
D = os.path.join(ICI, '..', 'data')
M = MoteurPGxProfilG(a.modeles, os.path.join(D, 'domaine_v8.json'), os.path.join(D, 'regles_v7_monogene.csv'), os.path.join(D, 'regles_v2_corrigees_multigene_v7.csv'))
P = pd.read_csv(os.path.join(D, 'profils_genes_v4.csv')).set_index('sample_id')
prof = {s: {g: (None if pd.isna(P.at[s, g]) else float(P.at[s, g])) for g in M.genes_profil} for s in P.index}
rng = np.random.RandomState(5); ech = list(rng.choice(P.index, 40, replace=False))

# T1 : sortie_complete = actions DL de predire() quand predire() donne une prédiction
n_cmp = n_dif = 0
for s in ech[:15]:
    sc = M.sortie_complete(prof[s])
    assert sc['n_medicaments'] == len(M.meds) and sum(sc['comptes'].values()) == len(M.meds)
    for r in M.predire(prof[s]):
        if 'action_dl' in r: n_cmp += 1; n_dif += r['action_dl'] != sc['actions'][r['medicament']]
verdict('T1 sortie_complete() = actions DL de predire() (profils réels)', n_cmp > 0 and n_dif == 0, '%d comparées, %d différentes' % (n_cmp, n_dif))

# T2 : chemin indépendant. On remplace le gène par la valeur normale DANS LE PROFIL puis on appelle predire() ; le résultat doit coïncider avec genes_decisifs().
n_cas = n_dif = n_decisifs = n_hors = 0
for s in ech[:12]:
    p = prof[s]; res = {r['medicament']: r for r in M.predire(p)}
    for m, r in res.items():
        if 'action_dl' not in r: continue
        dec = {tuple(d['genes']): d['action_si_normal'] for d in M.genes_decisifs(p, m) if len(d['genes']) == 1}
        for g in M.genes_modele:
            v = p.get(g)
            if v is None or float(v) == (0.0 if g.startswith('HLA-') else 1.0): continue
            q = dict(p); q[g] = 0.0 if g.startswith('HLA-') else 1.0; r2 = M.predire(q, [m])[0]
            if 'action_dl' not in r2: n_hors += 1; continue          # après substitution la combinaison est hors domaine : predire() ne répond pas, ce cas n'est pas comparable
            n_cas += 1; attendu = r2['action_dl'] if r2['action_dl'] != r['action_dl'] else None
            n_decisifs += attendu is not None; n_dif += (dec.get((g,)) != attendu)
verdict('T2 gènes décisifs = substitution dans le profil puis predire() (chemin indépendant)', n_cas > 0 and n_dif == 0, '%d substitutions comparées (%d non comparables : hors domaine), %d différentes, dont %d changent la prédiction' % (n_cas, n_hors, n_dif, n_decisifs))

# T3 : profil entièrement « normal » : aucun gène décisif
normal = {g: (0.0 if g.startswith('HLA-') else 1.0) for g in M.genes_modele}
tot = sum(len(M.genes_decisifs(normal, m)) for m in M.meds)
verdict('T3 profil entièrement normal : aucun gène décisif pour aucun médicament', tot == 0, '%d gènes décisifs trouvés' % tot)

# T4 : médicament inconnu ; gène non lu ignoré
verdict('T4a médicament inconnu : liste vide', M.genes_decisifs(prof[ech[0]], 'medicament_inventé') == [])
q = dict(prof[ech[0]]); q['CYP2C19'] = None
verdict('T4b gène non lu : jamais proposé comme gène décisif', all('CYP2C19' not in d['genes'] for m in ['clopidogrel', 'citalopram', 'omeprazole'] for d in M.genes_decisifs(q, m)))

# T5 : gènes non requis. Borne fixée à l'avance : au plus 1 % des couples (profil, médicament).
nr = tot_cell = 0
for s in ech[:12]:
    p = prof[s]
    for m, r in {r['medicament']: r for r in M.predire(p)}.items():
        if 'action_dl' not in r: continue
        tot_cell += 1; req = set(M.dom[m]['genes'])
        nr += any(not (set(d['genes']) <= req) for d in M.genes_decisifs(p, m))
print('INFO T5 : sur %d couples (profil, médicament) prédits, le DL change d\'avis en remplaçant un gène NON requis par la guideline dans %d cas (%.2f %%)' % (tot_cell, nr, 100 * nr / max(tot_cell, 1)))
verdict('T5 gènes non requis : au plus 1 % des couples (borne fixée à l\'avance)', nr / max(tot_cell, 1) <= 0.01, '%.2f %%' % (100 * nr / max(tot_cell, 1)))
print('\nRÉSULTAT GLOBAL :', 'TOUT PASSE' if OK else 'ÉCHEC'); sys.exit(0 if OK else 1)
