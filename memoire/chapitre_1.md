# CHAPITRE 1 — INTRODUCTION GÉNÉRALE

## 1.1 PharmaGeno — ce que le système fait

PharmaGeno est une application web de prédiction fondée sur le Deep Learning. Le clinicien y dépose le fichier VCF de son patient, et l'application prédit, médicament par médicament, la conduite à tenir parmi quatre : contre-indiqué, ajuster la dose, utiliser avec précaution, prescrivable normalement. Il peut également interroger une molécule précise et obtenir la prédiction établie pour ce patient.

Cette prédiction n'est pas lue dans une table de correspondance. Elle est produite par un modèle de Deep Learning à deux branches, qui reçoit simultanément le profil génétique complet du patient sur 31 gènes et la structure chimique du médicament interrogé, et apprend une représentation conjointe des deux pour prédire l'action.

[FIGURE 1.1 — Chaîne de prédiction de PharmaGeno : VCF patient vers parseur VCF vers profil 31 genes ; medicament vers structure PubChem vers empreinte de Morgan 518 bits ; les deux entrent dans le modele de Deep Learning a deux branches avec attention sur les genes, qui produit l'action predite parmi quatre.]

Ce modèle de Deep Learning et cette application de prédiction sont les deux objets de ce mémoire. Le jeu de données, le protocole d'évaluation et l'état de l'art existent pour les construire, les justifier et les valider.

---

## 1.2 Pourquoi le Deep Learning

Le recours au Deep Learning ne relève pas d'un effet d'affichage. Il répond à trois propriétés qu'une table de correspondance gène–médicament ne possède pas, et que l'architecture profonde retenue possède par construction.

### Composer les gènes plutôt que les juxtaposer

Une table de recommandations est indexée par paire. Interrogée sur un patient portant des variants dans quatre gènes pour une molécule substrat de trois d'entre eux, elle renvoie trois lignes indépendantes et laisse le clinicien les composer lui-même.

La branche génétique du modèle de Deep Learning reçoit les 31 valeurs de phénotype en un seul vecteur. Elle apprend une représentation du profil dans son ensemble, et non une suite de lectures isolées. Les combinaisons de gènes ne sont pas énumérées à la main : elles émergent de l'apprentissage, et c'est à partir de cette représentation globale que le modèle prédit l'action.

L'analyse du corpus, détaillée au chapitre 5, établit que pour 186 des 530 médicaments — soit 35 % — aucun gène unique ne détermine l'action à lui seul. C'est le point de départ empirique de ce travail : la formulation par paires est structurellement insuffisante pour un tiers des molécules du corpus.

### Interpoler dans l'espace chimique

La branche moléculaire ne reçoit pas le nom du médicament mais son empreinte de Morgan, un vecteur binaire calculé sur sa structure chimique. Deux molécules partageant des sous-structures occupent des positions voisines dans cet espace.

Cette propriété ouvre une capacité qu'aucune table ne possède : prédire une action pour une molécule absente des lignes directrices. Un modèle indexé sur l'identifiant du médicament en serait strictement incapable — il n'aurait aucune entrée à consulter. Un modèle structural dispose, lui, de l'information portée par la parenté chimique.

### Pondérer les gènes selon la molécule

Un mécanisme d'attention apprend, pour chaque prédiction, quels gènes pèsent le plus. Il remplit deux fonctions distinctes. Il enrichit la représentation en modulant le vecteur génétique avant son traitement. Et il fournit au clinicien une justification lisible — quel gène a porté cette prédiction — condition pratique de l'acceptabilité de l'outil au lit du patient.

### L'architecture Deep Learning retenue

[FIGURE 1.2 — Architecture du modele de Deep Learning. Branche genetique : profil 31 genes vers GeneAttention(31) definie par x multiplie par softmax(Wx), puis Linear 31 vers 64 avec BatchNorm ReLU Dropout 0.3, puis Linear 64 vers 32 avec BatchNorm ReLU. Branche moleculaire : empreinte de Morgan 518 bits vers Linear 518 vers 256 avec BatchNorm ReLU Dropout 0.4, puis Linear 256 vers 128 avec BatchNorm ReLU Dropout 0.3, puis Linear 128 vers 64 avec ReLU. Fusion par concatenation des deux vecteurs (96 dimensions), puis Linear 96 vers 64 vers 32 vers 4. Sortie : action predite.]

Trois verrous techniques accompagnent ce choix et sont traités aux chapitres 3 et 4.

**Hétérogénéité des encodages.** Un score d'activité CYP2D6, qui somme les contributions de deux allèles, et un code de génotype SNP pour VKORC1 ne sont pas commensurables, alors qu'ils occupent des colonnes de même nature dans la matrice d'entrée du modèle.

**Qualité des étiquettes avant déséquilibre des classes.** Un premier jeu de données élargi à douze gènes supplémentaires a dégradé les performances de prédiction. L'analyse a montré que la cause n'était pas le déséquilibre des classes, mais l'assignation d'actions à des gènes dépourvus de ligne directrice actionnable.

**Décalage entraînement–inférence.** Les phénotypes d'entraînement proviennent d'appeleurs d'allèles dédiés, alors que l'application dérive le phénotype du génotype brut lu dans le VCF.

---

## 1.3 L'application de prédiction : trois capacités pour le clinicien

Le modèle de Deep Learning n'a de valeur que s'il atteint le moment de la prescription. L'application web en est le véhicule, et sa spécification tient en trois capacités.

**Analyser un patient.** Le clinicien dépose le fichier VCF. L'application en dérive le profil sur 31 gènes et affiche les médicaments concernés, répartis en quatre blocs selon l'action prédite, avec pour chacun le gène responsable, le phénotype identifié et le score de confiance de la prédiction.

**Interroger une molécule.** Le clinicien saisit le nom d'un médicament qu'il envisage de prescrire. L'application prédit l'action pour ce patient, même si la molécule n'apparaît pas dans la liste initiale.

**Justifier chaque prédiction.** Chaque ligne affichée porte son explication : le gène qui a pesé sur la prédiction — information extraite du mécanisme d'attention du modèle de Deep Learning — le phénotype du patient, et la référence de la ligne directrice correspondante lorsqu'elle existe.

Ces trois capacités structurent le chapitre 6, qui décrit l'architecture logicielle, le parseur VCF, le moteur d'inférence et l'interface clinicien.

---

## 1.4 Contexte : la variabilité génétique de la réponse aux médicaments

La réponse à un médicament varie d'un patient à l'autre, et une part de cette variabilité est génétique. Les enzymes du cytochrome P450, les transporteurs membranaires et certaines cibles pharmacologiques sont codés par des gènes polymorphes. Selon le diplotype qu'il porte, un patient métabolise une molécule lentement, normalement ou très rapidement, ce qui modifie l'exposition au principe actif, donc l'efficacité et la toxicité du traitement.

Cette variabilité est massivement répandue. Dans une cohorte hospitalière suisse comparée à une cohorte populationnelle de 4 791 individus, 97,3 % des participants portaient au moins un variant pharmacogénétique actionnable (Clin Transl Sci, 2024). Une projection sur 7 769 359 usagers de la pharmacie du Veterans Health Administration aboutit à 99 % (JAMA Netw Open, 2019). L'analyse de 6 045 génomes qataris donne 3,6 génotypes actionnables par individu en moyenne, et 99,5 % de porteurs d'au moins un génotype actionnable (npj Genom Med, 2022).

Ce dernier chiffre est le point de départ technique de ce travail. Un patient réel n'a presque jamais un seul gène altéré, mais plusieurs simultanément — et le médicament qu'on lui prescrit est souvent substrat de plus d'un d'entre eux. C'est précisément la situation que la section 1.2 identifie comme hors de portée d'une table indexée par paire, et que le modèle de Deep Learning est conçu pour traiter.

Le bénéfice clinique du génotypage préemptif est établi par un essai randomisé. L'étude PREPARE, conduite sur 6 944 patients dans sept pays européens avec un panel de douze gènes, rapporte 21 % d'effets indésirables cliniquement pertinents dans le groupe guidé par le génotype contre 28 % dans le groupe témoin, soit une réduction du risque de 30 % (OR 0,70 ; IC 95 % 0,54–0,91 ; p = 0,0075) — Swen et al., Lancet 401:347-356, 2023.

Le verrou n'est donc plus la preuve du bénéfice. Il est dans l'outil capable de porter cette preuve jusqu'au moment de la prescription.

---

## 1.5 Le maillon manquant entre le VCF et la prescription

Entre le séquençage d'un patient et la décision du clinicien, la chaîne comporte trois maillons. Les deux premiers sont solidement occupés ; le troisième ne l'est pas.

**Le maillon de la preuve** est tenu par les bases de connaissances et les consortiums de recommandations. Le Clinical Pharmacogenetics Implementation Consortium publie des lignes directrices associant diplotype, phénotype et conduite à tenir : 34 gènes et 164 médicaments, 28 guidelines actives, utilisées par 128 établissements de santé et 40 laboratoires commerciaux (Caudle et al., Clin Pharmacol Ther, 2025). PharmGKB, désormais intégré à ClinPGx, agrège les annotations variant–médicament et leurs niveaux de preuve. Ce sont des corpus de connaissance ; ils ne s'exécutent pas sur un patient.

**Le maillon de l'interprétation** est tenu par les logiciels d'annotation. PharmCAT extrait les variants d'intérêt d'un VCF, en infère haplotypes et diplotypes, et produit un rapport reprenant les recommandations CPIC publiées (Sangkuhl et al., Clin Pharmacol Ther, 2020). PyPGx, Aldy et Stargazer appellent les allèles étoile. Leurs limites sont documentées par leurs propres auteurs : CYP2D6, HLA-A et HLA-B ne sont pas appelables depuis un VCF et doivent être fournis par un appel externe, parce que la variation structurale et le nombre de copies dépassent ce qu'un fichier de SNP et d'indels permet de déterminer.

**Le maillon de la décision est vide.** Aucun de ces systèmes ne prédit, pour un patient donné et une molécule donnée, une réponse unique et interrogeable. Trois raisons structurelles l'en empêchent.

Ils raisonnent paire par paire. Une table de correspondance est indexée par gène et par médicament. Quand un patient cumule des variants dans quatre gènes et que la molécule est substrat de trois d'entre eux, la table renvoie trois lignes indépendantes ; elle ne les compose pas en une décision.

Ils s'arrêtent au bord de la ligne directrice. Les 164 médicaments couverts par CPIC sont une fraction de ce qu'un clinicien prescrit. Une molécule hors table ne reçoit aucune réponse, pas même approchée, alors que sa parenté structurale avec des molécules documentées porte de l'information exploitable.

Ils produisent un rapport, pas un système interrogeable. Le clinicien qui a un médicament en tête doit relire un document au lieu de poser sa question.

C'est ce maillon que PharmaGeno occupe, et c'est pourquoi il est conçu comme une application de prédiction autonome — pipeline, modèle de Deep Learning, interface et jeu de données propres — et non comme une surcouche d'un outil existant.

---

## 1.6 Problématique et question de recherche

Peut-on apprendre, par le Deep Learning, une fonction de prédiction qui prenne en entrée le profil génétique complet d'un patient et la structure chimique d'un médicament, et qui prédise une conduite à tenir unique — y compris lorsque plusieurs gènes interviennent simultanément, et lorsque la molécule n'est couverte par aucune ligne directrice ?

Cette formulation impose d'emblée une exigence d'honnêteté méthodologique, discutée en détail au chapitre 5. Les étiquettes d'entraînement sont dérivées des règles CPIC. Sur les paires couvertes par une ligne directrice, la cible est donc une fonction déterministe des entrées, et les métriques rapportées mesurent d'abord une fidélité d'implémentation, non une performance prédictive sur une cohorte prospective.

Ce que le modèle de Deep Learning ajoute réellement se situe ailleurs : dans la composition de plusieurs gènes, et dans l'extrapolation chimique vers des molécules non couvertes. Ces deux apports sont quantifiés par les études d'ablation du chapitre 5.

---

## 1.7 Objectifs

L'objectif général est de concevoir, entraîner, évaluer et déployer une application web de prédiction fondée sur le Deep Learning, qui transforme un fichier VCF en recommandations de prescription explicites et sourcées.

Cinq objectifs techniques en découlent.

1. Concevoir l'architecture de Deep Learning à deux branches avec attention sur les gènes, et la comparer à des méthodes d'apprentissage automatique classiques — forêt aléatoire et XGBoost — sous protocole identique.

2. Construire un jeu de données traçable associant profils génétiques réels, médicaments et actions de prescription, en croisant PharmGKB, CPIC, ClinVar, la FDA et les données du 1000 Genomes Project.

3. Représenter chaque médicament par sa structure chimique, au moyen d'empreintes de Morgan calculées sur les structures PubChem, afin de rendre possible la prédiction pour des molécules hors ligne directrice.

4. Évaluer les modèles prédictifs sous un protocole exempt de fuite de données, et quantifier séparément la reproduction des règles et la généralisation multi-gènes.

5. Déployer l'ensemble dans une application Flask utilisable par un clinicien, avec explication et référence pour chaque prédiction.

---

## 1.8 Contributions

1. Une architecture de Deep Learning à deux branches avec attention sur les gènes, pour la prédiction de l'action de prescription. Elle traite le profil génétique comme une entité unique au lieu d'une suite de paires gène–médicament, et encode le médicament par sa structure chimique plutôt que par son identifiant. Évaluée par validation croisée stratifiée à cinq plis, avec normalisation ajustée à l'intérieur de chaque pli.

2. Une application web de prédiction complète de bout en bout, du fichier VCF à l'action prédite et interrogeable : parseur VCF, moteur d'inférence profond, interface clinicien avec justification par prédiction, et génération d'un rapport patient.

3. Une démonstration quantifiée de l'insuffisance du raisonnement par paires pour la prédiction : sur les 530 médicaments du corpus, aucun gène unique ne détermine l'action pour 186 d'entre eux, soit 35 %.

4. Un jeu de données pharmacogénomique multi-sources et documenté — 46 371 associations, 31 gènes, 530 médicaments, 3 666 profils génétiques distincts issus d'individus réels — accompagné d'un journal d'audit des conflits inter-sources et d'une traçabilité par ligne.

5. Une analyse méthodologique d'un échec instructif : l'ajout de gènes dépourvus de ligne directrice CPIC de niveau A dégrade les performances du modèle de Deep Learning, et aucune technique de rééquilibrage des classes ne compense un défaut de qualité des étiquettes.

---

## 1.9 Organisation du mémoire

Le chapitre 2 établit l'état de l'art et dégage les verrous scientifiques. Le chapitre 3 décrit les données et la représentation des entrées : construction du jeu de données, extraction des génotypes, encodage génotype–phénotype, audit des conflits, empreintes moléculaires. Le chapitre 4 est consacré au modèle de Deep Learning — architecture, mécanisme d'attention, entraînement, comparaison aux méthodes classiques. Le chapitre 5 présente le protocole d'évaluation et les résultats, y compris les études d'ablation qui isolent l'apport de chaque composant. Le chapitre 6 est consacré à l'application de prédiction : spécification fonctionnelle, architecture logicielle, interface, sécurité. Le chapitre 7 discute les résultats, le positionnement et les limites. Le chapitre 8 conclut et ouvre les perspectives.
