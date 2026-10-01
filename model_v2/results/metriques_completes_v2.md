# Metriques completes — Dataset v2

Dataset : 46117 lignes, 31 genes, 437 medicaments
Protocole : StratifiedKFold 5 folds, scaler intra-fold, RandomOverSampler sur train

## Vue d ensemble

| Modele | Macro-F1 | Weighted-F1 | Balanced Acc. | Critical Error Rate |
|--------|----------|-------------|---------------|---------------------|
| DL | 0.88 | 0.9304 | 0.9475 | 0.0571 (749/13120) |
| XGBoost | 0.9541 | 0.9786 | 0.9722 | 0.0366 (480/13120) |
| RandomForest | 0.9319 | 0.9563 | 0.9465 | 0.0422 (554/13120) |

## Detail par classe

### DL

| Classe | Precision | Recall | F1 | Support |
|--------|-----------|--------|----|---------|
| ADAPTER_DOSE | 0.9868 | 0.9152 | 0.9497 | 23454 |
| EVITER | 0.8955 | 0.9232 | 0.9092 | 13120 |
| STANDARD | 0.593 | 0.9808 | 0.7391 | 520 |
| SURVEILLER | 0.8779 | 0.971 | 0.9221 | 9023 |

### XGBoost

| Classe | Precision | Recall | F1 | Support |
|--------|-----------|--------|----|---------|
| ADAPTER_DOSE | 0.9951 | 0.9872 | 0.9912 | 23454 |
| EVITER | 0.9761 | 0.9565 | 0.9662 | 13120 |
| STANDARD | 0.8325 | 0.9558 | 0.8899 | 520 |
| SURVEILLER | 0.9499 | 0.9892 | 0.9692 | 9023 |

### RandomForest

| Classe | Precision | Recall | F1 | Support |
|--------|-----------|--------|----|---------|
| ADAPTER_DOSE | 0.9806 | 0.9756 | 0.9781 | 23454 |
| EVITER | 0.9359 | 0.928 | 0.932 | 13120 |
| STANDARD | 0.8279 | 0.9346 | 0.878 | 520 |
| SURVEILLER | 0.931 | 0.9479 | 0.9394 | 9023 |

## Critical Error Rate

Proportion de cas EVITER predits comme STANDARD ou SURVEILLER.
Erreur cliniquement grave : contre-indication non signalee au prescripteur.

- **DL** : 749 / 13120 = 0.0571
- **XGBoost** : 480 / 13120 = 0.0366
- **RandomForest** : 554 / 13120 = 0.0422