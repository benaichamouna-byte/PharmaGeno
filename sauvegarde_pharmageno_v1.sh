#!/usr/bin/env bash
# sauvegarde_pharmageno_v1.sh — WSL -> Windows -> GitHub (commit) + dossier de depot Drive
# Ne supprime RIEN, n'ecrase RIEN de plus ancien (rsync --update), n'envoie aucune donnee IWPC.
set -u

SRC="${SRC:-$HOME/projet_memoire/Model_v8_7_9_10}"
WIN="${WIN:-/mnt/c/Users/MSI/Desktop/memoire}"
DEPOT="${DEPOT:-$WIN/A_deposer_sur_Drive}"
SINCE="${SINCE:-2026-10-23}"           # le Drive 'scripts' s'arrete au 23 oct
MAXMB="${MAXMB:-20}"                   # fichiers plus gros : Windows seulement
GIT_REPO="${GIT_REPO:-$HOME/projet_memoire}"   # dossier qui contient .git
PUSH="${PUSH:-oui}"

[ -d "$SRC" ] || { echo "ERREUR : $SRC introuvable"; exit 1; }
[ -d "$WIN" ] || { echo "ERREUR : $WIN introuvable (Windows non monte ?)"; exit 1; }

echo "=== ETAPE 1/4 : WSL -> Windows ($WIN/Model_v8_7_9_10)"
mkdir -p "$WIN/Model_v8_7_9_10"
( cd "$SRC" && find . -type f ! -path '*/__pycache__/*' ! -name '*.pyc' -print0 \
  | xargs -0 -r cp -p -u --parents -t "$WIN/Model_v8_7_9_10/" )
echo "  copie terminee (fichiers plus recents seulement ; rien n'est supprime ni remplace par plus ancien)"

echo "=== ETAPE 2/4 : controle des fichiers copies (sha256 sur les fichiers legers)"
cd "$SRC" || exit 1
n_ok=0; n_ko=0
while IFS= read -r -d '' f; do
  a=$(sha256sum "$f" | cut -d' ' -f1); b=$(sha256sum "$WIN/Model_v8_7_9_10/$f" 2>/dev/null | cut -d' ' -f1)
  if [ "$a" = "$b" ]; then n_ok=$((n_ok+1)); else n_ko=$((n_ko+1)); echo "  DIFFERENT : $f"; fi
done < <(find scripts docs "journal de bord" -type f ! -name '*.pyc' -print0 2>/dev/null)
echo "  scripts/docs/journal : $n_ok identiques, $n_ko differents"

echo "=== ETAPE 3/4 : preparation du depot Drive ($DEPOT) — fichiers modifies depuis $SINCE"
mkdir -p "$DEPOT"
LISTE="$DEPOT/_LISTE_DES_FICHIERS_A_DEPOSER.txt"
: > "$LISTE"
liste_exclus="$DEPOT/_EXCLUS_et_pourquoi.txt"; : > "$liste_exclus"
cd "$SRC" || exit 1
cnt=0
while IFS= read -r -d '' f; do
  f="${f#./}"
  case "$f" in
    *__pycache__*|*.pyc) continue ;;
    *PS216536*|*[Ii][Ww][Pp][Cc]*.xls*|*ITPC*) echo "IWPC (jamais sur GitHub/Drive) : $f" >> "$liste_exclus"; continue ;;
    *DOUBLON*|*ECARTE*|*NE_PAS_UTILISER*|*_REMPLACE_*) echo "doublon/ecarte (reste sur Windows) : $f" >> "$liste_exclus"; continue ;;
    data/sources_nov2026/*) echo "source brute externe (retelechargeable, reste sur Windows) : $f" >> "$liste_exclus"; continue ;;
  esac
  sz=$(stat -c %s "$f")
  if [ "$sz" -gt $((MAXMB*1024*1024)) ]; then echo "plus de ${MAXMB} Mo (reste sur Windows) : $f" >> "$liste_exclus"; continue; fi
  case "$f" in
    scripts/*|data/*|docs/*|results/*|modeles_*) dest="$f" ;;
    "journal de bord"/*) dest="$f" ;;
    *) dest="autres/$f" ;;
  esac
  mkdir -p "$DEPOT/$(dirname "$dest")"
  cp -p -n "$f" "$DEPOT/$dest" 2>/dev/null
  echo "$dest" >> "$LISTE"; cnt=$((cnt+1))
done < <(find . -type f -newermt "$SINCE" -print0)
echo "  $cnt fichier(s) prepares dans $DEPOT"
echo "  (liste : $LISTE ; exclus : $liste_exclus)"

echo "=== ETAPE 4/4 : GitHub"
if [ -d "$GIT_REPO/.git" ]; then
  cd "$GIT_REPO" || exit 1
  git status --short | head -20
  # ajout fichier par fichier : legers, hors IWPC/doublons/modeles/sources brutes
  git ls-files --others --modified --exclude-standard -z | while IFS= read -r -d '' g; do
    case "$g" in
      *PS216536*|*[Ii][Ww][Pp][Cc]*.xls*|*ITPC*|*DOUBLON*|*ECARTE*|*NE_PAS_UTILISER*|*_REMPLACE_*|*sources_nov2026/*|*modeles_*rf*|*__pycache__*|*.pyc|*.joblib) continue ;;
    esac
    [ -f "$g" ] || continue
    [ "$(stat -c %s "$g")" -gt $((MAXMB*1024*1024)) ] && continue
    git add -- "$g"
  done
  if git diff --cached --quiet; then
    echo "  rien de nouveau a envoyer sur GitHub"
  else
    git diff --cached --stat | tail -5
    git commit -q -m "Sauvegarde $(date +%Y-%m-%d) : scripts, docs, resultats legers (sans IWPC)

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015Z7vtiAard9dWpxpAidMQV" && echo "  commit cree"
    if [ "$PUSH" = "oui" ]; then git push -u origin HEAD && echo "  push OK" || echo "  push ECHOUE : copie-moi le message ci-dessus"; fi
  fi
else
  echo "  Pas de depot git dans $GIT_REPO : dis-moi ou se trouve ton dossier GitHub (git rev-parse --show-toplevel)"
fi
echo "=== FIN. Reste a faire par toi : deposer le contenu de $DEPOT sur le Drive (voir procedure)."
