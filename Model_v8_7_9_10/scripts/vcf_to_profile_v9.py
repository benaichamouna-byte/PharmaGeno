#!/usr/bin/env python3
"""
vcf_to_profile_v9.py : lecteur de VCF v9 = vcf_to_profile_v8.py + UN changement : CYP2C9 est codé en SCORE D'ACTIVITÉ / 2 (0 ; 0,25 ; 0,5 ; 0,75 ; 1),
comme dans profils_genes_v5.csv et corpus_v9 (27 oct. 2026).
Raison : la guideline CPIC AINS (id 110058) et la guideline CPIC phénytoïne distinguent le score d'activité 1,0 du score 1,5 chez les métaboliseurs intermédiaires
(dose standard à 1,5 ; dose réduite ou alternative à 1,0) ; l'ancien codage (intermédiaire = 0,5) fusionnait les deux.
Calcul : génotype PyPGx « *a/*b » -> (activité(*a) + activité(*b)) / 2, valeurs d'activité de la table CPIC des allèles (data/cyp2c9_alleles_cpic_v1.csv, API CPIC /allele).
Allèle absent de la table ou sans valeur d'activité -> « non déterminé » (jamais « normal »).
vcf_to_profile_v8.py reste INTACT ; tout le reste (autres gènes, HLA, contrôles de fichier) est identique.
Usage : identique à vcf_to_profile_v8.py (+ variable d'environnement PHARMAGENO_CYP2C9_ALLELES pour le chemin de la table des allèles).
"""
import os, sys
import pandas as pd
import vcf_to_profile_v8 as v8
from vcf_to_profile_v8 import *   # noqa : mêmes noms publics (lire_vcf, lire_hla, GENES_VCF, ...)

_CHEMIN = os.environ.get('PHARMAGENO_CYP2C9_ALLELES') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'cyp2c9_alleles_cpic_v1.csv')
_ACT = None

def activites_cyp2c9():
    global _ACT
    if _ACT is None:
        _ACT = {r.allele: float(r.activity_value) for r in pd.read_csv(_CHEMIN).itertuples() if not pd.isna(r.activity_value)}
    return _ACT

v8.METHODE['CYP2C9'] = 'activite_cpic'
_coder_v8 = v8.coder_gene

def coder_gene(gene, genotype, phenotype, tables, codage):
    if gene != 'CYP2C9':
        return _coder_v8(gene, genotype, phenotype, tables, codage)
    if not isinstance(genotype, str) or len(genotype.split('/')) != 2:
        return None, 'PyPGx : génotype CYP2C9 absent ou illisible (« %s »).' % genotype, None
    a, b = genotype.split('/'); act = activites_cyp2c9()
    for x in (a, b):
        if x not in act:
            return None, "Allèle CYP2C9 %s sans valeur d'activité dans la table CPIC : non déterminé (jamais « normal »)." % x, None
    s = act[a] + act[b]
    return s / 2.0, None, "score d'activité %.1f" % s

v8.coder_gene = coder_gene   # lire_vcf (v8) appelle coder_gene par son nom global : il utilise désormais la version v9

if __name__ == '__main__':
    v8.main()
