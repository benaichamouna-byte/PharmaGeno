import pandas as pd
import numpy as np
import joblib
import pickle
import torch
import torch.nn as nn
import warnings
warnings.filterwarnings('ignore')

RF_MODEL   = '/home/mouna/projet_memoire/results/rf_v3_model.pkl'
RF_COLUMNS = '/home/mouna/projet_memoire/results/rf_v3_columns.pkl'
RF_CLASSES = '/home/mouna/projet_memoire/results/rf_v3_classes.pkl'

DL_MODEL   = '/home/mouna/projet_memoire/results/dl_v5_final.pth'
DL_COLUMNS = '/home/mouna/projet_memoire/results/dl_v5_columns.pkl'
DL_CLASSES = '/home/mouna/projet_memoire/results/dl_v5_classes.pkl'

class PharmDLv5(nn.Module):
    def __init__(self, input_size):
        super(PharmDLv5, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, 4)
        )
    def forward(self, x):
        return self.net(x)

def load_rf_model():
    rf = joblib.load(RF_MODEL)
    with open(RF_COLUMNS, 'rb') as f:
        columns = pickle.load(f)
    with open(RF_CLASSES, 'rb') as f:
        classes = pickle.load(f)
    return rf, columns, classes

def load_dl_model():
    with open(DL_COLUMNS, 'rb') as f:
        columns = pickle.load(f)
    with open(DL_CLASSES, 'rb') as f:
        classes = pickle.load(f)
    model = PharmDLv5(len(columns))
    model.load_state_dict(torch.load(DL_MODEL, map_location='cpu'))
    model.eval()
    return model, columns, classes

def find_best_column(prefix, value, columns):
    exact = f'{prefix}_{value.lower()}'
    if exact in columns:
        return exact
    for col in columns:
        if col.startswith(prefix + '_') and value.lower() in col.lower():
            return col
    return None

def predict_rf(gene, drug, rsid, genotype_str, rf, columns, classes):
    row = pd.Series(0, index=columns)
    gene_col = find_best_column('gene', gene, columns)
    drug_col = find_best_column('drug', drug, columns) if drug else None
    var_col  = find_best_column('variant', rsid, columns)
    if gene_col: row[gene_col] = 1
    if drug_col: row[drug_col] = 1
    if var_col:  row[var_col]  = 1

    proba      = rf.predict_proba([row.values])[0]
    pred_idx   = np.argmax(proba)
    return classes[pred_idx], round(proba[pred_idx] * 100, 1)

def predict_dl(gene, drug, rsid, genotype_str, model, columns, classes):
    gt_enc = 2 if genotype_str == '1/1' else 1 if genotype_str == '0/1' else 0
    row = pd.Series(0, index=columns)
    gene_col = find_best_column('gene', gene, columns)
    drug_col = find_best_column('drug', drug, columns) if drug else None
    var_col  = find_best_column('variant', rsid, columns)
    if gene_col: row[gene_col] = 1
    if drug_col: row[drug_col] = 1
    if var_col:  row[var_col]  = 1
    if 'genotype' in columns: row['genotype'] = gt_enc

    x = torch.FloatTensor([row.values.astype(np.float32)])
    with torch.no_grad():
        output = model(x)
        proba  = torch.softmax(output, dim=1).numpy()[0]
    pred_idx = np.argmax(proba)
    return classes[pred_idx], round(proba[pred_idx] * 100, 1)

def predict_phenotype(gene, drug, rsid, genotype_str, rf, columns, classes,
                       dl_model=None, dl_columns=None, dl_classes=None):
    gene_known = find_best_column('gene', gene, columns) is not None
    if not gene_known:
        return {
            'phenotype': 'Non determine',
            'confidence': 0,
            'color': 'unknown',
            'level': 'Gene non reconnu par le modele',
            'gene_recognized': False
        }
    phenotype_rf, confidence_rf = predict_rf(gene, drug, rsid, genotype_str, rf, columns, classes)

    if dl_model is not None:
        phenotype_dl, confidence_dl = predict_dl(gene, drug, rsid, genotype_str,
                                                    dl_model, dl_columns, dl_classes)
        agreement = (phenotype_rf == phenotype_dl)
        avg_confidence = round((confidence_rf + confidence_dl) / 2, 1)

        if agreement and avg_confidence >= 60:
            color = 'green'; level = 'Haute (accord DL+RF)'
        elif agreement:
            color = 'orange'; level = 'Modérée (accord DL+RF)'
        else:
            color = 'red'; level = 'Faible (désaccord DL/RF)'

        return {
            'phenotype':     phenotype_rf,
            'confidence':    avg_confidence,
            'color':         color,
            'level':         level,
            'phenotype_rf':  phenotype_rf,
            'confidence_rf': confidence_rf,
            'phenotype_dl':  phenotype_dl,
            'confidence_dl': confidence_dl,
            'agreement':     agreement
        }
    else:
        if confidence_rf >= 70: color = 'green'; level = 'Haute'
        elif confidence_rf >= 50: color = 'orange'; level = 'Modérée'
        else: color = 'red'; level = 'Faible'
        return {'phenotype': phenotype_rf, 'confidence': confidence_rf,
                'color': color, 'level': level}

if __name__ == '__main__':
    rf, columns, classes = load_rf_model()
    dl_model, dl_columns, dl_classes = load_dl_model()
    print(f"RF chargé : {len(columns)} colonnes | DL chargé : {len(dl_columns)} colonnes")

    tests = [
        ('CYP2C19', 'clopidogrel', 'rs4244285',  '1/1'),
        ('CYP2B6',  'efavirenz',   'rs3745274',  '0/1'),
    ]
    for gene, drug, rsid, gt in tests:
        r = predict_phenotype(gene, drug, rsid, gt, rf, columns, classes,
                               dl_model, dl_columns, dl_classes)
        print(f"\n{gene} + {drug} ({gt})")
        print(f"  RF : {r['phenotype_rf']} ({r['confidence_rf']}%)")
        print(f"  DL : {r['phenotype_dl']} ({r['confidence_dl']}%)")
        print(f"  Vote → {r['phenotype']} | Confiance: {r['confidence']}% | {r['level']}")
