# CHAPITRE 1 — INTRODUCTION GÉNÉRALE

*A Deep Learning based Webtool for Mutation-Aware Drug Recommendation*

---

## 1.1 Contexte et motivation

La réponse à un médicament varie considérablement d'un individu à l'autre. Pour une même molécule administrée à une dose identique, certains patients obtiennent l'effet thérapeutique attendu, tandis que d'autres présentent une réponse insuffisante ou développent des effets indésirables. Cette variabilité dépend de nombreux facteurs, notamment l'âge, l'état physiologique, les comorbidités, les interactions médicamenteuses et le patrimoine génétique du patient.

La pharmacogénomique étudie l'influence des variations génétiques sur la réponse aux médicaments. Des variants affectant des enzymes de métabolisation, des transporteurs ou des cibles pharmacologiques peuvent modifier l'exposition à un médicament, son efficacité ou son risque de toxicité. L'information génétique peut ainsi contribuer au choix thérapeutique, à l'ajustement de dose ou à la mise en place d'une surveillance spécifique.

L'intérêt potentiel de cette approche concerne une proportion importante de la population. Des études populationnelles et hospitalières rapportent une forte fréquence de variants pharmacogénétiques actionnables. Dans une cohorte suisse publiée en 2024, 97,3 % des participants portaient au moins un variant pharmacogénétique actionnable. Une étude portant sur 6 045 génomes qataris a rapporté en moyenne 3,6 génotypes ou diplotypes actionnables par individu et au moins un génotype actionnable chez 99,5 % des participants. Une analyse de plus de 7,7 millions d'usagers de la Veterans Health Administration avait également estimé que 99 % des individus porteraient au moins un variant pharmacogénétique actionnable.

Ce chiffre de 3,6 génotypes actionnables par individu oriente directement la formulation retenue dans ce mémoire : un patient présente rarement une seule particularité pharmacogénétique, et le médicament qui lui est prescrit relève souvent de plusieurs d'entre elles simultanément.

L'utilité clinique d'une stratégie pharmacogénomique préemptive a été évaluée prospectivement dans l'étude PREPARE. Cette étude multicentrique européenne, menée sur 6 944 patients dans sept pays et fondée sur un panel de douze gènes, rapporte 21 % d'effets indésirables cliniquement pertinents dans le groupe guidé par le génotype contre 28 % dans le groupe témoin, soit une réduction du risque de 30 % (OR 0,70 ; IC 95 % 0,54–0,91 ; p = 0,0075). Ces résultats renforcent l'intérêt d'outils capables d'intégrer l'information pharmacogénomique au moment de la prescription.

---

## 1.2 De la donnée génomique à la recommandation pharmacogénomique

Plusieurs ressources internationales structurent aujourd'hui les connaissances pharmacogénomiques. Le Clinical Pharmacogenetics Implementation Consortium (CPIC) publie des recommandations destinées à traduire certains résultats pharmacogénétiques en décisions de prescription. PharmGKB rassemble des connaissances sur les relations entre variants génétiques, médicaments et phénotypes pharmacologiques, et évolue désormais dans l'écosystème ClinPGx.

Des logiciels spécialisés automatisent une partie de l'interprétation. PharmCAT, par exemple, permet d'analyser des données génétiques compatibles, d'en déduire des haplotypes ou diplotypes et de générer un rapport fondé sur les recommandations disponibles. D'autres outils, tels que PyPGx, Aldy ou Stargazer, sont utilisés pour l'appel de certains allèles pharmacogénétiques complexes.

Ces ressources constituent une base essentielle, mais elles ne suppriment pas toutes les difficultés d'intégration. Certains gènes, notamment CYP2D6 ou certaines régions HLA, nécessitent des traitements spécifiques en raison de variants structuraux, de variations du nombre de copies ou de contraintes d'appel qui ne sont pas correctement résolues par une simple lecture de SNP et d'indels dans un fichier VCF conventionnel.

Le problème étudié dans ce mémoire ne correspond donc pas à une absence de recommandations pharmacogénomiques. Il concerne plutôt la manière d'exploiter simultanément plusieurs composantes du profil pharmacogénomique d'un patient et les caractéristiques d'un médicament dans un modèle prédictif unique, tout en maintenant une traçabilité vers les connaissances de référence.

---

## 1.3 Positionnement de PharmaGeno

Ce mémoire propose PharmaGeno, un système expérimental d'aide à la décision pharmacogénomique fondé principalement sur le Deep Learning. Le système reçoit le fichier VCF du patient, en dérive un profil pharmacogénomique multi-gènes, associe ce profil à une représentation moléculaire du médicament, puis produit une action pharmacogénomique prédite.

**La première entrée du modèle est le profil pharmacogénomique du patient.** Il est construit à partir des variants lus dans le fichier VCF, puis traduits en valeurs de phénotype lorsque l'information nécessaire est disponible. Plusieurs pharmacogènes sont représentés simultanément dans un même vecteur. L'objectif est de traiter le profil du patient comme un ensemble cohérent et non comme une simple succession de couples gène–médicament indépendants.

**La seconde entrée est une représentation du médicament fondée sur sa structure chimique.** La branche médicament reçoit une empreinte de Morgan de 512 bits, calculée avec RDKit à partir des structures SMILES obtenues auprès de PubChem, complétée par six descripteurs physico-chimiques — masse moléculaire, coefficient de partage, donneurs et accepteurs de liaisons hydrogène, liaisons rotatives et surface polaire topologique — soit un vecteur de 518 variables. Les deux représentations sont traitées par des branches distinctes puis fusionnées avant la classification finale.

**La sortie du système est normalisée en quatre catégories** : EVITER, ADAPTER_DOSE, SURVEILLER et STANDARD. Ces classes constituent une simplification opérationnelle destinée à rendre les résultats lisibles. Elles ne remplacent pas le texte détaillé d'une recommandation clinique et doivent rester reliées à leur provenance pharmacogénomique.

> **Figure 1.1** — Architecture fonctionnelle simplifiée de PharmaGeno. Le fichier VCF du patient est converti en profil pharmacogénomique multi-gènes ; le médicament interrogé est converti en empreinte moléculaire. Les deux représentations sont traitées conjointement par le modèle afin de produire une action pharmacogénomique prédite.

---

## 1.4 Pourquoi étudier le Deep Learning ?

Le recours au Deep Learning constitue l'hypothèse principale de recherche de ce mémoire, et non une conclusion posée à l'avance. Son intérêt potentiel repose sur trois propriétés qui doivent être évaluées expérimentalement : l'intégration d'un profil multi-gènes, l'exploitation d'une représentation moléculaire du médicament et l'utilisation d'un mécanisme d'attention sur les variables génétiques.

### 1.4.1 Intégration d'un profil multi-gènes

Un patient peut présenter simultanément plusieurs variations pharmacogénétiques, et un médicament peut être concerné par plusieurs mécanismes biologiques. Le modèle proposé reçoit donc un vecteur contenant simultanément l'information disponible pour plusieurs pharmacogènes. L'objectif est d'étudier si cette représentation globale améliore la prédiction par rapport à une représentation limitée au gène directement associé au médicament.

Cette hypothèse doit être vérifiée par une étude d'ablation comparant une configuration *single-gene* à une configuration multi-gènes, sur les mêmes données et sous le même protocole d'évaluation. L'apport du profil global ne sera donc pas supposé, mais mesuré.

### 1.4.2 Représentation moléculaire du médicament

L'utilisation d'une représentation chimique, plutôt qu'un simple identifiant de médicament, fournit au modèle des informations sur la structure moléculaire. Les empreintes de Morgan encodent la présence de sous-structures et permettent de comparer des molécules dans un espace de caractéristiques commun.

Cette représentation ouvre théoriquement la possibilité d'une généralisation à des médicaments absents de l'ensemble d'apprentissage mais chimiquement proches de molécules connues. Toutefois, cette capacité constitue une hypothèse expérimentale et ne doit pas être assimilée à une recommandation clinique. Elle devra être évaluée au moyen d'un protocole dédié où certains médicaments sont totalement exclus de l'entraînement.

La construction de cette représentation a elle-même fait l'objet d'un contrôle documenté. Un audit des empreintes initialement disponibles a révélé que les 512 bits structuraux étaient nuls pour l'intégralité des médicaments du corpus : seuls les six descripteurs globaux portaient effectivement de l'information. Les structures ont été récupérées depuis PubChem et les empreintes recalculées avec RDKit, portant la couverture à 437 médicaments sur 437, avec en moyenne 43 bits actifs par molécule. Les structures SMILES correspondantes sont conservées afin de rendre le calcul reproductible. Cet épisode est détaillé au chapitre 3 ; il illustre la nécessité d'un contrôle explicite des représentations avant toute interprétation des performances.

### 1.4.3 Mécanisme d'attention sur les gènes

La branche génétique intègre un mécanisme GeneAttention destiné à moduler la contribution des différentes variables génétiques avant leur traitement par le réseau. Les poids d'attention peuvent être analysés comme un signal d'interprétabilité du modèle. Ils ne constituent toutefois pas une preuve de causalité biologique et doivent être interprétés avec prudence, en complément de méthodes d'explicabilité adaptées aux autres modèles comparatifs.

---

## 1.5 Verrou scientifique et positionnement par rapport aux approches existantes

Les ressources et logiciels pharmacogénomiques existants jouent un rôle essentiel : ils organisent les connaissances, permettent l'appel de certains génotypes ou diplotypes et relient des résultats pharmacogénétiques à des recommandations documentées. PharmaGeno ne vise pas à remplacer CPIC, DPWG, PharmGKB ou PharmCAT.

Le verrou étudié est différent : il s'agit de déterminer si un modèle prédictif peut exploiter conjointement le profil pharmacogénomique multi-gènes d'un patient et la représentation moléculaire d'un médicament pour produire une action individualisée, tout en conservant une traçabilité vers les connaissances pharmacogénomiques de référence.

Cette question implique également de vérifier si le Deep Learning est réellement justifié par les données disponibles. Les données utilisées sont principalement structurées et leur volume reste limité par rapport aux domaines où les réseaux profonds présentent traditionnellement un avantage important. Random Forest et XGBoost sont donc introduits comme modèles de référence comparatifs. Leur rôle est d'évaluer objectivement si la complexité du modèle profond apporte un bénéfice mesurable.

---

## 1.6 Problématique et questions de recherche

> Dans quelle mesure une architecture de Deep Learning intégrant simultanément le profil pharmacogénomique multi-gènes d'un patient et la représentation moléculaire d'un médicament peut-elle prédire une action pharmacogénomique individualisée, et quel avantage apporte-t-elle par rapport aux approches classiques et aux représentations limitées à un seul gène ?

Cette problématique est déclinée en six questions de recherche.

**RQ1 — Profil multi-gènes.** L'utilisation du profil pharmacogénomique complet améliore-t-elle la prédiction par rapport à une représentation limitée au gène directement associé au médicament ?

**RQ2 — Deep Learning.** L'architecture proposée est-elle plus performante que Random Forest et XGBoost sur les données disponibles ?

**RQ3 — Attention.** Le mécanisme GeneAttention apporte-t-il un gain mesurable par rapport à une architecture multi-gènes sans attention ?

**RQ4 — Représentation moléculaire.** L'utilisation d'empreintes de Morgan et de descripteurs moléculaires améliore-t-elle la prédiction par rapport à une représentation exclusivement génétique ?

**RQ5 — Généralisation.** Dans quelle mesure les modèles conservent-ils leurs performances sur des patients indépendants et sur des médicaments absents de l'ensemble d'entraînement ?

**RQ6 — Concordance pharmacogénomique.** Dans les situations couvertes par une recommandation de référence, les actions produites sont-elles concordantes avec l'interprétation pharmacogénomique attendue ?

Cette formulation distingue volontairement la prédiction produite par un modèle de la recommandation clinique établie par une guideline. Lorsqu'une recommandation explicite existe, celle-ci demeure la référence clinique.

---

## 1.7 Objectifs du mémoire

L'objectif général est de concevoir, entraîner, évaluer et intégrer dans une application web un système expérimental d'aide à la décision pharmacogénomique combinant profil génétique multi-gènes, représentation moléculaire du médicament, Deep Learning et connaissances pharmacogénomiques de référence.

1. Construire et auditer un jeu de données pharmacogénomique multi-source, en assurant la traçabilité des labels, la gestion des valeurs manquantes et le traitement explicite des conflits entre sources.

2. Développer une architecture Deep Learning à deux branches : une branche génétique dédiée au profil multi-gènes et une branche dédiée à la représentation moléculaire du médicament.

3. Évaluer l'intérêt de GeneAttention par comparaison avec une architecture équivalente sans mécanisme d'attention.

4. Comparer le Deep Learning à Random Forest et XGBoost sous un protocole d'évaluation identique et exempt de fuite entre entraînement et test.

5. Mesurer spécifiquement l'apport du profil multi-gènes au moyen d'une comparaison *single-gene* contre multi-gènes.

6. Évaluer l'apport de la représentation moléculaire du médicament et étudier la généralisation à des médicaments non rencontrés pendant l'apprentissage.

7. Étudier l'explicabilité des prédictions au moyen des poids d'attention et de méthodes telles que SHAP pour les modèles à base d'arbres.

8. Déployer le pipeline dans une application Flask permettant l'analyse d'un fichier VCF, l'interrogation d'un médicament et l'affichage d'une sortie structurée, sourcée et interprétable.

---

## 1.8 Approche méthodologique générale

L'approche proposée suit une chaîne en cinq étapes complémentaires.

**Étape 1 — Acquisition du profil génétique.** Le système reçoit un fichier VCF ou des résultats pharmacogénomiques dérivés du patient.

**Étape 2 — Construction du profil pharmacogénomique.** Les variants pertinents sont identifiés et traduits, lorsque l'information nécessaire est disponible, en variables exploitables par les modèles. Les gènes nécessitant des appels spécialisés sont distingués des génotypes directement interprétables.

**Étape 3 — Représentation du médicament.** Chaque médicament est représenté par une empreinte de Morgan de 512 bits et six descripteurs physico-chimiques complémentaires, calculés à partir de sa structure chimique.

**Étape 4 — Prédiction et comparaison.** Le profil génétique et la représentation moléculaire sont fournis au modèle Deep Learning et aux modèles comparatifs afin d'estimer une action parmi les quatre catégories définies.

**Étape 5 — Restitution et traçabilité.** L'application présente la sortie du modèle avec les éléments d'explicabilité et, lorsqu'elle existe, la référence pharmacogénomique pertinente.

---

## 1.9 Contributions attendues

Afin d'éviter de présenter comme acquises des conclusions encore en cours de validation, les contributions sont formulées ici comme contributions méthodologiques et expérimentales attendues.

1. Une approche pharmacogénomique centrée sur le profil multi-gènes du patient, évaluée explicitement par rapport à une représentation *single-gene*.

2. Une architecture Deep Learning à deux branches combinant GeneAttention et une représentation moléculaire du médicament.

3. Une évaluation comparative rigoureuse du Deep Learning, de Random Forest et de XGBoost, complétée par des études d'ablation permettant d'isoler l'effet de chaque composant.

4. Une démarche documentée de contrôle qualité des données pharmacogénomiques : provenance, conflits de labels, valeurs manquantes, cohérence des profils, vérification des représentations moléculaires et reproductibilité du jeu de données.

5. Une application web intégrée reliant analyse du fichier VCF, construction du profil pharmacogénomique, inférence, explicabilité et restitution des résultats.

Une éventuelle capacité de généralisation à des médicaments non observés pendant l'apprentissage ne sera revendiquée comme contribution que si elle est démontrée par un protocole *drug-held-out* indépendant.

---

## 1.10 Organisation du mémoire

Le reste du mémoire est organisé comme suit. Le chapitre 2 présente l'état de l'art en pharmacogénomique computationnelle, les principales bases de connaissances, les guidelines et les approches de Machine Learning et de Deep Learning appliquées à la médecine personnalisée. Le chapitre 3 décrit les données, leur provenance, leur préparation, la construction du profil patient et la représentation moléculaire des médicaments. Le chapitre 4 présente l'architecture Deep Learning proposée ainsi que Random Forest et XGBoost utilisés comme modèles de référence. Le chapitre 5 détaille le protocole expérimental, les résultats et les études d'ablation. Le chapitre 6 est consacré à l'explicabilité et aux études de cas pharmacogénomiques. Le chapitre 7 décrit la conception et l'implémentation de l'application web PharmaGeno. Enfin, le chapitre 8 discute les résultats, les limites du travail et les perspectives, puis présente la conclusion générale.

---

*Références principales citées dans ce chapitre :* Swen et al., *The Lancet*, 2023 (PREPARE) ; études de prévalence pharmacogénétique (*Clin Transl Sci*, 2024 ; *JAMA Network Open*, 2019 ; *npj Genomic Medicine*, 2022) ; Caudle et al., *Clinical Pharmacology & Therapeutics*, 2025 ; Sangkuhl et al., *Clinical Pharmacology & Therapeutics*, 2020 ; ressources CPIC, PharmGKB/ClinPGx et PharmCAT ; RDKit et PubChem PUG REST pour le calcul des empreintes moléculaires.
