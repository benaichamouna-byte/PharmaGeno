#!/bin/bash
# Entraînement complet sur le corpus v7, protocole v8 INCHANGÉ (mêmes scripts train_arbres_v8.py / train_dl_v8.py / protocole_commun_v8.py). Résultats dans resultats_v9/ ; resultats_v8/ reste intact.
cd /mnt/user-data/outputs
D=corpus_v7/phenotype_drug_dataset_v7.csv
F=/home/claude/drug_fingerprints_v2.pkl
mkdir -p resultats_v9
( time python3 train_arbres_v8.py --data $D --fp $F --out resultats_v9/xgb --modele xgb --threads 2 ) > resultats_v9/xgb_sortie.txt 2>&1
( time python3 train_arbres_v8.py --data $D --fp $F --out resultats_v9/rf --modele rf --threads 2 ) > resultats_v9/rf_sortie.txt 2>&1
( time python3 train_dl_v8.py --data $D --fp $F --out resultats_v9/dl_film --variante film ) > resultats_v9/dl_film_sortie.txt 2>&1
echo FIN > resultats_v9/FIN.txt
