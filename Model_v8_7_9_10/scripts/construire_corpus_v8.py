#!/usr/bin/env python3
"""
construire_corpus_v8.py : corpus v8 = profils RÉELS (profils_genes_v4.csv) x médicaments ayant une règle utilisable dans regles_v8_monogene.csv (+ multigènes v7),
étiquetés par le MÊME moteur que v3/v7 (construire_corpus_v3.py, non modifié). Même procédé que construire_corpus_v7.py ; v7 reste intact.
Usage : python3 construire_corpus_v8.py --profils ../data/profils_genes_v4.csv --regles_mono ../data/regles_v8_monogene.csv --regles_multi ../data/regles_v2_corrigees_multigene_v7.csv --sortie ../data/corpus_v8
"""
import argparse, os, sys, tempfile
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construire_corpus_v3 as eng

def main():
    ap = argparse.ArgumentParser()
    for k in ('profils', 'regles_mono', 'regles_multi', 'sortie'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args(); os.makedirs(a.sortie, exist_ok=True)
    P = pd.read_csv(a.profils).set_index('sample_id')
    vals = [c for c in P.columns if not c.endswith(('_source', '_genotype', '_phenotype'))]
    rules = pd.read_csv(a.regles_mono); multi = pd.read_csv(a.regles_multi)
    meds = sorted(set(rules.medicament.str.lower()) | set(multi.medicament.str.lower()))
    base = P[vals].copy().astype(float); base.insert(0, 'sample_id', base.index); base['family_id'] = 'FAM_' + base.sample_id
    frames = []
    for m in meds:
        t = base.copy(); t['drug'] = m; t['action'] = 'STANDARD'; frames.append(t)
    cross = pd.concat(frames, ignore_index=True)[vals + ['drug', 'action', 'sample_id', 'family_id']]
    tmp = os.path.join(tempfile.mkdtemp(), 'croise_v8.csv'); cross.to_csv(tmp, index=False)
    print('profils', len(P), '| médicaments avec règle', len(meds), '| lignes croisées', len(cross))
    eng.main(tmp, a.regles_mono, a.regles_multi, a.sortie)
    os.replace(os.path.join(a.sortie, 'phenotype_drug_dataset_v3.csv'), os.path.join(a.sortie, 'phenotype_drug_dataset_v8.csv'))
    for n in ('ancienne_vs_v3_croisement.csv', 'couverture_corpus_v3_par_origine.csv'):
        p = os.path.join(a.sortie, n)
        if os.path.exists(p): os.remove(p)
    os.replace(os.path.join(a.sortie, 'couverture_corpus_v3_par_medicament.csv'), os.path.join(a.sortie, 'corpus_v8_couverture_par_medicament.csv'))
    v = pd.read_csv(os.path.join(a.sortie, 'phenotype_drug_dataset_v8.csv')).drop(columns=['action_ancienne', 'origine'], errors='ignore')
    v.to_csv(os.path.join(a.sortie, 'phenotype_drug_dataset_v8.csv'), index=False)
    print('\nCORPUS v8 :', len(v), 'lignes |', v.drug.nunique(), 'médicaments |', v.sample_id.nunique(), 'profils'); print(v.action.value_counts().to_dict())

if __name__ == '__main__': main()
