import pandas as pd
import numpy as np
import os

OUTPUT_DIR = "/home/mouna/projet_memoire/model_v2/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GENES = {
    "CYP2C19": {
        "variants": ["rs4244285","rs4986893","rs28399504","rs56337013","rs12248560"],
        "alleles": {
            "*1": [1.0,1.0,1.0,1.0,1.0],
            "*2": [0.0,1.0,1.0,1.0,1.0],
            "*3": [1.0,0.0,1.0,1.0,1.0],
            "*4": [1.0,1.0,0.0,1.0,1.0],
            "*5": [1.0,1.0,1.0,0.0,1.0],
            "*17":[1.0,1.0,1.0,1.0,1.5],
        },
        "activity_scores": {"*1":1.0,"*2":0.0,"*3":0.0,"*4":0.0,"*5":0.0,"*17":1.5},
        "diplotypes": {
            ("*1","*1"):"Normal Metabolizer",
            ("*1","*2"):"Intermediate Metabolizer",
            ("*1","*3"):"Intermediate Metabolizer",
            ("*1","*4"):"Intermediate Metabolizer",
            ("*1","*5"):"Intermediate Metabolizer",
            ("*2","*2"):"Poor Metabolizer",
            ("*2","*3"):"Poor Metabolizer",
            ("*2","*4"):"Poor Metabolizer",
            ("*2","*5"):"Poor Metabolizer",
            ("*3","*3"):"Poor Metabolizer",
            ("*3","*4"):"Poor Metabolizer",
            ("*4","*4"):"Poor Metabolizer",
            ("*1","*17"):"Ultrarapid Metabolizer",
            ("*17","*17"):"Ultrarapid Metabolizer",
            ("*2","*17"):"Intermediate Metabolizer",
            ("*3","*17"):"Intermediate Metabolizer",
        }
    },
    "CYP2B6": {
        "variants": ["rs3745274","rs2279343","rs8192719","rs34223104"],
        "alleles": {
            "*1": [1.0,1.0,1.0,1.0],
            "*6": [0.5,0.5,1.0,1.0],
            "*18":[1.0,1.0,0.0,1.0],
            "*4": [1.0,1.5,1.0,1.0],
            "*11":[1.0,1.0,1.0,0.0],
        },
        "activity_scores": {"*1":1.0,"*6":0.5,"*18":0.0,"*4":1.5,"*11":0.0},
        "diplotypes": {
            ("*1","*1"):"Normal Metabolizer",
            ("*1","*6"):"Intermediate Metabolizer",
            ("*6","*6"):"Poor Metabolizer",
            ("*1","*18"):"Intermediate Metabolizer",
            ("*6","*18"):"Poor Metabolizer",
            ("*18","*18"):"Poor Metabolizer",
            ("*1","*4"):"Ultrarapid Metabolizer",
            ("*4","*6"):"Normal Metabolizer",
            ("*4","*18"):"Intermediate Metabolizer",
            ("*1","*11"):"Intermediate Metabolizer",
            ("*6","*11"):"Poor Metabolizer",
        }
    },
    "CYP2C9": {
        "variants": ["rs1799853","rs1057910","rs28371686","rs9332131"],
        "alleles": {
            "*1":[1.0,1.0,1.0,1.0],
            "*2":[0.5,1.0,1.0,1.0],
            "*3":[1.0,0.0,1.0,1.0],
            "*5":[1.0,1.0,0.0,1.0],
            "*6":[1.0,1.0,1.0,0.0],
        },
        "activity_scores": {"*1":1.0,"*2":0.5,"*3":0.0,"*5":0.0,"*6":0.0},
        "diplotypes": {
            ("*1","*1"):"Normal Metabolizer",
            ("*1","*2"):"Intermediate Metabolizer",
            ("*1","*3"):"Intermediate Metabolizer",
            ("*2","*2"):"Intermediate Metabolizer",
            ("*2","*3"):"Poor Metabolizer",
            ("*3","*3"):"Poor Metabolizer",
            ("*1","*5"):"Intermediate Metabolizer",
            ("*1","*6"):"Intermediate Metabolizer",
            ("*2","*5"):"Poor Metabolizer",
            ("*3","*5"):"Poor Metabolizer",
            ("*5","*5"):"Poor Metabolizer",
        }
    },
    "CYP2D6": {
        "variants": ["rs3892097","rs1065852","rs28371706","rs16947","rs5030655"],
        "alleles": {
            "*1":  [1.0,1.0,1.0,1.0,1.0],
            "*4":  [0.0,1.0,1.0,1.0,1.0],
            "*5":  [1.0,0.0,1.0,1.0,1.0],
            "*10": [1.0,1.0,0.5,1.0,1.0],
            "*41": [1.0,1.0,1.0,0.5,1.0],
            "*6":  [1.0,1.0,1.0,1.0,0.0],
            "*2xN":[1.0,1.0,1.0,2.0,1.0],
        },
        "activity_scores": {"*1":1.0,"*4":0.0,"*5":0.0,"*10":0.5,"*41":0.5,"*6":0.0,"*2xN":2.0},
        "diplotypes": {
            ("*1","*1"):"Normal Metabolizer",
            ("*1","*4"):"Intermediate Metabolizer",
            ("*1","*5"):"Intermediate Metabolizer",
            ("*1","*10"):"Intermediate Metabolizer",
            ("*1","*41"):"Intermediate Metabolizer",
            ("*4","*4"):"Poor Metabolizer",
            ("*4","*5"):"Poor Metabolizer",
            ("*5","*5"):"Poor Metabolizer",
            ("*4","*6"):"Poor Metabolizer",
            ("*5","*6"):"Poor Metabolizer",
            ("*6","*6"):"Poor Metabolizer",
            ("*10","*10"):"Intermediate Metabolizer",
            ("*41","*41"):"Intermediate Metabolizer",
            ("*4","*10"):"Poor Metabolizer",
            ("*1","*2xN"):"Ultrarapid Metabolizer",
            ("*2xN","*2xN"):"Ultrarapid Metabolizer",
            ("*4","*2xN"):"Normal Metabolizer",
        }
    }
}

def build_vector(gene_data, a1, a2):
    variants = gene_data["variants"]
    alleles  = gene_data["alleles"]
    scores   = gene_data["activity_scores"]
    v1 = alleles.get(a1, [1.0]*len(variants))
    v2 = alleles.get(a2, [1.0]*len(variants))
    vec = {}
    for i, var in enumerate(variants):
        vec[var] = (v1[i] + v2[i]) / 2.0
    vec["activity_score_total"] = scores.get(a1,1.0) + scores.get(a2,1.0)
    return vec

print("=" * 55)
print("CONSTRUCTION DATASET — Tables CPIC officielles")
print("=" * 55)

all_rows = []

for gene_name, gene_data in GENES.items():
    rows = []
    for (a1,a2), phenotype in gene_data["diplotypes"].items():
        vec = build_vector(gene_data, a1, a2)
        vec["gene"]      = gene_name
        vec["diplotype"] = a1 + "/" + a2
        vec["phenotype"] = phenotype
        rows.append(vec)
        if a1 != a2:
            vec2 = build_vector(gene_data, a2, a1)
            vec2["gene"]      = gene_name
            vec2["diplotype"] = a2 + "/" + a1
            vec2["phenotype"] = phenotype
            rows.append(vec2)
    df = pd.DataFrame(rows)
    path = OUTPUT_DIR + "/" + gene_name + "_dataset.csv"
    df.to_csv(path, index=False)
    print("")
    print(gene_name + " : " + str(len(rows)) + " exemples")
    for ph, cnt in df["phenotype"].value_counts().items():
        print("  " + str(ph) + " : " + str(cnt))
    all_rows.extend(rows)

df_all = pd.DataFrame(all_rows)
df_all.to_csv(OUTPUT_DIR + "/combined_dataset.csv", index=False)
print("")
print("=" * 55)
print("TOTAL : " + str(len(df_all)) + " exemples")
print("")
print("Distribution globale :")
for ph, cnt in df_all["phenotype"].value_counts().items():
    pct = cnt/len(df_all)*100
    print("  " + str(ph) + " : " + str(cnt) + " (" + str(round(pct,1)) + "%)")
print("")
print("Fichiers sauvegardes dans " + OUTPUT_DIR)