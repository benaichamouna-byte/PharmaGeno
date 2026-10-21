#!/usr/bin/env python3
"""
test_app_v8c.py : tests de l'application web v8 (client de test Flask ; aucun entraînement ; ensemble final non lu).
À lancer depuis le dossier scripts/ :  python3 test_app_v8c.py
Ce qui est testé : la LOGIQUE et la mise en forme (pages, PDF, JSON, refus d'entrées invalides, suppression, en-têtes, échappement HTML, circuit VCF avec lecteur simulé).
Ce qui n'est PAS testé ici : la lecture réelle d'un VCF par PyPGx (voir valider_vcf_v8.py et test_app_v8c_vcf_reel.py) ni la performance du modèle.
"""
import io, json, os, re, shutil, sys, tempfile, time, types
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI); os.chdir(ICI)
import app_pharmageno_v8c as A

OK = True
def verdict(nom, cond, detail=''):
    global OK; OK &= bool(cond); print(('PASS ' if cond else 'FAIL ') + nom + (' | ' + detail if detail else ''), flush=True)

TRAV = tempfile.mkdtemp(prefix='tw_v8_')
cfg = types.SimpleNamespace(donnees=os.path.join(ICI, '..', 'data'), modeles=os.path.join(ICI, '..', 'results', 'resultats_final_v8'), codage=None, tables=None,
                            bundle='~/pypgx-bundle', travail=TRAV, pgx_python=sys.executable, taille_max_mo=5)
app = A.creer_app(cfg); c = app.test_client(); mo, rc = app.mo, app.rc
specs = [s for s in rc.specialites() if len(rc.medicaments_de_specialite(s)) > 0]

r = c.get('/'); t = r.get_data(as_text=True)
verdict('T1 accueil simplifié : VCF + spécialité + bouton ; ni HLA, ni CYP2D6, ni bloc démonstration', r.status_code == 200 and 'name="vcf"' in t and 'name="specialite"' in t and 'Lancer l' in t
        and 'name="hla_' not in t and 'cyp2d6' not in t and 'Profil de démonstration' not in t and specs[0] in t, '%d spécialités' % len(specs))

# --- démonstration, toutes les spécialités
def jid_de(loc): return loc.rsplit('/', 1)[1]
mauvais = []; n_pages = 0; trop_de_cartes = 0; sans_expl = 0; evit_manquants = 0; pdf_ko = 0; json_ko = 0; patient_ko = 0
for sp in specs:
    r = c.post('/demo', data={'specialite': sp}); loc = r.headers['Location']; jid = jid_de(loc)
    r = c.get(loc); t = r.get_data(as_text=True); n_pages += 1
    if r.status_code != 200 or 'Traceback' in t or '{{' in t or '{%' in t or '>None<' in t or 'undefined' in t: mauvais.append(sp)
    # tout médicament avec un avis EVITER (n'importe quelle spécialité) doit figurer dans la carte d'alertes de sécurité
    j = json.load(open(os.path.join(TRAV, 'jobs', jid + '.json'), encoding='utf-8')); res = mo.predire(j['profil']); par = {x['medicament']: x for x in res}
    attendus = [m for m, x in par.items() if 'EVITER' in {x.get('action_dl'), x.get('action_xgboost'), x.get('action_cpic')}]
    carte = t.split('À éviter pour ce patient (toutes spécialités)')[1].split('<form method="get"')[0] if attendus else ''
    evit_manquants += sum(1 for m in attendus if ('<b style="font-size:1.1rem">' + m + '</b>') not in carte)
    nb_prop = len(rc.recommander(res, sp, max_proposes=3)['proposes']); trop_de_cartes += (t.count('Prédiction du modèle (DL)') > 3)
    sans_expl += (nb_prop > 0 and t.count('En langage simple') < nb_prop)
    r = c.get('/pdf/' + jid); pdf_ko += not (r.status_code == 200 and r.mimetype == 'application/pdf' and r.data[:5] == b'%PDF-' and len(r.data) > 4000)
    r = c.get('/json/' + jid);
    try: d = json.loads(r.get_data(as_text=True)); json_ko += not (d['profil'] == j['profil'] and len(d['moteur']) == len(res))
    except Exception: json_ko += 1
    r = c.get('/patient/' + jid); tp = r.get_data(as_text=True); patient_ko += not (r.status_code == 200 and 'Traceback' not in tp and 'à lire d\'abord' in tp.lower())
verdict('T2 démonstration : toutes les spécialités rendent une page sans erreur ni gabarit non résolu', not mauvais, '%d pages ; mauvais : %s' % (n_pages, mauvais))
verdict('T3 tout médicament avec au moins un avis EVITER figure dans les alertes de sécurité (toutes spécialités)', evit_manquants == 0, '%d spécialités' % len(specs))
verdict('T3b au plus 3 médicaments proposés par spécialité, chacun avec prédiction et explication', trop_de_cartes == 0 and sans_expl == 0)
verdict('T4 PDF valide pour chaque spécialité', pdf_ko == 0)
verdict('T5 JSON cohérent avec le profil et le moteur', json_ko == 0)
verdict('T6 vue patient pour chaque spécialité', patient_ko == 0)

# --- contenu du PDF : trois avis, limites, « non évalué ne veut pas dire sans risque »
try:
    from pypdf import PdfReader
    r = c.get('/pdf/' + jid); txt = '\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(r.data)).pages)
    verdict('T7 PDF : sections attendues et formulation de sécurité', all(k in txt for k in ('Modèle (DL)', 'XGBoost', 'CPIC/DPWG', 'non évalué', 'Méthode et limites', 'non validé cliniquement')))
except ImportError:
    print('INFO pypdf absent : contenu du PDF non vérifié (T7 sautée)')

# --- recherche, échappement HTML
loc = '/resultats/' + jid
t = c.get(loc + '?q=warfarin').get_data(as_text=True); verdict('T8a recherche d\'un nom international', 'Médicament recherché : warfarin' in t)
t = c.get(loc + '?q=doliprane').get_data(as_text=True); verdict('T8b nom commercial : message clair, pas d\'erreur', 'non trouvé' in t.lower() or 'Médicament non trouvé' in t)
xss = '<script>alert(1)</script>'
t = c.get(loc, query_string={'q': xss}).get_data(as_text=True); verdict('T9 échappement HTML de la recherche', xss not in t and '&lt;script&gt;' in t)
t = c.get(loc + '?specialite=Inexistante').get_data(as_text=True); verdict('T10 spécialité inconnue en paramètre : repli sans erreur', 'Résultat - ' in t)

# --- en-têtes
r = c.get(loc); verdict('T11 en-têtes (no-store, nosniff, CSP)', r.headers.get('Cache-Control') == 'no-store' and r.headers.get('X-Content-Type-Options') == 'nosniff' and 'default-src' in r.headers.get('Content-Security-Policy', ''))

# --- entrées invalides
ok = []
ok.append(c.post('/demo', data={'specialite': 'Specialite inconnue'}).headers['Location'].startswith('/?erreur='))
ok.append(c.post('/analyser', data={'specialite': specs[0]}).headers['Location'].startswith('/?erreur='))
ok.append('erreur' in c.post('/analyser', data={'specialite': specs[0], 'vcf': (io.BytesIO(b'x'), 'x.txt')}, content_type='multipart/form-data').headers['Location'])
ok.append('erreur' in c.post('/analyser', data={'specialite': specs[0], 'cyp2d6': '9', 'vcf': (io.BytesIO(b'x'), 'x.vcf')}, content_type='multipart/form-data').headers['Location'])
ok.append('erreur' in c.post('/analyser', data={'specialite': specs[0], 'hla_HLA-B*57:01': 'probable', 'vcf': (io.BytesIO(b'x'), 'x.vcf')}, content_type='multipart/form-data').headers['Location'])
ok.append(c.get('/resultats/zzzzzzzzzzzz').status_code == 404 and c.get('/resultats/..%2f..%2fetc').status_code == 404 and c.get('/pdf/000000000000').status_code == 404)
verdict('T12 entrées invalides refusées (spécialité, fichier absent, extension, CYP2D6, HLA, identifiant)', all(ok), str(ok))
big = c.post('/analyser', data={'specialite': specs[0], 'vcf': (io.BytesIO(b'0' * (6 * 1024 * 1024)), 'x.vcf')}, content_type='multipart/form-data')
verdict('T13 fichier trop gros refusé (413)', big.status_code == 413)

# --- circuit VCF avec lecteur simulé (le vrai lecteur est validé à part)
import vcf_to_profile_v8 as L
vus = {}
def faux_lecteur(chemin, bundle, workdir, codage, tables, hla, assemblage, echantillon, **kw):
    vus.update(hla=hla, echantillon=echantillon, existe=os.path.exists(chemin), codage=os.path.basename(codage), tables=os.path.basename(tables))
    kw['progres'](50, 'milieu')
    p = {g: 1.0 for g in mo.genes_modele}; p['CYP2D6'] = None
    p['HLA-B*57:01'] = {'porteur': 1.0, 'non_porteur': 0.0}.get(dict(x.split('=') for x in hla.split(',') if x).get('HLA-B*57:01'))
    d = {g: dict(valeur=p[g], statut='appele' if p[g] is not None else 'non_determine', phenotype_utilise='Normal Metabolizer', genotype='*1/*1', motif=None) for g in p}
    return dict(profil=p, detail=d, assemblage='GRCh38', controle_assemblage=None, genotypes_haploides_chrX_convertis=0)
L_orig = L.lire_vcf; L.lire_vcf = faux_lecteur
vcf = (io.BytesIO(b'##fileformat=VCFv4.2\n'), 'patient.vcf')
r = c.post('/analyser', data={'specialite': specs[0], 'vcf': vcf, 'hla_HLA-B*57:01': 'porteur', 'cyp2d6': '0', 'echantillon': 'S1'}, content_type='multipart/form-data')
jv = jid_de(r.headers['Location'])
for _ in range(40):
    e = c.get('/etat/' + jv).get_json()
    if e['etat'] != 'en_cours': break
    time.sleep(0.25)
t = c.get('/resultats/' + jv).get_data(as_text=True)
verdict('T14 circuit VCF (lecteur simulé) : HLA et échantillon transmis, VCF supprimé du disque', e['etat'] == 'termine' and 'HLA-B*57:01=porteur' in vus.get('hla', '') and vus.get('echantillon') == 'S1'
        and vus.get('existe') and not os.path.exists(os.path.join(TRAV, jv)), str(vus))
verdict('T15 CYP2D6 saisi : marqué « Fourni par l\'utilisateur » (jamais « lu dans le VCF »)', 'Fourni par l&#39;utilisateur (test externe)' in t or "Fourni par l'utilisateur (test externe)" in t)
verdict('T16 HLA-B*57:01 porteur saisi : abacavir à éviter dans les alertes de sécurité', '<b style="font-size:1.1rem">abacavir</b>' in t.split('À éviter pour ce patient (toutes spécialités)')[1].split('<form method="get"')[0])
# CYP2D6 non fourni -> médicaments CYP2D6 « non évalués » + message explicite
L.lire_vcf = faux_lecteur
r = c.post('/analyser', data={'specialite': specs[0], 'vcf': (io.BytesIO(b'##fileformat=VCFv4.2\n'), 'p2.vcf')}, content_type='multipart/form-data'); j2 = jid_de(r.headers['Location'])
for _ in range(40):
    if c.get('/etat/' + j2).get_json()['etat'] != 'en_cours': break
    time.sleep(0.25)
t2 = c.get('/resultats/' + j2).get_data(as_text=True)
verdict('T17 CYP2D6 non fourni : message explicite « pas lisible depuis un VCF » et médicaments non évalués', "CYP2D6 n'est pas lisible depuis un VCF" in t2.replace('&#39;', "'"))
res2 = mo.predire(json.load(open(os.path.join(TRAV, 'jobs', j2 + '.json'), encoding='utf-8'))['profil'])
verdict('T18 aucun médicament dépendant de CYP2D6 n\'est classé « compatible » sans CYP2D6 (jamais supposé normal)',
        all(x['statut'] == 'non_determine_gene' or x['statut'] == 'dl_indisponible' or 'CYP2D6' not in x.get('genes_requis', []) or x.get('valeurs_requises', {}).get('CYP2D6') is not None for x in res2))
class Refus(Exception): pass
Refus.__name__ = 'VCFRefuse'
def lecteur_refuse(*a, **k): raise Refus('Le VCF ne contient aucun échantillon.')
L.lire_vcf = lecteur_refuse
r = c.post('/analyser', data={'specialite': specs[0], 'vcf': (io.BytesIO(b'x'), 'p3.vcf')}, content_type='multipart/form-data'); j3 = jid_de(r.headers['Location'])
for _ in range(40):
    if c.get('/etat/' + j3).get_json()['etat'] != 'en_cours': break
    time.sleep(0.25)
verdict('T19 fichier refusé par le lecteur : message affiché, pas de résultat', c.get('/etat/' + j3).get_json()['etat'] == 'refuse' and 'Fichier refusé' in c.get('/progression/' + j3).get_data(as_text=True))
L.lire_vcf = L_orig
# --- HLA et CYP2D6 facultatifs APRÈS les résultats
t2 = c.get('/resultats/' + j2).get_data(as_text=True)
verdict('T19b formulaire facultatif « Compléter » présent quand CYP2D6 et HLA sont absents', 'Compléter avec un test de laboratoire (facultatif)' in t2 and 'name="cyp2d6"' in t2 and 'name="hla_HLA-B*57:01"' in t2)
r = c.post('/completer/' + j2, data={'specialite': specs[0], 'cyp2d6': '1', 'hla_HLA-B*57:01': 'porteur'})
t3 = c.get('/resultats/' + j2).get_data(as_text=True)
carte3 = t3.split('À éviter pour ce patient (toutes spécialités)')[1].split('<form method="get"')[0] if 'À éviter pour ce patient (toutes spécialités)' in t3 else ''
verdict('T19c complétion : CYP2D6 et HLA-B*57:01 pris en compte, origine « saisi par l\'utilisateur », abacavir à éviter', r.status_code == 302 and '<b style="font-size:1.1rem">abacavir</b>' in carte3
        and "Saisi par l&#39;utilisateur" in t3 + t3.replace("'", '&#39;') and 'name="cyp2d6"' not in t3)
r = c.post('/completer/' + j2, data={'cyp2d6': '9'}); verdict('T19d complétion invalide refusée', 'erreur' in r.headers['Location'])

# --- suppression et purge
r = c.post('/supprimer/' + jv); verdict('T20 suppression des données', r.status_code == 302 and not os.path.exists(os.path.join(TRAV, 'jobs', jv + '.json')) and c.get('/resultats/' + jv).status_code == 404)
vieux = os.path.join(TRAV, 'jobs', 'aaaaaaaaaaaa.json'); open(vieux, 'w').write('{}'); os.utime(vieux, (time.time() - 25 * 3600,) * 2)
c.post('/demo', data={'specialite': specs[0]}); verdict('T21 purge automatique des tâches de plus de 24 h', not os.path.exists(vieux))
t = c.get('/apropos').get_data(as_text=True); verdict('T22 page « méthode, performances et limites »', all(k in t for k in ('0,9980', '0,0489', '0,467', 'Limites', 'non validé cliniquement')))

shutil.rmtree(TRAV, ignore_errors=True)
print('\nRÉSULTAT GLOBAL :', 'TOUT PASSE' if OK else 'ÉCHEC')
sys.exit(0 if OK else 1)
