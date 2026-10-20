#!/bin/bash
# DL film, protocole v8 inchangé, corpus v7, tous les gènes, poids « racine ».
# Phase 2b : identifiant de médicament + EVITER x2 ; empreinte + identifiant (hybride) sans puis avec EVITER x2.
cd /mnt/user-data/outputs
D=corpus_v7/phenotype_drug_dataset_v7.csv
F=/home/claude/drug_fingerprints_v2.pkl
mkdir -p resultats_v9/phase2b
run() { ( time python3 train_dl_v9.py --data $D --fp $F --out resultats_v9/phase2b/$1 --variante film --genes tous --poids racine "${@:2}" ) > resultats_v9/phase2b/$1_sortie.txt 2>&1; }
run dl_film_racine_id_evit2 --empreinte id --poids_evit 2
run dl_film_racine_hybride --empreinte hybride
run dl_film_racine_hybride_evit2 --empreinte hybride --poids_evit 2
echo FIN > resultats_v9/phase2b/FIN.txt
