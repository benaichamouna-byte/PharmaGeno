#!/usr/bin/env python3
"""compter_pages.py : page de debut de chaque partie du memoire dans le PDF, et nombre de pages.

Usage : python3 compter_pages.py memoire.pdf
Une partie commence a la page dont la premiere ligne de texte commence par son titre.
"""
import sys, subprocess

MARQUES = ["Remerciements", "Résumé", "Abstract", "Sommaire", "Liste des figures", "Liste des tableaux",
           "Liste des abréviations", "Chapitre 1 :", "Chapitre 2 :", "Objectifs", "Chapitre 3 :", "Chapitre 4 :",
           "Chapitre 5 :", "Chapitre 6 :", "Chapitre 7 :", "Chapitre 8 :", "Chapitre 9 :", "Conclusion",
           "Références bibliographiques", "Annexe A :", "Annexe B :", "Annexe C :", "Annexe D :", "Annexe E :",
           "Annexe F :", "Annexe G :", "Annexe H :"]

def main():
    pdf = sys.argv[1]
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    n = int(next(l.split()[-1] for l in info.splitlines() if l.startswith("Pages")))
    premieres = []
    for p in range(1, n + 1):
        t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", pdf, "-"],
                           capture_output=True, text=True).stdout
        lignes = [l.strip() for l in t.splitlines() if l.strip()]
        premieres.append(lignes[:2])
    debut, depart = {}, 0
    for m in MARQUES:
        for i in range(depart, n):
            if any(x.startswith(m) for x in premieres[i]):
                debut[m] = i + 1; depart = i; break
    trouves = [m for m in MARQUES if m in debut]
    for k, m in enumerate(trouves):
        fin = (debut[trouves[k + 1]] - 1) if k + 1 < len(trouves) else n
        print(f"{debut[m]:>4} - {fin:>4}  ({fin - debut[m] + 1:>2} p.)  {m}")
    print("pages :", n)

if __name__ == "__main__":
    main()
