#!/bin/bash
# sauvegarde.sh - copie des fichiers vers WSL puis Windows puis GitHub (jamais d'ecrasement)
# Usage : bash sauvegarde.sh fichier1 [fichier2 ...]
# Un nom simple est cherche dans Telechargements ; un chemin complet est utilise tel quel.
DL="${DL:-/mnt/c/Users/MSI/Downloads}"
WSL="${WSL:-$HOME/projet_memoire/memoire}"
WIN="${WIN:-/mnt/c/Users/MSI/Desktop/memoire}"
if [ $# -lt 1 ]; then echo "Usage : bash sauvegarde.sh fichier1 [fichier2 ...]"; exit 1; fi
mkdir -p "$WSL" "$WIN" || exit 1
REL=()
for f in "$@"; do
  if [ -f "$f" ]; then src="$f"; elif [ -f "$DL/$f" ]; then src="$DL/$f"; else echo "ERREUR : introuvable : $f"; exit 1; fi
  b=$(basename "$src")
  case "$b" in *.sh|*.py) sub="scripts";; *) sub="";; esac
  rel="${sub:+$sub/}$b"
  for d in "$WSL" "$WIN"; do
    mkdir -p "$d/$sub"
    if [ -e "$d/$rel" ]; then
      if cmp -s "$src" "$d/$rel"; then echo "DEJA PRESENT (identique) : $d/$rel"
      else echo "REFUS : $d/$rel existe deja et differe. Renomme ton fichier en _v2 puis relance."; exit 1; fi
    else
      cp "$src" "$d/$rel" || exit 1; echo "COPIE : $d/$rel"
    fi
  done
  h1=$(sha256sum "$WSL/$rel" | cut -d' ' -f1); h2=$(sha256sum "$WIN/$rel" | cut -d' ' -f1)
  if [ "$h1" = "$h2" ]; then echo "SHA256 identique WSL/Windows : ${h1:0:12}... ($rel)"; else echo "ERREUR : hash different pour $rel"; exit 1; fi
  REL+=("$rel")
done
if git -C "$WSL" rev-parse --show-toplevel >/dev/null 2>&1; then
  TOP=$(git -C "$WSL" rev-parse --show-toplevel)
  ADD=(); for r in "${REL[@]}"; do ADD+=("$(realpath --relative-to="$TOP" "$WSL/$r")"); done
  git -C "$TOP" add -- "${ADD[@]}"
  if git -C "$TOP" diff --cached --quiet; then echo "GitHub : rien de nouveau a envoyer."
  else
    git -C "$TOP" commit -q -m "Sauvegarde $(date +%Y-%m-%d_%H%M) : ${REL[*]}" && git -C "$TOP" push origin main && echo "GitHub : push OK ($(git -C "$TOP" rev-parse --short HEAD))"
  fi
else
  echo "ATTENTION : $WSL n'est pas dans un depot git. Etape GitHub non faite."
fi
echo "---"; echo "RESTE A FAIRE A LA MAIN : glisser dans Google Drive :"
for r in "${REL[@]}"; do echo "   $WIN/$r"; done
