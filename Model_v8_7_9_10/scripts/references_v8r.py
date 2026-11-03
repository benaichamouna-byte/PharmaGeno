# references_v8r.py (3 nov. 2026) = references_v8n.py (INTACT) + 3 références vérifiées le 3 nov. 2026 sur les pages officielles (Crossref pour IWPC ; PMLR pour Guo et al. ; JMLR pour scikit-learn).
# Même règle : aucune référence n'est écrite de mémoire ; ne pas en ajouter sans la vérifier.
import copy
from references_v8n import REFERENCES as _R, NOTE_LIENS_DIRECTIVES

REFERENCES = copy.deepcopy(_R)
for g in REFERENCES:
    if g['groupe'].startswith('Modèles de comparaison'):
        g['items'] = [
            dict(texte="Chen T, Guestrin C. XGBoost: a scalable tree boosting system. Proceedings of the 22nd ACM SIGKDD (KDD '16), 2016 (second modèle de contrôle affiché à côté du DL).",
                 lien='https://doi.org/10.1145/2939672.2939785', etiquette='doi:10.1145/2939672.2939785'),
            dict(texte="Breiman L. Random forests. Machine Learning 2001;45:5-32 (troisième modèle de contrôle affiché à côté du DL).",
                 lien='https://doi.org/10.1023/A:1010933404324', etiquette='doi:10.1023/A:1010933404324'),
            dict(texte="Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: machine learning in Python. Journal of Machine Learning Research 2011;12:2825-2830 (implémentation du Random Forest).",
                 lien='https://jmlr.org/papers/v12/pedregosa11a.html', etiquette='jmlr.org/papers/v12/pedregosa11a'),
            dict(texte="Guo C, Pleiss G, Sun Y, Weinberger KQ. On calibration of modern neural networks. Proceedings of the 34th International Conference on Machine Learning, PMLR 70:1321-1330, 2017 (mise à l'échelle par température du DL).",
                 lien='https://proceedings.mlr.press/v70/guo17a.html', etiquette='proceedings.mlr.press/v70/guo17a'),
        ] + [it for it in g['items'] if it['etiquette'] in ('doi:10.1016/j.ipm.2009.03.002', 'arXiv:1911.03347')]
REFERENCES.append(dict(groupe="Validation de la règle sur de vrais patients (warfarine)", items=[
    dict(texte="International Warfarin Pharmacogenetics Consortium. Estimation of the warfarin dose with clinical and pharmacogenetic data. N Engl J Med 2009;360(8):753-764 (données de 6 922 patients utilisées pour tester la règle warfarine).",
         lien='https://doi.org/10.1056/NEJMoa0809329', etiquette='doi:10.1056/NEJMoa0809329'),
]))


# --- v8r (3 nov. 2026, soir) : constantes partagées par l'écran et le PDF
REF_SOURCE = {   # référence générale de chaque source de règle (déjà dans la liste ci-dessus, DOI vérifiés)
    'CPIC': ('Relling & Klein, Clin Pharmacol Ther 2011;89:464-467', 'https://doi.org/10.1038/clpt.2010.279'),
    'DPWG': ('Swen et al., Clin Pharmacol Ther 2011;89:662-673', 'https://doi.org/10.1038/clpt.2011.34'),
    'RNPGx': ('Abdullah-Koolmees et al., Front Pharmacol 2021;11:595219', 'https://doi.org/10.3389/fphar.2020.595219'),
}
LEGENDE_SCORES = ("Le nombre sous chaque avis (de 0 à 1) est la certitude du modèle dans son propre avis ; il est arrondi vers le bas. "
                  "DL : probabilité calibrée par un réglage de température. XGBoost et Random Forest : scores non calibrés ; "
                  "le Random Forest, moyenne de 100 arbres, donne souvent des valeurs plus basses. "
                  "Ces modèles reproduisent les directives CPIC/DPWG : leur score mesure leur certitude de reproduire la règle, pas la probabilité que l'avis soit juste cliniquement.")
