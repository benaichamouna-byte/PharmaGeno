## Chapitre 6 : Résultats

Ce chapitre rapporte les résultats mesurés sur le corpus v15 selon le protocole du chapitre 4. Il est organisé dans l'ordre des questions de recherche : accord du réseau avec les règles (RQ1), qualité de ses probabilités (RQ3), utilité de l'abstention (RQ3), choix au sein d'une classe thérapeutique, comparaison aux modèles à base d'arbres (RQ2), concordance avec des études indépendantes (RQ6), puis résultats négatifs (RQ4 et RQ5). La validation sur patients réels (RQ7) fait l'objet des chapitres 7 et 8 : elle ne figure pas ici parce qu'elle ne porte pas sur les mêmes données et ne mesure pas la même chose.

Une mise en garde s'applique à toutes les mesures qui suivent : les étiquettes proviennent du moteur de règles CPIC, DPWG, RNPGx, FDA, EMA et Health Canada (chapitre 3). Un score élevé signifie que le modèle reproduit ces règles, non que l'avis est juste cliniquement. Les écarts-types décrivent la variabilité d'entraînement (5 plis × 5 graines) ; ils ne mesurent pas l'incertitude due au choix des profils, puisque les graines partagent les mêmes lignes. C'est pourquoi les comparaisons entre modèles (section 6.5) utilisent des intervalles de confiance obtenus par bootstrap sur les identifiants de profil, et non ces écarts-types.

L'ensemble final de 138 profils (23 455 lignes) n'a pas été lu : toutes les valeurs de ce chapitre viennent des 1 241 profils de développement, soit 211 177 lignes, dont 181 262 STANDARD, 18 188 ADAPTER\_DOSE, 7 215 EVITER et 4 512 SURVEILLER. Ces quatre effectifs servent de dénominateurs à tout le chapitre.

### 6.1 Réseau de profil : accord avec les règles

Le tableau 6.1 donne la moyenne et l'écart-type des 25 entraînements (5 plis × 5 graines) de la configuration 35, c'est-à-dire du réseau déployé dans l'application, évalué sur ses prédictions hors pli après calibration par température.

::: {custom-style="LegendeTableau"}
Tableau 6.1 : Réseau de profil, moyenne et écart-type sur les 25 entraînements hors pli (corpus v15)
:::

| Mesure | Valeur |
| --- | --- |
| F1 macro (4 actions) | 0,99820 ± 0,00075 |
| Exactitude | 0,99951 ± 0,00024 |
| Précision de la classe EVITER | 0,99878 ± 0,00119 |
| Rappel de la classe EVITER | 0,99342 ± 0,00334 |
| Log-loss | 0,00260 ± 0,00135 |
| ECE (15 intervalles) | 0,00029 ± 0,00012 |
| F1 macro sans la classe SURVEILLER | **[à compléter]** |
| Rappel des classes STANDARD, ADAPTER\_DOSE et SURVEILLER | **[à compléter]** |

Le F1 macro moyen par pli est de 0,99772, 0,99852, 0,99802, 0,99918 et 0,99754. L'écart entre le meilleur et le moins bon pli (0,00164) est du même ordre que l'écart-type entre entraînements : aucun pli n'est aberrant, ce qui est la condition pour que la moyenne sur les plis ait un sens. L'arrêt anticipé a eu lieu en moyenne à 81,4 époques (écart-type 14,7), soit bien avant le plafond de 300 époques fixé au chapitre 4 : ce plafond n'a donc jamais limité l'entraînement, et la patience de 25 époques est la contrainte qui arrête effectivement l'apprentissage.

**Erreurs.** Le réseau commet en moyenne 103,2 erreurs sur 211 177 lignes, soit 0,049 %. Parmi les 7 215 lignes EVITER, 47,4 sont manquées (0,657 %) et 8,8 lignes sont prédites EVITER à tort. Les deux lectures du rappel EVITER concordent : 1 − 0,99342 = 0,00658, à comparer à 47,4 / 7 215 = 0,00657. Cette concordance n'est pas automatique, les deux valeurs étant produites par deux programmes distincts (l'évaluation imbriquée et l'analyse de couverture-risque) à partir des mêmes fichiers de prédictions hors pli ; elle sert ici de contrôle de cohérence interne.

La répartition des erreurs par médicament et le F1 macro par niveau de source n'ont pas été recalculés sur le corpus v15 **[à compléter]**. Les valeurs correspondantes de la version antérieure du corpus ne sont pas reprises : les règles des thiopurines, de la warfarine et de la fluvastatine ont changé, et ce sont précisément les médicaments qui concentraient les erreurs.

**Un niveau de source ne peut pas recevoir de F1 macro interprétable.** Le niveau « EMA-étiquette » ne compte que 2 440 lignes et 2 médicaments (erlotinib : 987 STANDARD et 253 SURVEILLER ; lonafarnib : 1 199 STANDARD et 1 ADAPTER\_DOSE). Cette unique ligne ADAPTER\_DOSE vient de la règle lonafarnib / CYP3A4 de valeur 0, et un seul des 1 379 profils du corpus porte cette valeur (1 286 profils à 1,0, 50 à 0,5, 42 non typés). Hors pli, aucun profil d'entraînement ne porte donc cette valeur, et aucun modèle ne peut l'apprendre à partir de ce corpus. Le F1 macro étant la moyenne sur les classes présentes, manquer cette seule ligne fait tomber le F1 de la classe à 0 et le F1 macro du niveau à environ 2/3, quel que soit le modèle. Ce nombre mesure la taille de l'échantillon, non la performance : pour ce niveau, seuls les effectifs par classe sont rapportés. Ce cas est aussi un exemple concret de valeur génétique jamais vue à l'entraînement, situation traitée en section 6.7 et à la section 8.5.

### 6.2 Calibration

La température ajustée sur la validation interne de chaque entraînement vaut en moyenne 0,198, avec un minimum de 0,05 et un maximum de 0,269. L'ECE hors pli après calibration est de 0,00029 ± 0,00012.

Une température inférieure à 1 rend les probabilités plus tranchées : le réseau brut est donc sous-confiant sur ses prédictions correctes. Le lissage d'étiquettes de 0,05 (chapitre 4) y contribue vraisemblablement, puisqu'il interdit à la cible d'atteindre 1 ; cette interprétation n'a pas été vérifiée par une ablation du lissage et reste une hypothèse.

Deux réserves portent sur ce résultat. D'abord, le minimum observé, 0,05, est exactement la borne inférieure de l'intervalle de recherche fixé au chapitre 4 : pour au moins un entraînement, l'optimum se trouve à la borne ou au-delà, et la valeur retenue est alors contrainte par l'intervalle et non par les données. Élargir l'intervalle aurait rendu ces entraînements comparables aux autres ; l'intervalle n'a pas été modifié, parce qu'il avait été fixé avant les mesures et que le modifier après coup aurait transformé un réglage a priori en réglage choisi au vu des résultats. Ensuite, une ECE aussi basse s'obtient en partie parce que presque toutes les lignes sont correctes et très confiantes : la mesure est dominée par les lignes faciles et ne démontre pas que les probabilités sont bien calibrées sur les lignes rares, là où se trouvent les erreurs. C'est la section 6.3 qui examine ce point. Aucun diagramme de fiabilité n'est présenté **[à compléter]**.

### 6.3 Abstention

L'analyse de couverture-risque mesure si la confiance du réseau permet de repérer ses propres erreurs. Elle porte sur les prédictions hors pli calibrées des 211 177 lignes de développement, moyennées sur les 5 graines. Aucun seuil n'est choisi au vu de ces données : les seuils du tableau 6.2 sont des valeurs rondes fixées d'avance, et les quantiles rapportés plus bas sont des descriptions de la distribution, non des optimisations.

Le programme qui produit cette analyse a été réécrit pour le corpus v15, celui de la version antérieure n'étant plus disponible. Il n'est pas accepté sur sa seule lecture : exécuté sur les prédictions de la version antérieure du corpus, il redonne exactement les valeurs publiées pour cette version (113,0 erreurs, 60,2 EVITER manqués sur 7 227, 8,4 faux EVITER, AUROC 0,8704 ± 0,0253 et les quatre seuils de quantile). Cette reproduction à l'identique est la justification de son emploi sur la v15.

L'aire sous la courbe ROC de la confiance, employée comme indicateur d'erreur, est de 0,8696 ± 0,0115. Les 1 % de lignes les moins confiantes (2 112 lignes) contiennent 77,0 % des erreurs, et les 10 % les moins confiantes 80,3 %. La confiance est donc un indicateur utile mais partiel : passer de 1 % à 10 % de lignes écartées, soit dix fois plus de prédictions perdues, ne récupère que 3,3 points d'erreurs supplémentaires. Cela signifie que les erreurs restantes ne sont pas des hésitations mais des erreurs affirmées.

::: {custom-style="LegendeTableau"}
Tableau 6.2 : Couverture, exactitude sélective et erreurs restantes selon le seuil de confiance (corpus v15)
:::

| Seuil de confiance | Couverture | Exactitude sélective | Erreurs restantes (sur 103,2) | EVITER manqués acceptés (sur 47,4) | Lignes écartées |
| --- | --- | --- | --- | --- | --- |
| 0,70 | 0,99972 | 0,99964 | 75,4 | 38,4 | 59,2 |
| 0,90 | 0,99919 | 0,99976 | 49,6 | 32,0 | 170,4 |
| 0,95 | 0,99872 | 0,99980 | 42,2 | 29,2 | 269,8 |
| 0,99 | 0,99683 | 0,99985 | 32,0 | 25,2 | 669,4 |
| 0,9965 | 0,99441 | 0,99986 | 28,6 | 23,6 | 1 180,6 |

Les quantiles de la confiance hors pli, qui définissent les seuils d'abstention de l'application selon la méthode du chapitre 4, valent sur le corpus v15 : 0,9934 pour écarter 0,5 % des prédictions, 0,9981 pour 1 %, 0,9994 pour 2 % et 0,9998 pour 5 %. Ils sont tous plus élevés que ceux de la version antérieure du corpus (0,9895, 0,9965, 0,9988 et 0,9995) : le réseau est devenu plus confiant, de sorte qu'il faut un seuil plus haut pour écarter la même part de prédictions. La dernière ligne du tableau 6.2 le chiffre : le seuil 0,9965, qui écartait 1 % des prédictions sur la version antérieure, n'en écarte plus que 0,56 % sur la v15.

**Lecture.** L'abstention retire une part importante des erreurs, mais pas celles qui comptent le plus. Au seuil le plus strict du tableau, la moitié des EVITER manqués subsiste (23,6 sur 47,4), alors que le quart seulement des erreurs totales subsiste (28,6 sur 103,2) : les EVITER manqués sont donc, en proportion, deux fois plus résistants à l'abstention que les autres erreurs. C'est le résultat le plus important de cette section, et il est défavorable : le critère de sécurité du protocole est précisément celui que la confiance du réseau protège le moins. L'explication tient à la nature de la mesure. L'incertitude du réseau exprime son hésitation entre des étiquettes produites par des règles déterministes ; une règle appliquée à un génotype rare donne une étiquette franche, que le réseau prédit à tort avec une confiance élevée faute d'avoir vu ce génotype. L'incertitude ne peut donc pas signaler qu'une règle est insuffisante, ni qu'un génotype est hors du domaine appris : ce sont deux protections distinctes, assurées dans l'application par l'affichage de la règle et par le statut « hors domaine » (chapitre 5).

Un seuil portant spécifiquement sur la probabilité de la classe EVITER n'est pas proposé. Un tel seuil doit être fixé a priori sur la validation interne ; le fixer ici, sur les mêmes prédictions hors pli qui servent à le mesurer, produirait une valeur optimiste et inutilisable **[à compléter]**.

::: {custom-style="FigureImg"}
![](fig/fig_6_1.png){width=15cm}
:::

::: {custom-style="LegendeFigure"}
Figure 6.1 : Effet de l'abstention sur les erreurs restantes et sur les EVITER manqués acceptés, selon le seuil de confiance (corpus v15).
:::

### 6.4 Réseau de choix au sein d'une classe

Le réseau de choix n'a pas été réentraîné sur le corpus v15 **[à compléter]**. Les résultats de sa validation croisée portent donc sur la version antérieure du corpus et ne sont pas transposables telles quelles : les règles révisées en v15 touchent trois médicaments de la classe des thiopurines et deux statines, qui entrent dans la cible du réseau de choix, et sa cible est construite à partir des actions du moteur de règles (chapitre 4). Ce point est repris parmi les limites (section 6.8).

Ce que la version antérieure a mesuré reste utile sur un point, indépendant du corpus : la métrique « choix dans l'ensemble des médicaments acceptables » atteint déjà 99,09 % avec une référence qui ignore le profil du patient et propose les mêmes médicaments pour tous. Cette métrique ne discrimine donc pas et ne doit pas être présentée comme un résultat. Les deux mesures informatives sont l'ensemble exact retrouvé et l'indice de Jaccard, parce que la référence sans profil y descend respectivement à 38,9 % et 0,7275.

### 6.5 Comparaison avec XGBoost et Random Forest

Cette comparaison est la réponse à RQ2 et le test de l'hypothèse principale du mémoire. Elle suit le protocole figé avant tout résultat, complété par deux amendements écrits avant la lecture des résultats : validation croisée à 5 plis groupés par identifiant de profil, même validation interne, 40 configurations choisies par recherche imbriquée pour chaque modèle, 5 graines, probabilités calibrées par température pour les trois modèles.

Le deuxième amendement justifie deux points propres au corpus v15. D'abord, les recherches d'hyperparamètres ont été refaites entièrement sur la v15 et non reprises de la version antérieure : le corpus v15 partage les plis du précédent et n'en diffère que de 0,85 % des lignes, de sorte que reprendre des réglages sélectionnés sur l'autre version équivaudrait à les avoir choisis en ayant vu, sous une forme presque identique, les profils qui servent de test. Le coût de ce choix est d'environ neuf heures de calcul supplémentaires. Ensuite, la configuration 35 est la seule exception : elle n'est pas re-sélectionnée, parce qu'elle est par définition le réglage figé du modèle déployé, choisi sur une version antérieure du corpus, et que la re-sélectionner la priverait de ce qu'elle mesure. Elle figure donc comme bras de référence supplémentaire, hors de la règle de décision.

La statistique principale est la moyenne sur les graines : la mesure est calculée sur l'ensemble des prédictions hors pli de chaque graine, puis moyennée. Les intervalles sont obtenus par bootstrap sur les identifiants de profil (2 000 tirages), les profils apparentés étant traités comme indépendants.

::: {custom-style="LegendeTableau"}
Tableau 6.3 : Comparaison du réseau, de XGBoost et de Random Forest (corpus v15, moyenne de 5 graines)
:::

| Modèle | F1 macro | EVITER manqués (n) | Taux d'EVITER manqués | Erreurs (n) | ECE |
| --- | --- | --- | --- | --- | --- |
| Réseau (recherche imbriquée) | 0,997943 \[0,997316 ; 0,998484\] | 51,8 | 0,72 % | 123,6 | 0,00014 |
| XGBoost | 0,998288 \[0,997676 ; 0,998828\] | 13,8 | 0,19 % | 82,0 | 0,00030 |
| Random Forest | 0,992687 \[0,990923 ; 0,994187\] | 108,2 | 1,50 % | 655,6 | **[à compléter]** |
| Réseau, configuration 35 figée (modèle de l'application) | 0,998197 \[0,997651 ; 0,998674\] | 47,4 | 0,66 % | 103,2 | 0,00016 |

Les taux d'EVITER manqués sont le nombre de lignes EVITER manquées rapporté aux 7 215 lignes EVITER du développement. Les log-loss des quatre bras et les intervalles des comptes d'erreurs ne sont pas repris ici **[à compléter]**. La log-loss donnée au tableau 6.1 pour la configuration 35 n'est pas transposable dans ce tableau : elle est la moyenne des 25 entraînements, alors que les colonnes ci-dessus sont calculées sur l'ensemble des prédictions de chaque graine avant moyenne.

**Décisions selon la règle figée du protocole.** La règle compare la différence de F1 macro à une marge d'équivalence pratique de 0,001, fixée avant les mesures : un modèle est déclaré supérieur si la borne basse de l'intervalle dépasse 0, les deux modèles sont déclarés équivalents si l'intervalle entier tient dans ±0,001, et la différence est déclarée non tranchée sinon.

- Réseau moins XGBoost = −0,000345 \[−0,00106 ; +0,00034\] : **non tranché**. L'intervalle contient 0, donc aucune différence n'est démontrée statistiquement ; il dépasse la marge d'un côté, donc l'équivalence n'est pas démontrée non plus.
- XGBoost moins le réseau en configuration 35 = +0,000091 \[−0,00052 ; +0,00076\] : **équivalents**. L'intervalle entier tient dans ±0,001.
- Réseau moins Random Forest = +0,00526 : **réseau supérieur** \[à compléter : intervalle\].
- XGBoost moins Random Forest = +0,00560 : **XGBoost supérieur** \[à compléter : intervalle\].

**Lecture.** Sur le critère principal du protocole, le réseau et XGBoost ne sont pas séparés par ces données : la différence de F1 macro est inférieure au millième et son intervalle contient zéro. Pour la configuration effectivement déployée dans l'application, le protocole conclut à l'équivalence avec XGBoost. Les deux modèles dominent en revanche nettement Random Forest, dont le F1 macro est inférieur de plus de cinq millièmes et qui commet six fois plus d'erreurs que XGBoost.

Ce résultat ne doit pas être lu comme une supériorité du réseau. « Non tranché » signifie que la mesure ne permet pas de départager, et « équivalents » que l'écart est trop petit pour compter en pratique ; ni l'un ni l'autre n'établit que le réseau fait mieux. La question de recherche RQ2 demandait si le réseau était plus performant que les modèles à base d'arbres : la réponse mesurée est qu'il ne l'est pas, et qu'il n'est pas non plus moins performant au sens du F1 macro.

**Le critère de sécurité, lui, est tranché, et en défaveur du réseau.** Le réseau issu de la recherche imbriquée manque 38,0 lignes EVITER de plus que XGBoost, avec un intervalle à 95 % de \[23,2 ; 54,4\] qui exclut zéro. Sur le critère qui compte pour un outil d'aide à la prescription, XGBoost reste donc le meilleur des deux, et cet écart ne s'explique pas par le hasard d'entraînement. Ce critère n'a pas de règle de décision formelle dans le protocole, ce qui est une faiblesse du protocole : la métrique désignée comme mesure de sécurité est la seule à ne pas disposer d'un critère écrit à l'avance.

**La calibration est devenue un avantage du réseau.** Sur la version antérieure du corpus, l'ECE de XGBoost après calibration était meilleure que celle du réseau ; sur la v15, l'ordre est inversé (0,00014 et 0,00016 pour les deux bras du réseau, contre 0,00030 pour XGBoost). Cette inversion est rapportée telle quelle, mais elle ne porte pas de conclusion : il s'agit de trois valeurs inférieures à 0,0004 sur une tâche où plus de 99,9 % des lignes sont correctement prédites, et aucun intervalle de confiance n'a été calculé sur ces ECE. L'énoncé défendable est que la calibration des trois modèles est bonne et que leurs écarts ne sont pas interprétables à ce niveau.

**Les erreurs des deux modèles ne sont presque pas les mêmes.** Sur la statistique secondaire, qui agrège les probabilités des cinq graines avant de prédire, le réseau commet 94 erreurs, XGBoost 80 et Random Forest 650 ; mais seules 9 lignes sont erronées chez le réseau et chez XGBoost simultanément. Autrement dit, 85 des 94 erreurs du réseau sont correctement traitées par XGBoost, et 71 des 80 erreurs de XGBoost le sont par le réseau. Ce recouvrement très faible est une mesure, et non une interprétation ; elle justifie après coup un choix de conception de l'application, qui affiche l'avis de XGBoost comme second avis et signale les désaccords (chapitre 5), là où ce choix n'était jusqu'ici qu'une précaution. Elle indique aussi une piste : une combinaison des deux modèles pourrait descendre vers l'ordre de dix erreurs, chiffre qu'aucun des deux n'atteint seul. Cette piste n'a pas été testée, et elle ne le sera pas dans ce travail : une règle de combinaison choisie au vu de ces mêmes prédictions hors pli serait un réglage déguisé en résultat, et sa valeur devrait être établie sur des données non lues.

**Évolution par rapport à la version antérieure du corpus.** Sur l'autre version, la conclusion du protocole était que XGBoost était supérieur au réseau, statistiquement et en pratique (différence de −0,00265, intervalle entièrement sous −0,001). Sur la v15, cette conclusion ne tient plus. Deux mouvements l'expliquent arithmétiquement : les erreurs du réseau issu de la recherche imbriquée passent de 187,2 à 123,6, et celles de XGBoost de 41,8 à 82,0. Les règles révisées en v15 portent sur les médicaments qui concentraient les erreurs du réseau, en particulier la grille à deux gènes TPMT et NUDT15 des trois thiopurines et la règle à deux gènes de la fluvastatine : une étiquette qui dépend désormais de deux gènes tous deux présents à l'entrée du réseau est une fonction que le réseau peut apprendre, alors que l'étiquette antérieure dépendait d'un gène seul et était donc, pour une partie des profils, imprévisible à partir de l'entrée. Cette explication est plausible et cohérente avec la localisation des erreurs, mais elle n'est pas démontrée : aucune analyse appariée ligne par ligne entre les deux versions du corpus n'a été faite, les deux corpus n'ont pas les mêmes lignes, et la hausse symétrique des erreurs de XGBoost ne reçoit pas d'explication. Elle est donc présentée comme une hypothèse, non comme un résultat.

::: {custom-style="FigureImg"}
![](fig/fig_6_2.png){width=15cm}
:::

::: {custom-style="LegendeFigure"}
Figure 6.2 : Comparaison du réseau, de XGBoost et de Random Forest sur le corpus v15 : F1 macro et taux d'EVITER manqués (moyenne de 5 graines, intervalle de confiance à 95 % par bootstrap sur les profils).
:::

**Limites de cette comparaison.** L'accord est mesuré avec les règles, non avec la clinique. La parenté entre profils n'est pas contrôlée dans le bootstrap. Quatre comparaisons sont rapportées sans correction de multiplicité ; la première, celle du réseau et de XGBoost, est la comparaison principale désignée par le protocole, les autres sont secondaires. XGBoost et Random Forest sont un modèle unique recevant l'identifiant du médicament comme variable, alors que le réseau est multitâche et prédit les 189 médicaments d'un seul coup : l'égalité de protocole porte sur les plis, le réglage et la calibration, non sur la forme du problème posé à chaque modèle. Le contrôle des égalités de F1 à cinq décimales dans la sélection des configurations, prévu par le premier amendement, n'est pas fait **[à compléter]**. Enfin, l'évaluation sur les 138 profils réservés reste à faire.

### 6.6 Cohérence avec des études indépendantes (exploratoire)

Pour 8 couples gène-médicament, le sens de l'avis du réseau a été comparé à une étude clinique indépendante de CPIC et de DPWG. Cette analyse est exploratoire pour trois raisons, énoncées avant son résultat : le réseau a été interrogé avec des profils construits (tous les gènes à la valeur normale, un seul modifié) et non avec des patients ; les modèles utilisés sont ceux d'une version antérieure du corpus et le test n'a pas été refait avec les modèles v15 **[à compléter]** ; seuls les résumés des articles ont été lus. Les huit couples ont été retenus parce qu'ils sont les seuls pour lesquels une étude clinique de référence a pu être identifiée et lue ; ce n'est pas un échantillon des 189 médicaments.

::: {custom-style="LegendeTableau"}
Tableau 6.4 : Concordance de sens entre l'avis du réseau et une étude indépendante, par couple gène–médicament
:::

| Couple | Étude (type, effectif) | Concordance de sens |
| --- | --- | --- |
| SLCO1B1, simvastatine | SEARCH, 2008 ; étude génomique, 85 cas et 90 témoins | oui ; l'étude porte sur 80 mg, « à éviter » est plus fort |
| HLA-B\*57:01, abacavir | Mallal, 2008 ; essai randomisé, 1 956 patients | oui ; preuve forte |
| HLA-B\*15:02, carbamazépine | Chen, 2011 ; dépistage prospectif, 4 877 patients | oui ; population taïwanaise, comparaison à une incidence historique |
| HLA-B\*58:01, allopurinol | Hung, 2005 ; cas-témoins, 51 cas et 228 témoins | oui ; population Han, l'allèle est présent chez 15 % des tolérants |
| DPYD, fluorouracile | Henricks, 2018 ; essai prospectif, 1 103 patients | oui |
| CYP2C19, clopidogrel | Mega, 2010 ; méta-analyse, 9 études, 9 685 patients | oui ; patients traités par angioplastie |
| CYP2D6, codéine | Gasche, 2004 ; rapport de cas, 1 patient | même sens ; preuve faible, cas « lent » non couvert |
| CYP2D6, tamoxifène | Province, 2014 ; méta-analyse, 4 973 patientes | partielle ; effet seulement sous critères stricts |

Le sens est le même dans les 8 cas. Cet accord ne porte que sur la direction de l'effet : il ne montre pas que la recommandation améliore la prise en charge, et il ne porte pas sur l'intensité de l'avis. Pour la simvastatine et le tamoxifène, l'intensité « à éviter » dépasse ce que montre l'étude. Les couples des thiopurines, de UGT1A1 et de l'irinotécan, des inhibiteurs de la pompe à protons, du tacrolimus, des médicaments liés à G6PD et des antidépresseurs tricycliques n'ont pas de source lue : l'absence d'un couple dans ce tableau signifie qu'aucune étude n'a été lue pour lui, non que la concordance y serait moins bonne.

### 6.7 Résultats exploratoires négatifs

Deux pistes ont été abandonnées après mesure. Elles sont rapportées parce qu'elles répondent à RQ4 et RQ5 par la négative et qu'elles délimitent ce que l'application ne fait pas.

**Médicaments jamais vus.** Un réseau recevant le profil génétique et des descripteurs du médicament, sans aucune information de directive, a été évalué sur des médicaments laissés de côté à l'entraînement (3 graines, bootstrap sur les médicaments, 400 tirages). L'AUROC pour la distinction « non STANDARD » est de 0,774 \[0,726 ; 0,823\] avec les seuls liens gène-médicament, contre 0,817 \[0,779 ; 0,855\] pour une référence qui prédit par la fréquence des classes selon le gène et le phénotype, et 0,781 \[0,730 ; 0,835\] pour les 5 plus proches voisins. La différence avec la première référence est de −0,043 \[−0,079 ; −0,009\], donc défavorable au réseau ; avec les voisins, elle est de −0,007 \[−0,043 ; +0,028\], donc non tranchée. L'ajout de l'empreinte moléculaire du médicament dégrade les résultats. En laissant de côté une classe ATC entière, puis sur les médicaments ajoutés entre deux versions du corpus, le réseau reste inférieur aux références ou le résultat n'est pas concluant.

La conclusion est que la description du médicament ne permet pas de prédire l'action pour un médicament jamais vu mieux que des références simples. Elle a deux conséquences : la branche « description du médicament » n'est pas intégrée à l'application, et le médicament y reste une sortie du réseau et non une entrée (chapitre 4). Une explication de ce résultat mérite d'être retenue : la référence par gène et phénotype est forte, parce qu'une grande partie du signal vient de la rareté du profil génétique et non du médicament. Limites : 189 médicaments seulement, descripteurs plus riches pour les médicaments déjà couverts, 3 graines.

**Associations publiées.** Sur 2 141 lignes d'associations ClinPGx (256 médicaments, 80 gènes), la direction publiée de l'effet est prédite avec une exactitude de 0,638 ± 0,007 pour une séparation par couple gène-médicament, contre 0,581 pour la classe majoritaire et 0,656 pour une loi a priori par gène et catégorie ; pour une séparation par variant, 0,641 ± 0,008 contre 0,620. Le signal est faible (AUROC 0,651) et, sur des couples jamais vus, une loi a priori simple fait aussi bien ou mieux. Les étiquettes sont de plus bruitées : 957 des 2 141 lignes appartiennent à des combinaisons où des directions contradictoires sont publiées. Cette piste n'a pas été poursuivie.

### 6.8 Synthèse et limites des résultats

**Mesuré.** Sur 211 177 lignes hors pli, le réseau de profil déployé reproduit les étiquettes issues des règles avec un F1 macro de 0,99820 ± 0,00075 et manque 0,66 % des situations à éviter. Ses probabilités sont bien calibrées globalement (ECE 0,00029) après mise à l'échelle de la température. La confiance repère les erreurs de façon partielle (AUROC 0,870) et protège moins bien les EVITER manqués que les autres erreurs. Sous un protocole identique, le réseau et XGBoost ne sont pas départagés sur le F1 macro, et sont déclarés équivalents pour la configuration déployée ; les deux dominent nettement Random Forest. XGBoost conserve un avantage démontré sur le critère de sécurité, avec 38 EVITER manqués de moins. Les erreurs des deux modèles se recouvrent très peu, 9 lignes sur environ 90 de chaque côté. Le sens des avis concorde avec 8 études pour les 8 couples testés.

**Non mesuré ou non démontré.**

- La justesse clinique des avis. Toutes les mesures de ce chapitre portent sur l'accord avec des règles ; une seule règle est confrontée à des patients réels (chapitre 7).
- La supériorité du réseau sur les modèles à base d'arbres. Elle n'est pas établie : la comparaison conclut à une différence non tranchée sur le F1 macro, à l'équivalence pour la configuration déployée, et à un désavantage du réseau sur la sécurité. L'hypothèse principale du mémoire n'est donc pas confirmée par cette mesure.
- Les performances du réseau de choix sur le corpus v15, celui-ci n'ayant pas été réentraîné (section 6.4).
- Les performances sur l'ensemble final de 138 profils, volontairement non lu à ce stade.
- Les performances de la chaîne complète depuis un fichier VCF : les valeurs de ce chapitre portent sur des profils du corpus, non sur des profils lus dans un VCF. Cette question est traitée au chapitre 8.
- La généralisation à un médicament jamais vu (résultat négatif, section 6.7) et à une combinaison de gènes jamais observée, dont le cas du lonafarnib donne un exemple (section 6.1).
- La répartition des erreurs par médicament et par niveau de source sur le corpus v15 **[à compléter]**.

Les essais abandonnés, négatifs ou corrigés sont récapitulés dans l'annexe A.
