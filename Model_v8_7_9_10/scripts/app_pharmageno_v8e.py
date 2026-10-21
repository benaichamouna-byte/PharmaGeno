#!/usr/bin/env python3
"""
app_pharmageno_v8e.py : application web PharmaGeno v8e (Flask) : écran simplifié (VCF + spécialité, 1 à 3 médicaments avec prédiction et explication, HLA et CYP2D6 facultatifs après les résultats).
app_pharmageno_v8.py et app_pharmageno_v7.py restent intacts.

Chaîne : VCF (+ allèles HLA saisis) -> vcf_to_profile_v8.lire_vcf (PyPGx 0.27.0) -> profil de 22 gènes
         -> moteur_v8.MoteurPGx : le DL (film, identifiant de médicament) est le MOTEUR de la recommandation ; XGBoost = second avis ;
            la règle CPIC/DPWG est affichée à côté (jamais utilisée pour calculer la prédiction) ; alerte en cas de désaccord ;
            couche de sécurité : « non évalué » quand le modèle ne peut pas répondre de façon fiable
         -> recommandation_v8.Recommandeur (par spécialité) -> page de résultats / page patient / PDF / JSON.

Lancement (depuis le dossier scripts/ ; environnement avec flask, reportlab, torch, xgboost ; pysam + PyPGx 0.27.0 + Java seulement pour analyser un VCF) :
    python3 app_pharmageno_v8e.py --bundle ~/pypgx-bundle --pgx-python ~/pgxenv/bin/python
puis ouvrir http://127.0.0.1:5000 . Le bouton « profil de démonstration » fonctionne sans VCF ni PyPGx.
Par défaut, les données sont lues dans ../data et les modèles dans ../results/resultats_final_v8 (arborescence du dossier Model_v8_7_9_10) ;
--donnees et --modeles permettent d'indiquer d'autres dossiers.

Données du patient : le VCF téléversé et les fichiers intermédiaires sont supprimés dès la fin de l'analyse ; seul le profil (valeurs par gène) reste dans
<travail>/jobs/<id>.json jusqu'au clic sur « Supprimer mes données » ; les tâches de plus de 24 h sont supprimées automatiquement. Le serveur n'écoute que
sur 127.0.0.1.
"""
import argparse, json, os, re, shutil, sys, threading, time, traceback, uuid
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from moteur_v8 import MoteurPGx
from recommandation_v8 import Recommandeur, LIBELLE_PRO, TEXTE_PATIENT, AVERTISSEMENT_GENERAL
from rapport_pdf_v8 import construire_pdf

DEMO_ECHANTILLON = 'HG00101'   # profil réel du corpus (1000 Genomes) dont les 22 gènes du modèle sont connus ; vu à l'entraînement : sert UNIQUEMENT à montrer l'interface
CYP2D6_CHOIX = {'': None, '0': 0.0, '0.5': 0.5, '1': 1.0, '2': 2.0}   # valeurs présentes dans le corpus pour CYP2D6 (pas de 1,5)
HLA_CHOIX = {'': None, 'non_porteur': 'non_porteur', 'porteur': 'porteur'}   # « probable » (0,5) et « inconnu » ne sont pas proposés : exclus de l'entraînement / équivalents à « non renseigné »
# v8e (depuis v8b) : libellés alignés sur les sources cliniciens (CPIC, guide britannique, UF Health) ; recommandation_v8 non modifié (le module recommandation_v8 n'est pas modifié)
LIBELLE_PRO['STANDARD'] = "À dose standard : pas d'adaptation liée aux gènes analysés"
LIBELLE_PRO['EVITER'] = "Éviter pour ce profil génétique"
TEXTE_PATIENT['STANDARD'] = "Pour les gènes analysés, rien n'indique qu'il faille changer la dose ou la manière habituelle de prendre ce médicament."
ACTION_COURT = {'EVITER': 'Éviter', 'ADAPTER_DOSE': 'Adapter la dose', 'SURVEILLER': 'Surveiller', 'STANDARD': 'À dose standard'}
ORIGINE = {'appele': 'Lu dans le VCF (PyPGx)', 'saisi': 'Saisi par l\'utilisateur', 'fourni': 'Fourni par l\'utilisateur (test externe)', 'demo': 'Profil de démonstration',
           'non_determine': 'Non déterminé'}
CATEGORIE_LIBELLE = {'a_eviter': 'À éviter', 'proposable': 'Compatible', 'a_verifier': 'À vérifier', 'non_evalue': 'Non évalué', 'reference_seule': 'Règle de guideline seule'}
DUREE_CONSERVATION_H = 24

# Mesures (corpus v7, validation croisée groupée par famille, 5 plis) ; sources : results/resume_dl_v9_sortie.txt, results/RESUME_graines_et_medicament_inconnu_v1.csv.
# L'ensemble final mis de côté n'a PAS encore été utilisé (état au 20 octobre 2026).
PERFORMANCES = dict(
    patients_nouveaux=[('XGBoost (1 graine)', '0,9999', '0,0011'), ('Random Forest (1 graine)', '0,9817', '0,0489'),
                       ('DL film, identifiant de médicament, EVITER x2 (5 graines)', '0,9980 ± 0,0010', '0,0029 ± 0,0010')],
    medicament_jamais_vu=[('Témoin « classe majoritaire »', '0,261'), ('Random Forest', '0,502'), ('DL', '0,467'), ('XGBoost', '0,454')])


def _lecture_hla(v):
    return 'positif' if v == 1.0 else ('négatif' if v == 0.0 else 'non testé')


def _vocab(obj):
    """vocabulaire clinicien (sources : CPIC termes finaux, rapports de laboratoire) : HLA positif / négatif ; gène non lu = non testé ; pas de « valeur de codage » dans l'explication"""
    if isinstance(obj, dict):
        for e in obj.get('explication') or []:
            if isinstance(e, dict) and 'gene' in e:
                v = e.get('valeur_codage')
                if str(e['gene']).startswith('HLA-'): e['lecture'] = _lecture_hla(v)
                elif v is None: e['lecture'] = 'non testé'
                elif str(e.get('lecture', '')).startswith('valeur de codage'): e['lecture'] = 'non interprété (aucune règle pour ce cas)'
        for x in obj.values(): _vocab(x)
    elif isinstance(obj, (list, tuple)):
        for x in obj: _vocab(x)
    return obj


def creer_app(cfg):
    app = Flask(__name__, template_folder=os.path.join(ICI, 'templates_v8e'))
    app.config['MAX_CONTENT_LENGTH'] = cfg.taille_max_mo * 1024 * 1024
    D = os.path.abspath(cfg.donnees)
    chemin = lambda f: os.path.join(D, f)
    mo = MoteurPGx(cfg.modeles, chemin('domaine_v8.json'), chemin('regles_v7_monogene.csv'), chemin('regles_v2_corrigees_multigene_v7.csv'))
    rc = Recommandeur(chemin('atc_mapping_medicaments_v1.csv'), chemin('specialite_atc_v1.csv'), chemin('alternatives_atc4_v1.csv'), sorted(mo.dom))
    travail = os.path.abspath(cfg.travail); os.makedirs(os.path.join(travail, 'jobs'), exist_ok=True)
    pool = ThreadPoolExecutor(max_workers=1)   # PyPGx est lourd : une analyse à la fois, les autres attendent
    verrou = threading.Lock()
    nb_par_spec = {s: len(rc.medicaments_de_specialite(s)) for s in rc.specialites()}
    n_dans_modele = sum(1 for v in mo.dom.values() if v['dans_modele'])
    HLA = ['HLA-B*15:02', 'HLA-B*57:01', 'HLA-B*58:01', 'HLA-A*31:01']
    hla_meds = {a: sorted(m for m, v in mo.dom.items() if a in v['genes']) for a in HLA}
    profil_demo = None
    try:
        import pandas as pd
        P = pd.read_csv(chemin('profils_genes_v4.csv')).set_index('sample_id')
        if DEMO_ECHANTILLON in P.index:
            profil_demo = {g: (None if pd.isna(P.at[DEMO_ECHANTILLON, g]) else float(P.at[DEMO_ECHANTILLON, g])) for g in mo.genes_modele}
    except Exception:
        profil_demo = None

    def f_job(jid): return os.path.join(travail, 'jobs', jid + '.json')

    def purger():
        """supprime les tâches de plus de DUREE_CONSERVATION_H heures (profil du patient inclus)"""
        limite = time.time() - DUREE_CONSERVATION_H * 3600
        for nom in os.listdir(os.path.join(travail, 'jobs')):
            p = os.path.join(travail, 'jobs', nom)
            if nom.endswith('.json') and os.path.getmtime(p) < limite:
                try: os.remove(p); shutil.rmtree(os.path.join(travail, nom[:-5]), ignore_errors=True)
                except OSError: pass

    def charger(jid):
        if not re.fullmatch(r'[0-9a-f]{12}', jid or ''): abort(404)
        try:
            with open(f_job(jid), encoding='utf-8') as f: return json.load(f)
        except FileNotFoundError:
            abort(404)

    def ecrire(j):
        with verrou:
            tmp = f_job(j['id']) + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f: json.dump(j, f, ensure_ascii=False, indent=1)
            os.replace(tmp, f_job(j['id']))

    def maj(jid, **kw):
        j = charger(jid); j.update(kw); ecrire(j)

    def nouveau(mode, specialite, nom_fichier=None):
        purger()
        j = dict(id=uuid.uuid4().hex[:12], mode=mode, specialite=specialite, nom_fichier=nom_fichier, etat='en_cours', pct=0, message='En attente', cree=time.time())
        ecrire(j); return j

    def surcharge_cyp2d6(j, val):
        """Valeur CYP2D6 fournie par l'utilisateur (test externe) : tracée comme telle, jamais présentée comme lue dans le VCF."""
        j['profil']['CYP2D6'] = val
        j['detail']['CYP2D6'] = dict(valeur=val, statut='fourni', phenotype_utilise='fourni par l\'utilisateur', genotype=None,
                                      motif="Valeur saisie par l'utilisateur (test CYP2D6 externe) : non vérifiée par l'application.")

    def travailler(jid, chemin_vcf, echantillon, cyp2d6, hla_txt):
        dossier = os.path.join(travail, jid)
        try:
            import vcf_to_profile_v8 as lecteur   # import tardif : pysam / PyPGx ne sont nécessaires que pour analyser un VCF
            r = lecteur.lire_vcf(chemin_vcf, cfg.bundle, os.path.join(dossier, 'pypgx'), cfg.codage or chemin('codage_pypgx_valeur_v7.csv'),
                                 cfg.tables or chemin('tables_cpic_v8.json'), hla_txt, None, echantillon or None, verbose=False,
                                 progres=lambda p, m: maj(jid, pct=p, message=m), pgx_python=cfg.pgx_python)
            j = charger(jid)
            j.update(profil=r['profil'], detail=r['detail'], assemblage=r['assemblage'], controle_assemblage=r.get('controle_assemblage'),
                     chrX_haploide_converti=r.get('genotypes_haploides_chrX_convertis'), hla_saisis=hla_txt, cyp2d6_fourni=cyp2d6)
            if cyp2d6 is not None: surcharge_cyp2d6(j, cyp2d6)
            j.update(etat='termine', pct=100, message='Analyse terminée'); ecrire(j)
        except Exception as e:
            nom = type(e).__name__
            if nom == 'VCFRefuse': maj(jid, etat='refuse', message=str(e))
            elif nom == 'PyPGxIndisponible': maj(jid, etat='erreur', message="L'analyse n'a pas pu être faite : " + str(e))
            elif isinstance(e, ValueError): maj(jid, etat='erreur', message='Entrée invalide : ' + str(e))
            else:
                traceback.print_exc(); maj(jid, etat='erreur', message='Erreur inattendue : %s' % str(e)[:300])
        finally:
            shutil.rmtree(dossier, ignore_errors=True)   # le VCF du patient n'est pas conservé

    def table_genes(j):
        out = []
        for g in mo.genes_modele:
            d = j['detail'].get(g, {}); v = j['profil'].get(g)
            if g.startswith('HLA-'): lecture = _lecture_hla(v)
            else: lecture = d.get('phenotype_utilise') or d.get('phenotype_pypgx') or ('non testé' if v is None else '-')
            if v is None: origine = 'Non renseigné' if g.startswith('HLA-') else ORIGINE['non_determine']
            else: origine = ORIGINE.get(d.get('statut'), ORIGINE['non_determine'])
            out.append(dict(gene=g, valeur=v, valeur_txt='-' if v is None else ('%g' % v), lecture=lecture, genotype=d.get('genotype'), origine=origine, motif=d.get('motif')))
        return out

    def calculer(j, spec, q):
        res = mo.predire(j['profil'])
        par = {r['medicament']: r for r in res}
        reco = rc.recommander(res, spec, max_proposes=3)
        fiche = rc.chercher_medicament(q, res) if q else None
        _vocab(reco); _vocab(fiche)
        cat = {r['medicament']: rc.classer(r, par) for r in res}
        compte_cat = {}
        for c in cat.values(): compte_cat[c] = compte_cat.get(c, 0) + 1
        globaux = []
        for m in sorted(par):
            if cat[m] == 'a_eviter':
                f = rc.chercher_medicament(m, res)
                if f.get('trouve'): globaux.append(f)
        globaux.sort(key=lambda f: -((f.get('proba_dl') or {}).get('EVITER') or 0))
        manq = {}
        for r in res:
            if r['statut'] == 'non_determine_gene':
                for g in r['genes_manquants']: manq.setdefault(g, []).append(r['medicament'])
        bloquants = []
        for g, ms in sorted(manq.items()):
            if g == 'CYP2D6':
                txt = ("CYP2D6 n'est pas lisible depuis un VCF de variants ponctuels (délétions et duplications du gène) : %d médicament(s) qui en dépendent sont non évalués. "
                       "Si vous disposez d'un test CYP2D6 externe, vous pouvez le saisir ci-dessous (facultatif)." % len(ms))
            elif g.startswith('HLA-'):
                txt = ("L'allèle %s n'a pas été renseigné (il ne se lit pas dans un VCF de variants ponctuels) : %d médicament(s) qui en dépendent sont non évalués (%s)."
                       % (g, len(ms), ', '.join(ms)))
            else:
                txt = "Le gène %s n'a pas pu être déterminé : %d médicament(s) qui en dépendent sont non évalués." % (g, len(ms))
            bloquants.append(txt)
        resume = ("Sur %d médicaments : %d à éviter (signalés par au moins un avis) ; %d compatibles (modèle, XGBoost et règle de guideline d'accord) ; "
                  "%d à vérifier (alerte) ; %d non évalués ; %d avec la règle de guideline seule (pas de prédiction du modèle)." % (
                      len(res), compte_cat.get('a_eviter', 0), compte_cat.get('proposable', 0), compte_cat.get('a_verifier', 0), compte_cat.get('non_evalue', 0),
                      compte_cat.get('reference_seule', 0)))
        _vocab(globaux)
        return res, reco, fiche, resume, manq, bloquants, globaux, cat

    LIMITES = [
        "Outil de recherche (mémoire de master), non validé cliniquement : il ne remplace ni un médecin, ni un pharmacien, ni une prescription.",
        "Les étiquettes d'entraînement viennent d'un moteur de règles CPIC/DPWG ; les entrées du réseau sont des phénotypes déjà calculés. Le modèle reproduit donc en grande partie "
        "ces règles : sa fiabilité mesurée est celle d'un accord avec les règles, pas une exactitude clinique.",
        "Seuls les gènes et médicaments listés sont couverts ; les autres médicaments, les interactions, les maladies, l'âge et les doses ne sont pas pris en compte.",
        "CYP2D6 et les allèles HLA ne se lisent pas dans un VCF de variants ponctuels ; sans saisie, les médicaments concernés sont « non évalués ».",
        "Pour un médicament absent de l'entraînement, le modèle n'est pas fiable (mesure : F1 macro 0,467 pour le DL ; 63 à 70 % des cas à éviter manqués selon le modèle) : l'application affiche « non évalué ».",
        "Pas de test sur des patients réels : les tests de l'application portent sur des profils du corpus d'entraînement, qui vérifient la logique, pas la performance.",
    ]
    METHODE = ("Méthode : réseau de neurones (couche FiLM conditionnée par l'identifiant du médicament) = moteur de la recommandation ; XGBoost = second avis ; règle CPIC/DPWG "
               "affichée comme référence, avec sa source ; alerte en cas de désaccord ; abstention si la confiance du modèle est au plus égale au seuil fixé sur la validation croisée "
               "(1 % des prédictions les moins sûres). Les génotypes du VCF sont convertis en phénotypes par PyPGx 0.27.0 puis par les tables CPIC. Le texte des guidelines est donné "
               "en anglais, sans traduction, pour ne pas le déformer.")

    @app.after_request
    def entetes(r):
        r.headers['Cache-Control'] = 'no-store'
        r.headers['X-Content-Type-Options'] = 'nosniff'
        r.headers['Referrer-Policy'] = 'no-referrer'
        r.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'"
        return r

    def specialites_liste(): return [(s, nb_par_spec[s]) for s in rc.specialites()]

    def choisir_spec(j):
        spec = request.args.get('specialite', j['specialite'])
        return spec if spec in rc.classes else j['specialite']

    @app.route('/')
    def index():
        return render_template('index.html', specialites=specialites_liste(), erreur=request.args.get('erreur'), taille_max=cfg.taille_max_mo, hla=HLA, hla_meds=hla_meds,
                               demo_ok=profil_demo is not None, demo_echantillon=DEMO_ECHANTILLON)

    @app.route('/apropos')
    def apropos():
        return render_template('apropos.html', limites=LIMITES, methode=METHODE, perf=PERFORMANCES, n_med=len(mo.dom), n_modele=n_dans_modele, n_genes=len(mo.genes_modele),
                               genes=mo.genes_modele, seuil=mo.seuil, niveau='%g %%' % (100 * float(mo.niveau_abstention)))

    @app.route('/analyser', methods=['POST'])
    def analyser():
        spec = request.form.get('specialite', '')
        if spec not in rc.classes or nb_par_spec.get(spec, 0) == 0:
            return redirect(url_for('index', erreur='Choisissez une spécialité couverte par le modèle.'))
        f = request.files.get('vcf')
        if f is None or not f.filename:
            return redirect(url_for('index', erreur='Aucun fichier VCF sélectionné.'))
        if not re.search(r'\.vcf(\.gz)?$', f.filename, re.I):
            return redirect(url_for('index', erreur='Le fichier doit se terminer par .vcf ou .vcf.gz.'))
        cyp = CYP2D6_CHOIX.get(request.form.get('cyp2d6', ''), 'invalide')
        if cyp == 'invalide':
            return redirect(url_for('index', erreur='Valeur CYP2D6 invalide.'))
        hla_parts = []
        for a in HLA:
            v = request.form.get('hla_' + a, '')
            if v not in HLA_CHOIX: return redirect(url_for('index', erreur='Valeur HLA invalide pour %s.' % a))
            if v: hla_parts.append('%s=%s' % (a, v))
        j = nouveau('vcf', spec, os.path.basename(f.filename))
        dossier = os.path.join(travail, j['id']); os.makedirs(dossier, exist_ok=True)
        chemin_vcf = os.path.join(dossier, 'patient.vcf.gz' if f.filename.lower().endswith('.gz') else 'patient.vcf'); f.save(chemin_vcf)
        pool.submit(travailler, j['id'], chemin_vcf, request.form.get('echantillon', '').strip(), cyp, ','.join(hla_parts))
        return redirect(url_for('progression', jid=j['id']))

    @app.route('/demo', methods=['POST'])
    def demo():
        spec = request.form.get('specialite', '')
        if spec not in rc.classes or nb_par_spec.get(spec, 0) == 0:
            return redirect(url_for('index', erreur='Choisissez une spécialité couverte par le modèle.'))
        if profil_demo is None:
            return redirect(url_for('index', erreur='Profil de démonstration indisponible (profils_genes_v4.csv introuvable dans le dossier des données).'))
        j = nouveau('demo', spec, 'profil de démonstration')
        j.update(profil=dict(profil_demo), assemblage=None, etat='termine', pct=100, message='Profil de démonstration',
                 detail={g: dict(valeur=v, statut='demo' if v is not None else 'non_determine', phenotype_utilise=None, genotype=None, motif=None) for g, v in profil_demo.items()})
        ecrire(j); return redirect(url_for('resultats', jid=j['id']))

    @app.route('/progression/<jid>')
    def progression(jid):
        j = charger(jid)
        if j['etat'] == 'termine': return redirect(url_for('resultats', jid=jid))
        return render_template('progression.html', j=j)

    @app.route('/etat/<jid>')
    def etat(jid):
        j = charger(jid); return jsonify(etat=j['etat'], pct=j['pct'], message=j['message'])

    @app.route('/resultats/<jid>')
    def resultats(jid):
        j = charger(jid)
        if j['etat'] != 'termine': return redirect(url_for('progression', jid=jid))
        spec = choisir_spec(j); q = request.args.get('q', '').strip()
        res, reco, fiche, resume, manq, bloquants, globaux, cat = calculer(j, spec, q)
        tous = []
        for r in sorted(res, key=lambda x: x['medicament']):
            tous.append(dict(medicament=r['medicament'], categorie=CATEGORIE_LIBELLE[cat[r['medicament']]], cat=cat[r['medicament']], dl=r.get('action_dl'), xgb=r.get('action_xgboost'),
                             cpic=r.get('action_cpic'), alertes=[a for a in r.get('alertes', [])], message=r.get('message') or ''))
        return render_template('resultats.html', j=j, spec=spec, specialites=specialites_liste(), reco=reco, fiche=fiche, q=q, genes=table_genes(j), resume=resume, bloquants=bloquants,
                               hla=HLA, hla_meds=hla_meds, hla_absents=[a for a in HLA if j['profil'].get(a) is None], cyp_absent=j['profil'].get('CYP2D6') is None,
                               erreur=request.args.get('erreur'),
                               globaux=globaux, tous=tous, noms=sorted(rc.meds), avertissement=AVERTISSEMENT_GENERAL, limites=LIMITES, methode=METHODE, court=ACTION_COURT, n_med=len(res),
                               n_modele=n_dans_modele)

    @app.route('/completer/<jid>', methods=['POST'])
    def completer(jid):
        """Ajout FACULTATIF après les résultats : allèles HLA (typage de laboratoire) et résultat CYP2D6 d'un test externe. Les valeurs sont tracées comme saisies par l'utilisateur."""
        j = charger(jid)
        if j['etat'] != 'termine': return redirect(url_for('progression', jid=jid))
        cyp = CYP2D6_CHOIX.get(request.form.get('cyp2d6', ''), 'invalide')
        if cyp == 'invalide': return redirect(url_for('resultats', jid=jid, erreur='Valeur CYP2D6 invalide.'))
        saisis = []
        for a in HLA:
            v = request.form.get('hla_' + a, '')
            if v not in HLA_CHOIX: return redirect(url_for('resultats', jid=jid, erreur='Valeur HLA invalide pour %s.' % a))
            if v:
                val = 1.0 if v == 'porteur' else 0.0
                j['profil'][a] = val
                j['detail'][a] = dict(valeur=val, statut='saisi', methode='saisie_utilisateur', phenotype_utilise=_lecture_hla(val), genotype=None,
                                      motif="Valeur saisie par l'utilisateur : non vérifiée par l'application.")
                saisis.append('%s=%s' % (a, v))
        if saisis: j['hla_saisis'] = ','.join(filter(None, [j.get('hla_saisis') or '', ','.join(saisis)]))
        if cyp is not None: surcharge_cyp2d6(j, cyp); j['cyp2d6_fourni'] = cyp
        ecrire(j)
        return redirect(url_for('resultats', jid=jid, specialite=request.form.get('specialite') or j['specialite']))

    @app.route('/patient/<jid>')
    def patient(jid):
        j = charger(jid)
        if j['etat'] != 'termine': return redirect(url_for('progression', jid=jid))
        spec = choisir_spec(j)
        res, reco, fiche, resume, manq, bloquants, globaux, cat = calculer(j, spec, '')
        return render_template('patient.html', j=j, spec=spec, reco=reco, globaux=globaux, bloquants=bloquants, avertissement=AVERTISSEMENT_GENERAL, court=ACTION_COURT,
                               texte_non_evalue=TEXTE_PATIENT['NON_EVALUE'])

    @app.route('/pdf/<jid>')
    def pdf(jid):
        j = charger(jid)
        if j['etat'] != 'termine': abort(404)
        spec = choisir_spec(j)
        res, reco, fiche, resume, manq, bloquants, globaux, cat = calculer(j, spec, request.args.get('q', '').strip())
        buf = construire_pdf(j, reco, table_genes(j), fiche, resume, AVERTISSEMENT_GENERAL, globaux, bloquants, LIMITES, METHODE)
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name='rapport_pharmageno_v8_%s.pdf' % jid)

    @app.route('/json/<jid>')
    def json_fiche(jid):
        """fiche complète (profil, lecture du VCF, sortie brute du moteur, recommandation) : transparence et reproductibilité"""
        j = charger(jid)
        if j['etat'] != 'termine': abort(404)
        spec = choisir_spec(j)
        res, reco, fiche, resume, manq, bloquants, globaux, cat = calculer(j, spec, '')
        out = dict(id=jid, mode=j['mode'], assemblage=j.get('assemblage'), specialite=spec, profil=j['profil'], lecture_vcf=j['detail'], resume=resume, bloquants=bloquants,
                   a_eviter_toutes_specialites=[f['medicament'] for f in globaux], recommandation=reco, moteur=res)
        return app.response_class(json.dumps(out, ensure_ascii=False, indent=1, default=str), mimetype='application/json',
                                  headers={'Content-Disposition': 'attachment; filename=fiche_pharmageno_v8_%s.json' % jid})

    @app.route('/supprimer/<jid>', methods=['POST'])
    def supprimer(jid):
        charger(jid)
        if os.path.exists(f_job(jid)): os.remove(f_job(jid))
        shutil.rmtree(os.path.join(travail, jid), ignore_errors=True)
        return redirect(url_for('index', erreur='Vos données ont été supprimées.'))

    app.mo, app.rc = mo, rc   # exposés pour les tests
    return app


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    racine = os.path.dirname(ICI)
    ap.add_argument('--donnees', default=os.path.join(racine, 'data')); ap.add_argument('--modeles', default=os.path.join(racine, 'results', 'resultats_final_v8'))
    ap.add_argument('--codage', default=None); ap.add_argument('--tables', default=None)
    ap.add_argument('--bundle', default=os.path.expanduser('~/pypgx-bundle')); ap.add_argument('--travail', default='pharmageno_travail')
    ap.add_argument('--pgx-python', default=(os.path.expanduser('~/pgxenv/bin/python') if os.path.exists(os.path.expanduser('~/pgxenv/bin/python')) else sys.executable), dest='pgx_python', help="interpréteur Python de l'environnement PyPGx (ex. ~/pgxenv/bin/python)")
    ap.add_argument('--port', type=int, default=5000); ap.add_argument('--taille-max-mo', type=int, default=500, dest='taille_max_mo')
    cfg = ap.parse_args(); cfg.pgx_python = os.path.expanduser(cfg.pgx_python); cfg.bundle = os.path.expanduser(cfg.bundle)
    app = creer_app(cfg)
    app.run(host='127.0.0.1', port=cfg.port, debug=False, threaded=True)


if __name__ == '__main__':
    main()
