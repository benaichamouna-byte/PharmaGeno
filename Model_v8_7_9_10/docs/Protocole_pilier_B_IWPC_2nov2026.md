# Protocole du pilier B — validation externe sur patients réels (IWPC, warfarine)
Fixé le 2 novembre 2026 AVANT toute comparaison de dose entre groupes génétiques. Aucune règle ni aucun fichier du corpus v14 gelé n'est modifié.

## Objet
Les étiquettes du corpus viennent d'un moteur de règles (guidelines) : le F1 de 0,998 du DL mesure l'accord avec ces règles, pas la justesse clinique. Ici on confronte la règle warfarine du corpus à des patients réels (dose d'entretien stable observée), ce qui donne une validation indépendante des étiquettes.

## Données
- Fichier IWPC « Ethnicity Data Set 2009 » (PS215192) : 6 922 sujets uniques. Le fichier « Combined Data Set 2008 » (PS206767, 5 700 sujets) est inclus en totalité dans le précédent (5 700 identifiants sur 5 700 retrouvés) : il n'est pas utilisé, pour ne pas compter deux fois les mêmes patients.
- Résultat : « Therapeutic Dose of Warfarin » (mg/semaine), analysé en logarithme.
- Population principale : « Subject Reached Stable Dose » = 1, dose renseignée, génotype CYP2C9 consensus parmi *1/*1, *1/*2, *1/*3, *2/*2, *2/*3, *3/*3. Les autres génotypes (*5, *6, *11, *13, *14) n'ont pas de correspondance dans le corpus : exclus et comptés.

## Règle du corpus à valider
Corpus v14 : 394 lignes warfarine, toutes ADAPTER_DOSE (DPWG, CYP2C9 seul, valeurs de profil 0 ; 0,25 ; 0,5 ; 0,75). Il n'existe aucune ligne STANDARD pour la warfarine : *1/*1 (valeur 1,0) est la référence implicite sans règle. La question « ADAPTER_DOSE contre STANDARD » est donc remplacée par « profils ADAPTER_DOSE contre profils *1/*1 ».
Correspondance génotype IWPC -> valeur de profil (score d'activité / 2) : *1/*1 = 1,0 ; *1/*2 = 0,75 ; *1/*3 = 0,5 ; *2/*2 = 0,5 ; *2/*3 = 0,25 ; *3/*3 = 0,0. Classes du corpus : métaboliseur lent (0 ; 0,25), intermédiaire (0,5 ; 0,75).

## Hypothèse principale H1
Les patients étiquetés ADAPTER_DOSE par le corpus (valeur < 1) ont une dose d'entretien plus basse que les *1/*1.
- Estimateur : rapport des moyennes géométriques (exp de la différence des moyennes de log-dose), IC 95 % par bootstrap sur les patients (B = 2 000, graine 0).
- H1 est soutenue si la borne haute de l'IC est < 1. Sinon elle n'est pas soutenue et le résultat est rapporté comme tel.

## Analyses secondaires (déclarées d'avance)
- S1 : même rapport par classe du corpus (lent, intermédiaire) et par génotype.
- S2 : comparaison descriptive avec les pourcentages de la règle DPWG (20 % pour lent, 65 % pour intermédiaire). Ce sont des pourcentages de la dose INITIALE standard, pas de la dose d'entretien : aucun test, description seule.
- S3 : régression de log-dose sur le groupe, ajustée sur âge (milieu de classe), taille, poids, amiodarone, VKORC1 -1639 (nombre d'allèles A), origine (OMB) ; erreurs robustes HC3 ; version avec et sans VKORC1.
- S4 : sensibilité, patients « White » seulement.
- S5 : proportion de doses basses (≤ 21 mg/semaine, seuil fixé par nous) selon le groupe ; sensibilité et spécificité de l'étiquette ADAPTER_DOSE pour « dose basse ».
- S6 (exploratoire, hors règle du corpus) : VKORC1 -1639 (A/A, A/G contre G/G) : la règle warfarine du corpus n'utilise pas ce gène. Part de variance (R²) de log-dose : CYP2C9 seul, VKORC1 seul, les deux.

## Ce qui n'est pas testé ici
- Le DL lui-même : il a appris les étiquettes du moteur de règles ; valider la règle valide donc ce qu'il reproduit. Un test direct (probabilité du DL contre dose) demande les modèles entraînés ; étape suivante possible.
- Une seule molécule (warfarine) : la validation ne couvre pas les 189 médicaments.

## Engagements
Résultats rapportés tels quels (positifs, nuls ou négatifs), sans changer le protocole après coup ; toute analyse ajoutée ensuite est étiquetée « post hoc ».
