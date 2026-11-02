# Sources comparables pour les dimensions du corpus (2 novembre 2026)

Chiffres relevés dans les PDF fournis par Mouna (texte extrait avec pdftotext) et dans des sources vérifiées ; rien n'est tiré de la mémoire.

| Dimension | Source | Chiffre cité | Ce que cela soutient |
|---|---|---|---|
| Gènes | Sangkuhl et al., Clin Pharmacol Ther 2020 ;107:203 (PharmCAT), PMID 31306493 | « The initial version of PharmCAT interprets 11 genes from published CPIC guidelines … not including CYP2D6 » ; 10 gènes validés contre GeT-RM | L'outil de référence a démarré avec 11 gènes |
| Gènes | Li et al., Am J Hum Genet 2023 ;110:1628, https://doi.org/10.1016/j.ajhg.2023.09.001 | 17 pharmacogènes avec guidelines CPIC (18 gènes + 1 variant du cluster CYP2C) sur 200 044 participants UK Biobank | Étendue d'une étude publiée |
| Gènes | Sherman, Claw, Lee, Sci Rep 2024, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11445439/ | PyPGx : 58 pharmacogènes analysés (59 gèrés), 2 504 échantillons 1000 Genomes, 145 232 appels, 538 allèles étoile ; phénotype CPIC pour 16 gènes seulement | Même outil (PyPGx) et même cohorte que nos profils |
| Médicaments | CPIC, présentation du 2 oct. 2025, https://cpicpgx.org/wp-content/uploads/2025/10/CPIC-call-10022025.pdf | « Published 29 guidelines and 16 updates, covering 35 genes and > 160 drugs » | Échelle de la source principale |
| Médicaments | PharmCAT, fichier prescribing_guidance.json, commit du 25 sept. 2026 (comptage fait dans le conteneur, pas un chiffre publié) | CPIC 88 médicaments / 22 gènes ; DPWG 58 / 15 ; FDA 164 / 27 ; total distinct 197 médicaments, 31 gènes | Échelle de l'outil de référence |
| Validation sur 1000 Genomes | Sangkuhl 2020 | 59 échantillons 1000 Genomes caractérisés GeT-RM ; concordance 100 % (CYP2C19, CYP2C9, CYP3A5, IFNL3, VKORC1), TPMT 58/59, DPYD 56/59 (94,9 %), CYP4F2 36/45 (80 %), UGT1A1 24/45 (53,3 %), SLCO1B1 5/59 (8,5 %) | Limites connues de l'appel d'allèles sur 1000 Genomes |
| Validation | Li 2023 | 133 génomes entiers 1000 Genomes, 10 gènes, 100 % de concordance après revue manuelle | Idem |

## Nos dimensions
- Corpus v14 (gelé 2 nov., ex-v14b corrigée) : 189 médicaments pour le DL, + 21 en règle seule ; 19 gènes avec règle mono-gène utilisable (CYP2B6, CYP2C19, CYP2C9, CYP2D6, CYP3A4, CYP3A5, DPYD, F5, G6PD, HLA-A*31:01, HLA-B*15:02, HLA-B*57:01, HLA-B*58:01, NAT2, NUDT15, SLCO1B1, TPMT, UGT1A1, VKORC1 ; la v14 gelée n'ajoute aucun gène) ; CACNA1S, CFTR, MT-RNR1, RYR1 en règle seule ; 37 colonnes de gènes/allèles dans les profils ; 1 379 profils ; 232 664 lignes.
- Médicaments sans règle mais liés à un gène des profils (couverture maximale v14) : 705 substances, dont 440 avec structure moléculaire (SMILES) — réservoir pour une extrapolation par le DL.

## Ce que ces sources ne démontrent pas
- Aucune ne porte sur un modèle d'apprentissage profond : ce sont des outils à règles ou des études de fréquences. Elles soutiennent l'étendue (gènes, médicaments, cohorte), pas la suffisance de l'entraînement.
- La suffisance de l'entraînement doit s'appuyer sur (a) notre propre courbe d'apprentissage et la variance entre graines, (b) des sources de taille d'échantillon pour modèles prédictifs, non encore recherchées.

## Point de vigilance
- Sherman 2024, Tableau 1 : G6PD figure sans phénotype CPIC dans PyPGx (colonne Phenotype = No). Nos valeurs G6PD (0 / 0,5 / 1) sont un codage du projet : à décrire comme tel dans le chapitre méthodes.
