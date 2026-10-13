#!/bin/bash
DEST="/mnt/c/Users/MSI/Desktop/memoire/a_envoyer"
mkdir -p "$DEST"
for N in phenotype_drug_dataset_FINAL.csv drug_fingerprints_v2.pkl drug_smiles.csv vcf_parser.py; do
  if [ "$N" = "vcf_parser.py" ]; then
    P="$HOME/projet_memoire/scripts/vcf_parser.py"
    [ -f "$P" ] || P=""
  else
    P=$(find "$HOME/projet_memoire" -name "$N" -not -path "*/.git/*" 2>/dev/null | head -n 1)
  fi
  if [ -z "$P" ]; then
    echo "ABSENT : $N"
  elif [ -e "$DEST/$N" ]; then
    echo "DEJA PRESENT, non ecrase : $N"
  else
    cp "$P" "$DEST/$N" && echo "COPIE : $N  <-  $P"
  fi
done
echo "--- Contenu du dossier a envoyer"
ls -l "$DEST"
