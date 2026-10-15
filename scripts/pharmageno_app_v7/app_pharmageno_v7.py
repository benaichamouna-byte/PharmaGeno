#!/usr/bin/env python3
"""
app_pharmageno_v7.py : application web PharmaGeno (Flask). Remplace l'ancienne app.py (qui n'est pas modifiée).

Chaîne : VCF -> vcf_to_profile.lire_vcf (PyPGx) -> profil à 12 gènes -> moteur_v7.MoteurPGx (DL FiLM + XGBoost second avis + couche de sécurité)
         -> recommandation_v7.Recommandeur (spécialité, à éviter, alternatives, texte patient) -> page de résultats / PDF.

Lancement (depuis le dossier des scripts, environnement avec flask, reportlab, pypgx==0.27.0, pysam, torch, xgboost) :
    python3 app_pharmageno_v7.py --modeles resultats_final_v7 --bundle ~/pypgx-bundle
puis ouvrir http://localhost:5000 . Le bouton « profil de démonstration » fonctionne sans VCF ni PyPGx.

Données du patient : le VCF téléversé et les fichiers intermédiaires sont supprimés dès la fin de l'analyse ; seul le profil (12 valeurs) reste dans
<travail>/jobs/<id>.json tant que l'utilisateur ne clique pas sur « Supprimer mes données ».
"""
import argparse, json, os, re, shutil, sys, threading, time, traceback, uuid
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from moteur_v7 import MoteurPGx
from recommandation_v7 import Recommandeur, LIBELLE_VALEUR, LIBELLE_PRO, AVERTISSEMENT_GENERAL
from vcf_to_profile import lire_vcf, VCFRefuse, PyPGxIndisponible
from rapport_pdf_v7 import construire_pdf

# Profil réel du corpus d'entraînement (HG01148, 1000 Genomes) : sert UNIQUEMENT à montrer l'interface. Le modèle a pu le voir à l'entraînement.
PROFIL_DEMO = dict(ABCG2=0.5, CYP2B6=0.5, CYP2C19=0.5, CYP2C9=0.5, CYP2D6=0.5, CYP3A5=0.0, DPYD=1.0, F5=1.0, NUDT15=0.5, SLCO1B1=1.0, TPMT=0.5, UGT1A1=0.0)
CYP2D6_CHOIX = {'': None, '0': 0.0, '0.5': 0.5, '1': 1.0, '2': 2.0}   # valeurs présentes dans le corpus pour CYP2D6 (pas de 1,5)


def creer_app(cfg):
    app = Flask(__name__, template_folder=os.path.join(ICI, 'templates_v7'))
    app.config['MAX_CONTENT_LENGTH'] = cfg.taille_max_mo * 1024 * 1024
    mo = MoteurPGx(cfg.modeles, cfg.domaine)
    dom = json.load(open(cfg.domaine, encoding='utf-8'))['medicaments']
    rc = Recommandeur(cfg.atc, cfg.specialites, cfg.alternatives, mo.meds)
    travail = os.path.abspath(cfg.travail); os.makedirs(os.path.join(travail, 'jobs'), exist_ok=True)
    pool = ThreadPoolExecutor(max_workers=1)   # PyPGx est lourd : une analyse à la fois, les autres attendent
    verrou = threading.Lock()
    nb_par_spec = {s: len(rc.medicaments_de_specialite(s)) for s in rc.specialites()}

    def f_job(jid): return os.path.join(travail, 'jobs', jid + '.json')

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
        j = dict(id=uuid.uuid4().hex[:12], mode=mode, specialite=specialite, nom_fichier=nom_fichier, etat='en_cours', pct=0, message='En attente', cree=time.time())
        ecrire(j); return j

    def surcharge_cyp2d6(j, val):
        """Valeur CYP2D6 fournie par l'utilisateur (test externe) : tracée comme telle."""
        j['profil']['CYP2D6'] = val
        j['detail']['CYP2D6'] = dict(valeur=val, phenotype='fourni par l\'utilisateur', diplotype=None, statut='fourni',
                                      motif='Valeur saisie par l\'utilisateur (test CYP2D6 externe) : non vérifiée par l\'application.')

    def travailler(jid, chemin, echantillon, cyp2d6):
        dossier = os.path.join(travail, jid)
        try:
            r = lire_vcf(chemin, cfg.bundle, os.path.join(dossier, 'pypgx'), cfg.codage, echantillon=echantillon or None, verbose=False,
                         progres=lambda p, m: maj(jid, pct=p, message=m), pgx_python=cfg.pgx_python)
            j = charger(jid); j.update(profil=r['profil'], detail=r['detail'], assemblage=r['assemblage'])
            if cyp2d6 is not None: surcharge_cyp2d6(j, cyp2d6)
            j.update(etat='termine', pct=100, message='Analyse terminée'); ecrire(j)
        except VCFRefuse as e:
            maj(jid, etat='refuse', message=str(e))
        except PyPGxIndisponible as e:
            maj(jid, etat='erreur', message="L'analyse n'a pas pu être faite : " + str(e))
        except Exception as e:
            traceback.print_exc(); maj(jid, etat='erreur', message='Erreur inattendue : %s' % str(e)[:300])
        finally:
            shutil.rmtree(dossier, ignore_errors=True)   # le VCF du patient n'est pas conservé

    def table_genes(j):
        out = []
        for g in mo.genes:
            d = j['detail'].get(g, {}); v = j['profil'].get(g)
            out.append(dict(gene=g, valeur=v, lecture=LIBELLE_VALEUR.get(v, 'non déterminé'), phenotype=d.get('phenotype'), diplotype=d.get('diplotype'),
                            motif=d.get('motif'), statut=d.get('statut', 'non_determine')))
        return out

    def calculer(j, spec, q):
        res = mo.predire(j['profil'])
        reco = rc.recommander(res, spec, j['profil'], dom, j['detail'])
        fiche = rc.chercher_medicament(q, res, j['profil'], dom, j['detail']) if q else None
        nd = [x for x in res if x['statut'] == 'non_determine_gene']; manq = {}
        for x in nd:
            for g in x['genes_manquants']: manq[g] = manq.get(g, 0) + 1
        compte = {}
        for x in res: compte[x['statut']] = compte.get(x['statut'], 0) + 1
        resume = ("%d médicaments sur %d ont pu être évalués pour ce profil ; %d n'ont pas pu l'être faute d'un gène déterminé%s ; %d correspondent à une combinaison génétique "
                  "que le modèle n'a jamais rencontrée (aucune prédiction donnée)." % (
                      compte.get('ok', 0) + compte.get('desaccord', 0), len(res), compte.get('non_determine_gene', 0),
                      (' (' + ', '.join('%s : %d' % (g, n) for g, n in sorted(manq.items())) + ')') if manq else '', compte.get('hors_domaine', 0)))
        return res, reco, fiche, resume, manq, compte

    @app.route('/')
    def index():
        return render_template('index.html', specialites=[(s, nb_par_spec[s]) for s in rc.specialites()], erreur=request.args.get('erreur'),
                               taille_max=cfg.taille_max_mo)

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
        cyp = CYP2D6_CHOIX.get(request.form.get('cyp2d6', ''), None)
        j = nouveau('vcf', spec, os.path.basename(f.filename))
        dossier = os.path.join(travail, j['id']); os.makedirs(dossier, exist_ok=True)
        chemin = os.path.join(dossier, 'patient.vcf.gz' if f.filename.lower().endswith('.gz') else 'patient.vcf'); f.save(chemin)
        pool.submit(travailler, j['id'], chemin, request.form.get('echantillon', '').strip(), cyp)
        return redirect(url_for('progression', jid=j['id']))

    @app.route('/demo', methods=['POST'])
    def demo():
        spec = request.form.get('specialite', '')
        if spec not in rc.classes or nb_par_spec.get(spec, 0) == 0:
            return redirect(url_for('index', erreur='Choisissez une spécialité couverte par le modèle.'))
        j = nouveau('demo', spec, 'profil de démonstration')
        j.update(profil=dict(PROFIL_DEMO), assemblage=None, etat='termine', pct=100, message='Profil de démonstration',
                 detail={g: dict(valeur=v, phenotype=None, diplotype=None, statut='demo', motif=None) for g, v in PROFIL_DEMO.items()})
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
        spec = request.args.get('specialite', j['specialite'])
        if spec not in rc.classes: spec = j['specialite']
        q = request.args.get('q', '').strip()
        res, reco, fiche, resume, manq, compte = calculer(j, spec, q)
        tous = sorted(res, key=lambda x: x['medicament'])
        return render_template('resultats.html', j=j, spec=spec, specialites=[(s, nb_par_spec[s]) for s in rc.specialites()], reco=reco, fiche=fiche, q=q,
                               genes=table_genes(j), resume=resume, manq=manq, compte=compte, tous=tous, libelle_pro=LIBELLE_PRO, noms=sorted(rc.meds),
                               avertissement=AVERTISSEMENT_GENERAL)

    @app.route('/pdf/<jid>')
    def pdf(jid):
        j = charger(jid)
        if j['etat'] != 'termine': abort(404)
        spec = request.args.get('specialite', j['specialite'])
        if spec not in rc.classes: spec = j['specialite']
        res, reco, fiche, resume, manq, compte = calculer(j, spec, request.args.get('q', '').strip())
        buf = construire_pdf(j, reco, table_genes(j), fiche, resume, AVERTISSEMENT_GENERAL)
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name='rapport_pharmageno_%s.pdf' % jid)

    @app.route('/supprimer/<jid>', methods=['POST'])
    def supprimer(jid):
        charger(jid)
        for p in (f_job(jid),):
            if os.path.exists(p): os.remove(p)
        shutil.rmtree(os.path.join(travail, jid), ignore_errors=True)
        return redirect(url_for('index', erreur='Vos données ont été supprimées.'))

    return app


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--modeles', default='resultats_final_v7'); ap.add_argument('--domaine', default='domaine_v7.json')
    ap.add_argument('--atc', default='atc_mapping_medicaments_v1.csv'); ap.add_argument('--specialites', default='specialite_atc_v1.csv')
    ap.add_argument('--alternatives', default='alternatives_atc4_v1.csv'); ap.add_argument('--codage', default='codage_pypgx_valeur_v7.csv')
    ap.add_argument('--bundle', default=os.path.expanduser('~/pypgx-bundle')); ap.add_argument('--travail', default='pharmageno_travail')
    ap.add_argument('--pgx-python', default=sys.executable, dest='pgx_python', help="interpréteur Python de l'environnement PyPGx (ex. ~/pgxenv/bin/python)"); ap.add_argument('--port', type=int, default=5000); ap.add_argument('--taille-max-mo', type=int, default=500, dest='taille_max_mo')
    cfg = ap.parse_args(); cfg.pgx_python = os.path.expanduser(cfg.pgx_python)
    app = creer_app(cfg)
    app.run(host='127.0.0.1', port=cfg.port, debug=False, threaded=True)


if __name__ == '__main__':
    main()
