"""
app_v4.py — Application Flask PharmaGeno

Remplace app_v3.py. Aucun fichier existant n est modifie.

CORRECTIONS PAR RAPPORT A app_v3.py
------------------------------------

1. cpic_by_gene RENOMME
   Cette variable contenait une synthese produite par le modele, sous un nom qui
   revendiquait une provenance CPIC. Elle devient resume_modele. L ancien nom reste
   transmis au template pour ne pas casser results.html, mais le code ne l emploie plus.

2. PLUS AUCUN NOMBRE DE MEDICAMENTS CODE EN DUR
   app_v3 affichait « 531 medicaments », nombre qui n existe dans aucun fichier du
   projet. Toute mention passe par nb_medicaments().

3. SORTIE PRINCIPALE = RESEAU PROFOND, XGBoost EN COMPARATEUR
   L ensemble non valide (2*DL + 1*RF)/3 est supprime. L application affiche la
   prediction du reseau — objet du memoire — et, a cote, celle de XGBoost avec les
   taux d erreur mesures des deux modeles.

4. PROVENANCE AFFICHEE
   Chaque sortie est marquee comme prediction du modele, distincte d une recommandation
   de reference. Les libelles cliniques sont conserves.

ACQUIS DE app_v3, CONSERVES
---------------------------
   - Suppression de la regle ecrite a la main qui remplacait la sortie du modele.
   - Profil genetique complet a chaque inference.
   - Tous les medicaments du referentiel sont interrogeables.
"""

import os
import sys

from flask import Flask, render_template, request, redirect, url_for, send_file

sys.path.insert(0, '/home/mouna/projet_memoire/scripts')

from vcf_parser import parse_vcf
from drug_recommender import (load_pharmgkb, load_clinical_variants,
                              load_guidelines, get_recommendations)
from generate_report import generate_pdf_report

from predict_v4 import (
    load_models, predict_for_patient, predict_drug_for_patient,
    resume_modele_par_gene, nb_medicaments, poids_attention,
    ACTION_ICONS, ACTION_LABELS, ACTION_COLORS, ACTION_DETAIL,
    CER_MESURE, F1_MESURE, VERSION,
)

app = Flask(__name__)

UPLOAD_FOLDER = '/home/mouna/projet_memoire/app/uploads'
PHARMGKB_FILE = '/home/mouna/projet_memoire/data/var_drug_ann.tsv'
CLINICAL_FILE = '/home/mouna/projet_memoire/data/clinicalVariants.tsv'
JSON_DIR      = '/home/mouna/projet_memoire/data'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
load_models()

DRUG_NORMALIZE = {
    'warfarine': 'warfarin', 'aspirine': 'aspirin', 'methadone': 'methadone',
    'fluorouracile': 'fluorouracil', 'capecitabine': 'capecitabine',
    'tamoxifene': 'tamoxifen', 'codeine': 'codeine', 'omeprazole': 'omeprazole',
    'clopidogrel': 'clopidogrel', 'simvastatine': 'simvastatin',
    'atorvastatine': 'atorvastatin', 'azathioprine': 'azathioprine',
    'phenytoine': 'phenytoin', 'carbamazepine': 'carbamazepine',
}

AVERTISSEMENT = (
    "Prototype expérimental de recherche. Les sorties affichées sont des prédictions "
    "d'un modèle d'apprentissage, non des recommandations cliniques ni des "
    "contre-indications au sens réglementaire. Elles ne remplacent pas l'avis d'un "
    "professionnel de santé ni les recommandations de référence (CPIC, DPWG).")

PERFORMANCE = {
    'protocole': "Validation croisée groupée par individu, 5 plis, aucun recouvrement "
                 "patient entre apprentissage et test.",
    'modeles': [
        {'nom': 'Réseau profond', 'role': 'sortie principale',
         'f1': F1_MESURE['DL'], 'cer': CER_MESURE['DL']},
        {'nom': 'XGBoost', 'role': 'comparateur',
         'f1': F1_MESURE['XGBoost'], 'cer': CER_MESURE['XGBoost']},
    ],
    'note_cer': "Le taux d'erreur critique est la proportion de contre-indications "
                "non détectées par le modèle.",
}


# ---------------------------------------------------------------------------
def charger_contexte(filepath):
    """Analyse le VCF et charge les annotations de reference."""
    variants_df = parse_vcf(filepath)
    if len(variants_df) == 0:
        return variants_df, None, []

    results_df = get_recommendations(variants_df,
                                     load_pharmgkb(PHARMGKB_FILE),
                                     load_clinical_variants(CLINICAL_FILE),
                                     load_guidelines(JSON_DIR))
    results_df = (results_df
                  .drop_duplicates(subset=['gene', 'rsid', 'drug', 'phenotype'])
                  .sort_values(['gene', 'drug']))
    drugs_list = sorted(results_df[results_df['drug'] != 'Aucune recommandation trouvee']
                        ['drug'].unique().tolist())
    return variants_df, results_df, drugs_list


def analyser_patient(variants_df, results_df):
    """Predictions du modele et synthese par gene."""
    variants_list = variants_df.to_dict('records')

    documentes = []
    if results_df is not None and len(results_df) > 0:
        documentes = (results_df[results_df['drug'] != 'Aucune recommandation trouvee']
                      ['drug'].unique().tolist())

    predictions, mutes, gene_vector = predict_for_patient(variants_list,
                                                          extra_drugs=documentes)
    resume = resume_modele_par_gene(predictions, gene_vector, mutes)
    return predictions, resume, gene_vector, mutes


def rendu(**kwargs):
    """Rend results.html avec le contexte commun.

    resume_modele est transmis aussi sous l ancien nom cpic_by_gene pour que le
    template existant continue de fonctionner. Le nom a conserver est resume_modele.
    """
    resume = kwargs.pop('resume_modele', {})
    return render_template('results.html',
                           resume_modele=resume,
                           cpic_by_gene=resume,
                           version_modele=VERSION,
                           n_medicaments=nb_medicaments(),
                           performance=PERFORMANCE,
                           avertissement=AVERTISSEMENT,
                           **kwargs)


# ---------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', n_medicaments=nb_medicaments())


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'vcf_file' not in request.files:
        return redirect(url_for('index'))
    fichier = request.files['vcf_file']
    if fichier.filename == '':
        return redirect(url_for('index'))

    filepath = os.path.join(UPLOAD_FOLDER, fichier.filename)
    fichier.save(filepath)

    variants_df, results_df, drugs_list = charger_contexte(filepath)

    if len(variants_df) == 0:
        return rendu(filename=fichier.filename, variants=[], results=[],
                     predictions=[], drugs_list=[], n_variants=0, n_results=0,
                     drug_search=None, drug_result=None, resume_modele={},
                     covered_drugs=[], no_mutation=True)

    predictions, resume, _, _ = analyser_patient(variants_df, results_df)

    return rendu(filename=fichier.filename,
                 variants=variants_df.to_dict('records'),
                 results=results_df.to_dict('records'),
                 predictions=predictions, drugs_list=drugs_list,
                 n_variants=len(variants_df), n_results=len(results_df),
                 drug_search=None, drug_result=None,
                 resume_modele=resume, covered_drugs=[])


@app.route('/search_drug', methods=['POST'])
def search_drug():
    saisie = request.form.get('drug_query', '').lower().strip()
    drug_query = DRUG_NORMALIZE.get(saisie, saisie)
    vcf_filename = request.form.get('vcf_filename', '')

    variants_df, results_df, drugs_list = charger_contexte(
        os.path.join(UPLOAD_FOLDER, vcf_filename))
    predictions, resume, gene_vector, mutes = analyser_patient(variants_df, results_df)

    fiche = predict_drug_for_patient(gene_vector, drug_query, mutes)

    if fiche.get('known_drug'):
        action = fiche['action']
        details = []

        if not fiche['association_documentee']:
            details.append(
                "Aucune association documentée entre ce médicament et les gènes "
                "atypiques de ce patient dans les référentiels. La prédiction repose "
                "sur le profil génétique global et la structure de la molécule.")
        if fiche['appel_specialise']:
            details.append(
                "Le gène impliqué requiert un appel spécialisé ; son encodage à "
                "partir du VCF est approximatif.")
        if not fiche['accord_dl_xgboost']:
            details.append(
                f"XGBoost, dont le taux d'erreur critique mesuré est inférieur "
                f"({CER_MESURE['XGBoost']} % contre {CER_MESURE['DL']} %), prédit "
                f"« {fiche['label_xgboost']} » pour ce couple.")

        drug_result = {
            'status':           ACTION_COLORS.get(action, 'secondary'),
            'message':          f"{ACTION_ICONS.get(action, '')} {drug_query.upper()} — "
                                f"{ACTION_LABELS.get(action, action)}",
            'action':           action,
            'detail':           ACTION_DETAIL.get(action, ''),
            'confidence':       fiche['confidence'],
            'provenance':       'Prédiction du réseau profond',
            'responsible_gene': fiche['responsible_gene'],
            'comparateur':      {'nom': 'XGBoost',
                                 'label': fiche['label_xgboost'],
                                 'confiance': fiche['confiance_xgboost'],
                                 'accord': fiche['accord_dl_xgboost']},
            'ml_predictions':   [fiche],
            'details':          details,
        }
    else:
        drug_result = {
            'status':  'info',
            'message': f"{drug_query.upper()} — médicament hors référentiel moléculaire",
            'action':  None,
            'detail':  (f"Cette molécule ne figure pas parmi les {nb_medicaments()} "
                        f"médicaments du référentiel. Aucune prédiction n'est produite, "
                        f"plutôt qu'une prédiction non fondée."),
            'provenance': None, 'ml_predictions': [], 'details': [],
        }

    return rendu(filename=vcf_filename,
                 variants=variants_df.to_dict('records'),
                 results=results_df.to_dict('records'),
                 predictions=predictions, drugs_list=drugs_list,
                 n_variants=len(variants_df), n_results=len(results_df),
                 drug_search=drug_query, drug_result=drug_result,
                 resume_modele=resume, covered_drugs=[])


@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    vcf_filename = request.form.get('vcf_filename', '')
    drug_search = request.form.get('drug_search', '')

    variants_df, results_df, _ = charger_contexte(
        os.path.join(UPLOAD_FOLDER, vcf_filename))
    predictions, _, gene_vector, mutes = analyser_patient(variants_df, results_df)

    drug_result = None
    if drug_search:
        fiche = predict_drug_for_patient(gene_vector, drug_search, mutes)
        if fiche.get('known_drug'):
            drug_result = {
                'message': f"{ACTION_ICONS.get(fiche['action'], '')} {drug_search} — "
                           f"{ACTION_LABELS.get(fiche['action'], fiche['action'])}",
                'action':  fiche['action'],
                'detail':  ACTION_DETAIL.get(fiche['action'], ''),
                'provenance': 'Prédiction du réseau profond',
                'comparateur': f"XGBoost : {fiche['label_xgboost']}",
            }
        else:
            drug_result = {
                'message': f"{drug_search} — hors référentiel moléculaire",
                'action':  None,
                'detail':  "Aucune prédiction produite pour cette molécule.",
            }

    pdf_buffer = generate_pdf_report(
        vcf_filename, variants_df.to_dict('records'), predictions,
        results_df.to_dict('records'), drug_search, drug_result)

    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True,
                     download_name=f'rapport_pharmageno_{vcf_filename}.pdf')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
