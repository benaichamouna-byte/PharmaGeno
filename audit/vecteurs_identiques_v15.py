# -*- coding: utf-8 -*-
"""Profils finaux dont le vecteur d'entrée (39 colonnes gènes) est identique
à celui d'au moins un profil de développement — strate documentée le 5 nov."""
import csv
CORPUS = "Model_v8_7_9_10/data/corpus_v15/phenotype_drug_dataset_v15.csv"
FINAL = "Model_v8_7_9_10/data/profils_ensemble_final_v1.txt"
finaux = set(l.strip() for l in open(FINAL) if l.strip())
vec = {}
with open(CORPUS) as f:
    head = next(f).rstrip("\n").split(",")
    i_sid = head.index("sample_id")
    genes = head[:i_sid - 0][:head.index("sample_id")]
    n_g = head.index("sample_id")  # colonnes 0..n_g-1 = gènes
    for row in csv.reader(f):
        sid = row[i_sid]
        if sid not in vec: vec[sid] = tuple(row[:n_g])
print("colonnes gènes :", n_g, "| profils :", len(vec))
dev_vecs = {}
for s, v in vec.items():
    if s not in finaux: dev_vecs.setdefault(v, []).append(s)
ident = {s: dev_vecs[v] for s, v in vec.items() if s in finaux and v in dev_vecs}
print("finaux à vecteur identique à un dev :", len(ident))
for s, ds in sorted(ident.items()): print("  ", s, "==", ",".join(sorted(ds)))
