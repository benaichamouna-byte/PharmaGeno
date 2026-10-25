# Journal de Bord du Projet — 25 octobre 2026 (couvre les 24 et 25 octobre)

Titre du mémoire : A Deep Learning based Webtool for Mutation-Aware Drug Recommendation. Dépôt vers le 12 novembre (non confirmé) ; soutenance en décembre 2026. Sujet : un OUTIL WEB de RECOMMANDATION de médicaments : le clinicien envoie le VCF d'un patient et une spécialité, le DL lit tout le profil génétique, la page donne une réponse claire (✔ / ▲ / ✖). Le DL est au centre.

Rappel de définition (à répéter dès qu'on parle de « corpus ») : corpus = le tableau de données de lignes (profil du patient × médicament → action) sur lequel les modèles sont entraînés et testés. Version actuelle : corpus v8 (152 600 lignes, 133 médicaments, 1 379 profils réels 1000 Genomes ; 147 200 lignes étiquetées, 129 médicaments modélisés).

## 1. Décisions prises et validées
- Statistiques, figures et comparaison de modèles : exigées dès le début pour le mémoire et l'encadrant ; faites le 24-25 octobre sur le corpus v8, protocole commun v9 (5 plis groupés par famille, graine 42, 33 variables génétiques, ensemble final de 138 familles = 14 731 lignes jamais lu).
- Méthode statistique : bootstrap par famille (Field et Welsh 2007), 2 000 rééchantillonnages, mêmes familles pour tous les modèles ; ECE à 15 intervalles (Guo et al. 2017) ; test t corrigé de Nadeau et Bengio (2003) sur les 5 plis ; McNemar exact (Dietterich 1998), indicatif seulement.
- Document d'avancement pour l'encadrant : envoyé par e-mail le 25 octobre (avec le titre complet du mémoire, sans le nom du projet « PharmaGeno » dans l'e-mail). Titre du document = titre du mémoire ; le nom de l'encadrant n'y figure plus ; colonne « Date » retirée du tableau « étape par étape » ; phrase sur la réunion retirée. Rendez-vous du lundi 26 octobre à 14 h reporté (message WhatsApp + e-mail), nouvelle date à confirmer (mardi proposé).
- Le document contient maintenant : captures de l'application (6), figures 1 à 6, comparaison des modèles, tableau des fichiers avec liens Drive.
- Paquet de déploiement = dossier unique pour installer et lancer l'application ailleurs (code, modèles entraînés, données, versions de logiciels, notice, sommes md5). Version de test v8m existe (pharmageno_test_v8m.zip, 5 Mo) ; le paquet FINAL sera refait après gel de la version (règles ambiguës appliquées, corpus v9, réentraînement unique).

## 2. Résultats mesurés (corpus v8, prédictions hors-pli, 132 469 lignes, 1 241 familles)
- DL profil v2 (moyenne de 5 graines) : F1 macro 0,9986 [0,9977 ; 0,9993] ; « à éviter » manqués 0,0019 [0,0008 ; 0,0031] ; précision « à éviter » 0,9976 ; ECE 0,0059.
- XGBoost : F1 macro 0,9995 [0,9989 ; 1,0000] ; manqués 0,0009 ; précision 1,0000 ; ECE 0,0002.
- Forêt aléatoire : F1 macro 0,9819 [0,9784 ; 0,9852] ; manqués 0,0451 ; ECE 0,0587.
- Toujours « standard » : F1 macro 0,2326.
- DL moins XGBoost : F1 −0,0009 [−0,0015 ; −0,0005] (XGBoost un peu meilleur, intervalle sans zéro) ; McNemar 1 contre 52 ; Nadeau–Bengio p = 0,059 (5 plis, faible puissance). DL moins forêt : F1 +0,0167 [+0,0135 ; +0,0200] ; p = 0,0004.
- Limite : sorties du DL = moyenne de 5 graines, arbres = 1 exécution par pli (favorise légèrement le DL). Les étiquettes viennent des règles : fidélité aux règles, pas bénéfice clinique.
- Tests sur situations jamais vues (DL seul, anciennes versions, corpus v7) : médicament jamais vu F1 macro DL 0,467 / XGBoost 0,454 / forêt 0,502 (écarts du même ordre que l'écart entre plis, aucun test statistique) ; combinaisons de gènes cachées : exactitude 0,81 en moyenne sur les cas informatifs (3 tirages, 0,57 à 1,00). Comparaison avec XGBoost sur les combinaisons cachées : NON faite.
- Captures de l'application v8m (VCF de test NA19085, 1000 Genomes) : analyse complète 85 s ; clopidogrel à éviter (CYP2C19 intermédiaire) ; défaut : l'en-tête affiche « version 8l ».

## 3. Erreurs à ne plus reproduire
- Écrire qu'un test « n'est pas fait » sans relire les journaux (tests médicament jamais vu et combinaisons cachées existaient pour le DL).
- Tuer un processus par `ps | grep | awk | xargs kill` avec le nom du programme dans la même commande : la commande elle-même est tuée (code 144). Utiliser `fuser -k <port>/tcp`. Idem pour `pkill -f`.
- Lancer l'application sur le port 5061 pour une capture Chromium (port refusé) ; lancer l'application sans `--pgx-python <pgxenv>/bin/python --bundle <pypgx-bundle>` (l'analyse du VCF échoue).
- Bootstrap : ne jamais sommer la log-loss sur les rééchantillonnages (diviser par n) ; garder le même ordre de familles pour tous les modèles.
- Oublier la définition du corpus à la première mention ; écrire « Claude a vérifié ».
- Placer des fichiers dans les anciens dossiers Drive (Results, scripts d'origine) : les ranger dans Model_v8_7_9_10/scripts et /results.
- Donner plusieurs actions à la fois ; deviner des chemins WSL.

## 4. Plan exact de ce qui reste (dans l'ordre)
1. Sauvegarder le lot du 25 octobre (scripts train_arbres_v9.py, comparaison_modeles_v2.py ; résultats arbres_v9_rf, arbres_v9_xgb, comparaison_modeles_v2 ; captures de l'application ; journal) : WSL → Windows → GitHub → Drive.
2. Ranger sur le Drive : figures_modele_v2.py → Model_v8_7_9_10/scripts ; dossier figures_modele_v2 → Model_v8_7_9_10/results ; mettre à jour le tableau de fichiers du document.
3. Confirmer la nouvelle date de réunion avec l'encadrant ; partager le dossier Drive avec lui.
4. Comparer le DL et XGBoost sur les combinaisons de gènes cachées (et médicament jamais vu, corpus v8) ; envisager une régression logistique comme référence.
5. Examiner les règles ambiguës (59 mono-gène, 22 multi-gènes), construire le corpus v9 et le protocole v9, UN seul réentraînement.
6. Élargir la liste : groupe B (27 médicaments), groupe C (24).
7. Validation indépendante du DL (tamoxifène/CYP2D6 ITPC et autres couples avec sources).
8. Corriger l'application : rouge trop sévère (CYP2C19 rapide), noms de groupes en français, message si aucun gène lisible, indication non demandée, libellé « version 8l ».
9. Geler le protocole d'évaluation par écrit, UNE évaluation finale des trois modèles sur les 138 familles réservées (14 731 lignes).
10. Figer la version et refaire le paquet de déploiement et de test (nouveaux md5) ; vérifier que le paquet contient les données du corpus v8 et non du v7 (le zip de test actuel contient phenotype_drug_dataset_v7.csv).
11. Chapitres 3 à 8 du mémoire (listes DOME et TRIPOD+AI à remplir) ; plan Excel ; e-mail d'avancement à l'encadrant (fait pour le 25 oct.).

## 5. Sauvegarde / État d'avancement
Document d'avancement envoyé. Paquet de test v8m non figé. Rien n'est écrit dans l'ensemble final.
