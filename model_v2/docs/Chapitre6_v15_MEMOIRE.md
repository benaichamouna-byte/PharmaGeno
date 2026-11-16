## Chapitre 6 : Résultats

Ce chapitre rapporte les résultats mesurés sur le corpus v15 selon le protocole du chapitre 4, dans l'ordre des questions de recherche : accord du réseau avec les règles (RQ1), calibration et abstention (RQ3), choix au sein d'une classe thérapeutique, comparaison aux modèles à base d'arbres (RQ2), concordance avec des études indépendantes (RQ6), évaluation unique sur l'ensemble final réservé, puis résultats négatifs (RQ4 et RQ5). La validation sur patients réels (RQ7) fait l'objet des chapitres 7 et 8. Les tableaux de détail, les contrôles et les analyses secondaires sont en annexe G.

Une mise en garde s'applique à toutes les mesures qui suivent : les étiquettes proviennent du moteur de règles CPIC, DPWG, RNPGx, FDA, EMA et Health Canada (chapitre 3). Un score élevé signifie que le modèle reproduit ces règles, non que l'avis est juste cliniquement. Les écarts-types décrivent la variabilité d'entraînement (5 plis × 5 graines) ; ils ne mesurent pas l'incertitude due au choix des profils, puisque les graines partagent les mêmes lignes. C'est pourquoi les comparaisons entre modèles (sections 6.5 et 6.7) utilisent des intervalles de confiance obtenus par bootstrap sur les identifiants de profil.

Les sections 6.1 à 6.6 portent sur les 1 241 profils de développement, soit 211 177 lignes, dont 181 262 STANDARD, 18 188 ADAPTER\_DOSE, 7 215 EVITER et 4 512 SURVEILLER. La section 6.7 porte sur les 138 profils de l'ensemble final (23 455 lignes), lus une seule fois après que toutes les décisions des sections précédentes ont été prises.

### 6.1 Réseau de profil : accord avec les règles

Le tableau 6.1 donne la moyenne et l'écart-type des 25 entraînements de la configuration 35, c'est-à-dire du réseau déployé, sur ses prédictions hors pli après calibration.

::: {custom-style="LegendeTableau"}
Tableau 6.1 : Réseau de profil, moyenne et écart-type sur les 25 entraînements hors pli (corpus v15)
:::

| Mesure | Valeur |
| --- | --- |
| F1 macro (4 actions) | 0,99820 ± 0,00075 |
| F1 macro sans la classe SURVEILLER | 0,99779 ± 0,00100 |
| Exactitude | 0,99951 ± 0,00024 |
| Précision de la classe EVITER | 0,99878 ± 0,00119 |
| Rappel de la classe EVITER | 0,99342 ± 0,00334 |
| Rappel de la classe ADAPTER\_DOSE | 0,99850 ± 0,00106 |
| Rappel de la classe SURVEILLER | 0,99978 ± 0,00064 |
| Rappel de la classe STANDARD | 0,99985 ± 0,00013 |
| Log-loss | 0,00260 ± 0,00135 |
| ECE (15 intervalles) | 0,00029 ± 0,00012 |

Le F1 macro sans la classe SURVEILLER est rapporté parce que SURVEILLER est la classe dont la définition varie le plus d'une source à l'autre (chapitre 3) : il est légèrement plus bas que le F1 à quatre classes, ce qui montre que SURVEILLER est au contraire l'une des classes les mieux reproduites. La classe la moins bien reproduite est EVITER, celle qui compte le plus pour la sécurité. Aucun pli n'est aberrant, condition pour que la moyenne sur les plis ait un sens (annexe G.1).

**Erreurs.** Le réseau commet en moyenne 103,2 erreurs sur 211 177 lignes, soit 0,049 %. Parmi les 7 215 lignes EVITER, 47,4 sont manquées (0,657 %) et 8,8 lignes sont prédites EVITER à tort. Les deux lectures du rappel EVITER concordent, ce qui sert de contrôle de cohérence interne entre deux programmes distincts (annexe G.1).

**Répartition des erreurs par médicament.** Sur la statistique qui agrège les probabilités des cinq graines avant de prédire (section 6.5), le réseau commet 76 erreurs, réparties sur 20 des 189 médicaments. Quatre médicaments en portent 48, soit près des deux tiers : l'azathioprine (14), la rosuvastatine (13), la sertraline (11) et la fluvastatine (10). Trois d'entre eux dépendent de règles à deux gènes (TPMT et NUDT15 ; ABCG2 et SLCO1B1 ; CYP2C9 et SLCO1B1) : les erreurs se concentrent là où l'étiquette résulte de la combinaison de deux gènes, et les combinaisons rares y sont peu représentées.

**Accord par niveau de source.** Le F1 macro varie peu selon la source de la règle appliquée, sauf pour le niveau DPWG, le moins bien reproduit (0,99457 ± 0,00318) et le plus dispersé ; les causes n'en ont pas été analysées. Le niveau EMA ne peut pas recevoir de F1 macro interprétable : il ne compte que 2 440 lignes et 2 médicaments, et sa seule ligne ADAPTER\_DOSE vient d'une valeur de CYP3A4 que porte un unique profil du corpus, jamais présente à l'entraînement hors pli — exemple concret de valeur génétique jamais vue (sections 6.7, 6.8 et 8.5). Le détail par niveau est au tableau G.1.

### 6.2 Calibration

La température ajustée sur la validation interne de chaque entraînement vaut en moyenne 0,198, avec un minimum de 0,05 et un maximum de 0,269. L'ECE hors pli après calibration est de 0,00029 ± 0,00012.

Une température inférieure à 1 rend les probabilités plus tranchées : le réseau brut est donc sous-confiant sur ses prédictions correctes. Le lissage d'étiquettes de 0,05 (chapitre 4) y contribue vraisemblablement ; cette interprétation n'a pas été vérifiée par une ablation et reste une hypothèse. Deux réserves portent sur ce résultat. D'abord, le minimum observé, 0,05, est exactement la borne inférieure de l'intervalle de recherche fixé au chapitre 4 : pour au moins un entraînement, la valeur retenue est contrainte par l'intervalle et non par les données ; l'intervalle n'a pas été modifié après coup, parce qu'il avait été fixé avant les mesures. Ensuite, une ECE aussi basse s'obtient en partie parce que presque toutes les lignes sont correctes et très confiantes : la mesure est dominée par les lignes faciles et ne démontre pas que les probabilités sont bien calibrées sur les lignes rares, là où se trouvent les erreurs.

Le diagramme de fiabilité (figure 6.1) le montre directement : il porte en abscisse la confiance moyenne (la probabilité maximale calibrée) et en ordonnée l'exactitude observée, la diagonale en pointillés étant la calibration parfaite et un point au-dessous un excès de confiance. Les 1 054 765 lignes du dernier intervalle, soit 99,89 % des 1 055 885 prédictions hors pli, ont une confiance moyenne de 0,9999 et une exactitude de 0,9998 : c'est leur poids qui fixe l'ECE. Les 1 120 lignes restantes se répartissent dans huit intervalles, de confiance moyenne comprise entre 0,39 et 0,91 ; dans sept d'entre eux l'exactitude est inférieure à la confiance, avec un écart qui atteint 0,18 dans l'intervalle \]0,600 ; 0,667\]. Sur ces lignes rares, le réseau est donc trop confiant, ce que l'ECE globale ne laisse pas voir ; leur petit nombre rend cependant chaque point imprécis.

::: {custom-style="FigureImg"}
![](fig/fig_6_calibration.png){width=13cm}
:::

::: {custom-style="LegendeFigure"}
Figure 6.1 : Diagramme de fiabilité du réseau de profil (ECE 0,00029).
:::

### 6.3 Abstention

L'analyse de couverture-risque mesure si la confiance du réseau permet de repérer ses propres erreurs ; elle porte sur les prédictions hors pli calibrées des 211 177 lignes de développement, et aucun seuil n'est choisi au vu de ces données. Le programme, réécrit pour le corpus v15, n'est pas accepté sur sa seule lecture : exécuté sur les prédictions de la version antérieure, il redonne exactement les valeurs publiées pour elle (annexe G.2).

L'aire sous la courbe ROC de la confiance, employée comme indicateur d'erreur, est de 0,8696 ± 0,0115. Les 1 % de lignes les moins confiantes contiennent 77,0 % des erreurs, et les 10 % les moins confiantes 80,3 % : passer de 1 % à 10 % de lignes écartées, soit dix fois plus de prédictions perdues, ne récupère que 3,3 points d'erreurs. Les erreurs restantes ne sont donc pas des hésitations mais des erreurs affirmées. Les quantiles de la confiance hors pli, qui définissent les seuils de l'application (chapitre 4), valent 0,9934 pour écarter 0,5 % des prédictions, 0,9981 pour 1 %, 0,9994 pour 2 % et 0,9998 pour 5 % ; la couverture et le risque à chaque seuil sont au tableau G.2.

**Lecture.** L'abstention retire une part importante des erreurs, mais pas celles qui comptent le plus. Au seuil le plus strict examiné, la moitié des EVITER manqués subsiste (23,6 sur 47,4), alors que le quart seulement des erreurs totales subsiste (28,6 sur 103,2) : les EVITER manqués sont donc, en proportion, deux fois plus résistants à l'abstention que les autres erreurs. Le critère de sécurité du protocole est ainsi celui que la confiance du réseau protège le moins en développement. L'explication tient à la nature de la mesure : l'incertitude du réseau exprime son hésitation entre des étiquettes produites par des règles déterministes, et une règle appliquée à un génotype rare donne une étiquette franche, que le réseau prédit à tort avec une confiance élevée faute d'avoir vu ce génotype. L'incertitude ne peut donc signaler ni qu'une règle est insuffisante, ni qu'un génotype est hors du domaine appris : ce sont deux protections distinctes, assurées dans l'application par l'affichage de la règle et par le statut « hors domaine » (chapitre 5). L'ensemble final donne sur ce point un résultat différent (section 6.7).

Un seuil portant spécifiquement sur la probabilité de la classe EVITER n'est pas proposé : il aurait dû être fixé a priori sur la validation interne, avant la lecture de l'ensemble final, qui n'a donc pas pu servir à l'évaluer. C'est une limite de ce travail.

::: {custom-style="FigureImg"}
![](fig/fig_6_1.png){width=15cm}
:::

::: {custom-style="LegendeFigure"}
Figure 6.2 : Effet de l'abstention sur les erreurs restantes et sur les EVITER manqués acceptés, selon le seuil de confiance (corpus v15, développement).
:::

### 6.4 Réseau de choix au sein d'une classe

Le réseau de choix a été réentraîné sur le corpus v15 selon le protocole du chapitre 4 : 44 classes ATC de niveau 4 contenant au moins deux médicaments étiquetés, 5 plis groupés par profil et 5 graines, l'ensemble final n'étant pas utilisé. Il retrouve exactement l'ensemble de la convention de cible dans 98,92 % ± 0,08 des cas et obtient un indice de Jaccard de 0,99706 ± 0,00034, contre 34,35 % et 0,714 pour une référence qui ignore le profil : c'est là que la lecture du profil se voit, la mesure « choix dans l'ensemble acceptable » ne discriminant pas, puisque cette référence y atteint déjà 99,08 %. Sur le critère de sécurité propre à cette tâche, le réseau n'a jamais proposé un médicament étiqueté EVITER, dans aucun pli et avec aucune graine, alors que la référence sans profil le fait dans 0,073 % des cas où un tel médicament existe dans la classe. Ces résultats mesurent un accord avec une convention du projet, non la désignation du meilleur médicament pour le patient ; ce réseau n'a bénéficié d'aucune recherche d'hyperparamètres et n'a pas été évalué sur l'ensemble final (annexe G.9).

### 6.5 Comparaison avec XGBoost et Random Forest

Cette comparaison est la réponse à RQ2 et le test de l'hypothèse principale du mémoire. Elle suit le protocole figé avant tout résultat : 5 plis groupés par profil, même validation interne, 40 configurations choisies par recherche imbriquée pour chaque modèle, 5 graines, probabilités calibrées pour les trois modèles. Deux amendements écrits avant la lecture des résultats justifient que les recherches aient été refaites entièrement sur la v15 et que la configuration 35 en soit exclue, étant le réglage figé du modèle déployé (annexe G.4). La statistique principale est la moyenne sur les graines ; les intervalles viennent d'un bootstrap sur les profils (2 000 tirages).

::: {custom-style="LegendeTableau"}
Tableau 6.2 : Comparaison du réseau, de XGBoost et de Random Forest (corpus v15, développement, moyenne de 5 graines, intervalles de confiance à 95 %)
:::

| Modèle | F1 macro | EVITER manqués (n) | Taux d'EVITER manqués | Erreurs (n) | ECE | Log-loss |
| --- | --- | --- | --- | --- | --- | --- |
| Réseau (recherche imbriquée) | 0,997943 \[0,997316 ; 0,998484\] | 51,8 \[35,2 ; 70,8\] | 0,72 % | 123,6 \[96,8 ; 154,0\] | 0,00014 | 0,00366 |
| XGBoost | 0,998288 \[0,997676 ; 0,998828\] | 13,8 \[5,8 ; 25,2\] | 0,19 % | 82,0 \[59,6 ; 106,8\] | 0,00030 | 0,00234 |
| Random Forest | 0,992687 \[0,990923 ; 0,994187\] | 108,2 \[74,2 ; 149,4\] | 1,50 % | 655,6 \[534,8 ; 795,4\] | 0,00116 | 0,01374 |
| Réseau, configuration 35 figée (modèle de l'application) | 0,998197 \[0,997651 ; 0,998674\] | 47,4 \[32,4 ; 65,8\] | 0,66 % | 103,2 \[80,4 ; 128,8\] | 0,00016 | 0,00330 |

Les taux d'EVITER manqués rapportent le nombre de lignes EVITER manquées aux 7 215 lignes EVITER du développement.

**Décisions selon la règle figée du protocole.** La règle compare la différence de F1 macro à une marge d'équivalence pratique de 0,001, fixée avant les mesures.

- Réseau moins XGBoost = −0,000345 \[−0,00106 ; +0,00034\] : **non tranché**. L'intervalle contient 0, donc aucune différence n'est démontrée ; il dépasse la marge d'un côté, donc l'équivalence ne l'est pas non plus.
- XGBoost moins le réseau en configuration 35 = +0,000091 \[−0,00052 ; +0,00076\] : **équivalents**.
- Réseau moins Random Forest = +0,00526 \[0,00388 ; 0,00692\] : **réseau supérieur**.
- XGBoost moins Random Forest = +0,00560 \[0,00413 ; 0,00727\] : **XGBoost supérieur**.

**Lecture.** Sur le critère principal du protocole, le réseau et XGBoost ne sont pas séparés par ces données, et pour la configuration effectivement déployée le protocole conclut à l'équivalence ; les deux modèles dominent en revanche nettement Random Forest. Ce résultat ne doit pas être lu comme une supériorité du réseau : « non tranché » signifie que la mesure ne permet pas de départager, et « équivalents » que l'écart est trop petit pour compter en pratique. À la question RQ2, la réponse mesurée est donc que le réseau n'est pas plus performant que les modèles à base d'arbres, ni moins performant au sens du F1 macro.

**Le critère de sécurité, lui, est tranché, et en défaveur du réseau.** Le réseau issu de la recherche imbriquée manque 38,0 lignes EVITER de plus que XGBoost, avec un intervalle à 95 % de \[23,2 ; 54,4\] qui exclut zéro ; pour la configuration 35, l'écart est de 33,6 \[20,8 ; 48,6\]. Sur le critère qui compte pour un outil d'aide à la prescription, XGBoost reste donc le meilleur des deux. Ce critère n'a pas de règle de décision formelle dans le protocole, ce qui en est une faiblesse : la métrique désignée comme mesure de sécurité est la seule à ne pas disposer d'un critère écrit à l'avance.

**La calibration ne départage pas les modèles.** L'ECE est meilleure pour le réseau que pour XGBoost, alors que la log-loss est plus basse pour XGBoost : les deux mesures ne s'accordent pas sur un classement, et aucun intervalle de confiance n'a été calculé sur elles. L'énoncé défendable est que la calibration du réseau et de XGBoost est bonne et que leurs écarts ne sont pas interprétables à ce niveau ; Random Forest est nettement moins bien calibré sur les deux.

**Les erreurs des deux modèles ne sont presque pas les mêmes.** Sur la statistique secondaire, qui agrège les probabilités des cinq graines avant de prédire, le réseau commet 94 erreurs et XGBoost 80, mais seules 9 lignes sont erronées chez les deux : 85 des 94 erreurs du réseau sont correctement traitées par XGBoost, et 71 des 80 erreurs de XGBoost le sont par le réseau. Ce recouvrement très faible justifie un choix de conception de l'application, qui affiche l'avis de XGBoost comme second avis et signale les désaccords (chapitre 5) ; il indique aussi qu'une combinaison des deux pourrait descendre vers l'ordre de dix erreurs. Cette piste n'a pas été testée : une règle de combinaison choisie au vu de ces mêmes prédictions serait un réglage déguisé en résultat.

::: {custom-style="FigureImg"}
![](fig/fig_6_2.png){width=15cm}
:::

::: {custom-style="LegendeFigure"}
Figure 6.3 : Comparaison du réseau, de XGBoost et de Random Forest sur le corpus v15 : F1 macro et taux d'EVITER manqués (développement, moyenne de 5 graines, intervalle de confiance à 95 % par bootstrap sur les profils).
:::

**Évolution par rapport à la version antérieure du corpus.** Sur l'autre version, le protocole concluait à la supériorité de XGBoost ; sur la v15, cette conclusion ne tient plus. Les règles révisées portent sur les médicaments qui concentraient les erreurs du réseau : une étiquette qui dépend de deux gènes tous deux présents à l'entrée est une fonction que le réseau peut apprendre, alors que l'étiquette antérieure dépendait d'un gène seul et était, pour une partie des profils, imprévisible à partir de l'entrée. Cette explication est cohérente avec la localisation des erreurs mais n'est pas démontrée (annexe G.4).

**Limites de cette comparaison.** L'accord est mesuré avec les règles, non avec la clinique. La parenté entre profils n'est pas contrôlée dans le bootstrap. Quatre comparaisons sont rapportées sans correction de multiplicité ; seule la première est la comparaison principale désignée par le protocole. XGBoost et Random Forest sont un modèle unique recevant l'identifiant du médicament comme variable, alors que le réseau est multitâche : l'égalité de protocole porte sur les plis, le réglage et la calibration, non sur la forme du problème posé à chaque modèle. Un contrôle des égalités dans la sélection des configurations, prévu par amendement, montre de plus que la recherche ne distingue plus les configurations de XGBoost à cinq décimales dans quatre plis sur cinq (annexe G.4).

### 6.6 Cohérence avec des études indépendantes (exploratoire)

Pour 8 couples gène-médicament, le sens de l'avis du réseau a été comparé à une étude clinique indépendante de CPIC et de DPWG. L'analyse est exploratoire : le réseau a été interrogé avec des profils construits et non avec des patients, seuls les résumés des articles ont été lus, et les huit couples sont les seuls pour lesquels une étude de référence a pu être identifiée. Le sens est le même dans les 8 cas (tableau G.3), mais l'accord ne porte que sur la direction de l'effet, non sur l'intensité de l'avis : pour la simvastatine et le tamoxifène, l'intensité « à éviter » dépasse ce que montre l'étude, tandis que pour le fluorouracile chez un profil sans activité DPYD l'avis du réseau est plus faible que celui de la règle, qui est celui qu'affiche l'application. L'absence d'un couple de ce tableau signifie qu'aucune étude n'a été lue pour lui, non que la concordance y serait moins bonne (annexe G.3).

### 6.7 Évaluation unique sur l'ensemble final

Les sections précédentes reposent toutes sur les profils de développement, qui ont servi à choisir les configurations, les règles de décision et les seuils ; leurs résultats peuvent donc être optimistes. L'ensemble final de 138 profils (23 455 lignes, dont 816 EVITER) a été mis de côté avant tout essai. Il a été lu une seule fois, après la rédaction d'un protocole qui fixait à l'avance les modèles, les métriques, les règles de décision et les sous-groupes rapportés ; aucun résultat de cette lecture n'a entraîné de modification.

**Modèles évalués.** Les trois modèles ont été réentraînés avec leurs hyperparamètres inchangés, la même graine et la même validation interne, sur 1 207 profils au lieu de 1 241 : les 34 profils retirés sont ceux que le pedigree relie à un profil de l'ensemble final, règle fixée avant toute lecture. Ces modèles servent uniquement à l'évaluation ; l'application conserve ceux entraînés sur les 1 241 profils, pour lesquels aucune mesure sur l'ensemble final n'est donc disponible. Les intervalles viennent d'un bootstrap percentile sur les 138 profils, avec 10 000 tirages communs aux trois modèles, de sorte que les différences sont appariées (annexe G.5).

::: {custom-style="LegendeTableau"}
Tableau 6.3 : Évaluation unique sur l'ensemble final (138 profils, 23 455 lignes, 816 EVITER ; intervalles de confiance à 95 %, bootstrap sur les profils)
:::

| Modèle | F1 macro | Exactitude | EVITER manqués (n) | Taux d'EVITER manqués | Précision EVITER | Erreurs (n) | ECE | Log-loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Réseau, configuration 35 | 0,9940 \[0,9839 ; 0,9992\] | 0,9985 | 10 \[3 ; 20\] | 1,23 % | 0,989 | 35 | 0,0013 | 0,0096 |
| XGBoost | 0,9989 \[0,9976 ; 0,9998\] | 0,9998 | 3 \[0 ; 7\] | 0,37 % | 1,000 | 5 | 0,0172 | 0,0183 |
| Random Forest | 0,9300 \[0,9154 ; 0,9429\] | 0,9752 | 37 \[20 ; 57\] | 4,53 % | 0,797 | 581 | 0,1620 | 0,2349 |

**Décisions selon la règle figée.**

- Réseau moins XGBoost = −0,0049 \[−0,0152 ; +0,0007\] : **non tranché**. L'écart d'EVITER manqués, +7 \[−1 ; +17\], n'est pas démontré non plus.
- Réseau moins Random Forest = +0,0640 \[0,0519 ; 0,0772\] : **réseau supérieur**.
- XGBoost moins Random Forest = +0,0689 \[0,0563 ; 0,0832\] : **XGBoost supérieur**.

Une seule ligne est erronée à la fois chez le réseau et chez XGBoost.

**Lecture.** L'ensemble final confirme le classement établi en développement : XGBoost obtient les meilleurs résultats sur toutes les mesures sauf l'ECE, le réseau vient ensuite sans que l'écart soit tranché, et les deux dominent Random Forest. L'hypothèse principale du mémoire n'est donc pas confirmée par cette évaluation indépendante. L'intervalle de la différence entre le réseau et XGBoost est plus large qu'en développement, ce qui est attendu avec 138 profils au lieu de 1 241 : l'ensemble final ne pouvait pas trancher un écart de l'ordre du millième. Le F1 macro du réseau est plus bas que sur le développement, alors que celui de XGBoost reste stable ; cette baisse est portée par un seul profil.

**Abstention.** Aux seuils figés de la section 6.3, l'abstention écarte sur l'ensemble final une part de lignes un peu supérieure à celle visée (1,12 % au lieu de 1 % au seuil de l'application) : le réseau y est un peu moins confiant qu'en développement, ce qui est cohérent avec des profils non vus. Au seuil de l'application, 8 des 10 EVITER manqués sont écartés et signalés « à vérifier » (tableau G.4). Ce résultat diffère de celui du développement, où la moitié des EVITER manqués résistait à l'abstention. Il porte sur 10 lignes et ne suffit pas à conclure que l'abstention protège bien les EVITER manqués en général ; il montre seulement que, sur cet ensemble, la plupart de ces erreurs étaient des hésitations.

**Un profil atypique porte la baisse.** L'analyse qui suit n'était pas prévue par le protocole ; elle ne modifie aucun chiffre ci-dessus et n'a entraîné aucun nouvel essai. Un seul profil, HG03684, porte 26 des 35 erreurs du réseau sur ses 119 lignes, dont 4 des 10 EVITER manqués ; il combine plusieurs valeurs rares, et XGBoost n'y commet aucune erreur. En dehors de lui, le réseau commet 9 erreurs sur 23 336 lignes. Ces erreurs portent sur des médicaments dont les gènes ne sont pas ceux qui rendent le profil rare : l'amitriptyline dépend de CYP2C19 et CYP2D6, non de G6PD. Le réseau étant multitâche, une valeur inhabituelle d'un gène sans rapport avec un médicament modifie la représentation commune et peut changer l'avis donné pour ce médicament : c'est une contrepartie plausible de l'architecture choisie au chapitre 4, et pourquoi XGBoost y est moins sensible n'a pas été mesuré.

Cette analyse a une conséquence pour l'application : le contrôle de domaine (chapitre 5), qui vérifie pour chaque médicament que la combinaison de valeurs de ses gènes a été vue à l'entraînement, n'aurait rien signalé pour les 26 médicaments en erreur chez HG03684. L'abstention en aurait écarté 16 ; les 10 autres auraient été affichés avec une confiance d'au moins 0,998. Deux protections restent : la règle de la directive affichée à côté de l'avis du réseau, et le second avis de XGBoost, qui aurait fait apparaître un désaccord. Le contrôle de domaine par médicament ne suffit donc pas à repérer un profil atypique dans son ensemble ; un contrôle portant sur le profil complet n'a pas été mis en œuvre dans ce travail.

**Réserves.** L'ensemble final est réservé mais non vierge : 125 des 138 profils ont participé à la validation croisée d'essais antérieurs du projet, sans jamais être lus pour une évaluation (section 3.8, point 9). Le pedigree ne décrit que la parenté déclarée, non la structure de population. Deux paires de profils apparentés se trouvent à l'intérieur de l'ensemble final et sont traitées comme indépendantes par le bootstrap. Enfin, la référence reste le moteur de règles : l'évaluation mesure la reproduction des directives sur des profils nouveaux, non la justesse clinique des avis. Les sous-groupes fixés à l'avance ne font apparaître aucun avantage des profils apparentés (annexe G.5).

### 6.8 Résultats exploratoires négatifs

Deux pistes ont été abandonnées après mesure. Elles sont rapportées parce qu'elles répondent à RQ4 et RQ5 par la négative et qu'elles délimitent ce que l'application ne fait pas.

**Médicaments jamais vus.** Un réseau recevant le profil génétique et des descripteurs du médicament, sans aucune information de directive, a été évalué sur des médicaments laissés de côté à l'entraînement. L'AUROC pour la distinction « non STANDARD » est de 0,774 \[0,726 ; 0,823\], contre 0,817 \[0,779 ; 0,855\] pour une référence qui prédit par la fréquence des classes selon le gène et le phénotype : la différence, −0,043 \[−0,079 ; −0,009\], est défavorable au réseau. L'ajout de l'empreinte moléculaire du médicament dégrade encore les résultats. La conclusion est que la description du médicament ne permet pas de prédire l'action pour un médicament jamais vu mieux que des références simples ; la branche « description du médicament » n'est donc pas intégrée à l'application, et le médicament y reste une sortie du réseau et non une entrée. Le détail des variantes et des limites est en annexe G.6.

**Associations publiées.** Sur 2 141 lignes d'associations ClinPGx (256 médicaments, 80 gènes), la direction publiée de l'effet est prédite avec une exactitude de 0,638 ± 0,007, contre 0,581 pour la classe majoritaire et 0,656 pour une loi a priori par gène et catégorie. Le signal est faible (AUROC 0,651) et, sur des couples jamais vus, une loi a priori simple fait aussi bien ou mieux. Les étiquettes sont de plus bruitées : 957 des 2 141 lignes appartiennent à des combinaisons où des directions contradictoires sont publiées. Cette piste n'a pas été poursuivie.

### 6.9 Synthèse et limites des résultats

**Mesuré.** Sur 211 177 lignes hors pli, le réseau de profil déployé reproduit les étiquettes issues des règles avec un F1 macro de 0,99820 ± 0,00075 et manque 0,66 % des situations à éviter, ses erreurs se concentrant sur quatre médicaments à règle à deux gènes. Ses probabilités sont bien calibrées globalement (ECE 0,00029) ; la confiance repère les erreurs de façon partielle (AUROC 0,870) et, en développement, protège moins bien les EVITER manqués que les autres erreurs. Sous un protocole identique, le réseau et XGBoost ne sont pas départagés sur le F1 macro et sont déclarés équivalents pour la configuration déployée, les deux dominant nettement Random Forest ; XGBoost conserve un avantage démontré sur le critère de sécurité, avec 38 EVITER manqués de moins, et les erreurs des deux modèles se recouvrent très peu. Le réseau de choix retrouve exactement l'ensemble de la convention de cible dans 98,92 % des cas, contre 34,35 % pour une référence qui ignore le profil, et ne propose jamais de médicament à éviter. Le sens des avis concorde avec les 8 études lues.

Sur l'ensemble final, lu une seule fois, le classement est confirmé : XGBoost obtient un F1 macro de 0,9989 et manque 3 lignes EVITER sur 816, le réseau 0,9940 et 10, Random Forest 0,9300 et 37. L'écart entre le réseau et XGBoost reste non tranché. Au seuil de l'application, l'abstention écarte 8 des 10 EVITER manqués par le réseau. La baisse du réseau par rapport au développement est portée par un seul profil atypique, sur lequel XGBoost ne se trompe pas.

**Non mesuré ou non démontré.**

- La justesse clinique des avis. Toutes les mesures de ce chapitre portent sur l'accord avec des règles ; une seule règle est confrontée à des patients réels (chapitre 7).
- La supériorité du réseau sur les modèles à base d'arbres. Elle n'est établie ni en développement ni sur l'ensemble final. L'hypothèse principale du mémoire n'est donc pas confirmée.
- La robustesse du réseau à un profil atypique dans son ensemble. Un seul profil de l'ensemble final suffit à faire chuter son F1 macro, et le contrôle de domaine par médicament ne le repère pas.
- Les performances sur l'ensemble final des modèles de l'application eux-mêmes, entraînés sur 1 241 profils ; l'évaluation porte sur des modèles de même configuration entraînés sur 1 207 profils.
- Les performances de la chaîne complète depuis un fichier VCF, traitées au chapitre 8.
- La généralisation à un médicament jamais vu (résultat négatif, section 6.8) et à une combinaison de gènes jamais observée, dont le cas du lonafarnib donne un exemple (section 6.1).

Les essais abandonnés, négatifs ou corrigés sont récapitulés dans l'annexe A.
