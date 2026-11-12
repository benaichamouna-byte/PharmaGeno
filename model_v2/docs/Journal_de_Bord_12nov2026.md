# Journal de Bord du Projet — PharmaGeno
## Session du 12 novembre 2026

**Objet : correction des règles et construction du corpus v15 — étapes 1, 2 et 3 terminées.**
Dépôt du mémoire : 25 novembre 2026. Encadrant disponible à partir du 15 novembre. Date limite interne du v15 : 18 novembre.

---

## 1. Décisions prises et validées

| # | Décision | Statut |
| --- | --- | --- |
| 1 | Ordre de réparation : G6PD, warfarine, CYP2C9, thiopurines, fluvastatine | validée |
| 2 | **Warfarine : corriger par VKORC1 (DPWG PA166182841), sans CYP4F2** | validée |
| 3 | **CYP2C9 : voie A** — codage par score d'activité conservé, étiquettes corrigées, encodage d'entrée inchangé | validée |
| 4 | Résolution des valeurs ambiguës : action du diplotype nommé le plus fréquent, **sauf désescalade depuis `EVITER`** | validée |
| 5 | **Thioguanine TPMT normal × NUDT15 lent → `ADAPTER_DOSE`** : CPIC 2025 prime sur DPWG, par spécificité de la grille bi-génique | validée |
| 6 | **G6PD phénotype « variable » : exclu de l'étiquetage**, comme les autres règles conditionnelles | validée (révise une décision antérieure du même jour) |
| 7 | G6PD : phénotype `Deficient` retenu, CNSHA non dérivable d'un VCF, réserve clinique affichée dans l'application | validée |
| 8 | Séparation : le corpus porte des **étiquettes**, l'application porte de l'**information** | validée |
| 9 | Fluvastatine : aucune correction — le moteur applique déjà la priorité multi-gènes | constatée |

### Justifications à retenir

**Exclusion de CYP4F2 (warfarine).** CYP4F2 n'intervient que dans la directive CPIC PA166104949, qui prescrit une dose par algorithme multi-gènes dépendant de l'ascendance. Les clés de la grille PharmCAT correspondante sont « Any Result » : elle ne se ramène pas aux quatre classes. Conforme au principe déjà écrit dans `construire_corpus_v7.py`.

**Voie A pour CYP2C9.** Le protocole de comparaison équitable (15 octobre) et la validation externe sur 104 personnes portent sur un espace d'entrée qui ne doit pas changer ; le score d'activité CYP2C9 est l'indexation employée par PharmCAT lui-même ; le résidu après correction tombe à 0,06 % du corpus.

**Politique uniforme des règles conditionnelles.** Une règle dont l'action dépend d'une information absente du VCF n'est pas étiquetée. Six règles concernées : mavacamten, éliglustat, flécaïnide, quétiapine, primaquine, et le phénotype G6PD « variable ». Aucune dérogation.

---

## 2. Erreurs à ne plus reproduire

### Méthode

1. **Ne jamais conclure avant d'avoir lu la source.** Six diagnostics ont dû être retirés en une journée : incohérence TPMT, défaut G6PD sur médicaments à risque faible, phénytoïne affectée par le défaut CYP2C9, annotations G6PD absentes du v14, primaquine manquante, correction du moteur à faire. Dans chaque cas la source disait le contraire.
2. **Vérifier sur quel fichier on travaille.** Les erreurs G6PD venaient d'une analyse de `phenotype_drug_dataset_complet_v2.csv` (46 371 lignes) alors que le corpus de travail est `corpus_v14/phenotype_drug_dataset_v14.csv` (232 664 lignes).
3. **Ne jamais reprendre une classification automatique de texte sans la lire.** Trois classements faux, dont « No reason to avoid » lu comme `EVITER` — ce qui aurait inversé la recommandation CPIC sur la rasburicase et la primaquine. Une seconde fois dans le script de génération, sur la grille thiopurines.
4. **Vérifier la cohérence interne d'un document avant de le livrer** : la grille du § 4 a contredit deux fois le § 0.1 sur la mercaptopurine.
5. **Valider un pipeline en reproduisant l'existant avant de produire du neuf.** La reconstruction du v14 a révélé que le fichier de profils n'était pas celui qu'on croyait.
6. **Ne rien produire sans validation préalable** : exposer la méthode, attendre l'accord.
7. **Livrer du code en bloc exécutable**, jamais un fragment Python à coller dans bash.

### Pièges techniques

8. **`git push origin main` depuis une autre branche ne pousse rien.** La branche de travail est `sauvegarde-2026-11-02`. Un « Everything up-to-date » après un commit réussi signale ce piège.
9. **Windows n'écrase pas un téléchargement de même nom** : il crée `fichier (1).md`, `(2)`, `(3)`. Toujours vérifier la taille avant de commiter. Commande robuste : `NEW=$(ls -t /mnt/c/Users/MSI/Downloads/<motif>*.md | head -1)`.
10. **Les annotations ClinPGx n'ont pas de clé `recommendations`** : le texte est dans `guideline.textMarkdown.html` et `summaryMarkdown.html`.
11. **`prescribing_guidance.json` est dans `pharmcat-3.4.0-all.jar`** (5,2 Mo, 356 directives), extractible par `unzip`. Structure : `guidelines[].recommendations[]` avec `lookupKey` (liste de paires gène → phénotype), `classification.term`, `implications[]`, `text.html`.
12. **`tables_cpic_v8.json` ne contient que les tables diplotype → phénotype**, pas les recommandations.
13. **`profils_genes_v6.csv` et `profils_genes_v6_complet.csv` diffèrent** sur le DPYD de cinq profils (HG00613, HG01631, HG03115, NA18956, NA19711) et ne produisent pas le même corpus. **Le corpus v14 et le v15 viennent de `v6_complet`.**
14. **Un compte de caractères n'est pas un compte d'octets** : les accents en UTF-8 occupent deux octets. Annoncer les tailles avec `wc -c`.

---

## 3. État des fichiers

### Produits ce jour

| Fichier | Taille | Emplacement WSL |
| --- | --- | --- |
| `regles_corrigees_v15.md` (version 6) | 28 977 o | `model_v2/docs/` |
| `Journal_de_Bord_12nov2026.md` | — | `model_v2/docs/` |
| `generer_regles_v15.py` | 9 953 o | `Model_v8_7_9_10/scripts/` |
| `regles_v15_monogene.csv` | 242 914 o — 709 règles | `Model_v8_7_9_10/data/` |
| `regles_v15_multigene.csv` | 55 098 o — 124 règles | `Model_v8_7_9_10/data/` |
| `phenotype_drug_dataset_v15.csv` | 37 046 459 o — 234 632 lignes | `Model_v8_7_9_10/data/corpus_v15/` |
| `grilles_pharmcat_v15.md`, `textes_regles_v15.md`, `sources_regles_v15.md`, `mesure_cyp2c9.txt` | traces d'extraction | `model_v2/docs/sources_v15/` |

### Sauvegardes

Branche GitHub `sauvegarde-2026-11-02`. Commits du jour : `3cef762`, `87bbf55`, `f9fbf35`, `1c14646`, `bb30343`, `13be3fb`.

Drive : `Docs` contient le document de règles (version 6), les quatre traces d'extraction et `couverture_corpus_v15.csv`. `scripts_classification_9nov2026 / 1_etiquetage_regles` contient `generer_regles_v15.py` et les deux CSV de règles v15. Le corpus de 37 Mo n'est pas sur Drive — illisible en aperçu, présent sur GitHub.

**Intacts comme solution de repli** : `corpus_v14/`, `regles_v14_monogene.csv`, `regles_v13_multigene.csv`, modèles v14.

---

## 4. Le corpus v15 en chiffres

**234 632 lignes, 189 médicaments, 1 379 profils.**

| | v14 | v15 | Écart |
| --- | --- | --- | --- |
| `STANDARD` | 199 133 | 201 273 | +2 140 |
| `ADAPTER_DOSE` | 20 426 | 20 272 | −154 |
| `EVITER` | 8 049 | 8 031 | −18 |
| `SURVEILLER` | 5 056 | 5 056 | 0 |
| **Total** | **232 664** | **234 632** | **+1 968** |

Écarts vérifiés ligne à ligne : 1 968 ajouts, 0 suppression, 433 modifications — conformes à la prévision.

| Médicament | Transition | Lignes |
| --- | --- | --- |
| warfarine | `ADAPTER_DOSE` → `STANDARD` | 197 |
| siponimod | `ADAPTER_DOSE` → `STANDARD` | 218 |
| mercaptopurine | `EVITER` → `ADAPTER_DOSE` | 9 |
| thioguanine | `EVITER` → `ADAPTER_DOSE` | 9 |
| siponimod | lignes créées, `STANDARD` | +984 |
| warfarine | lignes créées, `STANDARD` | +741 |
| warfarine | lignes créées, `ADAPTER_DOSE` (VKORC1 variant) | +243 |

L'équilibre des classes est inchangé : le réentraînement se fait dans les mêmes conditions que le v14.

---

## 5. Plan de ce qu'il reste à faire

### Étape 4 — réentraînement (la partie longue, peu de décisions)

1. Réentraîner **DL, XGBoost et Random Forest** sur `corpus_v15/phenotype_drug_dataset_v15.csv`, protocole strictement inchangé : mêmes plis, mêmes réglages, mêmes mesures. Seul le corpus change.
2. Rédiger l'**amendement écrit au protocole** de comparaison équitable.
3. Refaire ce qui en dépend : **chapitres 6 à 8**, application avec les nouveaux modèles, comparaison sur les **104 personnes**, captures d'écran.
4. **Figer** règles, application, scripts, modèles et empreintes, puis évaluation finale unique sur les **138 profils**.

**Garde-fou** : si le v15 n'est pas réentraîné et vérifié au 18 novembre, retour au v14 avec les défauts déclarés comme limites. Le v14 est intact.

### En parallèle, indépendant du corpus

5. **Courbe d'apprentissage** selon le nombre de profils.
6. **Correction des 81 textes** de l'application.
7. **Validation par 2 ou 3 comparateurs externes** indépendants des règles d'entraînement.
8. **Chapitre 2**, inventaire des justifications, version 7 du mémoire à partir de `Memoire_texte_v6.md`.
9. **Déposer la copie zéro v6** dans `DOCs Memoire/` sur Drive — le dossier est encore vide.

### Limites à écrire dans le mémoire

- **CYP2C9** : le codage par score d'activité confond \*1/\*3 et \*2/\*2 pour le siponimod, auxquels la DPWG attribue des actions différentes. 146 lignes sur 232 664, un seul médicament. Erreur irréductible de la représentation, non défaut d'apprentissage. Voie B (porter le diplotype) identifiée comme perspective.
- **CNSHA** : phénotype non dérivable d'un VCF. L'outil assigne `Deficient` et affiche la réserve clinique.
- **Règles conditionnelles** : six règles non étiquetées car leur action dépend d'une information absente du VCF. Politique uniforme, sans dérogation.
- **Mercaptopurine en métaboliseur lent** : action dépendante de l'indication ; branche « malignité » retenue.
- **Hiérarchie des sources** : les grilles multi-gènes CPIC priment sur les règles mono-gènes DPWG, par spécificité. Distinct du principe de résolution des ambiguïtés d'encodage.
- **Fichiers de profils** : `v6` et `v6_complet` diffèrent sur cinq profils ; le corpus vient de `v6_complet`.

---

## 6. Règles de travail en vigueur

- Claude n'a aucun accès à la machine locale : toute commande est exécutée par Mouna, sortie collée. Claude lit en revanche directement le Drive et le dépôt GitHub, et y récupère les fichiers lui-même.
- Protocole en deux étapes : exposer la méthode, attendre validation, puis produire.
- Zéro invention : chaque texte de règle provient d'un fichier source cité.
- Sauvegarde quadruple : WSL → Windows (`C:\Users\MSI\Desktop\memoire\`) → GitHub (branche `sauvegarde-2026-11-02`) → Drive.
- Chaque affirmation accompagnée d'une référence ; ce qui n'est pas référencé est marqué « non vérifié ».
- À la fin de chaque réponse : bloc « Sauvegarde / État d'avancement » et rappel de ce qui reste en attente côté Mouna.
