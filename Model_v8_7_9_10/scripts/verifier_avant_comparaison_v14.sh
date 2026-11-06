#!/usr/bin/env bash
# Vérifie, AVANT lancement, que les fichiers de ton WSL sont identiques à ceux du protocole (empreintes SHA-256) et que les bibliothèques sont là.
# Usage : depuis le dossier scripts/ du projet :   bash verifier_avant_comparaison_v14.sh
cd "$(dirname "$0")"
cat > /tmp/empreintes_comparaison_v14.txt <<'EOS'
b876bb469e562d6e7f088190cc694f172ccabed50b1c2496d19e8928e50b238a  ../data/corpus_v14/phenotype_drug_dataset_v14.csv
5e554af79837f3f786fdf0452d61165d3b08aa3461164d67dc5ed68dc38b6155  ../data/profils_ensemble_final_v1.txt
99389477c3ab63fee3ea27783e4c24651d64233856644c10b36bd081ea469a6f  arbres_coeur_v1.py
c67b5cbe94783c6f74c051e32e99aa4ffd5c99125a78d1a3671827a2ca9a9dd7  recherche_hp_arbres_v1.py
26e1fe5bce46fc65fe080abe8da9174db38954ba1a27f74511133527593caf1e  evaluer_arbres_imbrique_v1.py
c92a8d41e82bd56c3de181e1cec0233781e8b7906279c4afdc87d20014cd28dd  comparaison_equitable_v14_v1.py
6ea5d070a7d19e7a970bb7905da79a62cb4ab4b88eac1f0d4cf2a1d5cb7b3c50  lancer_comparaison_equitable_v14.sh
63658d2674625a82788d05c178c362c1a265137970b3096fc98f00c4cb198d41  dl_coeur_v4.py
e95f09033fd83b8c810dbac51a92e7fe116adcd158d578f42cd5918fe5836039  protocole_commun_v10.py
5b387919434c040982075f2af2f3c4e42e37478f9d452b6c01c1134a988da1cd  evaluer_dl_imbrique_v5.py
73176f3d5101e23043b2dcb5a64f7364cb0289203871b5f20d71c33c11b7fda4  recherche_hp_dl_v4.py
EOS
echo "== 1/3 empreintes SHA-256 (11 lignes, toutes doivent afficher OK)"; sha256sum -c /tmp/empreintes_comparaison_v14.txt || { echo "ECHEC : un fichier differe. NE PAS LANCER. Me donner le fichier signale."; exit 1; }
echo "== 2/3 bibliotheques"; python3 -c "import numpy, pandas, scipy, sklearn, xgboost, torch; print('numpy', numpy.__version__, '| pandas', pandas.__version__, '| scipy', scipy.__version__, '| scikit-learn', sklearn.__version__, '| xgboost', xgboost.__version__, '| torch', torch.__version__)" || { echo "ECHEC : une bibliotheque manque (pip install --break-system-packages xgboost ... selon le message)."; exit 1; }
echo "== 3/3 machine"; echo "coeurs : $(nproc) | memoire libre (Go) : $(free -g | awk '/Mem:/{print $7}') | disque libre (Go) : $(df -BG --output=avail . | tail -1 | tr -dc 0-9)"
echo "TOUT EST BON : tu peux lancer  bash lancer_comparaison_equitable_v14.sh \$(nproc)"
