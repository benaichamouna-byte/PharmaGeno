#!/usr/bin/env python3
"""
construire_corpus_v7.py : corpus v7 = profils RÉELS (profils_genes_v4.csv) x médicaments ayant une règle utilisable, étiquetés par le MÊME moteur que le v3
(construire_corpus_v3.py, non modifié). Aucun fichier existant n'est modifié ou écrasé.
Règles v7 = regles_v2_corrigees_monogene_v7.csv SANS les lignes G6PD / HLA-B / MT-RNR1 de la v2 (marquées codage_a_valider, remplacées par les lectures complètes)
           + G6PD (regles_v3_candidates_v2.csv, classes STANDARD/EVITER/SURVEILLER ; « Variable » et « Indéterminé » sans règle -> ligne exclue)
           + HLA (CPIC uniquement : abacavir B*57:01 ; allopurinol B*58:01 ; carbamazépine B*15:02 et A*31:01 ; oxcarbazépine, phénytoïne, fosphénytoïne B*15:02).
Non étiquetés volontairement : RYR1/CACNA1S (résultat négatif = « susceptibilité incertaine », pas de recommandation), MT-RNR1 (aucune donnée),
antivitamines K (dose par algorithme pour tous), ivacaftor (aucun profil G551D/F508del homozygote).
Usage : python3 construire_corpus_v7.py --profils profils_genes_v4.csv --regles_mono regles_v2_corrigees_monogene_v7.csv --regles_multi regles_v2_corrigees_multigene_v7.csv --candidates regles_v3_candidates_v2.csv --moteur DOSSIER_AVEC_construire_corpus_v3.py --sortie DOSSIER
"""
import argparse, os, sys, tempfile
import numpy as np, pandas as pd

HLA = {  # (médicament, allèle) -> note ; action si porteur certain (1.0) = EVITER ; non porteur (0.0) = STANDARD
    ('abacavir', 'HLA-B*57:01'): 'CPIC Strong (PA166104997)', ('allopurinol', 'HLA-B*58:01'): 'CPIC Strong (PA166105003)',
    ('carbamazepine', 'HLA-B*15:02'): 'CPIC (PA166105008) ; DPWG PA166265162 : éviter', ('carbamazepine', 'HLA-A*31:01'): 'CPIC (PA166105008)',
    ('oxcarbazepine', 'HLA-B*15:02'): 'CPIC (PA166176623)', ('phenytoin', 'HLA-B*15:02'): 'CPIC (PA166122806)', ('fosphenytoin', 'HLA-B*15:02'): 'CPIC (PA166122806)'}
COLS = ['gene', 'valeur', 'medicament', 'action', 'ambigu', 'source', 'n_valeurs', 'phenotype', 'recommandation', 'fichier', 'table', 'guideline_multigene',
        'desaccord_autres_sources', 'conflit_intra_source', 'divergence_autre_table_meme_source', 'gene_dans_les_31', 'conditionnel', 'codage_a_valider']


def row(gene, val, med, act, src, phen, reco, fic, cond=False, desac=np.nan):
    return dict(gene=gene, valeur=val, medicament=med, action=act, ambigu=False, source=src, n_valeurs=1, phenotype=phen, recommandation=reco, fichier=fic, table=np.nan,
                guideline_multigene=0, desaccord_autres_sources=desac, conflit_intra_source=False, divergence_autre_table_meme_source=False, gene_dans_les_31=True,
                conditionnel=cond, codage_a_valider=False)


def main():
    ap = argparse.ArgumentParser()
    for k in ('profils', 'regles_mono', 'regles_multi', 'candidates', 'moteur', 'sortie'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args(); os.makedirs(a.sortie, exist_ok=True)
    sys.path.insert(0, a.moteur); import construire_corpus_v3 as eng
    P = pd.read_csv(a.profils).set_index('sample_id')
    vals = [c for c in P.columns if not c.endswith(('_source', '_genotype', '_phenotype'))]
    mono = pd.read_csv(a.regles_mono)
    retire = mono[mono.gene.isin(['G6PD', 'HLA-B', 'MT-RNR1'])]
    keep = mono[~mono.gene.isin(['G6PD', 'HLA-B', 'MT-RNR1'])]
    new = []
    cd = pd.read_csv(a.candidates).fillna('')
    g6 = cd[(cd.gene == 'G6PD') & cd.phenotype_ou_allele.isin(['Normal', 'Deficient', 'Variable']) & cd.action_classe_proposee.isin(['STANDARD', 'EVITER', 'SURVEILLER'])]
    for r in g6.itertuples():
        v = {'Normal': 1.0, 'Deficient': 0.0, 'Variable': 0.5}[r.phenotype_ou_allele]
        new.append(row('G6PD', v, r.medicament, r.action_classe_proposee, 'CPIC', 'G6PD ' + r.phenotype_ou_allele, r.condition[:200], r.id_guideline,
                       cond=('SAUF_SCHEMAS' in str(r.action_brute))))
    for (med, al), note in HLA.items():
        new.append(row(al, 1.0, med, 'EVITER', 'CPIC', 'porteur ' + al, note, 'hla_consignes_v2.csv', desac='autres organisations : force ou liste d\'allèles différente'))
        new.append(row(al, 0.0, med, 'STANDARD', 'CPIC', 'non porteur ' + al, note, 'hla_consignes_v2.csv', desac='autres organisations : force ou liste d\'allèles différente'))
    rules = pd.concat([keep, pd.DataFrame(new)[COLS]], ignore_index=True)
    rf = os.path.join(a.sortie, 'regles_v7_monogene.csv'); rules.to_csv(rf, index=False)
    multi = pd.read_csv(a.regles_multi)
    meds = sorted(set(rules.medicament.str.lower()) | set(multi.medicament.str.lower()))
    base = P[vals].copy().astype(float)
    base.insert(0, 'sample_id', base.index); base['family_id'] = 'FAM_' + base.sample_id
    frames = []
    for m in meds:
        t = base.copy(); t['drug'] = m; t['action'] = 'STANDARD'; frames.append(t)
    cross = pd.concat(frames, ignore_index=True)[vals + ['drug', 'action', 'sample_id', 'family_id']]
    tmp = os.path.join(tempfile.mkdtemp(), 'croise_v7.csv'); cross.to_csv(tmp, index=False)
    print('profils', len(P), '| médicaments avec règle', len(meds), '| lignes croisées', len(cross), '| colonnes valeur', len(vals))
    print('lignes de règles G6PD/HLA-B/MT-RNR1 de la v2 non reprises (remplacées, fichier v2 intact) :', len(retire))
    eng.main(tmp, rf, a.regles_multi, a.sortie)
    os.replace(os.path.join(a.sortie, 'phenotype_drug_dataset_v3.csv'), os.path.join(a.sortie, 'phenotype_drug_dataset_v7.csv'))
    for n in ('ancienne_vs_v3_croisement.csv', 'couverture_corpus_v3_par_origine.csv'):
        p = os.path.join(a.sortie, n)
        if os.path.exists(p): os.remove(p)
    os.replace(os.path.join(a.sortie, 'couverture_corpus_v3_par_medicament.csv'), os.path.join(a.sortie, 'corpus_v7_couverture_par_medicament.csv'))
    v7 = pd.read_csv(os.path.join(a.sortie, 'phenotype_drug_dataset_v7.csv')).drop(columns=['action_ancienne', 'origine'], errors='ignore')
    v7.to_csv(os.path.join(a.sortie, 'phenotype_drug_dataset_v7.csv'), index=False)
    print('\nCORPUS v7 :', len(v7), 'lignes |', v7.drug.nunique(), 'médicaments |', v7.sample_id.nunique(), 'profils')
    print(v7.action.value_counts().to_dict())

if __name__ == '__main__': main()
