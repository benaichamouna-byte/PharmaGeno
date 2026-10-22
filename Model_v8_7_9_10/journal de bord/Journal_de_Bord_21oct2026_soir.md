# Journal de Bord du Projet PharmaGeno : 21 octobre 2026, soir (17 h 30)

Complète les journaux de l'après-midi (rien n'est écrasé). « Mesuré » = affiché sur la machine de Mouna ou par un contrôle explicite.

## 1. Décisions
- Priorité de Mouna (14 h 36) : l'application d'abord, avec un DL le plus optimal possible. Objectif du DL (règle absolue, ne plus le redemander) : profil génétique en entrée, médicament(s) en sortie.
- Application v8f : branchée sur le DL « profil -> médicaments » (1 à 3 médicaments par spécialité). Démarrage sur la réponse « quoi faire now » (interprétée comme : donne la prochaine action). Les corrections prévues de l'application (message si aucun gène lisible, faux message « aucun médicament à éviter », contradiction multi-gènes « non interprété », étiquette « version 8b », médicaments indépendants du génotype) restent à valider une par une.
- Le modèle de l'application = DL profil, réglages identiques à ceux de la validation croisée (non ajustés), ensemble final non lu.

## 2. Mesures
- Sauvegarde du lot de l'après-midi : WSL, Windows (295 = 295), GitHub (commit 73b838f, 286 fichiers suivis), Drive : 15 fichiers sur 15 retrouvés dans les bons dossiers (scripts 3, results 2 + dl_profil_v1 3 + combinaisons_cachees_profil_v1 3, docs 1, journal de bord 3) ; tailles identiques aux miennes pour les scripts, la note et les journaux. Le total de 286 sur Drive est un calcul (211 + 60 + 15), pas un comptage récursif.
- `scripts/modele_final_profil_v1.py` (md5 a1a486539da128e8b570e5ecc1cf7477, 5 867 octets, vérifié chez Mouna) lancé chez elle : 1 116 profils d'entraînement, 125 de validation interne, 138 profils (12 524 lignes) de l'ensemble final non lus (1 116 + 125 + 138 = 1 379). 112 époques, 12 s. Fichiers écrits dans `modeles_v8f/` (modèle `.pt`, seuils d'abstention, validation interne, configuration).
- Validation interne (125 profils) : F1 macro 1,0 ; CER strict 0,0 ; précision EVITER 1,0 ; logloss 0,0043 ; ECE 0,0041. Lecture prudente : petit effectif, étiquettes = règles CPIC, ce n'est pas l'évaluation finale et cela ne prouve pas que le DL combine mieux que les règles.
- Seuils d'abstention (quantiles de la probabilité maximale hors-plis) : 0,005 -> 0,8595 ; 0,010 -> 0,9073 ; 0,020 -> 0,9442 ; 0,050 -> 0,9766.

## 3. Erreurs à ne plus reproduire
- Les erreurs des journaux précédents (redemander un objectif déjà donné ; garder le médicament en entrée du DL ; test de combinaisons sans contrôle de non-présence ; script envoyé par carte de fichier sans somme de contrôle).
- Messages trop longs quand Mouna demande « brièvement » : écrire UNE ligne « ce que je fais maintenant », exécuter, puis expliquer après (consigne du 21 oct., 16 h 56).
- Terminer une réponse par une question de validation quand l'action suivante est évidente et sans risque : donner directement l'action (sauf entraînement ou choix de direction).

## 4. Plan restant (chaque étape validée par Mouna)
1. Sauvegarde WSL -> Windows -> GitHub -> Drive de : `scripts/modele_final_profil_v1.py`, `modeles_v8f/` (4 fichiers), ce journal.
2. `moteur_v8f.py` (charge `modele_final_profil_v1.pt`, un passage du DL donne tous les médicaments) et `app_pharmageno_v8f.py` + tests ; garder v8e intact.
3. Essai de Mouna avec `HG00101.vcf` (barre de progression, captures) ; mail à l'encadrant (brouillon prêt, non envoyé).
4. Décisions de Mouna : trou escitalopram (CYP2C19 0, 1,5, 2,0 sans conseil dans le moteur ; Nguyen 2024 Table 2 : UM/PM = rouge) ; correspondance de nos 4 classes avec les 3 couleurs ; mots HLA « positif / négatif » ; date de dépôt (vers le 12 nov., non confirmée).
5. Étendre le test des combinaisons (plus de tirages, thiopurines, carbamazépine, phénytoïne) ; échec rosuvastatine ; défaut HLA-B*58:01.
6. Comparaison avec PharmCAT (`~/pharmcat_test/out/HG00101.report.json`) et une étude publiée ; réglage léger du DL sur validation seule ; évaluation finale unique sur les 12 524 lignes ; chapitres 3 à 8 ; Plan Excel.
7. Points ouverts : fichier parasite à la racine GitHub (`rf, columns, classes = load_rf_model()`), anciens fichiers `??` non suivis, commit 494a50e « Unverified », dépôts Drive en attente (`Tableau_de_bord_PharmaGeno_15oct2026.pdf`, `pharmageno_app_v7b.zip`), nettoyage des zips Windows (après liste), NAT2/CYP2A6 et HLA vs GeT-RM, source du multi-tâche à vérifier avant citation.
