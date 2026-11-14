## Chapitre 1 : Introduction générale

### 1.1 Contexte et motivation

La réponse à un médicament varie d'un individu à l'autre : à dose identique, certains patients obtiennent l'effet attendu, d'autres une réponse insuffisante ou des effets indésirables. L'âge, les comorbidités, les interactions et le patrimoine génétique y contribuent. La pharmacogénomique étudie le rôle des variations génétiques portant sur des enzymes de métabolisation, des transporteurs ou des cibles pharmacologiques : elles peuvent modifier l'exposition au médicament, son efficacité ou sa toxicité, et donc orienter le choix du traitement, la dose ou la surveillance.

L'intérêt concerne une grande part de la population. Dans une cohorte suisse publiée en 2024, 97,3 % des participants portaient au moins un variant pharmacogénétique actionnable (Hodel et al., 2024). Une étude de 6 045 génomes qataris rapporte en moyenne 3,6 génotypes ou diplotypes actionnables par individu et au moins un chez 99,5 % des participants (Jithesh et al., 2022). Une analyse de 7 769 359 usagers de la pharmacie de la Veterans Health Administration estime que 99 % des individus porteraient au moins un variant actionnable (Chanfreau-Coffinier et al., 2019). Un même patient peut donc cumuler plusieurs particularités, ce qui justifie d'étudier une représentation globale de son profil, sans présumer que plusieurs gènes interviennent dans la réponse à chaque médicament.

L'utilité clinique d'une stratégie préemptive a été évaluée dans l'étude PREPARE (6 944 patients, sept pays européens). Parmi les 1 558 participants avec une interaction gène–médicament actionnable pour le médicament index, une réaction indésirable cliniquement pertinente a été observée chez 21,0 % des patients traités selon le génotype contre 27,7 % en soins standards (OR = 0,70 ; IC 95 % : 0,54–0,91 ; p = 0,0075) (Swen et al., 2023).

### 1.2 De la donnée génomique à la recommandation

Le Clinical Pharmacogenetics Implementation Consortium (CPIC) publie des recommandations fondées sur les preuves ; une synthèse de 2025 rapporte 34 gènes et 164 médicaments (Caudle et al., 2025). PharmGKB, aujourd'hui intégré à ClinPGx, rassemble les relations entre variants, médicaments et phénotypes. Des logiciels automatisent une partie de l'interprétation : PharmCAT extrait les variants d'intérêt, infère haplotypes et diplotypes et produit un rapport (Sangkuhl et al., 2020) ; PyPGx, Aldy ou Stargazer réalisent l'appel d'allèles complexes.

Ces ressources ne suppriment pas toutes les difficultés. CYP2D6 et certaines régions HLA exigent des appels spécialisés (variations du nombre de copies, structures hybrides) que ne résout pas une simple lecture de SNP et d'indels dans un VCF ; la documentation PharmCAT recommande des appels externes pour CYP2D6, HLA-A et HLA-B (documentation PharmCAT, mode recherche). Le problème étudié ne tient donc pas à l'absence de recommandations, mais à la manière d'exploiter simultanément plusieurs composantes du profil d'un patient dans un modèle unique, pour de nombreux médicaments, avec une traçabilité vers les connaissances de référence.

### 1.3 Positionnement de PharmaGeno

PharmaGeno est un prototype expérimental d'aide à la décision pharmacogénomique fondé principalement sur le Deep Learning. L'entrée réelle est un fichier VCF patient et la spécialité choisie par le clinicien. Le système en extrait un profil multi-gènes ; un réseau de neurones lit ce profil en une fois et produit, pour chacun des 189 médicaments de son périmètre, une classe d'action parmi quatre : EVITER, ADAPTER\_DOSE, SURVEILLER, STANDARD. L'application web présente les résultats médicament par médicament, par spécialité, en les mettant en regard de la règle officielle CPIC/DPWG.

Dans le corpus v15, le profil compte 20 variables génétiques (16 gènes et 4 allèles HLA). Quatorze d'entre elles peuvent être non déterminées et reçoivent chacune un indicateur d'absence, de sorte que le réseau reçoit 34 entrées (20 variables et 14 indicateurs). Un gène non déterminé n'est jamais assimilé à un résultat normal.

Le médicament n'est pas une entrée du réseau : c'est une sortie. Le réseau possède, pour chaque médicament, un groupe de quatre probabilités ; le médicament interrogé sélectionne le groupe. Ce choix résulte d'une étape antérieure à deux branches (profil génétique et description chimique du médicament : empreinte de Morgan de 512 bits et six descripteurs physico-chimiques) qui n'a pas amélioré les performances et n'a pas permis de prédire l'action pour un médicament absent de l'entraînement (chapitre 6). Un second réseau, dit « choix », classe les médicaments évaluables d'une même classe ATC de niveau 4 par une probabilité de type softmax ; sa cible est une convention du projet, non une recommandation de guideline, et sa probabilité n'est pas une probabilité clinique de succès.

Le jeu de données est désigné par le terme « corpus » : un tableau dont chaque ligne associe un profil patient et un médicament à une action. La version actuelle, le corpus v15, combine 1 379 profils génétiques réels du 1000 Genomes Project avec des étiquettes calculées à partir de règles extraites des lignes directrices CPIC, DPWG, RNPGx et d'étiquettes réglementaires. Il compte 234 632 lignes portant sur 189 médicaments : STANDARD 201 273, ADAPTER\_DOSE 20 272, EVITER 8 031, SURVEILLER 5 056. Il ne s'agit pas d'une cohorte clinique : les étiquettes étant déterministes, **les métriques mesurent la fidélité des modèles aux lignes directrices, non un résultat clinique**. Le chapitre 7 y ajoute un contrôle sur de vrais patients.

### 1.4 Pourquoi étudier le Deep Learning ?

Le recours au Deep Learning est l'hypothèse principale du mémoire, non une conclusion posée à l'avance. Son intérêt potentiel repose sur deux propriétés à évaluer : l'intégration d'un profil multi-gènes et la prédiction simultanée, par un seul réseau, de l'action pour de nombreux médicaments avec des probabilités calibrées.

**Profil multi-gènes.** Un patient peut porter plusieurs particularités et certaines décisions dépendent de plusieurs gènes. Dans le corpus v15, 57 médicaments ont une action constante pour tous les profils — 52 toujours STANDARD, 4 toujours ADAPTER\_DOSE et 1 toujours EVITER — et 132 une action qui varie selon le profil. Sur le corpus v12, un audit de déterminisme a montré que l'action est constante ou déterminée par un seul gène pour 121 des 133 médicaments alors couverts ; le bénéfice attendu du profil global se concentre donc sur une minorité de médicaments (amitriptyline, azathioprine, carbamazépine, clomipramine, doxépine, fluvastatine, imipramine, mercaptopurine, rosuvastatine, sertraline, thioguanine, trimipramine). Cet audit n'a pas été refait sur le corpus v15 \[à compléter\] ; les règles à plusieurs gènes y étant plus nombreuses qu'en v12, la proportion actuelle est vraisemblablement différente, mais elle n'est pas mesurée.

**Représentation moléculaire du médicament (étape antérieure).** Elle devait permettre de généraliser à des médicaments absents de l'entraînement. Testée sur le corpus v7 avec des plis groupés par médicament, elle donne un F1 macro de 0,467 (DL), 0,502 (Random Forest) et 0,454 (XGBoost), avec 63 à 70 % des situations à éviter manquées : aucune généralisation fiable n'est démontrée. Un nouveau test, mené sur une version ultérieure du corpus (chapitre 6), conduit à la même conclusion.

**Attention.** Le mécanisme d'attention de l'étape antérieure (modulation FiLM par le médicament) n'existe plus dans le réseau actuel ; aucune ablation ne l'a isolé et aucun apport n'est revendiqué. Les poids d'attention ne sont pas utilisés comme explication (Jain et Wallace, 2019).

### 1.5 Verrou scientifique et positionnement

PharmaGeno ne remplace ni CPIC, ni DPWG, ni PharmGKB/ClinPGx, ni PharmCAT. Le verrou étudié est de déterminer si un modèle prédictif peut exploiter l'ensemble du profil multi-gènes d'un patient pour produire, en une lecture, une classe d'action pour de nombreux médicaments, avec une traçabilité vers les connaissances de référence. Il faut aussi vérifier que le Deep Learning est justifié par des données surtout structurées et de volume limité : Random Forest et XGBoost sont donc des comparateurs. Dans la comparaison à protocole identique sur le corpus v15, où les trois modèles reçoivent le même réglage, aucune supériorité du réseau sur XGBoost n'est établie — les deux modèles sont déclarés équivalents pour la configuration déployée dans l'application — et tous deux reproduisent les règles mieux que Random Forest ; XGBoost conserve en revanche un avantage sur le nombre de situations à éviter manquées (chapitre 6). Lorsqu'une recommandation explicite existe, elle reste la référence clinique.

### 1.6 Problématique et questions de recherche

> Dans quelle mesure un réseau de Deep Learning lisant le profil pharmacogénomique multi-gènes complet d'un patient peut-il prédire une classe d'action individualisée pour de nombreux médicaments, et quel avantage apporte-t-il par rapport aux approches classiques et aux représentations limitées à un seul gène ?

- **RQ1 — Profil multi-gènes.** Le profil complet améliore-t-il la prédiction par rapport au seul gène associé au médicament ?
- **RQ2 — Deep Learning.** Le réseau est-il plus performant que Random Forest et XGBoost, en F1 macro et en situations à éviter manquées ?
- **RQ3 — Calibration.** Les probabilités sont-elles calibrées et un seuil de confiance signale-t-il les cas incertains ?
- **RQ4 — Représentation moléculaire.** La description du médicament améliore-t-elle la prédiction, notamment pour un médicament jamais vu ?
- **RQ5 — Généralisation.** Les performances se conservent-elles sur des profils non utilisés à l'entraînement, des médicaments absents de l'entraînement et des combinaisons de gènes jamais observées ?
- **RQ6 — Concordance.** Les actions produites sont-elles concordantes avec l'interprétation attendue des références ?
- **RQ7 — Validité hors règles.** Les règles qui servent d'étiquettes sont-elles cohérentes avec des données de patients réels (cas de la warfarine) ?

### 1.7 Objectifs

L'objectif général est de concevoir, entraîner, évaluer et intégrer dans une application web un système expérimental d'aide à la décision combinant VCF, profil multi-gènes, Deep Learning et connaissances de référence.

1. Construire et auditer un corpus multi-source (traçabilité des étiquettes, valeurs manquantes, conflits entre sources).
2. Développer un réseau qui lit le profil complet et prédit l'action pour chaque médicament, avec probabilités calibrées, et documenter l'étape à deux branches qui l'a précédé.
3. Comparer le Deep Learning à Random Forest et XGBoost sous un protocole identique (validation croisée à 5 plis groupés par identifiant de profil) et réserver un ensemble final de 138 profils à une évaluation unique.
4. Mesurer l'apport du profil multi-gènes (comparaison single-gene / multi-gènes).
5. Évaluer la généralisation à des médicaments et à des combinaisons de gènes non vus.
6. Confronter les règles du corpus à des données de patients réels.
7. Déployer le pipeline dans une application Flask qui analyse un VCF et affiche une sortie structurée, sourcée et interprétable.

### 1.8 Contributions

Elles sont formulées comme contributions méthodologiques et expérimentales, y compris lorsque les résultats sont négatifs.

1. Un corpus pharmacogénomique de 189 médicaments et 1 379 profils réels, audité et traçable (règles, hypothèses et limites documentées).
2. Un réseau qui lit le profil entier et prédit l'action pour 189 médicaments avec des probabilités calibrées, et un second réseau de choix au sein des classes ATC4.
3. Une évaluation honnête : comparaison à des modèles d'arbres sous protocole identique, dont la conclusion est rapportée telle quelle y compris lorsqu'elle ne confirme pas l'hypothèse du mémoire ; résultat négatif sur la généralisation à des médicaments non vus ; contrôle de la règle warfarine sur 5 774 patients réels.
4. Une application web reproductible reliant VCF, profil, inférence, références et restitution.

### 1.9 Organisation du mémoire

Le chapitre 2 présente l'état de l'art. Le chapitre 3 décrit les données et le corpus v15. Le chapitre 4 décrit les méthodes (modèles, entraînement, calibration, protocole). Le chapitre 5 décrit l'application web. Le chapitre 6 rapporte les résultats. Le chapitre 7 présente la validation externe d'une règle isolée (la warfarine) sur des patients réels. Le chapitre 8 présente la validation externe sur profil complet (génotype, recommandation, patients publiés). Le chapitre 9 discute les limites, les perspectives et conclut.
