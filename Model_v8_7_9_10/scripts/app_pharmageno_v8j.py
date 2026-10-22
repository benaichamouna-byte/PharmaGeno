#!/usr/bin/env python3
"""
app_pharmageno_v8j.py : application web PharmaGeno v8j (Flask) : VCF + indication (classe de médicaments) -> le DL « choix du médicament » PRÉDIT le ou les médicaments ; HLA et CYP2D6 facultatifs après les résultats.
app_pharmageno_v8f.py, app_pharmageno_v8e.py, app_pharmageno_v8.py et app_pharmageno_v7.py restent intacts.
v8f = v8e branchée sur le DL « profil génétique -> médicaments » (moteur_v8f.py) : le profil est la seule entrée du réseau, le médicament est une sortie.
v8g = v8f + deux affichages qui rendent le rôle du DL visible : l'encadré « Le DL en action » (profil complet en entrée, un passage, conseils pour tous les médicaments)
et, pour chaque médicament proposé ou à éviter, les gènes qui font changer la prédiction du DL (analyse de sensibilité, moteur_v8g.py). app_pharmageno_v8f.py reste intacte.
v8h = v8g + écran de PRÉDICTION : les médicaments affichés pour la spécialité sont le classement du DL ; à action égale, les médicaments dont un gène requis du patient n'a pas la valeur normale passent d'abord, puis la probabilité du DL
(règle de classement d'affichage, écrite sur l'écran ; ce n'est pas une validation clinique). app_pharmageno_v8g.py reste intacte.
v8i = le DL CHOISIT le médicament : le profil complet est la seule entrée, un score par médicament en sortie, un softmax dans la classe thérapeutique choisie par le clinicien (moteur_v8i.py, train_dl_choix_v1.py).
Il remplace le classement écrit à la main de v8h. app_pharmageno_v8h.py reste intacte.
v8j = même moteur que v8i ; l'ÉCRAN est celui d'un outil de recommandation : la réponse en clair en haut, le contenu scientifique replié dans « Détails scientifiques ». app_pharmageno_v8i.py reste intacte.

Chaîne : VCF (+ allèles HLA saisis) -> vcf_to_profile_v8.lire_vcf (PyPGx 0.27.0) -> profil de 22 gènes
         -> moteur_v8f.MoteurPGxProfil : le DL « profil -> médicaments » est le MOTEUR de la recommandation ; XGBoost (ancien modèle) = second avis ;
            la règle CPIC/DPWG est affichée à côté (jamais utilisée pour calculer la prédiction) ; alerte en cas de désaccord ;
            couche de sécurité : « non évalué » quand le modèle ne peut pas répondre de façon fiable
         -> recommandation_v8.Recommandeur (par spécialité) -> page de résultats / page patient / PDF / JSON.

Lancement (depuis le dossier scripts/ ; environnement avec flask, reportlab, torch, xgboost ; pysam + PyPGx 0.27.0 + Java seulement pour analyser un VCF) :
    python3 app_pharmageno_v8j.py --bundle ~/pypgx-bundle --pgx-python ~/pgxenv/bin/python
puis ouvrir http://127.0.0.1:5000 . Le bouton « profil de démonstration » fonctionne sans VCF ni PyPGx.
Par défaut, les données sont lues dans ../data et le DL dans ../modeles_v8f et le second avis XGBoost dans ../results/resultats_final_v8 (arborescence du dossier Model_v8_7_9_10) ;
--donnees, --modeles, --modeles-choix (défaut ../modeles_v8i) et --modeles-xgb permettent d'indiquer d'autres dossiers.

Données du patient : le VCF téléversé et les fichiers intermédiaires sont supprimés dès la fin de l'analyse ; seul le profil (valeurs par gène) reste dans
<travail>/jobs/<id>.json jusqu'au clic sur « Supprimer mes données » ; les tâches de plus de 24 h sont supprimées automatiquement. Le serveur n'écoute que
sur 127.0.0.1.
"""
import argparse, json, os, re, shutil, sys, threading, time, traceback, uuid
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from moteur_v8i import MoteurPGxChoix
from recommandation_v8 import Recommandeur, ORDRE_PROPOSITION, LIBELLE_PRO, TEXTE_PATIENT, AVERTISSEMENT_GENERAL
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
                       ('DL film, identifiant de médicament, EVITER x2 (5 graines) : ancien DL', '0,9980 ± 0,0010', '0,0029 ± 0,0010'),
                       ('DL profil -> médicaments, profil seul en entrée (5 graines) : DL de l\'application v8f', '0,9985 ± 0,0002', '0,0015 ± 0,0002')],
    choix=[('DL « choix du médicament » (5 graines × 5 plis)', '99,55 % ± 0,06', '0,998 ± 0,0004', '0 cas'), ('Référence sans le profil (même réponse pour tous)', '6,9 %', '0,599', '0 cas')],
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
    app = Flask(__name__, template_folder=os.path.join(ICI, 'templates_v8j'))
    app.config['MAX_CONTENT_LENGTH'] = cfg.taille_max_mo * 1024 * 1024
    D = os.path.abspath(cfg.donnees)
    chemin = lambda f: os.path.join(D, f)
    mo = MoteurPGxChoix(cfg.modeles, getattr(cfg, 'modeles_choix', os.path.join(os.path.dirname(os.path.abspath(cfg.modeles)), 'modeles_v8i')), chemin('domaine_v8.json'), chemin('regles_v7_monogene.csv'), chemin('regles_v2_corrigees_multigene_v7.csv'), dossier_xgb=getattr(cfg, 'modeles_xgb', None))
    rc = Recommandeur(chemin('atc_mapping_medicaments_v1.csv'), chemin('specialite_atc_v1.csv'), chemin('alternatives_atc4_v1.csv'), sorted(mo.dom))
    travail = os.path.abspath(cfg.travail); os.makedirs(os.path.join(travail, 'jobs'), exist_ok=True)
    pool = ThreadPoolExecutor(max_workers=1)   # PyPGx est lourd : une analyse à la fois, les autres attendent
    verrou = threading.Lock()
    nb_par_spec = {s: len(rc.medicaments_de_specialite(s)) for s in rc.specialites()}
    n_dans_modele = sum(1 for v in mo.dom.values() if v['dans_modele'])

    def classes_liste(): return [(code, c['nom'], len(c['medicaments'])) for code, c in sorted(mo.classes_choix.items())]

    def spec_de_classe(code):
        """spécialité d'affichage rattachée à la classe (celle qui contient le plus de médicaments de la classe) : sert aux encadrés « spécialité », pas au choix du DL"""
        ms = set(mo.classes_choix[code]['medicaments']); meilleur, nb = None, 0
        for s in rc.specialites():
            n = len(ms & set(rc.medicaments_de_specialite(s)))
            if n > nb: meilleur, nb = s, n
        return meilleur or next(s for s in rc.specialites() if nb_par_spec[s] > 0)
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

    def recommander_dl(res, spec, profil):
        """v8h : médicaments proposés pour la spécialité = classement du DL. À action égale (STANDARD, SURVEILLER, ADAPTER_DOSE), ceux dont un gène requis du patient n'a pas la valeur normale
        passent d'abord (le profil du patient intervient), puis la probabilité du DL. Règle de classement d'affichage : le DL fournit les probabilités, il n'y a pas d'étiquette « le » médicament à prescrire."""
        reco = rc.recommander(res, spec, max_proposes=100000)
        def intervient(f):
            for e in (f.get('explication') or []):
                g = e.get('gene'); v = profil.get(g)
                if v is not None and float(v) != (0.0 if str(g).startswith('HLA-') else 1.0): return 1
            return 0
        prop = reco['proposes']
        for f in prop: f['gene_intervient'] = intervient(f)
        prop.sort(key=lambda f: (ORDRE_PROPOSITION[f['action']], -f['gene_intervient'], -(f['proba_dl'] or {}).get(f['action'], 0)))
        for i, f in enumerate(prop, 1): f['rang'] = i
        reco['autres_compatibles'] = max(0, len(prop) - 3); reco['proposes'] = prop[:3]
        reco['note_ordre'] = "Classement : à action égale, les médicaments dont un gène du patient intervient passent d'abord, puis la probabilité du DL. C'est une règle d'affichage, pas une validation clinique."
        return reco

    def construire_choix(j, classe, res):
        """v8i : le DL choisit dans la classe ; la couche de sécurité retire tout médicament signalé « à éviter » par un autre avis ; fiches complètes pour l'affichage."""
        ch = mo.choix(j['profil'], classe, res); par = {r['medicament']: r for r in res}; cat = {r['medicament']: rc.classer(r, par) for r in res}
        tg = table_genes(j); lect = {g['gene']: (g['lecture'] if g['lecture'] != '-' else 'valeur %s' % g['valeur_txt']) for g in tg}
        fiches, retires, ecartes = [], [], []
        for d in ch['candidats']:
            m = d['medicament']
            if d['dans_ensemble']:
                if cat[m] == 'a_eviter': retires.append(dict(medicament=m, proba_choix=d['proba_choix'])); continue
                f = rc.chercher_medicament(m, res); _vocab(f); f['proba_choix'] = d['proba_choix']; f['rang'] = len(fiches) + 1
                f['genes_decisifs'] = mo.genes_decisifs(j['profil'], m)
                ex = {e['gene']: e['lecture'] for e in (f.get('explication') or []) if isinstance(e, dict) and 'gene' in e and e.get('lecture')}
                for dd in f['genes_decisifs']: dd['lectures'] = [(g, ex.get(g) or lect.get(g, '-')) for g in dd['genes']]
                fiches.append(f)
            else:
                ecartes.append(dict(medicament=m, proba_choix=d['proba_choix'], action=par[m].get('action_dl'), a_eviter=(cat[m] == 'a_eviter')))
        dec = mo.genes_decisifs_choix(j['profil'], classe, res)
        for d in dec: d['lecture'] = lect.get(d['gene'], '-')
        return dict(code=classe, nom=ch['nom'], fiches=fiches, retires=retires, ecartes=ecartes, non_evalues=ch['non_evalues'], decisifs=dec, motif=ch.get('motif'))

    def calculer(j, spec, q):
        res = mo.predire(j['profil'])
        par = {r['medicament']: r for r in res}
        reco = recommander_dl(res, spec, j['profil'])
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
        "Le DL « choix du médicament » apprend une cible fixée par CONVENTION : pour un profil, les médicaments de la classe que CPIC/DPWG classent le mieux (standard, sinon surveiller, sinon adapter la dose), jamais « à éviter ». "
        "Aucune guideline ne dit lequel de ces médicaments est le meilleur : le DL ne les départage pas (probabilités quasi égales). La réponse clinique réelle des patients n'est pas mesurée.",
        "Le choix n'est possible que pour les 30 classes thérapeutiques (OMS, ATC niveau 4) qui contiennent au moins 2 médicaments du modèle (75 médicaments sur 113) ; seuls environ 6,5 % des cas (profil, classe) des données ont une réponse qui dépend du profil.",
        "Outil de recherche (mémoire de master), non validé cliniquement : il ne remplace ni un médecin, ni un pharmacien, ni une prescription.",
        "Les étiquettes d'entraînement viennent d'un moteur de règles CPIC/DPWG ; les entrées du réseau sont des phénotypes déjà calculés. Le modèle reproduit donc en grande partie "
        "ces règles : sa fiabilité mesurée est celle d'un accord avec les règles, pas une exactitude clinique.",
        "Seuls les gènes et médicaments listés sont couverts ; les autres médicaments, les interactions, les maladies, l'âge et les doses ne sont pas pris en compte.",
        "CYP2D6 et les allèles HLA ne se lisent pas dans un VCF de variants ponctuels ; sans saisie, les médicaments concernés sont « non évalués ».",
        "Un médicament absent de l'entraînement n'a pas de sortie dans le DL « profil -> médicaments » : l'application affiche « non évalué » (mesure faite avec l'ancien DL à identifiant de médicament : F1 macro 0,467, 63 à 70 % des cas à éviter manqués selon le modèle).",
        "Pas de test sur des patients réels : les tests de l'application portent sur des profils du corpus d'entraînement, qui vérifient la logique, pas la performance.",
    ]
    METHODE = ("Méthode : réseau de neurones « profil génétique -> médicaments » (le profil est la seule entrée, un conseil par médicament en sortie) = moteur de la recommandation ; XGBoost (ancien modèle) = second avis ; règle CPIC/DPWG "
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

    def choisir_classe(j):
        c = request.args.get('classe', j.get('classe'))
        if c in mo.classes_choix: return c
        return j.get('classe') if j.get('classe') in mo.classes_choix else sorted(mo.classes_choix)[0]

    def choisir_spec(j): return spec_de_classe(choisir_classe(j))

    @app.route('/')
    def index():
        return render_template('index.html', classes=classes_liste(), specialites=specialites_liste(), erreur=request.args.get('erreur'), taille_max=cfg.taille_max_mo, hla=HLA, hla_meds=hla_meds,
                               demo_ok=profil_demo is not None, demo_echantillon=DEMO_ECHANTILLON)

    @app.route('/apropos')
    def apropos():
        return render_template('apropos.html', limites=LIMITES, methode=METHODE, perf=PERFORMANCES, n_med=len(mo.dom), n_modele=n_dans_modele, n_genes=len(mo.genes_modele),
                               genes=mo.genes_modele, seuil=mo.seuil, niveau='%g %%' % (100 * float(mo.niveau_abstention)))

    @app.route('/analyser', methods=['POST'])
    def analyser():
        classe = request.form.get('classe', '')
        if classe not in mo.classes_choix:
            return redirect(url_for('index', erreur="Choisissez l'indication (classe de médicaments) dans la liste."))
        spec = spec_de_classe(classe)
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
        j = nouveau('vcf', spec, os.path.basename(f.filename)); j['classe'] = classe; ecrire(j)
        dossier = os.path.join(travail, j['id']); os.makedirs(dossier, exist_ok=True)
        chemin_vcf = os.path.join(dossier, 'patient.vcf.gz' if f.filename.lower().endswith('.gz') else 'patient.vcf'); f.save(chemin_vcf)
        pool.submit(travailler, j['id'], chemin_vcf, request.form.get('echantillon', '').strip(), cyp, ','.join(hla_parts))
        return redirect(url_for('progression', jid=j['id']))

    @app.route('/demo', methods=['POST'])
    def demo():
        classe = request.form.get('classe', '')
        if classe not in mo.classes_choix:
            return redirect(url_for('index', erreur="Choisissez l'indication (classe de médicaments) dans la liste."))
        spec = spec_de_classe(classe)
        if profil_demo is None:
            return redirect(url_for('index', erreur='Profil de démonstration indisponible (profils_genes_v4.csv introuvable dans le dossier des données).'))
        j = nouveau('demo', spec, 'profil de démonstration'); j['classe'] = classe
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
        spec = choisir_spec(j); classe = choisir_classe(j); q = request.args.get('q', '').strip()
        res, reco, fiche, resume, manq, bloquants, globaux, cat = calculer(j, spec, q)
        choix = construire_choix(j, choisir_classe(j), res); reco['proposes'] = choix['fiches']
        tg = table_genes(j); lect = {g['gene']: (g['lecture'] if g['lecture'] != '-' else 'valeur %s' % g['valeur_txt']) for g in tg}
        for f in list(globaux):
            f['genes_decisifs'] = mo.genes_decisifs(j['profil'], f['medicament'])
            ex = {e['gene']: e['lecture'] for e in (f.get('explication') or []) if isinstance(e, dict) and 'gene' in e and e.get('lecture')}
            for d in f['genes_decisifs']: d['lectures'] = [(g, ex.get(g) or lect.get(g, '-')) for g in d['genes']]
        sortie = mo.sortie_complete(j['profil'])
        masques = sum(1 for r in res if r['statut'] in ('non_determine_gene', 'hors_domaine'))
        apercu = dict(genes=tg, n_variables=len(mo.features), n_lus=sum(1 for g in tg if g['valeur'] is not None), n_med=sortie['n_medicaments'], comptes=sortie['comptes'], masques=masques)
        tous = []
        for r in sorted(res, key=lambda x: x['medicament']):
            tous.append(dict(medicament=r['medicament'], categorie=CATEGORIE_LIBELLE[cat[r['medicament']]], cat=cat[r['medicament']], dl=r.get('action_dl'), xgb=r.get('action_xgboost'),
                             cpic=r.get('action_cpic'), alertes=[a for a in r.get('alertes', [])], message=r.get('message') or ''))
        return render_template('resultats.html', j=j, spec=spec, specialites=specialites_liste(), classe=classe, classes=classes_liste(), choix=choix, reco=reco, fiche=fiche, q=q, genes=table_genes(j), resume=resume, bloquants=bloquants,
                               hla=HLA, hla_meds=hla_meds, hla_absents=[a for a in HLA if j['profil'].get(a) is None], cyp_absent=j['profil'].get('CYP2D6') is None,
                               erreur=request.args.get('erreur'), apercu=apercu,
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
        return redirect(url_for('resultats', jid=jid, classe=request.form.get('classe') or j.get('classe')))

    @app.route('/patient/<jid>')
    def patient(jid):
        j = charger(jid)
        if j['etat'] != 'termine': return redirect(url_for('progression', jid=jid))
        spec = choisir_spec(j)
        res, reco, fiche, resume, manq, bloquants, globaux, cat = calculer(j, spec, '')
        choix = construire_choix(j, choisir_classe(j), res); reco['proposes'] = choix['fiches']
        return render_template('patient.html', j=j, spec=spec, reco=reco, globaux=globaux, bloquants=bloquants, avertissement=AVERTISSEMENT_GENERAL, court=ACTION_COURT,
                               texte_non_evalue=TEXTE_PATIENT['NON_EVALUE'])

    @app.route('/pdf/<jid>')
    def pdf(jid):
        j = charger(jid)
        if j['etat'] != 'termine': abort(404)
        spec = choisir_spec(j)
        res, reco, fiche, resume, manq, bloquants, globaux, cat = calculer(j, spec, request.args.get('q', '').strip())
        choix = construire_choix(j, choisir_classe(j), res); reco['proposes'] = choix['fiches']
        buf = construire_pdf(j, reco, table_genes(j), fiche, resume, AVERTISSEMENT_GENERAL, globaux, bloquants, LIMITES, METHODE)
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name='rapport_pharmageno_v8j_%s.pdf' % jid)

    @app.route('/json/<jid>')
    def json_fiche(jid):
        """fiche complète (profil, lecture du VCF, sortie brute du moteur, recommandation) : transparence et reproductibilité"""
        j = charger(jid)
        if j['etat'] != 'termine': abort(404)
        spec = choisir_spec(j)
        res, reco, fiche, resume, manq, bloquants, globaux, cat = calculer(j, spec, '')
        choix = construire_choix(j, choisir_classe(j), res); reco['proposes'] = choix['fiches']
        out = dict(id=jid, mode=j['mode'], assemblage=j.get('assemblage'), specialite=spec, classe=choisir_classe(j), profil=j['profil'], lecture_vcf=j['detail'], resume=resume, bloquants=bloquants,
                   a_eviter_toutes_specialites=[f['medicament'] for f in globaux], recommandation=reco, choix=choix, moteur=res)
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
    ap.add_argument('--donnees', default=os.path.join(racine, 'data')); ap.add_argument('--modeles', default=os.path.join(racine, 'modeles_v8f')); ap.add_argument('--modeles-xgb', default=os.path.join(racine, 'results', 'resultats_final_v8'), dest='modeles_xgb')
    ap.add_argument('--modeles-choix', default=os.path.join(racine, 'modeles_v8i'), dest='modeles_choix'); ap.add_argument('--codage', default=None); ap.add_argument('--tables', default=None)
    ap.add_argument('--bundle', default=os.path.expanduser('~/pypgx-bundle')); ap.add_argument('--travail', default='pharmageno_travail')
    ap.add_argument('--pgx-python', default=(os.path.expanduser('~/pgxenv/bin/python') if os.path.exists(os.path.expanduser('~/pgxenv/bin/python')) else sys.executable), dest='pgx_python', help="interpréteur Python de l'environnement PyPGx (ex. ~/pgxenv/bin/python)")
    ap.add_argument('--port', type=int, default=5000); ap.add_argument('--taille-max-mo', type=int, default=500, dest='taille_max_mo')
    cfg = ap.parse_args(); cfg.pgx_python = os.path.expanduser(cfg.pgx_python); cfg.bundle = os.path.expanduser(cfg.bundle)
    app = creer_app(cfg)
    app.run(host='127.0.0.1', port=cfg.port, debug=False, threaded=True)


if __name__ == '__main__':
    main()
