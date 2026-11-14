## Chapitre 3 : Données et corpus v15 (sources, règles, étiquetage, prétraitement)

Ce chapitre décrit d'où viennent les données du projet, comment les étiquettes ont été construites, comment les entrées du modèle sont préparées et comment les profils sont répartis entre développement et évaluation finale. Tous les chiffres ont été recalculés dans les fichiers du corpus v15 ; ce qui n'a pas pu être confirmé est signalé comme tel dans la section 3.8.

### 3.1 Vue d'ensemble du corpus v15

Le corpus v15 associe des profils pharmacogénétiques à des médicaments. Chaque ligne correspond à un couple (profil, médicament) et porte une étiquette de recommandation produite par un moteur de règles (section 3.4).

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

**Pourquoi ces effectifs.** Aucun de ces nombres n'est un réglage choisi librement : chacun découle d'une règle de construction, indiquée ci-dessous avec ce qui empêche d'en avoir plus ou moins.

- **189 médicaments.** Ce sont les médicaments pour lesquels les sources retenues fournissent au moins une règle applicable aux gènes du corpus (709 règles à un gène et 124 règles à plusieurs gènes, section 3.3). Il n'y en a pas davantage parce que les autres médicaments n'ont pas de règle dans ces sources, ou que leur règle porte sur un gène inexploitable dans le corpus (21 médicaments, section 3.3). Ce nombre n'est donc pas fixé d'avance : il change quand une source ajoute ou retire une règle. Il est resté identique entre les versions 14 et 15 du corpus, les corrections apportées ayant porté sur des règles de médicaments déjà couverts.
- **1 379 profils.** Les fichiers source contiennent 3 202 échantillons ; le corpus en utilise 1 379, repris du jeu de données initial du projet. La règle qui a retenu ces échantillons n'a pas été retrouvée. L'examen de la liste montre que ce n'est pas un tirage au hasard : les enfants des trios en sont presque absents (4 sur 608), et la part d'échantillons retenus décroît dans l'ordre des identifiants (80 % des 200 premiers, puis entre 26 % et 56 % selon les tranches de 200). Ce nombre n'est donc pas justifié par un calcul de taille d'échantillon ; c'est une limite (section 3.8, point 2). \[à compléter : courbe d'apprentissage selon le nombre de profils\]
- **234 632 lignes.** Les 1 379 profils et les 189 médicaments forment 260 631 couples possibles. 25 999 couples n'ont pas de ligne, parce que le moteur ne produit une étiquette que si une règle s'applique à la valeur du gène du profil et si ce gène est typé. Le corpus v15 compte 1 968 lignes de plus que le v14, l'ajout de la règle fondée sur VKORC1 pour la warfarine et de la grille à deux gènes des thiopurines ayant rendu étiquetables des couples qui ne l'étaient pas.
- **118 à 178 lignes par profil.** C'est la conséquence du point précédent : un profil dont certains gènes ne sont pas typés est étiqueté pour moins de médicaments. Ainsi, 46 médicaments ont une ligne pour chacun des 1 379 profils, alors que la warfarine en a 1 378 (les profils dont le CYP2C9 ou le VKORC1 n'est pas de référence) et l'abacavir 508 (les profils disposant d'un typage HLA).
- **0 doublon et statut « ok ».** Ce sont des résultats de contrôle, non des choix : chaque couple (profil, médicament) n'apparaît qu'une fois, et seules les lignes dont l'étiquette a pu être calculée sans ambiguïté sont conservées.

Répartition des classes :

::: {custom-style="LegendeTableau"}
Tableau 3.2 : Répartition des classes d'action (étiquettes) dans le corpus v15
:::


| Classe | Lignes | Part |
| --- | --- | --- |
| STANDARD | 201 273 | 85,78 % |
| ADAPTER\_DOSE | 20 272 | 8,64 % |
| EVITER | 8 031 | 3,42 % |
| SURVEILLER | 5 056 | 2,15 % |

Le corpus est donc fortement déséquilibré en faveur de STANDARD ; ce déséquilibre est pris en compte dans l'entraînement (chapitre 4) et dans le choix des métriques (F1 macro, calibration). Les proportions sont pratiquement inchangées par rapport à la version précédente du corpus, où la classe STANDARD représentait 85,59 % des lignes : les corrections de règles n'ont pas modifié la difficulté de la tâche d'apprentissage.

::: {custom-style="FigureImg"}
![](fig/fig_3_1.png){width=15cm}
:::

::: {custom-style="LegendeFigure"}
Figure 3.1 : Répartition des classes d'action dans le corpus v15 (234 632 lignes).
:::

Chaque ligne porte aussi un niveau de confiance attribué par le moteur d'étiquetage : « haute » pour 145 078 lignes et « moyenne » pour 89 554 lignes. Une ou deux règles s'appliquent à chaque ligne (une règle : 222 318 lignes ; deux règles : 12 314 lignes). \[à compléter : définition des niveaux de confiance\]

### 3.2 Profils génétiques

**Origine.** Les profils sont des échantillons du projet 1000 Genomes. Les génotypes pharmacogénétiques sont obtenus avec PyPGx version 0.27.0 (Sherman, Claw et Lee, 2024), qui détermine les allèles étoilés des pharmacogènes à partir de fichiers VCF. Les fichiers VCF proviennent du paquet de données pypgx-bundle 0.27.0 (génome de référence GRCh38) ; ils contiennent 3 202 échantillons, dont 1 379 sont retenus dans le corpus. Ces 1 379 échantillons sont ceux du jeu de données initial du projet ; le critère qui les a retenus parmi les 3 202 n'a pas pu être reconstitué (section 3.8, point 2).

**Typage HLA.** Les allèles HLA (HLA-B\*15:02, HLA-B\*57:01, HLA-B\*58:01, HLA-A\*31:01) ne sont pas appelés par PyPGx dans ce projet. Ils proviennent d'un typage publié (Gourraud et al., 2014) disponible pour 508 des 1 379 profils ; pour les 871 autres, la valeur est déclarée manquante.

**Codage des génotypes.** Le génotype de chaque gène est converti en une valeur numérique selon la logique du phénotype (score d'activité ou statut présent/absent). Ce regroupement des diplotypes en un petit nombre de valeurs de phénotype est la pratique établie dans les travaux d'implémentation de la pharmacogénomique, où il est présenté comme la condition pour que l'aide à la décision reste praticable (Haidar et al., 2022 ; section 2.2) :

- les gènes à score d'activité (par exemple CYP2D6, NAT2, SLCO1B1) prennent des valeurs comprises entre 0 et 2 (CYP2D6 : 0 ; 0,5 ; 1 ; 2. NAT2 : 0 ; 0,5 ; 1,5. SLCO1B1 : 0 ; 0,5 ; 1 ; 1,5) ;
- CYP2C9 est codé par son score d'activité divisé par 2 (valeurs 0 ; 0,25 ; 0,5 ; 0,75 ; 1,0). Ce recodage fait suite à un audit des règles : CPIC distingue, pour CYP2C9 intermédiaire, un score d'activité de 1,5 (dose standard) et de 1,0 (dose réduite ou alternative) pour les anti-inflammatoires non stéroïdiens, alors que l'ancien codage leur donnait la même valeur 0,5. La limite de ce codage, lorsqu'une recommandation raisonne par diplotype plutôt que par score, est documentée à la section 3.8 ;
- VKORC1 est codé par le nombre d'allèles rs9923231 (0 allèle : 1 ; 1 allèle : 0,5 ; 2 allèles : 0) ;
- F5 et les allèles HLA sont codés 0 ou 1 (absent ou présent) ;
- G6PD est codé 0 ; 0,5 ; 1. Ce codage est une convention du projet : PyPGx ne fournit pas de phénotype CPIC pour G6PD (Sherman et al., 2024, tableau 1).

### 3.3 Règles de recommandation

**Sources.** Les règles proviennent de directives pharmacogénétiques publiées : CPIC (Relling et Klein, 2011), DPWG (Swen et al., 2011) et RNPGx (Abdullah-Koolmees et al., 2021), complétées par les informations de pharmacogénétique des étiquettes de médicaments de la FDA, de l'EMA et de Health Canada (HCSC). Les tables CPIC utilisées pour six gènes ont été prises dans PharmCAT (Sangkuhl et al., 2020), version du 25 septembre 2026 (commit 27ea1bc). Les tables FDA proviennent du fichier prescribing\_guidance.json de PharmCAT (commit 8e6f81b9372da54f9281d452cd171253c6a8974f, 16 octobre 2026). Les fiches de directives CPIC et DPWG proviennent de ClinPGx (Whirl-Carrillo et al., 2021) : 220 fichiers JSON téléchargés le 5 avril 2026, sous licence CC BY-SA 4.0.

**Règles mono-gène.** La table v15 contient 709 règles mono-gène, réparties par source : CPIC 363, DPWG 145, FDA 95, FDA-étiquette 84, HCSC-étiquette 8, RNPGx 8, EMA-étiquette 6. Elles concernent 19 gènes : CYP2B6, CYP2C19, CYP2C9, CYP2D6, CYP3A4, CYP3A5, DPYD, F5, G6PD, HLA-A\*31:01, HLA-B\*15:02, HLA-B\*57:01, HLA-B\*58:01, NAT2, NUDT15, SLCO1B1, TPMT, UGT1A1 et VKORC1.

**Règles multi-gènes.** 124 règles CPIC portent sur des combinaisons de gènes :

::: {custom-style="LegendeTableau"}
Tableau 3.3 : Règles multi-gènes, paires de gènes et médicaments concernés
:::


| Paire de gènes | Médicament(s) |
| --- | --- |
| ABCG2 + SLCO1B1 | rosuvastatine |
| CYP2B6 + CYP2C19 | sertraline |
| CYP2C19 + CYP2D6 | amitriptyline |
| CYP2C9 + HLA-B | phénytoïne, fosphénytoïne |
| CYP2C9 + SLCO1B1 | fluvastatine |
| TPMT + NUDT15 | azathioprine, mercaptopurine, thioguanine |

Ce tableau est exhaustif : la table des règles multi-gènes v15 ne contient aucune autre paire de gènes ni aucun autre médicament. Les 124 règles s'y répartissent ainsi : TPMT + NUDT15, 27 règles ; CYP2B6 + CYP2C19, 25 ; CYP2C19 + CYP2D6, 20 ; CYP2C9 + HLA-B, 20 ; CYP2C9 + SLCO1B1, 20 ; ABCG2 + SLCO1B1, 12. Le nombre de règles d'une paire est le produit du nombre de valeurs retenues pour chacun des deux gènes, multiplié par le nombre de médicaments de la paire : c'est donc la taille de la grille que la directive décrit, et non un choix. Les neuf médicaments cités portent tous aussi au moins une règle à un gène, sauf la rosuvastatine ; l'union des 188 médicaments à règle mono-gène et des 9 à règle multi-gènes donne les 189 médicaments du corpus.

**Médicaments « règle seule ».** 21 médicaments ont une règle mais aucune ligne d'entraînement, car le gène concerné n'est pas exploitable dans le corpus (CACNA1S, RYR1, CFTR, MT-RNR1, certains allèles HLA). Ils sont traités par le moteur de règles seul dans l'application (chapitre 5).

**Hypothèses de lecture des étiquettes FDA et RNPGx.** Les textes réglementaires ne donnent pas toujours une action directement utilisable. Quatre hypothèses de lecture ont été posées et sont explicitement séparées des directives CPIC et DPWG : H-FDA-1 (une valeur non citée dans le texte conduit à STANDARD), H-FDA-2 (une mise en garde liée au génotype conduit à SURVEILLER), H-FDA-3 (une dose réduite conduit à ADAPTER\_DOSE) et H-RNPGx-1 (hypothèse propre aux règles RNPGx, à détailler en annexe). Par conséquent, les métriques sont rapportées séparément pour les règles CPIC/DPWG et pour les règles FDA.

**Règles dont l'action dépend d'une information absente du fichier VCF.** Une règle dont l'action prescrite dépend d'une donnée que le fichier de variants ne contient pas — une comédication, une indication thérapeutique, un dosage enzymatique — n'est pas étiquetée. Six règles sont dans ce cas : mavacamten, éliglustat, flécaïnide, quétiapine, primaquine, ainsi que le phénotype G6PD dit « variable », pour lequel la recommandation prescrit de mesurer l'activité enzymatique avant de décider. Cette politique est appliquée sans dérogation : attribuer une action à ces règles reviendrait à inventer une décision que la source ne prend pas.

**Évolution depuis la v14.** Quatre corrections de règles ont été apportées, à partir du texte des directives :

- **Warfarine.** La recommandation DPWG fondée sur VKORC1 a été ajoutée. Elle était absente de la v14 sans justification, alors que la règle équivalente y figurait pour l'acénocoumarol et la phenprocoumone (chapitre 7).
- **CYP2C9.** Les actions prescrites par la DPWG pour les diplotypes que le score d'activité confond ont été reprises, en conservant le codage par score d'activité et en corrigeant les étiquettes. Le résidu de cette correction est documenté à la section 3.8.
- **Thiopurines.** La grille à deux gènes TPMT × NUDT15 de CPIC a été codée pour l'azathioprine, la mercaptopurine et la thioguanine, qui étaient auparavant traitées par le seul TPMT.
- **Fluvastatine.** Aucune correction n'a été nécessaire : le moteur applique déjà la priorité des règles à plusieurs gènes sur les règles à un gène.

Ces corrections modifient 433 lignes et en ajoutent 1 968 ; aucune n'est supprimée.

### 3.4 Construction des étiquettes

Les étiquettes ne sont pas des observations cliniques : elles sont produites automatiquement en appliquant, pour chaque couple (profil, médicament), la ou les règles dont la condition génotypique est satisfaite. Chaque ligne reçoit une des quatre classes STANDARD, ADAPTER\_DOSE, SURVEILLER ou EVITER. Lorsqu'une règle à plusieurs gènes et une règle à un gène s'appliquent au même couple, la règle à plusieurs gènes prime, par spécificité.

Les scripts de construction des règles et du corpus sont conservés avec celui-ci. La somme de contrôle (sha256, 16 premiers caractères) du corpus v15 est 68b564ce265728b6 ; celles des tables de règles sont : mono-gène v15, 9d5512543016cb89 ; multi-gènes v15, 1cb99ff632466696.

Conséquence importante pour l'interprétation : les métriques du chapitre 6 mesurent la capacité du modèle à reproduire les règles CPIC, DPWG et FDA à partir du génotype, et non la justesse clinique des recommandations.

### 3.5 Préparation des entrées du modèle

**Sélection des variables.** Le chargeur commun du projet (protocole\_commun\_v10) part des 31 gènes du corpus et des 4 allèles HLA, retire les gènes explicitement exclus (RYR1, CACNA1S, CYP4F2, CFTR, HLA-A, HLA-A\*02:01, HLA-B\*15:11) ainsi que les colonnes vides ou constantes. Il reste 20 variables génétiques : ABCG2, CYP2B6, CYP2C19, CYP2C9, CYP2D6, CYP3A4, CYP3A5, DPYD, F5, G6PD, NAT2, NUDT15, SLCO1B1, TPMT, UGT1A1, VKORC1, HLA-B\*15:02, HLA-B\*57:01, HLA-B\*58:01 et HLA-A\*31:01.

Parmi les colonnes écartées, onze (ACE, ADRB2, CYP1A2, CYP2A6, EGFR, HLA-A, HLA-B, IFNL3, MT-RNR1, MTHFR, SLC19A1) sont vides pour les 1 379 profils ; CACNA1S est constant ; CFTR n'a que 2 valeurs et 31 profils manquants ; CYP4F2 (3 valeurs) et RYR1 (2 valeurs) ont été exclus. L'exclusion de CYP4F2 mérite une justification propre : ce gène n'intervient que dans une recommandation de dose calculée par un algorithme multi-gènes dépendant de l'ascendance, qui ne se ramène pas aux quatre classes d'action du corpus (chapitre 7).

**Valeurs manquantes.** Pour 14 variables, une valeur manquante est remplacée par 0 et accompagnée d'un indicateur binaire « \<gène>\_manquant », de sorte que le modèle distingue « absent » de « non typé ». Nombre de profils manquants : CYP2B6 19, CYP2C19 18, CYP2C9 1, CYP3A4 42, G6PD 2, NAT2 153, NUDT15 56, SLCO1B1 60, TPMT 16, UGT1A1 1 ; pour chacun des 4 allèles HLA, 871 profils (le typage HLA n'existe que pour 508 profils). Le modèle reçoit donc 34 colonnes d'entrée (20 variables et 14 indicateurs).

**Standardisation.** Pour le réseau de neurones, les 34 colonnes d'entrée (variables et indicateurs) sont standardisées (moyenne 0, écart-type 1) avec une moyenne et un écart-type calculés sur les seuls profils d'entraînement de chaque pli (StandardScaler de scikit-learn), puis appliqués aux profils de validation et de test ; le modèle final enregistre ces deux vecteurs pour l'application. Les modèles à base d'arbres (XGBoost, Random Forest) reçoivent les valeurs brutes, sans mise à l'échelle.

Le codage du médicament, l'architecture et l'entraînement sont décrits au chapitre 4.

### 3.6 Découpage des données et ensemble final

**Unité de découpage.** Tous les découpages se font par profil : toutes les lignes d'un même profil sont dans le même groupe, afin d'éviter qu'un profil apparaisse à la fois en apprentissage et en test. La validation croisée utilise StratifiedGroupKFold à 5 plis (scikit-learn ; Pedregosa et al., 2011), avec la graine 42. Le regroupement se fait par identifiant de profil ; la parenté entre profils est examinée en section 3.8, point 3.

**Ensemble final.** 138 profils (23 455 lignes), soit 10 % des 1 379 profils, sont réservés à une évaluation finale unique. Ils ont été tirés une fois, puis leur liste a été figée pour que l'ensemble reste le même d'une version du corpus à l'autre. Ils ne servent ni à l'entraînement, ni au réglage, ni au choix des modèles, et ils n'ont jamais été lus pour évaluer un modèle. Ce n'est toutefois pas un ensemble vierge de toute exposition : 125 de ces profils ont participé à la validation croisée d'essais antérieurs du projet (section 3.8, point 9). Les 1 241 profils restants (211 177 lignes) servent au développement : choix des hyperparamètres, validation croisée et calibration (sur 10 % de validation interne).

### 3.7 Médicaments et métadonnées

Les classes ATC des médicaments proviennent d'une copie du dépôt public fabkury/atcd (25 avril 2026). Huit médicaments n'ont pas de code ATC fiable et trois n'ont pas de spécialité associée. La spécialité sert à regrouper les médicaments dans l'application.

### 3.8 Limites assumées

1. **Étiquettes issues de règles.** Les étiquettes reproduisent des directives ; elles ne mesurent aucun résultat clinique.
2. **Sélection des 1 379 profils.** La règle qui a retenu ces 1 379 échantillons parmi les 3 202 des fichiers source n'a pas été retrouvée ; la liste n'est pas un tirage au hasard (section 3.1). Le corpus n'est donc pas un échantillon représentatif documenté du projet 1000 Genomes, les fréquences d'allèles observées ne doivent pas être lues comme des fréquences de population, et l'effet du nombre de profils sur les performances n'a pas été mesuré.
3. **Apparentement.** Les plis regroupent les lignes par identifiant de profil. D'après le pedigree du projet 1000 Genomes, une seule paire parent-enfant figure parmi les 1 379 profils, et aucune fratrie. Le pedigree relie en outre 186 paires de profils par un enfant absent du corpus : 185 couples (le père et la mère de cet enfant) et une paire par alliance. D'après le pedigree, ces 372 profils ne sont pas apparentés génétiquement entre eux. Par précaution, une analyse de sensibilité dont le protocole a été fixé avant le calcul a refait la validation croisée du réseau en gardant ces 187 paires du même côté : sur 25 entraînements, le F1 macro passe de 0,99786 ± 0,00123 à 0,99807 ± 0,00094, soit un écart de 0,00022, inférieur au seuil de 0,001 fixé d'avance. Pour la même raison, les 34 profils de développement reliés par le pedigree à un profil de l'ensemble final seront retirés de l'entraînement avant l'évaluation finale. Deux réserves demeurent : le pedigree ne décrit que la parenté déclarée, non une parenté plus lointaine ni la structure de population ; deux des 138 profils finaux ont un vecteur d'entrée identique à celui d'un profil de développement et seront rapportés à part.
4. **Codage de CYP2C9 par score d'activité.** Le score d'activité confond des diplotypes auxquels la DPWG attribue des actions différentes. Pour les trois médicaments dont la recommandation DPWG raisonne par diplotype, les étiquettes ont été corrigées en retenant l'action du diplotype le plus fréquent, sauf lorsque ce choix conduirait à abandonner une action « éviter ». Un résidu subsiste : \[à compléter : nombre de lignes concernées, un seul médicament\] lignes pour lesquelles la représentation ne permet pas de distinguer les deux cas. Porter le diplotype plutôt que le seul score d'activité est identifié comme perspective (chapitre 9).
5. **Source HLA.** Un identifiant de source (« PA0811 ») apparaît dans les données HLA sans explication retrouvée.
6. **CYP2D6.** L'origine du génotype CYP2D6 n'est pas documentée ; CYP2D6 et les allèles HLA ne sont de plus pas lisibles à partir d'un VCF de variants ponctuels, d'où le formulaire de laboratoire dans l'application.
7. **Conventions du projet.** Le codage de G6PD et les choix d'étiquette pour les règles dont le texte propose plusieurs conduites sont des conventions du projet, pas des textes de directives.
8. **CNSHA.** Le phénotype d'anémie hémolytique non sphérocytaire congénitale, que la recommandation sur G6PD distingue, n'est pas dérivable d'un fichier de variants. L'outil assigne le phénotype déficient et affiche la réserve clinique correspondante.
9. **Règles révisées après observation.** Certaines règles ont été revues après l'examen d'erreurs de validation : l'évaluation sur les profils de développement n'est donc pas indépendante des règles.
10. **Ensemble final.** 125 des 138 profils actuels ont été utilisés dans la validation croisée d'essais antérieurs. Ils n'ont toutefois jamais été lus pour une évaluation. L'ensemble final est donc réservé, sans être vierge de toute exposition méthodologique.
11. **Règles non étiquetées.** Six règles ne reçoivent pas d'étiquette parce que leur action dépend d'une information absente du fichier VCF (section 3.3). Dans la table v15, 18 des 709 règles à un gène portent le drapeau « conditionnel » et 2 le drapeau « ambigu ». Ces drapeaux signalent une règle dont l'action dépend d'une information que le corpus ne porte pas ; ils servent à délimiter ce que l'étiquette recouvre, et non à écarter des lignes.
12. **Références générales.** L'application affiche pour chaque source la référence générale (CPIC : Relling et Klein, 2011 ; DPWG : Swen et al., 2011 ; RNPGx : Abdullah-Koolmees et al., 2021) ; l'association de chaque directive à sa publication précise (environ 152 identifiants PA) reste à faire.

### 3.9 Origine des principaux effectifs

Le tableau 3.4 indique, pour chaque effectif utilisé dans ce mémoire, ce qu'il désigne et d'où il vient.

::: {custom-style="LegendeTableau"}
Tableau 3.4 : Origine des principaux effectifs du corpus
:::

| Effectif | Ce qu'il désigne | Origine |
| --- | --- | --- |
| 3 202 | Échantillons des fichiers VCF source | Effectif des fichiers 1000 Genomes fournis avec pypgx-bundle 0.27.0 (section 3.2) |
| 1 379 | Profils du corpus | Échantillons du jeu de données initial du projet ; règle de sélection parmi les 3 202 non retrouvée, liste non aléatoire (section 3.1) |
| 508 | Profils avec typage HLA | Profils pour lesquels un typage HLA publié est disponible (Gourraud et al., 2014) ; valeur manquante pour les 871 autres |
| 189 | Médicaments | Médicaments couverts par au moins une règle applicable aux gènes du corpus (section 3.3) |
| 234 632 | Lignes | Couples (profil, médicament) pour lesquels une règle s'applique et le gène est typé, sur 260 631 couples possibles (section 3.1) |
| 211 177 | Lignes de développement | 234 632 lignes moins les 23 455 des 138 profils de l'ensemble final (section 3.6) |
| 4 | Classes d'action | STANDARD, ADAPTER\_DOSE, SURVEILLER, EVITER : actions produites par le moteur de règles (section 3.4) |
| 20 | Variables génétiques | 31 gènes et 4 allèles HLA du corpus, moins les colonnes vides, constantes ou exclues (section 3.5) |
| 34 | Colonnes d'entrée du modèle | 20 variables et 14 indicateurs de valeur manquante (section 3.5) |
| 138 | Profils de l'ensemble final | 10 % des 1 379 profils, tirés une fois puis figés (section 3.6) |
| 1 241 | Profils de développement | 1 379 profils moins les 138 de l'ensemble final (section 3.6) |
