#!/bin/bash
# Expérience « médicament jamais vu » : 5 modèles/témoins, même découpage groupé par médicament.
cd /mnt/user-data/outputs
D=corpus_v7/phenotype_drug_dataset_v7.csv
F=/home/claude/drug_fingerprints_v2.pkl
O=resultats_v9/medicament_inconnu
mkdir -p $O
for m in majorite genes_xgb rf xgb dl; do
  ( time python3 train_medicament_inconnu_v1.py --data $D --fp $F --out $O/$m --modele $m ) > $O/${m}_sortie.txt 2>&1
done
echo FIN > $O/FIN.txt
