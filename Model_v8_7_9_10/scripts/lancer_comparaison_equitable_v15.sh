#!/usr/bin/env bash
# lancer_comparaison_equitable_v15.sh (12 nov. 2026) : refait sur le corpus v15 les sept etapes de la comparaison equitable DL / XGBoost / RF,
# protocole INCHANGE (Protocole_comparaison_equitable_DL_XGB_RF_v14_4nov2026.md + Amendement 1 du 5 nov.). Seul le corpus change : v14 -> v15.
# Pourquoi les recherches d'hyperparametres sont REFAITES et non reprises de la v14 : le § 1 du protocole supprime l'asymetrie n 5
# (reglage choisi sur un autre corpus dont les familles de test ont servi ailleurs). Reutiliser hp_arbres_v14_* ou dl_hp_v14 sur la v15
# reintroduirait ce biais de selection. Le seul reglage volontairement NON refait est la configuration 35 du DL (etape 1),
# qui est par definition le modele fige de l'application, choisi sur la v13 : c'est un bras de reference, pas un bras regle.
# Tout est REPRENABLE : relancer le script reprend ou il s'est arrete. L'ensemble final (138 familles) n'est lu par AUCUNE etape.
# 12 nov. 22 h 30 : dl_hp_v13 ayant ete supprime, l'etape 1 lit configs.json dans dl_hp_v14 ; le fichier est deterministe (graine 0, espace fixe,
#                   aucune lecture des donnees) donc identique, et l'etape 0 verifie le contenu de la config 35 et non le nom du dossier.
# Usage depuis le dossier scripts/ du projet, dans WSL :   bash lancer_comparaison_equitable_v15.sh $(nproc)
set -euo pipefail
cd "$(dirname "$0")"
NJ="${1:?donner le nombre de coeurs : bash lancer_comparaison_equitable_v15.sh \$(nproc)}"
DATA="${2:-../data/corpus_v15/phenotype_drug_dataset_v15.csv}"
R=../results
mkdir -p $R

echo "===================== 0/7 VERIFICATIONS BLOQUANTES : $(date) ====================="
for f in "$DATA" ../data/regles_v15_monogene.csv ../data/regles_v15_multigene.csv \
         ../data/profils_ensemble_final_v1.txt evaluer_dl_imbrique_v6.py recherche_hp_dl_v4.py \
         recherche_hp_arbres_v1.py evaluer_arbres_imbrique_v1.py arbres_coeur_v1.py \
         dl_coeur_v4.py protocole_commun_v10.py comparaison_equitable_v14_v1.py comparaison_equitable_v14_v2.py; do
  [ -f "$f" ] || { echo "ABSENT : $f  -> NE PAS LANCER."; exit 1; }
done
# Etape 1 : la configuration 35 est definie dans configs.json. Ce fichier ne depend QUE de la graine 0 et d'un espace fixe
# (recherche_hp_dl_v4.configs : np.random.RandomState(0), aucune lecture des donnees), donc il est identique en v13, v14 et v15.
# dl_hp_v13 a ete supprime ; on lit dl_hp_v14 et on verifie le CONTENU de la config 35, ce qui est plus fort qu'un test d'existence.
HPC=$R/dl_hp_v14
[ -f $HPC/configs.json ] || { echo "ABSENT : $HPC/configs.json (la config 35 y est definie). NE PAS LANCER."; exit 1; }
python3 - "$HPC/configs.json" <<'PYV' || { echo "ECHEC : la configuration 35 n'est pas celle du modele de l'application. NE PAS LANCER."; exit 1; }
import json, sys
C = json.load(open(sys.argv[1]))
att = {'couches':2,'largeur':1024,'dropout':0.1,'bn':False,'act':'relu','lr':0.001,'wd':0.0001,'lot':64,'w_exp':0.5,'ev_x':1.0,'lissage':0.05,'patience':25}
assert len(C) >= 36, f"{len(C)} configurations, au moins 36 attendues"
obt = {k: C[35].get(k) for k in att}
assert obt == att, f"config 35 DIFFERENTE\n  obtenue  : {obt}\n  attendue : {att}"
print("config 35 CONFORME : 2 couches, 1024, sans BatchNorm, dropout 0.1, lissage 0.05")
print("  -> identique a celle de la v13, telle que documentee dans recherche_hp_dl_v4.configs_tour2")
PYV
echo "lignes du corpus v15 (en-tete comprise) : $(wc -l < "$DATA")   [attendu 234633]"
echo "scripts REUTILISES SANS MODIFICATION, empreintes du protocole du 4 nov. (doivent afficher OK) :"
cat > /tmp/empreintes_v15.txt <<'EOS'
99389477c3ab63fee3ea27783e4c24651d64233856644c10b36bd081ea469a6f  arbres_coeur_v1.py
c67b5cbe94783c6f74c051e32e99aa4ffd5c99125a78d1a3671827a2ca9a9dd7  recherche_hp_arbres_v1.py
26e1fe5bce46fc65fe080abe8da9174db38954ba1a27f74511133527593caf1e  evaluer_arbres_imbrique_v1.py
c92a8d41e82bd56c3de181e1cec0233781e8b7906279c4afdc87d20014cd28dd  comparaison_equitable_v14_v1.py
63658d2674625a82788d05c178c362c1a265137970b3096fc98f00c4cb198d41  dl_coeur_v4.py
e95f09033fd83b8c810dbac51a92e7fe116adcd158d578f42cd5918fe5836039  protocole_commun_v10.py
5b387919434c040982075f2af2f3c4e42e37478f9d452b6c01c1134a988da1cd  evaluer_dl_imbrique_v5.py
73176f3d5101e23043b2dcb5a64f7364cb0289203871b5f20d71c33c11b7fda4  recherche_hp_dl_v4.py
EOS
sha256sum -c /tmp/empreintes_v15.txt || { echo "ECHEC : un script reutilise a change. NE PAS LANCER. Me signaler le fichier."; exit 1; }
echo "empreintes des fichiers NOUVEAUX de la v15, enregistrees AVANT execution (tracabilite) :"
sha256sum "$DATA" ../data/regles_v15_monogene.csv ../data/regles_v15_multigene.csv \
          evaluer_dl_imbrique_v6.py comparaison_equitable_v14_v2.py "$0" | tee $R/empreintes_avant_v15.txt
python3 -c "import numpy,pandas,scipy,sklearn,xgboost,torch;print('numpy',numpy.__version__,'| pandas',pandas.__version__,'| scipy',scipy.__version__,'| scikit-learn',sklearn.__version__,'| xgboost',xgboost.__version__,'| torch',torch.__version__)"
echo "coeurs : $NJ | memoire libre (Go) : $(free -g | awk '/Mem:/{print $7}') | disque libre (Go) : $(df -BG --output=avail . | tail -1 | tr -dc 0-9)"

echo "===================== 1/7 DL config 35 figee = MODELE DE L'APPLICATION : $(date) ====================="
# Place en premier a dessein : c'est ce bras qui debloque la regeneration de l'application, les captures et les 104 personnes.
for p in $(seq 0 $((NJ-1))); do python3 evaluer_dl_imbrique_v6.py --graines 5 --part $p --parts $NJ --quoi c35_cal \
  --data "$DATA" --hp $HPC --regles_mono ../data/regles_v15_monogene.csv --regles_multi ../data/regles_v15_multigene.csv \
  --out $R/dl_imbrique_v15 > $R/log_dl_c35_v15_part$p.txt 2>&1 & done; wait

echo "===================== 2/7 recherche DL (40 configurations x 5 plis) sur v15 : $(date) ====================="
for p in $(seq 0 $((NJ-1))); do python3 recherche_hp_dl_v4.py --n 40 --part $p --parts $NJ --data "$DATA" \
  --out $R/dl_hp_v15 > $R/log_dl_hp_v15_part$p.txt 2>&1 & done; wait

echo "===================== 3/7 evaluation DL (config choisie par pli, 5 graines, calibration) : $(date) ====================="
for p in $(seq 0 $((NJ-1))); do python3 evaluer_dl_imbrique_v6.py --graines 5 --part $p --parts $NJ --quoi choisie_cal \
  --data "$DATA" --hp $R/dl_hp_v15 --regles_mono ../data/regles_v15_monogene.csv --regles_multi ../data/regles_v15_multigene.csv \
  --out $R/dl_imbrique_v15_equitable > $R/log_dl_eval_v15_part$p.txt 2>&1 & done; wait

echo "===================== 4/7 recherche XGBoost : $(date) ====================="
python3 recherche_hp_arbres_v1.py --modele xgb --part 0 --parts 1 --threads $NJ --data "$DATA" --out $R/hp_arbres_v15_xgb 2>&1 | tee -a $R/log_hp_xgb_v15.txt

echo "===================== 5/7 evaluation XGBoost : $(date) ====================="
python3 evaluer_arbres_imbrique_v1.py --modele xgb --quoi choisie_cal --graines 5 --threads $NJ --data "$DATA" --hp $R/hp_arbres_v15_xgb --out $R/eval_arbres_v15_xgb 2>&1 | tee -a $R/log_eval_xgb_v15.txt

echo "===================== 6/7 recherche puis evaluation Random Forest : $(date) ====================="
python3 recherche_hp_arbres_v1.py --modele rf --part 0 --parts 1 --threads $NJ --data "$DATA" --out $R/hp_arbres_v15_rf 2>&1 | tee -a $R/log_hp_rf_v15.txt
python3 evaluer_arbres_imbrique_v1.py --modele rf --quoi choisie_cal --graines 5 --threads $NJ --data "$DATA" --hp $R/hp_arbres_v15_rf --out $R/eval_arbres_v15_rf 2>&1 | tee -a $R/log_eval_rf_v15.txt

echo "===================== 7/7 analyse (v1 du protocole ET v2 de l'amendement 1) : $(date) ====================="
python3 comparaison_equitable_v14_v1.py --data "$DATA" --out $R/comparaison_equitable_v15_v1 \
  --dl $R/dl_imbrique_v15_equitable:choisie_cal --xgb $R/eval_arbres_v15_xgb:choisie_cal --rf $R/eval_arbres_v15_rf:choisie_cal \
  --extra "DL c35 fige (modele de l'application)=$R/dl_imbrique_v15:c35_cal" 2>&1 | tee $R/log_comparaison_v15_v1.txt
python3 comparaison_equitable_v14_v2.py --data "$DATA" --out $R/comparaison_equitable_v15_v2 \
  --dl $R/dl_imbrique_v15_equitable:choisie_cal --xgb $R/eval_arbres_v15_xgb:choisie_cal --rf $R/eval_arbres_v15_rf:choisie_cal \
  --extra "DL c35 fige (modele de l'application)=$R/dl_imbrique_v15:c35_cal" 2>&1 | tee $R/log_comparaison_v15_v2.txt
echo "===================== TERMINE : $(date) ====================="
