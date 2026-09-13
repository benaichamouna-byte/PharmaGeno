from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import sys, os

sys.path.insert(0, '/home/mouna/projet_memoire/scripts')
from vcf_parser import parse_vcf
from drug_recommender import load_pharmgkb, load_clinical_variants, load_guidelines, get_recommendations
from predict_v2 import load_models_v2, predict_action, predict_for_variant, predict_for_patient, PHENO_EXPLAIN, ACTION_ICONS, ACTION_LABELS, ACTION_COLORS
from generate_report import generate_pdf_report

app = Flask(__name__)
UPLOAD_FOLDER = '/home/mouna/projet_memoire/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PHARMGKB_FILE = '/home/mouna/projet_memoire/data/var_drug_ann.tsv'
CLINICAL_FILE = '/home/mouna/projet_memoire/data/clinicalVariants.tsv'
JSON_DIR      = '/home/mouna/projet_memoire/data'

load_models_v2()

DRUG_NORMALIZE = {
    'warfarine':'warfarin','aspirine':'aspirin','methadone':'methadone',
    'fluorouracile':'fluorouracil','capecitabine':'capecitabine',
    'tamoxifene':'tamoxifen','codeine':'codeine','omeprazole':'omeprazole',
}

ORDER = ['EVITER','ADAPTER_DOSE','SURVEILLER','STANDARD']

def build_results(variants_df, results_df):
    variants_list = variants_df.to_dict('records')
    extra_drugs   = results_df[results_df['drug']!='Aucune recommandation trouvee']['drug'].unique().tolist()
    patient_preds, mutated_genes, gene_vector = predict_for_patient(variants_list, extra_drugs)
    cpic_by_gene = {}
    from predict_v2 import GENE_DRUGS, PHENO_EXPLAIN, _GENES
    for gene in mutated_genes:
        idx      = _GENES.index(gene) if gene in _GENES else -1
        gene_val = gene_vector[idx] if idx >= 0 else 1.0
        gene_drugs_preds = [p for p in patient_preds if gene in p['responsible_gene']]
        if not gene_drugs_preds:
            gene_drugs_preds = patient_preds[:3]
        worst = sorted(gene_drugs_preds, key=lambda x: ORDER.index(x['action']) if x['action'] in ORDER else 4)[0]
        cpic_by_gene[gene] = {
            'action':          worst['action'],
            'icon':            worst['icon'],
            'label':           worst['label'],
            'color':           worst['color'],
            'phenotype':       PHENO_EXPLAIN.get(gene_val,'Normal Metabolizer'),
            'recommendations': gene_drugs_preds,
        }
    predictions = patient_preds
    return predictions, cpic_by_gene

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'vcf_file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['vcf_file']
    if file.filename == '': return redirect(url_for('index'))
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    variants_df = parse_vcf(filepath)
    if len(variants_df) == 0:
        return render_template('results.html', filename=file.filename,
            variants=[], results=[], predictions=[], drugs_list=[],
            n_variants=0, n_results=0, drug_search=None, drug_result=None,
            cpic_by_gene={}, covered_drugs=[], no_mutation=True)
    pharmgkb_df = load_pharmgkb(PHARMGKB_FILE)
    clinical_df = load_clinical_variants(CLINICAL_FILE)
    guidelines  = load_guidelines(JSON_DIR)
    results_df  = get_recommendations(variants_df, pharmgkb_df, clinical_df, guidelines)
    results_df  = results_df.drop_duplicates(subset=['gene','rsid','drug','phenotype']).sort_values(['gene','drug'])
    drugs_list  = sorted(results_df[results_df['drug']!='Aucune recommandation trouvee']['drug'].unique().tolist())
    predictions, cpic_by_gene = build_results(variants_df, results_df)
    return render_template('results.html', filename=file.filename,
        variants=variants_df.to_dict('records'), results=results_df.to_dict('records'),
        predictions=predictions, drugs_list=drugs_list,
        n_variants=len(variants_df), n_results=len(results_df),
        drug_search=None, drug_result=None, cpic_by_gene=cpic_by_gene, covered_drugs=[])

@app.route('/search_drug', methods=['POST'])
def search_drug():
    drug_query   = DRUG_NORMALIZE.get(request.form.get('drug_query','').lower().strip(), request.form.get('drug_query','').lower().strip())
    vcf_filename = request.form.get('vcf_filename','')
    filepath     = os.path.join(UPLOAD_FOLDER, vcf_filename)
    variants_df  = parse_vcf(filepath)
    pharmgkb_df  = load_pharmgkb(PHARMGKB_FILE)
    clinical_df  = load_clinical_variants(CLINICAL_FILE)
    guidelines   = load_guidelines(JSON_DIR)
    results_df   = get_recommendations(variants_df, pharmgkb_df, clinical_df, guidelines)
    results_df   = results_df.drop_duplicates(subset=['gene','rsid','drug','phenotype'])
    drugs_list   = sorted(results_df[results_df['drug']!='Aucune recommandation trouvee']['drug'].unique().tolist())
    ml_predictions = []
    for _, variant in variants_df.iterrows():
        pred = predict_action(variant['gene'], drug_query, variant['genotype'])
        pred.update({'gene':variant['gene'],'rsid':variant['rsid'],'genotype':variant['genotype'],'drug':drug_query})
        ml_predictions.append(pred)
    if ml_predictions:
        worst  = sorted(ml_predictions, key=lambda x: ORDER.index(x['action']) if x['action'] in ORDER else 4)[0]
        action = worst['action']
        drug_result = {'status':ACTION_COLORS.get(action,'secondary'),
            'message':ACTION_ICONS.get(action,'') + ' ' + drug_query.upper() + ' — ' + ACTION_LABELS.get(action,action),
            'action':action, 'ml_predictions':ml_predictions, 'details':[]}
    else:
        drug_result = {'status':'info','message':drug_query+' — aucune donnee disponible','ml_predictions':[]}
    predictions, cpic_by_gene = build_results(variants_df, results_df)
    return render_template('results.html', filename=vcf_filename,
        variants=variants_df.to_dict('records'),
        results=results_df.sort_values(['gene','drug']).to_dict('records'),
        predictions=predictions, drugs_list=drugs_list,
        n_variants=len(variants_df), n_results=len(results_df),
        drug_search=drug_query, drug_result=drug_result,
        cpic_by_gene=cpic_by_gene, covered_drugs=[])

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    vcf_filename = request.form.get('vcf_filename','')
    drug_search  = request.form.get('drug_search','')
    filepath     = os.path.join(UPLOAD_FOLDER, vcf_filename)
    variants_df  = parse_vcf(filepath)
    pharmgkb_df  = load_pharmgkb(PHARMGKB_FILE)
    clinical_df  = load_clinical_variants(CLINICAL_FILE)
    guidelines   = load_guidelines(JSON_DIR)
    results_df   = get_recommendations(variants_df, pharmgkb_df, clinical_df, guidelines)
    results_df   = results_df.drop_duplicates(subset=['gene','rsid','drug','phenotype']).sort_values(['gene','drug'])
    predictions, _ = build_results(variants_df, results_df)
    drug_result = None
    if drug_search:
        ml_preds = []
        for _, variant in variants_df.iterrows():
            pred = predict_action(variant['gene'], drug_search, variant['genotype'])
            pred.update({'gene':variant['gene'],'rsid':variant['rsid'],'drug':drug_search})
            ml_preds.append(pred)
        if ml_preds:
            worst = sorted(ml_preds, key=lambda x: ORDER.index(x['action']) if x['action'] in ORDER else 4)[0]
            drug_result = {'message':ACTION_ICONS.get(worst['action'],'') + ' ' + drug_search + ' — ' + ACTION_LABELS.get(worst['action'],worst['action'])}
    pdf_buffer = generate_pdf_report(vcf_filename, variants_df.to_dict('records'),
        predictions, results_df.to_dict('records'), drug_search, drug_result)
    return send_file(pdf_buffer, mimetype='application/pdf',
        as_attachment=True, download_name=f'rapport_pharmageno_{vcf_filename}.pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
