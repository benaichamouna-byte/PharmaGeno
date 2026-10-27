# Journal de Bord PharmaGeno — 27 octobre 2026 — addendum 16h10
(complète l'addendum 13h40 ; ce fichier a la priorité là où ils diffèrent)

## 1) Décisions validées / faites
- Profils complets : PyPGx DPYD terminé (15h08 -> 15h53, 45 min mesurées) ; data/profils_genes_v6_complet.csv = 8 gènes recalculés avec le lecteur v9 (ABCG2 59, CYP2B6 117, CYP2C19 20, CYP3A5 1, DPYD 5, UGT1A1 1 valeurs modifiées ; 203 lignes de différences dans profils_v6_complet_differences_vs_v5.csv). Le fichier provisoire profils_genes_v6.csv est conservé tel quel (rien d'écrasé).
- Contrôle des 14 autres gènes PyPGx contre le lecteur : 0 différence pour ADRB2, CFTR, CYP1A2, CYP2A6, CYP3A4, CYP4F2, G6PD, MTHFR, NAT2, NUDT15, SLCO1B1, TPMT, VKORC1. Écarts sur CACNA1S, RYR1 (profil 0,5 « Uncertain Susceptibility » vs lecteur : non déterminé) et IFNL3 (profil vide pour 687 patients vs lecteur : 1,0) : sans effet sur le DL actuel (ces gènes ne sont pas dans ses entrées), à traiter avec le groupe B.
- Règles v10 (data/regles_v10_monogene.csv, regles_v10_multigene.csv) : 1 correction, métoprolol CYP2D6 = 0 : STANDARD -> ADAPTER_DOSE (texte CPIC « lowest recommended starting dose »). Corpus v10 : data/corpus_v10/phenotype_drug_dataset_v10.csv, 157 432 lignes, 133 médicaments, 1 379 profils (STANDARD 133 540 | ADAPTER_DOSE 14 667 | EVITER 8 453 | SURVEILLER 772).
- Un indéterminé n'est plus codé « normal » : 384 lignes retirées du corpus (gène indéterminé), 7 ajoutées ; 41 étiquettes changées entre le premier corpus v9 et celui des profils v6 (dont 5 profils DPYD *5/*9A recodés de 0,5 à 1,0).

## 2) Résultats mesurés (DL, 5 graines x 5 plis, mêmes réglages, validation croisée seule, jeu final de 138 familles non lu)
- Corpus v9 (profils v5)            : F1 macro 0,9966 +/- 0,0007 ; erreurs strictes 0,0053 ; précision EVITER 0,9934 ; ECE 0,0076 ; 34 entrées.
- Corpus v9 (profils v6 complets)   : F1 macro 0,9963 +/- 0,0003 ; erreurs strictes 0,0061 +/- 0,0004 ; précision EVITER 0,9941 ; ECE 0,0074 ; 37 entrées ; 3 min 35 s.
- Corpus v10 (v6 + règle métoprolol) : F1 macro 0,9964 +/- 0,0003 ; erreurs strictes 0,0061 +/- 0,0008 ; précision EVITER 0,9930 ; exactitude 0,9986 ; ECE 0,0071 ; 2 min 29 s.
- Les trois corpus ne sont pas strictement comparables (les lignes diffèrent) : les écarts (0,0002 à 0,0003 de F1) sont de l'ordre de l'écart-type, donc aucune conclusion de « mieux / moins bien » n'est tirée. Ces chiffres ne sont PAS ceux du mémoire (hyperparamètres encore fixés a priori, protocole non gelé).

## 3) Contrôle des règles contre leur texte (results/audit_regles_ecran_texte_v1/)
- Écran par mots-clés : 123 monogènes + 39 multigènes signalées, toutes lues. 1 erreur confirmée (métoprolol, corrigée en v10). Phénytoïne/fosphénytoïne : pas d'erreur d'étiquette dans le corpus (la règle DPWG « adapter la dose » l'emporte) ; la table CPIC sépare bien AS 1,0 (25 % de moins) et AS 1,5 (aucun ajustement).
- À trancher : sertraline/citalopram/escitalopram CYP2C19 intermédiaire et sertraline CYP2B6 intermédiaire (« lower maintenance dose » en option, actuellement STANDARD) ; oxycodone (EVITER) vs propafénone/flécaïnide (SURVEILLER) pour des textes « alternative OU surveillance ».
- Limite : l'écran ne voit pas une erreur dont le texte ne contient aucun des mots recherchés.

## 4) Erreurs à ne plus reproduire (ajouts)
- Laisser un script de reconstruction écraser un fichier déjà sauvegardé (profils_genes_v6.csv a été réécrit par construire_profils_v6.py ; remis en place depuis l'archive).
- Lancer un calcul en arrière-plan avec nohup : il est arrêté ; utiliser le mode arrière-plan de l'outil.
- Conclure à une erreur de règle sans regarder l'étiquette finale du corpus (phénytoïne : le moteur combine plusieurs règles).

## 5) Plan exact restant
1. Trancher les règles « à trancher » (section 3), avec la force de recommandation lue sur CPIC.
2. Vérifier TPMT, NUDT15, SLCO1B1, UGT1A1 contre les classes CPIC (non fait).
3. Test lecteur VCF v9 contre le corpus pour les 1 379 profils (8 gènes) : zéro différence attendu.
4. Adapter app, moteur, lecteur au codage v9 (CYP2C9 en score d'activité, indéterminés -> manquant) ; corrections de l'application.
5. Protocole v9 écrit (à montrer avant l'entraînement final) ; recherche d'hyperparamètres sur validation seule (Bergstra & Bengio 2012) ; UN réentraînement ; combinaisons cachées ; validation indépendante ; gel du protocole ; UNE lecture du jeu final de 138 profils ; paquet de déploiement.
6. Chapitres 3 à 8 ; groupes B puis C si les données existent. Date exacte du dépôt à demander à l'encadrant.
