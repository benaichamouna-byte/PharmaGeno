## Chapitre 4 : Méthodes (modèles, calibration, abstention, protocole)

Ce chapitre décrit les modèles, leur entraînement, la calibration, l'abstention et le protocole d'évaluation ; chaque réglage est lu dans les scripts du projet. Les formules complémentaires, le détail des réglages et l'origine de chaque valeur sont en annexe D.

### 4.1 Principe général

Le réseau principal, dit « de profil », lit le profil génétique d'un patient (34 colonnes, chapitre 3) et produit en une passe, pour chacun des 189 médicaments, une distribution de probabilité sur les quatre classes STANDARD, ADAPTER\_DOSE, SURVEILLER et EVITER : le médicament n'est donc pas une entrée mais un groupe de sorties. L'architecture antérieure, qui donnait le médicament en entrée par une description chimique, n'a pas été retenue (annexe D.1). Un second réseau, dit « de choix », compare entre eux les médicaments d'une même classe ATC de niveau 4. Les deux réseaux sont programmés avec PyTorch (Paszke et al., 2019).

### 4.2 Réseau de profil

**Architecture.** Perceptron multicouche à deux couches cachées de 1 024 unités (ReLU), suivies d'une couche linéaire de 756 sorties regroupées en 189 groupes de 4 (figure 4.1), avec un Dropout de 0,1 (Srivastava et al., 2014) après chaque activation. Le réseau compte 1 860 340 paramètres ; profondeur, largeur et Dropout résultent de la recherche de la section 4.3.

::: {custom-style="FigureImg"}
![](fig/fig_4_1.png){width=10cm}
:::

::: {custom-style="LegendeFigure"}
Figure 4.1 : Architecture du réseau de profil.
:::

**Perte et optimisation.** Entropie croisée sur chaque case (profil, médicament) étiquetée, les cases sans étiquette étant ignorées, avec un lissage d'étiquettes de 0,05 (Szegedy et al., 2015 ; Müller et al., 2019). Chaque classe c est pondérée, pour compenser le déséquilibre, par :

$$w_c = \lambda_c \left( \frac{N}{K\, n_c} \right)^{\alpha} \qquad (4.1)$$

où N est le nombre de cases étiquetées de l'entraînement, n\_c celui de la classe c, K = 4, et α = 0,5 et λ\_c = 1 dans la configuration retenue. Aucun rééchantillonnage n'est fait : interpoler entre deux profils produirait des génotypes qui n'existent pas. L'optimisation utilise Adam (Kingma et Ba, 2015), avec arrêt anticipé sur une validation interne (annexe D.2).

### 4.3 Choix de la configuration

Les hyperparamètres ont été choisis par une recherche aléatoire (Bergstra et Bengio, 2012) de 40 configurations, en validation croisée imbriquée pour que la performance ne soit jamais estimée sur les données qui ont servi à choisir (Cawley et Talbot, 2010). La configuration 35 est la meilleure dans les cinq plis ; elle est reprise sans nouveau réglage sur le corpus v15 (annexe D.3).

### 4.4 Calibration par mise à l'échelle de température

L'application affiche les probabilités et s'en sert pour s'abstenir ; le réseau est donc calibré par mise à l'échelle de température (Guo et al., 2017), les logits z étant divisés par un scalaire T choisi en minimisant la log-vraisemblance négative sur la validation interne, dans l'intervalle [0,05 ; 5] :

$$q_{n,k}(T) = \frac{\exp(z_{n,k}/T)}{\sum_{j=1}^{K} \exp(z_{n,j}/T)} \qquad (4.2)$$

Cette méthode a un seul paramètre et ne change pas la classe prédite. La calibration est mesurée par l'erreur de calibration attendue (ECE, annexe D.4).

### 4.5 Abstention

Un outil qui répond toujours transforme une incertitude en affirmation. La confiance d'une prédiction est la probabilité maximale calibrée du groupe du médicament, et le système s'abstient quand elle est inférieure ou égale à un seuil : c'est la classification sélective (Geifman et El-Yaniv, 2017), dont la couverture et le risque sont définis en annexe D.5. Faute de valeur de référence publiée pour un risque clinique acceptable, les seuils sont les quantiles de la confiance sur les prédictions hors pli (tableau 4.1) : un seuil est donc défini par la part de prédictions qu'il écarte, non par le risque qu'il garantit.

::: {custom-style="LegendeTableau"}
Tableau 4.1 : Part de prédictions écartées et seuil de confiance correspondant (corpus v15)
:::

| Part de prédictions écartées | Seuil de confiance |
| --- | --- |
| 0,5 % | 0,9934 |
| 1 % | 0,9981 |
| 2 % | 0,9994 |
| 5 % | 0,9998 |

L'application emploie le seuil du niveau 1 %, soit **0,9981**, calculé et enregistré avec le modèle. La capacité de la confiance à signaler les erreurs est mesurée par l'aire sous la courbe ROC (annexe D.5 ; section 6.3).

### 4.6 Réseau de choix au sein d'une classe ATC4

Pour un profil et une classe ATC4 d'au moins deux médicaments étiquetés (44 classes), le réseau de choix ordonne les candidats. Sa cible, convention du projet, est la loi uniforme sur l'ensemble des médicaments de la meilleure action disponible, un médicament EVITER n'y entrant jamais ; il est comparé à une référence qui ignore le profil, seule façon de mesurer l'apport de celui-ci (annexe D.6).

### 4.7 Modèles de comparaison

Sur des données tabulaires, les modèles à base d'arbres surpassent souvent les réseaux de neurones (Grinsztajn et al., 2022 ; Shwartz-Ziv et Armon, 2022). Le réseau est donc comparé à **XGBoost** (Chen et Guestrin, 2016) et au **Random Forest** (Breiman, 2001), qui reçoivent une ligne par couple (profil, médicament). L'égalité de traitement porte sur les plis, le budget de réglage, les graines, la calibration et un protocole figé d'avance, non sur la forme du problème, multitâche pour le réseau (annexe D.7).

### 4.8 Protocole d'évaluation

- **Découpage et répétitions :** découpage de la section 3.6, commun à tous les modèles ; 25 entraînements par condition (5 graines × 5 plis). Un bootstrap par profil (2 000 tirages) donne les intervalles à 95 % des différences.
- **Métriques :** F1 macro (métrique principale, l'exactitude étant trompeuse quand prédire STANDARD partout dépasse 85 %), « EVITER manqués », c'est-à-dire le complément du rappel de la classe EVITER et la mesure de sécurité du protocole, exactitude, log-loss et ECE ; leurs définitions sont en annexe D.8.
- **Règle de décision, écrite avant les résultats :** un modèle est supérieur si la borne basse de l'intervalle de la différence de F1 macro dépasse 0 ; équivalent si l'intervalle tient dans ±0,001 ; sinon, la différence est non tranchée.
- **Évaluation finale :** les 138 profils ne sont lus qu'une fois, après gel du protocole (section 6.7).

### 4.9 Modèles finaux de l'application

Les modèles de l'application sont entraînés une fois sur 1 116 profils, avec 125 profils de validation interne pour l'arrêt anticipé et la température ; les 138 profils finaux ne sont pas utilisés, ce que le programme vérifie (annexe D.9).

### 4.10 Limites assumées

1. La configuration 35, choisie sur le corpus v13, pourrait ne pas être la mieux adaptée à la v15 ; la température est de plus ajustée sur l'ensemble de l'arrêt anticipé, ce qui rend la calibration légèrement optimiste.
2. Les seuils d'abstention sont des quantiles, non des seuils de risque clinique (section 6.3).
3. Le réseau de choix n'a bénéficié d'aucune recherche d'hyperparamètres, et sa cible est une convention du projet.
4. Tout accord mesuré est un accord avec les règles ; les versions des bibliothèques ont été relevées après coup (annexe D.10).
