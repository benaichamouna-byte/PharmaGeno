# PharmaGeno : état du projet au 20 octobre 2026 (à lire en premier)

Mémoire : *A Deep Learning based Webtool for Mutation-Aware Drug Recommendation* (M.Sc. Bioinformatique, ENSI). Dépôt prévu vers le 12 novembre (à confirmer) ; soutenance en décembre 2026.

Les fichiers sont rangés par type : `scripts`, `docs`, `data`, `results`, `journal de bord`. Tous s'ouvrent directement dans Drive ou GitHub. Les nombres de version (`_v7`, `_v8`, `_v9`) donnent l'ordre du travail. Non inclus : les probabilités hors-pli (`.npz`, volumineuses) et les anciennes versions du corpus (v4 à v6), conservées dans les zips des lots précédents.

## 1. Le projet en 6 lignes
- Données : 1 379 profils pharmacogénétiques réels (1000 Genomes) × 117 médicaments. Les profils sont calculés par PyPGx 0.27.0 et les tables CPIC ; 130 578 lignes profil × médicament sont étiquetées par un moteur de règles CPIC/DPWG (`construire_corpus_v3.py`, inchangé) en 4 actions : STANDARD, SURVEILLER, ADAPTER_DOSE, EVITER.
- Modèle central : réseau de neurones « PharmaGenoDL » (variante film : attention sur les gènes pilotée par le médicament). XGBoost et Random Forest servent de références, avec le même protocole.
- Protocole : validation croisée en 5 plis groupés par famille (graine 42) ; 10 % des familles mis de côté (12 524 lignes, 138 familles), **jamais lus à ce jour**, à utiliser une seule fois à la fin.
- Application v8 : le DL produit la recommandation ; la règle CPIC est affichée à côté avec sa source, et une alerte signale tout désaccord. Une couche de sécurité empêche le modèle de répondre hors de ce qu'il a appris (médicament inconnu, gène requis manquant, combinaison jamais vue).
- Lecteur de VCF : un VCF patient donne un profil de 22 gènes (18 lus par PyPGx, 4 allèles HLA saisis). Validation de bout en bout sur 19 échantillons 1000 Genomes : 321 comparaisons sur 323 identiques au profil d'entraînement ; les 2 écarts sont expliqués dans `docs/BILAN_validation_vcf_v8.txt` (un défaut du lecteur sur G6PD chez l'homme, corrigé ; un choix délibéré sur un résultat « indéterminé »).

## 2. Résultats mesurés (corpus v7, validation croisée)
| Modèle | F1 macro | EVITER manqués |
|---|---|---|
| XGBoost (1 graine) | 0,9999 | 0,0011 |
| Random Forest (1 graine) | 0,9817 | 0,0489 |
| DL film, empreinte moléculaire, poids inverses | 0,9687 | 0,0131 |
| DL film, identifiant de médicament, EVITER ×2 (5 graines) | 0,9980 ± 0,0010 | 0,0029 ± 0,0010 |

- **Aucune mesure ne montre, à ce jour, d'avantage du DL sur XGBoost avec ces étiquettes issues de règles** ; c'est écrit tel quel. L'écart sur les EVITER manqués (0,0029 contre 0,0011) n'est pas tranché : XGBoost n'a qu'une graine.
- **Médicament jamais vu** (plis groupés par médicament) : F1 macro DL 0,467, RF 0,502, XGBoost 0,454 ; les écarts entre modèles sont du même ordre que l'écart-type entre plis (0,08 à 0,09) ; EVITER manqués 63 à 70 %. Un modèle entraîné sur des génotypes ne peut pas, aujourd'hui, prédire de façon fiable pour un médicament absent de l'entraînement : l'application affiche « non évalué ».
- **Abstention** (1 % des cas les moins sûrs) : le DL passe de 15,6 à 4,6 EVITER manqués (lignes) ; XGBoost de 6 à 0. Ce n'est pas un avantage propre au DL (XGBoost est mieux calibré : ECE 0,0002 contre 0,0055).
- **Sensibilité aux gènes non pertinents** (`results/test_invariance_genes_v8_*`) : en remplaçant les gènes qui ne gouvernent pas le médicament par ceux d'un autre profil, l'action change dans 0,39 % des cas pour le DL et 0,95 % pour XGBoost ; le DL est touché sur 14 médicaments, XGBoost sur 4 ; la probabilité d'EVITER du DL peut varier fortement dans quelques cas (maximum 0,95). Mesuré sur des profils vus à l'entraînement : c'est une sensibilité, pas une exactitude. Piste d'amélioration centrée sur le DL.

## 3. Où trouver quoi
| Dossier | Contenu |
|---|---|
| `scripts` | tous les scripts Python et shell, à plat (les scripts s'appellent entre eux par chemins relatifs) : construction du corpus (`construire_*`), protocole et entraînement (`protocole_commun_v8.py`, `train_*`, `lancer_*`), application (`moteur_v8.py`, `regle_cpic_v8.py`, `recommandation_v8.py`, `modele_final_v8.py`), lecteur de VCF (`vcf_to_profile_v8.py`, `valider_vcf_v8.py`, `analyser_vcf_v8.py`), tests (`test_*`) |
| `data` | corpus v7, profils de gènes v4, tables de règles corrigées, codage PyPGx, HLA, tables ATC / spécialités / alternatives, domaine de validité (`domaine_v8.json`), tables CPIC extraites de PharmCAT |
| `results` | sorties des scripts (`*_sortie.txt`), résultats d'entraînement (`resultats_v9/` par pli, par graine, « médicament jamais vu »), modèles déployables (`resultats_final_v8/`), validation du lecteur de VCF (`validation_vcf_v8/`), test de sensibilité aux gènes, exemples de fiches |
| `docs` | ce fichier, notes de chaque lot (`LISEZ_MOI_lot_*`), rapport P1 sur le lecteur de VCF, bilan de validation du lecteur |
| `journal de bord` | décisions, erreurs à ne pas répéter, plan restant (versions résumées ; journaux complets dans le projet de travail) |

## 4. Intégrité et limites (à lire avant de juger les résultats)
- Les étiquettes sont déterministes (règles) et les entrées du DL sont des phénotypes déjà calculés (PyPGx + CPIC) : le DL apprend en grande partie une table. C'est la limite principale du dispositif ; elle est reconnue et le rôle propre du DL (niveau variants, médicament nouveau) reste à décider.
- Ensemble final : l'ancien (15 oct., protocole v7) et le nouveau partagent 13 familles ; rien n'a été choisi sur l'ensemble final ; le nouveau n'a jamais été lu.
- 30 765 des 161 343 paires profil × médicament (19,1 %) n'ont aucune action de référence (valeur sans règle ou gène manquant).
- 4 médicaments sans empreinte moléculaire (5 400 lignes) : pegloticase, rasburicase, sulfaméthoxazole/triméthoprime, vitamine K ; ils n'ont que la règle de référence.
- HLA typé pour 508 profils sur 1 379 ; CYP2D6 n'est pas lisible depuis un VCF de SNV : les médicaments qui en dépendent sortent « non évalués » à partir d'un VCF.
- Les tests de mécanique (moteur, recommandation, sensibilité) portent sur des profils vus à l'entraînement : ils vérifient la logique, pas la performance.
- Liste complète des limites : `journal de bord/Journal_de_Bord_19oct2026_soir.md`, section 4.

## 5. Reste à faire
Hyperparamètres (même budget pour XGBoost/RF, plusieurs graines pour tous) ; évaluation finale unique sur l'ensemble mis de côté ; application web v8 (Flask, PDF) ; comparaison avec une prédiction d'une étude publiée ; rédaction des chapitres 3 à 8.
