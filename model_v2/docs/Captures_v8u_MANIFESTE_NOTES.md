# Captures d'écran de l'application v8u (§ 5.11) — manifeste

**Ce document ne fait pas partie du mémoire.** Il décrit comment les 12 captures ont été produites, pour pouvoir les justifier.

## Conditions
- Application : `app_pharmageno_v8u.py` **révision 3** (empreinte 5ce6a85b40b9b5b3 ; gabarit résultats ee18bcc2607401dc ; 86/86 tests), modèles `modeles_v15`, domaine `domaine_v15_dev.json`.
- **Correction de ce manifeste** : sa première version indiquait la révision 2 (commit 28c45e7). C'était faux : l'application qui a servi aux captures avait été lancée sur la révision 3, présente dans le dossier de travail sans avoir été livrée. L'écart a été découvert en préparant le chapitre 5 ; Mouna a décidé d'adopter la révision 3 (voir `Application_v8u_corrections_test_manuel_15nov2026.md`). Les captures sont donc conformes au code sauvegardé une fois la révision 3 commitée. Deux de leurs éléments n'existent pas en révision 2 : l'hydralazine dans le bloc orange (fig. 5.4) et la mention « génotype lu chez ce patient : \*1/\*8 » (fig. B.2).
- Lecture du VCF : **réelle**, par PyPGx 0.27.0 et pypgx-bundle 0.27.0 (fichier `VERSION` = 0.27.0, commit e59b8a4), environnement séparé avec pandas 2.3.3 < 3, numpy 2.5.4, pysam 0.24.1, comme le prévoit `installer_pypgx_v7.sh`. Aucun profil rejoué ou injecté.
- Exemple : `paquet_encadrant_v8r/exemples/NA19472.vcf` (sha256 bfe147f24d2746fc), spécialité Cardiologie.
- **Contrôle de fidélité** : les génotypes lus sont identiques à ceux de l'exécution archivée chez Mouna (`results/validation_pharmcat_2personnes/sortie_v8s_NA19472.json`) sur les 22 variables, valeurs codées et génotypes (CYP2C9 \*1/\*8, CYP2C19 \*1/\*17, CYP3A5 \*1/\*6, NAT2 \*5/\*6, TPMT \*3C/\*8…).
- Durée de l'analyse : 86 s (cohérent avec « environ 90 secondes » du § 5.8).
- Navigateur : Chromium (Playwright), fenêtre 1280 px, facteur d'échelle 2. Toutes les captures de la page de résultats viennent d'une même analyse (identifiant 1537e2fecbb5), avant la saisie de laboratoire sauf la capture 12.

## Correspondance figure ↔ fichier
| Figure | Fichier | Contenu |
|---|---|---|
| 5.2 | cap_01_accueil.png | Accueil, NA19472.vcf choisi, Cardiologie |
| 5.3 | cap_02_progression.png | Progression, étape « Lecture des gènes du patient » (recadrée en hauteur) |
| 5.4 | cap_03_resultats_haut.png | Recommandation + « À éviter aussi » (6) |
| 5.5 | cap_04_trois_modeles.png | Avis et scores DL / directive / XGBoost / RF (13 médicaments) |
| 5.6 | cap_06_recherche_warfarin.png | Fiche warfarine, volet « Pourquoi ? » ouvert |
| 5.7 | cap_07_experts_B01AA.png | Détails experts, antivitamines K, volets ouverts |
| 5.8 | cap_08_comment_travaille.png | « Comment le programme a travaillé » |
| 5.9 | cap_09_genes_lus.png | Tableau des gènes lus (22 lignes) |
| 5.10 | cap_05b_completer_rempli.png | Formulaire de laboratoire, valeurs fictives : CYP2D6 lent, HLA-B\*57:01 positif |
| 5.11 | cap_12_apres_completion.png | Résultat après la saisie |
| 5.12 | cap_10_vue_patient.png | Vue patient |
| 5.13 | cap_11_pdf-1.png | Page 1 du rapport PDF (6 pages), avant saisie |

## Chiffres à reprendre dans le § 5.11 (relus sur les captures et les JSON ; ils remplacent ceux du texte v8s)
- **Bloc vert** : antivitamines K (phenprocoumon, acénocoumarol, **warfarine**), statines (6), antiagrégants (4), ibuprofène. **Bloc orange** : fluindione, fluvastatine, hydralazine. « Ce qui change » : CYP2C9 (score 1,5) pour fluindione et fluvastatine.
- **Changement par rapport au texte v8s : la warfarine passe d'« adapter la dose » à « dose standard »**, conséquence de la règle v15 (la règle DPWG CYP2C9 donne « standard » pour la valeur du patient ; VKORC1 de référence). La fiche (fig. 5.6) l'explique : règle CYP2C9 « \*1/\*2 » appliquée à la valeur de codage, génotype lu \*1/\*8 — **c'est la limite connue du codage CYP2C9** (\*1/\*2 et \*1/\*8 ont la même valeur), affichée en toutes lettres par l'application ; à écrire sous la figure. La phrase du texte v8s « le chapitre 7 montre … ignore VKORC1 » est périmée : la règle v15 inclut VKORC1.
- Non évalués de la spécialité : **14** avant saisie → **7** après. À éviter (autres spécialités) : **6 → 14** (7 médicaments CYP2D6 + abacavir + les 6 initiaux). Inchangé par rapport au texte v8s.
- Après saisie : flécaïnide, propafénone, **métoprolol** en orange ; disopyramide, quinidine, **amiodarone, clonidine** en vert. Le défaut du texte v8s (amiodarone, clonidine, métoprolol absents de la carte) est corrigé **par la révision 3** (test T85).
- Décompte du réseau (fig. 5.8) : Adapter 17, Éviter 13, Standard 140, Surveiller 19 = 189 (le texte v8s disait 19 / 13 / 138 / 19).
- Scores (fig. 5.5) : DL ≥ 0,999 partout ; XGBoost 0,908 à 0,991 ; RF 0,494 à 0,716 ; les 4 colonnes d'accord pour les 13 médicaments (le texte v8s disait « douze »).
- PDF : 6 pages ; résumé « 6 à éviter ; 110 compatibles ; 1 à vérifier ; 72 non évalués (60 CYP2D6) » (texte v8s : 111 / 0 / 72). Le médicament « à vérifier » est hors cardiologie : à identifier avant d'écrire la phrase.
- Après saisie (JSON) : 14 à éviter ; 144 compatibles ; 6 à vérifier ; 25 non évalués.

## Limites des captures
- Le bouton de fichier de l'accueil affiche « Choose File » : libellé du navigateur Chromium de capture (ressources de langue anglaises seulement), pas de l'application. Sur un navigateur français, il s'affiche « Choisir un fichier ».
- Défauts d'affichage observés, non corrigés (mineurs, à décider) : phénotypes en anglais dans le tableau des gènes (fig. 5.9 et PDF) alors que l'écran principal est en français (le test T32 ne couvre que l'écran principal) ; « score d'activité 1.5 » avec un point dans le tableau et une virgule ailleurs ; texte de directive sans accents (« Genotype de reference : non cite… ») pour la règle VKORC1 de la warfarine, tel qu'il est dans la table de règles.

## Sauvegarde
`bash ~/sauver_v2.sh "captures v8u NA19472 (12 figures du § 5.11)" captures_v8u.zip` — les `.png` vont dans `Model_v8_7_9_10/fig` et `fabrication/fig`.
