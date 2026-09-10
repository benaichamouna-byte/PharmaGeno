import pandas as pd
import numpy as np
import os

OUTPUT_DIR = "/home/mouna/projet_memoire/model_v2/data"

# Charger données filtrées
cv = pd.read_csv(OUTPUT_DIR + "/clinical_variants_filtered.csv")
vd = pd.read_csv("/home/mouna/projet_memoire/data/var_drug_ann.tsv", sep="	", low_memory=False)

# Nettoyer var_drug_ann
vd = vd[["Variant/Haplotypes","Gene","Drug(s)","Phenotype Category","Significance"]]
vd.columns = ["variant","gene","drug","phenotype_cat","significance"]
vd = vd[vd["significance"] == "yes"]

print("Données après filtrage significance=yes : " + str(len(vd)) + " lignes")

# Mapping phenotype category -> action clinique
ACTION_MAP = {
    "Dosage":       "ADAPTER_DOSE",
    "Toxicity":     "EVITER",
    "Efficacy":     "EVITER",
    "Metabolism/PK":"ADAPTER_DOSE",
    "Other":        "SURVEILLER",
}

# Combiner les deux sources
# Source 1 : clinicalVariants (niveau 1A/2A)
rows = []
for _, row in cv.iterrows():
    variant = str(row["variant"]).strip()
    gene    = str(row["gene"]).strip()
    drug    = str(row["chemicals"]).strip()
    pheno   = str(row["type"]).strip()
    level   = str(row["level of evidence"]).strip()
    if drug == "nan" or gene == "nan": continue
    action = ACTION_MAP.get(pheno, "SURVEILLER")
    # Pour Toxicity et Efficacy on met EVITER
    # Pour Dosage et Metabolism on met ADAPTER_DOSE
    rows.append({
        "variant": variant,
        "gene":    gene,
        "drug":    drug.lower().strip(),
        "action":  action,
        "phenotype": pheno,
        "level":   level,
        "source":  "clinicalVariants"
    })

# Source 2 : var_drug_ann (significance=yes)
for _, row in vd.iterrows():
    variant = str(row["variant"]).strip()
    gene    = str(row["gene"]).strip()
    drug    = str(row["drug"]).strip()
    pheno   = str(row["phenotype_cat"]).strip()
    if drug == "nan" or gene == "nan": continue
    action = ACTION_MAP.get(pheno, "SURVEILLER")
    rows.append({
        "variant": variant,
        "gene":    gene,
        "drug":    drug.lower().strip(),
        "action":  action,
        "phenotype": pheno,
        "level":   "PharmGKB",
        "source":  "var_drug_ann"
    })

df = pd.DataFrame(rows)
df = df.drop_duplicates(subset=["variant","gene","drug"])

print("Dataset combiné : " + str(len(df)) + " associations uniques")
print("")
print("Distribution des actions :")
print(df["action"].value_counts().to_string())
print("")
print("Gènes couverts : " + str(df["gene"].nunique()))
print("Médicaments couverts : " + str(df["drug"].nunique()))
print("")
print("Top 20 médicaments :")
print(df["drug"].value_counts().head(20).to_string())

# Sauvegarder
df.to_csv(OUTPUT_DIR + "/full_pgx_dataset.csv", index=False)
print("")
print("Sauvegardé : full_pgx_dataset.csv")