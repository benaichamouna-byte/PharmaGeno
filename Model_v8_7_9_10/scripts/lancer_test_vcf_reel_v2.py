#!/usr/bin/env python3
"""
lancer_test_vcf_reel_v2.py : passe un VCF patient dans la chaîne COMPLÈTE de l'application v8l (lecteur PyPGx -> DL profil + DL choix -> écran), sans navigateur,
et écrit la fiche JSON + les pages HTML de résultats. Les VCF des 2 profils de test sont dans results/test_vcf_reel_v1/vcf/ (reconstruits depuis les VCF 1KGP du pypgx-bundle).
Usage (depuis scripts/) : python3 lancer_test_vcf_reel_v2.py NA19085 Cardiologie Psychiatrie --sortie ../results/test_vcf_reel_v1_chez_moi
Le premier nom de spécialité sert à l'analyse ; les autres servent à produire d'autres pages de résultats.
"""
import os, sys, types, json, time, re, argparse
ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import app_pharmageno_v8m as A
ap = argparse.ArgumentParser(); ap.add_argument('echantillon'); ap.add_argument('specialites', nargs='+')
ap.add_argument('--vcf-dir', default=os.path.join(ICI, '..', 'results', 'test_vcf_reel_v1', 'vcf')); ap.add_argument('--sortie', required=True)
ap.add_argument('--modeles', default=os.path.join(ICI, '..', 'modeles_v9')); ap.add_argument('--modeles-choix', default=os.path.join(ICI, '..', 'modeles_v9'))
ap.add_argument('--bundle', default=os.path.expanduser('~/pypgx-bundle')); ap.add_argument('--pgx-python', default=os.path.expanduser('~/pgxenv/bin/python'))
a = ap.parse_args(); os.makedirs(a.sortie, exist_ok=True)
cfg = types.SimpleNamespace(donnees=os.path.join(ICI, '..', 'data'), modeles=a.modeles, modeles_choix=a.modeles_choix, modeles_xgb=os.path.join(ICI, '..', 'modeles_v9x'),
                            codage=None, tables=None, bundle=a.bundle, travail=os.path.join(a.sortie, 'travail'), pgx_python=a.pgx_python, port=5000, taille_max_mo=500)
app = A.creer_app(cfg); c = app.test_client(); ech = a.echantillon
with open(os.path.join(a.vcf_dir, ech + '.vcf'), 'rb') as f:
    r = c.post('/analyser', data={'specialite': a.specialites[0], 'vcf': (f, ech + '.vcf'), 'echantillon': ech}, content_type='multipart/form-data')
jid = r.headers['Location'].rstrip('/').split('/')[-1].split('?')[0]; t0 = time.time()
while True:
    e = c.get('/etat/' + jid).get_json(); print(round(time.time() - t0), e, flush=True)
    if e['etat'] in ('termine', 'erreur', 'echec'): break
    time.sleep(10)
json.dump(c.get('/json/' + jid).get_json(), open(os.path.join(a.sortie, 'sortie_%s.json' % ech), 'w'), indent=1, ensure_ascii=False)
for s2 in a.specialites:
    open(os.path.join(a.sortie, 'page_%s_%s.html' % (ech, re.sub(r'\W+', '_', s2))), 'w').write(c.get('/resultats/%s?specialite=%s' % (jid, s2)).get_data(as_text=True))
print('FIN', ech)
