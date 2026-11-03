# Migration de l'application vers le corpus v14 : résultat (3 novembre 2026)

## Ce qui a été fait (v8p, modeles_v9 et domaine_v9 restent intacts)
- Table ATC v14 : `atc_mapping_medicaments_v14.csv` (530 lignes v1 inchangées + 30 ajouts sourcés ClinPGx) ; 8 médicaments sans code ATC fiable et 3 sans spécialité restent des limites documentées.
- Domaine : `domaine_v10.json` (189 médicaments, tous dans le modèle, 131 dépendent du génotype), construit avec `construire_domaine_v8.py` inchangé, règles `regles_v14_monogene.csv` + `regles_v13_multigene.csv`.
- DL profil v14 : `modele_final_profil_v3.py` -> `modeles_v10/modele_final_profil_v3.pt` (configuration 35 fixée en v13, calibration par température T = 0,233, seuils d'abstention sur la probabilité maximale hors pli). Entraînement sur 1 116 profils, validation interne 125 profils ; ensemble final (138 familles, 23 249 lignes) NON lu.
- DL choix v14 : `train_dl_choix_v3.py` / `modele_final_choix_v3.py` (réglages v2 inchangés : 2 x 256, BatchNorm, Dropout 0,3) -> `modeles_v10/modele_final_choix_v3.pt` ; 44 classes ATC niveau 4.
- Second avis : `modele_final_xgb_v3.py` -> `modeles_v10x/` (réglages v2 inchangés).
- Moteur `moteur_v10f.py`, `moteur_v10g.py`, `moteur_v10i.py` (copies de v9, qui restent intactes) ; application `app_pharmageno_v8q.py` + `templates_v8q` ; test `test_app_v8q.py`.

## Mesures (validation croisée groupée par famille, ensemble final non lu)
- DL profil v14 (25 entraînements, config 35 + calibration) : F1 macro 0,9979 ± 0,0012 ; log-loss 0,0030 ± 0,0017 ; ECE 0,0003 ; EVITER manqués 60,2 / 7 227 (0,83 %) ; faux EVITER 8,4. Équivalent à v13 (0,9980).
- DL choix v14 (5 graines x 5 plis, 44 classes) : choix dans l'ensemble recommandé sur les cas informatifs 99,99 % ± 0,01 (référence sans le profil : 99,09 %) ; ensemble exact retrouvé 98,99 % (référence : 38,9 %) ; Jaccard 0,9973 (référence : 0,7275) ; choix d'un médicament EVITER quand EVITER est possible : 0,007 % (référence : 0,07 %). Le gain sur la référence est surtout visible sur l'ensemble exact et le Jaccard ; sur « choix dans S » la référence est déjà à 99,1 %.
- Second avis : validation interne uniquement (exactitude 1,0, log-loss 0,0157) ; aucune validation croisée refaite.

## Tests
- `test_app_v8q.py` : 53 tests PASS (« TOUT PASSE »), sortie dans `results/test_app_v8q_sortie.txt`. Ils vérifient la logique et l'affichage, pas la performance.
- Comparaison v8p / v8q sur 40 profils de développement (hors ensemble final), 4 249 couples (profil, médicament) communs aux deux versions : 98,6 % identiques ; les 59 désaccords (oxycodone, sertraline, citalopram, escitalopram, AINS) sont tous des règles modifiées entre le corpus v8 et le corpus v14 ; v8q suit l'étiquette v14 dans 59 cas sur 59, v8p dans 0. Limite : ces profils ont été vus à l'entraînement, ce n'est pas une mesure de généralisation.
- Non refait : lecture réelle d'un VCF par PyPGx avec v8q (test à refaire sur la machine de Mouna ou avec l'environnement PyPGx).

## « 210 médicaments » : NON confirmé
Les 21 médicaments « règle seule » (`data/regles_reference_seule_v13.csv` : MT-RNR1 33 lignes, RYR1 14, CACNA1S 14, CFTR 3, HLA-B*57:01, HLA-B*15:02) ne sont pas dans `domaine_v10.json` ni affichés par v8q (ni v8p). Chiffre à écrire dans le mémoire pour l'outil : 189 médicaments (DL + règle) ; les 21 sont à présenter comme règles documentées non intégrées, sauf intégration ultérieure (décision de conception à prendre : entrée mitochondriale / HLA saisi, conditions cliniques).

## Textes
Les nombres de médicaments dans l'application sont calculés (len du domaine) ; aucun « 133 » en dur dans le code de v8q hors commentaires historiques de l'en-tête. Le tableau PERFORMANCES a été mis à jour avec les valeurs v14 (il n'est pas affiché dans les gabarits actuels).
