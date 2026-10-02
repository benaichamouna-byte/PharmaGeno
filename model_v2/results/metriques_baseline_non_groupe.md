# Metriques — baseline non groupe

> **Protocole : StratifiedKFold sans groupement.** Un meme profil genetique peut
> figurer en entrainement et en test, apparie a des medicaments differents. Les valeurs
> ci-dessous constituent donc une reference haute, non la validation finale. La validation
> groupee par individu, ou chaque patient est entierement contenu dans un seul pli, est
> rapportee separement.

Dataset : 46 117 lignes, 31 genes, 437 medicaments
Pretraitement : scaler ajuste intra-pli, RandomOverSampler sur le pli d entrainement

## Vue d ensemble

| Modele | Macro-F1 | Weighted-F1 | Balanced Acc. | CER | CER strict |
|---|---|---|---|---|---|
| XGBoost | 0.9541 | 0.9786 | 0.9722 | 0.0366 | 0.0435 |
| RandomForest | 0.9319 | 0.9563 | 0.9465 | 0.0422 | 0.072 |
| DL | 0.88 | 0.9304 | 0.9475 | 0.0571 | 0.0768 |

## Les deux definitions du Critical Error Rate

Le CER mesure la part des contre-indications que le modele ne signale pas comme telles.
Deux definitions coexistent, et leur ecart est informatif.

**CER** — EVITER predit en STANDARD ou SURVEILLER. Le medicament est presente comme
prescriptible, eventuellement sous surveillance.

**CER strict** — toute erreur sur un cas EVITER, y compris vers ADAPTER_DOSE.
Dans ce dernier cas le medicament contre-indique est prescrit avec un simple ajustement
de dose : la contre-indication est manquee. Le CER strict vaut 1 moins le rappel sur EVITER.

| Modele | CER | CER strict | Rappel EVITER |
|---|---|---|---|
| XGBoost | 0.0366 (480/13120) | 0.0435 (571/13120) | 0.9565 |
| RandomForest | 0.0422 (554/13120) | 0.072 (944/13120) | 0.928 |
| DL | 0.0571 (749/13120) | 0.0768 (1007/13120) | 0.9232 |

### Destination des cas EVITER mal classes

| Modele | vers ADAPTER_DOSE | vers SURVEILLER | vers STANDARD |
|---|---|---|---|
| XGBoost | 91 | 446 | 34 |
| RandomForest | 390 | 523 | 31 |
| DL | 258 | 623 | 126 |

Le classement des modeles est identique sous les deux definitions : **XGBoost** 
presente le plus faible taux de contre-indications manquees. Cette conclusion ne depend 
donc pas du choix de definition.

## Detail par classe

### XGBoost

| Classe | Precision | Rappel | F1 | Support |
|---|---|---|---|---|
| ADAPTER_DOSE | 0.9951 | 0.9872 | 0.9912 | 23454 |
| EVITER | 0.9761 | 0.9565 | 0.9662 | 13120 |
| STANDARD | 0.8325 | 0.9558 | 0.8899 | 520 |
| SURVEILLER | 0.9499 | 0.9892 | 0.9692 | 9023 |

### RandomForest

| Classe | Precision | Rappel | F1 | Support |
|---|---|---|---|---|
| ADAPTER_DOSE | 0.9806 | 0.9756 | 0.9781 | 23454 |
| EVITER | 0.9359 | 0.928 | 0.932 | 13120 |
| STANDARD | 0.8279 | 0.9346 | 0.878 | 520 |
| SURVEILLER | 0.931 | 0.9479 | 0.9394 | 9023 |

### DL

| Classe | Precision | Rappel | F1 | Support |
|---|---|---|---|---|
| ADAPTER_DOSE | 0.9868 | 0.9152 | 0.9497 | 23454 |
| EVITER | 0.8955 | 0.9232 | 0.9092 | 13120 |
| STANDARD | 0.593 | 0.9808 | 0.7391 | 520 |
| SURVEILLER | 0.8779 | 0.971 | 0.9221 | 9023 |

## Lecture de la Balanced Accuracy

La Balanced Accuracy est la moyenne des rappels par classe ; elle ignore la precision.
Le DL atteint 0,948, soit le niveau de RandomForest (0,947), tout en perdant pres de
cinq points de macro-F1. L ecart vient entierement de la classe STANDARD, ou le DL
obtient un rappel de 0,981 pour une precision de 0,593 : il identifie presque tous les
vrais STANDARD, mais quatre de ses predictions STANDARD sur dix sont fausses.
La Balanced Accuracy ne percoit pas ce defaut. Elle est rapportee en metrique secondaire ;
le macro-F1 reste la metrique principale.

## Classe STANDARD — fragilite documentee

STANDARD comptait 628 lignes avant le filtrage des medicaments sans empreinte moleculaire,
520 apres, soit une perte de 17,2 % contre moins de 1 % pour les autres classes.
C est la classe la plus rare du corpus (1,1 %) et celle qui a ete la plus amputee.
Sa precision chez le DL est le principal facteur limitant du macro-F1.