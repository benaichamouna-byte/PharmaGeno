# Journal de Bord du Projet PharmaGeno - 20 octobre 2026, midi (suite du journal du matin)

## 0. Règles absolues (inchangées)
- Le DL est le CŒUR du sujet et de l'application : ne jamais le reléguer.
- Rien n'est écrasé ; une seule action demandée à Mouna à la fois ; chaîne de sauvegarde WSL -> Windows -> GitHub -> Drive.
- Ne jamais annoncer une suite sans l'exécuter dans le même tour.

## 1. Décisions et constats de la matinée
- Drive : lot_app_v8_moteur_20oct2026.zip confirmé (1,6 Mo). Les 4 étapes de sauvegarde sont faites pour ce lot.
- **Erreur de méthode corrigée (Mouna, 10h58)** : les lots zip servent de copie de secours (tailles exactes) mais ne sont pas lisibles par l'encadrant dans Drive/GitHub (aperçu : liste de noms seulement, pas d'ouverture de fichier). Nouvelle règle : en plus des zips, publier des fichiers ordinaires rangés PAR TYPE dans les dossiers existants du Drive (scripts, docs, data, results, journal de bord), avec un fichier d'accueil dans docs ; le Drive entier est destiné à l'encadrant ; GitHub et Drive contiennent désormais des fichiers lisibles. Les zips restent comme copie de secours.
- Couche de recommandation v8 (recommandation_v8.py) : spécialité, à éviter (tout avis EVITER du DL, de XGBoost ou de la règle), alternatives (même ATC4, statut ok, STANDARD), à vérifier, non évalués, référence seule ; test_recommandation_v8.py : I1 à I7 PASS sur 80 profils x 17 spécialités (6 741 fiches).
- Lecteur de VCF v8 (vcf_to_profile_v8.py) : 18 gènes lus par PyPGx 0.27.0 + 4 allèles HLA saisis ; codage identique à celui des profils d'entraînement ; test_codage_vcf_v8.py : 9 gènes dépendant du génotype, 1 379 profils, 0 différence avec profils_genes_v4.csv. Test de bout en bout (PyPGx réel) sur HG00101 : 17 gènes sur 17 identiques. Validation élargie (19 échantillons, 323 comparaisons) : 321 identiques, 2 écarts. (1) G6PD HG00698 : DÉFAUT du lecteur trouvé par la validation : homme, génotype haploïde sur chrX, lu « variable » au lieu de « déficient » ; corrigé (normaliser_chrX_haploide), vérifié sur ce cas (17/17), test unitaire T4. (2) CYP2B6 HG00127 : « indéterminé » PyPGx laissé non déterminé alors que le corpus v3 l'avait codé 1,0 (choix délibéré du lecteur). Détail : docs/BILAN_validation_vcf_v8.txt.
- Conséquence mesurée : depuis un VCF, CYP2D6 n'est pas lisible -> les médicaments dépendant de CYP2D6 (bêtabloquants, antiarythmiques, etc.) sortent « non évalués » (exemple HG00101, Cardiologie : 13 non évalués contre 6 avec le profil du corpus).
- Constat DL (test_invariance_genes_v8.py, 300 profils, 58 médicaments dépendants du génotype, profils vus à l'entraînement) : en remplaçant les gènes non requis, l'action du DL change dans 0,39 % des cas (XGBoost 0,95 %) ; 14 médicaments touchés pour le DL contre 4 pour XGBoost ; variation maximale de P(EVITER) 0,95 (DL) et 0,86 (XGBoost). Exemple : fluvastatine, confiance du DL 0,92 avec le profil du corpus contre 0,99 avec le profil lu du VCF (HLA-B*57:01 et CYP2D6 différents, non pertinents pour ce médicament). Piste d'amélioration centrée sur le DL (masque médicament-gène, entraînement avec perturbation des gènes non pertinents) ; à décider par Mouna.

## 2. Erreurs à ne plus reproduire (ajouts)
- Sauvegarder uniquement des zips quand l'encadrant doit pouvoir lire : toujours fournir des fichiers lisibles en plus.
- Nommer un dossier « pour l'encadrant » (tout le Drive lui est destiné), puis un dossier daté (lot_20oct2026) : l'encadrant cherche PAR TYPE (scripts, docs, results) et ne connaît pas les dates. Règle : ranger chaque fichier dans le dossier de son type ; la date sert aux sauvegardes zip, pas à la navigation.
- Toutes les erreurs des journaux du 19 oct. et du 20 oct. matin.

## 3. Plan restant
1. Sauvegarde du lot du 20 oct. midi (arborescence encadrant + fichiers à plat) sur les 4 supports.
2. Application web v8 (Flask, modèles, PDF) à côté de la v7 ; test avec profils réels ; comparaison avec une prédiction d'une étude publiée.
3. Décision de Mouna : rôle propre du DL (A niveau variants, B abstention/robustesse dont masque médicament-gène, piste 1 relations médicament-gène ClinPGx).
4. Hyperparamètres (validation seulement ; même budget XGBoost/RF ; plusieurs graines pour tous) ; évaluation finale UNE SEULE FOIS sur l'ensemble final (12 524 lignes) ; chapitres 3 à 8 ; plan Excel.
5. Ouvert : date du dépôt (~12 nov.) vs disponibilité de l'encadrant (15 nov.) ; envois Drive en attente (Tableau_de_bord_PharmaGeno_15oct2026.pdf, pharmageno_app_v7b.zip) ; fichiers v7 non suivis sur GitHub.
