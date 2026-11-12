# Règles corrigées — corpus v15

Étape 1 de la méthode validée le 11 novembre 2026 : écrire les règles corrigées à partir des textes officiels, pour validation avant tout calcul.

**Version du 12 novembre 2026 — décision voie A actée.**

Sources de tous les textes cités :
- `~/projet_memoire/data/guidelineAnnotations.json.zip` (annotations de directives ClinPGx) → trace dans `sources_v15/textes_regles_v15.md`
- `pharmcat-3.4.0-all.jar`, fichier interne `org/pharmgkb/pharmcat/reporter/prescribing_guidance.json` (356 directives, grilles par phénotype) → trace dans `sources_v15/grilles_pharmcat_v15.md`
- Mesures sur le corpus v14 → trace dans `sources_v15/mesure_cyp2c9.txt`

---

## 0. Trois signalements antérieurs retirés

### 0.1 « Incohérence TPMT lent entre les trois thiopurines » — RETIRÉ

CPIC différencie délibérément les trois médicaments. Textes exacts, grille PharmCAT, TPMT lent × NUDT15 normal :

| Médicament | Texte CPIC | Action juste |
| --- | --- | --- |
| azathioprine | « Consider alternative nonthiopurine immunosuppressant therapy. » | `EVITER` |
| mercaptopurine | « For malignancy: initiate therapy with drastically reduced starting doses. Reduce starting dose by 10-fold… For nonmalignancy: consider alternative nonthiopurine immunosuppressant therapy. » | `ADAPTER_DOSE` (branche malignité) |
| thioguanine | « Initiate therapy with drastically reduced starting doses. Reduce starting dose by 10-fold… » | `ADAPTER_DOSE` |

**Le corpus actuel est conforme.** Aucune correction.

À documenter : la mercaptopurine en métaboliseur lent dépend de l'indication (malignité ou non). Le webtool ne connaît pas l'indication ; la branche « malignité » est retenue, ce qui relève de la catégorie « dépend d'autre chose » déjà employée dans le corpus.

### 0.2 « G6PD sans effet sur ~50 médicaments » — RETIRÉ pour les lignes codées

PA166279741 est l'annotation des médicaments **à risque faible ou nul** : « There is no reason to avoid low-to-no risk drugs in patients with the G6PD deficient or G6PD variable phenotypes. » Les ~150 lignes `STANDARD` du corpus sont **correctes**. Le défaut réel porte sur des annotations absentes (règle 3).

### 0.3 « Phénytoïne affectée par le défaut CYP2C9 par allèle » — RETIRÉ

Vérification sur la table DPWG PA166104984 : pour la phénytoïne, le diplotype \*1/\*2 reçoit « use 75% of the standard dose » = `ADAPTER_DOSE`, et le métaboliseur normal « no recommendation » = `STANDARD`. **Le corpus est déjà juste pour la phénytoïne.** La correction ne concerne que la warfarine et le siponimod.

---

## 1. Warfarine × VKORC1 — règle à ajouter

**Source : PA166182841, DPWG, mise à jour novembre 2018, allèle lié rs9923231.**

| Génotype | Recommandation DPWG verbatim | Action |
| --- | --- | --- |
| VKORC1 -1639 AA (rs9923231 TT) | « 1. use 60% of the standard initial dose. The genotype-specific initial dose and maintenance dose can be calculated using an algorithm, as used in EU-PACT. From day 6 on the standard algorithm without genotype information can be used to calculate the dose. » | `ADAPTER_DOSE` |
| VKORC1 -1639 AG (rs9923231 CT) | « NO action is needed for this gene-drug interaction » | `STANDARD` |

### Lignes à écrire

| gene | valeur | medicament | action | phenotype | fichier |
| --- | --- | --- | --- | --- | --- |
| VKORC1 | 0.0 | warfarin | `ADAPTER_DOSE` | VKORC1 rs9923231 homozygote variant | PA166182841.json |
| VKORC1 | 0.5 | warfarin | `STANDARD` | VKORC1 rs9923231 hétérozygote | PA166182841.json |
| VKORC1 | 1.0 | warfarin | `STANDARD` | VKORC1 référence | PA166182841.json |

Codage identique à celui déjà employé pour VKORC1 (acénocoumarol, phenprocoumone, fluindione). Ligne 1.0 : génotype de référence non cité comme sous-groupe concerné → posologie générale, principe H-FDA-1 déjà en vigueur.

### Pourquoi CYP4F2 n'est pas ajouté

CYP4F2 n'intervient pour la warfarine que dans la directive CPIC PA166104949, qui prescrit une dose par algorithme multi-gènes dépendant de l'ascendance. La grille PharmCAT correspondante le confirme : ses clés sont de la forme « CYP2C9=Any Result + CYP4F2=Any Result + VKORC1=Any Result + rs12777823=Any Result », sans action par génotype. Elle ne se ramène pas aux quatre classes. Exclusion conforme au principe déjà documenté dans `construire_corpus_v7.py`.

Référence écartée : Johnson JA et al., *Clin Pharmacol Ther* 102(3):397-404, 2017. https://doi.org/10.1002/cpt.668

---

## 2. CYP2C9 selon DPWG — voie A retenue

### 2.1 Nature du défaut

DPWG définit ses recommandations **par diplotype nommé**. Le corpus encode CYP2C9 par un score d'activité normalisé. Certains diplotypes distincts partagent donc une même valeur alors que DPWG leur attribue des actions différentes.

Tables DPWG verbatim :

**Warfarine (PA166182842)**

| Diplotype | Score | Valeur corpus | Recommandation DPWG | Action |
| --- | --- | --- | --- | --- |
| \*1/\*2 | 1,5 | 0,75 | « NO action is required for this gene-drug interaction. » | `STANDARD` |
| \*1/\*3, \*2/\*2 | 1,0 | 0,50 | « use 65% of the standard initial dose » | `ADAPTER_DOSE` |
| \*2/\*3 | 0,5 | 0,25 | « use 45% of the standard initial dose » | `ADAPTER_DOSE` |
| \*3/\*3 | 0 | 0,00 | « use 20% of the standard initial dose » | `ADAPTER_DOSE` |
| IM other | 1,0–1,5 | 0,50–0,75 | « use 65% of the standard initial dose » | `ADAPTER_DOSE` |
| PM other | 0–0,5 | 0,00–0,25 | « use 20% of the standard initial dose » | `ADAPTER_DOSE` |

**Siponimod (PA166211021)**

| Diplotype | Valeur corpus | Recommandation DPWG | Action |
| --- | --- | --- | --- |
| \*1/\*2 | 0,75 | « NO action is required for this gene-drug interaction. » | `STANDARD` |
| \*2/\*2 | 0,50 | « NO action is required for this gene-drug interaction. » | `STANDARD` |
| \*1/\*3, IM other | 0,50–0,75 | « Use 50% of the normal maintenance dose. » | `ADAPTER_DOSE` |
| \*2/\*3 | 0,25 | « Use 50% of the normal maintenance dose. » | `ADAPTER_DOSE` |
| \*3/\*3, PM other | 0,00–0,25 | « Avoid siponimod. » | `EVITER` |

### 2.2 Décision : voie A, codage par score conservé

**Motifs.**

1. Le protocole de comparaison équitable, validé le 15 octobre 2026, et la validation externe sur 104 personnes portent sur un espace d'entrée donné. Corriger des étiquettes laisse cet espace intact ; changer l'encodage d'un gène modifie l'objet même que le protocole évalue.
2. Le score d'activité CYP2C9 est l'indexation employée par PharmCAT lui-même : les grilles fluvastatine et phénytoïne du fichier `prescribing_guidance.json` sont indexées par score (0.0, 0.5, 1.0, 1.5, 2.0), non par diplotype. Le choix du corpus est conforme à l'usage de l'outil de référence.
3. Le défaut porte sur 1 458 lignes (0,63 % du corpus v14) et, après correction, le résidu irréductible tombe à environ 0,06 %.

### 2.3 Principe de résolution des valeurs ambiguës

Quand une valeur recouvre plusieurs diplotypes aux actions différentes :

> **Retenir l'action du diplotype nommé le plus fréquent, sauf si cela conduit à abandonner `EVITER` — auquel cas l'action la plus sévère est conservée.**

Justification de l'asymétrie : les deux erreurs n'ont pas le même coût. Sur-avertir dégrade l'utilisabilité ; sous-avertir sur une contre-indication est une erreur clinique grave, précisément ce que mesure le *Critical Error Rate* retenu dans le protocole. Une fonction de coût asymétrique appelle une règle de décision asymétrique.

### 2.4 Lignes à modifier et à ajouter

**Warfarine × CYP2C9**

| valeur | corpus actuel | corrigé | motif |
| --- | --- | --- | --- |
| 0,00 | `ADAPTER_DOSE` | inchangé | \*3/\*3 et PM other → 20 % |
| 0,25 | `ADAPTER_DOSE` | inchangé | \*2/\*3 → 45 % |
| 0,50 | `ADAPTER_DOSE` | inchangé | \*1/\*3 et \*2/\*2 → 65 %, pas de conflit |
| **0,75** | `ADAPTER_DOSE` | **`STANDARD`** | \*1/\*2 → NO action — **218 lignes** |
| **1,00** | **absente** | **`STANDARD` à ajouter** | métaboliseur normal, non cité |

**Siponimod × CYP2C9**

| valeur | corpus actuel | corrigé | motif |
| --- | --- | --- | --- |
| 0,00 | `EVITER` | inchangé | \*3/\*3 et PM other → Avoid |
| 0,25 | `EVITER` | **inchangé** | \*2/\*3 → 50 % serait `ADAPTER_DOSE`, mais PM other → Avoid : désescalade depuis `EVITER` refusée par le principe du § 2.3 |
| 0,50 | `ADAPTER_DOSE` | inchangé | \*1/\*3 majoritaire ; \*2/\*2 (`STANDARD`) minoritaire |
| **0,75** | `ADAPTER_DOSE` | **`STANDARD`** | \*1/\*2 → NO action — **218 lignes** |
| **1,00** | **absente** | **`STANDARD` à ajouter** | métaboliseur normal |

**Phénytoïne × CYP2C9 : aucun changement** (voir § 0.3).

### 2.5 Limite à écrire dans le mémoire

> Le codage de CYP2C9 par score d'activité confond des diplotypes auxquels la DPWG attribue des actions différentes : à la valeur 0,50 pour le siponimod, \*1/\*3 (« Use 50% of the normal maintenance dose ») et \*2/\*2 (« NO action is required ») partagent la même entrée. Aucun modèle ne peut les séparer : il s'agit d'une erreur irréductible introduite par la représentation, non d'un défaut d'apprentissage. Elle concerne 146 lignes sur 232 664, soit 0,06 % du corpus, sur un seul médicament. La levée de cette limite suppose de porter le diplotype dans la variable plutôt que le score d'activité, ce qui modifie l'espace d'entrée des modèles et impose de rejouer l'ensemble du protocole d'évaluation ; cette voie est identifiée comme perspective.

---

## 3. G6PD — trois annotations à ajouter

Six annotations CPIC couvrent G6PD ; une seule est codée.

| Annotation | Médicaments | Statut |
| --- | --- | --- |
| PA166279741 | 24 médicaments à risque faible ou nul | codée, correcte |
| **PA166119846** | dapsone, bleu de méthylène, pegloticase, rasburicase, tafénoquine, bleu de toluidine | **à ajouter** |
| **PA166279621** | primaquine | **à ajouter** |
| **PA166279721** | nitrofurantoïne | **à ajouter** |
| PA166279481 | chlorpropamide, dabrafénib, gliclazide, glimépiride, glipizide, mépacrine, mésalazine, moxifloxacine, nicorandil, nitrofural, probénécide, nitrate de sodium, sulfacétamide, tolazamide, tramétinib | sans recommandation → ajout facultatif en `STANDARD` |
| PA166279561 | aspirine | sans recommandation → ajout facultatif en `STANDARD` |

### 3.1 Grilles vérifiées, textes CPIC verbatim

**PA166119846 — six médicaments à risque élevé**

| Phénotype CPIC | Texte verbatim | valeur corpus | action |
| --- | --- | --- | --- |
| Normal | « No reason to avoid based on G6PD status » | 1.0 | `STANDARD` |
| Deficient | « Avoid use » | 0.0 | `EVITER` |
| Deficient with CNSHA | « Avoid use » | — | `EVITER` |
| Variable / Indeterminate | « To ascertain G6PD status, enzyme activity must be measured. Drug use should be guided per the recommendations based on the activity-based phenotype. » | 0.5 | voir § 3.2 |

**PA166279621 — primaquine**

| Phénotype | Texte verbatim | valeur | action |
| --- | --- | --- | --- |
| Normal | « No reason to avoid based on G6PD status » | 1.0 | `STANDARD` |
| Deficient | « Avoid primaquine, except in the following cases where established expert consensus guidelines… » | 0.0 | `EVITER` |
| Deficient with CNSHA | « Avoid primaquine » | — | `EVITER` |
| Variable / Indeterminate | test enzymatique | 0.5 | voir § 3.2 |

**PA166279721 — nitrofurantoïne**

| Phénotype | Texte verbatim | valeur | action |
| --- | --- | --- | --- |
| Normal | « No reason to avoid based on G6PD status » | 1.0 | `STANDARD` |
| Deficient | « Use at standard doses with caution and with close monitoring for anemia » | 0.0 | `SURVEILLER` |
| Deficient with CNSHA | « Avoid » | — | `EVITER`, non dérivable (§ 3.2) |
| Variable / Indeterminate | test enzymatique | 0.5 | voir § 3.2 |

### 3.2 Deux points de conception

**Phénotype « variable » (valeur 0,5).** CPIC n'y prescrit pas une action mais un examen : « enzyme activity must be measured ». Ce n'est aucune des quatre classes. Proposition : `SURVEILLER`, avec le texte du test enzymatique affiché tel quel dans la recommandation. À valider.

**CNSHA.** Trois annotations distinguent le patient déficient avec anémie hémolytique chronique non sphérocytaire. Cette distinction est clinique, pas génotypique : elle n'est pas dérivable d'un VCF. Elle est sans effet pour les six médicaments à risque élevé et la primaquine (`EVITER` dans les deux cas), mais décisive pour la nitrofurantoïne : `SURVEILLER` sans CNSHA, `EVITER` avec. Proposition : retenir le cas sans CNSHA, qui est le cas général, et porter la réserve dans le texte affiché. À valider et à écrire comme limite.

Le gène étant porté par le chromosome X, le traitement haploïde décidé en phase 1 reste applicable.

---

## 4. Thiopurines — grille bi-génique TPMT × NUDT15

**Sources : PA166104933 (azathioprine), PA166104945 (mercaptopurine), PA166104965 (thioguanine), CPIC, mise à jour 2025.**

Chaque directive porte 35 combinaisons dans PharmCAT. Restreintes aux trois phénotypes que le corpus code (normal, intermédiaire, lent), elles donnent 9 cellules par médicament :

| TPMT | NUDT15 | azathioprine | mercaptopurine | thioguanine |
| --- | --- | --- | --- | --- |
| normal | normal | `STANDARD` | `STANDARD` | `STANDARD` |
| normal | intermédiaire | `ADAPTER_DOSE` | `ADAPTER_DOSE` | `ADAPTER_DOSE` |
| normal | lent | `EVITER` | `EVITER` | `ADAPTER_DOSE` |
| intermédiaire | normal | `ADAPTER_DOSE` | `ADAPTER_DOSE` | `ADAPTER_DOSE` |
| intermédiaire | intermédiaire | `ADAPTER_DOSE` | `ADAPTER_DOSE` | `ADAPTER_DOSE` |
| intermédiaire | lent | `EVITER` | `EVITER` | `ADAPTER_DOSE` |
| lent | normal | `EVITER` | `EVITER` | `ADAPTER_DOSE` |
| lent | intermédiaire | `EVITER` | `EVITER` | `ADAPTER_DOSE` |
| lent | lent | `EVITER` | `EVITER` | `ADAPTER_DOSE` |

Codage : TPMT et NUDT15 à 0.0 (lent), 0.5 (intermédiaire), 1.0 (normal). 27 lignes au total.

### Ce que la grille apporte par rapport aux règles mono-gènes

Pour l'azathioprine et la mercaptopurine, la grille coïncide avec la sévérité maximale des deux règles mono-gènes : le moteur produit déjà le bon résultat. Ce qui change :

1. **La condition conjointe devient explicite.** Les lignes actuelles portent le phénotype « TPMT Normal + NUDT15 Normal » mais sont écrites deux fois, une par gène. Chaque gène porte seul une recommandation qui n'est valable que si l'autre est normal.
2. **Le cas composé est distingué.** CPIC prescrit 20–50 % de la dose pour un patient intermédiaire sur les deux gènes, contre 30–80 % pour un intermédiaire sur un seul. Même classe, texte différent : la recommandation affichée au clinicien doit refléter la bonne réduction.
3. **La thioguanine ne suit pas la même logique** : elle ne descend jamais sous `ADAPTER_DOSE`, même en métaboliseur lent sur les deux gènes. Une règle de sévérité maximale appliquée uniformément lui donnerait `EVITER` à tort.

Référence : CPIC Guideline for Thiopurine Dosing Based on TPMT and NUDT15 genotypes: 2025 Update, *Clin Pharmacol Ther*.

---

## 5. Fluvastatine — priorité du moteur

**Source : PA166262341, CPIC. Grille PharmCAT : 48 combinaisons, indexées par score d'activité CYP2C9 et fonction SLCO1B1.**

Restreinte aux valeurs du corpus :

| CYP2C9 (valeur) | SLCO1B1 0.0 déficiente | 0.5 diminuée | 1.0 normale | 1.5 augmentée |
| --- | --- | --- | --- | --- |
| 0,00 | `EVITER` | `EVITER` | `ADAPTER_DOSE` | `ADAPTER_DOSE` |
| 0,25 | `EVITER` | `EVITER` | `ADAPTER_DOSE` | `ADAPTER_DOSE` |
| 0,50 | `EVITER` | `ADAPTER_DOSE` | `ADAPTER_DOSE` | `ADAPTER_DOSE` |
| 0,75 | `EVITER` | `ADAPTER_DOSE` | `ADAPTER_DOSE` | `ADAPTER_DOSE` |
| 1,00 | `ADAPTER_DOSE` | `STANDARD` | `STANDARD` | `STANDARD` |

Cette grille **existe déjà** dans `regles_v13_multigene.csv`. Le défaut n'est pas une règle manquante : les règles mono-gènes de `regles_v14_monogene.csv` donnent `ADAPTER_DOSE` là où la grille bi-génique donne `EVITER`, et la priorité entre les deux tables n'est pas définie explicitement.

**Correction** : poser dans le moteur la règle « pour un médicament couvert par une grille multi-gènes, la grille prime sur les règles mono-gènes des mêmes gènes ». Principe déjà implicite via la colonne `guideline_multigene`, à rendre explicite et à vérifier dans le code. Aucune nouvelle ligne à écrire.

---

## 6. Récapitulatif

| # | Règle | Nature | Volume | Prêt ? |
| --- | --- | --- | --- | --- |
| 1 | Warfarine × VKORC1 | ajout | 3 lignes | **oui** |
| 2 | CYP2C9 warfarine et siponimod | modification + ajout | 436 lignes modifiées, valeur 1,0 à créer | **oui** |
| 3 | G6PD, 3 annotations | ajout | 8 médicaments × 3 valeurs | oui, sous réserve des 2 points du § 3.2 |
| 4 | Thiopurines | grille bi-génique | 27 lignes | **oui** |
| 5 | Fluvastatine | priorité du moteur | 0 ligne, 1 correction de code | **oui** |

Aucun texte n'est écrit de mémoire : chaque citation provient des archives du projet, extractions tracées dans `model_v2/docs/sources_v15/`.

### Vérifications effectuées sur mes propres sorties

Le classement automatique des textes en quatre classes a produit trois résultats faux, corrigés après lecture du texte intégral :

- G6PD « Normal » classé `EVITER` au lieu de `STANDARD` — le mot « avoid » apparaissait dans « **No reason to avoid** based on G6PD status ». Repris tel quel, cela aurait inversé la recommandation CPIC sur la rasburicase et la primaquine.
- Mercaptopurine en métaboliseur lent classée `EVITER` au lieu de `ADAPTER_DOSE` — le texte comporte deux branches selon l'indication.
- Phénytoïne supposée affectée par le défaut CYP2C9 — la table DPWG lui attribue 75 % de la dose pour \*1/\*2, donc le corpus est juste.

### Étape suivante

Étape 2 de la méthode validée : construire le corpus v15 sans toucher au v14, et mesurer combien d'étiquettes changent, médicament par médicament, avant tout réentraînement.
