#!/bin/bash
set -e
F="Plan_PharmaGeno_12oct2026.xlsx"
SRC="/mnt/c/Users/MSI/Downloads/$F"
WSL_DIR="$HOME/projet_memoire/memoire"
WIN_DIR="/mnt/c/Users/MSI/Desktop/memoire"

echo "1/4 Verification du fichier telecharge"
if [ ! -f "$SRC" ]; then
  echo "ERREUR : $SRC introuvable. Le fichier n'est pas dans Telechargements."
  exit 1
fi

echo "2/4 Copie vers WSL"
mkdir -p "$WSL_DIR"
if [ -e "$WSL_DIR/$F" ]; then
  echo "ERREUR : $WSL_DIR/$F existe deja. Rien n'est ecrase."
  exit 1
fi
cp "$SRC" "$WSL_DIR/$F"

echo "3/4 Copie vers Windows (Bureau)"
mkdir -p "$WIN_DIR"
if [ -e "$WIN_DIR/$F" ]; then
  echo "ERREUR : $WIN_DIR/$F existe deja. Rien n'est ecrase."
  exit 1
fi
cp "$WSL_DIR/$F" "$WIN_DIR/$F"

echo "4/4 GitHub"
cd "$HOME/projet_memoire"
git add "memoire/$F"
git commit -m "Ajout du plan definitif PharmaGeno (suivi des taches, 12 oct 2026)"
git push

echo "--- Verification : les 3 empreintes doivent etre identiques"
sha256sum "$SRC" "$WSL_DIR/$F" "$WIN_DIR/$F"
git log -1 --stat
echo "--- Reste : deposer le fichier sur le Drive a la main"
