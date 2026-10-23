#!/usr/bin/env python3
"""
construire_regles_v8_v1.py : regles_v8_monogene.csv = regles_v7_monogene.csv + les 67 lignes du groupe A VALIDÉES par Mouna (« ok », 23 oct. 2026, 12 h 01).
Aucun fichier existant n'est modifié. Source des 67 lignes : results/elargissement_liste_v1/regles_proposees_groupe_A_v1.csv (lecture des fiches de directives DPWG, PA166...).
Usage : python3 construire_regles_v8_v1.py --v7 ../data/regles_v7_monogene.csv --ajout ../results/elargissement_liste_v1/regles_proposees_groupe_A_v1.csv --sortie ../data/regles_v8_monogene.csv
"""
import argparse
import numpy as np, pandas as pd

def main():
    ap = argparse.ArgumentParser()
    for k in ('v7', 'ajout', 'sortie'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args()
    v7 = pd.read_csv(a.v7); aj = pd.read_csv(a.ajout)
    assert not (set(aj.medicament) & set(v7.medicament.str.lower())), 'un médicament ajouté a déjà des règles v7'
    assert aj.statut_proposition.eq('A_valider_par_Mouna').all()
    new = pd.DataFrame(dict(gene=aj.gene, valeur=aj.valeur.astype(float), medicament=aj.medicament, action=aj.action, ambigu=False, source=aj.source, n_valeurs=1,
                            phenotype='règle v8 groupe A', recommandation=aj.recommandation, fichier=aj.fichier, table=np.nan, guideline_multigene=0,
                            desaccord_autres_sources=np.nan, conflit_intra_source=False, divergence_autre_table_meme_source=False, gene_dans_les_31=True,
                            conditionnel=False, codage_a_valider=False))
    out = pd.concat([v7, new[v7.columns]], ignore_index=True)
    assert out.duplicated(['gene', 'valeur', 'medicament']).sum() == v7.duplicated(['gene', 'valeur', 'medicament']).sum()
    out.to_csv(a.sortie, index=False)
    print('v7 :', len(v7), 'lignes,', v7.medicament.nunique(), 'médicaments | ajout :', len(new), 'lignes,', new.medicament.nunique(), 'médicaments | v8 :', len(out), 'lignes,', out.medicament.nunique(), 'médicaments')

if __name__ == '__main__': main()
