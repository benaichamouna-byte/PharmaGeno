## Chapitre 3 : Données et corpus v15 (sources, règles, étiquetage, prétraitement)

Ce chapitre décrit l'origine des données, la construction des étiquettes, la préparation des entrées et la répartition des profils entre développement et évaluation finale. Tous les chiffres ont été recalculés dans les fichiers du corpus v15. La justification de chaque effectif, le détail des règles et du codage, et la liste complète des limites sont en annexe C.

### 3.1 Vue d'ensemble du corpus v15

Chaque ligne du corpus correspond à un couple (profil, médicament) et porte une étiquette de recommandation produite par un moteur de règles (section 3.4).

::: {custom-style="LegendeTableau"}
Tableau 3.1 : Éléments du corpus v15
:::


| Élément | Valeur |
| --- | --- |
| Médicaments | 189 |
| Profils génétiques | 1 379 (1 070 d'identifiant HG et 309 d'identifiant NA, issus du projet 1000 Genomes) |
| Lignes (profil × médicament) | 234 632 |
| Doublons (profil, médicament) | 0 |
| Lignes par profil | minimum 118, médiane 170, maximum 178 |
| Statut d'étiquette | « ok » pour toutes les lignes |

Aucun de ces effectifs n'est un réglage choisi librement : chacun découle d'une règle de construction (annexe C.1). Les 234 632 lignes sont les couples, parmi les 260 631 possibles, pour lesquels une règle s'applique et le gène concerné est typé.

::: {custom-style="LegendeTableau"}
Tableau 3.2 : Répartition des classes d'action (étiquettes) dans le corpus v15
:::


| Classe | Lignes | Part |
| --- | --- | --- |
| STANDARD | 201 273 | 85,78 % |
| ADAPTER\_DOSE | 20 272 | 8,64 % |
| EVITER | 8 031 | 3,42 % |
| SURVEILLER | 5 056 | 2,15 % |

Le corpus est fortement déséquilibré en faveur de STANDARD (figure 3.1) ; ce déséquilibre est pris en compte dans l'entraînement et dans le choix des métriques (chapitre 4). Les proportions sont pratiquement celles de la version précédente du corpus (85,59 % de STANDARD) : les corrections de règles n'ont pas modifié la difficulté de la tâche.

::: {custom-style="FigureImg"}
![](fig/fig_3_1.png){width=11cm}
:::

::: {custom-style="LegendeFigure"}
Figure 3.1 : Répartition des classes d'action dans le corpus v15 (234 632 lignes).
:::

Chaque ligne porte aussi un niveau de confiance du moteur d'étiquetage, « haute » (145 078 lignes) ou « moyenne » (89 554 lignes) : il vaut « moyenne » quand une des règles appliquées est contredite par une autre source pour la même valeur du gène. Il mesure l'accord entre sources, non la force de la preuve.

### 3.2 Profils génétiques

Les profils sont des échantillons du projet 1000 Genomes. Leurs génotypes sont obtenus avec PyPGx 0.27.0 (Sherman, Claw et Lee, 2024) à partir des fichiers VCF du paquet pypgx-bundle 0.27.0 (génome GRCh38). Les allèles HLA (HLA-B\*15:02, HLA-B\*57:01, HLA-B\*58:01, HLA-A\*31:01) proviennent d'un typage publié (Gourraud et al., 2014), disponible pour 508 profils ; ils sont manquants pour les 871 autres.

Le génotype de chaque gène est converti en une valeur numérique selon la logique du phénotype (score d'activité ou statut présent/absent), regroupement qui est la pratique établie en implémentation de la pharmacogénomique (Haidar et al., 2022 ; section 2.2) : CYP2C9 par son score d'activité divisé par 2, VKORC1 par le nombre d'allèles rs9923231, F5 et les allèles HLA par 0 ou 1 (annexe C.2).

### 3.3 Règles de recommandation

Les règles proviennent des directives CPIC (Relling et Klein, 2011), DPWG (Swen et al., 2011) et RNPGx (Abdullah-Koolmees et al., 2021), complétées par les informations pharmacogénétiques des étiquettes de médicaments de la FDA, de l'EMA et de Health Canada. Les tables CPIC et FDA viennent de PharmCAT (Sangkuhl et al., 2020) et les fiches de directives de ClinPGx (Whirl-Carrillo et al., 2021) ; les versions exactes sont en annexe C.3.

La table v15 contient 709 règles à un gène, portant sur 19 gènes, et 124 règles CPIC à plusieurs gènes, qui couvrent six paires de gènes et neuf médicaments (tableau C.2). Vingt et un médicaments ont une règle mais aucune ligne d'entraînement, faute de gène exploitable dans le corpus : ils sont traités par le moteur de règles seul dans l'application (chapitre 5). Les étiquettes FDA et RNPGx reposent sur quatre hypothèses de lecture explicites ; les métriques sont donc rapportées séparément pour les règles CPIC/DPWG et FDA. Six règles dont l'action dépend d'une information absente du fichier VCF (comédication, indication, dosage enzymatique) ne sont pas étiquetées, plutôt que de leur attribuer une décision que la source ne prend pas.

Par rapport à la version 14, trois corrections de règles ont été apportées à partir du texte des directives : ajout de la règle DPWG fondée sur VKORC1 pour la warfarine (chapitre 7), reprise des actions DPWG pour les diplotypes CYP2C9 que le score d'activité confond, et codage de la grille TPMT × NUDT15 pour les thiopurines. Un quatrième point, la priorité des règles à plusieurs gènes pour la fluvastatine, a été vérifié et n'a demandé aucune correction. Ces corrections modifient 433 lignes et en ajoutent 1 968, sans en supprimer (annexe C.3).

### 3.4 Construction des étiquettes

Les étiquettes ne sont pas des observations cliniques. Pour chaque couple (profil, médicament), le moteur applique la ou les règles dont la condition génotypique est satisfaite et attribue une des quatre classes STANDARD, ADAPTER\_DOSE, SURVEILLER ou EVITER ; une règle à plusieurs gènes prime sur une règle à un gène, par spécificité. Les métriques du chapitre 6 mesurent donc la capacité du modèle à reproduire les règles CPIC, DPWG et FDA à partir du génotype, et non la justesse clinique des recommandations.

**Médicaments dont l'action dépend de plusieurs gènes.** Un audit de déterminisme mesure pour quels médicaments la lecture du profil entier est nécessaire : un médicament est dit déterminé par un seul gène lorsque toutes les lignes qui partagent la même valeur d'un gène portent la même action. Dans le corpus v15, l'action est constante pour 57 médicaments et déterminée par un seul gène pour 118 autres, soit 175 des 189 médicaments. Elle dépend de la combinaison de plusieurs gènes pour 14 médicaments seulement : amitriptyline, azathioprine, carbamazépine, clomipramine, doxépine, fluindione, fluvastatine, imipramine, mercaptopurine, rosuvastatine, sertraline, thioguanine, trimipramine et warfarine. Le bénéfice attendu d'une lecture globale du profil (question RQ1) se concentre donc sur cette minorité. Les sommes de contrôle du corpus et des tables de règles sont données en annexe C.4.

### 3.5 Préparation des entrées du modèle

Le chargeur commun du projet part des 31 gènes du corpus et des 4 allèles HLA, et retire les colonnes vides, constantes ou explicitement exclues (annexe C.4). Il reste 20 variables génétiques : ABCG2, CYP2B6, CYP2C19, CYP2C9, CYP2D6, CYP3A4, CYP3A5, DPYD, F5, G6PD, NAT2, NUDT15, SLCO1B1, TPMT, UGT1A1, VKORC1, HLA-B\*15:02, HLA-B\*57:01, HLA-B\*58:01 et HLA-A\*31:01.

Pour 14 variables, une valeur manquante est remplacée par 0 et accompagnée d'un indicateur binaire « \<gène>\_manquant », de sorte que le modèle distingue « absent » de « non typé ». Le modèle reçoit donc 34 colonnes d'entrée (20 variables et 14 indicateurs). Pour le réseau de neurones, elles sont standardisées avec la moyenne et l'écart-type des seuls profils d'entraînement de chaque pli ; les modèles à base d'arbres reçoivent les valeurs brutes.

### 3.6 Découpage des données et ensemble final

Tous les découpages se font par profil, pour qu'un même profil ne soit jamais à la fois en apprentissage et en test. La validation croisée utilise StratifiedGroupKFold à 5 plis (scikit-learn ; Pedregosa et al., 2011), graine 42, groupé par identifiant de profil ; la parenté entre profils est traitée en section 3.8, point 3.

**Ensemble final.** 138 profils (23 455 lignes), soit 10 % des 1 379 profils, sont réservés à une évaluation finale unique. Tirés une fois puis figés, ils ne servent ni à l'entraînement, ni au réglage, ni au choix des modèles. Ce n'est toutefois pas un ensemble vierge de toute exposition : 125 d'entre eux ont participé à la validation croisée d'essais antérieurs du projet (section 3.8, point 9). Les 1 241 profils restants (211 177 lignes) servent au développement : choix des hyperparamètres, validation croisée et calibration.

### 3.7 Médicaments et métadonnées

Les classes ATC proviennent du dépôt public fabkury/atcd ; elles servent, avec la spécialité médicale, à regrouper les médicaments dans l'application (annexe C.5). L'annexe F donne la liste des 189 médicaments avec leur sous-groupe ATC4, les gènes de leurs règles, leur nombre de lignes et les actions rencontrées.

### 3.8 Limites assumées

Les douze limites du corpus sont énumérées ici ; leur description complète est en annexe C.6.

1. **Étiquettes issues de règles** : elles reproduisent des directives, sans mesurer aucun résultat clinique.
2. **Sélection des 1 379 profils** : non aléatoire et non documentée ; les fréquences d'allèles ne sont pas des fréquences de population.
3. **Apparentement** : une seule paire parent-enfant ; une analyse de sensibilité regroupant les 187 paires reliées par le pedigree change le F1 macro de 0,00022, sous le seuil de 0,001 fixé d'avance.
4. **Codage de CYP2C9 par score d'activité** : il confond des diplotypes que la DPWG distingue ; résidu de 146 lignes et écart face à PharmCAT (section 8.3).
5. **Sources HLA et CYP2D6** : un identifiant de source HLA reste inexpliqué, l'origine du génotype CYP2D6 n'est pas documentée, et ni CYP2D6 ni HLA ne se lisent dans un VCF de variants ponctuels.
6. **Conventions du projet** : codage de G6PD et choix d'étiquette quand le texte propose plusieurs conduites.
7. **Anémie hémolytique non sphérocytaire** : phénotype non dérivable d'un VCF ; l'outil affiche la réserve clinique.
8. **Règles révisées après observation** : l'évaluation sur les profils de développement n'est pas indépendante des règles.
9. **Ensemble final** : 125 des 138 profils ont servi à des validations croisées antérieures, sans jamais avoir été lus pour une évaluation.
10. **Règles non étiquetées** : six règles dépendant d'une information absente du VCF.
11. **Références générales** : la publication précise de chaque directive n'a pas été associée ici.
