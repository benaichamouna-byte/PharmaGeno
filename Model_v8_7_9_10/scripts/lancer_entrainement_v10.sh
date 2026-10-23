#!/bin/bash
# Entraînement sur le corpus v8 (133 médicaments), protocole_commun_v9 (ensemble final FIXÉ aux 138 familles, jamais lu). Réglages des modèles INCHANGÉS par rapport aux v1.
cd "$(dirname "$0")"
D=../data/corpus_v8/phenotype_drug_dataset_v8.csv
F=/home/claude/drug_fingerprints_v2.pkl
R=../results
mkdir -p $R/dl_profil_v2 $R/dl_choix_v2 ../modeles_v9
( time python3 train_dl_profil_v2.py --data $D --fp $F --out $R/dl_profil_v2 ) > $R/dl_profil_v2_log.txt 2>&1
( time python3 train_dl_choix_v2.py  --data $D --fp $F --out $R/dl_choix_v2 ) > $R/dl_choix_v2_log.txt 2>&1
( time python3 modele_final_profil_v2.py --data $D --fp $F --oof $R/dl_profil_v2/oof_moyenne_graines.npz --out ../modeles_v9 ) > $R/modele_final_profil_v2_log.txt 2>&1
( time python3 modele_final_choix_v2.py --data $D --fp $F --out ../modeles_v9 ) > $R/modele_final_choix_v2_log.txt 2>&1
echo FIN > $R/FIN_entrainement_v10.txt
