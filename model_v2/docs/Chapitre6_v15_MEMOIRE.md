## Chapitre 6 : Résultats

Ce chapitre rapporte les résultats mesurés sur le corpus v15 selon le protocole du chapitre 4. Il suit l'ordre des questions de recherche : accord du réseau avec les règles (RQ1), qualité de ses probabilités et utilité de l'abstention (RQ3), choix au sein d'une classe thérapeutique, comparaison aux modèles à base d'arbres (RQ2), concordance avec des études indépendantes (RQ6), puis évaluation unique sur l'ensemble final réservé, qui confirme ou infirme les constats précédents sur des profils jamais lus. Les résultats négatifs (RQ4 et RQ5) viennent ensuite. La validation sur patients réels (RQ7) fait l'objet des chapitres 7 et 8 : elle ne porte pas sur les mêmes données et ne mesure pas la même chose.

Une mise en garde s'applique à toutes les mesures qui suivent : les étiquettes proviennent du moteur de règles CPIC, DPWG, RNPGx, FDA, EMA et Health Canada (chapitre 3). Un score élevé signifie que le modèle reproduit ces règles, non que l'avis est juste cliniquement. Les écarts-types décrivent la variabilité d'entraînement (5 plis × 5 graines) ; ils ne mesurent pas l'incertitude due au choix des profils, puisque les graines partagent les mêmes lignes. C'est pourquoi les comparaisons entre modèles (sections 6.5 et 6.7) utilisent des intervalles de confiance obtenus par bootstrap sur les identifiants de profil, et non ces écarts-types.

Les sections 6.1 à 6.6 portent sur les 1 241 profils de développement, soit 211 177 lignes, dont 181 262 STANDARD, 18 188 ADAPTER\_DOSE, 7 215 EVITER et 4 512 SURVEILLER. Ces quatre effectifs servent de dénominateurs à ces sections. La section 6.7 porte sur les 138 profils de l'ensemble final (23 455 lignes), lus une seule fois après que toutes les décisions des sections précédentes ont été prises.

### 6.1 Réseau de profil : accord avec les règles

Le tableau 6.1 donne la moyenne et l'écart-type des 25 entraînements (5 plis × 5 graines) de la configuration 35, c'est-à-dire du réseau déployé dans l'application, évalué sur ses prédictions hors pli après calibration par température.

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

Le F1 macro sans la classe SURVEILLER est rapporté parce que SURVEILLER est la classe dont la définition varie le plus d'une source à l'autre (chapitre 3) : il vérifie que le score global n'est pas porté par cette classe. Il est légèrement plus bas que le F1 à quatre classes, ce qui montre que SURVEILLER est au contraire l'une des classes les mieux reproduites (rappel 0,99978). La classe la moins bien reproduite est EVITER, celle qui compte le plus pour la sécurité.

Le F1 macro moyen par pli est de 0,99772, 0,99852, 0,99802, 0,99918 et 0,99754. L'écart entre le meilleur et le moins bon pli (0,00164) est du même ordre que l'écart-type entre entraînements : aucun pli n'est aberrant, ce qui est la condition pour que la moyenne sur les plis ait un sens. L'arrêt anticipé a eu lieu en moyenne à 81,4 époques (écart-type 14,7), soit bien avant le plafond de 300 époques fixé au chapitre 4 : ce plafond n'a donc jamais limité l'entraînement, et la patience de 25 époques est la contrainte qui arrête effectivement l'apprentissage.

**Erreurs.** Le réseau commet en moyenne 103,2 erreurs sur 211 177 lignes, soit 0,049 %. Parmi les 7 215 lignes EVITER, 47,4 sont manquées (0,657 %) et 8,8 lignes sont prédites EVITER à tort. Les deux lectures du rappel EVITER concordent : 1 − 0,99342 = 0,00658, à comparer à 47,4 / 7 215 = 0,00657. Cette concordance n'est pas automatique, les deux valeurs étant produites par deux programmes distincts (l'évaluation imbriquée et l'analyse de couverture-risque) à partir des mêmes fichiers de prédictions hors pli ; elle sert de contrôle de cohérence interne.

**Répartition des erreurs par médicament.** Sur la statistique qui agrège les probabilités des cinq graines avant de prédire (section 6.5), le réseau commet 76 erreurs, réparties sur 20 des 189 médicaments. Quatre médicaments en portent 48, soit près des deux tiers : l'azathioprine (14), la rosuvastatine (13), la sertraline (11) et la fluvastatine (10) ; suivent le méloxicam et le siponimod (5 chacun), puis le tacrolimus (3). Les deux premiers dépendent de règles à deux gènes (TPMT et NUDT15 ; ABCG2 et SLCO1B1), de même que la fluvastatine (CYP2C9 et SLCO1B1) : les erreurs se concentrent là où l'étiquette résulte de la combinaison de deux gènes, et les combinaisons rares y sont peu représentées.

**Accord par niveau de source.** Le tableau 6.2 donne le F1 macro selon la source dont provient la règle appliquée. Les sources sont celles du chapitre 3 ; le nombre de lignes de chaque niveau est fixé par le corpus et non choisi.

::: {custom-style="LegendeTableau"}
Tableau 6.2 : F1 macro du réseau de profil par niveau de source, moyenne et écart-type sur les 25 entraînements (corpus v15)
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

**Un niveau de source ne peut pas recevoir de F1 macro interprétable.** Le niveau « EMA-étiquette » ne compte que 2 440 lignes et 2 médicaments (erlotinib : 987 STANDARD et 253 SURVEILLER ; lonafarnib : 1 199 STANDARD et 1 ADAPTER\_DOSE). Cette unique ligne ADAPTER\_DOSE vient de la règle lonafarnib / CYP3A4 de valeur 0, et un seul des 1 379 profils du corpus porte cette valeur (1 286 profils à 1,0, 50 à 0,5, 42 non typés). Hors pli, aucun profil d'entraînement ne porte donc cette valeur, et aucun modèle ne peut l'apprendre à partir de ce corpus. Le F1 macro étant la moyenne sur les classes présentes, manquer cette seule ligne fait tomber le F1 de la classe à 0 et le F1 macro du niveau à environ 2/3, quel que soit le modèle. Ce nombre mesure la taille de l'échantillon, non la performance : pour ce niveau, seuls les effectifs par classe sont rapportés. Ce cas est aussi un exemple concret de valeur génétique jamais vue à l'entraînement, situation traitée en sections 6.7, 6.8 et 8.5.

### 6.2 Calibration

La température ajustée sur la validation interne de chaque entraînement vaut en moyenne 0,198, avec un minimum de 0,05 et un maximum de 0,269. L'ECE hors pli après calibration est de 0,00029 ± 0,00012.

Une température inférieure à 1 rend les probabilités plus tranchées : le réseau brut est donc sous-confiant sur ses prédictions correctes. Le lissage d'étiquettes de 0,05 (chapitre 4) y contribue vraisemblablement, puisqu'il interdit à la cible d'atteindre 1 ; cette interprétation n'a pas été vérifiée par une ablation du lissage et reste une hypothèse.

Deux réserves portent sur ce résultat. D'abord, le minimum observé, 0,05, est exactement la borne inférieure de l'intervalle de recherche fixé au chapitre 4 : pour au moins un entraînement, l'optimum se trouve à la borne ou au-delà, et la valeur retenue est alors contrainte par l'intervalle et non par les données. Élargir l'intervalle aurait rendu ces entraînements comparables aux autres ; l'intervalle n'a pas été modifié, parce qu'il avait été fixé avant les mesures et que le modifier après coup aurait transformé un réglage a priori en réglage choisi au vu des résultats. Ensuite, une ECE aussi basse s'obtient en partie parce que presque toutes les lignes sont correctes et très confiantes : la mesure est dominée par les lignes faciles et ne démontre pas que les probabilités sont bien calibrées sur les lignes rares, là où se trouvent les erreurs. C'est la section 6.3 qui examine ce point. Le diagramme de fiabilité (figure 6.1) le montre directement. Il regroupe les prédictions hors pli des 25 entraînements, soit 1 055 885 lignes (211 177 lignes pour chacune des 5 graines), dans les 15 intervalles de confiance employés pour l'ECE. Les 1 054 765 lignes du dernier intervalle, soit 99,89 %, ont une confiance moyenne de 0,9999 et une exactitude de 0,9998 : c'est leur poids qui fixe l'ECE. Les 1 120 lignes restantes se répartissent dans huit intervalles, de confiance moyenne comprise entre 0,39 et 0,91. Dans sept d'entre eux, l'exactitude est inférieure à la confiance, avec un écart qui atteint 0,18 dans l'intervalle \]0,600 ; 0,667\] (88 lignes, confiance moyenne 0,64, exactitude 0,45). Sur ces lignes rares, le réseau est donc trop confiant, ce que l'ECE globale ne laisse pas voir ; leur petit nombre rend cependant chaque point imprécis.

::: {custom-style="FigureImg"}
![](fig/fig_6_calibration.png){width=13cm}
:::

::: {custom-style="LegendeFigure"}
Figure 6.1 : Diagramme de fiabilité du réseau de profil (prédictions hors pli calibrées, 25 entraînements, 15 intervalles ; n = nombre de lignes par intervalle).
:::

### 6.3 Abstention

L'analyse de couverture-risque mesure si la confiance du réseau permet de repérer ses propres erreurs. Elle porte sur les prédictions hors pli calibrées des 211 177 lignes de développement, moyennées sur les 5 graines. Aucun seuil n'est choisi au vu de ces données : les seuils du tableau 6.3 sont des valeurs rondes fixées d'avance, et les quantiles rapportés plus bas sont des descriptions de la distribution, non des optimisations.

Le programme qui produit cette analyse a été réécrit pour le corpus v15, celui de la version antérieure n'étant plus disponible. Il n'est pas accepté sur sa seule lecture : exécuté sur les prédictions de la version antérieure du corpus, il redonne exactement les valeurs publiées pour cette version (113,0 erreurs, 60,2 EVITER manqués sur 7 227, 8,4 faux EVITER, AUROC 0,8704 ± 0,0253 et les quatre seuils de quantile). Cette reproduction à l'identique est la justification de son emploi sur la v15.

L'aire sous la courbe ROC de la confiance, employée comme indicateur d'erreur, est de 0,8696 ± 0,0115. Les 1 % de lignes les moins confiantes (2 112 lignes) contiennent 77,0 % des erreurs, et les 10 % les moins confiantes 80,3 %. La confiance est donc un indicateur utile mais partiel : passer de 1 % à 10 % de lignes écartées, soit dix fois plus de prédictions perdues, ne récupère que 3,3 points d'erreurs supplémentaires. Les erreurs restantes ne sont donc pas des hésitations mais des erreurs affirmées.

::: {custom-style="LegendeTableau"}
Tableau 6.3 : Couverture, exactitude sélective et erreurs restantes selon le seuil de confiance (corpus v15, développement)
:::

| Seuil de confiance | Couverture | Exactitude sélective | Erreurs restantes (sur 103,2) | EVITER manqués acceptés (sur 47,4) | Lignes écartées |
| --- | --- | --- | --- | --- | --- |
| 0,70 | 0,99972 | 0,99964 | 75,4 | 38,4 | 59,2 |
| 0,90 | 0,99919 | 0,99976 | 49,6 | 32,0 | 170,4 |
| 0,95 | 0,99872 | 0,99980 | 42,2 | 29,2 | 269,8 |
| 0,99 | 0,99683 | 0,99985 | 32,0 | 25,2 | 669,4 |
| 0,9965 | 0,99441 | 0,99986 | 28,6 | 23,6 | 1 180,6 |

Les quantiles de la confiance hors pli, qui définissent les seuils d'abstention de l'application selon la méthode du chapitre 4, valent sur le corpus v15 : 0,9934 pour écarter 0,5 % des prédictions, 0,9981 pour 1 %, 0,9994 pour 2 % et 0,9998 pour 5 %. Ils sont tous plus élevés que ceux de la version antérieure du corpus (0,9895, 0,9965, 0,9988 et 0,9995) : le réseau est devenu plus confiant, de sorte qu'il faut un seuil plus haut pour écarter la même part de prédictions. La dernière ligne du tableau 6.3 le chiffre : le seuil 0,9965, qui écartait 1 % des prédictions sur la version antérieure, n'en écarte plus que 0,56 % sur la v15.

**Lecture.** L'abstention retire une part importante des erreurs, mais pas celles qui comptent le plus. Au seuil le plus strict du tableau, la moitié des EVITER manqués subsiste (23,6 sur 47,4), alors que le quart seulement des erreurs totales subsiste (28,6 sur 103,2) : les EVITER manqués sont donc, en proportion, deux fois plus résistants à l'abstention que les autres erreurs. Ce résultat est défavorable : le critère de sécurité du protocole est précisément celui que la confiance du réseau protège le moins en développement. L'explication tient à la nature de la mesure. L'incertitude du réseau exprime son hésitation entre des étiquettes produites par des règles déterministes ; une règle appliquée à un génotype rare donne une étiquette franche, que le réseau prédit à tort avec une confiance élevée faute d'avoir vu ce génotype. L'incertitude ne peut donc pas signaler qu'une règle est insuffisante, ni qu'un génotype est hors du domaine appris : ce sont deux protections distinctes, assurées dans l'application par l'affichage de la règle et par le statut « hors domaine » (chapitre 5). L'ensemble final donne sur ce point un résultat différent, rapporté en section 6.7.

Un seuil portant spécifiquement sur la probabilité de la classe EVITER n'est pas proposé. Un tel seuil devrait être fixé a priori sur la validation interne, puis évalué sur des données non lues ; le fixer ici, sur les mêmes prédictions hors pli qui servent à le mesurer, produirait une valeur optimiste. Il n'a pas été fixé avant la lecture de l'ensemble final, qui n'a donc pas pu servir à l'évaluer : c'est une limite de ce travail.

::: {custom-style="FigureImg"}
![](fig/fig_6_1.png){width=15cm}
:::

::: {custom-style="LegendeFigure"}
Figure 6.2 : Effet de l'abstention sur les erreurs restantes et sur les EVITER manqués acceptés, selon le seuil de confiance (corpus v15, développement).
:::

### 6.4 Réseau de choix au sein d'une classe

Le réseau de choix a été réentraîné sur le corpus v15 selon le protocole du chapitre 4 : 44 classes ATC de niveau 4 contenant au moins deux médicaments étiquetés, 5 plis groupés par identifiant de profil et 5 graines, soit 25 entraînements. L'ensemble final n'est pas utilisé, ce que le programme vérifie et rapporte. Deux références encadrent les résultats : une référence qui ignore le profil du patient et propose pour tous les mêmes médicaments, à savoir ceux qui appartiennent le plus souvent à l'ensemble acceptable à l'entraînement, et un choix au hasard. Ces références sont déterministes, d'où leur écart-type nul.

::: {custom-style="LegendeTableau"}
Tableau 6.4 : Réseau de choix au sein d'une classe ATC4, validation croisée (44 classes, 5 plis × 5 graines, corpus v15)
:::

| Mesure | Réseau de choix | Référence sans profil | Hasard |
| --- | --- | --- | --- |
| Choix dans l'ensemble acceptable (cas informatifs) | 99,997 % ± 0,005 | 99,08 % | 55,14 % |
| Ensemble exact retrouvé | 98,92 % ± 0,08 | 34,35 % | — |
| Indice de Jaccard | 0,99706 ± 0,00034 | 0,71441 | — |
| Médicament EVITER choisi quand il en existe un dans la classe | 0,000 % ± 0,000 | 0,073 % | — |

**Ce que ces chiffres disent, et ce qu'ils ne disent pas.** La mesure « choix dans l'ensemble acceptable » ne discrimine pas : la référence qui ignore entièrement le profil atteint déjà 99,08 %, parce que dans la plupart des classes le même médicament convient à presque tous les patients. Elle est rapportée pour cette raison même, et non comme un résultat. Les deux mesures informatives sont l'ensemble exact retrouvé et l'indice de Jaccard, où la référence sans profil descend respectivement à 34,35 % et 0,714 : c'est là que la lecture du profil se voit.

Une mesure répond plus directement à la question de l'apport du profil. Parmi les cas informatifs, la référence sans profil propose un médicament hors de l'ensemble acceptable dans 72 cas répartis sur les cinq plis ; sur ces 72 cas, le réseau choisit correctement dans la totalité d'entre eux, et pour les cinq graines. Là où ignorer le profil conduit à une proposition inadéquate, la lecture du profil la corrige systématiquement. Le nombre de cas concernés est petit, ce qui limite la portée du constat, mais il est obtenu sans aucune exception.

Sur le critère de sécurité propre à cette tâche, le réseau n'a jamais proposé un médicament étiqueté EVITER, dans aucun pli et avec aucune graine, alors que la référence sans profil le fait dans 0,073 % des cas où un tel médicament existe dans la classe. C'est le seul chiffre de cette section qui porte une conséquence clinique directe.

**Limite de principe.** Tous ces résultats mesurent un accord avec la cible définie au chapitre 4, qui est une convention du projet : parmi les médicaments étiquetés de la classe, retenir ceux de la meilleure action disponible, et leur attribuer une probabilité uniforme. Aucune ligne directrice ne départage les médicaments de cet ensemble. Un score élevé signifie donc que le réseau reproduit fidèlement cette convention, et non qu'il désigne le meilleur médicament pour le patient. S'y ajoute le fait que ce réseau n'a bénéficié d'aucune recherche d'hyperparamètres, contrairement au réseau de profil (section 4.10), et qu'il n'a pas été évalué sur l'ensemble final : le protocole de la section 6.7 porte sur la recommandation par médicament, tâche principale du travail.

### 6.5 Comparaison avec XGBoost et Random Forest

Cette comparaison est la réponse à RQ2 et le test de l'hypothèse principale du mémoire. Elle suit le protocole figé avant tout résultat, complété par deux amendements écrits avant la lecture des résultats : validation croisée à 5 plis groupés par identifiant de profil, même validation interne, 40 configurations choisies par recherche imbriquée pour chaque modèle, 5 graines, probabilités calibrées par température pour les trois modèles.

Le deuxième amendement justifie deux points propres au corpus v15. D'abord, les recherches d'hyperparamètres ont été refaites entièrement sur la v15 et non reprises de la version antérieure : le corpus v15 partage les plis du précédent et n'en diffère que de 0,85 % des lignes, de sorte que reprendre des réglages sélectionnés sur l'autre version équivaudrait à les avoir choisis en ayant vu, sous une forme presque identique, les profils qui servent de test. Le coût de ce choix est d'environ neuf heures de calcul supplémentaires. Ensuite, la configuration 35 est la seule exception : elle n'est pas re-sélectionnée, parce qu'elle est par définition le réglage figé du modèle déployé, choisi sur une version antérieure du corpus, et que la re-sélectionner la priverait de ce qu'elle mesure. Elle figure donc comme bras de référence supplémentaire, hors de la règle de décision.

La statistique principale est la moyenne sur les graines : la mesure est calculée sur l'ensemble des prédictions hors pli de chaque graine, puis moyennée. Les intervalles sont obtenus par bootstrap sur les identifiants de profil (2 000 tirages), les profils apparentés étant traités comme indépendants.

::: {custom-style="LegendeTableau"}
Tableau 6.5 : Comparaison du réseau, de XGBoost et de Random Forest (corpus v15, développement, moyenne de 5 graines, intervalles de confiance à 95 %)
:::

| Modèle | F1 macro | EVITER manqués (n) | Taux d'EVITER manqués | Erreurs (n) | ECE | Log-loss |
| --- | --- | --- | --- | --- | --- | --- |
| Réseau (recherche imbriquée) | 0,997943 \[0,997316 ; 0,998484\] | 51,8 \[35,2 ; 70,8\] | 0,72 % | 123,6 \[96,8 ; 154,0\] | 0,00014 | 0,00366 |
| XGBoost | 0,998288 \[0,997676 ; 0,998828\] | 13,8 \[5,8 ; 25,2\] | 0,19 % | 82,0 \[59,6 ; 106,8\] | 0,00030 | 0,00234 |
| Random Forest | 0,992687 \[0,990923 ; 0,994187\] | 108,2 \[74,2 ; 149,4\] | 1,50 % | 655,6 \[534,8 ; 795,4\] | 0,00116 | 0,01374 |
| Réseau, configuration 35 figée (modèle de l'application) | 0,998197 \[0,997651 ; 0,998674\] | 47,4 \[32,4 ; 65,8\] | 0,66 % | 103,2 \[80,4 ; 128,8\] | 0,00016 | 0,00330 |

Les taux d'EVITER manqués sont le nombre de lignes EVITER manquées rapporté aux 7 215 lignes EVITER du développement. La log-loss donnée au tableau 6.1 pour la configuration 35 (0,00260) n'est pas comparable à celle de ce tableau (0,00330) : la première est la moyenne des 25 entraînements, la seconde est calculée sur l'ensemble des prédictions de chaque graine avant moyenne.

**Décisions selon la règle figée du protocole.** La règle compare la différence de F1 macro à une marge d'équivalence pratique de 0,001, fixée avant les mesures : un modèle est déclaré supérieur si la borne basse de l'intervalle dépasse 0, les deux modèles sont déclarés équivalents si l'intervalle entier tient dans ±0,001, et la différence est déclarée non tranchée sinon.

- Réseau moins XGBoost = −0,000345 \[−0,00106 ; +0,00034\] : **non tranché**. L'intervalle contient 0, donc aucune différence n'est démontrée statistiquement ; il dépasse la marge d'un côté, donc l'équivalence n'est pas démontrée non plus.
- XGBoost moins le réseau en configuration 35 = +0,000091 \[−0,00052 ; +0,00076\] : **équivalents**. L'intervalle entier tient dans ±0,001.
- Réseau moins Random Forest = +0,00526 \[0,00388 ; 0,00692\] : **réseau supérieur**.
- XGBoost moins Random Forest = +0,00560 \[0,00413 ; 0,00727\] : **XGBoost supérieur**.

**Lecture.** Sur le critère principal du protocole, le réseau et XGBoost ne sont pas séparés par ces données : la différence de F1 macro est inférieure au millième et son intervalle contient zéro. Pour la configuration effectivement déployée dans l'application, le protocole conclut à l'équivalence avec XGBoost. Les deux modèles dominent en revanche nettement Random Forest, dont le F1 macro est inférieur de plus de cinq millièmes et qui commet huit fois plus d'erreurs que XGBoost.

Ce résultat ne doit pas être lu comme une supériorité du réseau. « Non tranché » signifie que la mesure ne permet pas de départager, et « équivalents » que l'écart est trop petit pour compter en pratique ; ni l'un ni l'autre n'établit que le réseau fait mieux. La question de recherche RQ2 demandait si le réseau était plus performant que les modèles à base d'arbres : la réponse mesurée est qu'il ne l'est pas, et qu'il n'est pas non plus moins performant au sens du F1 macro.

**Le critère de sécurité, lui, est tranché, et en défaveur du réseau.** Le réseau issu de la recherche imbriquée manque 38,0 lignes EVITER de plus que XGBoost, avec un intervalle à 95 % de \[23,2 ; 54,4\] qui exclut zéro ; pour la configuration 35, l'écart est de 33,6 \[20,8 ; 48,6\]. Sur le critère qui compte pour un outil d'aide à la prescription, XGBoost reste donc le meilleur des deux, et cet écart ne s'explique pas par le hasard d'entraînement. Ce critère n'a pas de règle de décision formelle dans le protocole, ce qui est une faiblesse du protocole : la métrique désignée comme mesure de sécurité est la seule à ne pas disposer d'un critère écrit à l'avance.

**La calibration ne départage pas les modèles.** Sur la version antérieure du corpus, l'ECE de XGBoost après calibration était meilleure que celle du réseau ; sur la v15, l'ordre est inversé (0,00014 et 0,00016 pour les deux bras du réseau, contre 0,00030 pour XGBoost), alors que la log-loss reste plus basse pour XGBoost (0,00234 contre 0,00366 et 0,00330). Les deux mesures ne s'accordent donc pas sur un classement. Il s'agit de valeurs très faibles sur une tâche où plus de 99,9 % des lignes sont correctement prédites, et aucun intervalle de confiance n'a été calculé sur ces deux mesures. L'énoncé défendable est que la calibration du réseau et de XGBoost est bonne et que leurs écarts ne sont pas interprétables à ce niveau ; Random Forest est nettement moins bien calibré sur les deux mesures.

**Les erreurs des deux modèles ne sont presque pas les mêmes.** Sur la statistique secondaire, qui agrège les probabilités des cinq graines avant de prédire, le réseau commet 94 erreurs, XGBoost 80 et Random Forest 650 ; mais seules 9 lignes sont erronées chez le réseau et chez XGBoost simultanément, dont 8 le sont aussi chez Random Forest. Autrement dit, 85 des 94 erreurs du réseau sont correctement traitées par XGBoost, et 71 des 80 erreurs de XGBoost le sont par le réseau. Ce recouvrement très faible est une mesure, et non une interprétation ; il justifie un choix de conception de l'application, qui affiche l'avis de XGBoost comme second avis et signale les désaccords (chapitre 5). Il indique aussi une piste : une combinaison des deux modèles pourrait descendre vers l'ordre de dix erreurs, chiffre qu'aucun des deux n'atteint seul. Cette piste n'a pas été testée : une règle de combinaison choisie au vu de ces mêmes prédictions hors pli serait un réglage déguisé en résultat, et sa valeur devrait être établie sur des données non lues.

**Égalités dans la sélection des configurations.** Le premier amendement prévoyait de vérifier, pour chaque pli et chaque modèle, si la configuration retenue par la recherche imbriquée était à égalité, à cinq décimales près, avec une autre. Le contrôle a été fait sur les 200 essais de chaque recherche (40 configurations × 5 plis). Pour le réseau et pour Random Forest, la configuration retenue est unique dans chacun des cinq plis. Pour XGBoost, elle est à égalité avec au moins une autre dans quatre plis sur cinq, avec 2 à 7 configurations ex æquo, et un F1 de validation de 1,00000 dans deux plis : la recherche ne distingue plus les configurations de XGBoost à ce niveau de précision, et c'est la première configuration de la liste qui a été retenue (configurations 1, 0, 0 et 1 ; configuration 5, unique, dans le dernier pli). Le choix entre configurations ex æquo est donc arbitraire. Son effet sur les performances de XGBoost n'a pas été mesuré ; les configurations ex æquo étant indiscernables sur la validation, il n'y a pas de raison de s'attendre à un écart important, mais cela n'est pas démontré.

**Évolution par rapport à la version antérieure du corpus.** Sur l'autre version, la conclusion du protocole était que XGBoost était supérieur au réseau, statistiquement et en pratique (différence de −0,00265, intervalle entièrement sous −0,001). Sur la v15, cette conclusion ne tient plus. Deux mouvements l'expliquent arithmétiquement : les erreurs du réseau issu de la recherche imbriquée passent de 187,2 à 123,6, et celles de XGBoost de 41,8 à 82,0. Les règles révisées en v15 portent sur les médicaments qui concentraient les erreurs du réseau, en particulier la grille à deux gènes TPMT et NUDT15 des trois thiopurines et la règle à deux gènes de la fluvastatine : une étiquette qui dépend désormais de deux gènes tous deux présents à l'entrée du réseau est une fonction que le réseau peut apprendre, alors que l'étiquette antérieure dépendait d'un gène seul et était donc, pour une partie des profils, imprévisible à partir de l'entrée. Cette explication est plausible et cohérente avec la localisation des erreurs, mais elle n'est pas démontrée : aucune analyse appariée ligne par ligne entre les deux versions du corpus n'a été faite, les deux corpus n'ont pas les mêmes lignes, et la hausse des erreurs de XGBoost ne reçoit pas d'explication. Elle est donc présentée comme une hypothèse, non comme un résultat.

::: {custom-style="FigureImg"}
![](fig/fig_6_2.png){width=15cm}
:::

::: {custom-style="LegendeFigure"}
Figure 6.3 : Comparaison du réseau, de XGBoost et de Random Forest sur le corpus v15 : F1 macro et taux d'EVITER manqués (développement, moyenne de 5 graines, intervalle de confiance à 95 % par bootstrap sur les profils).
:::

**Limites de cette comparaison.** L'accord est mesuré avec les règles, non avec la clinique. La parenté entre profils n'est pas contrôlée dans le bootstrap. Quatre comparaisons sont rapportées sans correction de multiplicité ; la première, celle du réseau et de XGBoost, est la comparaison principale désignée par le protocole, les autres sont secondaires. XGBoost et Random Forest sont un modèle unique recevant l'identifiant du médicament comme variable, alors que le réseau est multitâche et prédit les 189 médicaments d'un seul coup : l'égalité de protocole porte sur les plis, le réglage et la calibration, non sur la forme du problème posé à chaque modèle. Ces constats de développement sont confrontés à l'ensemble final en section 6.7.

### 6.6 Cohérence avec des études indépendantes (exploratoire)

Pour 8 couples gène-médicament, le sens de l'avis du réseau a été comparé à une étude clinique indépendante de CPIC et de DPWG. Cette analyse est exploratoire pour deux raisons, énoncées avant son résultat : le réseau a été interrogé avec des profils construits (tous les gènes à la valeur normale, un seul modifié) et non avec des patients ; seuls les résumés des articles ont été lus. Les huit couples ont été retenus parce qu'ils sont les seuls pour lesquels une étude clinique de référence a pu être identifiée et lue ; ce n'est pas un échantillon des 189 médicaments.

L'interrogation a été refaite avec les modèles v15 : pour les 23 profils construits des 8 couples, l'action du réseau est identique à celle des modèles de la version antérieure, et elle l'est aussi pour les 43 profils d'une série élargie. Le tableau 6.6 vaut donc pour le réseau v15.

::: {custom-style="LegendeTableau"}
Tableau 6.6 : Concordance de sens entre l'avis du réseau et une étude indépendante, par couple gène–médicament
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

Le sens est le même dans les 8 cas. Cet accord ne porte que sur la direction de l'effet : il ne montre pas que la recommandation améliore la prise en charge, et il ne porte pas sur l'intensité de l'avis. Pour la simvastatine et le tamoxifène, l'intensité « à éviter » dépasse ce que montre l'étude ; pour le fluorouracile chez un profil sans activité DPYD, l'avis du réseau est au contraire plus faible que celui de la règle, qui est celui qu'affiche l'application comme avis de référence. Les couples des thiopurines, de UGT1A1 et de l'irinotécan, des inhibiteurs de la pompe à protons, du tacrolimus, des médicaments liés à G6PD et des antidépresseurs tricycliques n'ont pas de source lue : l'absence d'un couple dans ce tableau signifie qu'aucune étude n'a été lue pour lui, non que la concordance y serait moins bonne.

### 6.7 Évaluation unique sur l'ensemble final

Les sections précédentes reposent toutes sur les profils de développement, qui ont servi à choisir les configurations, les règles de décision et les seuils. Leurs résultats peuvent donc être optimistes. L'ensemble final de 138 profils (23 455 lignes, dont 816 EVITER) a été mis de côté avant tout essai pour estimer les performances sur des profils qui n'ont joué aucun rôle dans ces choix. Il a été lu une seule fois, après la rédaction d'un protocole qui fixait à l'avance les modèles, les métriques, les règles de décision et les sous-groupes rapportés ; aucun résultat de cette lecture n'a entraîné de modification.

**Modèles évalués.** Les trois modèles (réseau en configuration 35 calibré par température, XGBoost, Random Forest) ont été réentraînés avec leurs hyperparamètres inchangés, la même graine (42) et la même validation interne de 10 % des profils, sur 1 207 profils de développement au lieu de 1 241. Les 34 profils retirés sont ceux que le pedigree du projet 1000 Genomes relie à un profil de l'ensemble final (section 3.8, point 3). Cette règle a été fixée avant toute lecture : laisser un apparenté d'un profil final à l'entraînement aurait pu rendre l'évaluation optimiste, et le retrait ne coûte que 2,7 % des profils de développement. La liste des 34 a été recalculée à partir du pedigree et n'a été acceptée qu'après avoir reproduit exactement tous les décomptes de l'audit de parenté (187 paires, 34 paires entre ensemble final et développement, 34 profils de développement distincts). Les hyperparamètres n'ont pas été re-sélectionnés, parce qu'une nouvelle recherche sur 1 207 profils aurait été un nouveau choix fait sans contrôle et que la question posée est celle de la valeur des modèles tels qu'ils ont été choisis. Les seuils d'abstention sont ceux de la section 6.3, calculés sur la validation croisée de développement. Ces modèles servent uniquement à l'évaluation ; l'application conserve ceux entraînés sur les 1 241 profils, pour lesquels aucune mesure sur l'ensemble final n'est donc disponible.

**Méthode statistique.** Les intervalles de confiance à 95 % sont obtenus par bootstrap percentile sur les 138 identifiants de profil, avec 10 000 tirages communs aux trois modèles, de sorte que les différences sont appariées. Une évaluation unique ne coûtant que quelques secondes, le nombre de tirages n'était pas limité par le calcul. Il a été porté à 10 000, au lieu des 2 000 de la section 6.5, parce que les bornes d'un intervalle percentile reposent sur les 2,5 % de tirages extrêmes : 10 000 tirages en placent 250 de chaque côté au lieu de 50, ce qui réduit l'erreur de Monte-Carlo sur les bornes. Davantage de tirages n'aurait pas réduit l'incertitude principale, qui vient du nombre de profils (138) et non du nombre de tirages. La règle de décision est celle de la section 6.5, avec la même marge de 0,001.

::: {custom-style="LegendeTableau"}
Tableau 6.7 : Évaluation unique sur l'ensemble final (138 profils, 23 455 lignes, 816 EVITER ; intervalles de confiance à 95 %, bootstrap sur les profils)
:::

| Modèle | F1 macro | Exactitude | EVITER manqués (n) | Taux d'EVITER manqués | Précision EVITER | Erreurs (n) | ECE | Log-loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Réseau, configuration 35 | 0,9940 \[0,9839 ; 0,9992\] | 0,9985 | 10 \[3 ; 20\] | 1,23 % | 0,989 | 35 | 0,0013 | 0,0096 |
| XGBoost | 0,9989 \[0,9976 ; 0,9998\] | 0,9998 | 3 \[0 ; 7\] | 0,37 % | 1,000 | 5 | 0,0172 | 0,0183 |
| Random Forest | 0,9300 \[0,9154 ; 0,9429\] | 0,9752 | 37 \[20 ; 57\] | 4,53 % | 0,797 | 581 | 0,1620 | 0,2349 |

Les rappels du réseau sont de 0,9995 pour STANDARD, 0,9952 pour ADAPTER\_DOSE, 0,9877 pour EVITER et 0,9926 pour SURVEILLER ; son F1 macro sans la classe SURVEILLER est de 0,9942.

**Décisions selon la règle figée.**

- Réseau moins XGBoost = −0,0049 \[−0,0152 ; +0,0007\] : **non tranché**. L'écart d'EVITER manqués, +7 \[−1 ; +17\], n'est pas démontré non plus.
- Réseau moins Random Forest = +0,0640 \[0,0519 ; 0,0772\] : **réseau supérieur** ; 27 EVITER manqués de moins \[14 ; 41\].
- XGBoost moins Random Forest = +0,0689 \[0,0563 ; 0,0832\] : **XGBoost supérieur** ; 34 EVITER manqués de moins \[18 ; 54\].

Une seule ligne est erronée à la fois chez le réseau et chez XGBoost.

**Lecture.** L'ensemble final confirme le classement établi en développement : XGBoost obtient les meilleurs résultats sur toutes les mesures sauf l'ECE, le réseau vient ensuite sans que l'écart soit tranché, et les deux dominent Random Forest. L'hypothèse principale du mémoire, une supériorité du réseau sur les modèles à base d'arbres, n'est pas confirmée par cette évaluation indépendante. L'intervalle de la différence entre le réseau et XGBoost est plus large qu'en développement (0,016 contre 0,0014), ce qui est attendu avec 138 profils au lieu de 1 241 : l'ensemble final ne pouvait pas trancher un écart de l'ordre du millième, et il ne le fait pas. Le F1 macro du réseau est plus bas sur l'ensemble final qu'en développement (0,9940 contre 0,99820), alors que celui de XGBoost reste stable (0,9989 contre 0,99829) ; l'analyse de la section suivante montre que cette baisse est portée par un seul profil.

**Abstention.** Le tableau 6.8 applique au réseau les seuils figés de la section 6.3.

::: {custom-style="LegendeTableau"}
Tableau 6.8 : Abstention du réseau sur l'ensemble final, aux seuils fixés sur le développement
:::

| Part visée d'abstention | Seuil | Couverture | Lignes écartées | F1 macro des lignes gardées | EVITER manqués acceptés |
| --- | --- | --- | --- | --- | --- |
| 0,5 % | 0,9934 | 0,9939 | 143 | 0,9963 | 3 sur 804 |
| 1 % (seuil de l'application) | 0,9981 | 0,9888 | 263 | 0,9974 | 2 sur 800 |
| 2 % | 0,9994 | 0,9807 | 452 | 0,9981 | 2 sur 797 |
| 5 % | 0,9998 | 0,9630 | 867 | 0,9981 | 2 sur 794 |

Les seuils écartent sur l'ensemble final une part de lignes un peu supérieure à celle visée (1,12 % au lieu de 1 % au seuil de l'application) : le réseau y est un peu moins confiant qu'en développement, ce qui est cohérent avec des profils non vus. Au seuil de l'application, 8 des 10 EVITER manqués sont écartés et signalés « à vérifier ». Ce résultat diffère de celui du développement, où la moitié des EVITER manqués résistait à l'abstention (section 6.3). Il porte sur 10 lignes et ne suffit pas à conclure que l'abstention protège bien les EVITER manqués en général ; il montre seulement que, sur cet ensemble, la plupart de ces erreurs étaient des hésitations.

**Sous-groupes fixés à l'avance.** Les 34 profils finaux dont un apparenté a été retiré de l'entraînement (5 818 lignes) obtiennent un F1 macro de 0,9974 avec le réseau, 1,000 avec XGBoost et 0,9474 avec Random Forest ; les 104 autres profils (17 637 lignes) obtiennent 0,9930, 0,9985 et 0,9245. Aucun avantage des profils apparentés n'apparaît, ce qui est cohérent avec leur retrait de l'entraînement. Deux profils finaux ont un vecteur d'entrée identique à celui d'un profil de développement ; ils ont été conservés et rapportés à part, comme prévu : aucun des trois modèles ne commet d'erreur sur eux (169 et 168 lignes).

**Analyse descriptive, faite après la lecture.** L'analyse qui suit n'était pas prévue par le protocole. Elle ne modifie aucun chiffre ci-dessus et n'a entraîné aucun nouvel essai.

Un seul profil, HG03684, porte 26 des 35 erreurs du réseau sur ses 119 lignes, dont 4 des 10 EVITER manqués. Il combine plusieurs valeurs rares : G6PD non typé, cas présent chez un seul profil de développement, CYP2C9 à 0,25, F5 à 0 et G6PD à 0 ; aucun profil de développement n'en est à moins de cinq variables. XGBoost ne commet aucune erreur sur ce profil. En dehors de lui, le réseau commet 9 erreurs sur 23 336 lignes. Ces erreurs portent sur des médicaments dont les gènes ne sont pas ceux qui rendent le profil rare : l'amitriptyline dépend de CYP2C19 et CYP2D6, non de G6PD. Le réseau étant multitâche, une valeur inhabituelle d'un gène sans rapport avec un médicament modifie la représentation commune et peut changer l'avis donné pour ce médicament. C'est une contrepartie plausible de l'architecture multitâche choisie au chapitre 4. XGBoost reçoit les mêmes variables et ne se trompe pas sur ce profil ; pourquoi il y est moins sensible n'a pas été mesuré.

Cette analyse a une conséquence pour l'application. Le contrôle de domaine (chapitre 5) vérifie, pour chaque médicament, que la combinaison de valeurs des gènes de ce médicament a été vue à l'entraînement ; pour les 26 médicaments en erreur chez HG03684, c'était le cas, et le contrôle ne l'aurait pas signalé. L'abstention en aurait écarté 16 ; les 10 autres auraient été affichés avec une confiance d'au moins 0,998. Deux protections restent dans l'application : la règle de la directive est affichée à côté de l'avis du réseau, et le second avis de XGBoost, juste pour ce profil, aurait fait apparaître un désaccord. Ce cas montre que le contrôle de domaine par médicament ne suffit pas à repérer un profil atypique dans son ensemble ; un contrôle portant sur le profil complet n'a pas été mis en œuvre dans ce travail.

**Réserves.** L'ensemble final est réservé mais non vierge : 125 des 138 profils ont participé à la validation croisée d'essais antérieurs du projet, sans jamais être lus pour une évaluation (section 3.8, point 9). Le pedigree ne décrit que la parenté déclarée, non la structure de population. Deux paires de profils apparentés se trouvent à l'intérieur de l'ensemble final et sont traitées comme indépendantes par le bootstrap. Enfin, comme partout dans ce chapitre, la référence est le moteur de règles : l'évaluation mesure la reproduction des directives sur des profils nouveaux, non la justesse clinique des avis.

### 6.8 Résultats exploratoires négatifs

Deux pistes ont été abandonnées après mesure. Elles sont rapportées parce qu'elles répondent à RQ4 et RQ5 par la négative et qu'elles délimitent ce que l'application ne fait pas.

**Médicaments jamais vus.** Un réseau recevant le profil génétique et des descripteurs du médicament, sans aucune information de directive, a été évalué sur des médicaments laissés de côté à l'entraînement (3 graines, bootstrap sur les médicaments, 400 tirages). L'AUROC pour la distinction « non STANDARD » est de 0,774 \[0,726 ; 0,823\] avec les seuls liens gène-médicament, contre 0,817 \[0,779 ; 0,855\] pour une référence qui prédit par la fréquence des classes selon le gène et le phénotype, et 0,781 \[0,730 ; 0,835\] pour les 5 plus proches voisins. La différence avec la première référence est de −0,043 \[−0,079 ; −0,009\], donc défavorable au réseau ; avec les voisins, elle est de −0,007 \[−0,043 ; +0,028\], donc non tranchée. L'ajout de l'empreinte moléculaire du médicament dégrade les résultats. En laissant de côté une classe ATC entière, puis sur les médicaments ajoutés entre deux versions du corpus, le réseau reste inférieur aux références ou le résultat n'est pas concluant.

La conclusion est que la description du médicament ne permet pas de prédire l'action pour un médicament jamais vu mieux que des références simples. Elle a deux conséquences : la branche « description du médicament » n'est pas intégrée à l'application, et le médicament y reste une sortie du réseau et non une entrée (chapitre 4). Une explication de ce résultat mérite d'être retenue : la référence par gène et phénotype est forte, parce qu'une grande partie du signal vient de la rareté du profil génétique et non du médicament. Limites : 189 médicaments seulement, descripteurs plus riches pour les médicaments déjà couverts, 3 graines.

**Associations publiées.** Sur 2 141 lignes d'associations ClinPGx (256 médicaments, 80 gènes), la direction publiée de l'effet est prédite avec une exactitude de 0,638 ± 0,007 pour une séparation par couple gène-médicament, contre 0,581 pour la classe majoritaire et 0,656 pour une loi a priori par gène et catégorie ; pour une séparation par variant, 0,641 ± 0,008 contre 0,620. Le signal est faible (AUROC 0,651) et, sur des couples jamais vus, une loi a priori simple fait aussi bien ou mieux. Les étiquettes sont de plus bruitées : 957 des 2 141 lignes appartiennent à des combinaisons où des directions contradictoires sont publiées. Cette piste n'a pas été poursuivie.

### 6.9 Synthèse et limites des résultats

**Mesuré.** Sur 211 177 lignes hors pli, le réseau de profil déployé reproduit les étiquettes issues des règles avec un F1 macro de 0,99820 ± 0,00075 et manque 0,66 % des situations à éviter ; ses erreurs se concentrent sur quatre médicaments à règle à deux gènes. Ses probabilités sont bien calibrées globalement (ECE 0,00029) après mise à l'échelle de la température. La confiance repère les erreurs de façon partielle (AUROC 0,870) et, en développement, protège moins bien les EVITER manqués que les autres erreurs. Sous un protocole identique, le réseau et XGBoost ne sont pas départagés sur le F1 macro, et sont déclarés équivalents pour la configuration déployée ; les deux dominent nettement Random Forest. XGBoost conserve un avantage démontré sur le critère de sécurité, avec 38 EVITER manqués de moins. Les erreurs des deux modèles se recouvrent très peu, 9 lignes sur environ 90 de chaque côté. Le réseau de choix retrouve exactement l'ensemble de la convention de cible dans 98,92 % des cas, contre 34,35 % pour une référence qui ignore le profil, et ne propose jamais de médicament à éviter. Le sens des avis concorde avec 8 études pour les 8 couples testés.

Sur l'ensemble final, lu une seule fois, le classement est confirmé : XGBoost obtient un F1 macro de 0,9989 et manque 3 lignes EVITER sur 816, le réseau 0,9940 et 10, Random Forest 0,9300 et 37. L'écart entre le réseau et XGBoost reste non tranché. Au seuil de l'application, l'abstention écarte 8 des 10 EVITER manqués par le réseau. La baisse du réseau par rapport au développement est portée par un seul profil atypique, sur lequel XGBoost ne se trompe pas.

**Non mesuré ou non démontré.**

- La justesse clinique des avis. Toutes les mesures de ce chapitre portent sur l'accord avec des règles ; une seule règle est confrontée à des patients réels (chapitre 7).
- La supériorité du réseau sur les modèles à base d'arbres. Elle n'est établie ni en développement ni sur l'ensemble final : la comparaison conclut à une différence non tranchée sur le F1 macro et à un désavantage du réseau sur la sécurité en développement. L'hypothèse principale du mémoire n'est donc pas confirmée.
- La robustesse du réseau à un profil atypique dans son ensemble. Un seul profil de l'ensemble final suffit à faire chuter son F1 macro, et le contrôle de domaine par médicament ne le repère pas.
- Les performances sur l'ensemble final des modèles de l'application eux-mêmes, entraînés sur 1 241 profils ; l'évaluation porte sur des modèles de même configuration entraînés sur 1 207 profils.
- Les performances de la chaîne complète depuis un fichier VCF : les valeurs de ce chapitre portent sur des profils du corpus, non sur des profils lus dans un VCF. Cette question est traitée au chapitre 8.
- La généralisation à un médicament jamais vu (résultat négatif, section 6.8) et à une combinaison de gènes jamais observée, dont le cas du lonafarnib donne un exemple (section 6.1).

Les essais abandonnés, négatifs ou corrigés sont récapitulés dans l'annexe A.
