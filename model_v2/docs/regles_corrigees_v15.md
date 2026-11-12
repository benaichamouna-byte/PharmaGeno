# Règles corrigées — corpus v15

Étape 1 de la méthode validée le 11 novembre 2026 : écrire les règles corrigées à partir des textes officiels, pour validation avant tout calcul.

Source unique de tous les textes cités ci-dessous : `~/projet_memoire/data/guidelineAnnotations.json.zip` (annotations de directives ClinPGx), extraction du 12 novembre 2026, 13 annotations, fichier `textes_regles_v15.md`.

---

## 0. Deux signalements antérieurs retirés

Les textes sources contredisent deux défauts que j'avais annoncés. Ils sont retirés, avec leur preuve.

### 0.1 « Incohérence TPMT PM entre les trois thiopurines » — RETIRÉ

J'avais signalé comme incohérent que le corpus donne `EVITER` pour l'azathioprine et `ADAPTER_DOSE` pour la mercaptopurine et la thioguanine chez le métaboliseur lent TPMT. CPIC différencie effectivement les trois médicaments :

| Annotation | Médicament | Texte CPIC pour TPMT et/ou NUDT15 PM | Action juste |
| --- | --- | --- | --- |
| PA166104933 | azathioprine | « an alternative immunosuppressant therapy should be considered » | `EVITER` |
| PA166104945 | mercaptopurine | « markedly reduced doses should be used » | `ADAPTER_DOSE` |
| PA166104965 | thioguanine | « drastic dose reduction is required » | `ADAPTER_DOSE` |

**Le corpus actuel est conforme à CPIC sur ce point.** Aucune correction à faire.

### 0.2 « G6PD sans effet sur ~50 médicaments » — RETIRÉ pour les médicaments codés

J'avais signalé comme défaut grave que toutes les lignes G6PD du corpus soient à `STANDARD`. L'annotation PA166279741, seule codée, est celle des médicaments **à risque faible ou nul**, et son texte dit :

> « The CPIC dosing guideline does not recommend changing prescribing actions based on G6PD genotype for low-to-no risk drugs. There is no reason to avoid low-to-no risk drugs in patients with the G6PD deficient or G6PD variable phenotypes. »

**Les ~150 lignes `STANDARD` du corpus sont correctes**, et le résumé « prudence et surveillance de l'hémolyse chez les patients CNSHA » reflète fidèlement la réserve CPIC. Aucune correction à faire sur ces lignes.

Le défaut G6PD réel est différent et plus étroit : il porte sur des **annotations absentes**, traité en règle 3.

---

## 1. Warfarine × VKORC1 — règle à ajouter

**Source : PA166182841, DPWG, « Annotation of DPWG Guideline for warfarin and VKORC1 », mise à jour novembre 2018, allèle lié rs9923231.**

Texte verbatim du tableau DPWG :

| Génotype | Description DPWG | Recommandation DPWG |
| --- | --- | --- |
| VKORC1 -1639 AA (rs9923231 TT) | « The genetic variation results in increased sensitivity to warfarin. This results in an increase in the risk of excessively severe inhibition of blood clotting (INR > 4) during the first month of the treatment. » | « 1. use 60% of the standard initial dose. The genotype-specific initial dose and maintenance dose can be calculated using an algorithm, as used in EU-PACT. From day 6 on the standard algorithm without genotype information can be used to calculate the dose. » |
| VKORC1 -1639 AG (rs9923231 CT) | « the effect is small and GA is also the most common genotype » | « NO action is needed for this gene-drug interaction » |

### Règles à écrire

| gene | valeur | medicament | action | phenotype | fichier |
| --- | --- | --- | --- | --- | --- |
| VKORC1 | 0.0 | warfarin | `ADAPTER_DOSE` | VKORC1 rs9923231 homozygote variant | PA166182841.json |
| VKORC1 | 0.5 | warfarin | `STANDARD` | VKORC1 rs9923231 hétérozygote | PA166182841.json |
| VKORC1 | 1.0 | warfarin | `STANDARD` | VKORC1 référence | PA166182841.json |

Codage de la valeur : identique à celui déjà employé pour VKORC1 dans le corpus (0.0 homozygote variant, 0.5 hétérozygote, 1.0 référence), défini dans `construire_regles_etiquettes_v14b_v1.py`.

Ligne 1.0 : le génotype de référence n'est pas cité comme sous-groupe concerné, donc posologie générale — même principe que l'hypothèse H-FDA-1 déjà appliquée dans le corpus.

### Justification de l'ajout

La directive existait dans les fichiers source du projet et la règle équivalente était déjà codée pour deux autres antivitamines K (acénocoumarol, phenprocoumone, DPWG) et pour la fluindione (RNPGx). Son absence pour la warfarine était une omission, non un choix — constat établi dans `claude/Justification_regle_warfarine_et_omission_VKORC1_11nov2026.md`.

### Pourquoi CYP4F2 n'est pas ajouté

CYP4F2 n'intervient pour la warfarine que dans la directive CPIC PA166104949, qui prescrit une dose calculée par algorithme multi-gènes dépendant de l'ascendance, et non une table génotype → action. Elle ne se ramène donc pas aux quatre classes du corpus. Cette exclusion est le principe déjà appliqué et documenté dans `construire_corpus_v7.py` : « non étiquetés volontairement : … antivitamines K (dose par algorithme pour tous) ». L'ajouter romprait la cohérence de construction du corpus.

Référence de la directive écartée : Johnson JA et al., *Clin Pharmacol Ther* 102(3):397-404, 2017. https://doi.org/10.1002/cpt.668

---

## 2. CYP2C9 selon DPWG — lecture par allèle au lieu du score d'activité

**Sources : PA166182842 (warfarine) et PA166211021 (siponimod), DPWG.**

DPWG définit ses recommandations **par diplotype nommé**, pas par score d'activité. Le corpus les lit par score, ce qui fusionne des diplotypes que DPWG sépare.

### 2.1 Warfarine — tableau DPWG verbatim

| Diplotype | Recommandation DPWG | Action |
| --- | --- | --- |
| CYP2C9\*1/\*2 | « NO action is required for this gene-drug interaction. » | `STANDARD` |
| CYP2C9\*1/\*3 | « use 65% of the standard initial dose » | `ADAPTER_DOSE` |
| CYP2C9\*2/\*2 | « use 65% of the standard initial dose » | `ADAPTER_DOSE` |
| CYP2C9\*2/\*3 | « use 45% of the standard initial dose » | `ADAPTER_DOSE` |
| CYP2C9\*3/\*3 | « use 20% of the standard initial dose » | `ADAPTER_DOSE` |
| CYP2C9 IM other | « use 65% of the standard initial dose » | `ADAPTER_DOSE` |
| CYP2C9 PM other | « use 20% of the standard initial dose » | `ADAPTER_DOSE` |

### 2.2 Siponimod — tableau DPWG verbatim

| Diplotype | Recommandation DPWG | Action |
| --- | --- | --- |
| CYP2C9\*1/\*2 | « NO action is required for this gene-drug interaction. » | `STANDARD` |
| CYP2C9\*2/\*2 | « NO action is required for this gene-drug interaction. » | `STANDARD` |
| CYP2C9\*1/\*3 | « Use 50% of the normal maintenance dose. » | `ADAPTER_DOSE` |
| CYP2C9\*2/\*3 | « Use 50% of the normal maintenance dose. » | `ADAPTER_DOSE` |
| CYP2C9 IM other | « Use 50% of the normal maintenance dose. » | `ADAPTER_DOSE` |
| CYP2C9\*3/\*3 | « Avoid siponimod. » | `EVITER` |
| CYP2C9 PM other | « Avoid siponimod. » | `EVITER` |

### 2.3 Nature exacte du défaut

Les diplotypes porteurs de \*2 seulement reçoivent **NO action** chez DPWG, alors que le score d'activité les classe en métaboliseur intermédiaire :

| Diplotype | Score d'activité | Classe par score dans le corpus | Action DPWG réelle | Écart |
| --- | --- | --- | --- | --- |
| \*1/\*2 | 1.5 | intermédiaire → `ADAPTER_DOSE` | `STANDARD` | **oui** |
| \*2/\*2 (siponimod) | 1.0 | intermédiaire → `ADAPTER_DOSE` | `STANDARD` | **oui** |
| \*2/\*2 (warfarine) | 1.0 | intermédiaire → `ADAPTER_DOSE` | `ADAPTER_DOSE` | non |

Le corpus surestime donc l'action pour les porteurs de \*2 sans \*3. Pour le siponimod, il manque en outre la distinction `EVITER` pour \*3/\*3 et PM other, actuellement présente mais à vérifier après recodage par allèle.

### 2.4 Décision à prendre (bloquante)

Le corpus encode CYP2C9 par une valeur numérique unique, pas par diplotype. Deux voies :

- **(A)** Garder le codage par score et n'ajouter que les lignes manquantes (valeur 1.0 absente pour phénytoïne, siponimod, warfarine). Rapide, mais l'écart \*1/\*2 et \*2/\*2 subsiste et doit être déclaré comme limite.
- **(B)** Introduire une distinction permettant de séparer les porteurs de \*2 seul des porteurs de \*3. Exige de reprendre l'encodage de la colonne CYP2C9 depuis les diplotypes PyPGx, donc de régénérer le corpus en amont des règles.

Cette décision conditionne l'ampleur du travail et la tenue du 18 novembre. **À trancher avant d'écrire le code.**

---

## 3. G6PD — trois annotations à ajouter

Le gène est couvert par six annotations CPIC ; une seule est codée. Les textes de résumé donnent l'action de chacune.

| Annotation | Médicaments | Texte CPIC | Statut |
| --- | --- | --- | --- |
| PA166279741 | 24 médicaments à risque faible ou nul | « does not recommend changing prescribing actions » | **codée, correcte** |
| **PA166119846** | rasburicase, dapsone, bleu de méthylène, pegloticase, tafénoquine | « high risk drugs should be avoided in G6PD deficient patients with or without CNSHA » | **absente → à ajouter** |
| **PA166279621** | primaquine | « should be avoided in G6PD deficient patients with or without CNSHA in most cases, with some exceptions for G6PD deficient patients without CNSHA » | **absente → à ajouter** |
| **PA166279721** | nitrofurantoïne | « use with caution in G6PD deficient patients without CNSHA and completely avoided by G6PD deficient patients with CNSHA » | **absente → à ajouter** |
| PA166279481 | chlorpropamide, dabrafénib, gliclazide, glimépiride, glipizide, mépacrine, mésalazine, moxifloxacine, nicorandil, nitrofural, probénécide, nitrate de sodium, sulfacétamide, tolazamide, tramétinib | « does not provide recommendations » | absente, sans action → ajout facultatif en `STANDARD` |
| PA166279561 | aspirine | « no reason to avoid aspirin at doses of ≤1g/day » ; « no recommendation » au-delà de 1 g/j | absente, sans action → ajout facultatif en `STANDARD` |

### 3.1 Règles à écrire — forme

Pour les trois annotations à action, en reprenant le codage G6PD du corpus (0.0 déficient, 0.5 variable, 1.0 normal) :

| gene | valeur | medicament | action | fichier |
| --- | --- | --- | --- | --- |
| G6PD | 0.0 | rasburicase, dapsone, methylene blue, pegloticase, tafenoquine | `EVITER` | PA166119846.json |
| G6PD | 0.5 | *(idem)* | *(à décider, voir 3.2)* | PA166119846.json |
| G6PD | 1.0 | *(idem)* | `STANDARD` | PA166119846.json |
| G6PD | 0.0 | primaquine | `EVITER` | PA166279621.json |
| G6PD | 1.0 | primaquine | `STANDARD` | PA166279621.json |
| G6PD | 0.0 | nitrofurantoin | `SURVEILLER` | PA166279721.json |
| G6PD | 1.0 | nitrofurantoin | `STANDARD` | PA166279721.json |

### 3.2 Deux points à trancher

- **Phénotype « variable » (valeur 0.5).** CPIC recommande pour ce phénotype un **test d'activité enzymatique avant traitement**, pas une action de prescription : « In patients with a G6PD variable or indeterminate phenotype, an enzyme activity test should be carried out before initiating drug therapy. » Ce n'est aucune des quatre classes. Proposition : `SURVEILLER`, avec mention explicite du test enzymatique dans le texte de recommandation. À valider.
- **CNSHA.** Trois des textes distinguent le patient déficient **avec** anémie hémolytique chronique non sphérocytaire de celui **sans**. Cette distinction est clinique, pas génotypique : elle n'est pas dérivable du VCF. La nitrofurantoïne en dépend directement (`SURVEILLER` sans CNSHA, `EVITER` avec). Proposition : retenir l'action du cas **sans CNSHA**, qui est le cas général, et porter la réserve CNSHA dans le texte affiché. À valider, et à écrire comme limite du mémoire.

Le gène étant porté par le chromosome X, le traitement haploïde déjà décidé en phase 1 reste applicable.

---

## 4. Thiopurines — directive bi-génique traitée en mono-gène

**Sources : PA166104933 (azathioprine), PA166104945 (mercaptopurine), PA166104965 (thioguanine), CPIC, mise à jour 2025 publiée dans *Clinical Pharmacology and Therapeutics*.**

Les trois directives portent sur **TPMT et NUDT15 conjointement**. Le corpus les a éclatées en règles mono-gènes, ce qui fait perdre deux informations :

1. **Le cas composé.** Mise à jour CPIC de février 2024 : « Patients who are intermediate metabolizers or possible intermediate metabolizers for both genes are recommended to begin with a starting dose of 20-50% of the normal dosage. » Un patient intermédiaire sur les deux gènes reçoit une réduction plus forte qu'un intermédiaire sur un seul. Deux règles mono-gènes ne peuvent pas l'exprimer.
2. **La condition conjointe des lignes normales.** Les lignes du corpus issues de `prescribing_guidance.json` portent le phénotype « TPMT Normal + NUDT15 Normal » mais sont écrites deux fois, une par gène. Chaque gène porte seul une recommandation qui n'est valable que si l'autre est normal.

### Règles à écrire — forme

Une grille bi-génique TPMT × NUDT15 par médicament, sur le modèle des grilles déjà présentes dans `regles_v13_multigene.csv` (rosuvastatine, sertraline, amitriptyline, phénytoïne, fluvastatine).

Logique CPIC, par médicament :

| Combinaison | azathioprine | mercaptopurine | thioguanine |
| --- | --- | --- | --- |
| Normal × Normal | `STANDARD` | `STANDARD` | `STANDARD` |
| IM sur un seul gène | `ADAPTER_DOSE` | `ADAPTER_DOSE` | `ADAPTER_DOSE` |
| IM sur les deux gènes | `ADAPTER_DOSE` (20-50 % de la dose) | `ADAPTER_DOSE` | `ADAPTER_DOSE` |
| PM sur l'un ou l'autre | `EVITER` | `ADAPTER_DOSE` | `ADAPTER_DOSE` |

**Texte exact par case manquant.** Les annotations ClinPGx ne contiennent que la prose ; la table par diplotype est dans le `prescribing_guidance.json` de PharmCAT, déjà cité dans la colonne `fichier` du corpus. Une extraction complémentaire est nécessaire avant d'écrire les lignes.

Référence : CPIC Guideline for Thiopurine Dosing Based on TPMT and NUDT15 genotypes: 2025 Update, *Clin Pharmacol Ther*.

---

## 5. Fluvastatine — directive bi-génique traitée en mono-gène

**Source : PA166262341, CPIC, « Annotation of CPIC Guideline for fluvastatin and CYP2C9, SLCO1B1 ».**

Texte du résumé CPIC :

> « CYP2C9 IMs avoid fluvastatin doses greater than 40mg while CYP2C9 PMs should avoid doses greater than 20mg. If higher doses are required for desired efficacy, an alternative statin should be considered. Patients with SLCO1B1 poor function should also avoid fluvastatin doses greater than 40mg and adjust doses of fluvastatin based on disease-specific guidelines. **Patients with both SLCO1B1 poor function and CYP2C9 IM/PM should be prescribed an alternative statin depending on the desired potency.** »

La dernière phrase est le cas bi-génique : fonction SLCO1B1 déficiente **et** CYP2C9 IM ou PM → statine alternative, soit `EVITER`.

### État réel

La grille bi-génique complète CYP2C9 × SLCO1B1 **existe déjà** dans `regles_v13_multigene.csv`, avec les textes CPIC verbatim et les 20 combinaisons. Les règles mono-gènes de `regles_v14_monogene.csv` existent aussi, mais donnent `ADAPTER_DOSE` là où la grille bi-génique donne `EVITER`.

**Le défaut n'est donc pas une règle manquante mais une priorité non définie** entre la table mono-gène et la table multi-gènes. Selon la table interrogée, le même patient reçoit « ajuster la dose » ou « éviter ».

### Correction proposée

Règle de priorité explicite dans le moteur : pour un médicament couvert par une grille multi-gènes, la grille multi-gènes prime sur les règles mono-gènes des mêmes gènes. Principe déjà implicite dans le corpus (colonne `guideline_multigene`) mais à rendre explicite et à vérifier dans le code du moteur.

Aucune nouvelle ligne à écrire pour ce point : la table existe. À vérifier dans le moteur, puis à documenter.

---

## 6. Récapitulatif — ce qui reste à faire

| # | Règle | Nature | Texte source en main ? | Bloqué par |
| --- | --- | --- | --- | --- |
| 1 | Warfarine × VKORC1 | 3 lignes à ajouter | **oui, verbatim** | rien — prêt à coder |
| 2 | CYP2C9 DPWG par allèle | recodage | **oui, verbatim** | décision (A) ou (B) au § 2.4 |
| 3 | G6PD, 3 annotations | lignes à ajouter | résumés oui, textes par phénotype non | décisions § 3.2 + extraction PharmCAT |
| 4 | Thiopurines bi-géniques | grille à construire | logique oui, grille non | extraction PharmCAT |
| 5 | Fluvastatine | priorité du moteur | **oui** | vérification du code du moteur |

### Extraction complémentaire nécessaire

Le `prescribing_guidance.json` de PharmCAT, pour les tables par phénotype de : azathioprine, mercaptopurine, thioguanine (TPMT × NUDT15), rasburicase, dapsone, bleu de méthylène, pegloticase, tafénoquine, primaquine, nitrofurantoïne (G6PD).

---

*Document rédigé le 12 novembre 2026. Aucun texte n'est écrit de mémoire : chaque citation provient de l'archive `guidelineAnnotations.json.zip` du projet, extraction tracée dans `textes_regles_v15.md`. Les points marqués « à trancher » ne sont pas codés tant qu'ils ne sont pas validés.*
