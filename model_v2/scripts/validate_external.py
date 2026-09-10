import pandas as pd
import numpy as np
import joblib, pickle, sys
sys.path.insert(0, "/home/mouna/projet_memoire/scripts")
from vcf_parser import parse_vcf

# Charger les modeles et encodeur
rf  = joblib.load("/home/mouna/projet_memoire/model_v2/results/rf_final.pkl")
xgb = joblib.load("/home/mouna/projet_memoire/model_v2/results/xgb_final.pkl")
with open("/home/mouna/projet_memoire/model_v2/results/label_encoder.pkl","rb") as f:
    le = pickle.load(f)
with open("/home/mouna/projet_memoire/model_v2/results/feature_cols.pkl","rb") as f:
    feature_cols = pickle.load(f)

# Charger dataset pour connaitre les variants de chaque gene
df_data = pd.read_csv("/home/mouna/projet_memoire/model_v2/data/combined_dataset.csv")

# Parser le VCF reel
vcf_file = "/home/mouna/projet_memoire/data/pharmacat.example2.vcf"
variants_df = parse_vcf(vcf_file)
print("Variants detectes dans le VCF :")
print(variants_df[["gene","rsid","genotype"]].to_string(index=False))

# Pour chaque gene present dans le VCF
genes_in_vcf = variants_df["gene"].unique()

print("")
print("=" * 60)
print("VALIDATION EXTERNE — Comparaison avec PharmCAT")
print("=" * 60)

# Reference PharmCAT pour ce VCF (publie officiellement)
PHARMCAT_REFERENCE = {
    "CYP2C19": "Poor Metabolizer",
    "CYP2B6":  "Indeterminate",
}

for gene in genes_in_vcf:
    gene_variants = variants_df[variants_df["gene"] == gene]
    # Construire le vecteur pour ce gene
    vector = np.ones(len(feature_cols))
    for i, feat in enumerate(feature_cols):
        if feat == "activity_score_total":
            # Calculer activity score depuis les genotypes
            score = 0.0
            for _, row in gene_variants.iterrows():
                rsid = row["rsid"]
                gt   = row["genotype"]
                # Score selon genotype
                if gt == "1/1":   score += 0.0  # homozygote muté = perte totale
                elif gt == "0/1": score += 0.5  # heterozygote = perte partielle
                else:             score += 1.0  # normal
            vector[i] = score
        elif feat in gene_variants["rsid"].values:
            row = gene_variants[gene_variants["rsid"] == feat].iloc[0]
            gt  = row["genotype"]
            if gt == "1/1":   vector[i] = 0.0
            elif gt == "0/1": vector[i] = 0.5
            else:             vector[i] = 1.0
    vector = vector.reshape(1, -1)
    # Predictions
    pred_rf  = le.inverse_transform(rf.predict(vector))[0]
    pred_xgb = le.inverse_transform(xgb.predict(vector))[0]
    prob_rf  = round(rf.predict_proba(vector).max()*100, 1)
    prob_xgb = round(xgb.predict_proba(vector).max()*100, 1)
    ref = PHARMCAT_REFERENCE.get(gene, "Non disponible")
    concordance_rf  = "OK" if pred_rf  == ref else "DIVERGE"
    concordance_xgb = "OK" if pred_xgb == ref else "DIVERGE"
    print("")
    print("Gene : " + gene)
    print("  Variants : " + ", ".join(gene_variants["rsid"].tolist()))
    print("  RF  predit : " + pred_rf  + " (" + str(prob_rf)  + "%) — " + concordance_rf)
    print("  XGB predit : " + pred_xgb + " (" + str(prob_xgb) + "%) — " + concordance_xgb)
    print("  PharmCAT   : " + ref)

print("")
print("=" * 60)
print("NOTE : CYP2B6 Indeterminate dans PharmCAT = pas assez")
print("d information pour classer. Notre modele fait une")
print("prediction meme dans ce cas — avantage du DL.")
print("=" * 60)