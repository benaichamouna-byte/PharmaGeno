#!/usr/bin/env python3
"""
verifier_installation.py : contrôle de l'installation en ~1 minute, sans navigateur et sans VCF.
Usage : python3 verifier_installation.py
Vérifie : (1) les sommes de contrôle des fichiers, (2) le chargement des 3 modèles et du domaine (189 médicaments),
(3) le parcours complet « profil de démonstration » dans toutes les spécialités (page, PDF, JSON, vue patient).
Ne mesure PAS la performance des modèles (voir le mémoire).
"""
import hashlib, io, json, os, sys, tempfile, types
RACINE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(RACINE, 'scripts'))
ok = True
def verdict(nom, cond, detail=''):
    global ok; ok &= bool(cond); print(('OK    ' if cond else 'ECHEC ') + nom + (' | ' + detail if detail else ''), flush=True)
# 1. sommes de contrôle
man = os.path.join(RACINE, 'MANIFESTE.sha256'); mauvais = []; n = 0
for l in open(man, encoding='utf-8'):
    h, f = l.strip().split('  ', 1); n += 1
    if hashlib.sha256(open(os.path.join(RACINE, f), 'rb').read()).hexdigest() != h: mauvais.append(f)
verdict('Sommes de contrôle', not mauvais, '%d fichiers ; différents : %s' % (n, mauvais))
# 2. chargement
import app_pharmageno_v8r as A
cfg = types.SimpleNamespace(donnees=os.path.join(RACINE, 'data'), modeles=os.path.join(RACINE, 'modeles_v10'), modeles_choix=os.path.join(RACINE, 'modeles_v10'), modeles_xgb=os.path.join(RACINE, 'modeles_v10x'), modeles_rf=os.path.join(RACINE, 'modeles_v10rf'),
                            codage=None, tables=None, bundle='', travail=tempfile.mkdtemp(prefix='pharmageno_'), pgx_python=sys.executable, port=5000, taille_max_mo=5)
app = A.creer_app(cfg); mo, rc = app.mo, app.rc
verdict('Modèles et domaine chargés', len(mo.dom) == 189 and mo.rf is not None, '%d médicaments, %d classes de choix, %d variables' % (len(mo.dom), len(mo.classes_choix), len(mo.genes_modele)))
# 3. parcours démonstration
c = app.test_client(); specs = [s for s in rc.specialites() if rc.medicaments_de_specialite(s)]; mal = []
for sp in specs:
    r = c.post('/demo', data={'specialite': sp}); loc = r.headers['Location']; jid = loc.rsplit('/', 1)[1].split('?')[0]
    t = c.get(loc).get_data(as_text=True); p = c.get('/pdf/' + jid); j = c.get('/json/' + jid); pat = c.get('/patient/' + jid)
    if not (t and 'Traceback' not in t and '{{' not in t and p.data[:5] == b'%PDF-' and j.status_code == 200 and pat.status_code == 200): mal.append(sp)
verdict('Parcours des résultats (profil interne de contrôle) : page, PDF, JSON et vue patient pour chaque spécialité', not mal, '%d spécialités ; en échec : %s' % (len(specs), mal))
import importlib.util, shutil
_m = []
if importlib.util.find_spec('pysam') is None: _m.append('pysam')
if not os.path.exists(os.path.expanduser('~/pgxenv/bin/python')): _m.append('PyPGx (~/pgxenv)')
if not os.path.isdir(os.path.expanduser('~/pypgx-bundle')): _m.append('pypgx-bundle')
if shutil.which('java') is None: _m.append('Java')
print(('INFO  Lecture des VCF : installée' if not _m else 'INFO  Lecture des VCF : pas encore installée (manque : %s) -> lancer : bash installer_vcf.sh' % ', '.join(_m)))
print('\nRÉSULTAT : ' + ('INSTALLATION CORRECTE' if ok else 'PROBLÈME (voir lignes ECHEC)')); sys.exit(0 if ok else 1)
