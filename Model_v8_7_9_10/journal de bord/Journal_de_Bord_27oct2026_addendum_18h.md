# Journal de Bord PharmaGeno — 27 octobre 2026 — addendum 18h
(complète l'addendum 16h10 ; ce fichier a la priorité là où ils diffèrent)

## 1) Décisions validées
- Mouna a validé l'option A (« ok fais ») : règle CPIC « Moderate/Strong demandant une dose plus basse = ADAPTER_DOSE, Optional = inchangé » ; « alternative OU surveillance » = SURVEILLER. Détail dans results/audit_regles_ecran_texte_v1/DECISIONS_REGLES_V11_27oct2026.md.
- Règles v11 (data/regles_v11_monogene.csv, regles_v11_multigene.csv) : 9 règles modifiées (citalopram, escitalopram, sertraline x3 + 2 multigènes, oxycodone x3, azathioprine TPMT lent). Corpus v11 : data/corpus_v11/phenotype_drug_dataset_v11.csv (157 432 lignes).
- Vérifié sans changement : TPMT/NUDT15 (CPIC thiopurines, 35 lignes lues), SLCO1B1 (catégories CPIC, 60 lignes lues sur plus).

## 2) Résultat mesuré (DL, 5 graines x 5 plis, mêmes réglages, validation croisée seule, jeu final non lu ; 2 min 44 s)
- Corpus v10 : F1 macro 0,9964 +/- 0,0003 ; erreurs strictes 0,0061 +/- 0,0008 ; précision EVITER 0,9930 ; exactitude 0,9986 ; ECE 0,0071.
- Corpus v11 : F1 macro 0,9955 +/- 0,0002 ; erreurs strictes 0,0060 +/- 0,0006 ; précision EVITER 0,9950 ; exactitude 0,9977 ; ECE 0,0071.
- Lecture : le F1 baisse de 0,0009 alors que 1 894 étiquettes ont été corrigées d'après les textes (ADAPTER_DOSE des antidépresseurs et SURVEILLER de l'oxycodone, plus nuancés que l'ancien STANDARD/EVITER). Les corpus ne sont pas comparables ligne à ligne. Aucune conclusion d'amélioration ou de dégradation du modèle n'est tirée ; on n'a PAS choisi les règles pour maximiser le score. Analyse des erreurs par médicament à faire.

## 3) Erreurs à ne plus reproduire (ajouts)
- Lancer deux entraînements dans le même dossier de sortie : l'ancien processus a écrit dans le dossier du nouveau (fin.txt à 17h55:01, avant la vraie fin à 17h57:41). Règle : un dossier de sortie par lancement ; vérifier debut/fin et l'heure des fichiers avant de lire un résultat.
- Affirmer un nombre de règles modifiées sans le recompter (un décompte « 501 » venait d'une comparaison de cases vides ; le vrai nombre est 9).

## 4) Plan exact restant
1. UGT1A1 : relire contre l'API CPIC ; statines : relire les lignes restantes (simvastatine, pravastatine, rosuvastatine, lovastatine, pitavastatine).
2. Analyse des erreurs du DL par médicament sur le corpus v11 (oof_moyenne_graines.npz).
3. Test de bout en bout lecteur VCF -> profils (1 379) : zéro différence attendu.
4. Adapter app, moteur, lecteur au codage v9/v11 ; corrections de l'application.
5. Protocole v9 écrit (à montrer avant l'entraînement final) ; recherche d'hyperparamètres sur validation seule ; UN réentraînement ; combinaisons cachées ; validation indépendante ; gel du protocole ; UNE lecture du jeu final de 138 profils ; paquet de déploiement.
6. Chapitres 3 à 8 ; groupes B puis C. Date exacte du dépôt à demander à l'encadrant.
