## Annexe G : Compléments sur les résultats

Cette annexe rassemble les tableaux de détail, les contrôles et les analyses secondaires du chapitre 6. Les numéros de section entre parenthèses renvoient au chapitre 6.

### G.1 Réseau de profil : contrôles et accord par source

Le F1 macro moyen par pli est de 0,99772, 0,99852, 0,99802, 0,99918 et 0,99754. L'écart entre le meilleur et le moins bon pli (0,00164) est du même ordre que l'écart-type entre entraînements : aucun pli n'est aberrant, ce qui est la condition pour que la moyenne sur les plis ait un sens. L'arrêt anticipé a eu lieu en moyenne à 81,4 époques (écart-type 14,7), soit bien avant le plafond de 300 époques fixé au chapitre 4 : ce plafond n'a donc jamais limité l'entraînement, et la patience de 25 époques est la contrainte qui arrête effectivement l'apprentissage.

La concordance des deux lectures du rappel EVITER est un contrôle interne : 1 − 0,99342 = 0,00658, à comparer à 47,4 / 7 215 = 0,00657. Elle n'est pas automatique, les deux valeurs étant produites par deux programmes distincts, l'évaluation imbriquée et l'analyse de couverture-risque, à partir des mêmes fichiers de prédictions hors pli.

**Accord par niveau de source.** Le tableau G.1 donne le F1 macro selon la source dont provient la règle appliquée. Les sources sont celles du chapitre 3 ; le nombre de lignes de chaque niveau est fixé par le corpus et non choisi.

::: {custom-style="LegendeTableau"}
Tableau G.1 : F1 macro du réseau de profil par niveau de source, moyenne et écart-type sur les 25 entraînements (corpus v15)
:::

| Niveau de source | Lignes de développement | F1 macro |
| --- | --- | --- |
| CPIC | 108 579 | 0,99854 ± 0,00080 |
| DPWG | 35 649 | 0,99457 ± 0,00318 |
| FDA (tableau des associations) | 27 810 | 0,99960 ± 0,00040 |
| FDA (étiquette) | 34 219 | 0,99862 ± 0,00227 |
| Health Canada (étiquette) | 1 240 | 0,99976 ± 0,00118 |
| RNPGx | 1 240 | 0,99966 ± 0,00119 |
| EMA (étiquette) | 2 440 | non interprétable (voir ci-dessous) |

Le niveau DPWG est le moins bien reproduit, avec la plus grande dispersion. Les causes de cet écart, en particulier la part de chaque médicament, n'ont pas été analysées. Les niveaux Health Canada et RNPGx ne comptent chacun que 1 240 lignes : leur F1 est élevé, mais il repose sur peu de lignes non STANDARD.


### G.2 Abstention : contrôle du programme et table de couverture-risque

Le programme qui produit cette analyse a été réécrit pour le corpus v15, celui de la version antérieure n'étant plus disponible. Il n'est pas accepté sur sa seule lecture : exécuté sur les prédictions de la version antérieure du corpus, il redonne exactement les valeurs publiées pour cette version (113,0 erreurs, 60,2 EVITER manqués sur 7 227, 8,4 faux EVITER, AUROC 0,8704 ± 0,0253 et les quatre seuils de quantile). Cette reproduction à l'identique est la justification de son emploi sur la v15.

::: {custom-style="LegendeTableau"}
Tableau G.2 : Couverture, exactitude sélective et erreurs restantes selon le seuil de confiance (corpus v15, développement)
:::

| Seuil de confiance | Couverture | Exactitude sélective | Erreurs restantes (sur 103,2) | EVITER manqués acceptés (sur 47,4) | Lignes écartées |
| --- | --- | --- | --- | --- | --- |
| 0,70 | 0,99972 | 0,99964 | 75,4 | 38,4 | 59,2 |
| 0,90 | 0,99919 | 0,99976 | 49,6 | 32,0 | 170,4 |
| 0,95 | 0,99872 | 0,99980 | 42,2 | 29,2 | 269,8 |
| 0,99 | 0,99683 | 0,99985 | 32,0 | 25,2 | 669,4 |
| 0,9965 | 0,99441 | 0,99986 | 28,6 | 23,6 | 1 180,6 |

Les quantiles de la confiance hors pli, qui définissent les seuils d'abstention de l'application selon la méthode du chapitre 4, valent sur le corpus v15 : 0,9934 pour écarter 0,5 % des prédictions, 0,9981 pour 1 %, 0,9994 pour 2 % et 0,9998 pour 5 %. Ils sont tous plus élevés que ceux de la version antérieure du corpus (0,9895, 0,9965, 0,9988 et 0,9995) : le réseau est devenu plus confiant, de sorte qu'il faut un seuil plus haut pour écarter la même part de prédictions. La dernière ligne du tableau 6.3 le chiffre : le seuil 0,9965, qui écartait 1 % des prédictions sur la version antérieure, n'en écarte plus que 0,56 % sur la v15.

### G.3 Cohérence avec des études indépendantes

L'interrogation a été refaite avec les modèles v15 : pour les 23 profils construits des 8 couples, l'action du réseau est identique à celle des modèles de la version antérieure, et elle l'est aussi pour les 43 profils d'une série élargie. Le tableau G.3 vaut donc pour le réseau v15.

::: {custom-style="LegendeTableau"}
Tableau G.3 : Concordance de sens entre l'avis du réseau et une étude indépendante, par couple gène–médicament
:::

| Couple | Étude (type, effectif) | Concordance de sens |
| --- | --- | --- |
| SLCO1B1, simvastatine | SEARCH, 2008 ; étude génomique, 85 cas et 90 témoins | oui ; l'étude porte sur 80 mg, « à éviter » est plus fort |
| HLA-B\*57:01, abacavir | Mallal, 2008 ; essai randomisé, 1 956 patients | oui ; preuve forte |
| HLA-B\*15:02, carbamazépine | Chen, 2011 ; dépistage prospectif, 4 877 patients | oui ; population taïwanaise, comparaison à une incidence historique |
| HLA-B\*58:01, allopurinol | Hung, 2005 ; cas-témoins, 51 cas et 228 témoins | oui ; population Han, l'allèle est présent chez 15 % des tolérants |
| DPYD, fluorouracile | Henricks, 2018 ; essai prospectif, 1 103 patients | oui ; pour DPYD = 0, le réseau donne « adapter la dose » et la règle « éviter » |
| CYP2C19, clopidogrel | Mega, 2010 ; méta-analyse, 9 études, 9 685 patients | oui ; patients traités par angioplastie |
| CYP2D6, codéine | Gasche, 2004 ; rapport de cas, 1 patient | même sens ; preuve faible, cas « lent » non couvert |
| CYP2D6, tamoxifène | Province, 2014 ; méta-analyse, 4 973 patientes | partielle ; effet seulement sous critères stricts |

### G.4 Comparaison des modèles : amendements, égalités et évolution

Le deuxième amendement justifie deux points propres au corpus v15. D'abord, les recherches d'hyperparamètres ont été refaites entièrement sur la v15 et non reprises de la version antérieure : le corpus v15 partage les plis du précédent et n'en diffère que de 0,85 % des lignes, de sorte que reprendre des réglages sélectionnés sur l'autre version équivaudrait à les avoir choisis en ayant vu, sous une forme presque identique, les profils qui servent de test. Le coût de ce choix est d'environ neuf heures de calcul supplémentaires. Ensuite, la configuration 35 est la seule exception : elle n'est pas re-sélectionnée, parce qu'elle est par définition le réglage figé du modèle déployé, choisi sur une version antérieure du corpus, et que la re-sélectionner la priverait de ce qu'elle mesure. Elle figure donc comme bras de référence supplémentaire, hors de la règle de décision.

La statistique principale est la moyenne sur les graines : la mesure est calculée sur l'ensemble des prédictions hors pli de chaque graine, puis moyennée. Les intervalles sont obtenus par bootstrap sur les identifiants de profil (2 000 tirages), les profils apparentés étant traités comme indépendants.

Les taux d'EVITER manqués sont le nombre de lignes EVITER manquées rapporté aux 7 215 lignes EVITER du développement. La log-loss donnée au tableau 6.1 pour la configuration 35 (0,00260) n'est pas comparable à celle de ce tableau (0,00330) : la première est la moyenne des 25 entraînements, la seconde est calculée sur l'ensemble des prédictions de chaque graine avant moyenne.

**Égalités dans la sélection des configurations.** Le premier amendement prévoyait de vérifier, pour chaque pli et chaque modèle, si la configuration retenue par la recherche imbriquée était à égalité, à cinq décimales près, avec une autre. Le contrôle a été fait sur les 200 essais de chaque recherche (40 configurations × 5 plis). Pour le réseau et pour Random Forest, la configuration retenue est unique dans chacun des cinq plis. Pour XGBoost, elle est à égalité avec au moins une autre dans quatre plis sur cinq, avec 2 à 7 configurations ex æquo, et un F1 de validation de 1,00000 dans deux plis : la recherche ne distingue plus les configurations de XGBoost à ce niveau de précision, et c'est la première configuration de la liste qui a été retenue (configurations 1, 0, 0 et 1 ; configuration 5, unique, dans le dernier pli). Le choix entre configurations ex æquo est donc arbitraire. Son effet sur les performances de XGBoost n'a pas été mesuré ; les configurations ex æquo étant indiscernables sur la validation, il n'y a pas de raison de s'attendre à un écart important, mais cela n'est pas démontré.

**Évolution par rapport à la version antérieure du corpus.** Sur l'autre version, la conclusion du protocole était que XGBoost était supérieur au réseau, statistiquement et en pratique (différence de −0,00265, intervalle entièrement sous −0,001). Sur la v15, cette conclusion ne tient plus. Deux mouvements l'expliquent arithmétiquement : les erreurs du réseau issu de la recherche imbriquée passent de 187,2 à 123,6, et celles de XGBoost de 41,8 à 82,0. Les règles révisées en v15 portent sur les médicaments qui concentraient les erreurs du réseau, en particulier la grille à deux gènes TPMT et NUDT15 des trois thiopurines et la règle à deux gènes de la fluvastatine : une étiquette qui dépend désormais de deux gènes tous deux présents à l'entrée du réseau est une fonction que le réseau peut apprendre, alors que l'étiquette antérieure dépendait d'un gène seul et était donc, pour une partie des profils, imprévisible à partir de l'entrée. Cette explication est plausible et cohérente avec la localisation des erreurs, mais elle n'est pas démontrée : aucune analyse appariée ligne par ligne entre les deux versions du corpus n'a été faite, les deux corpus n'ont pas les mêmes lignes, et la hausse des erreurs de XGBoost ne reçoit pas d'explication. Elle est donc présentée comme une hypothèse, non comme un résultat.

### G.5 Évaluation finale : modèles, méthode et sous-groupes

**Modèles évalués.** Les trois modèles (réseau en configuration 35 calibré par température, XGBoost, Random Forest) ont été réentraînés avec leurs hyperparamètres inchangés, la même graine (42) et la même validation interne de 10 % des profils, sur 1 207 profils de développement au lieu de 1 241. Les 34 profils retirés sont ceux que le pedigree du projet 1000 Genomes relie à un profil de l'ensemble final (section 3.8, point 3). Cette règle a été fixée avant toute lecture : laisser un apparenté d'un profil final à l'entraînement aurait pu rendre l'évaluation optimiste, et le retrait ne coûte que 2,7 % des profils de développement. La liste des 34 a été recalculée à partir du pedigree et n'a été acceptée qu'après avoir reproduit exactement tous les décomptes de l'audit de parenté (187 paires, 34 paires entre ensemble final et développement, 34 profils de développement distincts). Les hyperparamètres n'ont pas été re-sélectionnés, parce qu'une nouvelle recherche sur 1 207 profils aurait été un nouveau choix fait sans contrôle et que la question posée est celle de la valeur des modèles tels qu'ils ont été choisis. Les seuils d'abstention sont ceux de la section 6.3, calculés sur la validation croisée de développement. Ces modèles servent uniquement à l'évaluation ; l'application conserve ceux entraînés sur les 1 241 profils, pour lesquels aucune mesure sur l'ensemble final n'est donc disponible.

**Méthode statistique.** Les intervalles de confiance à 95 % sont obtenus par bootstrap percentile sur les 138 identifiants de profil, avec 10 000 tirages communs aux trois modèles, de sorte que les différences sont appariées. Une évaluation unique ne coûtant que quelques secondes, le nombre de tirages n'était pas limité par le calcul. Il a été porté à 10 000, au lieu des 2 000 de la section 6.5, parce que les bornes d'un intervalle percentile reposent sur les 2,5 % de tirages extrêmes : 10 000 tirages en placent 250 de chaque côté au lieu de 50, ce qui réduit l'erreur de Monte-Carlo sur les bornes. Davantage de tirages n'aurait pas réduit l'incertitude principale, qui vient du nombre de profils (138) et non du nombre de tirages. La règle de décision est celle de la section 6.5, avec la même marge de 0,001.

Les rappels du réseau sont de 0,9995 pour STANDARD, 0,9952 pour ADAPTER\_DOSE, 0,9877 pour EVITER et 0,9926 pour SURVEILLER ; son F1 macro sans la classe SURVEILLER est de 0,9942.

::: {custom-style="LegendeTableau"}
Tableau G.4 : Abstention du réseau sur l'ensemble final, aux seuils fixés sur le développement
:::

| Part visée d'abstention | Seuil | Couverture | Lignes écartées | F1 macro des lignes gardées | EVITER manqués acceptés |
| --- | --- | --- | --- | --- | --- |
| 0,5 % | 0,9934 | 0,9939 | 143 | 0,9963 | 3 sur 804 |
| 1 % (seuil de l'application) | 0,9981 | 0,9888 | 263 | 0,9974 | 2 sur 800 |
| 2 % | 0,9994 | 0,9807 | 452 | 0,9981 | 2 sur 797 |
| 5 % | 0,9998 | 0,9630 | 867 | 0,9981 | 2 sur 794 |

**Sous-groupes fixés à l'avance.** Les 34 profils finaux dont un apparenté a été retiré de l'entraînement (5 818 lignes) obtiennent un F1 macro de 0,9974 avec le réseau, 1,000 avec XGBoost et 0,9474 avec Random Forest ; les 104 autres profils (17 637 lignes) obtiennent 0,9930, 0,9985 et 0,9245. Aucun avantage des profils apparentés n'apparaît, ce qui est cohérent avec leur retrait de l'entraînement. Deux profils finaux ont un vecteur d'entrée identique à celui d'un profil de développement ; ils ont été conservés et rapportés à part, comme prévu : aucun des trois modèles ne commet d'erreur sur eux (169 et 168 lignes).

### G.6 Résultats négatifs : détail

**Médicaments jamais vus.** Un réseau recevant le profil génétique et des descripteurs du médicament, sans aucune information de directive, a été évalué sur des médicaments laissés de côté à l'entraînement (3 graines, bootstrap sur les médicaments, 400 tirages). L'AUROC pour la distinction « non STANDARD » est de 0,774 \[0,726 ; 0,823\] avec les seuls liens gène-médicament, contre 0,817 \[0,779 ; 0,855\] pour une référence qui prédit par la fréquence des classes selon le gène et le phénotype, et 0,781 \[0,730 ; 0,835\] pour les 5 plus proches voisins. La différence avec la première référence est de −0,043 \[−0,079 ; −0,009\], donc défavorable au réseau ; avec les voisins, elle est de −0,007 \[−0,043 ; +0,028\], donc non tranchée. L'ajout de l'empreinte moléculaire du médicament dégrade les résultats. En laissant de côté une classe ATC entière, puis sur les médicaments ajoutés entre deux versions du corpus, le réseau reste inférieur aux références ou le résultat n'est pas concluant.

La conclusion est que la description du médicament ne permet pas de prédire l'action pour un médicament jamais vu mieux que des références simples. Elle a deux conséquences : la branche « description du médicament » n'est pas intégrée à l'application, et le médicament y reste une sortie du réseau et non une entrée (chapitre 4). Une explication de ce résultat mérite d'être retenue : la référence par gène et phénotype est forte, parce qu'une grande partie du signal vient de la rareté du profil génétique et non du médicament. Limites : 189 médicaments seulement, descripteurs plus riches pour les médicaments déjà couverts, 3 graines.

### G.7 Protocole de la validation warfarine : détail

Les six analyses secondaires déclarées d'avance sont les suivantes.

- S1, rapport par classe et par génotype ;
- S2, comparaison descriptive avec les pourcentages DPWG ;
- S3, régression de la log-dose ajustée sur l'âge, la taille, le poids, l'amiodarone, VKORC1 (-1639, nombre d'allèles A) et l'origine, avec erreurs robustes HC3, avec et sans VKORC1 ;
- S4, patients d'origine « White » seulement ;
- S5, proportion de doses basses (≤ 21 mg par semaine), sensibilité et spécificité de l'étiquette ;
- S6, exploratoire, part de variance (R²) de la log-dose expliquée par CYP2C9, par VKORC1 et par les deux.

Le nombre de tirages du bootstrap et la graine ont été fixés dans le protocole avant le calcul ; la graine assure la reproductibilité. Le nombre de tirages n'avait pas été justifié par un calcul de précision ; il a été contrôlé après coup : avec 10 000 tirages, l'intervalle de H1 devient [0,8038 ; 0,8569] avec la même graine et [0,8037 ; 0,8570] avec une autre, contre [0,8039 ; 0,8572] avec 2 000 tirages. Les bornes sont identiques à la troisième décimale, la seule rapportée. La population principale se répartit en 4 351 patients \*1/\*1 et 1 423 porteurs d'un autre génotype (772 \*1/\*2, 503 \*1/\*3, 59 \*2/\*2, 69 \*2/\*3 et 20 \*3/\*3). Les chiffres principaux ont été recoupés par un second calcul indépendant (pandas ; scikit-learn pour les parts de variance).

### G.8 Associations publiées : définition des verdicts

Les verdicts sont définis par le protocole figé, en comptant les articles (PMID) distincts. Une ligne d'étude est concordante si l'effet publié va dans le sens de l'alerte (toxicité accrue, efficacité diminuée, ou dose et exposition dans le sens de la recommandation) ; elle compte contre la règle si l'effet va en sens inverse ou si l'étude ne trouve pas d'association. Une règle est **soutenue** si au moins un article est concordant et qu'aucun autre ne compte contre elle ; **mixte** si elle a à la fois des articles concordants et des articles contre ; **non soutenue** si elle n'a que des articles contre. Le **signal non orienté** regroupe les règles dont les seuls résultats positifs ne peuvent pas être orientés, par exemple un effet pharmacocinétique pour une règle qui ne donne pas de sens de dose. **Non tranchable** désigne les règles que la relecture manuelle n'a pas permis de classer. Les règles **non appariées** ont des études pour leur couple gène–médicament, mais aucune n'a pu être rattachée automatiquement à l'état métaboliseur de la règle ; **aucune étude** signifie qu'aucune ligne n'existe pour le couple.

### G.9 Réseau de choix : détail

Le réseau de choix a été réentraîné sur le corpus v15 selon le protocole du chapitre 4 : 44 classes ATC de niveau 4 contenant au moins deux médicaments étiquetés, 5 plis groupés par profil et 5 graines. L'ensemble final n'est pas utilisé, ce que le programme vérifie. Deux références encadrent les résultats : une référence qui ignore le profil du patient et propose pour tous les mêmes médicaments, et un choix au hasard ; ces références sont déterministes, d'où leur écart-type nul.

::: {custom-style="LegendeTableau"}
Tableau G.5 : Réseau de choix au sein d'une classe ATC4, validation croisée (44 classes, 5 plis × 5 graines, corpus v15)
:::

| Mesure | Réseau de choix | Référence sans profil | Hasard |
| --- | --- | --- | --- |
| Choix dans l'ensemble acceptable (cas informatifs) | 99,997 % ± 0,005 | 99,08 % | 55,14 % |
| Ensemble exact retrouvé | 98,92 % ± 0,08 | 34,35 % | — |
| Indice de Jaccard | 0,99706 ± 0,00034 | 0,71441 | — |
| Médicament EVITER choisi quand il en existe un dans la classe | 0,000 % ± 0,000 | 0,073 % | — |

**Ce que ces chiffres disent, et ce qu'ils ne disent pas.** La mesure « choix dans l'ensemble acceptable » ne discrimine pas : la référence qui ignore entièrement le profil atteint déjà 99,08 %, parce que dans la plupart des classes le même médicament convient à presque tous les patients ; elle est rapportée pour cette raison même, et non comme un résultat. Les deux mesures informatives sont l'ensemble exact retrouvé et l'indice de Jaccard, où la référence sans profil descend respectivement à 34,35 % et 0,714 : c'est là que la lecture du profil se voit. Une mesure y répond plus directement : parmi les cas informatifs, la référence sans profil propose un médicament hors de l'ensemble acceptable dans 72 cas, et le réseau choisit correctement dans la totalité d'entre eux, pour les cinq graines. Le nombre de cas concernés est petit, ce qui limite la portée du constat, mais il est obtenu sans exception. Sur le critère de sécurité propre à cette tâche, le réseau n'a jamais proposé un médicament étiqueté EVITER, dans aucun pli et avec aucune graine, alors que la référence sans profil le fait dans 0,073 % des cas où un tel médicament existe dans la classe.

**Limite de principe.** Tous ces résultats mesurent un accord avec la cible définie au chapitre 4, qui est une convention du projet. Un score élevé signifie donc que le réseau reproduit fidèlement cette convention, et non qu'il désigne le meilleur médicament pour le patient. S'y ajoutent l'absence de recherche d'hyperparamètres pour ce réseau (section 4.10) et le fait qu'il n'a pas été évalué sur l'ensemble final, le protocole de la section 6.7 portant sur la tâche principale du travail.


### G.10 Comparaison à PharmCAT : les 136 lignes non retrouvées

Chaque motif a été lu après le calcul (section 8.3).

- **Warfarine (98 lignes).** 91 lignes ne portent aucune différence d'action ou de dose. Elles viennent de la formulation (texte du projet en français, « no action is needed » contre « no action is required », numérotation « 1. » en tête du texte) ou de la structure : l'application affiche une règle par gène (CYP2C9 et VKORC1), alors que PharmCAT n'affiche que la recommandation du gène qui demande une action, de sorte que la règle « aucune action » de l'autre gène n'a pas de vis-à-vis. Les 7 autres lignes sont des écarts réels, tous liés au codage de CYP2C9 par score d'activité : chez 5 personnes de génotype \*1/\*5, \*1/\*8 ou \*1/\*11, l'application applique la règle DPWG de \*1/\*2 (aucune action), qui a le même score d'activité, alors que PharmCAT, qui lit la directive allèle par allèle, recommande 65 % de la dose initiale ; chez 2 personnes métaboliseurs lents, l'application affiche 20 % de la dose et PharmCAT 45 %, ce qui reste la même classe d'action.
- **Siponimod (8 lignes).** Les 8 écarts ont la même cause que ceux de la warfarine : le codage par score d'activité applique à des génotypes rares la règle d'un génotype fréquent de même score.
- **Thiopurines (8 lignes pour chacun des trois médicaments).** Pour 6 personnes, PyPGx et PharmCAT n'appellent pas le même phénotype NUDT15 ; pour 2 personnes, l'application n'applique que la règle TPMT. Ce sont des différences d'appel de génotype, non de règle.
- **Flucytosine (4 lignes).** Le texte du projet est une traduction française de la recommandation DPWG (« rester attentif aux effets graves »), absente de la liste d'équivalences ; le contenu est le même.
- **Fluvastatine (1 ligne)** et **sertraline (1 ligne).** Pour la fluvastatine, l'application déclare SLCO1B1 non déterminé et n'applique que la règle CYP2C9 (cas détaillé en annexe B.2) ; pour la sertraline, la règle combinée CYP2B6 et CYP2C19 diffère de celle de PharmCAT pour une personne.

