from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sys
import os

sys.path.append('/home/mouna/projet_memoire/scripts')
from vcf_parser import parse_vcf
from drug_recommender import load_pharmgkb, load_clinical_variants, load_guidelines, get_recommendations
from predict_phenotype import load_rf_model, predict_phenotype, find_best_column
from generate_report import generate_pdf_report
from flask import send_file

app = Flask(__name__)
UPLOAD_FOLDER = '/home/mouna/projet_memoire/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PHARMGKB_FILE = '/home/mouna/projet_memoire/data/var_drug_ann.tsv'
CLINICAL_FILE = '/home/mouna/projet_memoire/data/clinicalVariants.tsv'
JSON_DIR      = '/home/mouna/projet_memoire/data'

rf, columns, classes = load_rf_model()

def predict_best_for_variant(gene, rsid, genotype, drug_matches):
    drug_matches = [d for d in drug_matches if d != 'Aucune recommandation trouvée']
    best_pred = None
    for drug in (drug_matches[:5] if drug_matches else ['']):
        pred = predict_phenotype(gene, drug, rsid, genotype, rf, columns, classes)
        if best_pred is None or pred['confidence'] > best_pred['confidence']:
            best_pred = pred
            best_pred['drug_used'] = drug if drug else 'aucun'
    best_pred['gene']     = gene
    best_pred['rsid']     = rsid
    best_pred['genotype'] = genotype
    return best_pred

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

    drugs_list = sorted(results_df[
        results_df['drug'] != 'Aucune recommandation trouvée'
    ]['drug'].unique().tolist())

    predictions = []
    for _, variant in variants_df.iterrows():
        gene     = variant['gene']
        rsid     = variant['rsid']
        genotype = variant['genotype']
        drug_matches = results_df[results_df['rsid'] == rsid]['drug'].tolist()
        pred = predict_best_for_variant(gene, rsid, genotype, drug_matches)
        predictions.append(pred)

    variants = variants_df.to_dict('records')
    results  = results_df.to_dict('records')

    return render_template('results.html',
                           filename=file.filename,
                           variants=variants,
                           results=results,
                           predictions=predictions,
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

    match = results_df[results_df['drug'].str.lower().str.contains(drug_query, na=False)]
    match = match.drop_duplicates(subset=['gene', 'rsid', 'phenotype'])

    ml_predictions = []
    genes_with_drug = match['gene'].unique().tolist() if not match.empty else []
    for _, variant in variants_df.iterrows():
        if variant['gene'] not in genes_with_drug:
            continue
        pred = predict_phenotype(
            variant['gene'], drug_query, variant['rsid'],
            variant['genotype'], rf, columns, classes)
        pred['gene']     = variant['gene']
        pred['rsid']     = variant['rsid']
        pred['genotype'] = variant['genotype']
        ml_predictions.append(pred)

    if match.empty:
        drug_result = {
            'status':  'safe',
            'message': f'Aucune interaction pharmacogénomique connue pour {drug_query}.',
            'details': [],
            'ml_predictions': ml_predictions
        }
    else:
        phenotypes = match['phenotype'].tolist()
        if any(p in ['Toxicity', 'Dosage'] for p in phenotypes):
            status  = 'danger'
            message = f'⚠️ ATTENTION — Interaction détectée pour {drug_query}'
        elif any(p in ['Efficacy'] for p in phenotypes):
            status  = 'warning'
            message = f'⚠️ Efficacité potentiellement réduite pour {drug_query}'
        else:
            status  = 'warning'
            message = f'Information pharmacogénomique disponible pour {drug_query}'

        drug_result = {
            'status':  status,
            'message': message,
            'details': match[['gene', 'rsid', 'genotype', 'phenotype', 'source']].to_dict('records'),
            'ml_predictions': ml_predictions
        }

    drugs_list = sorted(results_df[
        results_df['drug'] != 'Aucune recommandation trouvée'
    ]['drug'].unique().tolist())

    predictions = []
    for _, variant in variants_df.iterrows():
        gene     = variant['gene']
        rsid     = variant['rsid']
        genotype = variant['genotype']
        drug_matches = results_df[results_df['rsid'] == rsid]['drug'].tolist()
        pred = predict_best_for_variant(gene, rsid, genotype, drug_matches)
        predictions.append(pred)

    variants = variants_df.to_dict('records')
    results  = results_df.sort_values(['gene', 'drug']).to_dict('records')

    return render_template('results.html',
                           filename=vcf_filename,
                           variants=variants,
                           results=results,
                           predictions=predictions,
                           drugs_list=drugs_list,
                           n_variants=len(variants_df),
                           n_results=len(results_df),
                           drug_search=drug_query,
                           drug_result=drug_result)
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    vcf_filename = request.form.get('vcf_filename', '')
    drug_search  = request.form.get('drug_search', '')
    filepath     = os.path.join(UPLOAD_FOLDER, vcf_filename)

    variants_df = parse_vcf(filepath)
    pharmgkb_df = load_pharmgkb(PHARMGKB_FILE)
    clinical_df = load_clinical_variants(CLINICAL_FILE)
    guidelines  = load_guidelines(JSON_DIR)
    results_df  = get_recommendations(variants_df, pharmgkb_df, clinical_df, guidelines)
    results_df  = results_df.drop_duplicates(subset=['gene', 'rsid', 'drug', 'phenotype'])
    results_df  = results_df.sort_values(['gene', 'drug'])

    predictions = []
    for _, variant in variants_df.iterrows():
        gene     = variant['gene']
        rsid     = variant['rsid']
        genotype = variant['genotype']
        drug_matches = results_df[results_df['rsid'] == rsid]['drug'].tolist()
        pred = predict_best_for_variant(gene, rsid, genotype, drug_matches)
        predictions.append(pred)

    variants = variants_df.to_dict('records')
    results  = results_df.to_dict('records')

    drug_result = None
    if drug_search:
        match = results_df[results_df['drug'].str.lower().str.contains(drug_search.lower(), na=False)]
        if not match.empty:
            phenotypes = match['phenotype'].tolist()
            message = (f'⚠️ Interaction détectée pour {drug_search}'
                       if any(p in ['Toxicity','Dosage'] for p in phenotypes)
                       else f'Information disponible pour {drug_search}')
            drug_result = {'message': message}

    pdf_buffer = generate_pdf_report(vcf_filename, variants, predictions, results,
                                      drug_search, drug_result)

    return send_file(pdf_buffer, mimetype='application/pdf',
                      as_attachment=True,
                      download_name=f'rapport_pharmageno_{vcf_filename}.pdf')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
