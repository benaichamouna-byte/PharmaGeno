"""
construire_profils_genes_v4.py : profils_genes_v4.csv = profils_genes_v3.csv avec NUDT15, TPMT et SLCO1B1 remplacés.
Nouvelle valeur = génotype PyPGx 0.27.0 -> table CPIC (PharmCAT phenotype/<GENE>.json) -> codage du projet (codage_pypgx_valeur_v7.csv),
calculée par verif_getrm_v1/calculer_phenotypes_cpic_12genes_v1.py (variante A).
Règle : un diplotype absent de la table CPIC ('non_mappable'), « Indeterminate » dans la table CPIC ('indetermine_cpic') ou sans génotype reste MANQUANT, jamais « normal ».
Les autres colonnes et gènes sont inchangés (copie de la v3). La colonne <GENE>_source indique l'origine de chaque valeur.
Raison : la v3 avait traité « Indeterminate » de PyPGx comme normal (NUDT15 *6, TPMT *16...) et manqué des allèles rares ; accord avec GeT-RM : NUDT15 4/7 -> 7/7, TPMT 28/30 -> 30/30, SLCO1B1 18/21 -> 20/21.
Usage : python3 construire_profils_genes_v4.py --profils profils_genes_v3.csv --cpic verif_getrm_v1/phenotypes_cpic_12genes_v1.csv --sortie profils_genes_v4.csv
"""
import argparse
import numpy as np, pandas as pd

GENES = ['NUDT15', 'TPMT', 'SLCO1B1']

def main():
    ap = argparse.ArgumentParser()
    for k in ('profils', 'cpic', 'sortie'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args()
    P = pd.read_csv(a.profils).set_index('sample_id')
    C = pd.read_csv(a.cpic, index_col=0).reindex(P.index)
    assert C.index.equals(P.index) and not C.index.duplicated().any()
    Q = P.copy(); rows = []
    for g in GENES:
        ancien = P[g].copy(); val = C[g + '_valeur_cpic']; st = C[g + '_statut']
        Q[g] = val
        Q[g + '_source'] = st.map({'ok': 'pypgx0.27.0+cpic_pharmcat', 'non_mappable': 'manquant:diplotype_absent_table_cpic',
                                   'indetermine_cpic': 'manquant:indetermine_table_cpic', 'genotype_absent': 'manquant:genotype_absent'})
        assert Q[g + '_source'].notna().all(), g
        Q[g + '_genotype'] = C[g + '_genotype_pypgx']
        same = ancien.fillna(-9) == val.fillna(-9)
        rows.append(dict(gene=g, profils=len(P), valeurs_changees=int((~same).sum()), manquants_v3=int(ancien.isna().sum()), manquants_v4=int(val.isna().sum()),
                         **{f'v4_{k}': int((val == k).sum()) for k in (0.0, 0.5, 1.0, 1.5, 2.0)}))
    Q.reset_index().to_csv(a.sortie, index=False)
    r = pd.DataFrame(rows); print(r.to_string(index=False)); r.to_csv(a.sortie.replace('.csv', '_resume.csv'), index=False)
    autres = [c for c in P.columns if not any(c.startswith(g) for g in GENES)]
    assert Q[autres].fillna(-9).astype(str).equals(P[autres].fillna(-9).astype(str)), 'colonnes hors des 3 gènes modifiées'
    print('Contrôle : les', len(autres), 'autres colonnes sont identiques à la v3 ;', Q.shape[0], 'profils,', Q.shape[1], 'colonnes')

if __name__ == '__main__':
    main()
