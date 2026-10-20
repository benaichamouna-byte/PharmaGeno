#!/usr/bin/env python3
"""
construire_corpus_v3.py
Construit un NOUVEAU corpus (v3) dont les étiquettes viennent des règles de guidelines v2
(CPIC / DPWG) et non plus de l'ancienne table PharmGKB (Toxicity/Efficacy -> EVITER, etc.).
Le fichier d'origine n'est JAMAIS modifié.

Usage :
  python3 construire_corpus_v3.py CORPUS.csv REGLES_MONO.csv REGLES_MULTI.csv SORTIE_DIR

Règles de construction (toutes écrites ici pour la traçabilité) :
 1. Une règle mono-gène est UTILISABLE si : non ambiguë, non conditionnelle, codage de valeur
    déjà vérifié (codage_a_valider = False), gène présent dans les 31 gènes, pas de conflit
    interne à la source.
 2. Une règle multi-gènes est UTILISABLE si : non ambiguë, non conditionnelle, pas de conflit interne.
 3. Pour une ligne (échantillon, médicament) :
      - on regarde chaque gène pour lequel le médicament possède une règle utilisable ;
      - si une règle multi-gènes correspond aux deux valeurs, elle remplace les règles mono-gène
        de ses deux gènes ;
      - action finale = la plus sévère des actions applicables
        (EVITER > ADAPTER_DOSE > SURVEILLER > STANDARD) ;
      - si un gène du médicament a une valeur SANS règle (ex. 1.5 pour la codéine, pas de ligne
        dans la guideline) et qu'aucune action EVITER n'est déjà établie, la ligne est EXCLUE
        (statut 'incomplet') : on n'invente pas d'action.
 4. Les médicaments sans règle utilisable ne reçoivent AUCUNE étiquette (statut 'sans_regle').
 5. confiance = 'haute' si aucune autre source ne contredit la règle utilisée, 'moyenne' sinon.
"""
import sys, os
import pandas as pd

# Règles « conditionnelles » ACCEPTÉES après lecture du texte complet de la guideline (JSON PharmGKB).
# Motif : la condition (indication, co-médication) ne change pas la CLASSE d'action de la règle.
# Les autres règles conditionnelles (eliglustat PM : dépend de la co-médication ; flecainide IM :
# « aucune action » pour le test de Brugada) restent EXCLUES.
CONDITIONNELS_ACCEPTES = {
    ('clopidogrel', 'CYP2C19', 0.0): "EVITER pour SCA/ICP (fort) et autres indications CV (modéré)",
    ('clopidogrel', 'CYP2C19', 0.5): "EVITER pour SCA/ICP (fort) ; « pas de recommandation » hors SCA/ICP",
    ('siponimod', 'CYP2C9', 0.5): "50 % de la dose ; réévaluer si inducteur du CYP3A4",
    ('brexpiprazole', 'CYP2D6', 0.5): "aucune action requise",
    ('brexpiprazole', 'CYP2D6', 2.0): "aucune action requise",
    ('capecitabine', 'DPYD', 1.0): "dose standard (génotype normal)",
    ('fluorouracil', 'DPYD', 1.0): "dose standard (génotype normal)",
    ('azathioprine', 'NUDT15', 0.5): "réduction de dose dans toutes les indications (immunosuppression, leucémie)",
    ('mercaptopurine', 'NUDT15', 0.5): "réduction de dose dans toutes les indications",
    ('thioguanine', 'NUDT15', 0.5): "réduction de dose dans toutes les indications",
    ('azathioprine', 'TPMT', 0.5): "réduction de dose dans toutes les indications",
    ('mercaptopurine', 'TPMT', 0.5): "réduction de dose dans toutes les indications",
    ('thioguanine', 'TPMT', 0.5): "réduction de dose (75 %) dans toutes les indications",
    ('irinotecan', 'UGT1A1', 0.0): "70 % de la dose initiale",
}
# Les règles multi-gènes qui impliquent un gène dont le codage de valeur est encore « à valider »
# sont exclues (HLA-B, G6PD, MT-RNR1).
GENES_CODAGE_A_VALIDER = {'HLA-B', 'G6PD', 'MT-RNR1'}

SEVERITE = {'STANDARD': 0, 'SURVEILLER': 1, 'ADAPTER_DOSE': 2, 'EVITER': 3}
INV = {v: k for k, v in SEVERITE.items()}


def b(s):
    return s.astype(str).str.lower().isin(['true', '1'])


def main(corpus, mono_f, multi_f, outdir):
    os.makedirs(outdir, exist_ok=True)
    df = pd.read_csv(corpus)
    mono = pd.read_csv(mono_f)
    multi = pd.read_csv(multi_f)
    genes31 = [c for c in df.columns if c not in ('drug', 'action', 'sample_id', 'family_id')]

    for t in (mono, multi):
        t['medicament'] = t['medicament'].str.lower().str.strip()
    acc = pd.Series([(r.medicament, r.gene, float(r.valeur)) in CONDITIONNELS_ACCEPTES
                     for r in mono.itertuples()], index=mono.index)
    mono_u = mono[(~b(mono.ambigu)) & ((~b(mono.conditionnel)) | acc) & (~b(mono.codage_a_valider))
                  & b(mono.gene_dans_les_31) & (~b(mono.conflit_intra_source))].copy()
    multi_u = multi[(~b(multi.ambigu)) & (~b(multi.conditionnel)) & (~b(multi.conflit_intra_source))].copy()
    multi_u = multi_u[multi_u.gene_a.isin(genes31) & multi_u.gene_b.isin(genes31)
                      & ~multi_u.gene_a.isin(GENES_CODAGE_A_VALIDER) & ~multi_u.gene_b.isin(GENES_CODAGE_A_VALIDER)]

    # index des règles
    R1 = {}      # (med, gene, valeur) -> (action, desaccord)
    G1 = {}      # med -> set(genes)
    for r in mono_u.itertuples(index=False):
        R1[(r.medicament, r.gene, float(r.valeur))] = (r.action, isinstance(r.desaccord_autres_sources, str))
        G1.setdefault(r.medicament, set()).add(r.gene)
    R2 = {}      # (med, ga, va, gb, vb) -> (action, desaccord)
    M2 = {}      # med -> liste de (ga, gb)
    for r in multi_u.itertuples(index=False):
        R2[(r.medicament, r.gene_a, float(r.valeur_a), r.gene_b, float(r.valeur_b))] = (
            r.action, isinstance(r.desaccord_autres_sources, str))
        M2.setdefault(r.medicament, set()).add((r.gene_a, r.gene_b))

    meds = set(G1) | set(M2)
    df['_d'] = df['drug'].str.lower().str.strip()
    sub = df[df['_d'].isin(meds)]

    out_action, out_stat, out_conf, out_n = {}, {}, {}, {}
    cols = {g: sub.columns.get_loc(g) for g in genes31}
    arr = sub.values
    di = sub.columns.get_loc('_d')
    for idx, row in zip(sub.index, arr):
        d = row[di]
        val = {g: float(row[cols[g]]) for g in genes31}
        actions, desacc, couverts = [], False, set()
        for (ga, gb) in M2.get(d, ()):
            k = (d, ga, val[ga], gb, val[gb])
            if k in R2:
                a, des = R2[k]
                actions.append(a); desacc |= des; couverts |= {ga, gb}
        inconnu = False
        for g in G1.get(d, ()):
            if g in couverts:
                continue
            k = (d, g, val[g])
            if k in R1:
                a, des = R1[k]
                actions.append(a); desacc |= des
            else:
                inconnu = True
        if actions and max(SEVERITE[a] for a in actions) == 3:
            fin = 'EVITER'
        elif inconnu or not actions:
            fin = None
        else:
            fin = INV[max(SEVERITE[a] for a in actions)]
        out_action[idx] = fin
        out_stat[idx] = 'ok' if fin else 'incomplet'
        out_conf[idx] = ('moyenne' if desacc else 'haute') if fin else ''
        out_n[idx] = len(actions)

    df['action_ancienne'] = df['action']
    df['action_v3'] = pd.Series(out_action)
    df['statut_etiquette'] = pd.Series(out_stat).reindex(df.index).fillna('sans_regle')
    df['confiance'] = pd.Series(out_conf).reindex(df.index).fillna('')
    df['nb_regles_appliquees'] = pd.Series(out_n).reindex(df.index).fillna(0).astype(int)
    df['origine'] = df['sample_id'].str.extract(r'^([A-Za-z]+)')[0].map({'HG': '1KGP_HG', 'NA': '1KGP_NA', 'DOC': 'DOC'})  # 'NA' seul serait lu comme valeur manquante par pandas
    df = df.drop(columns=['_d'])

    # corpus v3 = uniquement les lignes étiquetées par les règles
    v3 = df[df.statut_etiquette == 'ok'].copy()
    v3['action'] = v3['action_v3']
    v3 = v3.drop(columns=['action_v3'])
    v3.to_csv(os.path.join(outdir, 'phenotype_drug_dataset_v3.csv'), index=False)
    print('Fichier ecrit :', os.path.join(outdir, 'phenotype_drug_dataset_v3.csv'), len(v3), 'lignes')

    # couverture
    tot = df.groupby('origine').size().rename('lignes_corpus')
    ok = df[df.statut_etiquette == 'ok'].groupby('origine').size().rename('lignes_v3')
    inc = df[df.statut_etiquette == 'incomplet'].groupby('origine').size().rename('lignes_incompletes')
    sr = df[df.statut_etiquette == 'sans_regle'].groupby('origine').size().rename('lignes_sans_regle')
    cov = pd.concat([tot, ok, inc, sr], axis=1).fillna(0).astype(int)
    cov.to_csv(os.path.join(outdir, 'couverture_corpus_v3_par_origine.csv'))

    pm = df.groupby('drug').agg(
        lignes=('drug', 'size'),
        v3=('statut_etiquette', lambda s: (s == 'ok').sum()),
        incompletes=('statut_etiquette', lambda s: (s == 'incomplet').sum()))
    pm['a_une_regle'] = [str(d).lower().strip() in meds for d in pm.index]
    pm = pm[pm.a_une_regle].sort_values('lignes', ascending=False)
    dist = v3.groupby(['drug', 'action']).size().unstack(fill_value=0)
    pm = pm.join(dist, how='left').fillna(0)
    pm.to_csv(os.path.join(outdir, 'couverture_corpus_v3_par_medicament.csv'))

    # comparaison avec l'ancienne étiquette
    cmp_ = pd.crosstab(v3['action_ancienne'], v3['action'], rownames=['ancienne'], colnames=['v3'])
    cmp_.to_csv(os.path.join(outdir, 'ancienne_vs_v3_croisement.csv'))
    print('Lignes corpus :', len(df))
    print(cov.to_string())
    print('Médicaments avec règle utilisable :', len(meds), '| présents au corpus :', pm.shape[0])
    print('Distribution v3 :', v3['action'].value_counts().to_dict())
    print('Distribution v3 par origine :'); print(pd.crosstab(v3['origine'], v3['action']).to_string())
    print('Accord ancienne/v3 :', round((v3.action_ancienne == v3.action).mean(), 3))
    print(cmp_.to_string())
    print('Confiance :', v3.confiance.value_counts().to_dict())


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
