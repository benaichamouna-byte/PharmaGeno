::: {custom-style="TitreFront"}
Résumé
:::

PharmaGeno est un prototype d'aide à la décision pharmacogénomique. À partir du fichier VCF d'un patient, il construit un profil multi-gènes qu'un réseau de neurones lit en une passe pour prédire, pour 189 médicaments, une action parmi quatre : éviter, adapter la dose, surveiller, dose standard. Une application web affiche chaque avis à côté de la recommandation officielle. Les étiquettes du corpus (1 379 profils du projet 1000 Genomes, 234 632 lignes) sont produites par des règles tirées principalement des recommandations CPIC et DPWG, complétées par RNPGx et des étiquettes réglementaires : les scores mesurent la fidélité à ces règles, non la justesse clinique. En validation croisée groupée par profil, le réseau obtient un F1 macro de 0,9982 ; sous protocole identique, sa différence avec XGBoost n'est pas tranchée, et XGBoost manque moins de situations à éviter. Sur 138 profils réservés, lus une seule fois, le F1 macro est de 0,9940, la baisse étant portée par un profil atypique. Sur 104 personnes hors corpus, 95,9 % des recommandations affichées sont retrouvées chez PharmCAT. Sur 5 774 patients réels traités par warfarine, la règle du corpus va dans le bon sens. Le réseau se dégrade sur des profils partiels.

**Mots-clés :** pharmacogénomique, apprentissage profond, aide à la décision, recommandations CPIC, fichier VCF.

::: {custom-style="TitreFront"}
Abstract
:::

PharmaGeno is a pharmacogenomic decision-support prototype. From a patient's VCF file, it builds a multi-gene profile that a neural network reads in a single pass to predict, for 189 drugs, one of four actions: avoid, adjust dose, monitor, standard dose. A web application, run locally, calls 18 genes with PyPGx, displays each prediction next to the official recommendation and flags uncertain or conflicting predictions for review. The corpus labels (1,379 profiles from the 1000 Genomes Project, 234,632 rows) are produced by rules derived mainly from CPIC and DPWG guidelines, complemented by RNPGx and regulatory drug labels: scores measure agreement with these rules, not clinical correctness. In cross-validation grouped by profile, the network reaches a macro-F1 of 0.9982; under an identical protocol, its difference from XGBoost is inconclusive, and XGBoost misses fewer avoid situations. On 138 held-out profiles evaluated once, macro-F1 is 0.9940, the drop being driven by one atypical profile. On 104 individuals outside the corpus, 95.9% of the displayed recommendations are found in PharmCAT output. On 5,774 real warfarin patients, the corpus rule points in the right direction. The network degrades on partial profiles.

**Keywords:** pharmacogenomics, deep learning, clinical decision support, CPIC guidelines, VCF file.
