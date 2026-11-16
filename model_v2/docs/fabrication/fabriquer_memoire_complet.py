#!/usr/bin/env python3
"""fabriquer_memoire_complet.py : assemble le memoire complet v15 en .docx puis .pdf.

Ordre (formulaire ISBST) :
  page de garde (reprise de la copie zero v6, logos compris)
  -> Remerciements, Resume, Abstract (Front_matter_v15_MEMOIRE.md)
  -> Sommaire, Liste des figures, Liste des tableaux, Liste des abreviations
  -> Chapitre 1 -> Chapitre 2 -> Objectifs -> Chapitres 3 a 9
  -> References -> Annexe A -> Annexe B

Usage : python3 fabriquer_memoire_complet.py <dossier_md> <dossier_contenant_fig> <reference_v6.docx> <sortie_sans_extension>
  <dossier_contenant_fig> est le dossier qui contient le sous-dossier fig/ (images appelees fig/xxx.png).

Les champs (sommaire, listes) sont remplis par LibreOffice au moment de l'export PDF
(script mettre_a_jour_index.py) ; dans Word, Ctrl+A puis F9 les remet a jour.
"""
import sys, os, subprocess, copy, re
import docx
from docxcompose.composer import Composer

ORDRE = ["Front_matter_v15_MEMOIRE.md", "@LISTES", "Chapitre1_v15_MEMOIRE.md", "Chapitre2_MEMOIRE.md",
         "Objectifs_v15_MEMOIRE.md"] + [f"Chapitre{i}_v15_MEMOIRE.md" for i in range(3, 10)] + \
        ["Bibliographie_v15_MEMOIRE.md", "AnnexeA_v15_MEMOIRE.md", "AnnexeB_v15_MEMOIRE.md"]

ABREV = [("ATC", "Anatomical Therapeutic Chemical (classification des médicaments)"),
         ("AUROC", "Aire sous la courbe ROC (area under the ROC curve)"),
         ("CDC", "Centers for Disease Control and Prevention"),
         ("CPIC", "Clinical Pharmacogenetics Implementation Consortium"),
         ("CPNDS", "Canadian Pharmacogenomics Network for Drug Safety"),
         ("DL", "Deep Learning (apprentissage profond)"),
         ("DPWG", "Dutch Pharmacogenetics Working Group"),
         ("ECE", "Erreur de calibration attendue (expected calibration error)"),
         ("EMA", "European Medicines Agency (Agence européenne des médicaments)"),
         ("F1", "Moyenne harmonique de la précision et du rappel ; F1 macro : moyenne non pondérée sur les quatre classes"),
         ("FDA", "Food and Drug Administration (États-Unis)"),
         ("FiLM", "Feature-wise Linear Modulation"),
         ("GeT-RM", "Genetic Testing Reference Material Coordination Program (CDC)"),
         ("HCSC", "Health Canada–Santé Canada"),
         ("HLA", "Human Leukocyte Antigen (antigènes des leucocytes humains)"),
         ("IC 95 %", "Intervalle de confiance à 95 %"),
         ("IWPC", "International Warfarin Pharmacogenetics Consortium"),
         ("JSON", "JavaScript Object Notation (format de fichier de données)"),
         ("OR", "Odds ratio (rapport de cotes)"),
         ("PREPARE", "Preemptive Pharmacogenomic Testing for Preventing Adverse Drug Reactions"),
         ("RNPGx", "Réseau national de pharmacogénétique (France)"),
         ("ROC", "Receiver operating characteristic"),
         ("RQ", "Question de recherche"),
         ("VCF", "Variant Call Format"),
         ("XGBoost", "eXtreme Gradient Boosting")]

def champ(instr, texte):
    return ('```{=openxml}\n<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r><w:t>{texte}</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>\n```\n')

def saut():
    return '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n'

def titre_front(t):
    return f'::: {{custom-style="TitreFront"}}\n{t}\n:::\n'

def listes(intro_abrev):
    s = saut() + titre_front("Sommaire") + "\n" + champ('TOC \\o "1-2" \\h \\z \\u', "Mettre à jour le champ (F9).")
    s += saut() + titre_front("Liste des figures") + "\n" + champ('TOC \\h \\z \\t "LegendeFigure,1"', "Mettre à jour le champ (F9).")
    s += saut() + titre_front("Liste des tableaux") + "\n" + champ('TOC \\h \\z \\t "LegendeTableau,1"', "Mettre à jour le champ (F9).")
    s += saut() + titre_front("Liste des abréviations") + "\n" + intro_abrev + "\n\n| Abréviation | Signification |\n| --- | --- |\n"
    s += "".join(f"| {a} | {b} |\n" for a, b in ABREV)
    return s + "\n"

def couverture(ref, sortie):
    """Garde la page de garde de la copie zero v6 : tout le corps jusqu'au paragraphe CouvAnnee inclus."""
    d = docx.Document(ref)
    body = d.element.body
    garder, fin = True, False
    for el in list(body.iterchildren()):
        tag = el.tag.split('}')[1]
        if tag == "sectPr":
            continue
        if fin:
            body.remove(el); continue
        if tag == "p":
            p = docx.text.paragraph.Paragraph(el, d)
            if p.style.name == "CouvAnnee":
                fin = True
    d.save(sortie)

def main():
    dmd, dfig, ref, sortie = sys.argv[1:5]
    d6 = docx.Document(ref)
    intro = next(p.text for p in d6.paragraphs if p.text.startswith("Les symboles de gènes"))
    parts = []
    for f in ORDRE:
        if f == "@LISTES":
            parts.append(listes(intro)); continue
        txt = open(os.path.join(dmd, f), encoding="utf-8").read()
        parts.append(txt if f.startswith("Front") else txt)
    md = "\n\n".join(parts)
    src = sortie + "_source.md"
    open(src, "w", encoding="utf-8").write(md)
    corps = sortie + "_corps.docx"
    cmd = ["pandoc", src, "-o", corps, f"--reference-doc={ref}", "--resource-path", dfig,
           "--shift-heading-level-by=-1",
           "--from", "markdown+pipe_tables+raw_attribute+fenced_divs+tex_math_dollars", "--to", "docx"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr); sys.exit(1)
    if r.stderr.strip(): print("pandoc :", r.stderr.strip()[:1500])
    couv = sortie + "_couverture.docx"
    couverture(ref, couv)
    maitre = docx.Document(couv)
    # pas de saut ajoute : le style TitreFront de « Remerciements » commence deja une page
    comp = Composer(maitre)
    comp.append(docx.Document(corps))
    comp.save(sortie + ".docx")
    for f in (couv, corps): os.remove(f)
    print("ecrit", sortie + ".docx", os.path.getsize(sortie + ".docx"), "octets")

if __name__ == "__main__":
    main()
