#!/bin/bash
# Configuration retenue (DL film, identifiant de médicament, poids « racine », EVITER x2, tous les gènes),
# réentraînée avec 4 graines de modèle supplémentaires (1 à 4) ; la graine 0 = résultat phase 2b.
# Découpage en plis identique (comparaison appariée). Ensemble final 10% NON utilisé.
cd /mnt/user-data/outputs
D=corpus_v7/phenotype_drug_dataset_v7.csv
F=/home/claude/drug_fingerprints_v2.pkl
mkdir -p resultats_v9/graines
for g in 1 2 3 4; do
  ( time python3 train_dl_v9_graines.py --data $D --fp $F --out resultats_v9/graines/id_evit2_graine$g --variante film --genes tous --poids racine --empreinte id --poids_evit 2 --graine_modele $g ) > resultats_v9/graines/id_evit2_graine${g}_sortie.txt 2>&1
done
echo FIN > resultats_v9/graines/FIN.txt
