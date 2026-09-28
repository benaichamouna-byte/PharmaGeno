# Reconstruction des identifiants d individu et de famille

Jeu de donnees : **46371 lignes**, 31 genes, 530 medicaments
SHA256 : `9a933859545ebe15fbf858422db5d2b69516662f9aadc3a130f5104e3abb327a`

## Appariement

Chaque ligne du jeu de donnees a ete confrontee au fichier intermediaire 
`phenotype_drug_dataset_1kg.csv`, qui avait conserve la colonne `sample`. 
La cle d appariement combine les 16 phenotypes geniques communs, le medicament et l action.

| | Lignes | Part |
|---|---|---|
| Rattachees a un individu sequence | 36049 | 77.7 % |
| Issues du corpus documentaire | 10322 | 22.3 % |

Les lignes non rattachees proviennent de PharmGKB, CPIC, ClinVar et de la FDA. 
Ce sont des associations documentaires, non des profils d individus sequences : 
elles ne peuvent recevoir aucun identifiant. Chacune forme un groupe a elle seule, 
ce qui les rend neutres vis-a-vis du groupement lors de la validation croisee.

## Structure familiale

| | Valeur |
|---|---|
| Individus sequences identifies | 1379 |
| Familles distinctes | 1378 |
| Familles comptant plusieurs membres | 1 |
| Individus apparentes | 2 (0.1 %) |
| Lignes concernees | 82 (0.2 %) |

## Portee

Un individu apparente a un autre partage une part substantielle de son genome. 
Si un parent figure dans le pli d entrainement et son enfant dans le pli de test, 
la performance mesuree est optimiste : le modele a deja vu un profil proche. 
Les identifiants reconstruits permettent d imposer qu une famille entiere reste 
du meme cote de la separation, au moyen d un `StratifiedGroupKFold` sur `family_id`.

## Colonnes ajoutees

- `sample_id` — identifiant de l individu 1000 Genomes, ou identifiant documentaire `DOC_n`
- `family_id` — identifiant de famille ; un trio parent-parent-enfant en partage un seul