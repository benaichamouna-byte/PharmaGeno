::: {custom-style="TitreFront"}
Remerciements
:::

Je tiens à exprimer ma gratitude au Professeur Kais Ghedira, qui a encadré ce travail. Sa rigueur, ses exigences et la liberté qu'il m'a laissée dans la conduite du projet en ont déterminé la forme et le contenu.

Je remercie l'Institut Pasteur de Tunis, qui a accueilli ce stage et mis à ma disposition les moyens nécessaires à sa réalisation, ainsi que l'équipe du laboratoire pour ses conseils et sa disponibilité.

Mes remerciements vont également à l'Institut Supérieur de Biotechnologie de Sidi Thabet et à l'École Nationale des Sciences de l'Informatique, dont la formation conjointe en Bio-Data Analytics a rendu ce travail possible, ainsi qu'à l'ensemble des enseignants du mastère.

Je remercie les membres du jury d'avoir accepté d'évaluer ce mémoire et de consacrer leur temps à sa lecture.

Je remercie enfin ma famille et mes proches pour leur soutien constant tout au long de cette année.

::: {custom-style="TitreFront"}
Résumé / Abstract
:::

PharmaGeno est un prototype d'aide à la décision pharmacogénomique. À partir d'un fichier VCF et d'une spécialité, un réseau de neurones lit le profil génétique du patient en une passe et prédit, pour 189 médicaments, une action parmi quatre : EVITER, ADAPTER\_DOSE, SURVEILLER, STANDARD. Une application web locale affiche ces avis avec la recommandation officielle.

Le corpus associe 1 379 profils du projet 1000 Genomes à 189 médicaments (232 664 lignes). Les étiquettes sont calculées par un moteur de règles d'après les recommandations CPIC, DPWG, RNPGx et des étiquettes réglementaires : ce ne sont pas des réponses cliniques, et toutes les mesures expriment une fidélité aux règles, non une justesse clinique.

En validation croisée par profil, le réseau atteint un F1 macro de 0,9979 et manque 0,83 % des situations à éviter. Sous protocole identique, XGBoost reproduit les règles mieux que le réseau (0,9994 contre 0,9968). Sur 104 personnes hors corpus, la recommandation affichée est retrouvée chez PharmCAT pour 97,8 % des lignes comparables. Sur 5 774 patients traités à la warfarine, la règle du corpus va dans le bon sens mais ignore VKORC1, principal déterminant de la dose. L'ensemble final de 138 profils n'a pas encore été évalué \[à compléter\].

**Mots-clés :** pharmacogénomique, apprentissage profond, aide à la décision, calibration, VCF.

**Abstract.** PharmaGeno is a pharmacogenomic decision-support prototype. From a patient VCF file and a medical specialty, it builds a multi-gene genetic profile; a neural network reads this profile in a single pass and predicts, for 189 drugs, one action among four: AVOID, ADJUST DOSE, MONITOR, STANDARD. A local web application displays these outputs alongside the corresponding official recommendation.

The corpus pairs 1,379 profiles from the 1000 Genomes Project with 189 drugs, yielding 232,664 rows. Labels are computed by a rule engine from CPIC, DPWG and RNPGx recommendations and regulatory drug labels: they are not observed clinical responses, so all measurements express agreement with the rules rather than clinical correctness.

In cross-validation grouped by profile, the network reaches a macro-F1 of 0.9979 and misses 0.83 % of situations to avoid. Under an identical protocol, XGBoost reproduces the rules better than the network (0.9994 against 0.9968). On 104 individuals outside the corpus, the displayed recommendation is found in PharmCAT output for 97.8 % of comparable rows. On 5,774 patients treated with warfarin, the corpus rule points in the right direction but omits VKORC1, the main genetic determinant of dose. The reserved set of 138 profiles has not yet been evaluated \[à compléter\].

**Keywords:** pharmacogenomics, deep learning, decision support, calibration, VCF.
