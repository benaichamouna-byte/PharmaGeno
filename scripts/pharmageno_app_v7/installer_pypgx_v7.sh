#!/bin/bash
# installer_pypgx_v7.sh : installe PyPGx 0.27.0 dans un environnement dédié (~/pgxenv), séparé de ton environnement principal.
# Pourquoi : PyPGx 0.27.0 exige pandas < 3. Dans un environnement avec pandas 3, il échoue avec « setting an array element with a sequence ».
# Ce script ne modifie PAS ton environnement principal (conda base). Il peut être relancé sans risque.
set -e
ENV="${PGX_ENV:-$HOME/pgxenv}"
BUNDLE="${PYPGX_BUNDLE_DIR:-$HOME/pypgx-bundle}"
echo "1/4  Environnement dédié : $ENV"
[ -x "$ENV/bin/python" ] || python3 -m venv "$ENV"
echo "2/4  Installation de pypgx 0.27.0, pandas<3, pysam"
"$ENV/bin/pip" install -q --upgrade pip
"$ENV/bin/pip" install -q "pypgx==0.27.0" "pandas<3" pysam
echo "3/4  Panel de référence 1000 Genomes (pypgx-bundle 0.27.0, environ 500 Mo)"
if [ -d "$BUNDLE/1kgp" ]; then echo "     déjà présent : $BUNDLE"
else git clone --depth 1 --branch 0.27.0 https://github.com/sbslee/pypgx-bundle "$BUNDLE"; fi
echo "4/4  Vérifications"
"$ENV/bin/python" -c "import importlib.metadata as m, pypgx, pandas, numpy, pysam; print('     pypgx', m.version('pypgx'), '| pandas', pandas.__version__, '| numpy', numpy.__version__, '| pysam', pysam.__version__)"
if command -v java >/dev/null 2>&1; then echo "     Java : présent"; else echo "     ATTENTION : Java absent. Installe-le avec : sudo apt install default-jre"; exit 1; fi
[ -d "$BUNDLE/1kgp" ] && echo "     pypgx-bundle : présent" || { echo "     ATTENTION : pypgx-bundle incomplet"; exit 1; }
echo
echo "INSTALLATION OK. Relance l'application avec :"
echo "   python3 app_pharmageno_v7.py --pgx-python $ENV/bin/python --bundle $BUNDLE"
