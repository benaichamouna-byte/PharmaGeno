## Chapitre 9 : Discussion, limites, conclusion et perspectives

Ce chapitre interprète les résultats des chapitres 6 à 8, répond aux sept questions de recherche posées à la section 1.6, énonce les limites du travail et les perspectives qu'elles ouvrent.

### 9.1 Ce que le travail établit, et dans quels termes

Une précaution de lecture gouverne tout ce chapitre et a été posée dès le chapitre 3 : les étiquettes du corpus sont produites par un moteur de règles appliquant les recommandations CPIC, DPWG, RNPGx et les étiquettes réglementaires. Elles ne sont pas des réponses cliniques observées. Par conséquent, un score élevé signifie que le modèle reproduit fidèlement ces recommandations, et non que l'avis produit est cliniquement juste. Cette distinction n'est pas une précaution de style : elle détermine ce que chacun des résultats suivants autorise à conclure.

Sous cette réserve, trois constats sont établis.

Le premier est que **la tâche est apprenable avec une fidélité élevée**. Sur 209 415 lignes hors pli, le réseau déployé reproduit l'étiquette du moteur de règles avec un F1 macro de 0,9979 ± 0,0012 et manque 0,83 % des situations à éviter. Ses probabilités sont bien calibrées globalement après mise à l'échelle de la température (ECE de 0,0003).

Le deuxième est que **la chaîne complète, depuis un fichier VCF, restitue les recommandations de référence**. Sur 104 personnes absentes du corpus, la recommandation affichée est retrouvée chez PharmCAT pour 97,8 % des 3 534 lignes comparables, et l'action prédite par le réseau coïncide avec l'action soutenue par PharmCAT dans 99,92 % des 2 600 unités examinées.

Le troisième est que **la seule règle confrontée à des patients réels va dans le bon sens, mais imprécisément**. Sur 5 774 patients traités par warfarine, les patients que le corpus étiquette comme devant recevoir une dose adaptée reçoivent une dose d'entretien égale à 0,830 fois celle des patients de génotype de référence (intervalle à 95 % : 0,804 à 0,857), avec un gradient cohérent selon le génotype.

Ces trois constats portent sur des objets différents — l'apprentissage, la restitution, la validité clinique d'une règle — et leur portée décroît dans cet ordre. Le premier est solide et bien mesuré ; le deuxième l'est également, mais mesure une concordance entre systèmes partageant leur source ; le troisième ne concerne qu'une molécule sur 189.

### 9.2 Réponse aux questions de recherche

**RQ1 — Le profil multi-gènes améliore-t-il la prédiction par rapport au seul gène associé au médicament ?**

La réponse est partielle et doit être formulée avec prudence. Un audit de déterminisme mené sur le corpus v12 établit que l'action est constante ou déterminée par un seul gène pour 121 des 133 médicaments alors couverts : le bénéfice attendu d'une lecture globale du profil se concentre donc sur une minorité de médicaments, ceux dont la règle dépend effectivement de plusieurs gènes — amitriptyline, azathioprine, carbamazépine, clomipramine, doxépine, fluvastatine, imipramine, mercaptopurine, rosuvastatine, sertraline, thioguanine et trimipramine. Cet audit n'a pas été refait sur le corpus v14 [à compléter], de sorte que la proportion actuelle n'est pas connue. Il est à noter que les médicaments concernés sont aussi ceux sur lesquels le réseau commet l'essentiel de ses erreurs (section 6.1), ce qui est cohérent : ce sont les décisions les plus complexes.

**RQ2 — Le réseau est-il plus performant que Random Forest et XGBoost ?**

La réponse est négative pour XGBoost et positive pour Random Forest. Dans la comparaison menée sous protocole identique — mêmes plis, même budget de réglage, même critère d'arrêt, même calibration — XGBoost reproduit les règles mieux que le réseau (F1 macro de 0,99941 contre 0,99676), l'écart étant à la fois statistiquement établi et supérieur à la marge d'équivalence pratique fixée à l'avance. Le réseau fait mieux que Random Forest (0,99333). Sur le critère de sécurité, le réseau manque 47 situations à éviter de plus que XGBoost.

Ce résultat est défavorable à l'hypothèse principale du mémoire et il est rapporté comme tel. Il est par ailleurs cohérent avec ce que la littérature établit sur les données tabulaires (section 2.5), et une explication plausible, formulée comme hypothèse non testée, tient à la forme de la cible : les étiquettes proviennent d'un moteur dont les décisions sont des seuils sur des valeurs discrètes, soit exactement la classe de fonctions qu'un arbre représente nativement.

Ce constat ne conduit pas à remplacer le modèle de l'application, mais il déplace la justification de ce choix : le réseau n'est pas retenu parce qu'il reproduit mieux les règles, mais parce qu'il produit en une passe les sorties de 189 médicaments avec des probabilités calibrées, et qu'il se prête à l'extension du jeu d'entrées.

**RQ3 — Les probabilités sont-elles calibrées, et un seuil de confiance signale-t-il les cas incertains ?**

La réponse est affirmative pour la calibration et nuancée pour le seuil. Après mise à l'échelle de la température, l'erreur de calibration attendue hors pli est de 0,0003. Cette valeur doit cependant être lue avec la réserve posée à la section 6.2 : elle est faible en partie parce que la quasi-totalité des lignes sont correctes et très confiantes, et elle ne démontre pas que les probabilités sont bien calibrées sur les lignes rares et difficiles.

La calibration n'est pas davantage un avantage propre au réseau : après le même traitement, XGBoost obtient une erreur de calibration et une log-loss meilleures ou équivalentes.

Quant au seuil, il remplit partiellement son office. La confiance sépare les lignes correctes des lignes erronées avec une aire sous la courbe ROC de 0,870, et les 1 % de lignes les moins confiantes concentrent 71,6 % des erreurs. Mais au seuil employé par l'application, la moitié des situations à éviter manquées restent acceptées : ce sont des erreurs commises avec une confiance élevée, que l'abstention ne peut pas détecter.

**RQ4 — La description moléculaire du médicament améliore-t-elle la prédiction, notamment pour un médicament jamais vu ?**

La réponse est négative. Un réseau recevant le profil et des descripteurs du médicament, évalué sur des médicaments laissés de côté, obtient une aire sous la courbe ROC de 0,774 pour distinguer les situations non standard, contre 0,817 pour une référence simple fondée sur la fréquence des classes par gène et phénotype. L'empreinte moléculaire dégrade les résultats. Ce résultat négatif est la raison pour laquelle cette architecture n'est pas intégrée à l'application.

Il appelle une interprétation : la référence à laquelle le réseau est comparé n'est pas naïve, une grande partie du signal provenant de la rareté du profil génétique lui-même. L'échec porte donc sur la capacité à transférer une connaissance d'un médicament à un autre, et non sur la prédiction en général.

**RQ5 — Les performances se conservent-elles hors des conditions d'entraînement ?**

La réponse diffère selon la nature de l'écart, et c'est un résultat en soi.

Pour des **profils non utilisés à l'entraînement** mais complets, la performance se conserve : sur 104 personnes lues depuis leur fichier VCF, le réseau diverge de la règle dans 6 lignes sur 6 172, soit 0,1 %.

Pour des **profils partiels**, elle se dégrade nettement : sur les onze patients publiés dont seuls quatre à sept gènes sur 31 sont renseignés, la divergence atteint 8,0 % des lignes. Le réseau est donc fragile hors de la distribution sur laquelle il a été entraîné, et c'est la règle affichée à côté de sa prédiction, ainsi que l'alerte « à vérifier », qui constituent la protection.

Pour des **médicaments absents de l'entraînement**, elle n'est pas démontrée (RQ4).

Pour des **combinaisons de valeurs jamais observées**, l'application ne prédit pas : elle déclare le cas hors domaine et n'affiche aucun avis.

**RQ6 — Les actions produites sont-elles concordantes avec l'interprétation attendue des références ?**

La réponse est affirmative, dans les termes rappelés à la section 9.1. La concordance avec PharmCAT atteint 97,8 % des lignes comparables, et les écarts ont été attribués à des causes identifiées : trois défauts de règles du corpus et des différences d'appel d'allèles chez quatre personnes. Sur les onze patients publiés, la règle de l'application est conforme à l'article dans les 36 lignes évaluables.

Cette concordance mesure une restitution fidèle de recommandations partagées, non une justesse clinique.

**RQ7 — Les règles qui servent d'étiquettes sont-elles cohérentes avec des données de patients réels ?**

La réponse est affirmative dans le sens, négative dans la précision, et elle révèle une omission.

Dans le sens : l'hypothèse principale est soutenue, les patients étiquetés comme devant recevoir une dose adaptée recevant effectivement une dose plus basse.

Dans la précision : l'étiquette ne détecte qu'environ 31 % des doses basses, et le génotype le plus fréquent de la classe intermédiaire n'est pas distinguable du génotype de référence dans la population complète.

Dans l'omission : la règle du corpus ignore VKORC1, qui explique dans ces données environ six fois plus de variance de la dose que CYP2C9 (R² de 0,294 contre 0,048). Il ne s'agit pas d'une limite de la source, puisque la DPWG publie une recommandation fondée sur VKORC1 pour la warfarine : c'est une omission du corpus, identifiée et déclarée.

### 9.3 La circularité entre les règles et le modèle

La limite la plus structurante de ce travail n'est aucune de celles qui précèdent prise isolément, mais leur cause commune. Le réseau est entraîné sur des étiquettes produites par un moteur de règles ; ce moteur applique les recommandations de CPIC et de la DPWG ; PharmCAT applique les mêmes recommandations. Mesurer l'accord entre ces systèmes ne peut donc pas établir leur justesse : il établit qu'ils lisent les mêmes textes de la même façon.

Trois dispositifs sortent de ce cercle, et ils sont les seuls.

La **comparaison des génotypes à GeT-RM** (section 8.2) est indépendante, puisque cette référence est établie par un programme externe sans rapport avec la chaîne évaluée. Elle révèle d'ailleurs que la concordance est élevée pour certains gènes et faible pour d'autres.

La **confrontation de la règle de la warfarine aux patients de l'IWPC** (chapitre 7) est indépendante, puisque les doses observées ne proviennent d'aucune recommandation. C'est la seule validation de ce type du mémoire, et elle ne porte que sur une molécule.

La **comparaison du sens des avis à huit études cliniques** (section 6.6) est partiellement indépendante : les études sont antérieures et distinctes des recommandations, mais la comparaison porte sur la direction de l'effet et non sur son ampleur, et elle a été menée avec des profils construits et des modèles d'une version antérieure du corpus [à compléter].

Il en découle que la portée de ce travail est celle d'une démonstration de faisabilité : il établit qu'un modèle peut reproduire fidèlement un corpus de recommandations à partir d'un profil multi-gènes, et que la chaîne complète fonctionne depuis un fichier VCF. Il n'établit pas que les avis produits améliorent la prise en charge, et ne pouvait pas l'établir avec les données employées.

### 9.4 Limites

Les limites propres à chaque étape sont énoncées aux sections 3.8, 4.10, 5.10, 6.8, 7.7 et 8.8. Les six suivantes sont celles qui affectent l'interprétation d'ensemble.

1. **Les étiquettes sont des règles, non des observations cliniques.** Toutes les mesures des chapitres 6 et 8 expriment une fidélité à des recommandations. La validité clinique de ces recommandations repose sur les études primaires qui les fondent, et n'est pas établie par ce travail.

2. **La validation est partiellement circulaire** (section 9.3). Les trois dispositifs qui y échappent portent respectivement sur les génotypes, sur une molécule, et sur la direction de l'effet pour huit couples.

3. **Quatre défauts de règles ont été identifiés et ne sont pas tous corrigés** dans la version évaluée : les thiopurines traitées par un seul gène alors que la recommandation en combine deux, CYP2C9 lu par score d'activité là où la DPWG raisonne par diplotype, SLCO1B1 ignoré pour la fluvastatine, et VKORC1 absent de la règle de la warfarine. Les trois premiers ont été mis en évidence par la comparaison à PharmCAT, le quatrième par la confrontation aux patients réels. Leur existence montre que la validation externe remplit son office ; leur persistance dans la version évaluée est une limite.

4. **L'appel d'allèles est incertain pour plusieurs gènes.** La concordance avec GeT-RM est élevée pour CYP2C9 et CYP3A5, et faible pour CYP2B6, SLCO1B1, UGT1A1 et DPYD. Une erreur à cette étape se propage inchangée à l'avis produit. Les causes n'ont pas été attribuées cas par cas [à compléter], et un désaccord ne prouve pas une erreur de l'outil, la nomenclature des allèles évoluant.

5. **Le réseau est fragile sur les profils partiels** (RQ5) : la divergence passe de 0,1 % à 8,0 % lorsque seuls quatre à sept gènes sur 31 sont renseignés. C'est la situation la plus probable en pratique clinique réelle, où un panel ne couvre pas tous les gènes.

6. **La constitution du corpus n'est pas entièrement justifiée.** La règle ayant retenu 1 379 échantillons parmi les 3 202 disponibles n'a pas été retrouvée, et la liste n'est pas un tirage aléatoire. Le corpus n'est donc pas un échantillon documenté de la population d'origine, les fréquences alléliques observées ne doivent pas être lues comme des fréquences de population, et l'effet du nombre de profils sur les performances n'a pas été mesuré. Par ailleurs, le regroupement des lignes se fait par identifiant de profil et non par parenté : 374 des 1 379 profils ont un apparenté dans le corpus. Une analyse de sensibilité montre que l'effet sur le F1 macro est inférieur au seuil fixé d'avance, mais la parenté réelle n'est pas contrôlée au-delà du pedigree déclaré.

### 9.5 Perspectives

Les perspectives suivantes découlent directement des limites ci-dessus, et sont classées par ce qu'elles coûtent.

**Corrections de règles identifiées.** Les quatre défauts du point 3 ont chacun une correction connue : coder la grille à deux gènes pour les thiopurines, porter le diplotype de CYP2C9 plutôt que son seul score d'activité, ajouter SLCO1B1 à la règle de la fluvastatine, et reprendre la recommandation DPWG fondée sur VKORC1 pour la warfarine. Leur mise en œuvre impose de reconstruire le corpus et de réentraîner les modèles sous le protocole inchangé.

**Mesure de l'effet du nombre de profils.** Une courbe d'apprentissage selon le nombre de profils d'entraînement dirait si les 1 379 profils constituent un plateau ou une contrainte, et transformerait une limite déclarée en résultat mesuré.

**Robustesse aux profils partiels.** La dégradation constatée au point 5 suggère un entraînement incluant des profils volontairement incomplets, de sorte que le réseau apprenne à traiter l'absence d'un gène comme une information et non comme une anomalie.

**Validation clinique.** La confrontation à des patients réels n'a été possible que pour la warfarine, faute de jeux de données publics comparables pour les autres molécules. Toute extension de cette validation est subordonnée à la disponibilité de telles données.

**Intégration au flux de soins.** La littérature d'implémentation établit que les obstacles décisifs au déploiement d'une aide à la décision pharmacogénomique sont l'intégration au dossier patient informatisé, la pérennité des interprétations et la portabilité des résultats (section 2.3). Aucun n'est traité ici, et chacun relève d'un travail d'une autre nature que celui mené dans ce mémoire.

### 9.6 Conclusion

Ce travail a conçu, entraîné, évalué et déployé un système expérimental d'aide à la décision pharmacogénomique fondé sur l'apprentissage profond. À partir du fichier VCF d'un patient, le système construit un profil multi-gènes, qu'un réseau de neurones lit en une seule passe pour produire, pour 189 médicaments, une action parmi quatre, assortie d'une probabilité calibrée et de la recommandation officielle correspondante.

Les résultats établissent que cette tâche est apprenable avec une fidélité élevée, que la chaîne complète restitue les recommandations de référence depuis un fichier de variants, et que la seule règle confrontée à des patients réels va dans le bon sens. Ils établissent aussi, et le mémoire les rapporte sans les atténuer, que XGBoost reproduit ces règles mieux que le réseau sous protocole identique, que la description moléculaire du médicament ne permet pas de généraliser à un médicament jamais vu, et que le réseau se dégrade sensiblement sur des profils partiels.

La contribution de ce travail ne réside donc pas dans la supériorité d'une famille de modèles, mais dans la construction d'un corpus pharmacogénomique tracé et auditable, dans l'évaluation honnête d'une architecture lisant le profil entier, et dans une chaîne complète et reproductible allant du fichier de variants à une recommandation sourcée. Les résultats négatifs y ont été conservés et analysés, car ils délimitent ce que l'approche permet.

Le système demeure un prototype de recherche. Il n'est pas un dispositif médical, n'a fait l'objet d'aucune validation clinique, et ne remplace ni les recommandations publiées ni le jugement du prescripteur. Lorsqu'une recommandation explicite existe, elle reste la référence.
