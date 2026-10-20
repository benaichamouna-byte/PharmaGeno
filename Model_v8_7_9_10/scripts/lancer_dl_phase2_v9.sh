#!/bin/bash
# DL film, protocole v8 inchangé, corpus v7, tous les gènes, poids « racine » (meilleure configuration de la phase 1).
# Phase 2, points 1-2 : facteur de poids sur EVITER (x2, x4, x8) puis identifiant de médicament appris à la place de l'empreinte.
cd /mnt/user-data/outputs
D=corpus_v7/phenotype_drug_dataset_v7.csv
F=/home/claude/drug_fingerprints_v2.pkl
mkdir -p resultats_v9/phase2
for f in 2 4 8; do
  ( time python3 train_dl_v9.py --data $D --fp $F --out resultats_v9/phase2/dl_film_racine_evit$f --variante film --genes tous --poids racine --poids_evit $f ) > resultats_v9/phase2/dl_film_racine_evit${f}_sortie.txt 2>&1
done
( time python3 train_dl_v9.py --data $D --fp $F --out resultats_v9/phase2/dl_film_racine_id --variante film --genes tous --poids racine --empreinte id ) > resultats_v9/phase2/dl_film_racine_id_sortie.txt 2>&1
echo FIN > resultats_v9/phase2/FIN.txt
