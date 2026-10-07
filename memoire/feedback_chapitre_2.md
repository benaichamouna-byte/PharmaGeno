# FEEDBACK CRITIQUE — Chapitre 2 (version `Chapitre_2_Etat_de_l_art_PharmaGeno_FINAL.docx`)

**Date de vérification :** 6 octobre 2026
**Document analysé :** 4 547 mots, 9 sections, 9 références numérotées
**Méthode :** vérification source par source. Chaque référence a été recherchée et, quand la page était accessible, ouverte. Les mentions « ✔ CONFIRMÉ » signifient que j'ai lu la métadonnée sur une page de l'éditeur, d'un dépôt institutionnel ou du DOAJ. Les mentions « ⚠ À CONFIRMER » signifient que je n'ai pas pu vérifier et qu'il ne faut pas l'écrire sans contrôle.

---

## 1. VERDICT GLOBAL

Cette version est **meilleure que celle que j'avais rédigée** sur trois points précis, et je le dis sans réserve :

1. **Le traitement de PAnno.** La phrase « *Il serait donc incorrect de présenter l'agrégation de plusieurs déterminants génétiques comme totalement absente de la littérature* » est honnête et retire du mémoire une affirmation qu'un jury aurait démolie. Ma version laissait entendre que la couche de décision était vide. C'était faux.
2. **La reformulation du verrou** en *conjonction de trois éléments* plutôt qu'en *absence de système de décision*. C'est défendable en soutenance ; l'autre formulation ne l'était pas.
3. **La section 2.9.2** qui énonce explicitement qu'une performance élevée mesure d'abord la reproduction de la connaissance du corpus et non une découverte clinique. C'est exactement la bonne réponse à l'objection de circularité soulevée dans le projet.

**Mais le chapitre n'est pas publiable en l'état.** Le problème n'est pas le raisonnement, il est la **traçabilité** :

- **9 références pour 4 547 mots d'état de l'art.** Un état de l'art de M.Sc. en porte normalement 40 à 60. Le chapitre 1 (introduction) en a 9 — c'est normal pour une introduction, pas pour un chapitre 2.
- **Les sections 2.6 et 2.8 n'ont AUCUNE référence.** Or 2.6 justifie le choix Morgan 512 bits + 6 descripteurs, c'est-à-dire la variable centrale de la question de recherche RQ4. Ce choix est actuellement **affirmé, pas sourcé**. En soutenance, « j'ai choisi Morgan parce que les représentations apprises ne sont pas nécessairement meilleures sur des corpus modestes » sans citation est une opinion de confort. Avec la citation que je donne plus bas, cela devient un résultat documenté sur 25 modèles et 25 jeux de données. C'est précisément la différence entre *bon* et *excellent*.
- **Deux erreurs factuelles et deux références défectueuses** (détail en section 2).
- **Une publication de 2016 manque, et elle met la revendication de nouveauté en danger** (détail en section 4, point ①). C'est le point le plus grave du document.

---

## 2. VÉRIFICATION DES 9 RÉFÉRENCES

### [1] PharmCAT Research Mode — **affirmation correcte, URL morte**

L'affirmation du chapitre est exacte. J'ai ouvert la documentation : l'appel CYP2D6 depuis VCF appartient au Research Mode, la page invoque « *the large influence of SV and CNV on phenotype prediction* » et précise « *these features are not intended for use outside a research context* ».

**Problème :** `https://pharmcat.org/using/Research-Mode/` renvoie un **302 vers `https://pharmcat.clinpgx.org/using/Research-Mode/`**. PharmCAT a migré sous le domaine ClinPGx. Une URL qui redirige dans une bibliographie de mémoire est un défaut mineur mais visible.

**Correction :**
```
[1] PharmCAT. Research Mode — CYP2D6 calling from VCF: limitations.
    Documentation PharmCAT. https://pharmcat.clinpgx.org/using/Research-Mode/
    (consulté le 6 octobre 2026)
```
Toute référence à une ressource web doit porter une date de consultation. Aucune des références [1] et [3] n'en a.

### [2] Caudle et al. 2025 — **article réel, chiffre non vérifié**

L'article existe, le DOI est valide : *Advancing Clinical Pharmacogenomics Worldwide Through the Clinical Pharmacogenetics Implementation Consortium (CPIC)*, Caudle, **Clinical Pharmacology & Therapeutics**, 2025, DOI `10.1002/cpt.70005`. La page Wiley répond, mais refuse l'accès automatisé (403).

**Je n'ai donc pas pu vérifier le « 34 gènes et 164 médicaments » dans le texte de l'article.** Le PMID 40678821 n'est pas vérifié non plus.

**Deux actions obligatoires :**
1. Ouvre l'article toi-même et vérifie la phrase exacte qui porte ces deux nombres. Si elle n'existe pas sous cette forme, le chiffre sort du chapitre.
2. Quoi qu'il arrive, ce type de dénombrement **évolue** : CPIC ajoute des guidelines en continu. Un nombre sans date est faux l'année suivante. Écris : « *Une synthèse publiée en 2025 rapportait une couverture de X gènes et Y médicaments [2]* » — la formulation au passé est déjà bonne dans le chapitre, garde-la — **et** ajoute en note la source primaire avec date de consultation : `https://cpicpgx.org/genes-drugs/`.

### [3] IGSR / 1000 Genomes 30x — **affirmation correcte, source à élever**

2 504 individus non apparentés + 698 apparentés = 3 202 à ~30× : conforme. Mais citer un **portail de données** pour un fait qui dispose d'un article revu par les pairs est un affaiblissement gratuit.

**Référence à ajouter (✔ CONFIRMÉ, métadonnée lue chez le New York Genome Center) :**
```
Byrska-Bishop M, Evani US, Zhao X, et al. High-coverage whole-genome sequencing
of the expanded 1000 Genomes Project cohort including 602 trios.
Cell. 2022;185(18):3426-3440.e19. DOI: 10.1016/j.cell.2022.08.004
```
Garde l'URL IGSR **en plus**, pour la version exacte des fichiers utilisés — c'est justifié pour la reproductibilité.

### [4] PAnno — **✔ CONFIRMÉ**

Vérifié sur DOAJ. Complète les auteurs :
```
Liu Y, Lin Z, Chen Q, Chen Q, Sang L, Wang Y, Shi L, Guo L, Yu Y.
PAnno: A pharmacogenomics annotation tool for clinical genomic testing.
Front Pharmacol. 2023;14:1008330. DOI: 10.3389/fphar.2023.1008330
```

### [5] Kidwai-Khan et al. 2022 — **✔ CONFIRMÉ, exact**

Vérifié contre le BibTeX fourni par la revue elle-même. Rien à corriger. C'est la référence la mieux citée du chapitre.

### [6] Partin et al. 2023 — **référence ✔ CONFIRMÉE, mais ERREUR FACTUELLE dans le texte**

La référence est juste (*Front Med.* 2023;10:1086097, DOI `10.3389/fmed.2023.1086097`).

**Mais le chapitre écrit : « a recensé 61 modèles de Deep Learning ».** J'ai lu le texte de l'article : il dit « *a total of **61 peer-reviewed publications** have been identified* ». **Publications ≠ modèles.** Une publication peut proposer plusieurs modèles, ou aucun nouveau. C'est le genre d'imprécision qu'un rapporteur attentif relève, et qui jette un doute sur tout le reste du chapitre.

**Correction :** « *a recensé 61 publications revues par les pairs consacrées à des modèles de Deep Learning appliqués à la réponse aux traitements anticancéreux* ».

### [7] MOLI — **référence INCOMPLÈTE**

Le chapitre donne « Bioinformatics, 2019. PMCID: PMC6612815 ». Un PMCID seul, dans une liste où les autres portent un DOI, est incohérent.

**Référence complète (✔ CONFIRMÉE) :**
```
Sharifi-Noghabi H, Zolotareva O, Collins CC, Ester M.
MOLI: multi-omics late integration with deep neural networks for drug response prediction.
Bioinformatics. 2019;35(14):i501-i509. DOI: 10.1093/bioinformatics/btz318
```

### [8] DeepCDR — **RÉFÉRENCE DÉFECTUEUSE**

Le chapitre écrit « Bioinformatics, **2020/2021**. PMID: 33381841 ». Une année ambiguë dans un mémoire est inacceptable, et je n'ai pas pu confirmer ce PMID.

**Référence correcte (✔ CONFIRMÉE sur la page Oxford Academic) :**
```
Liu Q, Hu Z, Jiang R, Zhou M.
DeepCDR: a hybrid graph convolutional network for predicting cancer drug response.
Bioinformatics. 2020;36(Supplement_2):i911-i918. DOI: 10.1093/bioinformatics/btaa822
```
Supprime le PMID : le DOI suffit et il est vérifié.

### [9] HiDRA — **✔ CONFIRMÉ partiellement**

Titre, auteurs, revue, année, volume 61, numéro 8 et DOI `10.1021/acs.jcim.1c00706` : confirmés. **Les pages 3858-3867 : je ne les ai pas vérifiées** — les sources que j'ai pu ouvrir ne donnaient pas la pagination. ⚠ Contrôle-les sur la page ACS avant de figer la bibliographie.

---

## 3. SECTIONS SANS AUCUNE RÉFÉRENCE — RÉFÉRENCES À INSÉRER

Toutes les références ci-dessous ont été vérifiées sauf mention contraire explicite.

| § | Entité nommée sans source | Référence à insérer |
|---|---|---|
| 2.1.2 | PharmVar | Gaedigk A, Ingelman-Sundberg M, Miller NA, Leeder JS, Whirl-Carrillo M, Klein TE. *Clin Pharmacol Ther.* 2018;103(3):399-401. DOI: `10.1002/cpt.910` ✔ |
| 2.1.3 | « *Des travaux récents montrent que des modifications des définitions d'allèles étoile…* » | **Affirmation non sourcée — l'article qui dit exactement cela existe :** van der Maas S, Denil S, Maes B, Ertaylan G, Volders PJ. *Dynamic star allele definitions in Pharmacogenomics: impact on diplotype calls, Phenotype predictions and statin therapy recommendations.* Front Pharmacol. 2025;16:1584658. DOI: `10.3389/fphar.2025.1584658` ✔ |
| 2.2.1 | PharmGKB et ses niveaux de preuve | Whirl-Carrillo M, Huddart R, Gong L, Sangkuhl K, Thorn CF, Whaley R, Klein TE. *An Evidence-Based Framework for Evaluating Pharmacogenomics Knowledge for Personalized Medicine.* Clin Pharmacol Ther. 2021;110(3). PMID: 34216021 ✔ (volume/pages ⚠ à compléter) |
| 2.2.2 | CPIC — référence fondatrice absente | Relling MV, Klein TE. *CPIC: Clinical Pharmacogenetics Implementation Consortium of the Pharmacogenomics Research Network.* Clin Pharmacol Ther. 2011. DOI: `10.1038/clpt.2010.279` ✔ (volume/pages ⚠ à compléter) |
| 2.2.3 | DPWG | Swen JJ, et al. *Pharmacogenetics: from bench to byte — an update of guidelines.* Clin Pharmacol Ther. 2011;89(5):662-673. DOI: `10.1038/clpt.2011.34` ✔ |
| 2.2.3 | — (à ajouter : preuve d'utilité clinique) | Swen JJ, et al. *A 12-gene pharmacogenetic panel to prevent adverse drug reactions (PREPARE).* Lancet. 2023;401(10374):347-356. DOI: `10.1016/S0140-6736(22)01841-4` ✔ |
| 2.2.4 | ClinVar | Landrum MJ, et al. *ClinVar: improving access to variant interpretations and supporting evidence.* Nucleic Acids Res. 2018. PMID: 29165669 ✔ (DOI et pages ⚠ à confirmer sur la page OUP) |
| 2.3.2 | Stargazer | Lee SB, Wheeler MM, Patterson K, McGee S, Dalton R, Woodahl EL, Gaedigk A, Thummel KE, Nickerson DA. *Genet Med.* 2019;21(2):361-372. DOI: `10.1038/s41436-018-0054-0` ✔ |
| 2.3.2 | Aldy | Numanagić I, Malikić S, Ford M, et al. *Allelic decomposition and exact genotyping of highly polymorphic and structurally variant genes.* Nat Commun. 2018;9(1). DOI: `10.1038/s41467-018-03273-1` ✔ |
| 2.3.2 | PyPGx | **Pas d'article primaire.** Cite l'application revue par les pairs : Sherman CA, Claw KG, Lee S. *Sci Rep.* 2024;14:22774. DOI: `10.1038/s41598-024-73748-3` ✔ (voir section 4, point ⑤ — référence critique) |
| 2.6.2 | Morgan / ECFP | Rogers D, Hahn M. *Extended-Connectivity Fingerprints.* J Chem Inf Model. 2010. DOI: `10.1021/ci100050t` ✔ (volume/pages ⚠ à compléter) |
| 2.6.3 / 2.6.4 | « *pas nécessairement supérieurs sur des jeux de données modestes* » | **C'est l'affirmation la plus importante du chapitre et elle est nue.** Praski M, Adamczyk J, Czech W. *Benchmarking Pretrained Molecular Embedding Models For Molecular Representation Learning.* arXiv:2508.06199, 2025. ✔ — **25 modèles × 25 jeux de données ; aucune amélioration significative sur la baseline ECFP, à l'exception de CLAMP qui repose lui-même sur des empreintes.** |
| 2.8.1 | SHAP | Lundberg SM, Lee SI. *A Unified Approach to Interpreting Model Predictions.* NeurIPS 2017. ⚠ référence à vérifier avant insertion |
| 2.8.3 | « *les poids d'attention ne doivent pas être interprétés comme une preuve de causalité* » | Jain S, Wallace BC. *Attention is not Explanation.* NAACL-HLT 2019:3543-3556. DOI: `10.18653/v1/N19-1357` ✔ (BibTeX lu sur l'ACL Anthology) |

---

## 4. LITTÉRATURE MANQUANTE QUI MENACE OU RENFORCE LE VERROU

### ① Le risque le plus sérieux du chapitre — DL-ADR (2016)

```
Liang Z, Huang JX, Zeng X, Zhang G.
DL-ADR: a novel deep learning model for classifying genomic variants into
adverse drug reactions.
BMC Med Genomics. 2016;9(Suppl 2):48. DOI: 10.1186/s12920-016-0207-4   ✔ CONFIRMÉ
```

J'ai lu l'article. Ce qu'il fait :

- **Entrées :** 15 variables codant les combinaisons alléliques diploïdes de 5 SNP sur **CYP2D6 (\*2, \*10, \*14)** et **CYP1A2 (\*1C, \*1F)**, plus la dose.
- **Sortie :** prédiction ordinale sur **14 catégories d'effets indésirables**, de −2 à +2.
- **Architecture :** generative stochastic network avec stacked denoising autoencoder.
- **Résultat :** > 80 % d'exactitude, supérieur à LASSO et k-NN sur les 14 catégories.

Donc : **génotype pharmacogénétique germinal + Deep Learning + sortie clinique catégorielle, publié en 2016.**

Ta revendication au § 2.9.2 — « *nous n'avons pas identifié de travail combinant explicitement les trois éléments* » — **survit**, parce que DL-ADR n'a pas de représentation moléculaire du médicament : il a la dose, dans un contexte mono-médicament. Le troisième élément manque réellement.

**Mais elle ne survit que si le chapitre le dit lui-même.** Si un membre du jury connaît ce papier et que le chapitre 2 ne le mentionne pas, la formule « à notre connaissance » s'effondre et toute la section 2.9 devient suspecte. À l'inverse, citer DL-ADR puis montrer précisément ce qui l'en distingue **renforce** la revendication : cela prouve que la recherche bibliographique a été faite.

**À insérer en 2.4 ou 2.5, avec cette articulation :** le travail le plus proche en pharmacogénomique germinale profonde date de 2016, porte sur deux gènes et cinq SNP, et représente le médicament par sa seule dose ; PharmaGeno étend l'entrée génétique à 31 gènes et remplace la dose par une représentation structurale, ce qui ouvre la question de la généralisation à des molécules non vues — question que DL-ADR ne pouvait pas poser.

### ② DGANet (2025) — structure chimique + information génique, à distinguer

```
He M, Shi Y, Han F, Cai Y.
Prediction of adverse drug reactions based on pharmacogenomics combination
features: a preliminary study.
Front Pharmacol. 2025;16:1448106. DOI: 10.3389/fphar.2025.1448106   ✔ CONFIRMÉ
```

Combine structure chimique, expression génique, interactions chimique–gène et associations gène–maladie dans un CNN ; 453 médicaments, 1 091 effets indésirables, 23 395 paires ; AUROC 92,76 %.

**Distinction à écrire explicitement :** DGANet prédit une **association médicament–effet indésirable au niveau du médicament**, à partir de caractéristiques agrégées. PharmaGeno prédit une **action de prescription pour un patient donné**, à partir de son profil pharmacogénomique individuel. Ce n'est pas la même unité statistique. Sans cette phrase, le chapitre laisse une faille.

### ③ Les LLM — section absente

```
Zack M, Slobodchikov I, Stupichev D, et al.
Benchmarking large language models for replication of guideline-based
PGx recommendations.
Pharmacogenomics J. 2025;25:23. DOI: 10.1038/s41397-025-00383-0   ✔ CONFIRMÉ
```

Score de 0,92 pour un modèle adapté au domaine ; les modèles généralistes « *produisent fréquemment des sorties incomplètes ou dangereuses* ».

Le § 2.4 ne contient **aucune** sous-section sur les LLM. C'est le paradigme concurrent actuel ; son absence fait paraître l'état de l'art daté. Et l'argument te sert : ces systèmes **répliquent** une recommandation existante ; ils n'apprennent pas une décision à partir d'un génotype et d'une structure moléculaire. C'est exactement ta frontière.

### ④ La référence stratégiquement la plus utile de tout le mémoire

```
Kebir S, Cappello G, Oster C, Schmidt T, Grieger J, Jekel L, et al.
Machine learning models for adverse drug reaction prediction. A systematic
review and three-level multilevel meta-analysis.
Front Pharmacol. 2026;17:1906920. DOI: 10.3389/fphar.2026.1906920   ✔ CONFIRMÉ
```

Revue systématique PRISMA 2020 avec dépistage PROBAST, 11 études éligibles, 9 quantitatives, 30 estimations de performance, méta-régression multiniveau à trois niveaux par maximum de vraisemblance restreint. AUC agrégée **0,841 (IC 95 % 0,789–0,883)**.

**Conclusion de l'article : les réseaux de neurones ne surpassent pas significativement les algorithmes traditionnels une fois la dépendance intra-étude prise en compte.** L'article ajoute que le bénéfice supposé des descripteurs de cibles protéiques disparaît après contrôle de la domination par une étude unique — « *une annotation biologique plus riche* » peut introduire du bruit plutôt que du signal.

**Pourquoi c'est décisif pour toi.** Ton résultat actuel est que XGBoost dépasse ton modèle profond (macro-F1 0,955 vs 0,885 ; CER strict 4,35 % vs 7,68 %). Sans cette référence, ce résultat se lit comme un échec de ton architecture. Avec elle, il se lit comme **un résultat cohérent avec l'état méta-analytique de la littérature sur données pharmacogénomiques structurées**. Ce n'est pas une excuse : c'est un cadrage scientifiquement exact, et c'est la différence entre un chapitre 7 défensif et un chapitre 7 qui affirme une contribution.

À placer en 2.4.3, puis à rappeler en 2.9.3 (où le chapitre invoque déjà Kidwai-Khan pour le même argument — Kebir est beaucoup plus fort, car c'est une méta-analyse et non une étude unique), et à mobiliser en chapitre 7.

### ⑤ Le précédent méthodologique de tes propres données — absent

```
Sherman CA, Claw KG, Lee S.
Pharmacogenetic analysis of structural variation in the 1000 genomes project
using whole genome sequences.
Sci Rep. 2024;14:22774. DOI: 10.1038/s41598-024-73748-3   ✔ CONFIRMÉ
```

Ce que fait cet article : **PyPGx appliqué aux 2 504 individus non apparentés du 1000 Genomes haute couverture**, 26 sous-populations, **58 pharmacogènes**, 538 allèles étoile uniques, 53 allèles porteurs de variations structurales retrouvés dans **22,9 % des diplotypes**, 210 variants cliniquement pertinents hors nomenclature, et — **98,2 % des individus présentent au moins un phénotype de réponse médicamenteuse atypique.**

C'est **exactement ta source de données et exactement ton outil**, dans une publication revue par les pairs, par le groupe de S. Lee (auteur de Stargazer et de PyPGx). Son absence est une lacune majeure : elle prive le chapitre de son précédent méthodologique le plus direct.

Et le chiffre de **98,2 %** est l'argument empirique dont manque ton § 2.9.2.1 : si presque tout individu porte au moins un phénotype atypique, une représentation mono-gène est insuffisante par construction, et ce n'est plus toi qui l'affirmes — c'est mesuré sur la cohorte que tu utilises.

---

## 5. FAIBLESSES DE FOND (au-delà du référencement)

**① Le verrou a perdu ses chiffres.** La version précédente ancrait le § 2.9.2 sur les mesures de ton propre audit : **186 des 530 médicaments pour lesquels aucun gène unique ne détermine l'action à lui seul**, et **164 médicaments couverts par CPIC sur 530 dans le corpus**. Cette version les a supprimés, ce qui rend 2.9.2.1 et 2.9.2.3 abstraits. Ces nombres viennent de tes données ; ce sont tes arguments les plus solides, ils ne sont réfutables par personne d'autre. **Remets-les.**

**② Aucune section sur l'asymétrie des erreurs.** Le mémoire utilise une Cross-Entropy pondérée et mesure un CER strict (= 1 − rappel(EVITER)). En décision clinique, manquer un EVITER et manquer un STANDARD ne sont pas des erreurs de même nature. C'est un sujet d'état de l'art à part entière (coût asymétrique, apprentissage sensible au coût, seuils de décision cliniques). En l'absence de cette section, la métrique CER du chapitre 6 arrivera **sans justification bibliographique** et le jury demandera pourquoi elle a été inventée. Il faut une sous-section 2.8.4 ou 2.4.4.

**③ Les niveaux de preuve ne sont jamais nommés.** Le § 2.2.1 dit « *les niveaux les plus élevés* » sans écrire 1A, 1B, 2A, 2B, 3, 4, et le § 2.2.2 parle du « niveau A » de CPIC sans mentionner B, C, D. Or ton corpus a été construit sur « PharmGKB 1A/2A » et « CPIC niveau A ». Un lecteur doit pouvoir relier le chapitre 2 au chapitre 3 sans deviner. Nomme-les.

**④ Rien sur les matériaux de référence pour la validation.** Le projet prévoit de tester l'application sur un cas réel documenté (échantillons GeT-RM). Le § 2.3 est l'endroit naturel pour introduire la notion de matériau de référence pharmacogénomique. Sans cela, le chapitre de validation surgira sans fondement méthodologique.

**⑤ Déséquilibre structurel.** Le § 2.4.2 fait trois phrases, sans aucune citation, et décrit la détection ML de variations structurales **sans nommer PyPGx**, alors que PyPGx est décrit deux pages plus haut. Fusionne-le dans 2.3.2. À l'inverse, le § 2.7 n'a pas de sous-sections alors que toutes les autres en ont.

**⑥ Pas de titre de chapitre.** Le document commence directement par « 2.1 Fondements… ». Il manque l'en-tête « CHAPITRE 2 — ÉTAT DE L'ART ET VERROUS SCIENTIFIQUES », ce qui crée une incohérence avec le chapitre 1.

**⑦ Format bibliographique incohérent.** [1] et [3] sont des URL sans date de consultation ; [7] porte un PMCID seul ; [8] un PMID seul et une année ambiguë ; les autres un DOI. Un seul format pour tout le mémoire.

---

## 6. CE QU'IL FAUT FAIRE, DANS CET ORDRE

1. **Corriger les deux erreurs factuelles** : « 61 modèles » → « 61 publications » (§ 2.5.1) ; référence [8] DeepCDR → `2020;36(Supplement_2):i911-i918, DOI 10.1093/bioinformatics/btaa822`.
2. **Vérifier toi-même le « 34 gènes / 164 médicaments »** dans l'article Caudle 2025, et lui adjoindre `cpicpgx.org/genes-drugs/` avec date de consultation.
3. **Corriger [1]** (domaine `pharmcat.clinpgx.org`, + date de consultation), **compléter [7]** (volume, pages, DOI), **élever [3]** (ajouter Byrska-Bishop 2022), **compléter [4]** (auteurs).
4. **Vérifier les 4 éléments marqués ⚠** : pages de HiDRA, volume/pages de Relling & Klein 2011, de Whirl-Carrillo 2021, de Rogers & Hahn 2010, DOI de ClinVar, et la référence NeurIPS de SHAP.
5. **Insérer les 14 références de la section 3** — priorité absolue sur § 2.6 et § 2.8, qui n'en ont aucune.
6. **Insérer DL-ADR (2016) et écrire explicitement la distinction.** C'est le point qui protège la revendication de nouveauté.
7. **Insérer DGANet (2025), Zack et al. (2025), Kebir et al. (2026), Sherman et al. (2024).**
8. **Remettre les chiffres du corpus** (186/530, 164/530) dans le § 2.9.2.
9. **Ajouter la sous-section sur l'asymétrie des erreurs cliniques.**
10. **Nommer les niveaux de preuve** (1A–4, A–D) aux § 2.2.1 et 2.2.2.
11. Ajouter le titre de chapitre, fusionner 2.4.2 dans 2.3.2, uniformiser le format bibliographique.

Après ces onze points, le chapitre passera de 9 à environ 28–30 références, ce qui est le minimum acceptable pour un état de l'art de M.Sc. Les points 1 à 4 sont des corrections d'erreurs : ils ne sont pas négociables. Les points 5 à 7 décident de la solidité du verrou en soutenance.

---

## 7. SAUVEGARDE / ÉTAT D'AVANCEMENT

**Acquis de cette session**
- Chapitre 2 existe en deux versions : la mienne (`chapitre_2.md`, 9 sections, sans citations) et la version retravaillée (`Chapitre_2_Etat_de_l_art_PharmaGeno_FINAL.docx`, 9 sections, 9 références). **La version retravaillée est la base à conserver** : son traitement de PAnno et sa formulation du verrou sont plus défendables.
- 9 références du chapitre vérifiées une par une : 3 confirmées exactes ([4] [5] [6]-référence), 1 affirmation correcte mais URL morte ([1]), 1 article réel mais chiffre non vérifié ([2]), 1 source à élever ([3]), 2 défectueuses ([7] [8]), 1 partiellement confirmée ([9]).
- 2 erreurs factuelles identifiées : « 61 modèles » au lieu de « 61 publications » ; DeepCDR daté « 2020/2021 ».
- 14 références vérifiées rassemblées pour les sections sans sources (§ 2.1.2, 2.1.3, 2.2.1–2.2.4, 2.3.2, 2.6, 2.8).
- 5 publications manquantes identifiées et vérifiées, dont **DL-ADR 2016** (menace la revendication de nouveauté si non citée), **Kebir 2026** (méta-analyse : les réseaux de neurones ne surpassent pas significativement les méthodes classiques — cadre ton propre résultat XGBoost > DL) et **Sherman 2024** (PyPGx sur ta cohorte exacte ; 98,2 % des individus ont ≥ 1 phénotype atypique).

**Décisions validées**
- Le verrou reste formulé comme la conjonction de trois éléments, pas comme une absence de système de décision.
- Le choix Morgan 512 bits + 6 descripteurs est maintenu comme baseline structurale contrôlable, désormais appuyé sur Praski et al. 2025 (25 modèles × 25 jeux de données).
- Le résultat XGBoost > DL sera cadré par Kebir et al. 2026 et non présenté comme un échec.

**Erreurs à ne plus reproduire**
- Ne jamais écrire un nombre de gènes/médicaments couverts par une guideline sans date de consultation : ces dénombrements évoluent.
- Ne jamais écrire « X modèles » quand la source écrit « X publications ».
- Ne jamais laisser une année ambiguë (« 2020/2021 ») dans une bibliographie.
- Ne pas citer un portail de données quand un article revu par les pairs existe pour le même fait.
- Ne pas rédiger une section d'état de l'art sans aucune citation (§ 2.6 et § 2.8 l'étaient).

**En suspens**
- Vérifications ⚠ à faire par consultation directe : chiffre Caudle 2025, pages HiDRA, volume/pages Relling & Klein 2011, Whirl-Carrillo 2021, Rogers & Hahn 2010, DOI ClinVar, référence NeurIPS SHAP.
- Insertion des 19 références (14 + 5) dans le chapitre.
- Sous-section sur l'asymétrie des erreurs cliniques à rédiger.
- Entraînement `train_neg.py` : état à vérifier (`pgrep -f train_neg.py >/dev/null && echo "EN COURS" || echo "TERMINE"`), puis lancement de `train_final.py`.
- Expériences non lancées : mono-gène vs multi-gène (RQ1), ablation attention (RQ3), leave-one-drug-out (RQ5), SHAP + concordance CPIC (RQ6).
- Application Flask : règle écrite à la main `app.py:61` à retirer ; `predict_v2.py` à basculer sur le profil complet ; modèles `*_31genes` (v1, avec fuite) à remplacer.
- Test de l'application sur un cas réel documenté (GeT-RM) : **toujours en attente**.
- Chapitres 3 à 8 à rédiger ; figure 1.1 à insérer dans le document du chapitre 1.
