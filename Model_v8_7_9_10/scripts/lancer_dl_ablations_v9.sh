#!/bin/bash
# DL film, protocole v8 inchangé, corpus v7 : 5 combinaisons gènes (tous/règles) x poids de classes (inverse/racine/aucun). La combinaison tous+inverse = référence déjà faite (resultats_v9/dl_film).
cd /mnt/user-data/outputs
D=corpus_v7/phenotype_drug_dataset_v7.csv
F=/home/claude/drug_fingerprints_v2.pkl
mkdir -p resultats_v9/ablations
for cfg in "regles inverse" "tous racine" "tous aucun" "regles racine" "regles aucun"; do
  set -- $cfg
  ( time python3 train_dl_v9.py --data $D --fp $F --out resultats_v9/ablations/dl_film_$1_$2 --variante film --genes $1 --poids $2 ) > resultats_v9/ablations/dl_film_$1_$2_sortie.txt 2>&1
done
echo FIN > resultats_v9/ablations/FIN.txt
