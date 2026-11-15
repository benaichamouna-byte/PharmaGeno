# -*- coding: utf-8 -*-
"""Recalcul de l'audit de parenté du 5 nov. 2026 (audit_parente_v1.py perdu).
Méthode documentée (Amendement 1 v14 + Regle_retrait_apparentes_profils_finaux_5nov2026) :
graphe sur les 3202 individus du pedigree, arêtes enfant-père et enfant-mère ;
deux profils du corpus (1379) sont apparentés s'ils sont dans la même composante.
Acceptation UNIQUEMENT si l'on retrouve exactement :
187 paires, aucun groupe > 2, 1 paire parent-enfant, 185 couples via enfant absent,
1 paire par alliance, 372 profils ; 34 paires final/dev, 34 profils dev distincts,
34 profils finaux concernés, 2 groupes à deux finaux (HG02678/HG02679, HG01953/HG01954)."""
import csv, itertools, sys
from collections import defaultdict

PED = "data/1kGP_3202_pedigree.txt"
CORPUS = "Model_v8_7_9_10/data/corpus_v15/phenotype_drug_dataset_v15.csv"
FINAL = "Model_v8_7_9_10/data/profils_ensemble_final_v1.txt"

# 1. pedigree
pere, mere = {}, {}
with open(PED) as f:
    next(f)
    for ln in f:
        s, fa, mo, _ = ln.split()
        if fa != "0": pere[s] = fa
        if mo != "0": mere[s] = mo

# union-find sur toutes les personnes du pedigree
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb
for d in (pere, mere):
    for c, p in d.items(): union(c, p)

# 2. profils du corpus (1379)
profils = set()
with open(CORPUS) as f:
    r = csv.reader(f)
    head = next(f).rstrip("\n").split(",")
    i_sid = head.index("sample_id")
    for row in csv.reader(f):
        profils.add(row[i_sid])
print("profils corpus :", len(profils))

finaux = set(l.strip() for l in open(FINAL) if l.strip() and not l.startswith("#"))
print("profils finaux :", len(finaux), "| dev :", len(profils - finaux))

# 3. groupes d'apparentés dans le corpus
groupes = defaultdict(list)
for s in sorted(profils):
    if s in parent or s in pere or s in mere:
        groupes[find(s)].append(s)
    else:
        groupes["singleton_" + s].append(s)
multi = {k: v for k, v in groupes.items() if len(v) > 1}
paires = []
for v in multi.values():
    paires += list(itertools.combinations(sorted(v), 2))
print("groupes >1 :", len(multi), "| taille max :", max((len(v) for v in multi.values()), default=0))
print("paires :", len(paires), "| profils impliqués :", sum(len(v) for v in multi.values()))

# 4. typage des paires
def type_paire(a, b):
    if pere.get(a) == b or mere.get(a) == b or pere.get(b) == a or mere.get(b) == a:
        return "parent-enfant"
    if (pere.get(a) and pere.get(a) == pere.get(b)) or (mere.get(a) and mere.get(a) == mere.get(b)):
        return "fratrie"
    # couple : parents d'un même enfant du pedigree
    enfants_a = {c for c in pere if pere[c] == a} | {c for c in mere if mere[c] == a}
    enfants_b = {c for c in pere if pere[c] == b} | {c for c in mere if mere[c] == b}
    if enfants_a & enfants_b: return "couple (enfant absent)"
    return "alliance (chaîne)"
types = defaultdict(int)
for a, b in paires: types[type_paire(a, b)] += 1
for t, n in sorted(types.items()): print("  ", t, ":", n)

# 5. paires final/développement
fd = [(a, b) for a, b in paires if (a in finaux) != (b in finaux)]
devs = sorted({a if a not in finaux else b for a, b in fd})
fins = sorted({a if a in finaux else b for a, b in fd})
print("paires final/dev :", len(fd), "| dev distincts :", len(devs), "| finaux concernés :", len(fins))

# groupes contenant deux finaux
deux_fin = [sorted(set(v) & finaux) for v in multi.values() if len(set(v) & finaux) == 2]
print("groupes à deux finaux :", deux_fin)

# lignes des 34 dev dans le corpus v15
lignes = defaultdict(int)
with open(CORPUS) as f:
    head = next(f).rstrip("\n").split(",")
    i_sid = head.index("sample_id")
    tot = 0
    for row in csv.reader(f):
        sid = row[i_sid]
        if sid not in finaux: tot += 1
        if sid in devs: lignes[sid] += 1
print("lignes des dev apparentés (v15) :", sum(lignes.values()), "sur", tot, "lignes dev")

with open("audit/apparentes_des_profils_finaux_a_retirer_v15.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["profil_developpement"])
    for d in devs: w.writerow([d])
with open("audit/paires_final_dev_v15.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["profil_final", "profil_developpement"])
    for a, b in sorted(fd):
        fi, de = (a, b) if a in finaux else (b, a)
        w.writerow([fi, de])
print("écrit : audit/apparentes_des_profils_finaux_a_retirer_v15.csv")
