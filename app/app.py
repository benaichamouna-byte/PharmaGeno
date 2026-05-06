from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sys
import os

sys.path.append('/home/mouna/projet_memoire/scripts')
from vcf_parser import parse_vcf
from drug_recommender import load_pharmgkb, load_clinical_variants, load_guidelines, get_recommendations

app = Flask(__name__)
UPLOAD_FOLDER = '/home/mouna/projet_memoire/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PHARMGKB_FILE = '/home/mouna/projet_memoire/data/var_drug_ann.tsv'
CLINICAL_FILE = '/home/mouna/projet_memoire/data/clinicalVariants.tsv'
JSON_DIR      = '/home/mouna/projet_memoire/data'

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'vcf_file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['vcf_file']
    if file.filename == '':
        return redirect(url_for('index'))
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    variants_df = parse_vcf(filepath)
    pharmgkb_df = load_pharmgkb(PHARMGKB_FILE)
    clinical_df = load_clinical_variants(CLINICAL_FILE)
    guidelines  = load_guidelines(JSON_DIR)
    results_df  = get_recommendations(variants_df, pharmgkb_df, clinical_df, guidelines)
    results_df  = results_df.drop_duplicates(subset=['gene', 'rsid', 'drug', 'phenotype'])
    results_df  = results_df.sort_values(['gene', 'drug'])

    # Liste unique des médicaments pour la recherche
    drugs_list = sorted(results_df[results_df['drug'] != 'Aucune recommandation trouvée']['drug'].unique().tolist())

    variants = variants_df.to_dict('records')
    results  = results_df.to_dict('records')

    return render_template('results.html',
                           filename=file.filename,
                           variants=variants,
                           results=results,
                           drugs_list=drugs_list,
                           n_variants=len(variants_df),
                           n_results=len(results_df),
                           drug_search=None,
                           drug_result=None)

@app.route('/search_drug', methods=['POST'])
def search_drug():
    drug_query   = request.form.get('drug_query', '').lower().strip()
    vcf_filename = request.form.get('vcf_filename', '')
    filepath     = os.path.join(UPLOAD_FOLDER, vcf_filename)

    variants_df = parse_vcf(filepath)
    pharmgkb_df = load_pharmgkb(PHARMGKB_FILE)
    clinical_df = load_clinical_variants(CLINICAL_FILE)
    guidelines  = load_guidelines(JSON_DIR)
    results_df  = get_recommendations(variants_df, pharmgkb_df, clinical_df, guidelines)
    results_df  = results_df.drop_duplicates(subset=['gene', 'rsid', 'drug', 'phenotype'])

    # Chercher le médicament
    match = results_df[results_df['drug'].str.lower().str.contains(drug_query, na=False)]

    if match.empty:
        drug_result = {
            'status': 'safe',
            'message': f'Aucune interaction pharmacogénomique connue pour {drug_query}.',
            'details': []
        }
    else:
        # Vérifier le type de phénotype
        phenotypes = match['phenotype'].tolist()
        if any(p in ['Toxicity', 'Dosage'] for p in phenotypes):
            status = 'danger'
            message = f'⚠️ ATTENTION — Interaction détectée pour {drug_query}'
        elif any(p in ['Efficacy'] for p in phenotypes):
            status = 'warning'
            message = f'⚠️ Efficacité potentiellement réduite pour {drug_query}'
        else:
            status = 'warning'
            message = f'Information pharmacogénomique disponible pour {drug_query}'

        drug_result = {
            'status': status,
            'message': message,
            'details': match[['gene', 'rsid', 'genotype', 'phenotype', 'source']].to_dict('records')
        }

    drugs_list = sorted(results_df[results_df['drug'] != 'Aucune recommandation trouvée']['drug'].unique().tolist())
    variants   = variants_df.to_dict('records')
    results    = results_df.sort_values(['gene', 'drug']).to_dict('records')

    return render_template('results.html',
                           filename=vcf_filename,
                           variants=variants,
                           results=results,
                           drugs_list=drugs_list,
                           n_variants=len(variants_df),
                           n_results=len(results_df),
                           drug_search=drug_query,
                           drug_result=drug_result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
