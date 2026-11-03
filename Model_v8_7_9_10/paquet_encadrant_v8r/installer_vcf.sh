#!/bin/bash
# installer_vcf.sh : installe ce qu'il faut pour LIRE UN FICHIER VCF (facultatif : l'application de base n'en a pas besoin pour démarrer).
# À lancer depuis le dossier du paquet, avec l'environnement du paquet activé (source .venv/bin/activate). Peut être relancé sans risque.
# Installe : (1) pysam dans l'environnement du paquet, (2) PyPGx 0.27.0 avec pandas<3 dans un environnement séparé (~/pgxenv),
# (3) le panel de référence pypgx-bundle 0.27.0 (~/pypgx-bundle, plusieurs centaines de Mo, téléchargé depuis GitHub), (4) vérifie Java.
set -e
ENV="${PGX_ENV:-$HOME/pgxenv}"
BUNDLE="${PYPGX_BUNDLE_DIR:-$HOME/pypgx-bundle}"
cd "$(dirname "$0")"
echo "1/5  pysam dans l'environnement actif ($(python3 -c 'import sys;print(sys.prefix)'))"
python3 -m pip install -q "pysam==0.24.1"
echo "2/5  Environnement séparé pour PyPGx : $ENV (PyPGx 0.27.0 exige pandas < 3)"
[ -x "$ENV/bin/python" ] || python3 -m venv "$ENV"
"$ENV/bin/pip" install -q --upgrade pip
"$ENV/bin/pip" install -q "pypgx==0.27.0" "pandas<3" pysam
echo "3/5  Panel de référence 1000 Genomes (pypgx-bundle 0.27.0)"
if [ -d "$BUNDLE/1kgp" ]; then echo "     déjà présent : $BUNDLE"
else
  command -v git >/dev/null 2>&1 || { echo "     ATTENTION : git absent. Installez-le (ex. sudo apt install git) puis relancez ce script."; exit 1; }
  git clone --depth 1 --branch 0.27.0 https://github.com/sbslee/pypgx-bundle "$BUNDLE"
fi
echo "4/5  Java (utilisé par PyPGx)"
if command -v java >/dev/null 2>&1; then echo "     présent"; else echo "     ATTENTION : Java absent. Installez-le (ex. sudo apt install default-jre-headless) puis relancez ce script."; exit 1; fi
echo "5/5  Vérifications"
"$ENV/bin/python" -c "import importlib.metadata as m, pypgx, pandas, numpy, pysam; print('     PyPGx', m.version('pypgx'), '| pandas', pandas.__version__, '| numpy', numpy.__version__, '| pysam', pysam.__version__)"
python3 -c "import pysam; print('     pysam (environnement du paquet)', pysam.__version__)"
[ -d "$BUNDLE/1kgp" ] && [ -d "$BUNDLE/cnv" ] && echo "     pypgx-bundle complet" || { echo "     ATTENTION : pypgx-bundle incomplet ($BUNDLE)"; exit 1; }
echo
echo "INSTALLATION DE LA LECTURE DES VCF : OK. Relancez l'application : bash lancer.sh"
