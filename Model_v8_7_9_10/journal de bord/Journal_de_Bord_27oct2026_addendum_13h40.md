# Journal de Bord PharmaGeno — 27 octobre 2026 — addendum 13h40
(complète Journal_de_Bord_27oct2026.md ; ce fichier a la priorité là où ils diffèrent)

## 1) Décisions validées (ajouts)
- Dépôt du mémoire en novembre 2026 (date exacte : à demander à l'encadrant).
- Le DL et l'application restent le cœur ; XGBoost/RF seulement dans la section comparaison.
- CYP2C9_manquant ajouté aux entrées du DL : 34 entrées (au lieu de 33), sortie 129 médicaments x 4 actions.
- Les profils du corpus sont recalculés avec la même chaîne que le lecteur VCF (PyPGx 0.27.0 + coder_gene de vcf_to_profile_v9.py) pour supprimer le décalage entraînement/service.
- Sauvegarde : un MANIFESTE (liste + empreinte sha256 de chaque fichier) accompagne chaque archive ; le script vérifie WSL et Windows avec ce manifeste ; Drive = le même dossier, vérifié par moi contre le manifeste.

## 2) Résultats mesurés aujourd'hui
- Entraînement DL sur le corpus v9 (premier jeu de profils, v5), 5 graines x 5 plis, mêmes réglages que le journal du 19 oct : F1 macro 0,9966 +/- 0,0007 ; erreurs strictes (EVITER manqué) 0,0053 +/- 0,0007 ; précision EVITER 0,9934 ; exactitude 0,9987 ; ECE 0,0076 (results/dl_profil_v3/). Le 19 oct (corpus v8) : 0,9980 / 0,0029 / 0,992. Comparaison NON équivalente : le corpus a changé (règles ambiguës tranchées, CYP2C9 recodé, 157 809 lignes). À refaire sur le corpus final.
- Durée mesurée : environ 16 s par entraînement ; 5 graines x 5 plis = 157 s.
- Profils recalculés (data/profils_genes_v6.csv) : 198 valeurs différentes de v5 sur 7 gènes (ABCG2 59, CYP2B6 117, CYP2C19 20, CYP3A5 1, UGT1A1 1 ; CYP2C9 et F5 : 0). DPYD n'est PAS encore recalculé : profils_genes_v6.csv est PROVISOIRE (7 gènes sur 8). Une version complète portera un nom différent ; rien n'est écrasé.
- Le corpus v9 actuel est construit avec profils v5 : il sera reconstruit avec la version complète des profils v6 avant tout entraînement final.

## 3) Erreurs à ne plus reproduire (ajouts)
- Livrer des lots partiels de fichiers sans liste complète : Windows, WSL, GitHub et Drive n'avaient pas les mêmes fichiers. Règle : une archive complète + manifeste sha256, vérification dans la même commande.
- Dire « c'est bon » pour Drive sans l'avoir vérifié dans la liste réelle de Drive.
- Lancer un calcul en arrière-plan quand la demande du moment est la sauvegarde.

## 4) Plan exact restant
1. Relancer et terminer PyPGx DPYD (predict-alleles -> call-genotypes -> call-phenotypes) ; il s'était arrêté après import.
2. construire_profils_v6.py --pgx /home/claude/pgxrun -> profils complets ; reconstruire le corpus v9 final ; comparer avec le premier v9.
3. Réentraîner le DL (5 graines x 5 plis, validation croisée seule) ; comparer.
4. Relire ligne par ligne l'API CPIC phénytoïne/fosphénytoïne ; vérifier TPMT/NUDT15/SLCO1B1/UGT1A1 (classes regroupant plusieurs scores).
5. Adapter app, moteur, lecteur VCF au codage v9 ; corrections de l'application ; protocole v9 écrit (à montrer avant l'entraînement final) ; recherche d'hyperparamètres sur validation seule ; un seul réentraînement ; combinaisons cachées ; validation indépendante ; gel du protocole ; UNE lecture du jeu final de 138 profils ; paquet de déploiement.
6. Chapitres 3 à 8 ; groupes B puis C si les données existent.
