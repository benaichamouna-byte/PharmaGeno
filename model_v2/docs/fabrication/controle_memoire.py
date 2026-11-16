#!/usr/bin/env python3
"""controle_memoire.py : controle automatique du memoire avant depot.

Verifie, sur les fichiers *_MEMOIRE.md :
  1. renvois de section, de tableau, de figure, d'annexe et de formule : la cible existe-t-elle ;
  2. marqueurs restants ([a completer], TODO, XXX) ;
  3. citations (Auteur, annee) sans reference dans la bibliographie, et references jamais citees ;
  4. numerotation des tableaux et des figures : continue et dans l'ordre d'apparition ;
  5. tableaux et figures jamais appeles dans le texte.

Usage : python3 controle_memoire.py <dossier_md>
Sortie : une ligne par probleme ; "AUCUN PROBLEME" si tout va bien.
"""
import sys, os, re, unicodedata
from collections import OrderedDict

ORDRE = (["Chapitre1_v15_MEMOIRE.md", "Chapitre2_MEMOIRE.md", "Objectifs_v15_MEMOIRE.md"]
         + [f"Chapitre{i}_v15_MEMOIRE.md" for i in range(3, 10)]
         + ["Conclusion_v15_MEMOIRE.md"]
         + [f"Annexe{x}_v15_MEMOIRE.md" for x in "ABCDEFG"])

def sansaccent(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower()

def main():
    d = sys.argv[1]
    textes = OrderedDict()
    for f in ORDRE:
        p = os.path.join(d, f)
        if os.path.isfile(p):
            textes[f] = open(p, encoding="utf-8").read()
    tout = "\n".join(textes.values())
    pbs = []

    # --- cibles existantes
    sections = set(re.findall(r'^#{2,4} ((?:\d+\.\d+|[A-G]\.\d+))', tout, re.M))
    chapitres = set(re.findall(r'^## Chapitre (\d+)', tout, re.M))
    annexes = set(re.findall(r'^## Annexe ([A-G])', tout, re.M))
    tableaux, figures = [], []
    for f, t in textes.items():
        tableaux += re.findall(r'^Tableau ([A-G0-9]+\.\d+) ?:', t, re.M)
        figures += re.findall(r'^Figure ([A-G0-9]+\.\d+) ?:', t, re.M)
    formules = set(re.findall(r'\\qquad \(([A-G0-9]+\.\d+)\)', tout))

    # --- 1. renvois
    for f, t in textes.items():
        for m in re.finditer(r'sections? ((?:\d+\.\d+|[A-G]\.\d+))', t):
            if m.group(1) not in sections:
                pbs.append(f"{f} : renvoi vers la section {m.group(1)}, qui n'existe pas")
        for m in re.finditer(r'[Cc]hapitres? (\d+)', t):
            if m.group(1) not in chapitres:
                pbs.append(f"{f} : renvoi vers le chapitre {m.group(1)}, qui n'existe pas")
        for m in re.finditer(r'[Aa]nnexes? ([A-G])\b', t):
            if m.group(1) not in annexes:
                pbs.append(f"{f} : renvoi vers l'annexe {m.group(1)}, qui n'existe pas")
        for m in re.finditer(r'[Tt]ableaux? ([A-G0-9]+\.\d+)', t):
            if m.group(1) not in tableaux:
                pbs.append(f"{f} : renvoi vers le tableau {m.group(1)}, qui n'existe pas")
        for m in re.finditer(r'[Ff]igures? ([A-G0-9]+\.\d+)', t):
            if m.group(1) not in figures:
                pbs.append(f"{f} : renvoi vers la figure {m.group(1)}, qui n'existe pas")
        for m in re.finditer(r'formule \(([A-G0-9]+\.\d+)\)', t):
            if m.group(1) not in formules:
                pbs.append(f"{f} : renvoi vers la formule ({m.group(1)}), qui n'existe pas")

    # --- 2. marqueurs
    for f, t in textes.items():
        for m in re.finditer(r'\[à compléter[^\]]*\]|\bTODO\b|\bXXX\b|\bFIXME\b', t, re.I):
            pbs.append(f"{f} : marqueur restant « {m.group(0)[:40]} »")

    # --- 3. citations et bibliographie
    bib = open(os.path.join(d, "Bibliographie_v15_MEMOIRE.md"), encoding="utf-8").read()
    refs = [l[2:] for l in bib.split("\n") if l.startswith("- ")]
    cites = set()
    # (Auteur, annee) et (Auteur, annee ; Autre, annee), y compris dans les tableaux
    for m in re.finditer(r'(?<![\w,])([A-ZÉÀ][\w\'’.-]+(?: et [A-ZÉÀ][\w\'’.-]+| et al\.| Collaborative Group| Consortium)?),\s*(\d{4})[a-z]?(?=[\s;,)\]])', tout):
        nom = m.group(1).strip()
        if not re.match(r'^\d', nom):
            cites.add((nom, m.group(2)))
    for m in re.finditer(r'\b([A-ZÉÀ][\w\'’-]+(?: et [A-ZÉÀ][\w\'’-]+| et al\.)?)\s*\((\d{4})\)', tout):
        cites.add((m.group(1).strip(), m.group(2)))
    utilisees = set()
    for nom, annee in sorted(cites):
        premier = sansaccent(re.split(r'[ ,]', nom)[0])
        trouve = [r for r in refs if sansaccent(r).startswith(premier) and annee in r]
        if not trouve:
            trouve = [r for r in refs if premier in sansaccent(r) and annee in r]
        if trouve:
            utilisees.add(trouve[0])
        else:
            pbs.append(f"citation sans référence : ({nom}, {annee})")
    # references sans auteur ni annee (logiciels, organismes) : citees par leur nom
    NOMS = {"CDC,": ["GeT-RM"], "Pallets.": ["Flask"], "PharmCAT.": ["PharmCAT"],
            "PyPGx.": ["PyPGx"], "ReportLab.": ["ReportLab"],
            "WHO Collaborating": ["WHO Collaborating Centre for Drug Statistics Methodology"]}
    for r in refs:
        if r in utilisees:
            continue
        cle = next((k for k in NOMS if r.startswith(k)), None)
        if cle and any(n in tout for n in NOMS[cle]):
            continue
        pbs.append(f"référence jamais citée : {r[:70]}")

    # --- 4. numerotation continue, dans l'ordre d'apparition
    for nom, liste in (("tableau", tableaux), ("figure", figures)):
        groupes = {}
        for x in liste:
            groupes.setdefault(x.split(".")[0], []).append(int(x.split(".")[1]))
        for g, nums in groupes.items():
            if nums != list(range(1, len(nums) + 1)):
                pbs.append(f"numérotation des {nom}s du groupe {g} : {nums} au lieu de 1..{len(nums)}")

    # --- 5. tableaux et figures jamais appeles
    for x in tableaux:
        if not re.search(r'[Tt]ableaux? %s\b' % re.escape(x), tout):
            pbs.append(f"tableau {x} jamais appelé dans le texte")
    for x in figures:
        if not re.search(r'[Ff]igures? %s\b' % re.escape(x), tout):
            pbs.append(f"figure {x} jamais appelée dans le texte")

    for p in pbs:
        print(p)
    print("\n%d fichier(s) contrôlé(s), %d tableau(x), %d figure(s), %d référence(s)."
          % (len(textes), len(tableaux), len(figures), len(refs)))
    print("AUCUN PROBLEME" if not pbs else "%d PROBLEME(S)" % len(pbs))

if __name__ == "__main__":
    main()
