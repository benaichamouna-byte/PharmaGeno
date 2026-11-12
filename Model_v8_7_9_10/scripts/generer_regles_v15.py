#!/usr/bin/env python3
"""
generer_regles_v15.py — construit regles_v15_monogene.csv et regles_v15_multigene.csv
a partir de regles_v14_monogene.csv et regles_v13_multigene.csv, SANS les modifier.

Corrections appliquees (voir model_v2/docs/regles_corrigees_v15.md) :
  R1  warfarine x VKORC1 (DPWG PA166182841)           : 3 regles mono-gene ajoutees
  R2a warfarine x CYP2C9 valeur 0.75 -> STANDARD      : diplotype *1/*2, "NO action" (DPWG PA166182842)
  R2b siponimod x CYP2C9 valeur 0.75 -> STANDARD      : diplotype *1/*2, "NO action" (DPWG PA166211021)
  R2c warfarine et siponimod x CYP2C9 valeur 1.0      : regles ajoutees (metaboliseur normal)
  R4  grille bi-genique TPMT x NUDT15                 : 27 regles multi-gene (CPIC 2025)
  R3/R5 : aucune ligne (G6PD variable et primaquine exclus = regles conditionnelles ;
          fluvastatine = correction de priorite dans le moteur)

Usage :
  python3 -I generer_regles_v15.py DOSSIER_DATA DOSSIER_SOURCES_V15
"""
import sys, os, re, json
import pandas as pd

D   = sys.argv[1].rstrip("/") + "/"
SRC = sys.argv[2].rstrip("/") + "/"

MONO_IN  = D + "regles_v14_monogene.csv"
MULTI_IN = D + "regles_v13_multigene.csv"
MONO_OUT = D + "regles_v15_monogene.csv"
MULTI_OUT= D + "regles_v15_multigene.csv"
GRILLES  = SRC + "grilles_pharmcat_v15.md"

for f in (MONO_IN, MULTI_IN, GRILLES):
    if not os.path.exists(f): sys.exit("FICHIER ABSENT : " + f)

m = pd.read_csv(MONO_IN, low_memory=False)
x = pd.read_csv(MULTI_IN, low_memory=False)
m0, x0 = len(m), len(x)
print(f"Entree  : mono-gene {m0} regles | multi-gene {x0} regles")

if "decision_v15" not in m.columns: m["decision_v15"] = ""
if "decision_v15" not in x.columns: x["decision_v15"] = ""

journal = []

# ---------------------------------------------------------------- R2a / R2b
TXT_NO_ACTION = "NO action is required for this gene-drug interaction."
for med, fich in [("warfarin", "PA166182842.json"), ("siponimod", "PA166211021.json")]:
    sel = (m.gene == "CYP2C9") & (m.medicament == med) & (m.valeur == 0.75)
    n = int(sel.sum())
    if n != 1:
        sys.exit(f"ATTENDU 1 ligne CYP2C9=0.75 pour {med}, TROUVE {n}")
    anc = m.loc[sel, "action"].iloc[0]
    m.loc[sel, "action"] = "STANDARD"
    m.loc[sel, "phenotype"] = "CYP2C9*1/*2"
    m.loc[sel, "recommandation"] = TXT_NO_ACTION
    m.loc[sel, "decision_v15"] = (
        "v15 R2 : la DPWG definit par diplotype. A la valeur 0.75 (score d activite 1.5) "
        "le diplotype *1/*2 domine et recoit 'NO action is required'. "
        f"Corrige {anc} -> STANDARD. Residu documente : les diplotypes *1/autre-allele-deficient "
        "(IM other, rares) restent confondus a cette valeur.")
    journal.append(f"MODIF  CYP2C9=0.75 {med:10s} {anc} -> STANDARD")

# ---------------------------------------------------------------- R2c
TXT_NM = {
 "warfarin":  "Metaboliseur normal (CYP2C9*1/*1) : non cite comme sous-groupe concerne par la "
              "DPWG, posologie generale de l etiquette.",
 "siponimod": "Metaboliseur normal (CYP2C9*1/*1) : non cite comme sous-groupe concerne par la "
              "DPWG, posologie generale de l etiquette."}
for med, fich in [("warfarin", "PA166182842.json"), ("siponimod", "PA166211021.json")]:
    if ((m.gene == "CYP2C9") & (m.medicament == med) & (m.valeur == 1.0)).any():
        journal.append(f"DEJA   CYP2C9=1.0 {med} present, rien a ajouter"); continue
    base = m[(m.gene == "CYP2C9") & (m.medicament == med)].iloc[0].copy()
    base["valeur"] = 1.0; base["action"] = "STANDARD"
    base["phenotype"] = "CYP2C9 Normal Metabolizer"
    base["recommandation"] = TXT_NM[med]
    base["decision_v15"] = ("v15 R2c : valeur 1.0 absente du v14, un profil CYP2C9 normal ne "
                            "recevait aucune regle pour ce medicament. Ajoutee en STANDARD "
                            "(principe H-FDA-1 : valeur non citee -> posologie generale).")
    m = pd.concat([m, base.to_frame().T], ignore_index=True)
    journal.append(f"AJOUT  CYP2C9=1.0 {med:10s} STANDARD")

# ---------------------------------------------------------------- R1
VK = [(0.0, "ADAPTER_DOSE", "VKORC1 rs9923231 homozygote variant (-1639 AA)",
       "1. use 60% of the standard initial dose. The genotype-specific initial dose and "
       "maintenance dose can be calculated using an algorithm, as used in EU-PACT. From day 6 "
       "on the standard algorithm without genotype information can be used to calculate the dose."),
      (0.5, "STANDARD", "VKORC1 rs9923231 heterozygote (-1639 AG)",
       "NO action is needed for this gene-drug interaction"),
      (1.0, "STANDARD", "VKORC1 reference",
       "Genotype de reference : non cite comme sous-groupe concerne, posologie generale.")]
modele = m[(m.gene == "VKORC1") & (m.medicament == "fluindione")]
if modele.empty: sys.exit("Modele VKORC1 introuvable (fluindione)")
modele = modele.iloc[0]
for val, act, phen, txt in VK:
    if ((m.gene == "VKORC1") & (m.medicament == "warfarin") & (m.valeur == val)).any():
        journal.append(f"DEJA   VKORC1={val} warfarin present"); continue
    r = modele.copy()
    r["valeur"] = val; r["medicament"] = "warfarin"; r["action"] = act
    r["phenotype"] = phen; r["recommandation"] = txt
    r["source"] = "DPWG"; r["fichier"] = "PA166182841.json"
    r["decision_v15"] = ("v15 R1 : directive DPWG warfarine-VKORC1 presente dans les sources du "
                         "projet et deja codee pour l acenocoumarol, la phenprocoumone et la "
                         "fluindione, mais absente pour la warfarine. Omission corrigee.")
    m = pd.concat([m, r.to_frame().T], ignore_index=True)
    journal.append(f"AJOUT  VKORC1={val} warfarin  {act}")

# ---------------------------------------------------------------- R4
def textes_thiopurines():
    t = open(GRILLES, encoding="utf-8").read()
    blocs = re.split(r"\n={70,}\n", t)
    PH = {1.0: "Normal Metabolizer", 0.5: "Intermediate Metabolizer", 0.0: "Poor Metabolizer"}
    out = {}
    for med, pa in [("azathioprine","PA166104933"),("mercaptopurine","PA166104945"),
                    ("thioguanine","PA166104965")]:
        b = next((y for y in blocs if "## " + pa + " " in y), "")
        if not b: sys.exit("Bloc absent dans grilles_pharmcat_v15.md : " + pa)
        d = {}
        for r in re.finditer(r"CLE    : (.+?)\n  FORCE  : (.*?)\n(?:  PORTEE : .*?\n)?"
                             r"  TEXTE  : (.+?)(?=\n\n|\n  CLE|\Z)", b, re.S):
            try: k = json.loads(r.group(1).strip())
            except Exception: continue
            kk = {g: v for e in k for g, v in e.items()}
            d[(kk.get("TPMT"), kk.get("NUDT15"))] = (r.group(2).strip(),
                                                     " ".join(r.group(3).split()))
        for vt, pt in PH.items():
            for vn, pn in PH.items():
                if (pt, pn) in d: out[(med, vt, vn)] = (pt, pn) + d[(pt, pn)]
    return out

# Grille verifiee a la main sur les textes CPIC 2025 (voir regles_corrigees_v15.md § 4).
# Le classement automatique du texte est volontairement ecarte : il confondait
# "For malignancy ... For nonmalignancy: consider alternative" avec un EVITER simple.
#   azathioprine   : un seul texte en metaboliseur lent -> "Consider alternative
#                    nonthiopurine immunosuppressant therapy" = EVITER
#   mercaptopurine : texte a deux branches selon l indication ; branche malignite
#                    retenue (le webtool ignore l indication) = ADAPTER_DOSE
#   thioguanine    : "drastically reduced ... 10-fold" en toutes circonstances = ADAPTER_DOSE
def action_thio(med, vt, vn, txt):
    if vt == 1.0 and vn == 1.0:
        return "STANDARD"
    if med == "azathioprine" and (vt == 0.0 or vn == 0.0):
        return "EVITER"
    return "ADAPTER_DOSE"

TH = textes_thiopurines()
modele_x = x.iloc[0]
n_th = 0
for (med, vt, vn), (pt, pn, force, txt) in sorted(TH.items()):
    if ((x.gene_a == "TPMT") & (x.gene_b == "NUDT15") & (x.medicament == med)
        & (x.valeur_a == vt) & (x.valeur_b == vn)).any():
        continue
    act = action_thio(med, vt, vn, txt)
    r = modele_x.copy()
    r["gene_a"], r["valeur_a"] = "TPMT", vt
    r["gene_b"], r["valeur_b"] = "NUDT15", vn
    r["medicament"], r["action"] = med, act
    r["source"] = "CPIC"
    r["phenotype_a"], r["phenotype_b"] = "TPMT " + pt, "NUDT15 " + pn
    r["recommandation"] = txt
    r["fichier"] = {"azathioprine":"PA166104933","mercaptopurine":"PA166104945",
                    "thioguanine":"PA166104965"}[med]
    r["ambigu"] = False; r["conditionnel"] = False
    r["decision_v15"] = ("v15 R4 : la directive CPIC 2025 porte sur TPMT et NUDT15 conjointement. "
                         "Grille bi-genique ajoutee ; elle prime sur les regles mono-gene des memes "
                         "genes (principe de specificite). Force CPIC : " + force + ".")
    x = pd.concat([x, r.to_frame().T], ignore_index=True)
    n_th += 1
journal.append(f"AJOUT  grille TPMT x NUDT15 : {n_th} regles multi-gene")

# ---------------------------------------------------------------- sortie
m.to_csv(MONO_OUT, index=False)
x.to_csv(MULTI_OUT, index=False)

print("\n--- JOURNAL DES CORRECTIONS ---")
for j in journal: print("  " + j)
print(f"\nSortie  : mono-gene {m0} -> {len(m)} (+{len(m)-m0}) | multi-gene {x0} -> {len(x)} (+{len(x)-x0})")
print(f"Ecrits  : {MONO_OUT}\n          {MULTI_OUT}")
print(f"Intacts : {MONO_IN}\n          {MULTI_IN}")

print("\n--- CONTROLE : regles warfarine et siponimod apres correction ---")
c = m[((m.gene.isin(["CYP2C9","VKORC1"])) & (m.medicament.isin(["warfarin","siponimod"])))]
print(c[["gene","valeur","medicament","action","phenotype"]].sort_values(
    ["medicament","gene","valeur"]).to_string(index=False))

print("\n--- CONTROLE : grille thiopurines ---")
g = x[(x.gene_a=="TPMT") & (x.gene_b=="NUDT15")]
print(g.pivot_table(index=["valeur_a","valeur_b"], columns="medicament",
                    values="action", aggfunc="first").to_string())
