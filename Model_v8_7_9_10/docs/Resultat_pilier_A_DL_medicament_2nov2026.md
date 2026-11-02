# Résultat du pilier A — DL qui généralise à des médicaments jamais vus (2 novembre 2026)

Corpus v14 gelé (189 médicaments, 232 664 lignes ; 1 241 profils hors ensemble final de 138 familles). Scripts : `construire_descripteurs_medicaments_v1.py`, `evaluer_dl_medicament_v1.py`, `analyser_dl_medicament_v1.py`. Sorties : `results/dl_medicament_v1/` (résultats par graine, prédictions hors-échantillon, `analyse_bootstrap.csv`, `analyse_bootstrap_sans_exclus.csv`, `prospectif_par_medicament*.csv`).

## Protocole
- Entrée du DL : profil génétique (une-hot) + descripteurs du médicament sans aucune source de guideline : liens gène-médicament (relationships, annotations de variants, meilleur niveau d'annotation clinique), classes ATC 1/4/5, empreinte de Morgan 512 bits. Variantes : `lien`, `lien+atc`, `lien+atc+fp`, `porte:lien+atc+fp`.
- Trois schémas : (1) validation en laissant des médicaments de côté (quasi-doublons regroupés), (2) en laissant de côté une classe ATC de niveau 3, (3) prospectif : entraînement sur les 176 médicaments de v13, test sur les 13 ajoutés depuis.
- Références : majoritaire, `prior_gene_phenotype` (fréquence de classe par gène et phénotype), `voisins_k5`.
- 3 graines. Intervalles à 95 % par bootstrap sur les médicaments (unité de généralisation = le médicament, 400 tirages) ; différences appariées DL − référence. Le calcul rapide du bootstrap a été vérifié contre scikit-learn (écart maximal 2·10⁻¹⁶).

## Résultats (AUROC « non-STANDARD », moyenne des graines, IC 95 %)
| Schéma | DL lien | DL lien+atc | DL lien+atc+fp | DL porte | prior_gene_phenotype | voisins_k5 |
|---|---|---|---|---|---|---|
| Médicament (189) | 0,774 [0,726 ; 0,823] | 0,769 [0,725 ; 0,826] | 0,723 [0,672 ; 0,787] | 0,725 [0,675 ; 0,789] | 0,817 [0,779 ; 0,855] | 0,781 [0,730 ; 0,835] |
| Classe ATC | 0,693 | 0,697 | 0,654 | 0,662 | 0,790 [0,750 ; 0,825] | 0,769 [0,718 ; 0,822] |
| Prospectif (13) | 0,818 [0,691 ; 0,959] | 0,706 | 0,806 | 0,805 | 0,883 [0,763 ; 0,996] | 0,877 [0,783 ; 0,978] |

Différences appariées (schéma médicament) : DL lien − prior = −0,043 [−0,079 ; −0,009] ; DL lien − voisins = −0,007 [−0,043 ; +0,028] ; les variantes avec empreinte moléculaire sont plus basses (−0,09 vs prior, −0,06 vs voisins, IC excluant 0). Précision moyenne (AP) schéma médicament : DL 0,38 à 0,43 contre prior 0,416 [0,366 ; 0,477] et voisins 0,460 [0,383 ; 0,549] ; différences DL − prior de l'AP : IC incluant 0 pour les quatre variantes (équivalence non démontrée, mais aucune supériorité) ; DL − voisins : IC excluant 0 pour les variantes avec empreinte. Schéma classe ATC : AUROC et AP du DL inférieurs aux deux références, IC excluant 0. Prospectif : AP du DL 0,17 à 0,37 contre 0,64 à 0,66 pour les références (IC excluant 0 pour DL − prior).

F1 macro (schéma médicament) : DL 0,41 à 0,44 ; voisins_k5 0,483 [0,427 ; 0,555] ; prior 0,244. Le DL dépasse prior (+0,16 à +0,20), mais prior prédit presque toujours STANDARD (rappels EVITER 0,00, ADAPTER_DOSE 0,03) : ce n'est pas un gain comparable. Contre voisins_k5, le DL est inférieur (−0,04 à −0,09, IC excluant 0). Rappels du DL `lien` (moyenne des graines, sans IC) : EVITER 0,49, ADAPTER_DOSE 0,27, SURVEILLER 0,28 ; voisins_k5 : 0,38 / 0,32 / 0,15.

## Analyse de sensibilité (sans les six ajouts à preuve plus faible : chlorpropamide, glipizide, tolazamide, nitrite de sodium, eltrombopag, lusutrombopag, retirés du test seulement)
Mêmes conclusions : schéma médicament AUROC DL `lien` 0,767 contre prior 0,809 ; différences DL − prior −0,04 à −0,09, DL − voisins −0,01 (IC incluant 0) pour `lien`/`lien+atc`. Prospectif : 7 médicaments seulement, IC très larges (par exemple DL `lien` 0,716 [0,603 ; 0,912], prior 0,722 [0,510 ; 0,981]) : aucune conclusion possible.

## Lecture (sans extrapoler)
- Dans ce protocole, le DL à descripteurs de médicament **ne dépasse pas** les références simples sur l'AUROC ; il est équivalent à voisins_k5 pour `lien` et `lien+atc`, et inférieur à `prior_gene_phenotype`. L'ajout de l'empreinte moléculaire dégrade les résultats.
- La référence `prior_gene_phenotype` est forte : une grande partie du signal « non-STANDARD » dépend de la rareté du profil génétique, pas du médicament.
- Limites : 189 médicaments seulement ; descripteurs de lien plus riches pour les médicaments déjà couverts par une guideline que pour les médicaments de déploiement (décalage de distribution) ; test prospectif sur 13 (7) médicaments ; 3 graines.
- Conséquence : pas d'intégration du pilier A à l'application. À rapporter comme résultat exploratoire négatif dans le mémoire (chapitre résultats / limites). Toute reprise (autre architecture, autres descripteurs) demande un nouveau protocole fixé avant de regarder le test.

## Rappels de rigueur
- Aucun réglage sur le jeu de test ; l'ensemble final de 138 familles n'a jamais été lu.
- Chiffres issus de `analyse_bootstrap*.csv` (copie ci-dessus à 3 décimales).
