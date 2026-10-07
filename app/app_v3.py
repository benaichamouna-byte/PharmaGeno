"""
app_v3.py — Application Flask PharmaGeno

Remplace app.py. Aucun fichier existant n est modifie.

TROIS CORRECTIONS PAR RAPPORT A app.py
---------------------------------------

1. SUPPRESSION DE LA REGLE ECRITE A LA MAIN
   app.py ligne 61 :
       'action': 'EVITER' if gene_val == 0.0 else ('ADAPTER_DOSE' if gene_val == 0.5
                                                   else 'STANDARD')
   Cette ligne deduisait l action d un seuil sur la valeur du gene et remplacait la
   sortie du modele dans le resume par gene. L application n utilisait donc pas le
   Deep Learning a cet endroit, mais trois conditions. Le resume est desormais produit
   par predict_v3.resume_par_gene, a partir des predictions du modele.

2. PROFIL COMPLET A L INFERENCE
   download_pdf appelait predict_action(gene, drug, genotype), qui construisait un
   vecteur de 1.0 sur les 31 genes et n en renseignait qu un seul. Toutes les routes
   utilisent maintenant predict_drug_for_patient, qui recoit le profil complet.

3. TOUS LES MEDICAMENTS INTERROGEABLES
   La recherche passait par predict_for_patient, qui ecartait silencieusement tout
   medicament absent du dictionnaire GENE_DRUGS. Elle porte maintenant sur l ensemble
   du referentiel moleculaire, et affiche un message explicite quand la molecule n y
   figure pas.

Les libelles affiches sont les libelles cliniques de predict_v3 ; les etiquettes du
modele (EVITER, ADAPTER_DOSE, SURVEILLER, STANDARD) restent inchangees en interne.
"""

import os
import sys

from flask import Flask, render_template, request, redirect, url_for, send_file

sys.path.insert(0, '/home/mouna/projet_memoire/scripts')

from vcf_parser import parse_vcf
from drug_recommender import (load_pharmgkb, load_clinical_variants,
                              load_guidelines, get_recommendations)
from generate_report import generate_pdf_report

from predict_v3 import (
    load_models, predict_for_patient, predict_drug_for_patient,
    build_patient_profile, genes_mutes, resume_par_gene,
    PHENO_EXPLAIN, ACTION_ICONS, ACTION_LABELS, ACTION_COLORS, ACTION_DETAIL,
    ORDRE_GRAVITE, VERSION,
)

app = Flask(__name__)

UPLOAD_FOLDER  = '/home/mouna/projet_memoire/app/uploads'
PHARMGKB_FILE  = '/home/mouna/projet_memoire/data/var_drug_ann.tsv'
CLINICAL_FILE  = '/home/mouna/projet_memoire/data/clinicalVariants.tsv'
JSON_DIR       = '/home/mouna/projet_memoire/data'

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

AVERTISSEMENT = ("Prototype expérimental de recherche. Les sorties du modèle ne "
                 "constituent pas une recommandation clinique et ne remplacent pas "
                 "l'avis d'un professionnel de santé.")


# ---------------------------------------------------------------------------
def charger_contexte(filepath):
    """Analyse le VCF et charge les annotations de reference."""
    variants_df = parse_vcf(filepath)
    if len(variants_df) == 0:
        return variants_df, None, []

    pharmgkb_df = load_pharmgkb(PHARMGKB_FILE)
    clinical_df = load_clinical_variants(CLINICAL_FILE)
    guidelines  = load_guidelines(JSON_DIR)
    results_df  = get_recommendations(variants_df, pharmgkb_df, clinical_df, guidelines)
    results_df  = (results_df
                   .drop_duplicates(subset=['gene', 'rsid', 'drug', 'phenotype'])
                   .sort_values(['gene', 'drug']))
    drugs_list = sorted(results_df[results_df['drug'] != 'Aucune recommandation trouvee']
                        ['drug'].unique().tolist())
    return variants_df, results_df, drugs_list


def analyser_patient(variants_df, results_df):
    """Predictions du modele et resume par gene.

    Le resume provient des predictions, non d une regle sur la valeur du gene.
    """
    variants_list = variants_df.to_dict('records')

    documentes = []
    if results_df is not None and len(results_df) > 0:
        documentes = (results_df[results_df['drug'] != 'Aucune recommandation trouvee']
                      ['drug'].unique().tolist())

    predictions, mutes, gene_vector = predict_for_patient(variants_list,
                                                          extra_drugs=documentes)
    cpic_by_gene = resume_par_gene(predictions, gene_vector, mutes)
    return predictions, cpic_by_gene, gene_vector, mutes


# ---------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


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
        return render_template(
            'results.html', filename=fichier.filename,
            variants=[], results=[], predictions=[], drugs_list=[],
            n_variants=0, n_results=0, drug_search=None, drug_result=None,
            cpic_by_gene={}, covered_drugs=[], no_mutation=True,
            version_modele=VERSION, avertissement=AVERTISSEMENT)

    predictions, cpic_by_gene, _, _ = analyser_patient(variants_df, results_df)

    return render_template(
        'results.html', filename=fichier.filename,
        variants=variants_df.to_dict('records'),
        results=results_df.to_dict('records'),
        predictions=predictions, drugs_list=drugs_list,
        n_variants=len(variants_df), n_results=len(results_df),
        drug_search=None, drug_result=None,
        cpic_by_gene=cpic_by_gene, covered_drugs=[],
        version_modele=VERSION, avertissement=AVERTISSEMENT)


@app.route('/search_drug', methods=['POST'])
def search_drug():
    saisie = request.form.get('drug_query', '').lower().strip()
    drug_query = DRUG_NORMALIZE.get(saisie, saisie)
    vcf_filename = request.form.get('vcf_filename', '')
    filepath = os.path.join(UPLOAD_FOLDER, vcf_filename)

    variants_df, results_df, drugs_list = charger_contexte(filepath)
    predictions, cpic_by_gene, gene_vector, mutes = analyser_patient(variants_df,
                                                                     results_df)

    # Interrogation directe sur le profil complet, sans filtre GENE_DRUGS
    fiche = predict_drug_for_patient(gene_vector, drug_query, mutes)

    if fiche.get('known_drug'):
        action = fiche['action']
        details = []
        if not fiche['association_documentee']:
            details.append("Aucune association documentée entre ce médicament et les "
                           "gènes atypiques de ce patient dans les référentiels. "
                           "La prédiction repose sur le profil génétique global et la "
                           "structure de la molécule.")
        if fiche['action_dl'] != action:
            details.append(f"Le réseau profond seul prédit « "
                           f"{ACTION_LABELS.get(fiche['action_dl'], fiche['action_dl'])} ».")
        if fiche['action_xgboost'] != action:
            details.append(f"XGBoost prédit « "
                           f"{ACTION_LABELS.get(fiche['action_xgboost'], fiche['action_xgboost'])} ».")

        drug_result = {
            'status':         ACTION_COLORS.get(action, 'secondary'),
            'message':        f"{ACTION_ICONS.get(action, '')} {drug_query.upper()} — "
                              f"{ACTION_LABELS.get(action, action)}",
            'action':         action,
            'detail':         ACTION_DETAIL.get(action, ''),
            'confidence':     fiche['confidence'],
            'responsible_gene': fiche['responsible_gene'],
            'ml_predictions': [fiche],
            'details':        details,
        }
    else:
        drug_result = {
            'status':  'info',
            'message': f"{drug_query.upper()} — médicament hors référentiel moléculaire",
            'action':  None,
            'detail':  ("Cette molécule ne figure pas dans le référentiel de "
                        "531 médicaments du modèle. Aucune prédiction n'est produite "
                        "plutôt qu'une prédiction non fondée."),
            'ml_predictions': [],
            'details': [],
        }

    return render_template(
        'results.html', filename=vcf_filename,
        variants=variants_df.to_dict('records'),
        results=results_df.to_dict('records'),
        predictions=predictions, drugs_list=drugs_list,
        n_variants=len(variants_df), n_results=len(results_df),
        drug_search=drug_query, drug_result=drug_result,
        cpic_by_gene=cpic_by_gene, covered_drugs=[],
        version_modele=VERSION, avertissement=AVERTISSEMENT)


@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    vcf_filename = request.form.get('vcf_filename', '')
    drug_search = request.form.get('drug_search', '')
    filepath = os.path.join(UPLOAD_FOLDER, vcf_filename)

    variants_df, results_df, _ = charger_contexte(filepath)
    predictions, _, gene_vector, mutes = analyser_patient(variants_df, results_df)

    drug_result = None
    if drug_search:
        # Profil complet, et non un patient fictif normal sur trente genes
        fiche = predict_drug_for_patient(gene_vector, drug_search, mutes)
        if fiche.get('known_drug'):
            drug_result = {
                'message': f"{ACTION_ICONS.get(fiche['action'], '')} {drug_search} — "
                           f"{ACTION_LABELS.get(fiche['action'], fiche['action'])}",
                'action':  fiche['action'],
                'detail':  ACTION_DETAIL.get(fiche['action'], ''),
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
