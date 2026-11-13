# Amendement 2 au protocole de comparaison équitable — passage du corpus v14 au corpus v15

**Rédigé le 13 novembre 2026 au matin, AVANT toute lecture des résultats de l'étape d'analyse.** Les étapes 1 à 5 de l'exécution v15 sont terminées et l'étape 6 est en cours au moment de la rédaction ; aucune de leurs sorties n'a été analysée (voir § 7, transparence). Amende le `Protocole_comparaison_equitable_DL_XGB_RF_v14_4nov2026.md` (figé, SHA-256 `3272cc33985c10a739c2c12f08fd6f0176eaf30c4e014d3bd9daffff342c754b`) et l'`Amendement_1_protocole_comparaison_equitable_v14_5nov2026.md`. Ces deux textes restent **intacts** : le présent document s'y ajoute, il n'en remplace aucune ligne.

---

## 1. Objet

Les règles d'étiquetage ont été corrigées le 12 novembre 2026 sur quatre points (warfarine × VKORC1, CYP2C9 par voie A, thioguanine, mercaptopurine), produisant le corpus **v15**. La comparaison équitable DL / XGBoost / forêt aléatoire doit donc être refaite sur ce corpus.

**Une seule chose change : le corpus.** Le présent amendement établit ce qui reste identique, justifie les trois écarts d'exécution, et enregistre les éléments de traçabilité produits avant le lancement.

---

## 2. Ce qui change

| | v14 | v15 |
| --- | --- | --- |
| Corpus | `corpus_v14/phenotype_drug_dataset_v14.csv`, 232 664 lignes | `corpus_v15/phenotype_drug_dataset_v15.csv`, **234 632 lignes** |
| SHA-256 du corpus | `b876bb469e562d6e…` | `68b564ce265728b6f800929032df3f4e046710e47f3cbe311beedbd2c830d2b5` |
| Règles mono-géniques | `regles_v14_monogene.csv`, 704 règles | `regles_v15_monogene.csv`, 709 règles, SHA-256 `9d5512543016cb89c612e6213326f4b0662444b79f2dd9aec31acd877ac80728` |
| Règles multi-géniques | `regles_v13_multigene.csv`, 97 règles | `regles_v15_multigene.csv`, 124 règles, SHA-256 `1cb99ff63246669c1a2438f9776b93b00538c67981d89ef92d7cf6d51f28dfc6` |

Écarts du corpus, vérifiés ligne à ligne : **1 968 ajouts, 0 suppression, 433 modifications.** L'équilibre des classes est pratiquement inchangé (`STANDARD` 85,59 % → 85,78 %), de sorte que la difficulté de la tâche d'apprentissage reste comparable. Le détail par médicament figure au § 4 du `Journal_de_Bord_12nov2026_regles_v15.md` et la justification de chaque correction dans `Regles_corrigees_v15_textes_sources_12nov2026.md`.

Les 189 médicaments, les 1 379 profils et la nature de l'étiquette (sortie du moteur de règles, donc accord avec les directives et non exactitude clinique) sont inchangés.

---

## 3. Ce qui ne change pas

Repris sans modification du protocole du 4 novembre, et vérifié par empreinte SHA-256 avant exécution (§ 6) :

- **Plis externes** : `protocole_commun_v10.decouper`, StratifiedGroupKFold, 5 plis, graine 42, groupe = `family_id`.
- **Ensemble final** : les mêmes 138 familles, **lues par aucune étape**.
- **Validation interne** : 15 % (graine 49) pendant la recherche, 10 % (graine 42) pendant l'entraînement final, mêmes familles pour les trois bras.
- **Espaces de recherche** des trois modèles, **budget** de 40 configurations × 5 plis, configuration 0 = réglage de référence, graine de tirage 0.
- **Critère** de sélection et d'arrêt : F1 macro de la validation interne, égalité tranchée par le plus petit indice.
- **Entraînement final** : 5 graines (42 + 100·s + k), calibration par mise à l'échelle de la température sur la validation interne.
- **Mesures, statistique et incertitude** : F1 macro primaire, EVITER manqués, faux EVITER, erreurs totales, log-loss, ECE, F1 par niveau de source ; bootstrap par famille, 2 000 tirages, graine 42, mêmes familles pour tous les modèles.
- **Règle de décision** : marge d'équivalence pratique δ = 0,001, trois comparaisons sans correction pour multiplicité.
- **Usage des résultats** (§ 8 du protocole) : rapportés en entier quel que soit le sens, aucun réglage ni changement de métrique après lecture, aucun remplacement automatique du modèle de l'application.
- **Analyse** : `comparaison_equitable_v14_v1.py` (règle du protocole) **et** `_v2.py` (amendement 1) sont tous deux exécutés, conformément à l'exigence de l'amendement 1 que la v1 soit conservée et exécutée.

---

## 4. Les trois écarts d'exécution, et leur justification

### 4.1 Les recherches d'hyperparamètres sont refaites sur la v15, non reprises de la v14

**Décision.** Les six étapes de recherche et d'évaluation sont rejouées intégralement sur le corpus v15. Les dossiers `dl_hp_v14`, `hp_arbres_v14_xgb` et `hp_arbres_v14_rf` ne sont pas réutilisés comme réglages.

**Justification.** Le § 1 du protocole du 4 novembre énumère cinq asymétries que ce protocole a été écrit pour supprimer. La cinquième est : « le réglage du DL (config 35) a été choisi sur le corpus v13 ; les familles de test de chaque pli v14 ont très probablement servi, dans la v13, d'entraînement ou de validation interne à d'autres plis ». Le corpus v15 partage les plis du v14 et en diffère de 0,85 % des lignes. Reprendre sur la v15 des hyperparamètres sélectionnés sur la v14 reproduirait donc exactement la situation que cette clause écarte : des réglages choisis en ayant vu, sous une forme quasi identique, les familles qui serviront de test.

Le coût est d'environ neuf heures de calcul supplémentaires. Il est assumé : l'alternative aurait été d'invalider la propriété centrale que le protocole revendique.

**Exception, une seule.** La configuration 35 du DL n'est pas re-sélectionnée. Elle est, par définition, le réglage figé du modèle déployé dans l'application, choisi sur la v13 ; le protocole la désigne explicitement comme « bras de référence supplémentaire » (§ 5) et non comme un bras réglé. La re-sélectionner la priverait de ce qu'elle mesure.

### 4.2 L'ordre des étapes est modifié : le DL en configuration 35 passe en premier

**Décision.** Le bras « DL c35 figé » est exécuté en étape 1, avant les recherches, alors qu'en v14 il avait été lancé séparément.

**Justification.** Ce bras ne dépend d'aucune recherche et conditionne la régénération de l'application, les captures d'écran et la comparaison externe sur 104 personnes. Placé en tête, il est disponible après sept minutes au lieu de vingt heures. **Aucun effet sur les résultats** : les bras sont indépendants, chacun recalcule ses propres plis et n'écrit que dans son dossier de sortie.

### 4.3 Un script est paramétré : `evaluer_dl_imbrique_v6.py`

**Décision.** `evaluer_dl_imbrique_v5.py` est conservé **intact**. Une copie `v6` est créée, dont le diff avec la v5 comporte exactement quatre blocs :

1. l'en-tête de documentation ;
2. `niveau_par_medicament()` reçoit deux paramètres `f_mono` et `f_multi` au lieu de chemins v14 écrits en dur ;
3. deux options `--regles_mono` et `--regles_multi` sont ajoutées à l'analyseur d'arguments, et le défaut de `--data` passe au corpus v15 ;
4. le site d'appel transmet ces deux paramètres.

**Justification.** La v5 lit `regles_v14_monogene.csv` et `regles_v13_multigene.csv` en dur pour construire la table médicament → niveau de source (CPIC / DPWG / RNPGx / FDA), utilisée par la mesure « F1 macro par niveau de source ». Exécutée telle quelle sur la v15, elle aurait attribué les niveaux de source d'après des règles périmées. **Aucune ligne de calcul, d'entraînement, de découpage ou de métrique n'est touchée.**

**Vérification.** Le fichier a été produit chez Mouna par transformation programmée de la v5, chaque remplacement devant trouver exactement une occurrence sous peine d'arrêt. L'empreinte obtenue, `8e7b302fd95c0625ebfca2a94e129d5575f01e4f07d1648baa58daa3e63ba1d0`, est identique à celle du fichier contrôlé et compilé indépendamment. Le diff a été relu bloc par bloc.

---

## 5. Incident de traçabilité : suppression de `dl_hp_v13`

Le dossier `results/dl_hp_v13/`, qui contenait le `configs.json` définissant la configuration 35, **n'existe plus** dans l'arborescence au 12 novembre 2026. L'étape 1 lit donc `results/dl_hp_v14/configs.json`.

**Cette substitution est sans effet, et c'est démontrable.** La fonction `recherche_hp_dl_v4.configs(n, graine=0)` construit la liste des configurations par `np.random.RandomState(0)` sur un espace fixe (`ESPACE`), augmentée de `dl_coeur_v4.CFG_V3` en position 0. Elle **ne lit aucune donnée**. Le fichier produit est donc strictement déterministe et identique en v13, v14 et v15, pour un même `--n 40`.

Vérification effectuée : les 40 configurations ont été régénérées indépendamment à partir des deux fichiers source (dont les empreintes SHA-256 sont conformes au protocole), et la configuration 35 obtenue est **2 couches, largeur 1024, sans BatchNorm, dropout 0,1, activation relu, pas d'apprentissage 1e-3, décroissance 1e-4, lot 64, w_exp 0,5, ev_x 1,0, lissage 0,05, patience 25** — identique à la description qu'en donne la docstring de `recherche_hp_dl_v4.configs_tour2`, rédigée à l'époque de la v13. Deux sources indépendantes concordent.

En conséquence, l'étape 0 du script de lancement **vérifie le contenu de la configuration 35** et interrompt l'exécution en cas d'écart, au lieu de se contenter de constater l'existence d'un dossier. Le contrôle porte sur ce qui définit le modèle, non sur un nom de répertoire.

**À déclarer comme limite** : la perte de ce dossier est une perte de traçabilité, non de reproductibilité. Elle est réparable à tout moment en réexécutant `recherche_hp_dl_v4.py --n 40`.

---

## 6. Traçabilité enregistrée avant exécution

### 6.1 Environnement d'exécution, identique à celui de la v14

| | v14 (5 nov.) | v15 (12 nov.) |
| --- | --- | --- |
| numpy | 2.4.3 | 2.4.3 |
| pandas | 3.0.2 | 3.0.2 |
| scipy | 1.17.1 | 1.17.1 |
| scikit-learn | 1.8.0 | 1.8.0 |
| xgboost | 3.3.0 | 3.3.0 |
| torch | 2.11.0+cu130 | 2.11.0+cu130 |
| machine | 8 cœurs, 7 Go libres | 8 cœurs, 7 Go libres |

Source v14 : `Journal_de_Bord_5nov2026_comparaison_equitable.md`, § 1. Source v15 : étape 0 du journal d'exécution, horodatée du 12 novembre à 22 h 25. **« Protocole inchangé » vaut donc aussi pour l'environnement logiciel**, ce qui n'allait pas de soi et n'avait pas été exigé par le protocole initial.

### 6.2 Empreintes des scripts réutilisés sans modification

Les huit empreintes SHA-256 inscrites au § 9 du protocole du 4 novembre (`arbres_coeur_v1.py`, `recherche_hp_arbres_v1.py`, `evaluer_arbres_imbrique_v1.py`, `comparaison_equitable_v14_v1.py`, `dl_coeur_v4.py`, `protocole_commun_v10.py`, `evaluer_dl_imbrique_v5.py`, `recherche_hp_dl_v4.py`) ont été **vérifiées conformes** par l'étape 0, qui refuse de lancer en cas d'écart.

### 6.3 Empreintes des fichiers nouveaux, enregistrées avant exécution

Consignées dans `results/empreintes_avant_v15.txt` :

```
68b564ce265728b6f800929032df3f4e046710e47f3cbe311beedbd2c830d2b5  corpus_v15/phenotype_drug_dataset_v15.csv
9d5512543016cb89c612e6213326f4b0662444b79f2dd9aec31acd877ac80728  regles_v15_monogene.csv
1cb99ff63246669c1a2438f9776b93b00538c67981d89ef92d7cf6d51f28dfc6  regles_v15_multigene.csv
8e7b302fd95c0625ebfca2a94e129d5575f01e4f07d1648baa58daa3e63ba1d0  evaluer_dl_imbrique_v6.py
26acdf3b962a627f58fcf19b374356c78ed5453567e2c9bb52375358830c7b28  comparaison_equitable_v14_v2.py
f0bcb993e6621e3a5a60c6ff79eeba6d1f38f299554176ff41643d233595b871  lancer_comparaison_equitable_v15.sh
```

### 6.4 Reproductibilité du corpus par un tiers

L'empreinte du corpus v15 a été obtenue de **trois sources indépendantes** : le fichier présent sur la machine d'exécution au moment du lancement, le fichier archivé sur le dépôt GitHub (branche `sauvegarde-2026-11-02`, commit `13be3fb`), et une reconstruction menée séparément à partir des seuls scripts du dépôt, dans un autre environnement. Les trois donnent `68b564ce265728b6f800929032df3f4e046710e47f3cbe311beedbd2c830d2b5`. Même concordance entre machine et dépôt pour les deux fichiers de règles.

**Le corpus v15 est donc reconstructible à l'identique par un tiers disposant du seul dépôt.** Cette propriété n'était pas établie pour les corpus antérieurs.

### 6.5 Horodatage de l'exécution

| Étape | Début |
| --- | --- |
| 0/7 vérifications bloquantes | 12 nov. 22 h 25 min 03 |
| 1/7 DL configuration 35 figée | 12 nov. 22 h 25 min 09 |
| 2/7 recherche DL | 12 nov. 22 h 32 min 04 |
| 3/7 évaluation DL | 12 nov. 23 h 06 min 58 |
| 4/7 recherche XGBoost | 12 nov. 23 h 15 min 50 |
| 5/7 évaluation XGBoost | 13 nov. 01 h 46 min 48 |
| 6/7 recherche puis évaluation Random Forest | 13 nov. 01 h 58 min 45 |

Commande : `bash lancer_comparaison_equitable_v15.sh 8`, journal complet dans `results/log_lancement_comparaison_v15.txt`.

L'étape 1 a produit les 25 prédictions hors-pli attendues (5 plis × 5 graines) en 6 min 55 s, sans erreur.

---

## 7. Transparence : ce qui a déjà été vu des sorties

Dans le même esprit que le § 2 du protocole du 4 novembre, et pour que rien ne soit présenté après coup :

- **Une ligne de journal a été lue** le 12 novembre à 22 h 36, en vérifiant que l'étape 1 fonctionnait : `{'quoi': 'c35_cal', 'config': 35, 'pli': 5, 'graine': 0, 'f1_macro': 0.998, 'CER_strict': 0.0097}`. Il s'agit d'une métrique d'un seul pli et d'une seule graine du bras de référence, lue à des fins de contrôle d'exécution. Elle n'a pas été comparée aux chiffres de la v14 et n'a motivé aucune décision.
- **Trois lignes du journal de recherche RF** ont été lues le 13 novembre au matin pour estimer le temps restant (`config 13 pli 2/3/4, F1val 0,992-0,994`). Ce sont des F1 de validation interne d'une configuration candidate, utilisés uniquement pour le chronométrage.
- **Aucune autre sortie n'a été consultée.** Les fichiers d'analyse des étapes 1 à 6 n'ont pas été ouverts ; aucune comparaison entre modèles ni entre corpus n'a été faite.
- **Attente déclarée a priori, inchangée depuis le protocole du 4 novembre** : XGBoost est attendu au moins aussi bon que le DL en F1 macro. Elle ne guide aucun choix de cet amendement.

---

## 8. Ce que cet amendement ne fait pas

- Il ne modifie **aucune mesure**, aucune statistique, aucun intervalle, et pas la marge δ = 0,001.
- Il ne modifie **pas la règle de décision** ni le traitement des comparaisons multiples.
- Il ne touche **pas à l'ensemble final** de 138 familles, qui reste non lu et dont l'évaluation unique fera l'objet d'un gel écrit distinct.
- Il ne remplace **aucun modèle de l'application** : conformément au § 8 du protocole, un éventuel avantage d'un arbre modifierait la justification écrite du choix du DL, et le choix du modèle de référence serait discuté avec le Pr. Ghedira.

---

## 9. Fichiers de référence

- Protocole figé : `Protocole_comparaison_equitable_DL_XGB_RF_v14_4nov2026.md`
- Amendement 1 : `Amendement_1_protocole_comparaison_equitable_v14_5nov2026.md`
- Corrections de règles et textes sources : `Regles_corrigees_v15_textes_sources_12nov2026.md`
- Journal de la session de construction : `Journal_de_Bord_12nov2026_regles_v15.md`
- Script de lancement : `Model_v8_7_9_10/scripts/lancer_comparaison_equitable_v15.sh`
- Journal d'exécution : `Model_v8_7_9_10/results/log_lancement_comparaison_v15.txt`
- Empreintes avant exécution : `Model_v8_7_9_10/results/empreintes_avant_v15.txt`
- Dépôt : branche `sauvegarde-2026-11-02`, commits `bb30343` (règles), `13be3fb` (corpus), `12b6610` (scripts d'exécution).
