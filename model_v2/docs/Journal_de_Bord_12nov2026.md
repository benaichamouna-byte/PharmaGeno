# Journal de Bord du Projet — PharmaGeno
## Session du 12 novembre 2026

**Objet de la session : étapes 1 et 2 de la correction des règles (corpus v15).**
Dépôt du mémoire : 25 novembre 2026. Encadrant disponible à partir du 15 novembre. Date limite interne du v15 : 18 novembre.

---

## 1. Décisions prises et validées

| # | Décision | Statut |
| --- | --- | --- |
| 1 | Ordre de réparation des défauts : G6PD, warfarine, CYP2C9, thiopurines, fluvastatine | validée |
| 2 | G6PD inclus comme cinquième défaut, en plus des quatre initiaux | validée |
| 3 | **Warfarine : corriger par VKORC1 (DPWG PA166182841), sans CYP4F2** | validée |
| 4 | **CYP2C9 : voie A** — codage par score d'activité conservé, étiquettes corrigées, encodage d'entrée inchangé | validée |
| 5 | Principe de résolution des valeurs ambiguës : action du diplotype nommé le plus fréquent, **sauf désescalade depuis `EVITER`** | validée |
| 6 | G6PD phénotype « variable » → `SURVEILLER` avec le texte du test enzymatique | validée |
| 7 | G6PD : phénotype `Deficient` retenu, CNSHA non dérivable d'un VCF, réserve clinique affichée | validée |
| 8 | **Thioguanine TPMT normal × NUDT15 lent → `ADAPTER_DOSE`** (CPIC 2025 prime sur DPWG, principe de spécificité) | validée |
| 9 | Fluvastatine : grille multi-gènes prime sur les règles mono-gènes — correction du moteur, aucune ligne à écrire | validée |

### Justification de l'exclusion de CYP4F2 (warfarine)

CYP4F2 n'intervient que dans la directive CPIC PA166104949, qui prescrit une dose par algorithme multi-gènes dépendant de l'ascendance. Les clés de la grille PharmCAT correspondante sont de la forme « Any Result », sans action par génotype : elle ne se ramène pas aux quatre classes. Exclusion conforme au principe déjà documenté dans `construire_corpus_v7.py`.

### Justification de la voie A (CYP2C9)

Trois arguments : le protocole de comparaison équitable (15 octobre) et la validation externe sur 104 personnes portent sur un espace d'entrée qui ne doit pas changer ; le score d'activité CYP2C9 est l'indexation employée par PharmCAT lui-même (grilles fluvastatine et phénytoïne) ; le résidu après correction tombe à 0,06 % du corpus.

---

## 2. Erreurs à ne plus reproduire

### Erreurs de méthode de Claude (consignées)

1. **Ne jamais conclure avant d'avoir lu la source.** Quatre diagnostics ont dû être retirés : incohérence TPMT (le corpus était conforme à CPIC), défaut G6PD sur les médicaments à risque faible (les lignes `STANDARD` étaient correctes), phénytoïne affectée par le défaut CYP2C9 (DPWG lui donne 75 % pour \*1/\*2), annotations G6PD absentes du v14 (deux sur trois y étaient déjà).
2. **Ne jamais diagnostiquer sur le mauvais fichier.** Les erreurs G6PD venaient d'une analyse de `phenotype_drug_dataset_complet_v2.csv` (46 371 lignes) alors que le corpus de travail est `corpus_v14/phenotype_drug_dataset_v14.csv` (232 664 lignes). Vérifier le fichier de référence avant toute mesure.
3. **Ne jamais reprendre une classification automatique sans lire le texte.** Trois classements faux : « No reason to avoid » lu comme `EVITER` (aurait inversé la recommandation CPIC sur la rasburicase et la primaquine), mercaptopurine en lent classée `EVITER` alors que le texte a deux branches selon l'indication, phénytoïne supposée en écart.
4. **Vérifier la cohérence interne d'un document avant de le livrer.** La grille du § 4 contredisait le § 0.1 du même document sur la mercaptopurine.
5. **Ne pas livrer un fragment Python à coller dans un terminal bash.** Tout code doit être fourni en bloc directement exécutable (heredoc ou fichier).
6. **Ne rien produire sans validation préalable** — protocole en deux étapes : exposer la méthode, attendre l'accord.

### Pièges techniques rencontrés

7. **`git push origin main` depuis une autre branche ne pousse rien.** La branche de travail est `sauvegarde-2026-11-02` ; pousser avec `git push origin sauvegarde-2026-11-02`. Un « Everything up-to-date » après un commit réussi signale ce piège.
8. **Windows n'écrase pas un téléchargement de même nom** : il crée `fichier (1).md`, `fichier (2).md`. Vérifier la taille du fichier copié avant de commiter. Commande robuste : `NEW=$(ls -t /mnt/c/Users/MSI/Downloads/<motif>*.md | head -1)`.
9. **Les annotations ClinPGx ne contiennent pas de clé `recommendations`** : le texte est dans `guideline.textMarkdown.html` et `guideline.summaryMarkdown.html`. Les grilles par phénotype sont ailleurs.
10. **`prescribing_guidance.json` est à l'intérieur de `pharmcat-3.4.0-all.jar`** (5,2 Mo, 356 directives), extractible avec `unzip`. Sa structure : `guidelines[].recommendations[]` avec `lookupKey` (liste de paires gène → phénotype), `classification.term`, `implications[]`, `text.html`.
11. **`tables_cpic_v8.json` ne contient que les tables diplotype → phénotype**, pas les recommandations.

---

## 3. État des fichiers

### Produits ce jour

| Fichier | Taille | Emplacements |
| --- | --- | --- |
| `regles_corrigees_v15.md` | 22 193 o | WSL, Windows, GitHub, Drive `Docs`, projet Claude |
| `grilles_pharmcat_v15.md` | 334 940 o | WSL, Windows, GitHub, Drive `Docs` |
| `textes_regles_v15.md` | 97 851 o | idem |
| `sources_regles_v15.md` | 3 737 o | idem |
| `mesure_cyp2c9.txt` | 1 454 o | idem |

Chemin WSL : `~/projet_memoire/model_v2/docs/` et `~/projet_memoire/model_v2/docs/sources_v15/`.
Branche GitHub : `sauvegarde-2026-11-02`. Derniers commits : `3cef762`, `87bbf55`, `f9fbf35`.

### Classement Drive

`Docs/` : les cinq fichiers v15 (pièces justificatives). `DOCs Memoire/` : réservé au mémoire lui-même (copie zéro v6).

---

## 4. Plan exact de ce qu'il reste à faire

### Immédiat — corpus v15

1. **Écrire les cinq règles corrigées** dans les fichiers de règles, à partir du § 1 à § 5 de `regles_corrigees_v15.md`.
2. **Construire le corpus v15** sans toucher au v14, et **vérifier que les écarts correspondent exactement** aux volumes mesurés : 415 lignes modifiées, 2 441 ajoutées, 232 664 → 235 105 lignes.
3. **Corriger le moteur** : rendre explicite la primauté des grilles multi-gènes sur les règles mono-gènes des mêmes gènes (fluvastatine, thiopurines).
4. **Réentraîner** DL, XGBoost et RF avec le protocole inchangé — mêmes plis, mêmes réglages, mêmes mesures. Rédiger l'amendement écrit au protocole.
5. **Refaire ce qui en dépend** : chapitres 6 à 8, application avec les nouveaux modèles, comparaison sur les 104 personnes, captures d'écran.
6. **Figer** règles, application, scripts, modèles et empreintes, puis évaluation finale unique sur les 138 profils.

**Garde-fou** : si le v15 n'est pas réentraîné et vérifié au 18 novembre, retour au v14 avec les défauts déclarés comme limites. Le v14 reste intact.

### En parallèle, indépendant du corpus

7. **Courbe d'apprentissage** selon le nombre de profils (décidée le 11 novembre).
8. **Correction des 81 textes de l'application** (reportée après la copie zéro).
9. **Validation par 2 ou 3 comparateurs externes** indépendants des règles d'entraînement (exigence du 7 novembre).
10. **Chapitre 2**, inventaire des justifications, version 7 du mémoire à partir de `Memoire_texte_v6.md`.
11. **Déposer la copie zéro v6** dans `DOCs Memoire/` sur Drive.

### Limites à écrire dans le mémoire

- **CYP2C9** : le codage par score d'activité confond \*1/\*3 et \*2/\*2 pour le siponimod, auxquels la DPWG attribue des actions différentes. 146 lignes sur 232 664 (0,06 %), un seul médicament. Erreur irréductible de la représentation, non défaut d'apprentissage. Voie B (porter le diplotype) identifiée comme perspective.
- **CNSHA** : phénotype non dérivable d'un VCF. L'outil assigne `Deficient` et affiche la réserve clinique.
- **Mercaptopurine en métaboliseur lent** : action dépendante de l'indication. La branche « malignité » est retenue, le webtool ne connaissant pas l'indication.
- **Hiérarchie des sources** : les grilles multi-gènes CPIC priment sur les règles mono-gènes DPWG, par spécificité. Distinct du principe de résolution des ambiguïtés d'encodage.

---

## 5. Règles de travail en vigueur

- Aucun accès de Claude à la machine locale : toute commande est exécutée par Mouna, sortie collée. Claude lit en revanche directement le Drive et le dépôt GitHub.
- Protocole en deux étapes : exposer la méthode, attendre validation, puis produire.
- Zéro invention : chaque texte de règle provient d'un fichier source cité, jamais d'une rédaction de mémoire.
- Sauvegarde quadruple : WSL → Windows (`C:\Users\MSI\Desktop\memoire\`) → GitHub (branche `sauvegarde-2026-11-02`) → Drive.
- Chaque affirmation accompagnée d'une référence ; ce qui n'est pas référencé est marqué « non vérifié ».
- À la fin de chaque réponse : bloc « Sauvegarde / État d'avancement » et rappel de ce qui reste en attente côté Mouna.
