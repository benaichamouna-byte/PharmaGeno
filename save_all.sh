#!/bin/bash
# save_all.sh - Sauvegarde Windows + GitHub en une commande
# Usage: bash save_all.sh "message decrivant le changement"

MESSAGE="${1:-Mise a jour}"
DEST="/mnt/c/Users/MSI/Desktop/memoire"

echo "=== Copie vers Windows ==="
cp -r ~/projet_memoire/scripts/*.py "$DEST/" 2>/dev/null
cp -r ~/projet_memoire/app/app.py "$DEST/" 2>/dev/null
cp -r ~/projet_memoire/app/templates/*.html "$DEST/" 2>/dev/null
cp -r ~/projet_memoire/results/*.png "$DEST/" 2>/dev/null
echo "Fichiers copies dans $DEST"

echo "=== Envoi vers GitHub ==="
cd ~/projet_memoire
git add scripts/ app/ README.md 2>/dev/null
git commit -m "$MESSAGE"
git push origin main

echo "=== TERMINE ==="
echo "N'oublie pas de mettre a jour le Drive manuellement si besoin."
