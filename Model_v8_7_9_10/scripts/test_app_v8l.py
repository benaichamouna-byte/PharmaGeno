#!/usr/bin/env python3
"""
test_app_v8l.py : tests de l'application web v8l (client de test Flask ; aucun entraînement ; ensemble final non lu).
À lancer depuis le dossier scripts/ :  python3 test_app_v8h.py   (variables facultatives PHARMAGENO_MODELES_V8F et PHARMAGENO_MODELES_V8I pour indiquer d'autres dossiers que ../modeles_v8f et ../modeles_v8i)
Ce qui est testé : la LOGIQUE et la mise en forme (pages, PDF, JSON, refus d'entrées invalides, suppression, en-têtes, échappement HTML, circuit VCF avec lecteur simulé).
Ce qui n'est PAS testé ici : la lecture réelle d'un VCF par PyPGx (voir valider_vcf_v8.py et test_app_v8e_vcf_reel.py) ni la performance du modèle.
"""
import io, json, os, re, shutil, sys, tempfile, time, types
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI); os.chdir(ICI)
import app_pharmageno_v8l as A

OK = True
def verdict(nom, cond, detail=''):
    global OK; OK &= bool(cond); print(('PASS ' if cond else 'FAIL ') + nom + (' | ' + detail if detail else ''), flush=True)

TRAV = tempfile.mkdtemp(prefix='tw_v8_')
cfg = types.SimpleNamespace(modeles_choix=os.environ.get('PHARMAGENO_MODELES_V8I', os.path.join(ICI, '..', 'modeles_v8i')), donnees=os.path.join(ICI, '..', 'data'), modeles=os.environ.get('PHARMAGENO_MODELES_V8F', os.path.join(ICI, '..', 'modeles_v8f')), modeles_xgb=os.path.join(ICI, '..', 'results', 'resultats_final_v8'), codage=None, tables=None,
                            bundle='~/pypgx-bundle', travail=TRAV, pgx_python=sys.executable, taille_max_mo=5)
app = A.creer_app(cfg); c = app.test_client(); mo, rc = app.mo, app.rc
specs = [s for s in rc.specialites() if len(rc.medicaments_de_specialite(s)) > 0]   # v8l : l'entrée du clinicien est la spécialité

r = c.get('/'); t = r.get_data(as_text=True)
verdict('T1 accueil simplifié : VCF + spécialité + bouton ; ni HLA, ni CYP2D6, ni bloc démonstration', r.status_code == 200 and 'name="vcf"' in t and 'name="specialite"' in t and 'name="classe"' not in t and 'Lancer l' in t
        and 'name="hla_' not in t and 'cyp2d6' not in t and 'Profil de démonstration' not in t and specs[0] in t, '%d spécialités' % len(specs))

# --- démonstration, toutes les spécialités
def jid_de(loc): return loc.rsplit('/', 1)[1]
import re
def rouges(t):
    """zones « à éviter » de l'écran principal : feu rouge de la spécialité + encadré « à éviter aussi » (autres spécialités)"""
    m1 = re.search(r'class="feu feu-rouge".*?</div>', t, re.S); m2 = re.search(r'<div class="danger">.*?</div>', t, re.S)
    return (m1.group(0) if m1 else '') + (m2.group(0) if m2 else '')
def dans(m, zone): return re.search(r'>\s*' + re.escape(m) + r'\s*</b>', zone) is not None
mauvais = []; n_pages = 0; trop_de_cartes = 0; sans_expl = 0; evit_manquants = 0; pdf_ko = 0; json_ko = 0; patient_ko = 0
for sp in specs:
    r = c.post('/demo', data={'specialite': sp}); loc = r.headers['Location']; jid = jid_de(loc)
    r = c.get(loc); t = r.get_data(as_text=True); n_pages += 1
    if r.status_code != 200 or 'Traceback' in t or '{{' in t or '{%' in t or '>None<' in t or 'undefined' in t: mauvais.append(sp)
    # tout médicament avec un avis EVITER (n'importe quelle spécialité) doit figurer dans la carte d'alertes de sécurité
    j = json.load(open(os.path.join(TRAV, 'jobs', jid + '.json'), encoding='utf-8')); res = mo.predire(j['profil']); par = {x['medicament']: x for x in res}
    attendus = [m for m, x in par.items() if 'EVITER' in {x.get('action_dl'), x.get('action_xgboost'), x.get('action_cpic')}]
    carte = rouges(t)
    evit_manquants += sum(1 for m in attendus if not dans(m, carte))
    cls = [k for k, v in mo.classes_choix.items() if len(set(v['medicaments']) & set(rc.medicaments_de_specialite(sp))) >= 2]; par_ = {x['medicament']: x for x in res}
    top = t.split('<details class="carte"><summary><b>Détails scientifiques')[0]; attendus_m = set()
    for k in cls: attendus_m |= {m for m in mo.choix(j['profil'], k, res)['ensemble'] if rc.classer(par_[m], par_) != 'a_eviter'}
    trop_de_cartes += (not all(m in top for m in attendus_m)); sans_expl += ((not cls) and 'Le DL ne peut pas choisir entre médicaments' not in top)
    r = c.get('/pdf/' + jid); pdf_ko += not (r.status_code == 200 and r.mimetype == 'application/pdf' and r.data[:5] == b'%PDF-' and len(r.data) > 4000)
    r = c.get('/json/' + jid);
    try: d = json.loads(r.get_data(as_text=True)); json_ko += not (d['profil'] == j['profil'] and len(d['moteur']) == len(res))
    except Exception: json_ko += 1
    r = c.get('/patient/' + jid); tp = r.get_data(as_text=True); patient_ko += not (r.status_code == 200 and 'Traceback' not in tp and 'à lire d\'abord' in tp.lower())
verdict('T2 démonstration : toutes les spécialités rendent une page sans erreur ni gabarit non résolu', not mauvais, '%d pages ; mauvais : %s' % (n_pages, mauvais))
verdict('T3 tout médicament avec au moins un avis EVITER figure dans les alertes de sécurité (toutes spécialités)', evit_manquants == 0, '%d spécialités' % len(specs))
verdict('T3b pour chaque spécialité : tous les médicaments recommandés par le DL figurent dans la recommandation en haut ; sans groupe de médicaments, le message le dit', trop_de_cartes == 0 and sans_expl == 0)
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
t = c.get(loc + '?specialite=Inexistante').get_data(as_text=True); verdict('T10 spécialité inconnue en paramètre : repli sans erreur', 'Ce que le DL recommande pour ce patient' in t)

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
verdict('T16 HLA-B*57:01 porteur saisi : abacavir à éviter dans les alertes de sécurité', dans('abacavir', rouges(t)))
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
carte3 = rouges(t3)
verdict('T19c complétion : CYP2D6 et HLA-B*57:01 pris en compte, origine « saisi par l\'utilisateur », abacavir à éviter', r.status_code == 302 and dans('abacavir', carte3)
        and "Saisi par l&#39;utilisateur" in t3 + t3.replace("'", '&#39;') and 'name="cyp2d6"' not in t3)
import re as _re
vis3 = t3.split('<details class="carte"><summary>Détail complet pour vérification')[0] + t3.split('<form class="nopr" action=')[-1]
verdict('T19e vocabulaire clinicien : HLA « positif », ni « porteur » ni « valeur de codage » ni « probable » dans l\'écran principal', 'positif' in t3.lower() and 'valeur de codage' not in vis3.lower() and 'probable' not in vis3.lower() and '>Porteur<' not in t3)
verdict('T19f formulaire HLA : Positif / Négatif / Non testé', '<option value="porteur">Positif</option>' in t2 and '<option value="non_porteur">Négatif</option>' in t2)
r = c.post('/completer/' + j2, data={'cyp2d6': '9'}); verdict('T19d complétion invalide refusée', 'erreur' in r.headers['Location'])

# --- suppression et purge
r = c.post('/supprimer/' + jv); verdict('T20 suppression des données', r.status_code == 302 and not os.path.exists(os.path.join(TRAV, 'jobs', jv + '.json')) and c.get('/resultats/' + jv).status_code == 404)
vieux = os.path.join(TRAV, 'jobs', 'aaaaaaaaaaaa.json'); open(vieux, 'w').write('{}'); os.utime(vieux, (time.time() - 25 * 3600,) * 2)
c.post('/demo', data={'specialite': specs[0]}); verdict('T21 purge automatique des tâches de plus de 24 h', not os.path.exists(vieux))
t = c.get('/apropos').get_data(as_text=True); verdict('T22 page « méthode, performances et limites »', all(k in t for k in ('0,9980', '0,0489', '0,467', '99,55', 'Limites', 'non validé cliniquement')))

shutil.rmtree(TRAV, ignore_errors=True)
# --- v8l : le DL recommande ; nouvelle instance (les tests précédents ont supprimé le dossier de travail)
TRAV2 = tempfile.mkdtemp(prefix='tw_v8l_'); cfg2 = types.SimpleNamespace(**dict(vars(cfg), travail=TRAV2)); app2 = A.creer_app(cfg2); c2 = app2.test_client(); mo2 = app2.mo; rc2 = app2.rc
r = c2.post('/demo', data={'specialite': 'Cardiologie'}); loc = r.headers['Location']; t = c2.get(loc).get_data(as_text=True); jid = jid_de(loc)
jj = json.load(open(os.path.join(TRAV2, 'jobs', jid + '.json'), encoding='utf-8')); res2 = mo2.predire(jj['profil']); par2 = {x['medicament']: x for x in res2}
verdict('T23 la « Recommandation du DL pour ce patient » est la première réponse de la page, avant les alertes ; le contenu scientifique est replié dans « Détails scientifiques »',
        'Ce que le DL recommande pour ce patient' in t and t.index('Ce que le DL recommande pour ce patient') < t.index('À éviter aussi pour ce patient') < t.index('Détails scientifiques') < t.index('Le DL en action') and 'Pourquoi :' in t.split('Détails scientifiques')[0] and 'Spécialité : Cardiologie' in t)
import torch
ms = mo2.classes_choix['C10AA']['medicaments']; cand = [m for m in ms if 'action_dl' in par2.get(m, {})]
vec, _ = mo2.vecteur(jj['profil']); x = torch.from_numpy(((vec - mo2.mu_c) / mo2.sd_c).astype('float32'))[None]
with torch.no_grad(): sc = mo2.dlc(x)[0]
z = torch.stack([sc[mo2._idx[m]] for m in cand]); p = torch.softmax(z, 0).numpy(); ens = [m for m, pm in sorted(zip(cand, p), key=lambda a: -a[1]) if pm >= 0.5 * p.max()]
ens = [m for m in ens if rc2.classer(par2[m], par2) != 'a_eviter']
import re, html as _h
def texte(h): return re.sub(r'\s+', ' ', _h.unescape(re.sub(r'<[^>]+>', ' ', h))).replace(' · ', ' · ')
top_html = t.split('Détails scientifiques')[0]; top = texte(top_html)
verdict('T24 statines (Cardiologie, profil de démonstration) : médicaments recommandés affichés = sortie du réseau recalculée indépendamment', (' · '.join(ens) in top) and len(ens) >= 1, 'attendus %s | candidats %s' % (ens, cand))
verdict("T25 un médicament à éviter n'est jamais affiché comme recommandé", all(rc2.classer(par2[m], par2) != 'a_eviter' for m in ens) and 'simvastatin' not in ' · '.join(ens))
dec = mo2.genes_decisifs_choix(jj['profil'], 'C10AA', res2); n_ok = 0
for d in dec:
    q = dict(jj['profil']); q[d['gene']] = 0.0 if d['gene'].startswith('HLA-') else 1.0; e2 = [m for m in mo2.choix(q, 'C10AA')['ensemble'] if m in cand]
    n_ok += set(e2) == set(d['ensemble_si_normal'])
verdict('T26 gènes qui changent le choix : le moteur et une substitution dans le profil suivie de choix() donnent le même ensemble', n_ok == len(dec), '%d gènes décisifs, %d concordants' % (len(dec), n_ok))
verdict("T26b ces gènes sont affichés à l'écran avec leur lecture, dans la recommandation en haut", all(('%s (' % d['gene']) in top for d in dec) and len(dec) > 0, '%d gènes : %s' % (len(dec), [d['gene'] for d in dec]))
import pandas as pd
D = os.path.join(ICI, '..', 'data'); P = pd.read_csv(os.path.join(D, 'profils_genes_v4.csv')).set_index('sample_id'); lab = pd.read_csv(os.path.join(D, 'phenotype_drug_dataset_v7.csv'), usecols=['sample_id', 'drug', 'action']).set_index(['sample_id', 'drug']).action.to_dict()
ech = list(np.random.RandomState(9).choice(P.index, 25, replace=False)); n_ens = n_ev = n_ev_perm = 0
for s in ech:
    prof = {g: (None if pd.isna(P.at[s, g]) else float(P.at[s, g])) for g in mo2.genes_profil}
    for code, cl in mo2.classes_choix.items():
        ch = mo2.choix(prof, code)
        if not ch['ensemble']: continue
        n_ens += len(ch['ensemble']); n_ev += sum(lab.get((s, m)) == 'EVITER' for m in ch['ensemble'])
        noms = [d['medicament'] for d in ch['candidats']]; probs = [d['proba_choix'] for d in ch['candidats']][::-1]; pm = max(probs)
        n_ev_perm += sum(lab.get((s, m)) == 'EVITER' for m, pp in zip(noms, probs) if pp >= 0.5 * pm)
verdict("T27 câblage : part des médicaments « EVITER » (étiquette du corpus) dans l'ensemble prédit <= 1 % (profils d'entraînement)", n_ens > 0 and n_ev / n_ens <= 0.01, '%d médicaments prédits, %d étiquetés EVITER' % (n_ens, n_ev))
verdict('T27b contre-épreuve : avec les probabilités attribuées aux mauvais médicaments, cette part augmente nettement', n_ev_perm > n_ev + 5, '%d contre %d' % (n_ev_perm, n_ev))
tp = c2.get('/patient/' + jid).get_data(as_text=True); dj = json.loads(c2.get('/json/' + jid).get_data(as_text=True))
fich = [c for c in dj['choix'] if c['code'] == 'C10AA'][0]['fiches']
verdict("T28 vue patient et JSON : mêmes médicaments recommandés que l'écran principal", all(m in tp for m in ens) and [f['medicament'] for f in fich] == ens and dj['specialite'] == 'Cardiologie')
t_b = c2.get(loc + '?specialite=Psychiatrie').get_data(as_text=True); top_b = t_b.split('Détails scientifiques')[0].split('À éviter aussi pour ce patient')[0]   # la recommandation seule (l'encadré rouge cite aussi des alternatives)
verdict("T29 changer de spécialité dans la page de résultats change la réponse du DL", 'Spécialité : Psychiatrie' in t_b and 'ISRS' in top_b and 'pravastatin' not in top_b)
rs = c2.post('/demo', data={'specialite': 'Gynécologie-obstétrique'}); tg = c2.get(rs.headers['Location']).get_data(as_text=True)
verdict("T30 spécialité sans groupe de médicaments interchangeables : message clair, pas de choix inventé", 'Le DL ne peut pas choisir entre médicaments pour cette spécialité' in tg.split('Détails scientifiques')[0])
# --- v8l : feux tricolores
def section(h, debut, fins):
    if debut not in h: return ''
    i = h.index(debut); fin = min([h.index(f, i + 1) for f in fins if f in h[i + 1:]] or [len(h)]); return texte(h[i:fin])
vert_t = section(top_html, '✔ À prescrire', ['▲ Dose', '✖ À éviter', 'Pourquoi'])
orange_t = section(top_html, '▲ Dose à adapter', ['✖ À éviter', 'Pourquoi'])
rouge_t = section(top_html, '✖ À éviter', ['Pourquoi'])
ma, mv, mo_ = 'atorvastatin', 'simvastatin', 'pravastatin'
verdict('T31 feux : atorvastatin (adapter la dose) en orange seulement ; simvastatin (éviter) en rouge seulement ; pravastatin en vert seulement',
        ma in orange_t and ma not in vert_t and ma not in rouge_t and mv in rouge_t and mv not in vert_t and mv not in orange_t and mo_ in vert_t and mo_ not in orange_t and mo_ not in rouge_t,
        'vert=%s | orange=%s | rouge=%s' % (vert_t[:80], orange_t[:60], rouge_t[:50]))
act = {m: par2[m].get('action_dl') for m in (ma, mv, mo_)}
verdict("T31b les feux suivent les actions du moteur recalculées : atorvastatin ADAPTER_DOSE ou SURVEILLER, simvastatin EVITER (DL ou règle), pravastatin STANDARD", act[ma] in ('ADAPTER_DOSE', 'SURVEILLER') and act[mo_] == 'STANDARD' and (act[mv] == 'EVITER' or rc2.classer(par2[mv], par2) == 'a_eviter'), str(act))
tous_feux = [m for sec in (vert_t, orange_t, rouge_t) for m in re.findall(r'[a-z]{5,}', sec)]
verdict("T32 aucune terme anglais de phénotype dans l'écran principal (Decreased/Normal/Poor/Intermediate function ou metabolizer)", not re.search(r'(?i)decreased function|normal function|poor metabolizer|intermediate metabolizer|ultrarapid|rapid metabolizer', top + texte(t.split('Détails scientifiques')[0].split('Spécialité')[0])), '')
_m = re.search(r'Non évalués pour ce patient : (\d+) médicament', top); n_json = len(dj['recommandation']['non_evalues'])
verdict("T33 une seule liste de médicaments non évalués, avec le même nombre que le moteur (pas de « 5 » puis « 6 »)", 'Aucune recommandation pour' not in t and _m is not None and int(_m.group(1)) == n_json and all(x['medicament'] in top for x in dj['recommandation']['non_evalues']), 'affiché %s | moteur %d' % (_m.group(1) if _m else None, n_json))
verdict("T34 l'encadré « à éviter aussi » ne répète jamais un médicament déjà dans le résumé de la spécialité", all(m not in texte(top_html.split('À éviter aussi')[1].split('Spécialité')[0]) for m in re.findall(r'[a-z]{6,}', rouge_t) if m in par2) if 'À éviter aussi' in top_html else True)
t_p = c2.post('/demo', data={'specialite': 'Psychiatrie'}); tp_ = c2.get(t_p.headers['Location']).get_data(as_text=True); tp_top = tp_.split('Détails scientifiques')[0]
verdict("T35 Psychiatrie : simvastatin (autre spécialité) apparaît dans « à éviter aussi » et pas dans la liste verte", 'À éviter aussi' in tp_top and 'simvastatin' in texte(tp_top.split('À éviter aussi')[1]) and 'simvastatin' not in section(tp_top, '✔ À prescrire', ['À éviter aussi', 'Pourquoi']))
print('\nRÉSULTAT GLOBAL :', 'TOUT PASSE' if OK else 'ÉCHEC')
sys.exit(0 if OK else 1)
