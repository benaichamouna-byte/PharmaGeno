import pandas as pd
import numpy as np
import joblib
import pickle
import warnings
warnings.filterwarnings('ignore')

RF_MODEL   = '/home/mouna/projet_memoire/results/rf_v3_model.pkl'
RF_COLUMNS = '/home/mouna/projet_memoire/results/rf_v3_columns.pkl'
RF_CLASSES = '/home/mouna/projet_memoire/results/rf_v3_classes.pkl'

def load_rf_model():
    rf = joblib.load(RF_MODEL)
    with open(RF_COLUMNS, 'rb') as f:
        columns = pickle.load(f)
    with open(RF_CLASSES, 'rb') as f:
        classes = pickle.load(f)
    return rf, columns, classes

def find_best_column(prefix, value, columns):
    exact = f'{prefix}_{value.lower()}'
    if exact in columns:
        return exact
    for col in columns:
        if col.startswith(prefix + '_') and value.lower() in col.lower():
            return col
    return None

def predict_phenotype(gene, drug, rsid, genotype_str, rf, columns, classes):
    row = pd.Series(0, index=columns)

    gene_col    = find_best_column('gene', gene, columns)
    drug_col    = find_best_column('drug', drug, columns)
    variant_col = find_best_column('variant', rsid, columns)

    if gene_col:    row[gene_col]    = 1
    if drug_col:    row[drug_col]    = 1
    if variant_col: row[variant_col] = 1

    proba      = rf.predict_proba([row.values])[0]
    pred_idx   = np.argmax(proba)
    phenotype  = classes[pred_idx]
    confidence = proba[pred_idx] * 100

    if confidence >= 70:
        color = 'green'
        level = 'Haute'
    elif confidence >= 50:
        color = 'orange'
        level = 'Modérée'
    else:
        color = 'red'
        level = 'Faible'

    return {
        'phenotype':    phenotype,
        'confidence':   round(confidence, 1),
        'color':        color,
        'level':        level,
        'gene_col':     gene_col,
        'drug_col':     drug_col,
        'variant_col':  variant_col
    }

if __name__ == '__main__':
    rf, columns, classes = load_rf_model()
    print(f"Modèle chargé : {len(columns)} colonnes")

    tests = [
        ('CYP2C19', 'clopidogrel', 'rs4244285',  '1/1'),
        ('CYP2C19', 'omeprazole',  'rs4244285',  '1/1'),
        ('CYP2B6',  'efavirenz',   'rs3745274',  '0/1'),
        ('CYP2B6',  'methadone',   'rs3745274',  '0/1'),
    ]

    print("\nTest prédictions :")
    for gene, drug, rsid, gt in tests:
        result = predict_phenotype(gene, drug, rsid, gt, rf, columns, classes)
        print(f"\n  {gene} + {drug} ({gt})")
        print(f"  Colonnes trouvées : {result['gene_col']} | {result['drug_col']} | {result['variant_col']}")
        print(f"  → {result['phenotype']} ({result['confidence']}%) [{result['level']}]")
