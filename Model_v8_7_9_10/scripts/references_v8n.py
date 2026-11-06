# references_v8n.py : liste des références affichées dans l'application v8n (page « Références » et accueil).
# RÈGLE : chaque entrée a été vérifiée le 29 oct. 2026 (titre, auteurs, revue, année, DOI lus sur Crossref ou sur la page de l'éditeur/du dépôt) ; aucune référence n'est écrite de mémoire.
# Une entrée sans DOI renvoie à la page officielle du projet. Ne pas ajouter de référence sans la vérifier de la même façon.

def _doi(d): return 'https://doi.org/' + d

REFERENCES = [
    dict(groupe="Directives pharmacogénétiques (source des règles affichées à côté du DL)", items=[
        dict(texte="Relling MV, Klein TE. CPIC: Clinical Pharmacogenetics Implementation Consortium of the Pharmacogenomics Research Network. Clin Pharmacol Ther 2011;89(3):464-467.",
             lien=_doi('10.1038/clpt.2010.279'), etiquette='doi:10.1038/clpt.2010.279'),
        dict(texte="CPIC : directives par gène et médicament (site officiel ; la page redirige vers ClinPGx).",
             lien='https://cpicpgx.org/guidelines/', etiquette='cpicpgx.org/guidelines'),
        dict(texte="Swen JJ, Nijenhuis M, de Boer A, et al. Pharmacogenetics: from bench to byte, an update of guidelines (DPWG). Clin Pharmacol Ther 2011;89:662-673.",
             lien=_doi('10.1038/clpt.2011.34'), etiquette='doi:10.1038/clpt.2011.34'),
        dict(texte="Abdullah-Koolmees H, van Keulen AM, Nijenhuis M, et al. Pharmacogenetics guidelines: overview and comparison of the DPWG, CPIC, CPNDS, and RNPGx guidelines. Front Pharmacol 2021;11:595219.",
             lien=_doi('10.3389/fphar.2020.595219'), etiquette='doi:10.3389/fphar.2020.595219'),
        dict(texte="Whirl-Carrillo M, Huddart R, Gong L, et al. An evidence-based framework for evaluating pharmacogenomics knowledge for personalized medicine (PharmGKB, aujourd'hui ClinPGx). Clin Pharmacol Ther 2021;110:563-572.",
             lien=_doi('10.1002/cpt.2350'), etiquette='doi:10.1002/cpt.2350'),
    ]),
    dict(groupe="Lecture du génome du patient (VCF → génotype → phénotype)", items=[
        dict(texte="Lee S-b, Shin J-Y, Kwon N-J, et al. ClinPharmSeq: a targeted sequencing panel for clinical pharmacogenetics implementation. PLoS ONE 2022;17:e0272129 (référence principale demandée par les auteurs de PyPGx 0.27.0).",
             lien=_doi('10.1371/journal.pone.0272129'), etiquette='doi:10.1371/journal.pone.0272129'),
        dict(texte="Lee S-b, et al. Calling star alleles with Stargazer in 28 pharmacogenes with whole genome sequences. Clin Pharmacol Ther 2019 (outil dont PyPGx est issu).",
             lien=_doi('10.1002/cpt.1552'), etiquette='doi:10.1002/cpt.1552'),
        dict(texte="PyPGx, logiciel libre de pharmacogénomique (S.-b. Lee), version 0.27.0 utilisée.",
             lien='https://github.com/sbslee/pypgx', etiquette='github.com/sbslee/pypgx'),
        dict(texte="Sangkuhl K, Whirl-Carrillo M, Whaley RM, et al. Pharmacogenomics Clinical Annotation Tool (PharmCAT). Clin Pharmacol Ther 2020;107(1):203-210 (tables génotype → phénotype CPIC).",
             lien=_doi('10.1002/cpt.1568'), etiquette='doi:10.1002/cpt.1568'),
    ]),
    dict(groupe="Données d'entraînement et classification des médicaments", items=[
        dict(texte="The 1000 Genomes Project Consortium, Auton A, Abecasis GR, et al. A global reference for human genetic variation. Nature 2015;526(7571):68-74 (profils génétiques réels des personnes utilisées pour l'entraînement et les tests).",
             lien=_doi('10.1038/nature15393'), etiquette='doi:10.1038/nature15393'),
        dict(texte="Classification anatomique, thérapeutique et chimique (ATC) : WHO Collaborating Centre, Oslo (classes de médicaments interchangeables et spécialités).",
             lien='https://www.whocc.no/atc_ddd_index/', etiquette='whocc.no/atc_ddd_index'),
    ]),
    dict(groupe="Modèles de comparaison et mesures de performance", items=[
        dict(texte="Chen T, Guestrin C. XGBoost: a scalable tree boosting system. Proceedings of the 22nd ACM SIGKDD (KDD '16), 2016.",
             lien=_doi('10.1145/2939672.2939785'), etiquette='doi:10.1145/2939672.2939785'),
        dict(texte="Breiman L. Random forests. Machine Learning 2001;45:5-32.",
             lien=_doi('10.1023/A:1010933404324'), etiquette='doi:10.1023/A:1010933404324'),
        dict(texte="Sokolova M, Lapalme G. A systematic analysis of performance measures for classification tasks. Information Processing & Management 2009;45:427-437 (pourquoi ne pas se limiter au pourcentage de bonnes réponses).",
             lien=_doi('10.1016/j.ipm.2009.03.002'), etiquette='doi:10.1016/j.ipm.2009.03.002'),
        dict(texte="Opitz J, Burst S. Macro F1 and Macro F1. arXiv:1911.03347, 2019 (deux définitions du F1 macro ; nous utilisons la moyenne des F1 par classe).",
             lien='https://arxiv.org/abs/1911.03347', etiquette='arXiv:1911.03347'),
    ]),
]

NOTE_LIENS_DIRECTIVES = ("Le lien « directive » ouvre la fiche de la directive sur ClinPGx (nouveau nom de PharmGKB) à partir de l'identifiant PA… enregistré avec la règle ; "
                         "l'identifiant vient du fichier de directive CPIC/DPWG utilisé pour construire la règle. Les règles sans identifiant PA (tables PharmCAT, consignes HLA, API CPIC) n'ont pas de lien.")
