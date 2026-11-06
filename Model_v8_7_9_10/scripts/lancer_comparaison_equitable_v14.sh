#!/usr/bin/env bash
# lancer_comparaison_equitable_v14.sh (4 nov. 2026) : enchaîne les six étapes de la comparaison équitable DL / XGBoost / RF sur le corpus v14.
# Protocole : Protocole_comparaison_equitable_DL_XGB_RF_v14_4nov2026.md (à lire AVANT de lancer). Tout est REPRENABLE : relancer le script reprend là où il s'est arrêté
# (les étapes de recherche sautent les couples (configuration, pli) déjà faits ; les évaluations réécrivent leurs fichiers de la graine concernée).
# À lancer depuis le dossier scripts/ du projet, dans WSL :   bash lancer_comparaison_equitable_v14.sh <NB_COEURS>      (NB_COEURS = résultat de la commande  nproc)
# L'ensemble final (138 familles) n'est lu par AUCUNE de ces étapes.
set -euo pipefail
NJ="${1:?donner le nombre de coeurs (commande nproc)}"
DATA=../data/corpus_v14/phenotype_drug_dataset_v14.csv
R=../results
mkdir -p $R
echo "== 1/6 recherche DL (40 configurations x 5 plis) sur v14 : $(date)"
for p in $(seq 0 $((NJ-1))); do python3 recherche_hp_dl_v4.py --n 40 --part $p --parts $NJ --data $DATA --out $R/dl_hp_v14 > $R/log_dl_hp_v14_part$p.txt 2>&1 & done; wait
echo "== 2/6 evaluation DL (config choisie par pli, 5 graines, calibration) : $(date)"
for p in $(seq 0 $((NJ-1))); do python3 evaluer_dl_imbrique_v5.py --graines 5 --part $p --parts $NJ --quoi choisie_cal --data $DATA --hp $R/dl_hp_v14 --out $R/dl_imbrique_v14_equitable > $R/log_dl_eval_v14_part$p.txt 2>&1 & done; wait
echo "== 3/6 recherche XGBoost : $(date)"
python3 recherche_hp_arbres_v1.py --modele xgb --part 0 --parts 1 --threads $NJ --data $DATA --out $R/hp_arbres_v14_xgb 2>&1 | tee -a $R/log_hp_xgb_v14.txt
echo "== 4/6 evaluation XGBoost : $(date)"
python3 evaluer_arbres_imbrique_v1.py --modele xgb --quoi choisie_cal --graines 5 --threads $NJ --data $DATA --hp $R/hp_arbres_v14_xgb --out $R/eval_arbres_v14_xgb 2>&1 | tee -a $R/log_eval_xgb_v14.txt
echo "== 5/6 recherche puis evaluation Random Forest : $(date)"
python3 recherche_hp_arbres_v1.py --modele rf --part 0 --parts 1 --threads $NJ --data $DATA --out $R/hp_arbres_v14_rf 2>&1 | tee -a $R/log_hp_rf_v14.txt
python3 evaluer_arbres_imbrique_v1.py --modele rf --quoi choisie_cal --graines 5 --threads $NJ --data $DATA --hp $R/hp_arbres_v14_rf --out $R/eval_arbres_v14_rf 2>&1 | tee -a $R/log_eval_rf_v14.txt
echo "== 6/6 analyse : $(date)"
python3 comparaison_equitable_v14_v1.py --out $R/comparaison_equitable_v14 --dl $R/dl_imbrique_v14_equitable:choisie_cal --xgb $R/eval_arbres_v14_xgb:choisie_cal --rf $R/eval_arbres_v14_rf:choisie_cal --extra "DL c35 fige (modele de l'application)=$R/dl_imbrique_v14:c35_cal" 2>&1 | tee $R/log_comparaison_equitable_v14.txt
echo "TERMINE : $(date)"
