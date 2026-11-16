## Chapitre 9 : Discussion, limites et perspectives

Ce chapitre interprète les résultats des chapitres 6 à 8, répond aux sept questions de recherche de la section « Objectifs » et énonce les limites du travail et les perspectives qu'elles ouvrent.

### 9.1 Ce que le travail établit, et dans quels termes

Une précaution de lecture gouverne tout ce chapitre et a été posée dès le chapitre 3 : les étiquettes du corpus sont produites par un moteur de règles appliquant les recommandations CPIC, DPWG, RNPGx et les étiquettes réglementaires. Elles ne sont pas des réponses cliniques observées. Par conséquent, un score élevé signifie que le modèle reproduit fidèlement ces recommandations, et non que l'avis produit est cliniquement juste. Cette distinction n'est pas une précaution de style : elle détermine ce que chacun des résultats suivants autorise à conclure.

Sous cette réserve, trois constats sont établis.

Le premier est que **la tâche est apprenable avec une fidélité élevée**. Sur 211 177 lignes hors pli, le réseau déployé reproduit l'étiquette du moteur de règles avec un F1 macro de 0,99820 ± 0,00075 et manque 0,66 % des situations à éviter. Ses probabilités sont bien calibrées globalement après mise à l'échelle de la température (ECE de 0,00029). Sur l'ensemble final de 138 profils, lu une seule fois après que toutes les décisions ont été prises, le F1 macro est de 0,9940 (intervalle à 95 % : 0,9839 à 0,9992) et 10 des 816 situations à éviter sont manquées ; la baisse par rapport au développement est portée par un seul profil atypique (section 6.7).

Le deuxième est que **la chaîne complète, depuis un fichier VCF, restitue les recommandations de référence**. Sur 104 personnes absentes du corpus, la recommandation affichée est retrouvée chez PharmCAT pour 95,9 % des 3 357 lignes comparables (99,1 % pour les recommandations CPIC), et l'action prédite par le réseau coïncide avec l'action soutenue par PharmCAT dans 99,73 % des 2 600 unités examinées.

Le troisième est que **la seule règle confrontée à des patients réels va dans le bon sens, mais imprécisément**. Sur 5 774 patients traités par warfarine, les patients que le corpus étiquette comme devant recevoir une dose adaptée reçoivent une dose d'entretien égale à 0,830 fois celle des patients de génotype de référence (intervalle à 95 % : 0,804 à 0,857), avec un gradient cohérent selon le génotype. La règle corrigée du corpus v15, qui ajoute VKORC1, sépare beaucoup mieux les doses sur les mêmes patients, dans une analyse post hoc (section 7.7).

Ces trois constats portent sur des objets différents — l'apprentissage, la restitution, la validité clinique d'une règle — et leur portée décroît dans cet ordre. Le premier est solide et bien mesuré ; le deuxième l'est également, mais mesure une concordance entre systèmes partageant leur source ; le troisième ne concerne qu'une molécule sur 189.

### 9.2 Réponse aux questions de recherche

**RQ1 — Le profil multi-gènes améliore-t-il la prédiction par rapport au seul gène associé au médicament ?**

La réponse est partielle et doit être formulée avec prudence. Un audit de déterminisme mené sur le corpus v12 établit que l'action est constante ou déterminée par un seul gène pour 121 des 133 médicaments alors couverts : le bénéfice attendu d'une lecture globale du profil se concentre donc sur une minorité de médicaments, ceux dont la règle dépend effectivement de plusieurs gènes — amitriptyline, azathioprine, carbamazépine, clomipramine, doxépine, fluvastatine, imipramine, mercaptopurine, rosuvastatine, sertraline, thioguanine et trimipramine. Refait sur le corpus v15, l'audit donne 175 médicaments sur 189 dont l'action est constante ou déterminée par un seul gène, et 14 dont l'action dépend de plusieurs gènes : les douze précédents, plus la fluindione et la warfarine (section 3.4). Sur le corpus v15, les erreurs du réseau se concentrent précisément sur des médicaments dont l'étiquette combine deux gènes : l'azathioprine, la rosuvastatine et la fluvastatine portent avec la sertraline 48 des 76 erreurs (section 6.1). C'est là que le profil multi-gènes est nécessaire, et c'est là que le réseau est le moins fiable, parce que les combinaisons rares y sont peu représentées. Le travail ne comporte pas de modèle « un seul gène » qui permettrait de mesurer l'apport du profil complet par comparaison directe : la question RQ1 reste sans réponse quantitative.

**RQ2 — Le réseau est-il plus performant que Random Forest et XGBoost ?**

La réponse est non pour XGBoost, au sens où aucune supériorité du réseau n'est établie, et oui pour Random Forest.

Dans la comparaison menée sous protocole identique — mêmes plis, même budget de réglage, même critère d'arrêt, même calibration — la différence de F1 macro entre le réseau et XGBoost est de −0,000345, avec un intervalle de confiance à 95 % de [−0,00106 ; +0,00034]. Cet intervalle contient zéro : aucune différence n'est démontrée statistiquement. Il dépasse d'un côté la marge d'équivalence pratique de 0,001 fixée avant les mesures : l'équivalence n'est pas démontrée non plus. La règle de décision du protocole conclut donc que la comparaison n'est pas tranchée. Pour la configuration effectivement déployée dans l'application, la conclusion est plus nette : l'intervalle tient entièrement dans la marge ([−0,00052 ; +0,00076]) et le protocole déclare les deux modèles équivalents. Le réseau et XGBoost dominent l'un comme l'autre Random Forest (0,99269), dont le F1 macro est inférieur de plus de cinq millièmes.

Trois précautions encadrent cette réponse. D'abord, « non tranché » et « équivalent » ne disent pas que le réseau fait mieux : l'hypothèse principale du mémoire, qui postulait un avantage du Deep Learning, n'est pas confirmée. Ensuite, le critère de sécurité, lui, est tranché et reste défavorable au réseau, qui manque 38 situations à éviter de plus que XGBoost, avec un intervalle qui exclut zéro. Enfin, sur la version antérieure du corpus, le même protocole concluait à la supériorité de XGBoost (section 6.5) : une conclusion qui change avec la version des règles dépend des règles, et n'est pas une propriété des modèles.

L'évaluation unique sur l'ensemble final de 138 profils (section 6.7) confirme ce classement sur des profils qui n'ont joué aucun rôle dans les choix : la différence de F1 macro entre le réseau et XGBoost est de −0,0049, avec un intervalle de [−0,0152 ; +0,0007], de nouveau non tranchée ; XGBoost obtient les meilleurs résultats sur toutes les mesures sauf l'erreur de calibration, et manque 3 situations à éviter contre 10 pour le réseau. Les deux modèles dominent Random Forest (F1 macro 0,9300).

Ce résultat reste cohérent avec ce que la littérature établit sur les données tabulaires (section 2.5) : les modèles à base d'arbres y sont au moins aussi bons que les réseaux, sans leur être systématiquement supérieurs. Une explication plausible, formulée comme hypothèse non testée, tient à la forme de la cible : les étiquettes proviennent d'un moteur dont les décisions sont des seuils sur des valeurs discrètes, soit exactement la classe de fonctions qu'un arbre représente nativement.

Ce constat ne conduit pas à remplacer le modèle de l'application : le réseau est équivalent à XGBoost sur le critère principal, et il produit en une passe les sorties des 189 médicaments avec des probabilités calibrées, tout en se prêtant à l'extension du jeu d'entrées. Une mesure de la section 6.5 renforce ce choix sans avoir été cherchée pour cela : les erreurs du réseau et celles de XGBoost ne se recouvrent presque pas, neuf lignes communes sur environ quatre-vingt-dix de chaque côté. Les deux modèles échouent donc sur des situations différentes, ce qui donne un fondement mesuré au second avis affiché par l'application (chapitre 5) et indique qu'une combinaison des deux pourrait réduire sensiblement le nombre d'erreurs — piste écartée ici, parce qu'une règle de combinaison choisie au vu des mêmes prédictions hors pli serait un réglage présenté comme un résultat. Le désavantage sur les situations à éviter manquées reste à la charge du réseau : c'est pourquoi l'avis de XGBoost et la règle officielle sont affichés à côté de sa prédiction, et non après elle.

**RQ3 — Les probabilités sont-elles calibrées, et un seuil de confiance signale-t-il les cas incertains ?**

La réponse est affirmative pour la calibration et nuancée pour le seuil. Après mise à l'échelle de la température, l'erreur de calibration attendue hors pli est de 0,00029. Cette valeur doit cependant être lue avec la réserve posée à la section 6.2 : elle est faible en partie parce que la quasi-totalité des lignes sont correctes et très confiantes, et elle ne démontre pas que les probabilités sont bien calibrées sur les lignes rares et difficiles.

L'ordre des modèles sur ce critère s'est inversé entre les deux versions du corpus ; cette inversion est rapportée sans qu'aucune conclusion en soit tirée, les valeurs étant toutes inférieures à 0,0004 et sans intervalle de confiance. L'énoncé défendable est que les trois modèles sont bien calibrés après mise à l'échelle de la température et que leurs écarts ne sont pas interprétables à ce niveau : la calibration n'est un argument en faveur d'aucun des trois.

Quant au seuil, il remplit partiellement son office. La confiance sépare les lignes correctes des lignes erronées avec une aire sous la courbe ROC de 0,870, et les 1 % de lignes les moins confiantes concentrent 77,0 % des erreurs. Mais en développement, au seuil employé par l'application, une part importante des situations à éviter manquées reste acceptée : ce sont des erreurs commises avec une confiance élevée, que l'abstention ne peut pas détecter (section 6.3). Sur l'ensemble final, le même seuil écarte 263 lignes et 8 des 10 situations à éviter manquées ; il laisse cependant afficher, avec une confiance d'au moins 0,998, 10 erreurs commises sur le profil atypique de la section 6.7.

**RQ4 — La description moléculaire du médicament améliore-t-elle la prédiction, notamment pour un médicament jamais vu ?**

La réponse est négative. Un réseau recevant le profil et des descripteurs du médicament, évalué sur des médicaments laissés de côté, obtient une aire sous la courbe ROC de 0,774 pour distinguer les situations non standard, contre 0,817 pour une référence simple fondée sur la fréquence des classes par gène et phénotype. L'empreinte moléculaire dégrade les résultats. Ce résultat négatif est la raison pour laquelle cette architecture n'est pas intégrée à l'application.

La référence à laquelle le réseau est comparé n'est pas naïve, une grande partie du signal provenant de la rareté du profil génétique lui-même : l'échec porte donc sur la capacité à transférer une connaissance d'un médicament à un autre, et non sur la prédiction en général.

**RQ5 — Les performances se conservent-elles hors des conditions d'entraînement ?**

La réponse diffère selon la nature de l'écart, et c'est un résultat en soi.

Pour des **profils non utilisés à l'entraînement** mais complets, la performance se conserve en moyenne : sur 104 personnes lues depuis leur fichier VCF, le réseau diverge de la règle dans 10 lignes sur 6 322, soit 0,2 %, et sur l'ensemble final de 138 profils son F1 macro reste de 0,9940. Mais cette moyenne cache une fragilité : un seul profil de l'ensemble final, dont plusieurs valeurs génétiques sont rares, porte 26 des 35 erreurs du réseau, alors que XGBoost n'en commet aucune sur ce profil. Le contrôle de domaine de l'application, qui porte sur les gènes de chaque médicament, ne l'aurait pas signalé (section 6.7).

Pour des **profils partiels**, elle se dégrade nettement : sur les onze patients publiés dont seuls quatre à sept gènes sur 31 sont renseignés, la divergence atteint 11,4 % des lignes (50 sur 439). Le réseau est donc fragile hors de la distribution sur laquelle il a été entraîné, et c'est la règle affichée à côté de sa prédiction, ainsi que l'alerte « à vérifier », qui constituent la protection.

Pour des **médicaments absents de l'entraînement**, elle n'est pas démontrée (RQ4).

Pour des **combinaisons de valeurs jamais observées**, l'application ne prédit pas : elle déclare le cas hors domaine et n'affiche aucun avis.

**RQ6 — Les actions produites sont-elles concordantes avec l'interprétation attendue des références ?**

La réponse est affirmative, dans les termes rappelés à la section 9.1. La concordance avec PharmCAT atteint 95,9 % des lignes comparables, dont 99,1 % pour les recommandations CPIC. Les 136 lignes non retrouvées ont été lues une par une : la plupart tiennent à la formulation ou à la structure des textes, sans différence d'action ; les écarts de contenu tiennent au codage de CYP2C9 par score d'activité, qui applique à des génotypes rares la règle d'un génotype fréquent de même score, et à des différences d'appel de NUDT15 (section 8.3). Sur les onze patients publiés, la règle de l'application est conforme à l'article dans les 36 lignes évaluables.

Cette concordance mesure une restitution fidèle de recommandations partagées, non une justesse clinique.

**RQ7 — Les règles qui servent d'étiquettes sont-elles cohérentes avec des données de patients réels ?**

La réponse est affirmative dans le sens, négative dans la précision, et elle révèle une omission.

Dans le sens, l'hypothèse principale est soutenue : les patients étiquetés comme devant recevoir une dose adaptée reçoivent effectivement une dose plus basse. Dans la précision, l'étiquette ne détecte qu'environ 31 % des doses basses, et le génotype le plus fréquent de la classe intermédiaire n'est pas distinguable du génotype de référence dans la population complète. Dans l'omission : la règle du corpus v14 ignorait VKORC1, qui explique dans ces données environ six fois plus de variance de la dose que CYP2C9 (R² de 0,294 contre 0,048). Ce n'était pas une limite de la source, puisque la DPWG publie une recommandation fondée sur VKORC1 pour la warfarine : c'était une omission du corpus, corrigée dans le corpus v15. Sur les mêmes patients, dans une analyse post hoc qui ne constitue pas une validation indépendante, l'étiquette corrigée sépare beaucoup mieux les doses (rapport 0,559 au lieu de 0,828) et détecte 75 % des doses basses au lieu de 32 %. Elle classe cependant \*1/\*2 en dose standard, conformément à la directive, alors que ces patients reçoivent une dose plus basse d'environ 16 % (section 7.7).

### 9.3 La circularité entre les règles et le modèle

La limite la plus structurante de ce travail n'est aucune de celles qui précèdent prise isolément, mais leur cause commune. Le réseau est entraîné sur des étiquettes produites par un moteur de règles ; ce moteur applique les recommandations de CPIC et de la DPWG ; PharmCAT applique les mêmes recommandations. Mesurer l'accord entre ces systèmes ne peut donc pas établir leur justesse : il établit qu'ils lisent les mêmes textes de la même façon.

Trois dispositifs sortent de ce cercle, et ils sont les seuls.

La **comparaison des génotypes à GeT-RM** (section 8.2) est indépendante, puisque cette référence est établie par un programme externe sans rapport avec la chaîne évaluée. Elle révèle d'ailleurs que la concordance est élevée pour certains gènes et faible pour d'autres.

La **confrontation de la règle de la warfarine aux patients de l'IWPC** (chapitre 7) est indépendante, puisque les doses observées ne proviennent d'aucune recommandation. C'est la seule validation de ce type du mémoire, et elle ne porte que sur une molécule ; pour la règle corrigée du corpus v15, elle n'est plus indépendante, la correction ayant été motivée par ces mêmes données.

La **comparaison du sens des avis à huit études cliniques** (section 6.6) est partiellement indépendante : les études sont antérieures et distinctes des recommandations, mais la comparaison porte sur la direction de l'effet et non sur son ampleur, et elle a été menée avec des profils construits ; refaite avec les modèles du corpus v15, elle donne les mêmes actions dans les 23 tests des huit couples.

Il en découle que la portée de ce travail est celle d'une démonstration de faisabilité : il établit qu'un modèle peut reproduire fidèlement un corpus de recommandations à partir d'un profil multi-gènes, et que la chaîne complète fonctionne depuis un fichier VCF. Il n'établit pas que les avis produits améliorent la prise en charge, et ne pouvait pas l'établir avec les données employées.

### 9.4 Limites

Les limites propres à chaque étape sont énoncées aux sections 3.8, 4.10, 5.8, 6.9, 7.8 et 8.8. Les six suivantes sont celles qui affectent l'interprétation d'ensemble.

1. **Les étiquettes sont des règles, non des observations cliniques.** Toutes les mesures des chapitres 6 et 8 expriment une fidélité à des recommandations. La validité clinique de ces recommandations repose sur les études primaires qui les fondent, et n'est pas établie par ce travail.

2. **La validation est partiellement circulaire** (section 9.3). Les trois dispositifs qui y échappent portent respectivement sur les génotypes, sur une molécule, et sur la direction de l'effet pour huit couples.

3. **Les règles ont été corrigées en partie à partir des données de validation.** Trois défauts de règles ont été identifiés : les thiopurines traitées par un seul gène alors que la recommandation en combine deux, la règle DPWG de CYP2C9 appliquée par score d'activité, et VKORC1 absent de la règle de la warfarine. Les deux premiers ont été mis en évidence par la comparaison à PharmCAT, le troisième par la confrontation aux patients réels, et le corpus v15 les corrige. Un quatrième point, la priorité des règles à plusieurs gènes pour la fluvastatine, a été vérifié à la même occasion et s'est révélé conforme. Leur existence montre que la validation externe remplit son office ; mais, pour les règles corrigées, la comparaison à PharmCAT et la confrontation aux patients de l'IWPC ne sont plus des validations indépendantes. Un défaut demeure : le codage de CYP2C9 par score d'activité applique à des génotypes rares, comme \*1/\*8 ou \*1/\*11, la règle de \*1/\*2, qui a le même score, et l'écart avec la directive est mesuré pour la warfarine et le siponimod (section 8.3).

4. **L'appel d'allèles est incertain pour plusieurs gènes.** La concordance avec GeT-RM est élevée pour CYP2C9 et CYP3A5, et faible pour CYP2B6, SLCO1B1, UGT1A1 et DPYD. Une erreur à cette étape se propage inchangée à l'avis produit. Les causes n'ont pas été attribuées cas par cas, ce qui reste une limite, et un désaccord ne prouve pas une erreur de l'outil, la nomenclature des allèles évoluant.

5. **Le réseau est fragile sur les profils partiels** (RQ5) : la divergence passe de 0,2 % à 11,4 % lorsque seuls quatre à sept gènes sur 31 sont renseignés. C'est la situation la plus probable en pratique clinique réelle, où un panel ne couvre pas tous les gènes. La même fragilité apparaît sur un profil complet mais atypique de l'ensemble final, que le contrôle de domaine par médicament ne repère pas (section 6.7).

6. **La constitution du corpus n'est pas entièrement justifiée.** La règle ayant retenu 1 379 échantillons parmi les 3 202 disponibles n'a pas été retrouvée, et la liste n'est pas un tirage aléatoire. Le corpus n'est donc pas un échantillon documenté de la population d'origine, les fréquences alléliques observées ne doivent pas être lues comme des fréquences de population, et l'effet du nombre de profils sur les performances n'a pas été mesuré. Par ailleurs, le regroupement des lignes se fait par identifiant de profil et non par parenté : 374 des 1 379 profils ont un apparenté dans le corpus. Une analyse de sensibilité montre que l'effet sur le F1 macro est inférieur au seuil fixé d'avance, mais la parenté réelle n'est pas contrôlée au-delà du pedigree déclaré.

### 9.5 Perspectives

Les perspectives suivantes découlent des limites ci-dessus et sont classées par leur coût.

**Codage de CYP2C9 par diplotype.** Le seul écart de contenu systématique restant avec PharmCAT tient au codage de CYP2C9 par score d'activité. Porter le diplotype, et non le seul score, supprimerait cet écart pour la warfarine et le siponimod ; cela change l'espace d'entrée du réseau et impose de reconstruire le corpus et de réentraîner les modèles sous le protocole inchangé.

**Contrôle de domaine sur le profil complet.** Le cas de l'ensemble final montre qu'un profil atypique dans son ensemble échappe au contrôle par médicament. Une mesure de distance entre le profil du patient et les profils d'entraînement, fixée sur les données de développement, permettrait de signaler ces cas avant d'afficher un avis.

**Mesure de l'effet du nombre de profils.** Une courbe d'apprentissage dirait si les 1 379 profils constituent un plateau ou une contrainte, et transformerait une limite déclarée en résultat mesuré.

**Robustesse aux profils partiels.** La dégradation constatée au point 5 suggère un entraînement incluant des profils volontairement incomplets, de sorte que le réseau apprenne à traiter l'absence d'un gène comme une information et non comme une anomalie.

**Validation clinique et intégration au flux de soins.** La confrontation à des patients réels n'a été possible que pour la warfarine, faute de jeux publics comparables ; et les obstacles décisifs au déploiement — intégration au dossier patient informatisé, pérennité des interprétations, portabilité des résultats (section 2.3) — ne sont pas traités ici.
