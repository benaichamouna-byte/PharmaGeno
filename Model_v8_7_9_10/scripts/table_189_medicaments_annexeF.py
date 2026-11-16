#!/usr/bin/env python3
"""table_189_medicaments_annexeF.py : produit le tableau de l'annexe F du memoire.

Une ligne par medicament du corpus v15 : classe ATC de niveau 4, gene(s) de la regle,
nombre de lignes du corpus et actions distinctes rencontrees. Tout est lu dans les
fichiers du projet, rien n'est saisi a la main.

Usage : python3 table_189_medicaments_annexeF.py <dossier_Model_v8_7_9_10> <sortie.md>
"""
import sys, os, csv
from collections import defaultdict

ACTION_COURTE = {"STANDARD": "S", "ADAPTER_DOSE": "A", "SURVEILLER": "V", "EVITER": "E"}
ORDRE = ["STANDARD", "ADAPTER_DOSE", "SURVEILLER", "EVITER"]

def fr(n):
    return f"{n:,}".replace(",", " ")

def main():
    base, sortie = sys.argv[1], sys.argv[2]
    d = lambda *p: os.path.join(base, "data", *p)

    lignes, actions = defaultdict(int), defaultdict(set)
    with open(d("corpus_v15", "phenotype_drug_dataset_v15.csv"), newline="") as f:
        for row in csv.DictReader(f):
            med = row["drug"]
            lignes[med] += 1
            actions[med].add(row["action"])

    genes = defaultdict(set)
    with open(d("regles_v15_monogene.csv"), newline="") as f:
        for row in csv.DictReader(f):
            genes[row["medicament"]].add(row["gene"])
    with open(d("regles_v15_multigene.csv"), newline="") as f:
        for row in csv.DictReader(f):
            genes[row["medicament"]].update([row["gene_a"], row["gene_b"]])

    atc = {}
    # table employee par l'application v8u (app_pharmageno_v8u.py)
    with open(d("atc_mapping_medicaments_v14.csv"), newline="") as f:
        for row in csv.DictReader(f):
            codes = [c.strip() for c in (row["atc_codes"] or "").split(";") if c.strip()]
            # niveau 4 = les 5 premiers caracteres du code ATC (ex. B01AA03 -> B01AA)
            n4 = sorted({c[:5] for c in codes if len(c) >= 5})
            atc[row["medicament"]] = ", ".join(n4)

    meds = sorted(lignes)
    out = ["## Annexe F : Les 189 médicaments du corpus v15\n",
           "Ce tableau est produit par programme à partir des fichiers du corpus et des tables de règles ; "
           "aucune valeur n'y est saisie à la main. La colonne « ATC4 » donne le ou les sous-groupes "
           "anatomique, thérapeutique et chimique de niveau 4 du médicament ; une case vide signale un "
           "médicament dont le code n'a pas été retrouvé dans la table employée (section C.5). La colonne "
           "« Gènes » liste les gènes des règles qui s'appliquent au médicament, un médicament à plusieurs "
           "gènes portant une règle combinée (section C.3). La colonne « Actions » donne les classes "
           "rencontrées dans le corpus : S pour dose standard, A pour adapter la dose, V pour surveiller "
           "et E pour éviter ; un médicament dont la colonne ne porte qu'une lettre a la même action pour "
           "tous les profils du corpus.\n",
           "::: {custom-style=\"LegendeTableau\"}",
           f"Tableau F.1 : Les {len(meds)} médicaments du corpus v15, leur sous-groupe ATC4, "
           "les gènes de leurs règles, leur nombre de lignes et les actions rencontrées",
           ":::\n", "", "| Médicament | ATC4 | Gènes | Lignes | Actions |", "| --- | --- | --- | --- | --- |"]
    for m in meds:
        g = ", ".join(sorted(genes.get(m, []))).replace("*", "\\*")
        a = " ".join(ACTION_COURTE[x] for x in ORDRE if x in actions[m])
        out.append(f"| {m} | {atc.get(m, '')} | {g} | {fr(lignes[m])} | {a} |")
    out.append("")
    open(sortie, "w", encoding="utf-8").write("\n".join(out))
    print(len(meds), "medicaments |", fr(sum(lignes.values())), "lignes |",
          sum(1 for m in meds if not atc.get(m)), "sans code ATC |",
          sum(1 for m in meds if len(genes.get(m, [])) > 1), "a plusieurs genes")

if __name__ == "__main__":
    main()
