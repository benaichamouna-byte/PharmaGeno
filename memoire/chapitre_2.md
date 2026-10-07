# CHAPITRE 2 — ÉTAT DE L'ART ET VERROUS SCIENTIFIQUES

---

## 2.1 Fondements de la pharmacogénomique clinique

### 2.1.1 Du génotype à l'action thérapeutique

La pharmacogénomique repose sur une chaîne causale à trois niveaux. Le **génotype** est la séquence observée chez l'individu, lue dans ce travail à partir d'un fichier VCF. Le **phénotype métabolique** est la capacité fonctionnelle qui en découle : métaboliseur lent, intermédiaire, normal, rapide ou ultrarapide. L'**action clinique** est la conduite à tenir qui en résulte pour un médicament donné.

Cette chaîne concerne principalement les gènes de l'ADME — absorption, distribution, métabolisme, excrétion — dont les produits déterminent la concentration du principe actif à son site d'action, et plus marginalement les cibles pharmacologiques elles-mêmes.

Deux mécanismes opposés découlent d'un déficit enzymatique, et cette asymétrie interdit toute règle uniforme. Pour un médicament administré sous sa forme active, un métaboliseur lent accumule le principe actif et s'expose à la toxicité. Pour un promédicament, qui doit être converti en métabolite actif, le même métaboliseur lent n'obtient aucun effet thérapeutique. Le clopidogrel, promédicament activé par CYP2C19, et la codéine, convertie en morphine par CYP2D6, illustrent ce point : un déficit enzymatique ne signifie pas « surdosage » dans l'absolu. L'action dépend conjointement du gène et de la molécule, ce qui justifie que les deux soient fournis ensemble au modèle développé dans ce travail.

### 2.1.2 Les cytochromes P450 et les autres familles

Les cytochromes P450 constituent la superfamille enzymatique dominante du métabolisme des xénobiotiques. Les isoformes CYP2D6, CYP2C19, CYP2C9, CYP3A4, CYP3A5, CYP2B6, CYP1A2 et CYP2A6 concentrent l'essentiel de la variabilité pharmacogénomique documentée.

D'autres familles interviennent : les transporteurs membranaires comme SLCO1B1 et ABCG2, qui conditionnent l'entrée hépatique des statines ; les enzymes de phase II comme TPMT, NUDT15 et UGT1A1 ; les cibles pharmacologiques comme VKORC1 pour les antivitamines K ; et les allèles HLA, associés à des réactions d'hypersensibilité sévères.

CYP2D6 mérite une mention particulière, car il concentre les difficultés techniques du domaine. Le locus présente non seulement des variants ponctuels, mais des délétions complètes, des duplications et des gènes hybrides avec le pseudogène voisin CYP2D7. Le nombre de copies module directement l'activité : une duplication d'allèle fonctionnel produit un métaboliseur ultrarapide. Cette variation structurale est la raison pour laquelle un fichier VCF de SNP et d'indels ne suffit pas à déterminer le phénotype CYP2D6 — point sur lequel repose une partie de la méthodologie du chapitre 3.

### 2.1.3 Allèles étoile, diplotypes et scores d'activité

La traduction du génotype en phénotype passe par un objet intermédiaire, le **diplotype** : la paire d'haplotypes portée par l'individu, notée par exemple `*1/*4`. La nomenclature en allèles étoile standardise la désignation de ces haplotypes fonctionnels, et le Pharmacogene Variation Consortium (PharmVar) en est le dépositaire : il définit, pour chaque gène, la composition en variants de chaque allèle et sa fonction attribuée.

Chaque allèle reçoit une fonction — normale, diminuée, nulle, augmentée — puis un score numérique. La somme des scores des deux allèles donne le **score d'activité**, converti en catégorie phénotypique par des seuils définis par consensus d'experts.

Ce score d'activité est un choix de représentation déterminant pour ce travail : il fournit une échelle numérique ordonnée, directement exploitable comme entrée d'un réseau de neurones, là où un diplotype est une étiquette catégorielle. Il présente toutefois une limite, examinée au chapitre 3 : tous les gènes du panel ne disposent pas d'un score d'activité au sens strict, et les échelles employées ne sont pas commensurables entre elles.

Toute chaîne allant du VCF au phénotype dépend des tables de définition d'allèles, et leur mise à jour peut modifier rétroactivement une interprétation. Un travail de 2025 a d'ailleurs montré que l'évolution des définitions d'allèles étoile modifie les appels de diplotypes, les prédictions de phénotype et, par conséquent, les recommandations thérapeutiques pour les statines. C'est un point de reproductibilité repris au chapitre 8.

---

## 2.2 Ressources de connaissances pharmacogénomiques

### 2.2.1 PharmGKB et ClinPGx — les niveaux de preuve

PharmGKB, désormais intégré à la plateforme ClinPGx, agrège et annote la littérature pharmacogénomique. Ses *clinical annotations* associent un variant à un médicament et reçoivent un niveau de preuve de 1A à 4, attribué par un système de score.

Le niveau 1A désigne une association variant–médicament figurant dans une ligne directrice CPIC ou d'une société savante, ou implémentée dans un système de santé majeur. Le niveau 1B correspond à une association que la prépondérance des preuves annotées soutient. Le niveau 2A exige une réplication de l'association et porte sur des variants de gènes prioritaires.

Seuls les niveaux 1A et 2A ont été retenus pour ce travail : ce sont ceux dont l'association est suffisamment établie pour porter une recommandation d'action, et non une simple observation statistique.

### 2.2.2 CPIC — des recommandations actionnables

Le Clinical Pharmacogenetics Implementation Consortium traduit les associations établies en conduites à tenir. Ses lignes directrices sont gratuites, révisées par les pairs, et structurées de façon exploitable par machine : tables d'assignation allèle–fonction, table diplotype–phénotype, table phénotype–recommandation. Une synthèse publiée en 2025 rapporte une couverture de 34 gènes et 164 médicaments.

CPIC assigne à chaque paire gène–médicament un niveau, de A à D. Le niveau A signifie qu'une action de prescription est recommandée. Cette distinction s'est révélée centrale dans ce travail : le chapitre 5 montre qu'assigner des actions à des paires hors niveau A dégrade mesurablement les performances du modèle, et c'est ce critère qui a servi de filtre au jeu de données final.

Un point mérite d'être souligné dès maintenant. CPIC couvre 164 médicaments ; le corpus construit pour ce travail en contient 530. Pour les 366 molécules restantes, aucune recommandation n'existe. Ce décalage définit l'un des espaces dans lesquels un modèle appris peut apporter quelque chose qu'une table ne peut fournir.

### 2.2.3 DPWG et autres consortiums

Le Dutch Pharmacogenetics Working Group, le Canadian Pharmacogenomics Network for Drug Safety et le Réseau national de pharmacogénétique français publient des recommandations selon des méthodologies propres. Leurs conclusions recoupent largement celles de CPIC mais divergent sur certaines paires.

Le corpus d'annotations rassemblé pour ce travail comprend 217 fichiers de guidelines issus de dix organismes — CPIC, DPWG, RNPGx, CPNDS et six autres — représentant 386 associations gène–médicament sur 41 gènes et 208 médicaments. Cette hétérogénéité de sources est la cause directe des conflits d'étiquetage audités au chapitre 3, et la règle de résolution adoptée y est explicitée.

### 2.2.4 ClinVar et annotations réglementaires

ClinVar fournit l'interprétation de signification clinique des variants, avec un statut de revue. La Food and Drug Administration publie une table des associations pharmacogénétiques et fait figurer certaines informations dans les notices de médicaments. Ces deux sources apportent une couverture complémentaire, notamment sur des variants absents des lignes directrices des consortiums.

### 2.2.5 Le 1000 Genomes Project — des profils génétiques réels

La distinction entre profils réels et profils synthétiques est décisive. Un modèle entraîné sur des combinaisons de gènes générées aléatoirement apprendrait des profils que la génétique des populations ne produit jamais. Les données du 1000 Genomes Project fournissent des co-occurrences authentiques, avec leurs déséquilibres de liaison et leurs structures de population.

Le travail de référence utilisé ici a appliqué PyPGx aux données de séquençage complet à haute couverture de 2 504 individus non apparentés, répartis sur 26 populations, pour caractériser les allèles étoile de 58 gènes pharmacogénomiques. Les données proviennent d'un séquençage à couverture moyenne de 30×, et le code comme les données sont publics. Ces diplotypes précalculés constituent la source des profils multi-gènes du jeu de données, complétés par une extraction directe de variants décrite au chapitre 3.

---

## 2.3 Pipelines déterministes d'interprétation

### 2.3.1 PharmCAT

PharmCAT est l'outil de référence pour l'interprétation pharmacogénomique à partir d'un VCF. Il extrait les variants d'intérêt, en infère haplotypes et diplotypes, et produit un rapport reprenant les recommandations des lignes directrices publiées.

Ses limites sont documentées par ses propres auteurs. CYP2D6, HLA-A et HLA-B ne sont pas appelables par l'outil dans les usages standards et doivent être fournis par un appel externe, parce que la variation structurale et le nombre de copies dépassent ce qu'un VCF de SNP et d'indels permet de déterminer.

Au-delà de cette limite de couverture, PharmCAT est par conception un outil d'annotation : il restitue ce que les lignes directrices énoncent, paire par paire, sans produire de décision agrégée ni traiter les molécules non couvertes.

### 2.3.2 Appeleurs d'allèles — PyPGx, Stargazer, Aldy, deCYPher

Ces outils résolvent un problème distinct : déterminer le diplotype à partir de données de séquençage brutes, y compris en présence de variation structurale.

Stargazer a introduit l'usage de la profondeur de lecture pour calculer le nombre de copies spécifique de paralogue. PyPGx poursuit cette approche et expose les profils de nombre de copies et de fraction allélique pour permettre l'inspection manuelle de la qualité des appels de variants structuraux ; il produit également des phénotypes prédits pour les 16 gènes disposant d'une table génotype–phénotype CPIC. Aldy emploie l'optimisation combinatoire pour l'appel d'allèles étoile à travers différentes technologies de séquençage. Plus récemment, deCYPher exploite des assemblages résolus par haplotype issus de lectures longues pour obtenir des assignations non ambiguës, en particulier sur des loci complexes comme CYP2D6.

Ces outils s'arrêtent au diplotype, éventuellement au phénotype. Ils ne produisent ni décision agrégée sur un panel entier, ni recommandation pour une molécule donnée. Ce sont des fournisseurs d'entrée pour la chaîne décrite dans ce mémoire, non des concurrents.

### 2.3.3 Systèmes de restitution — PAnno

PAnno se présente comme une solution de bout en bout pour l'aide à la décision pharmacogénomique clinique, résolvant, annotant et rapportant les variants germinaux. Comme PharmCAT, il produit un rapport fondé sur des règles. Le passage de la connaissance à la décision y reste déterministe.

### 2.3.4 La limite commune de ces approches

Le recensement précédent fait apparaître une architecture à trois couches dont la troisième est inoccupée.

La **couche de preuve** — PharmGKB, CPIC, DPWG — produit de la connaissance sous forme de règles indexées par paire gène–médicament. La **couche d'interprétation** — PharmCAT, PyPGx, Aldy, deCYPher, PAnno — exécute une lecture du génome et restitue ces règles.

La **couche de décision** n'est pas occupée par un système appris. Trois propriétés y font défaut.

*La composition des gènes.* Une table indexée par paire renvoie autant de lignes que de gènes concernés, sans les agréger. Or un individu porte en moyenne 3,6 génotypes actionnables, et le chapitre 5 montre que pour 186 des 530 médicaments du corpus — soit 35 % — aucun gène unique ne détermine l'action à lui seul.

*L'extrapolation hors table.* Les 164 médicaments couverts par CPIC ne couvrent pas la pharmacopée. Une table ne peut rien dire d'une molécule absente ; une représentation structurale le peut, par similarité.

*L'interrogation directe.* Un rapport statique impose au clinicien de chercher ; un système de décision répond à une question posée.

---

## 2.4 Apprentissage automatique en pharmacogénomique clinique

### 2.4.1 Les travaux existants

L'application de l'apprentissage automatique à la pharmacogénomique clinique germinale reste limitée en nombre, et presque entièrement cantonnée aux méthodes classiques.

Le travail le plus directement comparable à ce mémoire est un prototype d'aide à la décision pharmacogénomique publié en 2022. Les auteurs ont comparé cinq méthodes — Random Forest, machine à vecteurs de support, XGBoost, k plus proches voisins et arbre de décision — pour détecter des événements indésirables potentiels à partir de dossiers patients enrichis de données génétiques. Plus de 98 % de la cohorte avait reçu au cours de sa vie au moins un médicament couvert par une ligne directrice CPIC de niveau A. **XGBoost s'est révélé le plus performant**, et l'ajout des données génétiques a amélioré la prédiction.

Ce résultat est important à deux titres pour le présent travail. Il confirme que les données pharmacogénomiques structurées se prêtent bien aux méthodes d'ensemble. Et il fournit un précédent auquel comparer les résultats du chapitre 5, où XGBoost dépasse également le réseau profond.

D'autres travaux emploient l'apprentissage pour des sous-problèmes. Des prédicteurs computationnels de l'effet des variants ont été évalués pour l'assignation fonctionnelle des allèles étoile, avec l'objectif d'étendre l'interprétation à des variants non répertoriés. PyPGx lui-même recourt à un classificateur à vecteurs de support pour détecter les variations structurales à partir des profils de nombre de copies. Ces usages restent toutefois en amont de la décision thérapeutique : ils servent à mieux appeler un génotype, non à prédire une action.

### 2.4.2 Une direction émergente — les modèles de langage

Un travail de 2025 explore l'usage de grands modèles de langage affinés, couplés à une génération augmentée par récupération, pour produire des recommandations pharmacogénomiques ancrées sur les guidelines CPIC et ClinPGx. L'approche combine le contenu narratif des recommandations et des enregistrements structurés gène–médicament–phénotype.

Les performances rapportées restent faibles — une exactitude de 0,35, avec une précision de 0,39 et un rappel de 0,44. Ce travail illustre néanmoins une direction active du domaine, et le chapitre 8 y revient en perspectives.

### 2.4.3 Le constat

Les approches d'apprentissage appliquées à la pharmacogénomique clinique germinale emploient donc presque exclusivement des méthodes classiques, et portent sur des formulations distinctes de celle retenue ici : prédiction d'événements indésirables à partir de dossiers, assignation fonctionnelle de variants, ou génération de texte ancré sur les guidelines.

---

## 2.5 Deep Learning et prédiction de réponse médicamenteuse

### 2.5.1 Un champ dominé par l'oncologie de précision

La littérature du Deep Learning consacrée à la prédiction de réponse médicamenteuse est aujourd'hui dominée par l'oncologie de précision. Une revue systématique publiée en 2023 dans *Frontiers in Medicine* a recensé l'ensemble des travaux employant des réseaux de neurones pour cette tâche et en couvre plusieurs dizaines.

La formulation y est constante : le modèle reçoit une représentation du *cancer* — profil transcriptomique, mutations somatiques, méthylation — et une représentation du *médicament*, puis prédit une mesure de sensibilité telle que l'IC50 ou l'aire sous la courbe. Les données proviennent majoritairement de lignées cellulaires, issues de ressources comme GDSC ou le Cancer Cell Line Encyclopedia.

Plusieurs architectures jalonnent ce champ. MOLI emploie une intégration tardive multi-omique par réseaux profonds. DeepCDR combine réseau de graphes et convolution pour la réponse aux médicaments anticancéreux. SWnet associe signatures génomiques et structures chimiques. HiDRA introduit une hiérarchie avec attention. XGDP exploite des réseaux de graphes explicables pour révéler le mécanisme d'action. MOViDA utilise une architecture biologiquement informée pour améliorer l'interprétabilité.

### 2.5.2 Pourquoi cette littérature ne transpose pas directement

Trois différences séparent ces travaux de la formulation retenue ici.

**La nature du patient.** Dans ces modèles, l'entité biologique est une lignée cellulaire ou une tumeur, caractérisée par son transcriptome. Ici, c'est un individu caractérisé par son génotype germinal. Une revue de 2023 note d'ailleurs que le transfert des modèles entraînés sur lignées cellulaires vers des patients réels demeure nettement plus difficile.

**La nature de la sortie.** Ces modèles prédisent une grandeur continue de sensibilité pharmacologique. Ici, la sortie est une catégorie d'action de prescription, directement interprétable par un clinicien.

**La nature du génome considéré.** Les variants somatiques caractérisés dans le tissu tumoral sont par construction absents d'un VCF germinal. Les deux problèmes portent sur des objets biologiques différents.

### 2.5.3 Un précédent architectural utile

Ces travaux conservent néanmoins un intérêt direct pour ce mémoire : ils fournissent un **précédent architectural** pour la fusion de deux représentations hétérogènes. La structure à deux branches — une pour l'entité biologique, une pour la molécule, suivies d'une fusion — y est largement employée, et l'architecture retenue au chapitre 4 s'en inspire.

Une observation récurrente de ce champ mérite par ailleurs d'être retenue. Les travaux recensés rapportent de façon constante une **chute des performances sur les composés jamais vus par le modèle**. Cette observation motive directement l'expérience de généralisation moléculaire menée au chapitre 5.

---

## 2.6 Représentations informatiques des médicaments

### 2.6.1 Des descripteurs aux empreintes circulaires

Représenter une molécule pour un modèle d'apprentissage suppose de choisir ce que l'on encode.

Les **descripteurs physico-chimiques** — masse moléculaire, coefficient de partage, donneurs et accepteurs de liaisons hydrogène, liaisons rotatives, surface polaire topologique — résument des propriétés globales. Ils sont peu nombreux, interprétables, mais ne distinguent pas deux molécules de propriétés voisines et de structures différentes.

Les **empreintes moléculaires** encodent la présence de sous-structures. Plusieurs familles coexistent : MACCS et PubChem reposent sur des clés structurales prédéfinies, l'empreinte ErG sur des motifs pharmacophoriques, et les empreintes à connectivité étendue — ECFP, communément appelées empreintes de Morgan — sur l'expansion itérative du voisinage atomique.

Cette dernière famille présente une propriété importante : elle décrit des sous-structures sans liste prédéfinie, et peut donc caractériser des groupes fonctionnels non anticipés. Sa limite tient au hachage, qui peut provoquer des collisions de bits et une perte d'information.

### 2.6.2 Les représentations apprises

Les réseaux de neurones sur graphes apprennent une représentation adaptée à la tâche plutôt que de l'encoder a priori. Les modèles de passage de messages, les transformeurs moléculaires et les embeddings pré-entraînés sur de grands corpus chimiques relèvent de cette approche.

### 2.6.3 Ce que montre la littérature comparative

Un ensemble de travaux récents conduit à nuancer la supériorité supposée des représentations apprises.

Une évaluation portant sur 25 modèles d'embeddings moléculaires pré-entraînés et 25 jeux de données conclut que les empreintes ECFP comptées restent hautement compétitives, et que la plupart des modèles neuronaux sophistiqués — réseaux de graphes et architectures transformeur de grande taille — ne montrent pas d'amélioration statistique consistante sur la prédiction de propriétés moléculaires.

Un travail de 2025 sur la prédiction d'interactions médicamenteuses compare explicitement les empreintes de Morgan ECFP4, des représentations issues de réseaux convolutionnels sur graphes pré-entraînés, et des embeddings de type transformeur, en ne modifiant que la représentation. Les auteurs rapportent qu'un modèle léger alimenté par des empreintes de Morgan atteint des performances comparables ou supérieures à des systèmes bien plus complexes, tout en employant plusieurs ordres de grandeur de paramètres en moins.

Une analyse théorique éclaire ce résultat : l'empreinte ECFP de rayon 2 équivaut approximativement à un réseau de passage de messages à deux couches, dont elle reproduit le mécanisme d'agrégation du voisinage.

### 2.6.4 Le choix retenu

Ces éléments justifient le choix opéré dans ce travail : une empreinte de Morgan de 512 bits, de rayon 2, complétée par six descripteurs physico-chimiques. Ce choix n'est pas un compromis par défaut mais une option documentée par la littérature comparative, adaptée à un corpus de taille modérée où les représentations apprises n'apportent pas de gain établi.

---

## 2.7 Modèles multimodaux patient–médicament

La formulation retenue dans ce mémoire relève d'une classe d'architectures où deux représentations de nature différente sont traitées séparément puis fusionnées avant la décision.

Dans les modèles de réponse anticancéreuse, la première branche encode l'entité biologique et la seconde la molécule. MOLI emploie une intégration tardive de trois modalités omiques. DeepCDR traite le médicament par un réseau de graphes et le profil génomique par des couches denses. SWnet associe signature génomique et structure chimique. HiDRA introduit une hiérarchie accompagnée d'un mécanisme d'attention.

Ces travaux établissent trois points méthodologiques utiles ici.

**La fusion tardive est préférable à la concaténation précoce** lorsque les deux modalités diffèrent fortement en dimension et en nature. Un vecteur de 31 phénotypes et un vecteur de 518 variables moléculaires ne peuvent être traités par les mêmes couches sans que la modalité la plus large ne domine.

**Les mécanismes d'attention améliorent l'interprétabilité** autant que la représentation. HiDRA en fait un usage explicite, et des approches d'attribution comme GNNExplainer ou les gradients intégrés sont employées pour interpréter les interactions entre caractéristiques moléculaires et gènes.

**La généralisation à des molécules non vues constitue un point faible documenté** de ces architectures, et doit être évaluée par un protocole dédié plutôt que supposée.

---

## 2.8 Explicabilité et sécurité décisionnelle

### 2.8.1 L'exigence d'explicabilité en contexte clinique

Un système d'aide à la décision médicale ne peut se limiter à produire une sortie. Le prescripteur doit pouvoir comprendre sur quoi repose la recommandation pour décider s'il la suit.

Deux familles de méthodes sont employées dans ce travail. **SHAP** attribue à chaque variable d'entrée une contribution à la prédiction, et s'applique naturellement aux modèles à base d'arbres. Les **poids d'attention** d'un réseau neuronal indiquent quelles variables le modèle a modulées avant traitement, et fournissent un signal d'interprétabilité propre à l'architecture.

### 2.8.2 La fidélité de l'explication

La littérature récente insiste sur un point : produire une explication ne suffit pas. Sa fidélité, son utilité et sa pertinence doivent elles-mêmes être évaluées. Une explication plausible mais déconnectée du raisonnement réel du modèle est trompeuse plutôt qu'utile.

Ce constat oriente la méthode retenue au chapitre 6. Plutôt que de présenter des figures d'attribution comme résultat en soi, ce travail mesure la **concordance entre l'attribution du modèle et l'attribution pharmacogénomique attendue**. Pour chaque médicament, CPIC désigne un ou deux gènes responsables. On vérifie si ces gènes figurent parmi ceux que le modèle juge déterminants, et l'on calcule un taux de concordance.

Cette mesure n'est pas circulaire : l'attribution du gène responsable ne figure pas dans l'étiquette apprise. Le modèle prédit une action, non un gène. Qu'il retrouve néanmoins le bon axe biologique constitue un résultat distinct de sa performance de classification.

### 2.8.3 Les limites de l'attention comme explication

Les poids d'attention ne constituent pas une preuve de causalité biologique. Ils indiquent ce que le modèle a pondéré, non ce qui détermine la réponse pharmacologique chez le patient. Cette distinction est maintenue dans l'interprétation des résultats du chapitre 6.

---

## 2.9 Verrou scientifique et positionnement de PharmaGeno

### 2.9.1 Deux littératures et un espace entre elles

Le recensement conduit dans ce chapitre fait apparaître deux ensembles de travaux distincts.

Le premier regroupe les **systèmes pharmacogénomiques cliniques déterministes**. Ils partent d'un génotype, en dérivent un diplotype puis un phénotype, et appliquent une règle issue d'une ligne directrice. PharmCAT, PyPGx, Aldy, Stargazer, deCYPher et PAnno relèvent de cette catégorie. Leur fiabilité tient précisément à leur caractère déterministe, et leur limite à la couverture des règles disponibles.

Le second regroupe les **modèles de Deep Learning de réponse médicamenteuse**, développés principalement en oncologie de précision. Ils apprennent à partir de données tumorales ou de lignées cellulaires, avec des représentations transcriptomiques ou multi-omiques, et prédisent une mesure de sensibilité pharmacologique.

Entre les deux se situe une formulation peu explorée :

> à partir d'un **profil pharmacogénomique germinal multi-gènes** et d'une **représentation structurale du médicament**, prédire directement une **catégorie d'action de prescription** au moyen d'un modèle appris.

### 2.9.2 Formulation du verrou

À notre connaissance, et sur la base de la littérature examinée, nous n'avons pas identifié de travail combinant explicitement ces trois éléments. Les travaux d'apprentissage en pharmacogénomique clinique germinale emploient des méthodes classiques et portent sur des formulations distinctes — prédiction d'événements indésirables à partir de dossiers, assignation fonctionnelle de variants, ou génération de recommandations textuelles.

Cette formulation soulève par ailleurs une difficulté méthodologique propre, assumée dès le chapitre 1. Les étiquettes d'entraînement étant dérivées des recommandations existantes, la cible est, sur les paires couvertes, une fonction largement déterministe des entrées. Les métriques de classification mesurent donc d'abord une fidélité d'implémentation.

Ce qu'un modèle appris peut apporter au-delà se situe dans trois directions, qui structurent les expériences du chapitre 5.

**La composition multi-gènes.** Une table indexée par paire ne compose pas plusieurs déterminants en une décision. L'analyse du corpus établit que pour 186 des 530 médicaments, aucun gène unique ne détermine l'action à lui seul.

**L'extrapolation moléculaire.** Les 164 médicaments couverts par CPIC représentent moins du tiers du corpus. Une représentation structurale ouvre la possibilité d'une réponse pour des molécules absentes des recommandations — hypothèse à évaluer par un protocole où certains médicaments sont entièrement exclus de l'entraînement.

**La résolution de cas ambigus.** L'audit des conflits mené au chapitre 3 identifie des paires gène–médicament portant plusieurs actions légitimes selon le phénotype précis — CYP2D6 et tamoxifène, CYP2C19 et voriconazole, où métaboliseur ultrarapide et métaboliseur lent appellent des conduites opposées. Une correspondance gène vers action est donc insuffisante par construction.

### 2.9.3 Positionnement

PharmaGeno ne vise pas à remplacer CPIC, DPWG, PharmGKB ou PharmCAT. Ces ressources organisent la connaissance pharmacogénomique et demeurent la référence clinique lorsqu'une recommandation explicite existe.

Le travail présenté ici occupe la couche de décision : il étudie dans quelle mesure un modèle appris peut intégrer simultanément le profil pharmacogénomique complet d'un patient et la structure chimique d'un médicament pour produire une action individualisée, et évalue rigoureusement ce que cette approche apporte par rapport aux méthodes classiques et aux représentations limitées à un seul gène.

La question de la justification même du Deep Learning sur ces données fait partie du travail. Les données employées sont structurées et de volume modéré ; le précédent de 2022, où XGBoost dépasse les autres méthodes sur des données pharmacogénomiques, invite à ne pas présumer de la supériorité d'une architecture profonde. Random Forest et XGBoost sont donc évalués sous un protocole identique, et le chapitre 7 discute ce que les résultats établissent à ce sujet.
