#!/usr/bin/env python3
"""rejouer_moteur_104_v1.py : repasse les profils genetiques des 104 personnes (lus dans les VCF par la v8s, sorties archivees)
dans une version de l'application, SANS relancer PyPGx.
Justification : la lecture du VCF (vcf_to_profile_v9, PyPGx 0.27.0) est identique entre v8s et v8t ; seuls les regles, le domaine et les
modeles changent. Le profil et le detail de lecture de chaque personne sont donc repris tels quels de la sortie archivee, injectes comme
une analyse terminee, puis la fiche /json de l'application est demandee, comme le faisait lancer_lot_v1.py.
Usage : python3 rejouer_moteur_104_v1.py --app app_pharmageno_v8t --modeles ../modeles_v15 --modeles-xgb ../modeles_v15 --modeles-rf ../modeles_v15 \
        --entree DOSSIER_SORTIES_V8S --sortie DOSSIER --scripts DOSSIER_SCRIPTS_APPLICATION [--specialite Cardiologie]"""
import argparse, importlib, json, os, sys, tempfile, time, types, uuid, glob
ap = argparse.ArgumentParser()
for k in ('app', 'modeles', 'modeles_xgb', 'modeles_rf', 'entree', 'sortie', 'scripts'): ap.add_argument('--' + k.replace('_', '-'), dest=k, required=True)
ap.add_argument('--specialite', default='Cardiologie'); a = ap.parse_args()
sys.path.insert(0, a.scripts); os.chdir(a.scripts); A = importlib.import_module(a.app)
trav = tempfile.mkdtemp(prefix='rejeu_'); os.makedirs(os.path.join(trav, 'jobs'))
cfg = types.SimpleNamespace(donnees=os.path.join(a.scripts, '..', 'data'), modeles=a.modeles, modeles_choix=a.modeles, modeles_xgb=a.modeles_xgb, modeles_rf=a.modeles_rf,
                            codage=None, tables=None, bundle='~/pypgx-bundle', travail=trav, pgx_python=sys.executable, port=5000, taille_max_mo=500)
app = A.creer_app(cfg); c = app.test_client(); os.makedirs(a.sortie, exist_ok=True); n = 0
for f in sorted(glob.glob(os.path.join(a.entree, 'sortie_*.json'))):
    ech = os.path.basename(f)[len('sortie_'):-len('.json')]; s = json.load(open(f, encoding='utf-8'))
    jid = uuid.uuid4().hex[:12]
    job = dict(id=jid, mode='vcf', specialite=a.specialite, nom_fichier=ech + '.vcf', etat='termine', pct=100, message='Analyse terminée', cree=time.time(),
               profil=s['profil'], detail=s['lecture_vcf'], assemblage=s.get('assemblage'))
    json.dump(job, open(os.path.join(trav, 'jobs', jid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    r = c.get('/json/' + jid); assert r.status_code == 200, (ech, r.status_code)
    json.dump(r.get_json(), open(os.path.join(a.sortie, 'sortie_%s.json' % ech), 'w', encoding='utf-8'), indent=1, ensure_ascii=False); n += 1
print('personnes rejouees :', n, '| application :', a.app, '| modeles :', a.modeles)
