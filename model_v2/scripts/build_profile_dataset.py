import pandas as pd
import numpy as np
import os, re

DATA_DIR = "/home/mouna/projet_memoire/model_v2/data"

df = pd.read_csv(DATA_DIR + "/full_pgx_dataset.csv")
print("Dataset chargé : " + str(len(df)) + " lignes")

def extract_rsid(variant_str):
    if pd.isna(variant_str): return []
    return re.findall(r"rs\d+", str(variant_str))

all_rsids = set()
for variant in df["variant"].dropna():
    for rsid in extract_rsid(variant):
        all_rsids.add(rsid)

all_rsids = sorted(list(all_rsids))
print("Variants rsID extraits : " + str(len(all_rsids)))

rows = []
for _, row in df.iterrows():
    variant = str(row["variant"])
    drug    = str(row["drug"])
    action  = str(row["action"])
    gene    = str(row["gene"])
    rsids_present = extract_rsid(variant)
    if not rsids_present: continue
    vector = {rsid: 0 for rsid in all_rsids}
    for rsid in rsids_present:
        if rsid in vector:
            vector[rsid] = 1
    vector["gene"]   = gene
    vector["drug"]   = drug
    vector["action"] = action
    rows.append(vector)

df_final = pd.DataFrame(rows)
print("Dataset final : " + str(len(df_final)) + " lignes")
print("Features (variants) : " + str(len(all_rsids)))
print("")
print("Distribution des actions :")
print(df_final["action"].value_counts().to_string())

df_final.to_csv(DATA_DIR + "/profile_drug_dataset.csv", index=False)

with open(DATA_DIR + "/all_rsids.txt", "w") as f:
    f.write("\n".join(all_rsids))

print("")
print("Sauvegardé : profile_drug_dataset.csv")
print("Sauvegardé : all_rsids.txt")
