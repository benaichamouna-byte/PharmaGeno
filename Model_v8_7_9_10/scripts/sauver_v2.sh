#!/usr/bin/env bash
# sauver_v2.sh : sauvegarde WSL -> Windows -> GitHub. Le depot Drive reste manuel (niveau 4).
#
# NOUVEAUTES par rapport a la v1 :
#   1. accepte une ARCHIVE .zip : un seul telechargement par livraison
#        bash ~/sauver_v2.sh "message" lot.zip
#   2. SUPPRIME les sources des Telechargements apres copie verifiee
#        -> plus jamais de doublon "fichier (1).md" sauvegarde par erreur
#   3. route aussi les .png vers les deux dossiers de figures
#   4. verifie que la copie a la meme taille que la source avant de supprimer
#
# Usage :
#   bash ~/sauver_v2.sh "message de commit" lot.zip
#   bash ~/sauver_v2.sh "message de commit" fichier1.md fichier2.py   (mode v1, toujours valable)
#
# Destinations par extension :
#   .md             -> model_v2/docs/
#   .py .sh         -> Model_v8_7_9_10/scripts/
#   .csv .json .txt -> Model_v8_7_9_10/data/
#   .png            -> Model_v8_7_9_10/fig/  (+ copie dans fabrication/fig/)
set -uo pipefail
DEPOT=/home/mouna/projet_memoire
DL=/mnt/c/Users/MSI/Downloads
WIN=/mnt/c/Users/MSI/Desktop/memoire
FABFIG=/home/mouna/projet_memoire/fabrication/fig
BRANCHE=sauvegarde-2026-11-02

[ $# -ge 2 ] || { echo "Usage : bash ~/sauver_v2.sh \"message de commit\" lot.zip"; exit 1; }
MSG="$1"; shift
cd "$DEPOT" || { echo "ECHEC : depot introuvable ($DEPOT)"; exit 1; }

# ---- si l'argument est une archive, on la deballe et on travaille sur son contenu
TMP=""; SRCDIR="$DL"; NOMS=("$@"); ARCHIVE=""
if [ $# -eq 1 ] && [[ "$1" == *.zip ]]; then
  command -v unzip >/dev/null || { echo "ECHEC : unzip absent. Installe-le : sudo apt install -y unzip"; exit 1; }
  ARCHIVE=$(ls -t "$DL/${1%.zip}"*.zip 2>/dev/null | head -1)
  [ -n "$ARCHIVE" ] || { echo "ECHEC : $1 absent de $DL"; exit 1; }
  TMP=$(mktemp -d); unzip -q -o -j "$ARCHIVE" -d "$TMP" || { echo "ECHEC : archive illisible"; rm -rf "$TMP"; exit 1; }
  SRCDIR="$TMP"; mapfile -t NOMS < <(cd "$TMP" && ls)
  echo "Archive : $(basename "$ARCHIVE")  ->  ${#NOMS[@]} fichier(s)"
fi

AJOUTES=(); SOURCES=()
for NOM in "${NOMS[@]}"; do
  BASE="${NOM%.*}"; EXT="${NOM##*.}"
  case "$EXT" in
    md)            SOUS="model_v2/docs" ;;
    py|sh)         SOUS="Model_v8_7_9_10/scripts" ;;
    csv|json|txt)  SOUS="Model_v8_7_9_10/data" ;;
    png)           SOUS="Model_v8_7_9_10/fig" ;;
    *)             echo "  ?  $NOM : extension .$EXT inconnue, ignore"; continue ;;
  esac
  if [ -n "$TMP" ]; then SRC="$SRCDIR/$NOM"
  else SRC=$(ls -t "$SRCDIR/$BASE"*."$EXT" 2>/dev/null | head -1); fi
  [ -n "${SRC:-}" ] && [ -f "$SRC" ] || { echo "  !  $NOM : absent de $SRCDIR"; continue; }

  mkdir -p "$SOUS" "$WIN"
  cp "$SRC" "$SOUS/$NOM"                                   # niveau 1 : WSL
  if [ "$(wc -c < "$SRC")" -ne "$(wc -c < "$SOUS/$NOM")" ]; then
    echo "  ECHEC $NOM : la copie n'a pas la meme taille que la source, rien n'est supprime"; continue; fi
  cp "$SOUS/$NOM" "$WIN/"                                  # niveau 2 : Windows
  [ "$EXT" = png ] && { mkdir -p "$FABFIG"; cp "$SOUS/$NOM" "$FABFIG/"; }
  echo "  OK $NOM  ->  $SOUS/  ($(wc -c < "$SOUS/$NOM") octets)"
  AJOUTES+=("$SOUS/$NOM"); SOURCES+=("$NOM")
done

if [ ${#AJOUTES[@]} -eq 0 ]; then echo; echo "Rien a sauvegarder. Verifie les noms de fichiers."; [ -n "$TMP" ] && rm -rf "$TMP"; exit 1; fi

echo; echo "== niveau 3 : GitHub =="
git add "${AJOUTES[@]}"
if git diff --cached --quiet; then
  echo "Aucun changement : ces fichiers sont deja identiques dans le depot."
else
  git commit -q -m "$MSG" && git push -q origin "$BRANCHE" && echo "Pousse sur $BRANCHE : $(git log --oneline -1)"
fi

# ---- niveau 1 bis : nettoyage des Telechargements (apres copie verifiee seulement)
echo; echo "== nettoyage des Telechargements =="
if [ -n "$ARCHIVE" ]; then
  rm -f "$ARCHIVE"; echo "  archive supprimee : $(basename "$ARCHIVE")"
  # les homonymes periment dans les Telechargements : on les retire aussi
  for NOM in "${SOURCES[@]}"; do
    BASE="${NOM%.*}"; EXT="${NOM##*.}"
    N=0; while IFS= read -r f; do rm -f "$f"; N=$((N+1)); done < <(ls "$DL/$BASE"*."$EXT" 2>/dev/null)
    [ "$N" -gt 0 ] && echo "  $NOM : $N homonyme(s) perime(s) supprime(s)"
  done
else
  for NOM in "${SOURCES[@]}"; do
    BASE="${NOM%.*}"; EXT="${NOM##*.}"
    N=0; while IFS= read -r f; do rm -f "$f"; N=$((N+1)); done < <(ls "$DL/$BASE"*."$EXT" 2>/dev/null)
    [ "$N" -gt 0 ] && echo "  $NOM : $N fichier(s) supprime(s) des Telechargements"
  done
fi
echo "  (plus aucun doublon \"nom (1).ext\" ne peut etre repris par erreur)"
[ -n "$TMP" ] && rm -rf "$TMP"

echo
echo "== niveau 4 : Drive, a faire a la main =="
echo "Glisse ces fichiers depuis  C:\\Users\\MSI\\Desktop\\memoire\\  vers le dossier Docs de ton Drive :"
for f in "${AJOUTES[@]}"; do echo "   - $(basename "$f")"; done
