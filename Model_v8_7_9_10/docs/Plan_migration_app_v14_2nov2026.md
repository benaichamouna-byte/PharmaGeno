# Plan de migration de l'application vers le corpus v14 (2 novembre 2026, état des lieux)
## Constat (lecture seule)
- Application la plus récente : `app_pharmageno_v8p.py` (et templates_v8p). Elle charge `modeles_v9` (DL profil v2 et DL choix v2) et `domaine_v9.json` : **133 médicaments**, corpus v8.
- Aucun modèle entraîné sur v13 ou v14 n'existe : les résultats v13 (config 35 + calibration, F1 macro 0,998) sont des validations croisées. Il faut donc RÉENTRAÎNER pour l'application.
- Corpus v14 : 189 médicaments ; les 133 de l'application y sont tous ; **56 sont à ajouter**.
## Les 56 à intégrer : ATC
- 54 ont un code ATC dans les exports ClinPGx ; 2 sans code (deuruxolitinib, sodium ascorbate) ; plusieurs combinaisons à codes multiples (ex. lidocaine / prilocaine : 8 codes).
- Table d'ajouts (nouveau fichier) : `data/atc_mapping_medicaments_v14_ajouts_a_valider.csv` ; les lignes « à valider » demandent un choix de code de référence (source à citer : index ATC de l'OMS).
## Étapes
1. Table ATC des 56 (48 médicaments sur 56 prêts, 8 « à valider » : 3 codes incomplets, 2 sans code, 3 combinaisons à codes multiples), puis dérivation de `specialite_atc` et `alternatives_atc4` pour les nouveaux médicaments (fichiers v14 NOUVEAUX, anciens intacts).
2. `domaine_v10.json` (189 médicaments) et règles : `regles_v14_monogene.csv` + `regles_v13_multigene.csv`.
3. Réentraînement du DL profil et du DL choix sur corpus v14, réglages FIXÉS (config 35 déjà choisie sur v13, pas de nouveau réglage), calibration par température, seuils d'abstention ; évaluation en validation croisée groupée par famille, ensemble final de 138 familles non lu.
4. Moteur (adapter `moteur_v9i` à l'architecture v13 si elle diffère), app v8q + templates, textes « 133 » -> « 189 » (à relire un par un).
5. Tests (`test_app_v8p.py` adapté), comparaison v8p / v8q sur profils de démonstration et VCF réels, vérification que les 21 médicaments « règle seule » s'affichent avant d'écrire « 210 ».
6. Sauvegarde quadruple ; anciennes versions conservées (v8p, modeles_v9 intacts).
## Points de décision (par défaut si non contredits)
- Réglages DL : config 35 de v13, inchangés ; la comparaison avec v8 est rapportée telle quelle.
- Second avis : l'application garde son second modèle actuel, réentraîné sur v14 pour rester cohérent.
