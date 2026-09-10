import pandas as pd
import numpy as np
import os

OUTPUT_DIR = "/home/mouna/projet_memoire/model_v2/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Charger les deux fichiers
print("Chargement des données...")
cv = pd.read_csv("/home/mouna/projet_memoire/data/clinicalVariants.tsv", sep="	", low_memory=False)
vd = pd.read_csv("/home/mouna/projet_memoire/data/var_drug_ann.tsv", sep="	", low_memory=False)

print("clinicalVariants : " + str(len(cv)) + " lignes")
print("var_drug_ann     : " + str(len(vd)) + " lignes")
print("")
print("Colonnes clinicalVariants :")
for i, col in enumerate(cv.columns): print("  " + str(i+1) + ". " + col)
print("")
print("Colonnes var_drug_ann :")
for i, col in enumerate(vd.columns[:8]): print("  " + str(i+1) + ". " + col)
print("")

# Niveaux de preuve disponibles
print("Niveaux de preuve dans clinicalVariants :")
print(cv["level of evidence"].value_counts().to_string())
print("")

# Filtrer niveau 1A et 2A seulement
cv_filtered = cv[cv["level of evidence"].isin(["1A", "2A"])]
print("Après filtrage 1A+2A : " + str(len(cv_filtered)) + " lignes")
print("")

# Gènes couverts après filtrage
genes = cv_filtered["gene"].dropna().unique()
print("Gènes couverts (niveau 1A+2A) : " + str(len(genes)))
print(", ".join(sorted(genes)))
print("")

# Sauvegarder pour vérification
cv_filtered.to_csv(OUTPUT_DIR + "/clinical_variants_filtered.csv", index=False)
print("Fichier sauvegardé : clinical_variants_filtered.csv")