# Rapport technique d'avancement — PharmaGeno

**Période couverte** : 26 septembre — 4 octobre 2026
**Projet** : A Deep Learning based Webtool for Mutation-Aware Drug Recommendation
**M.Sc. Bioinformatique — ENSI Tunisie** · Encadrant : Pr. Kais Ghedira · Soutenance décembre 2026
**Dépôt** : github.com/benaichamouna-byte/PharmaGeno — commit `a322da6`

---

## Table des matières

1. [Vue d'ensemble de la période](#1-vue-densemble-de-la-période)
2. [Validation croisée — achèvement du protocole non groupé](#2-validation-croisée--achèvement-du-protocole-non-groupé)
3. [Métriques complètes et Critical Error Rate](#3-métriques-complètes-et-critical-error-rate)
4. [Reconstruction des identifiants d'individu](#4-reconstruction-des-identifiants-dindividu)
5. [Validation croisée groupée par individu](#5-validation-croisée-groupée-par-individu)
6. [Documentation du corpus](#6-documentation-du-corpus)
7. [Rédaction du chapitre 1](#7-rédaction-du-chapitre-1)
8. [Critiques méthodologiques reçues et leur résolution](#8-critiques-méthodologiques-reçues-et-leur-résolution)
9. [Points ouverts et travaux restants](#9-points-ouverts-et-travaux-restants)
10. [Inventaire des livrables](#10-inventaire-des-livrables)

---

## 1. Vue d'ensemble de la période

La période a été consacrée à l'achèvement et à la fiabilisation de la Phase 3 — la validation des modèles — ainsi qu'à la documentation rétrospective du corpus, qui relevait des Phases 1 et 2 du plan.

Trois résultats structurent la période.

**La validation croisée est complète pour les trois modèles.** XGBoost, Random Forest et le réseau profond ont été évalués sur cinq plis sous un protocole corrigé, exempt de fuite par normalisation. Les scores sont établis et reproductibles.

**Le risque de fuite par répétition de profil a été mesuré, et non supposé.** Une critique méthodologique sérieuse portait sur l'absence de groupement : un même profil génétique pouvait figurer en entraînement et en test, apparié à des médicaments différents. La reconstruction des identifiants d'individu a permis de tester cette hypothèse directement. Les scores ne baissent pas sous groupement.

**Le corpus est désormais documenté ligne par ligne.** Couverture moléculaire, fiches par gène, audit des conflits de labels, provenance des identifiants : quatre documents produits, qui constituent les annexes du mémoire et répondent par avance aux questions attendues du jury.

---

## 2. Validation croisée — achèvement du protocole non groupé

### Le problème

Le protocole initial présentait un défaut identifié : le `StandardScaler` était ajusté sur l'ensemble du jeu de données **avant** la découpe en plis. Les statistiques de normalisation — moyenne et écart-type de chaque variable — incorporaient donc les données de test. C'est une fuite classique, qui gonfle artificiellement les performances rapportées.

Un second problème, pratique celui-là, bloquait l'exécution : l'entraînement en lot complet sur 46 117 lignes saturait les 7,6 Go de mémoire disponibles, et le processus était tué avant la fin.

### La méthode

Deux corrections ont été appliquées simultanément.

Le scaler est désormais ajusté **à l'intérieur de chaque pli**, sur le pli d'entraînement seul, puis appliqué au pli de test. Les statistiques de normalisation ne voient jamais les données d'évaluation.

L'entraînement du réseau profond passe par un `DataLoader` en mini-lots de 256 exemples, avec libération explicite de la mémoire entre les plis. La consommation est passée d'un pic saturant à un plateau stable autour de 2 Go.

Les trois modèles ont été entraînés séparément pour contenir la charge : XGBoost et le DL d'abord, Random Forest ensuite, dans un script dédié. Les hyperparamètres sont restés strictement identiques à ceux du protocole v1, afin que la comparaison entre versions reste valide.

### Les résultats

| Modèle | Macro-F1 v2 | Macro-F1 v1 (avec fuite) | Écart |
|---|---|---|---|
| XGBoost | 0,954 ± 0,006 | 0,962 ± 0,002 | −0,008 |
| Random Forest | 0,932 ± 0,007 | 0,940 ± 0,001 | −0,008 |
| Deep Learning | 0,899 ± 0,020 | 0,875 ± 0,011 | **+0,024** |

Détail par pli :

| Pli | XGBoost | Random Forest | DL |
|---|---|---|---|
| 1 | 0,954 | 0,922 | 0,902 |
| 2 | 0,945 | 0,933 | 0,923 |
| 3 | 0,959 | 0,934 | 0,918 |
| 4 | 0,951 | 0,929 | 0,872 |
| 5 | 0,962 | 0,942 | 0,879 |

### Ce que cela signifie

XGBoost et Random Forest perdent **exactement 0,008 chacun**. Cette coïncidence n'en est pas une : elle correspond à l'effet de la correction de fuite, identique pour deux modèles qui subissent le même prétraitement. C'est une vérification indirecte que la correction a bien l'effet attendu, et seulement lui.

Le réseau profond, lui, **gagne 0,024** malgré un protocole plus strict. L'explication tient à ce que le dataset v2 n'est pas seulement le v1 corrigé : il intègre cinq gènes supplémentaires issus des VCF 1000 Genomes — VKORC1, CYP4F2, G6PD, NAT2, IFNL3 — tous dotés d'une ligne directrice CPIC de niveau A. L'enrichissement bénéficie davantage au modèle profond, capable d'exploiter les relations entre gènes, qu'aux ensembles d'arbres.

### Difficultés rencontrées

Le processus a été interrompu trois fois — deux fois par épuisement mémoire, une fois par fermeture de session. Chaque interruption a coûté le pli en cours.

La réponse a été d'introduire une **écriture incrémentale des scores** : chaque pli est enregistré dans un fichier JSON dès son achèvement, et le script relit ce fichier au démarrage pour sauter les plis déjà calculés. Ce mécanisme a été systématisé pour tous les scripts longs, et il a servi dès la validation groupée.

---

## 3. Métriques complètes et Critical Error Rate

### Le problème

Le macro-F1 seul ne dit pas grand-chose à un jury. Interrogée sur « 0,899 de quoi, exactement », la réponse manquait. Plus grave : un macro-F1 traite toutes les erreurs comme équivalentes, alors qu'en contexte clinique elles ne le sont pas du tout.

Confondre STANDARD et ADAPTER_DOSE conduit à ajuster une dose sans nécessité — inconfort, pas danger. Confondre EVITER et STANDARD conduit à prescrire un médicament contre-indiqué en le présentant comme sûr. Les deux pèsent identiquement dans le F1.

### La méthode

Un script a réentraîné les trois modèles sur les cinq mêmes plis — mêmes graines, même découpe — en collectant cette fois toutes les prédictions hors pli, et non seulement le score agrégé. À partir de ces prédictions ont été calculés : précision, rappel et F1 par classe ; Balanced Accuracy ; matrices de confusion ; et une métrique de sécurité clinique.

**Critical Error Rate** — proportion des cas EVITER que le modèle ne signale pas comme tels.

Une première définition ne comptait que `EVITER → STANDARD` et `EVITER → SURVEILLER`. Une critique externe a fait observer qu'elle omettait `EVITER → ADAPTER_DOSE` : dans ce cas aussi le médicament contre-indiqué est prescrit, avec un simple ajustement posologique. La contre-indication est manquée.

Les deux définitions sont donc rapportées. Le **CER strict** vaut `1 − rappel(EVITER)`.

### Les résultats

| Modèle | Macro-F1 | Weighted-F1 | Balanced Acc. | CER | CER strict |
|---|---|---|---|---|---|
| XGBoost | 0,954 | 0,979 | 0,972 | 3,66 % | 4,35 % |
| Random Forest | 0,932 | 0,956 | 0,947 | 4,22 % | 7,20 % |
| Deep Learning | 0,880 | 0,930 | 0,948 | 5,71 % | 7,68 % |

Destination des cas EVITER mal classés :

| Modèle | → ADAPTER_DOSE | → SURVEILLER | → STANDARD | Total |
|---|---|---|---|---|
| XGBoost | 91 | 446 | 34 | 571 |
| Random Forest | 390 | 523 | 31 | 944 |
| Deep Learning | 258 | 623 | **126** | 1 007 |

Détail par classe :

**XGBoost**

| Classe | Précision | Rappel | F1 | Support |
|---|---|---|---|---|
| ADAPTER_DOSE | 0,995 | 0,987 | 0,991 | 23 454 |
| EVITER | 0,976 | 0,957 | 0,966 | 13 120 |
| STANDARD | 0,833 | 0,956 | 0,890 | 520 |
| SURVEILLER | 0,950 | 0,989 | 0,969 | 9 023 |

**Random Forest**

| Classe | Précision | Rappel | F1 | Support |
|---|---|---|---|---|
| ADAPTER_DOSE | 0,981 | 0,976 | 0,978 | 23 454 |
| EVITER | 0,936 | 0,928 | 0,932 | 13 120 |
| STANDARD | 0,828 | 0,935 | 0,878 | 520 |
| SURVEILLER | 0,931 | 0,948 | 0,939 | 9 023 |

**Deep Learning**

| Classe | Précision | Rappel | F1 | Support |
|---|---|---|---|---|
| ADAPTER_DOSE | 0,987 | 0,915 | 0,950 | 23 454 |
| EVITER | 0,896 | 0,923 | 0,909 | 13 120 |
| STANDARD | **0,593** | 0,981 | 0,739 | 520 |
| SURVEILLER | 0,878 | 0,971 | 0,922 | 9 023 |

### Ce que cela signifie

**Le classement est stable sous les deux définitions.** XGBoost présente le plus faible taux de contre-indications manquées, que l'on compte ou non les cas déviés vers ADAPTER_DOSE. La conclusion ne dépend donc pas d'un choix de définition — ce qui la rend défendable.

**La majorité des erreurs va vers SURVEILLER.** Un médicament contre-indiqué présenté comme « à utiliser avec précaution » déclenche tout de même une vigilance du prescripteur. C'est une erreur, mais la moins dangereuse des trois.

**STANDARD est l'erreur grave.** Le médicament y est présenté comme prescriptible sans réserve. Le réseau profond en commet 126, soit quatre fois plus que XGBoost (34) ou Random Forest (31). Cette faiblesse n'est pas qu'une affaire de métrique : elle a une traduction clinique directe.

**Random Forest se dégrade fortement sous la définition stricte** — de 4,22 % à 7,20 % — parce qu'il envoie 390 cas EVITER vers ADAPTER_DOSE. Sous la définition permissive il paraissait plus sûr que le DL ; sous la définition stricte, les deux sont au même niveau.

**La Balanced Accuracy masque le défaut du DL.** Elle vaut 0,948 pour le réseau profond et 0,947 pour Random Forest, alors que leurs macro-F1 diffèrent de cinq points. L'explication est arithmétique : la Balanced Accuracy est la moyenne des rappels et ignore entièrement la précision. Le DL obtient un rappel de 0,981 sur STANDARD — il identifie presque tous les vrais STANDARD — pour une précision de 0,593. Six de ses prédictions STANDARD sur dix sont fausses, et la Balanced Accuracy ne le voit pas.

**Conséquence adoptée** : le macro-F1 reste la métrique principale, la Balanced Accuracy est rapportée en secondaire avec cette explication, et le CER strict accompagne systématiquement le CER.

### La classe STANDARD — fragilité documentée

STANDARD comptait 628 lignes avant le filtrage des médicaments sans empreinte moléculaire, 520 après. Soit une perte de **17,2 %**, contre moins de 1 % pour les autres classes. La classe déjà la plus rare du corpus — 1,1 % des lignes — est celle qui a été la plus amputée. Ce fait est consigné dans la provenance du jeu de données.

---

## 4. Reconstruction des identifiants d'individu

### Le problème

Une critique méthodologique sérieuse a été formulée : le protocole de validation ne groupait pas les lignes par patient. Le corpus contient 3 666 profils génétiques distincts pour 46 117 lignes, soit environ 12,6 lignes par profil — une par médicament associé. Rien n'empêchait donc qu'un même vecteur de 31 phénotypes figure en entraînement, apparié à la warfarine, et en test, apparié au clopidogrel.

Si le modèle mémorise les profils plutôt que la règle, les scores sont optimistes.

Le problème pratique : le dataset final ne contenait **ni `sample_id` ni `family_id`**. Lors de la fusion des sources, ces colonnes avaient été supprimées pour ne conserver que les variables d'entrée et l'étiquette. Impossible de grouper sans identifiants.

### La méthode — première tentative, échec

La première approche consistait à reconstruire les profils depuis les sources primaires — `1kgp_pgx_combined.csv` et les génotypes extraits des VCF — puis à les apparier au dataset par correspondance exacte du vecteur de 31 valeurs.

**Taux d'appariement : 0,1 %.** Vingt-huit lignes sur 46 371.

La cause est structurelle : le dataset contient 3 666 profils distincts alors que les sources n'en fournissent que 2 504. Une partie des profils provient de l'ancien corpus documentaire — PharmGKB, CPIC, ClinVar, FDA — qui n'a jamais eu d'individus associés.

### La méthode — seconde tentative

Un fichier intermédiaire a été retrouvé : `phenotype_drug_dataset_1kg.csv`, la portion 1000 Genomes avant fusion, qui avait **conservé sa colonne `sample`** sur 37 117 lignes.

La clé d'appariement combine les 16 phénotypes géniques communs aux deux fichiers, le médicament et l'action. Cette combinaison s'avère quasi unique par individu.

Le rattachement familial utilise ensuite `1kGP_3202_pedigree.txt`. Un individu dont les parents sont renseignés partage leur identifiant de famille, de sorte qu'un trio parent-parent-enfant forme un seul groupe.

Les lignes non appariées — issues du corpus documentaire — reçoivent chacune un identifiant propre. Elles forment ainsi des groupes singletons, neutres vis-à-vis du groupement : elles ne sont ni exclues, ni source de fuite.

### Les résultats

| | Lignes | Part |
|---|---|---|
| Rattachées à un individu séquencé | 36 049 | 77,7 % |
| Issues du corpus documentaire | 10 322 | 22,3 % |

| | Valeur |
|---|---|
| Individus séquencés identifiés | 1 379 |
| Familles distinctes | 1 378 |
| Familles comptant plusieurs membres | 1 |
| **Individus apparentés** | **2 (0,1 %)** |
| Lignes concernées | 82 (0,2 %) |

Fichier produit : `phenotype_drug_dataset_FINAL.csv`
SHA256 : `9a933859545ebe15fbf858422db5d2b69516662f9aadc3a130f5104e3abb327a`

### Ce que cela signifie

**Le risque d'apparentement est négligeable et mesuré.** Deux individus apparentés sur 1 379. Ce résultat est cohérent avec la source : le travail de Sherman, Claw et Lee repose sur les 2 504 individus **non apparentés** de la phase 3 du 1000 Genomes. Les 608 individus avec parents renseignés appartiennent à l'extension haute couverture à 3 202 échantillons, dont très peu figurent dans notre corpus.

Le point important est méthodologique : **l'absence de risque n'a pas été supposée, elle a été mesurée.** C'est une différence substantielle devant un jury.

**Mais le vrai risque était ailleurs.** Avec 1 378 familles pour 1 379 individus, un groupement par famille serait presque identique à un groupement par individu. Le risque réel n'était pas l'apparentement mais la **répétition du même individu** sur plusieurs lignes, une par médicament. C'est ce que le `sample_id` reconstruit permet enfin de corriger.

---

## 5. Validation croisée groupée par individu

### Le problème

Vérifier si les scores tiennent lorsqu'aucun patient ne traverse la séparation entre entraînement et test.

### La méthode

`StratifiedGroupKFold` à cinq plis, groupé sur `sample_id`. Modèles, hyperparamètres et prétraitement strictement identiques à la validation précédente, pour que la seule différence soit le groupement.

Le script vérifie et affiche à chaque pli l'intersection des identifiants entre entraînement et test. Cette valeur doit être nulle.

Les scores sont écrits dans un fichier JSON dès qu'un pli s'achève, et les plis déjà calculés sont sautés au redémarrage.

### Les résultats — trois plis sur cinq au moment de la rédaction

| Pli | XGBoost | Random Forest | DL | Recouvrement |
|---|---|---|---|---|
| 1 | 0,9545 | 0,9358 | 0,8845 | 0 |
| 2 | 0,9616 | 0,9479 | 0,8900 | 0 |
| 3 | 0,9535 | 0,9380 | 0,8828 | 0 |
| **Moyenne** | **0,9565** | **0,9406** | **0,8858** | |

Comparaison avec le baseline non groupé :

| Modèle | Groupé par individu | Baseline non groupé | Écart |
|---|---|---|---|
| XGBoost | 0,9565 | 0,954 | +0,0025 |
| Random Forest | 0,9406 | 0,932 | +0,0086 |
| Deep Learning | 0,8858 | 0,880 | +0,0058 |

Le corpus compte 11 476 groupes : 1 379 individus séquencés et environ 10 000 lignes documentaires formant chacune son propre groupe.

### Ce que cela signifie

**Les scores ne baissent pas.** Les trois modèles sont même légèrement au-dessus du baseline. La fuite par répétition de profil, redoutée dans la critique, n'a pas d'effet mesurable.

Deux lectures sont possibles, et elles convergent vers la même conclusion pratique.

**Lecture favorable** — la fuite n'existait pas en pratique. Les scores du baseline étaient honnêtes, et la validation groupée les confirme.

**Lecture plus sobre** — le groupement par individu ne mord pas parce que la tâche dépend peu du patient. Si l'action est largement déterminée par la paire gène–médicament, avoir vu un profil particulier à l'entraînement n'apporte rien : le modèle apprend la règle, pas l'individu. L'absence de chute confirmerait alors la nature déterministe de la cible.

Dans les deux cas, **les chiffres rapportés sont solides**. Mais la seconde lecture renforce l'idée que le véritable test de généralisation est ailleurs : sur des molécules jamais vues. Cette expérience reste à mener.

---

## 6. Documentation du corpus

Quatre documents ont été produits. Ils relèvent des Phases 1 et 2 du plan et constituent les annexes du mémoire.

### 6.1 Couverture moléculaire — `drug_dictionary.csv`, `drug_coverage_report.md`

**Le problème.** Le corpus comptait « 93 médicaments sans empreinte de Morgan », consigné comme limitation sans analyse. Un jury demanderait naturellement de quoi il s'agit.

**La méthode.** Classification de chacun des 530 médicaments selon la nature de l'entrée, avec détection des formes salines et des métabolites.

**Les résultats.**

| Catégorie | Médicaments |
|---|---|
| Empreinte disponible | 437 |
| Petites molécules manquantes | 21 |
| Classes thérapeutiques | 20 |
| Métabolites | 20 |
| Biologiques | 13 |
| Combinaisons | 10 |
| Fragments de parsing | 8 |
| Forme galénique | 1 |

**Couverture réelle : 46 117 lignes sur 46 371, soit 99,5 %.**

**Ce que cela signifie.** Les 93 entrées ne forment pas une lacune homogène. Les classes thérapeutiques — « antidépresseurs », « inhibiteurs de la pompe à protons » — ne correspondent à aucune structure chimique unique : leur exclusion est méthodologiquement justifiée. Les biologiques — héparine, tocilizumab, vaccins — sortent du périmètre des empreintes de Morgan, conçues pour les petites molécules. Les métabolites sont des molécules chimiquement distinctes de leur molécule mère et ne doivent pas être fusionnées avec elle. Les fragments de parsing proviennent de virgules non protégées dans le fichier source — la 1,3,7-triméthylxanthine, c'est-à-dire la caféine, a été scindée en trois entrées.

Seules **21 petites molécules** constituent une lacune réelle, et leur structure est disponible sur PubChem.

**Formes salines** : 25 groupes où une molécule apparaît sous forme libre et sous forme saline — warfarine et warfarine sodique, par exemple. Leur fusion a été écartée à ce stade : elle modifierait les profils et invaliderait la validation croisée obtenue.

### 6.2 Fiches par gène — `gene_sheets.csv`, `gene_sheets.md` (Annexe A)

**La méthode.** Une fiche par gène, construite uniquement à partir des données vérifiables du projet. Ce qui n'était pas documenté est marqué comme tel, sans invention.

**Les résultats.**

| | Gènes |
|---|---|
| Panel total | 31 |
| Porteurs de variance | 24 |
| Colonnes constantes | 7 |

Colonnes constantes : ACE, ADRB2, CFTR, EGFR, MT-RNR1, MTHFR, SLC19A1.

Origine des phénotypes :

| Source | Gènes |
|---|---|
| Extraction directe des VCF 1000 Genomes | 12 |
| PyPGx — Sherman, Claw & Lee, *Sci Rep* 2024 | 15 |
| Corpus documentaire initial | 4 |

Chaque fiche porte le variant, sa position GRCh38, l'origine du phénotype, l'échelle numérique employée, les valeurs observées, les médicaments associés et les limites connues.

**Ce que cela signifie.** Le document établit une limite méthodologique importante : **les 31 colonnes ne partagent pas une échelle commune.** Trois natures coexistent.

Les *scores d'activité* — CYP2D6, CYP2C19, CYP2B6, CYP2C9, DPYD — somment les contributions fonctionnelles des deux allèles. Grandeur additive et ordonnée.

Les *phénotypes ordinaux* — TPMT, NUDT15, SLCO1B1, UGT1A1, ABCG2, CYP3A5 — catégorisent une fonction enzymatique ou de transport.

Les *codes de génotype SNP* — VKORC1, IFNL3, CYP4F2, G6PD, NAT2 — encodent le génotype à un locus unique. La valeur 0,5 y désigne un hétérozygote, **non une demi-activité**.

Une normalisation commune appliquée à l'ensemble suppose implicitement que ces échelles sont commensurables. Elles ne le sont pas. La limite est documentée ; sa correction exigerait un réentraînement complet.

Trois gènes présentent par ailleurs des limites de principe. CYP2D6 n'est pas appelable depuis un VCF de SNP et d'indels — variation structurale et nombre de copies — et son phénotype provient de PyPGx. HLA-A et HLA-B relèvent du typage HLA, non d'un schéma métaboliseur : les forcer dans l'échelle 0–1 est une erreur de catégorie, et ils sont quasi constants dans le corpus. EGFR porte des variants somatiques caractérisés dans le tissu tumoral, absents par construction d'un VCF germinal.

### 6.3 Audit des conflits — `conflict_audit.csv`, `conflict_audit_report.md`

**Le problème.** Le corpus croise PharmGKB, CPIC, DPWG, ClinVar et la FDA. Ces sources divergent sur certaines paires gène–médicament, produisant des étiquettes contradictoires. Un rapport de résolution existait, mais sa procédure n'était pas documentée.

**La méthode.** Consolidation des trois passes successives de résolution en un document unique traçant l'origine de chaque décision.

**Les résultats.**

| Passe | Méthode | Paires résolues |
|---|---|---|
| 1 | Recherche de ligne directrice CPIC par paire | 58 |
| 2 | Recherche élargie, sources multiples | 111 |
| 3 | Suppression des lignes invalides | 75 |

État final sur 309 paires auditées : 150 sans ligne directrice identifiée, 78 avec texte mais sans action extractible, 75 rendues cohérentes après nettoyage, **6 conflits persistants**. 174 lignes invalides supprimées au total.

**Les six conflits persistants.**

| Gène | Médicament | Actions | Justification clinique |
|---|---|---|---|
| CYP2D6 | tamoxifène | ADAPTER_DOSE, EVITER | Métaboliseur lent : alternative recommandée. Intermédiaire : surveillance ou dose ajustée |
| CYP2C19 | voriconazole | ADAPTER_DOSE, EVITER, SURVEILLER | Ultrarapide : risque d'échec thérapeutique. Lent : risque de toxicité. Actions opposées |
| CYP3A5 | tacrolimus | ADAPTER_DOSE, SURVEILLER | Expresseur : augmentation de dose requise. Non-expresseur : dose standard |
| CYP2C9 | fluvastatine | ADAPTER_DOSE, EVITER | Selon le degré de réduction d'activité |
| SLCO1B1 | fluvastatine | ADAPTER_DOSE, EVITER | Risque de myopathie variable selon le génotype |
| CYP2C19 | mavacamten | ADAPTER_DOSE, EVITER | Ligne directrice récente, recommandations variables |

**Ce que cela signifie.** Ces six cas ne sont pas des erreurs de données. **L'action clinique dépend du phénotype précis, non de la seule paire gène–médicament.** Une table de correspondance gène → action serait donc insuffisante par construction : la même paire appelle des actions différentes selon le patient.

C'est un argument direct en faveur de la formulation adoptée — apprendre une fonction `(profil génétique complet, médicament) → action` — et donc de l'architecture à deux branches.

### 6.4 Provenance des identifiants — `sample_family_report.md`

Document décrivant la méthode d'appariement, les taux obtenus, la structure familiale mesurée et la portée du groupement. Détaillé en section 4.

---

## 7. Rédaction du chapitre 1

### Le problème

Une première version du chapitre 1 avait été produite. Trois défauts l'affectaient.

**Le Deep Learning y était marginal.** Sur environ 2 500 mots, il occupait une seule section d'environ 350 mots. Le reste traitait de pharmacogénomique, de CPIC, de PharmCAT, de bases de données. Un lecteur en sortait avec l'impression d'un mémoire de pharmacogénomique clinique — alors que le titre annonce *A Deep Learning based Webtool*.

**Le terme « Deep Learning » n'apparaissait jamais.** Le texte disait « réseau de neurones profond », « modèle profond », « réseau à deux branches ». Le lien avec le titre n'était pas fait explicitement.

**Le mot « prédiction » était absent.** Le texte parlait de « recommandation », « conduite à tenir », « verdict ». Rien n'indiquait qu'il s'agit d'une prédiction apprise — un lecteur pouvait croire à un système de règles qui consulte des recommandations.

S'ajoutaient des erreurs factuelles : le chiffre de 186 médicaments mal interprété, une affirmation non vérifiée sur « six formats » de VCF, un renvoi au mauvais chapitre.

### La méthode

Restructuration complète. Le chapitre s'ouvre désormais sur l'objet du travail — ce que le système fait, pourquoi le Deep Learning, ce que voit le clinicien — et le contexte biologique vient ensuite, pour justifier.

Deux figures décrites : la chaîne de prédiction et l'architecture du réseau.

Le triplet **Deep Learning — prédiction — application web** apparaît dans chaque section clé.

### Le résultat

Neuf sections, 2 385 mots.

| Section | Contenu |
|---|---|
| 1.1 | PharmaGeno — ce que le système fait |
| 1.2 | Pourquoi le Deep Learning |
| 1.3 | L'application de prédiction : trois capacités |
| 1.4 | Contexte : variabilité génétique de la réponse |
| 1.5 | Le maillon manquant entre le VCF et la prescription |
| 1.6 | Problématique et question de recherche |
| 1.7 | Objectifs |
| 1.8 | Contributions |
| 1.9 | Organisation du mémoire |

Les sections 1.1 à 1.3 occupent environ 45 % du chapitre.

### Corrections factuelles appliquées

**Le chiffre 186/530 reformulé.** L'ancienne version affirmait que « l'action change selon la combinaison d'au moins deux gènes ». Ce n'est pas ce que mesure le test, qui vérifie seulement s'il existe un gène unique déterminant parfaitement l'action. La formulation retenue est : « aucun gène unique ne détermine l'action à lui seul ». La démonstration d'une interaction multi-gènes viendra de l'ablation.

**« Six formats » de VCF retiré** — affirmation non vérifiée.

**Renvoi corrigé** — les ablations sont au chapitre 5, non au chapitre 4.

**Méthode d'extraction HTTP déplacée.** Elle figurait parmi les contributions principales ; c'est une solution de contournement d'un problème d'environnement, non une contribution scientifique. Elle ira en méthodes.

**Contributions réordonnées** — le modèle en premier, l'application en second.

### Positionnement scientifique retenu

Le chapitre assume explicitement la nature de la cible : les étiquettes sont dérivées des règles CPIC, donc sur les paires couvertes la cible est une fonction déterministe des entrées. Les métriques mesurent d'abord une **fidélité d'implémentation**, non une performance prédictive sur une cohorte prospective.

Ce que le modèle ajoute réellement se situe ailleurs — composition de plusieurs gènes, extrapolation chimique vers des molécules non couvertes — et ces deux apports sont annoncés comme quantifiés au chapitre 5.

Cet aveu protège le travail : il vaut mieux l'énoncer soi-même que se le voir opposer.

---

## 8. Critiques méthodologiques reçues et leur résolution

Plusieurs critiques ont été formulées par un assistant externe. Chacune a été traitée. Voici leur statut.

### 8.1 Fuite par normalisation — CONFIRMÉE, CORRIGÉE

Le scaler était ajusté sur l'ensemble du dataset avant la découpe en plis. Correction appliquée : ajustement intra-pli. L'effet mesuré est de −0,008 sur XGBoost et Random Forest.

### 8.2 Absence de mini-lots — CONFIRMÉE, CORRIGÉE

L'entraînement en lot complet saturait la mémoire. `DataLoader` avec lots de 256 introduit, avec libération explicite entre les plis.

### 8.3 Fuite par répétition de profil — CONFIRMÉE, MESURÉE, SANS EFFET

Critique juste sur le principe : le protocole ne groupait pas par patient. La reconstruction des identifiants a permis de tester l'hypothèse. **Les scores ne baissent pas sous groupement** — ils augmentent même légèrement. La fuite n'avait pas d'effet mesurable.

### 8.4 Fuite par duplicats — ÉCARTÉE

Hypothèse : des lignes `(X → y)` identiques réparties entre plis. Test effectué : 46 371 lignes pour 46 371 combinaisons `X` uniques. **Aucun duplicat.**

### 8.5 Double correction du déséquilibre — ÉCARTÉE APRÈS VÉRIFICATION

Hypothèse : `RandomOverSampler` et `compute_class_weight` simultanément actifs, compensant deux fois la classe minoritaire — ce qui expliquerait la précision de 0,593 sur STANDARD.

Vérification du code : `train_dl` reçoit `Xb, yb`, les données **déjà rééchantillonnées**. Le `compute_class_weight('balanced')` calculé sur ces données équilibrées renvoie 1,0 pour les quatre classes. **La pondération est neutre.** L'hypothèse est fausse.

La cause de la faiblesse sur STANDARD reste à déterminer. Deux pistes : la duplication des 520 lignes 45 fois par l'oversampling, qui ferait mémoriser plutôt qu'apprendre ; ou la rareté intrinsèque de la classe — 520 exemples pour 549 variables d'entrée.

### 8.6 Critical Error Rate trop permissif — CONFIRMÉE, CORRIGÉE

La définition omettait `EVITER → ADAPTER_DOSE`. Les deux définitions sont désormais rapportées. Le classement des modèles est stable sous les deux.

### 8.7 Balanced Accuracy trompeuse — CONFIRMÉE, DOCUMENTÉE

Arithmétiquement vérifiée. Métrique reléguée au second rang avec explication.

### 8.8 Étiquetage trompeur du fichier de métriques — CONFIRMÉE, CORRIGÉE

`metriques_completes_v2.md` laissait croire à la validation finale alors que son protocole était non groupé. Renommé `metriques_baseline_non_groupe.md`, avec un avertissement en tête de document.

### 8.9 Axe molécule jamais tenu en dehors — CONFIRMÉE, NON TRAITÉE

Chaque médicament figure en entraînement et en test de chaque pli. Le protocole actuel mesure la généralisation patient, non la généralisation moléculaire.

**Cette critique est la plus importante et reste ouverte.** La revendication de thèse — le Deep Learning généralise aux molécules hors ligne directrice via les empreintes de Morgan — n'est pas testable sous le protocole actuel.

Un plan factoriel à trois blocs a été proposé : Bloc A, patients tenus dehors, molécules vues — c'est ce qui a été fait ; Bloc B, molécules tenues dehors par *leave-one-drug-out* ; Bloc C, les deux simultanément.

Le Bloc B est inscrit en Phase 4.

### 8.10 Hétérogénéité sémantique des colonnes — CONFIRMÉE, DOCUMENTÉE

Scores d'activité, phénotypes ordinaux et codes de génotype SNP empilés sur un même axe numérique, puis soumis à une normalisation commune. La limite est documentée dans les fiches par gène. Sa correction exigerait un réentraînement complet.

### 8.11 Reformulation de l'évaluation de GeneAttention — ACCEPTÉE

Si la cible est largement déterministe, une ablation comparant des F1 ne montrera rien, et l'absence de différence serait interprétée à tort comme une absence d'apport.

Reformulation retenue : mesurer si les poids d'attention retrouvent la **bonne attribution gène → médicament**. Pour chaque médicament, CPIC désigne un ou deux gènes ; on mesure si l'attention se concentre dessus. C'est une contribution d'interprétabilité mesurable, et non circulaire — l'attribution ne figure pas dans l'étiquette.

### 8.12 Observation sur le DL battu par le gradient boosting — ACCEPTÉE, NUANCÉE

Le constat est exact : XGBoost domine sur tous les critères, y compris la sécurité clinique.

La cause avancée — « mauvais biais inductif » du réseau dense — mérite une formulation plus précise. La cible, construite depuis des règles CPIC, est largement une **fonction par morceaux sur des variables discrètes**. Les ensembles d'arbres partitionnent nativement ce type d'espace ; un réseau dense doit l'approximer. L'avantage structurel des arbres est donc attendu, et c'est au chapitre 7 de l'expliquer plutôt que de le subir.

Deux terrains restent où le Deep Learning peut se défendre : les molécules jamais vues (Bloc B) et les 186 médicaments pour lesquels aucun gène unique ne détermine l'action. Les deux expériences sont à mener.

Si le Deep Learning perd aussi sur ces deux terrains, la conclusion scientifique correcte est que la tâche ne requiert pas d'apprentissage profond. C'est un résultat négatif publiable, à condition d'être annoncé et analysé, non subi.

---

## 9. Points ouverts et travaux restants

### En cours

Plis 4 et 5 de la validation croisée groupée. Environ trois heures.

### Phase 4 — études d'ablation

**Mono-gène contre multi-gènes.** Comparer un modèle recevant le seul gène concerné à un modèle recevant le profil complet, en se concentrant sur les 186 médicaments où aucun gène unique ne détermine l'action. C'est la réponse expérimentale à l'objection « pourquoi un modèle si CPIC énonce déjà des règles ».

**Ablation de GeneAttention**, évaluée sur la récupération de l'attribution gène → médicament plutôt que sur le F1.

**Apport des empreintes de Morgan.** Quatre configurations : gènes seuls ; gènes et descripteurs ; gènes et empreintes ; gènes, empreintes et descripteurs.

**Leave-one-drug-out.** Chaque médicament entièrement en entraînement ou entièrement en test. C'est l'expérience décisive pour justifier le Deep Learning : XGBoost mémorise probablement l'identité moléculaire et devrait s'effondrer. Une chute marquée des performances est attendue, et cette chute **est le résultat scientifique** — elle quantifie la part de mémorisation dans les scores actuels.

### Phase 5 — explicabilité et validation clinique

SHAP pour XGBoost. Visualisation des poids d'attention. Confrontation à 20–50 cas de référence CPIC, avec calcul d'une concordance clinique. Comparaison chiffrée avec PharmCAT.

### Phase 6 — application et rédaction

Terminologie clinique dans l'interface : *contre-indiqué*, *ajuster la dose*, *utiliser avec précaution*, *prescrivable normalement*. Modification de l'affichage uniquement — les étiquettes du jeu de données restent inchangées, sous peine de devoir réentraîner.

Correction du bug mirtazapine : la prédiction est aujourd'hui limitée aux médicaments d'un mappage manuel ; une molécule absente retourne « aucune donnée » alors que le modèle pourrait la traiter.

Correction du message « aucune mutation détectée → doses standard applicables pour tous les médicaments », cliniquement faux. Formulation correcte : « aucun variant pharmacogénomique pertinent parmi les positions couvertes par l'analyse ».

R�daction des chapitres 2 à 8.

### Diagnostics en attente

**Cause de la faiblesse sur STANDARD.** Entraîner le réseau sans rééchantillonnage, avec pondération réelle calculée sur les données brutes. Si la précision remonte, la duplication était en cause ; sinon c'est la rareté de la classe.

Attention au périmètre : ce test est un diagnostic, non une comparaison. Modifier le prétraitement du seul Deep Learning invaliderait le tableau comparatif. Deux issues honnêtes — documenter le constat en discussion sans toucher au tableau, ou optimiser le prétraitement des trois modèles séparément et comparer chacun dans sa meilleure configuration. La seconde coûte environ quinze heures de calcul.

**Point de rédaction.** Signaler les 7 colonnes constantes dès le chapitre 1, ou réserver cette précision au chapitre 3 où l'audit est détaillé.

---

## 10. Inventaire des livrables

### Données

| Fichier | Contenu |
|---|---|
| `phenotype_drug_dataset_FINAL.csv` | 46 371 lignes, 31 gènes, `sample_id`, `family_id` |
| `phenotype_drug_dataset_complet_v2.csv` | Version précédente, sans identifiants |

### Résultats

| Fichier | Contenu |
|---|---|
| `metriques_baseline_non_groupe.md` | Métriques par classe, CER, CER strict |
| `metriques_completes_v2.json` | Valeurs brutes, matrices de confusion |
| `confusion_matrices_v2.png` | Figure trois modèles |
| `groupkfold_scores.json` | Scores de la validation groupée |
| `validation_groupee_pli1.xlsx` | Feuille de comparaison des protocoles |
| `HISTORIQUE_RESULTATS_COMPLET.md` | Document de référence, douze étapes |

### Documentation

| Fichier | Contenu |
|---|---|
| `gene_sheets.csv` / `.md` | Annexe A — fiches par gène |
| `drug_dictionary.csv` | Classification des 530 médicaments |
| `drug_coverage_report.md` | Analyse de la couverture moléculaire |
| `conflict_audit.csv` | Traçabilité des 309 paires en conflit |
| `conflict_audit_report.md` | Procédure et analyse des conflits |
| `sample_family_report.md` | Reconstruction des identifiants |
| `dataset_provenance.md` | Provenance du jeu de données |

### Scripts

| Fichier | Rôle |
|---|---|
| `train_dl_kfold_only.py` | Validation DL et XGBoost, plis 1 à 3 |
| `train_kfold_folds45.py` | Pli 4 et XGBoost pli 5 |
| `train_dl_fold5.py` | DL pli 5 |
| `train_rf_kfold_v2.py` | Random Forest, cinq plis |
| `metriques_completes_v2.py` | Métriques par classe et CER |
| `fix_metriques_report.py` | Réétiquetage et CER strict |
| `train_groupkfold.py` | Validation groupée par individu |
| `build_final_dataset.py` | Reconstruction des identifiants |
| `build_gene_sheets.py` | Fiches par gène |
| `build_drug_dictionary.py` | Dictionnaire des médicaments |
| `build_conflict_audit.py` | Audit des conflits |

### Mémoire

| Fichier | Contenu |
|---|---|
| `chapitre_1.md` | Introduction générale, 2 385 mots |

Tous les fichiers sont présents sur les trois supports : WSL, Windows (`C:\Users\MSI\Desktop\memoire\`) et Google Drive (`PharmaGeno_Memoire/`). Les modèles Random Forest, dépassant 100 Mo, sont exclus de GitHub et conservés sur Windows et Drive uniquement.
