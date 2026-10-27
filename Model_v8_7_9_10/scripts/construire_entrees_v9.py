#!/usr/bin/env python3
"""
construire_entrees_v9.py : prépare les entrées du corpus v9 SANS toucher aux fichiers v8.
 1. profils_genes_v5.csv : CYP2C9 recodé en score d'activité / 2 (0, 0.25, 0.5, 0.75, 1.0), calculé depuis le diplotype PyPGx
    et la table CPIC des allèles (data/cyp2c9_alleles_cpic_v1.csv, API CPIC /allele, 27 oct. 2026). Diplotype indéterminé -> NaN.
 2. regles_v9_monogene.csv / regles_v9_multigene.csv :
    - les 81 règles ambiguës sont tranchées selon l'audit (data/audit_81_regles_decisions_v1.csv, type de formulation du texte publié) :
      type1 EVITER, type2 ADAPTER_DOSE, type3 ADAPTER_DOSE (validé 27 oct.), type4 EXCLURE (dépend de la co-médication/indication),
      type6 STANDARD, type5 (AINS CYP2C9 intermédiaire) remplacé par les règles par score d'activité de la guideline CPIC 110058.
    - les règles CYP2C9 sont réécrites sur la nouvelle échelle : ancien 0.0 -> {0.0, 0.25} ; ancien 0.5 -> {0.5, 0.75} ; 1.0 -> {1.0}
      (même action, sauf les 7 AINS dont les 5 valeurs sont écrites une à une d'après l'API CPIC guideline 110058).
Usage : python3 construire_entrees_v9.py <dossier_des_diplotypes_pypgx_extraits> (voir chemins dans le code)
"""
import pandas as pd, numpy as np, re, sys
D = '../data/'
GENO, PHENO = sys.argv[1], sys.argv[2]
A = pd.read_csv(D + 'cyp2c9_alleles_cpic_v1.csv').set_index('allele').activity_value.to_dict()
g = pd.read_csv(GENO, sep='\t', index_col=0)['Genotype']
P = pd.read_csv(D + 'profils_genes_v4.csv')
def sa(x):
    a, b = x.split('/')
    return (A[a] + A[b]) / 2 if a in A and b in A else np.nan
new = P.sample_id.map(lambda s: sa(g[s]))
P['CYP2C9_ancien_codage'] = P.CYP2C9
P['CYP2C9'] = new
P['CYP2C9_source'] = 'pypgx_diplotype+cpic_activity_v1'
P.to_csv(D + 'profils_genes_v5.csv', index=False)
print('profils v5 :', len(P), '| CYP2C9 :', P.CYP2C9.value_counts(dropna=False).sort_index().to_dict())

# ---------- règles
M = pd.read_csv(D + 'regles_v8_monogene.csv'); X = pd.read_csv(D + 'regles_v2_corrigees_multigene_v7.csv')
dec = pd.read_csv(D + 'audit_81_regles_decisions_v1.csv')
ACT = {'1_EVITER_d_abord': 'EVITER', '2_DOSE_d_abord': 'ADAPTER_DOSE', '3_deux_options_au_choix': 'ADAPTER_DOSE', '6_standard_d_abord': 'STANDARD'}
dm = {}
for r in dec.itertuples():
    if r.nature == 'mono-gene':
        med, rest = [s.strip() for s in r.regle.split('|')]; gn, v = rest.split('='); dm[('m', med, gn.strip(), float(v))] = r.type
    else:
        med, rest = [s.strip() for s in r.regle.split('|')]; a, b = rest.split(' x '); ga, va = a.split('='); gb, vb = b.split('=')
        va, vb = float(va), float(vb)
        if ga.strip() == 'SLCO1B1' and va == 2.0: va = 1.5      # le codage projet note « increased function » 1.5 (cf. profils) ; l'extraction brute de l'audit disait 2.0
        if gb.strip() == 'SLCO1B1' and vb == 2.0: vb = 1.5
        dm[('x', med, ga.strip(), va, gb.strip(), vb)] = r.type
M['decision_v9'] = ''; X['decision_v9'] = ''
for i, r in M.iterrows():
    k = ('m', r.medicament, r.gene, float(r.valeur))
    if k in dm:
        t = dm[k]; M.at[i, 'decision_v9'] = t
        if t in ACT: M.loc[i, ['action', 'ambigu', 'conflit_intra_source', 'conditionnel']] = [ACT[t], False, False, False]
for i, r in X.iterrows():
    k = ('x', r.medicament, r.gene_a, float(r.valeur_a), r.gene_b, float(r.valeur_b))
    if k in dm:
        t = dm[k]; X.at[i, 'decision_v9'] = t
        if t in ACT: X.loc[i, ['action', 'ambigu', 'conflit_intra_source', 'conditionnel']] = [ACT[t], False, False, False]
print('décisions appliquées : mono', (M.decision_v9 != '').sum(), '| multi', (X.decision_v9 != '').sum())

# ---------- AINS : règles CYP2C9 par score d'activité (API CPIC /recommendation, guideline 110058)
NS = {  # valeur nouvelle échelle : 0.0 (AS0), 0.25 (AS0.5), 0.5 (AS1.0), 0.75 (AS1.5), 1.0 (AS2.0)
 **{d: {0.0: 'ADAPTER_DOSE', 0.25: 'ADAPTER_DOSE', 0.5: 'ADAPTER_DOSE', 0.75: 'STANDARD', 1.0: 'STANDARD'} for d in ('celecoxib', 'flurbiprofen', 'ibuprofen', 'lornoxicam')},
 'meloxicam': {0.0: 'EVITER', 0.25: 'EVITER', 0.5: 'ADAPTER_DOSE', 0.75: 'STANDARD', 1.0: 'STANDARD'},
 'piroxicam': {0.0: 'EVITER', 0.25: 'EVITER', 0.5: 'EVITER', 0.75: 'STANDARD', 1.0: 'STANDARD'},
 'tenoxicam': {0.0: 'EVITER', 0.25: 'EVITER', 0.5: 'EVITER', 0.75: 'STANDARD', 1.0: 'STANDARD'}}
M = M[~((M.gene == 'CYP2C9') & M.medicament.isin(NS))].copy()
tpl = M.iloc[0].copy()
new = []
for d, vv in NS.items():
    for v, a in vv.items():
        r = tpl.copy(); r['gene'] = 'CYP2C9'; r['valeur'] = v; r['medicament'] = d; r['action'] = a; r['ambigu'] = False; r['source'] = 'CPIC'
        r['n_valeurs'] = 1; r['phenotype'] = f'activity score {v*2}'; r['recommandation'] = 'API CPIC /recommendation guideline 110058, lookupkey CYP2C9 = ' + str(v*2)
        r['fichier'] = 'CPIC_API_110058'; r['table'] = 0; r['guideline_multigene'] = False; r['desaccord_autres_sources'] = np.nan
        r['conflit_intra_source'] = False; r['divergence_autre_table_meme_source'] = False; r['gene_dans_les_31'] = True; r['conditionnel'] = False
        r['codage_a_valider'] = False; r['decision_v9'] = 'AINS_par_score_activite'; new.append(r)
# ---------- réécriture des autres règles CYP2C9 sur la nouvelle échelle
EXP = {0.0: [0.0, 0.25], 0.5: [0.5, 0.75], 1.0: [1.0]}
rows = []
for _, r in M.iterrows():
    if r.gene == 'CYP2C9':
        for v in EXP[float(r.valeur)]:
            q = r.copy(); q['valeur'] = v; rows.append(q)
    else: rows.append(r)
M2 = pd.concat([pd.DataFrame(rows), pd.DataFrame(new)], ignore_index=True)
# siponimod CYP2C9 intermédiaire : condition (inducteur du CYP3A4) déjà acceptée en v8 (classe d'action inchangée) ; reportée sur 0.5 et 0.75
M2.loc[(M2.medicament == 'siponimod') & (M2.gene == 'CYP2C9'), 'conditionnel'] = False
rows = []
for _, r in X.iterrows():
    va = EXP[float(r.valeur_a)] if r.gene_a == 'CYP2C9' else [float(r.valeur_a)]
    vb = EXP[float(r.valeur_b)] if r.gene_b == 'CYP2C9' else [float(r.valeur_b)]
    for x in va:
        for y in vb:
            q = r.copy(); q['valeur_a'] = x; q['valeur_b'] = y; rows.append(q)
X2 = pd.DataFrame(rows)
M2.to_csv(D + 'regles_v9_monogene.csv', index=False); X2.to_csv(D + 'regles_v9_multigene.csv', index=False)
print('règles mono v8', len(pd.read_csv(D + 'regles_v8_monogene.csv')), '-> v9', len(M2), '| multi v7', len(X), '-> v9', len(X2))
print('ambiguës restantes : mono', M2.ambigu.astype(str).str.lower().eq('true').sum(), '| multi', X2.ambigu.astype(str).str.lower().eq('true').sum())
