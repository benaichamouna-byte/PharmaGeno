#!/usr/bin/env python3
"""
concordance_pypgx_corpus_v7.py : compare les phénotypes calculés par PyPGx 0.27.0 (VCF 1KGP du paquet pypgx-bundle, GRCh38, 1 379 échantillons du corpus)
avec les valeurs 0 / 0,5 / 1 / 1,5 / 2 des profils du corpus v3. Objectif : savoir si la correspondance « phénotype PyPGx -> valeur » utilisée par l'application
est la même que celle des données d'entraînement, gène par gène. Aucun entraînement, aucun modèle.

Correspondance testée (fixée AVANT de regarder les résultats ; elle suit le vocabulaire des tables de règles et de PyPGx) :
  Poor Metabolizer / Likely Poor Metabolizer / Poor Function / Unfavorable Response           -> 0.0
  Intermediate / Likely Intermediate / Possible Intermediate / Decreased / Possible Decreased  -> 0.5
  Normal Metabolizer / Normal Function / Favorable Response                                    -> 1.0
  Rapid Metabolizer -> 1.5 ; Increased Function -> 1.5 ; Ultrarapid Metabolizer -> 2.0
  Indeterminate -> None (« non déterminé »)  [le corpus, lui, a mis 1.0 : voir la colonne 'indetermine_code_1_0_dans_corpus']

Usage : python3 concordance_pypgx_corpus_v7.py --pgx DOSSIER_PGXRUN --data phenotype_drug_dataset_v3_croise.csv --out concordance_pypgx_corpus_v7
  (DOSSIER_PGXRUN contient <GENE>/phenotypes.zip produits par PyPGx ; voir pgx_1kgp_v7.sh)
"""
import argparse, os, json
import pandas as pd
from pypgx.sdk.utils import Archive

GENES = ['ABCG2', 'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP3A5', 'DPYD', 'F5', 'NUDT15', 'SLCO1B1', 'TPMT', 'UGT1A1']  # CYP2D6 : voir mémoire (variants structuraux)

CODAGE = {
    'Poor Metabolizer': 0.0, 'Likely Poor Metabolizer': 0.0, 'Poor Function': 0.0, 'Unfavorable Response': 0.0,
    'Intermediate Metabolizer': 0.5, 'Likely Intermediate Metabolizer': 0.5, 'Possible Intermediate Metabolizer': 0.5,
    'Decreased Function': 0.5, 'Possible Decreased Function': 0.5,
    'Normal Metabolizer': 1.0, 'Normal Function': 1.0, 'Favorable Response': 1.0,
    'Rapid Metabolizer': 1.5, 'Increased Function': 1.5, 'Ultrarapid Metabolizer': 2.0,
    'Indeterminate': None,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pgx', required=True); ap.add_argument('--data', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    df = pd.read_csv(a.data); prof = df.drop_duplicates('sample_id').set_index('sample_id')
    lignes, croises, tous = [], [], []
    for g in GENES:
        f = os.path.join(a.pgx, g, 'phenotypes.zip')
        if not os.path.exists(f):
            print(g, ': phenotypes.zip absent'); continue
        t = Archive.from_file(f).data[['Phenotype']].join(prof[[g]].rename(columns={g: 'valeur_corpus'}), how='inner')
        inconnus = sorted(set(t.Phenotype) - set(CODAGE))
        assert not inconnus, '%s : phénotypes non prévus dans la correspondance : %s' % (g, inconnus)
        t['valeur_pypgx'] = t.Phenotype.map(CODAGE)
        ct = pd.crosstab(t.Phenotype, t.valeur_corpus); ct.insert(0, 'gene', g); croises.append(ct.reset_index())
        det = t[t.valeur_pypgx.notna()]; ind = t[t.valeur_pypgx.isna()]
        ok = int((det.valeur_pypgx == det.valeur_corpus).sum())
        lignes.append(dict(gene=g, n=len(t), n_determines=len(det), concordants=ok, concordance_pct=round(100 * ok / len(det), 2),
                           ecarts=len(det) - ok, indetermines_pypgx=len(ind),
                           indetermine_code_1_0_dans_corpus=int((ind.valeur_corpus == 1.0).sum())))
        t['gene'] = g; tous.append(t.reset_index().rename(columns={'index': 'sample_id'}))
        print('\n==', g); print(ct.drop(columns='gene').to_string())
    res = pd.DataFrame(lignes); res.to_csv(os.path.join(a.out, 'concordance_resume.csv'), index=False)
    pd.concat(croises).to_csv(os.path.join(a.out, 'concordance_tableaux_croises.csv'), index=False)
    pd.concat(tous).to_csv(os.path.join(a.out, 'concordance_par_echantillon.csv'), index=False)
    pd.DataFrame([dict(phenotype_pypgx=k, valeur=v) for k, v in CODAGE.items()]).to_csv(os.path.join(a.out, 'codage_pypgx_valeur_v7.csv'), index=False)
    print('\nRÉSUMÉ'); print(res.to_string(index=False))
    print('Total : %d concordants sur %d appels déterminés (%.2f %%) ; %d indéterminés PyPGx.' % (
        res.concordants.sum(), res.n_determines.sum(), 100 * res.concordants.sum() / res.n_determines.sum(), res.indetermines_pypgx.sum()))


if __name__ == '__main__':
    main()
