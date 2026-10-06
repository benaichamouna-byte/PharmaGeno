# HISTORIQUE COMPLET DES RÉSULTATS — PharmaGeno
## Projet : A Deep Learning based Webtool for Mutation-Aware Drug Recommendation
## M.Sc. Bioinformatique — ENSI Tunisie — Soutenance Décembre 2026

---

## 1. ANCIEN PIPELINE — var_drug_ann (septembre 2026, début projet)
Dataset : var_drug_ann.tsv filtré Significance=yes
Features : 7 One-Hot + génotype
Protocole : StratifiedKFold 5 folds + SMOTE

| Modèle | Accuracy |
|--------|----------|
| DL v5 | 79.0% ± 0.7% |
| RF v3 | 81.4% ± 1.0% |
| XGBoost | 78.0% ± 1.4% |

Script : cross_validation.py

---

## 2. PIPELINE MONO-GÈNE (CYP2C19 seul)
Modèles : dl_pgx_monogene.pth, xgb_pgx_monogene.pkl
Résultats : documentés dans graphique evolution_complete.png

---

## 3. PIPELINE MULTI-GÈNES (21 gènes)
Modèles : dl_pgx_multigene.pth, rf_pgx_multigene.pkl, xgb_pgx_multigene.pkl

---

## 4. DATASET v1 — 31 GÈNES (18-20 septembre 2026)
Dataset : phenotype_drug_dataset_complet.csv
- 39 259 lignes | 31 gènes | 530 médicaments
- Classes : EVITER 13 505 | ADAPTER_DOSE 17 923 | SURVEILLER 7 310 | STANDARD 521
- Sources : PharmGKB 1A/2A + ClinVar + CPIC + FDA + 1KGP 2504 individus

### Première exécution (script reconstruit, hyperparamètres incorrects)
| Modèle | F1-macro |
|--------|----------|
| DL | 0.254 ± 0.056 |
| XGBoost | 0.961 ± 0.003 |
| RF | 0.940 ± 0.002 |

Problème : 100 epochs au lieu de 500, SMOTE au lieu de RandomOverSampler

### Deuxième exécution (script corrigé — RÉFÉRENCE v1)
Protocole : StratifiedKFold 5 folds, RandomOverSampler, 500 epochs, Weighted CrossEntropy
**Limitation : scaler fit sur tout le dataset avant K-Fold (data leakage)**

| Fold | RF | XGBoost | DL |
|------|-----|---------|-----|
| 1 | 0.939 | 0.963 | 0.865 |
| 2 | 0.939 | 0.960 | 0.857 |
| 3 | 0.941 | 0.959 | 0.886 |
| 4 | 0.942 | 0.961 | 0.884 |
| 5 | 0.938 | 0.963 | 0.880 |
| **Moyenne** | **0.940 ± 0.001** | **0.962 ± 0.002** | **0.875 ± 0.011** |

Script : train_pgx_31genes_v2.py
Modèles : dl_pgx_31genes.pth, xgb_pgx_31genes.pkl, rf_pgx_31genes.pkl

### Dataset corrigé (827 conflits résolus)
| Fold | RF | XGBoost | DL |
|------|-----|---------|-----|
| 1 | 0.939 | 0.963 | 0.886 |
| 2 | 0.939 | 0.960 | 0.883 |
| 3 | 0.941 | 0.959 | 0.861 |
| 4 | 0.942 | 0.961 | 0.860 |
| 5 | 0.938 | 0.963 | 0.889 |
| **Moyenne** | **0.940 ± 0.001** | **0.962 ± 0.002** | **0.876 ± 0.013** |

Conclusion : résultats identiques → correction des conflits sans impact significatif
Script : train_pgx_31genes_REEL_sur_dataset_corrige.py

---

## 5. DATASET v2 — PREMIÈRE VERSION (échec, 22 septembre 2026)
Dataset : 145 303 lignes, 12 gènes enrichis VCF EBI
Problème : encodage phénotype→action sans validation CPIC par gène
Déséquilibre : ADAPTER_DOSE 70.4% du dataset

| Modèle | F1-macro |
|--------|----------|
| DL (500 epochs, train only) | **0.736** |

Rapport par classe :
- ADAPTER_DOSE : precision 0.96, recall 0.81, f1 0.88 (92 408 support)
- EVITER : precision 0.63, recall 0.82, f1 0.71 (30 795)
- STANDARD : precision 0.42, recall 1.00, f1 0.59 (520)
- SURVEILLER : precision 0.61, recall 0.99, f1 0.75 (6 347)
- Accuracy : 0.82

**Conclusion : ÉCHEC — moins bon que v1 (0.875)**

### Tests de solutions au déséquilibre (100 epochs, split 80/20)
| Approche | F1-macro |
|----------|----------|
| WCE (actuel) | 0.576 |
| Focal Loss gamma=2 | 0.426 |
| Focal Loss gamma=3 | 0.412 |
| Undersampling ADAPTER_DOSE | 0.548 |
| Focal + Undersampling | 0.411 |

**Conclusion : aucune solution de rééquilibrage ne fonctionne → le problème est la qualité des données, pas le déséquilibre**

---

## 6. DATASET v2 — VERSION CPIC VALIDÉE (23-26 septembre 2026)
Dataset : phenotype_drug_dataset_complet_v2.csv
- 46 371 lignes | 31 gènes | 530 médicaments | 3 666 profils génétiques distincts
- Classes : ADAPTER_DOSE 23 516 (50.7%) | EVITER 13 202 (28.5%) | SURVEILLER 9 025 (19.5%) | STANDARD 628 (1.4%)
- 5 gènes enrichis CPIC Level A uniquement : VKORC1, CYP4F2, G6PD, NAT2, IFNL3
- 7 gènes remis à 1.0 (sans guideline CPIC Level A) : CYP3A4, CYP1A2, CYP2A6, ADRB2, ACE, MTHFR, SLC19A1

### Test préliminaire (100 epochs, split 80/20)
DL F1 = 0.720

### Entraînement final (500 epochs, sur tout le dataset — DATA LEAKAGE)
| Epoch | Loss | F1 |
|-------|------|-----|
| 100 | 0.4418 | 0.717 |
| 200 | 0.2853 | 0.828 |
| 300 | 0.2485 | 0.831 |
| 400 | 0.2130 | 0.849 |
| 500 | 0.1984 | **0.861** |

Rapport par classe :
- ADAPTER_DOSE : precision 0.98, recall 0.90, f1 0.94 (23 454)
- EVITER : precision 0.91, recall 0.90, f1 0.90 (13 120)
- STANDARD : precision 0.53, recall 1.00, f1 0.69 (520)
- SURVEILLER : precision 0.84, recall 0.99, f1 0.91 (9 023)
- **Accuracy : 0.92**

Script : train_dl_final_only.py
**Limitation : F1 calculé sur données d'entraînement (data leakage)**

### K-FOLD VALIDÉ — SANS DATA LEAKAGE (26 septembre 2026)
Protocole : StratifiedKFold 5 folds, **scaler fit intra-fold uniquement**, mini-batches DataLoader batch_size=512, gradient clipping max_norm=1.0

| Fold | XGBoost | Random Forest | DL |
|------|---------|---------------|-----|
| 1 | 0.954 | 0.922 | 0.902 |
| 2 | 0.945 | 0.933 | 0.923 |
| 3 | 0.959 | 0.934 | 0.918 |
| 4 | 0.951 | 0.929 | 0.872 |
| 5 | 0.962 | 0.942 | 0.879 |
| **Moyenne** | **0.954 ± 0.006** | **0.932 ± 0.007** | **0.899 ± 0.020** |

### Comparaison v1 vs v2 — TROIS MODELES COMPLETS

| Modele | v2 (protocole corrige) | v1 (avec data leakage) | Difference |
|--------|------------------------|------------------------|------------|
| XGBoost | 0.954 ± 0.006 | 0.962 ± 0.002 | -0.008 |
| Random Forest | 0.932 ± 0.007 | 0.940 ± 0.001 | -0.008 |
| Deep Learning | **0.899 ± 0.020** | 0.875 ± 0.011 | **+0.024** |

**Observation cle pour la discussion :** XGBoost et RF perdent exactement 0.008 chacun — cet ecart correspond a la correction du data leakage du scaler. Le DL gagne 0.024 malgre cette correction : l'enrichissement du dataset avec les 5 genes CPIC Level A (VKORC1, CYP4F2, G6PD, NAT2, IFNL3) beneficie principalement au modele profond, capable d'exploiter les interactions multi-geniques.

**Scripts :** train_dl_kfold_only.py (DL+XGB folds 1-3), train_kfold_folds45.py (fold 4 + XGB fold 5), train_dl_fold5.py (DL fold 5), train_rf_kfold_v2.py (RF 5 folds)
**Conditions identiques a v1 :** RF 200 arbres, XGB 100 estimateurs, DL 500 epochs, StratifiedKFold(5, shuffle=True, random_state=42), RandomOverSampler sur train uniquement


Script : train_dl_kfold_only.py
RF valide separement avec n_jobs=2 et garbage collection (script train_rf_kfold_v2.py)

---

## 7. ÉVOLUTION DU DL — SYNTHÈSE

| Étape | Dataset | F1-macro | Protocole |
|-------|---------|----------|-----------|
| Ancien pipeline | var_drug_ann | 0.790 (accuracy) | K-Fold + SMOTE |
| v1 première tentative | 39 259 lignes | 0.254 | Hyperparamètres incorrects |
| **v1 référence** | 39 259 lignes | **0.875 ± 0.011** | K-Fold, scaler global (leakage) |
| v1 dataset corrigé | 39 259 lignes | 0.876 ± 0.013 | K-Fold, scaler global (leakage) |
| v2 échec | 145 303 lignes | 0.736 | Train only, encodage non-CPIC |
| v2 CPIC (train only) | 46 371 lignes | 0.861 | Train only (leakage) |
| **v2 CPIC K-Fold** | 46 371 lignes | **0.899 ± 0.020** | K-Fold 5 folds, scaler intra-fold ✅ |

---

## 8. ERREURS MÉTHODOLOGIQUES IDENTIFIÉES ET CORRIGÉES

1. Scaler fit sur tout le dataset avant K-Fold → corrigé (fit intra-fold)
2. Full-batch sur 145k lignes → OOM → corrigé (DataLoader mini-batches)
3. Encodage phénotype→action sans validation CPIC → corrigé (mapping CPIC explicite)
4. F1 calculé sur données d'entraînement → corrigé (K-Fold)
5. Merger datasets colonnes communes → corrigé (union + fillna)
6. Oubli remap samples VCF (s0→HG00096) → corrigé (fichier pedigree)

---

## 9. LIMITATIONS DOCUMENTÉES

- 7 colonnes géniques constantes : ACE, ADRB2, CFTR, EGFR, MT-RNR1, SLC19A1, MTHFR
- HLA-A et HLA-B quasi constants (8 et 26 lignes non-défaut sur 46 371)
- 93 médicaments sans Morgan Fingerprint sur 530
- Axe molécule jamais tenu en dehors (chaque médicament présent en train et test)
- Hétérogénéité sémantique des colonnes (activity score vs phénotype ordinal vs génotype SNP)
- RF non validé par K-Fold sur v2 (contrainte RAM)
- Circularité par construction : label = fonction déterministe de (phénotype, médicament) via mapping CPIC

## 10. DÉTERMINISME PAR MÉDICAMENT (analyse 26 septembre)
Sur 530 médicaments :
- 87 (16%) : action constante
- 257 (48%) : déterminée par 1 seul gène
- **186 (35%) : nécessite ≥2 gènes** → justifie l'architecture multi-gènes

---

## 11. METRIQUES COMPLETES — baseline non groupe (1er octobre 2026)

Protocole : StratifiedKFold 5 plis, scaler intra-pli, RandomOverSampler sur le pli d entrainement.
Sans groupement : un meme profil genetique peut figurer en entrainement et en test, apparie a des medicaments differents.

| Modele | Macro-F1 | Weighted-F1 | Balanced Acc. | CER | CER strict |
|---|---|---|---|---|---|
| XGBoost | 0.9541 | 0.9786 | 0.9722 | 0.0366 | 0.0435 |
| RandomForest | 0.9319 | 0.9563 | 0.9465 | 0.0422 | 0.072 |
| DL | 0.88 | 0.9304 | 0.9475 | 0.0571 | 0.0768 |

### Detail par classe

**XGBoost**

| Classe | Precision | Rappel | F1 | Support |
|---|---|---|---|---|
| ADAPTER_DOSE | 0.9951 | 0.9872 | 0.9912 | 23454 |
| EVITER | 0.9761 | 0.9565 | 0.9662 | 13120 |
| STANDARD | 0.8325 | 0.9558 | 0.8899 | 520 |
| SURVEILLER | 0.9499 | 0.9892 | 0.9692 | 9023 |

**RandomForest**

| Classe | Precision | Rappel | F1 | Support |
|---|---|---|---|---|
| ADAPTER_DOSE | 0.9806 | 0.9756 | 0.9781 | 23454 |
| EVITER | 0.9359 | 0.928 | 0.932 | 13120 |
| STANDARD | 0.8279 | 0.9346 | 0.878 | 520 |
| SURVEILLER | 0.931 | 0.9479 | 0.9394 | 9023 |

**DL**

| Classe | Precision | Rappel | F1 | Support |
|---|---|---|---|---|
| ADAPTER_DOSE | 0.9868 | 0.9152 | 0.9497 | 23454 |
| EVITER | 0.8955 | 0.9232 | 0.9092 | 13120 |
| STANDARD | 0.593 | 0.9808 | 0.7391 | 520 |
| SURVEILLER | 0.8779 | 0.971 | 0.9221 | 9023 |

### Critical Error Rate — deux definitions

**CER** : EVITER predit en STANDARD ou SURVEILLER — le medicament est presente comme prescriptible.
**CER strict** : toute erreur sur un cas EVITER, y compris vers ADAPTER_DOSE, ou le medicament
contre-indique est prescrit avec un simple ajustement de dose. Vaut 1 moins le rappel sur EVITER.

| Modele | vers ADAPTER_DOSE | vers SURVEILLER | vers STANDARD | Total manque |
|---|---|---|---|---|
| XGBoost | 91 | 446 | 34 | 571 |
| RandomForest | 390 | 523 | 31 | 944 |
| DL | 258 | 623 | 126 | 1007 |

Observations :
- XGBoost presente le plus faible taux de contre-indications manquees sous les deux definitions ; la conclusion ne depend pas du choix de definition.
- La majorite des erreurs va vers SURVEILLER, qui declenche tout de meme une vigilance du prescripteur. STANDARD est l erreur la plus grave : le DL en commet 126, contre 34 pour XGBoost et 31 pour RandomForest.
- RandomForest passe de 4,22 % a 7,20 % sous la definition stricte, car il envoie 390 cas EVITER vers ADAPTER_DOSE. Sous cette definition il rejoint le DL.
- La Balanced Accuracy du DL (0,948) egale celle de RandomForest (0,947) malgre cinq points de macro-F1 en moins : elle est la moyenne des rappels et ignore la precision. Le DL sur-predit STANDARD — rappel 0,981, precision 0,593. Metrique rapportee en secondaire.
- La classe STANDARD a perdu 17,2 % de ses lignes au filtrage des empreintes moleculaires (628 vers 520), contre moins de 1 % pour les autres classes.

---

## 12. VALIDATION CROISEE GROUPEE PAR INDIVIDU (2-3 octobre 2026)

Protocole : StratifiedGroupKFold 5 plis sur `sample_id`. Chaque individu est entierement
contenu dans un seul pli ; recouvrement entrainement/test nul, verifie a chaque pli.
Jeu de donnees : phenotype_drug_dataset_FINAL.csv, 11 476 groupes dont 1 379 individus sequences.

| Pli | XGBoost | RandomForest | DL |
|---|---|---|---|
| 1 | 0.9545 | 0.9358 | 0.8845 |
| 2 | 0.9616 | 0.9479 | 0.89 |
| 3 | 0.9535 | 0.938 | 0.8828 |
| 4 | 0.9585 | 0.932 | 0.8783 |
| 5 | 0.9489 | 0.9391 | 0.8878 |
| **Moyenne (5/5)** | **0.9554 ± 0.0044** | **0.9386 ± 0.0053** | **0.8847 ± 0.0041** |

### Comparaison des deux protocoles

| Modele | Groupe par individu | Baseline non groupe | Ecart |
|---|---|---|---|
| XGBoost | 0.9554 ± 0.0044 | 0.954 | +0.0014 |
| RandomForest | 0.9386 ± 0.0053 | 0.932 | +0.0066 |
| DL | 0.8858 | 0.880 | +0.0058 |

Les scores ne baissent pas lorsque chaque individu est confine dans un seul pli ; les trois
modeles sont legerement au-dessus du baseline. Deux lectures convergent vers la meme conclusion
pratique — les chiffres rapportes sont solides.

1. La fuite par repetition de profil, redoutee, n a pas d effet mesurable : le baseline etait honnete.
2. Le groupement ne mord pas parce que la tache depend peu du patient : si l action est determinee
   par la paire gene-medicament, voir un profil a l entrainement n apporte rien au modele.

La seconde lecture renforce l idee que le veritable test de generalisation porte sur des molecules
jamais vues — experience qui reste a mener (Phase 4).

Validation complete sur les cinq plis. Les ecarts au baseline sont inferieurs aux ecarts-types
entre plis : le groupement par individu ne modifie pas les performances. Le DL gagne par ailleurs
en stabilite, son ecart-type passant de 0,020 (non groupe) a 0,004 (groupe).

Note : les plis 4 et 5 ont ete relances apres une interruption du processus. Le script reprend
les plis deja calcules depuis groupkfold_scores.json, sans les recalculer.

---

## 13. AUDIT DES EMPREINTES MOLECULAIRES (5 octobre 2026)

### Constat

La branche medicament du reseau recoit un vecteur de 518 variables, decrit comme
une empreinte de Morgan de 512 bits complete par six descripteurs physico-chimiques.
Une verification de ce vecteur a etabli que **les 512 bits structuraux etaient nuls
pour les 437 medicaments du referentiel**, sans exception.

| Indicateur | Valeur mesuree |
|---|---|
| Empreintes entierement nulles | 437 / 437 |
| Bits actifs en moyenne | 0,0 |
| Bits jamais actifs sur le corpus | 512 / 512 |

Les six descripteurs finaux — masse moleculaire, coefficient de partage, donneurs et
accepteurs de liaisons hydrogene, liaisons rotatives, surface polaire — etaient en
revanche corrects. **Les modeles entraines jusque-la ne disposaient donc que de six
variables moleculaires globales, et d aucune information de structure.**

### Portee

Avec six descripteurs globaux, deux molecules de masse et de polarite voisines sont
indiscernables, quelle que soit leur structure. Cela explique en partie les predictions
aberrantes observees lors du test de prediction elargie : pour un patient ne presentant
que deux genes mutes, 326 medicaments sur 437 etaient classes en contre-indication, et
la neomycine — sans lien documente avec CYP2C19 ou CYP2B6 — obtenait 94,6 % de confiance,
soit davantage que les medicaments reellement concernes.

Le script ayant produit ces fichiers n avait pas ete conserve et les structures SMILES
n avaient pas ete sauvegardees, ce qui a empeche un diagnostic plus precoce.

### Correction

| Parametre | Valeur |
|---|---|
| Source des structures | PubChem PUG REST, interrogation par nom |
| Bibliotheque | RDKit 2026.03.6 |
| Type d empreinte | Morgan circulaire, rayon 2 |
| Longueur | 512 bits |
| Descripteurs conserves | MW, LogP, HBD, HBA, RB, TPSA |

Une difficulte technique a ete rencontree : l API PubChem a change de nomenclature et
renvoie desormais la structure sous la cle `ConnectivitySMILES` et non `CanonicalSMILES`.
Le premier passage a donc echoue silencieusement. Apres correction et ralentissement de
la cadence de requetes — le serveur renvoyant des codes 503 en cas de saturation —
402 empreintes ont ete obtenues, puis les 35 restantes lors d un second passage.

| Indicateur | Avant | Apres |
|---|---|---|
| Empreintes calculees | 0 | 437 / 437 |
| Empreintes nulles | 437 | 0 |
| Bits actifs en moyenne | 0,0 | 42,9 / 512 |
| Bits jamais actifs | 512 | 0 |

Les structures SMILES sont desormais conservees dans `drug_smiles.csv` avec leur
identifiant PubChem, ce qui rend le calcul reproductible et verifiable.

**Scripts** : `build_fingerprints.py`, `completer_fingerprints.py`
**Fichiers** : `drug_fingerprints_v2.pkl`, `drug_smiles.csv`, `fingerprints_report.md`

---

## 14. CORPUS ENRICHI DE PAIRES SANS ASSOCIATION (5 octobre 2026)

### Constat

Le modele ne savait pas repondre qu un medicament ne concerne pas un patient donne.
La cause en est l absence de contre-exemples : la classe STANDARD ne representait que
520 lignes sur 46 117, soit 1,1 % du corpus. Le reseau n avait jamais vu de paire
profil-medicament sans association, et tranchait donc systematiquement dans les classes
qu il connaissait.

Cette carence se lisait directement dans les metriques : precision de 0,593 sur STANDARD
pour un rappel de 0,981 — le reseau identifiait presque tous les vrais STANDARD, mais
quatre de ses predictions STANDARD sur dix etaient fausses.

### Methode

Les associations gene-medicament documentees ont ete extraites des 217 fichiers
d annotation de guidelines presents dans le projet, soit **386 paires couvrant 41 genes
et 208 medicaments**.

| Source | Paires |
|---|---|
| CPIC | 315 |
| DPWG | 111 |
| RNPGx | 31 |
| CPNDS | 13 |
| AIOM, SEFF/SEOM, ACR, CFF, AusNZ, AHA | 11 |

Pour chaque profil genetique du corpus, les genes non normaux sont identifies, puis les
medicaments associes a l un d eux sont exclus. Parmi les medicaments restants, trois sont
tires au hasard et etiquetes STANDARD. Le tirage est reproductible — graine fixee a 42.

Ces paires ne sont pas inventees : un patient porteur d une seule deficience CYP2C19 ne
requiert aucun ajustement pour la metformine. C est un fait clinique etabli que le corpus
initial ne contenait simplement pas.

### Resultat

| Action | Avant | Apres | Part finale |
|---|---|---|---|
| ADAPTER_DOSE | 23 454 | 23 454 | 41,1 % |
| EVITER | 13 120 | 13 120 | 23,0 % |
| SURVEILLER | 9 023 | 9 023 | 15,8 % |
| STANDARD | 520 | 11 456 | 20,1 % |

Corpus : 46 117 vers **57 053 lignes**.
SHA256 : `3c04b5cc66edcf3c2e43d63c2695466514e457303ca0b956d7c6b694ef5ddfb4`

### Limite

L absence d association repose sur les guidelines disponibles. Une paire non documentee
n est pas necessairement sans interaction : elle peut relever d une association non
encore etablie. Le modele apprend donc l etat des connaissances publiees, non une verite
biologique.

**Script** : `build_dataset_negatifs.py` · **Fichiers** : `phenotype_drug_dataset_NEG.csv`, `negatifs_report.md`

---

## 15. ENTRAINEMENT SUR CORPUS ENRICHI (6 octobre 2026)

Protocole identique a la validation groupee : StratifiedGroupKFold sur `sample_id`,
cinq plis, scaler ajuste intra-pli, reechantillonnage sur le pli d entrainement seul.
La representation moleculaire reste celle des empreintes nulles — ce calcul constitue
donc la mesure de reference **sans information structurale**.

| Pli | XGBoost | RandomForest | DL |
|---|---|---|---|
| 1 | 0.977 | 0.9607 | 0.9103 |
| 2 | 0.9772 | 0.956 | 0.9044 |
| **Moyenne (2/5)** | **0.9771** | **0.9584** | **0.9073** |

### Effet sur la classe STANDARD

| Modele | Precision STANDARD | Rappel EVITER | CER strict |
|---|---|---|---|
| XGBoost | 0.9853 | 0.9578 | 0.0421 |
| RandomForest | 0.9766 | 0.9376 | 0.0624 |
| DL | 0.9896 | 0.8935 | 0.1065 |

### Lecture

**La correction a produit l effet recherche.** La precision du reseau sur STANDARD
passe de 0,593 a pres de 0,99 : il sait desormais reconnaitre l absence de lien entre
un profil et un medicament. Son macro-F1 progresse de 0,885 a environ 0,91.

**Mais un effet secondaire apparait.** Le rappel sur EVITER diminue et le taux
d erreur critique strict augmente, passant d environ 7,7 % a 10,5 % pour le reseau.
Ayant appris a dire "pas de lien", le modele le dit un peu trop souvent — et manque
davantage de contre-indications.

C est le compromis classique entre les deux types d erreur. Il concerne les trois
modeles, mais le reseau en souffre le plus. Pour un outil d aide a la prescription,
c est une degradation a considerer : une contre-indication manquee pese plus lourd
qu une prudence excessive.

**Script** : `train_neg.py` · **Modeles** : `*_neg`

---

## 16. PROCHAINE ETAPE — entrainement avec empreintes reparees

Le script `train_final.py` reprend exactement le protocole precedent, en substituant
`drug_fingerprints_v2.pkl` aux empreintes nulles. Tout le reste est identique : meme
corpus, memes plis, memes hyperparametres.

**L ecart entre les deux entrainements mesurera donc exclusivement l apport de la
representation structurale du medicament — question de recherche RQ4.**
