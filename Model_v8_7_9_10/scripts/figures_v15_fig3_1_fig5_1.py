#!/usr/bin/env python3
"""figures_v15_fig3_1_fig5_1.py : refait les figures 3.1 et 5.1 du memoire pour le corpus v15.

Pourquoi : les images de la copie zero v6 portaient des valeurs v14
  - figure 3.1 : repartition des classes du corpus v14 (232 664 lignes) ;
  - figure 5.1 : seuil d'abstention 0,9965 (v14) au lieu de 0,9981 (application v8u, corpus v15).
Les comptes de la figure 3.1 sont recalcules ici a partir du fichier du corpus, pas recopies.

Usage : python3 figures_v15_fig3_1_fig5_1.py <phenotype_drug_dataset_v15.csv> <dossier_fig>
"""
import sys, os, csv
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "Liberation Serif"
BLEU, ROUGE, ORANGE, GRIS, FOND = "#1f3a5f", "#b5483c", "#d9832b", "#8a9099", "#e8edf3"

def fr(n):  # 201273 -> "201 273" (espace fine insecable)
    return f"{n:,}".replace(",", " ")

def fig_3_1(corpus, sortie):
    with open(corpus, newline="") as f:
        r = csv.DictReader(f)
        col = next(c for c in r.fieldnames if c.lower() in ("action", "label", "classe", "action_code"))
        n = Counter(row[col] for row in r)
    ordre = ["STANDARD", "ADAPTER_DOSE", "EVITER", "SURVEILLER"]
    tot = sum(n.values())
    print("colonne", col, "| total", tot, "|", {k: n[k] for k in ordre})
    assert set(n) == set(ordre), f"classes inattendues : {set(n)}"
    fig, ax = plt.subplots(figsize=(9.3, 3.7), dpi=200)
    vals = [n[k] for k in ordre][::-1]
    ax.barh(ordre[::-1], vals, color=[GRIS, ORANGE, ROUGE, BLEU], height=0.8)
    for y, v in enumerate(vals):
        ax.text(v + tot * 0.007, y, f"{fr(v)} ({100*v/tot:.2f} %)".replace(".", ","), va="center", fontsize=13)
    ax.set_xlim(0, 265000)
    ax.set_xticks(range(0, 250001, 50000))
    ax.set_xticklabels([fr(x) for x in range(0, 250001, 50000)], fontsize=12)
    ax.tick_params(axis="y", labelsize=13)
    ax.set_xlabel("Nombre de lignes (profil, médicament)", fontsize=13)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(sortie); plt.close(fig)
    return tot

def fig_5_1(sortie):
    etapes = [
        ("Fichier VCF d'un patient (GRCh37 ou GRCh38)", "contrôles : tri, un seul échantillon, assemblage", False),
        ("Appel des génotypes : PyPGx 0.27.0 (18 gènes)", "+ saisie facultative de CYP2D6 et des 4 allèles HLA", True),
        ("Codage en valeurs numériques (34 entrées)", "gène non déterminé = « manquant », jamais « normal »", True),
        ("Réseau de profil : 189 médicaments × 4 actions", "probabilités calibrées ; abstention si confiance ≤ 0,9981", True),
        ("Avis de contrôle : XGBoost (statuts), Random Forest (information)", "+ règle CPIC, DPWG ou RNPGx affichée avec sa source", True),
        ("Statuts : ok, à vérifier, non déterminé, hors domaine", "catégories : à éviter, proposable, à vérifier, non évalué, règle seule", False),
        ("Sorties : page de résultats, PDF, alternatives de la même classe ATC4", "", False),
    ]
    fig, ax = plt.subplots(figsize=(7.9, 6.8), dpi=200)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    h, gap = 9.6, 4.4
    y = 97
    for i, (l1, l2, gris) in enumerate(etapes):
        y0 = y - h
        ax.add_patch(FancyBboxPatch((5, y0), 90, h, boxstyle="round,pad=0,rounding_size=1.2",
                                    lw=2, ec=BLEU, fc=FOND if gris else "white"))
        txt = l1 + ("\n" + l2 if l2 else "")
        ax.text(50, y0 + h / 2, txt, ha="center", va="center", fontsize=12.5, linespacing=1.45)
        if i < len(etapes) - 1:
            ax.annotate("", xy=(50, y0 - gap + 0.2), xytext=(50, y0 - 0.2),
                        arrowprops=dict(arrowstyle="-|>", color=BLEU, lw=2.2, mutation_scale=16))
        y = y0 - gap
    fig.savefig(sortie, bbox_inches="tight"); plt.close(fig)

if __name__ == "__main__":
    corpus, dossier = sys.argv[1], sys.argv[2]
    os.makedirs(dossier, exist_ok=True)
    tot = fig_3_1(corpus, os.path.join(dossier, "fig_3_1.png"))
    fig_5_1(os.path.join(dossier, "fig_5_1.png"))
    print("ecrit :", os.path.join(dossier, "fig_3_1.png"), os.path.join(dossier, "fig_5_1.png"), "| lignes", tot)
