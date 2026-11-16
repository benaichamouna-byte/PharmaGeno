## Annexe D : Compléments sur les méthodes

Cette annexe donne le détail du chapitre 4 : architecture antérieure, écriture complète de la perte, recherche d'hyperparamètres, calibration, abstention, réseau de choix, comparaison des modèles, modèles finaux et origine des valeurs numériques du protocole. Les numéros de section entre parenthèses renvoient au chapitre 4 ou aux chapitres suivants.

### D.1 Architecture antérieure à représentation moléculaire

Cette alternative était l'architecture d'une étape antérieure du projet : deux branches, l'une lisant le profil génétique, l'autre une description chimique du médicament (empreinte de Morgan de 512 bits et six descripteurs physico-chimiques), le profil étant modulé par le médicament (modulation FiLM). Testée sur le corpus v7 avec des plis groupés par médicament, elle donnait un F1 macro de 0,467 (réseau), 0,502 (Random Forest) et 0,454 (XGBoost), avec 63 à 70 % des situations à éviter manquées : aucune généralisation fiable à un médicament absent de l'entraînement n'était démontrée, et un nouveau test conduit à la même conclusion (section 6.8). Le mécanisme d'attention de cette étape n'existe plus dans le réseau actuel ; aucune ablation ne l'a isolé, aucun apport n'est revendiqué, et des poids d'attention ne sont pas utilisés comme explication (Jain et Wallace, 2019).

### D.2 Fonction de perte

Le nombre de paramètres du réseau de profil résulte de l'architecture : 34×1 024 + 1 024 + 1 024×1 024 + 1 024 + 1 024×756 + 756 = 1 860 340. L'exposant α et le coefficient λ\_EVITER de la formule (4.1) ne sont pas fixés a priori : ils font partie de l'espace exploré (section D.3), et les valeurs retenues sont celles de la configuration sélectionnée.

Pour un lot de cases étiquetées indicées par n, soit z\_n les quatre logits du groupe du médicament de la case, p\_{n,c} la probabilité softmax de la classe c, y\_n la classe vraie et ε = 0,05 le lissage d'étiquettes. La perte minimisée est :

$$\mathcal{L} = \frac{1}{\sum_{n} w_{y_n}} \sum_{n} \left[ -(1-\varepsilon)\, w_{y_n} \log p_{n,y_n} \;-\; \frac{\varepsilon}{K} \sum_{c=1}^{K} w_c \log p_{n,c} \right] \qquad (D.1)$$

Cette écriture est celle de la fonction d'entropie croisée de PyTorch avec poids de classes et lissage d'étiquettes ; son égalité avec le calcul de la fonction a été vérifiée numériquement sur un lot d'essai de 512 cases, avec la version de PyTorch de l'environnement d'entraînement (2.11.0) : l'écart entre les deux calculs est nul en double précision.

**Optimisation.** Adam (Kingma et Ba, 2015), pas d'apprentissage 10⁻³, décroissance des poids 10⁻⁴, lots de 64 profils, 300 époques au maximum. Les poids retenus sont ceux de l'époque dont le F1 macro sur la validation interne est le meilleur ; l'entraînement s'arrête après 25 époques sans amélioration d'au moins 10⁻⁴. La validation interne regroupe 10 % des profils du jeu d'entraînement du pli, sans recouvrement avec lui. Le plafond de 300 époques n'a jamais été atteint : l'arrêt anticipé intervient en moyenne à 81,4 époques (section 6.1), de sorte que c'est la patience de 25 époques, et non le plafond, qui termine l'entraînement.

### D.3 Recherche d'hyperparamètres

- **Espace exploré :** 1 à 3 couches ; largeur 128, 256, 512 ou 1 024 ; Dropout de 0,1 à 0,5 ; avec ou sans normalisation par lots (Ioffe et Szegedy, 2015) ; ReLU ou GELU ; pas d'apprentissage 3×10⁻⁴, 10⁻³ ou 3×10⁻³ ; décroissance des poids 0, 10⁻⁵, 10⁻⁴ ou 10⁻³ ; lots de 32, 64, 128 ou 256 ; exposant des poids de classes 0,5, 0,75 ou 1 ; coefficient EVITER 1, 2 ou 4 ; lissage 0 ou 0,05.
- **Essais :** 40 configurations, la configuration 0 étant le réglage de référence de l'étape précédente et les 39 autres tirées au hasard. Chacune est entraînée une fois dans chacun des 5 plis, soit 200 entraînements. Le nombre de 40 est un compromis entre la couverture de l'espace et le temps de calcul, et il est le même pour les trois modèles comparés (section 4.7) : c'est l'égalité de ce budget qui rend la comparaison équitable, non sa valeur absolue.
- **Critère :** F1 macro sur une validation interne de 15 % des profils du jeu d'entraînement du pli. Le pli de test et l'ensemble final de 138 profils ne sont pas lus pendant la recherche.
- **Résultat :** la configuration 35 (2 × 1 024, ReLU, sans normalisation par lots, Dropout 0,1, lissage 0,05, coefficient EVITER 1, exposant 0,5) est la meilleure dans les cinq plis. Son F1 macro moyen de validation interne est de 0,9987, contre 0,9977 pour la deuxième (configuration 38).
- **Sur le corpus v15 :** la configuration 35 est reprise telle quelle, sans nouveau réglage, et sert de bras de référence. Les recherches des trois modèles comparés ont en revanche été intégralement refaites sur la v15 (section 4.7).
- **Second tour :** un tour de recherche locale autour de la configuration 35 a été amorcé puis interrompu (un seul entraînement terminé, jamais utilisé) ; il n'intervient pas dans le choix.

### D.4 Calibration

La température retenue est celle qui minimise, sur l'intervalle [0,05 ; 5], la log-vraisemblance négative moyenne des M cases étiquetées de la validation interne, calculée avec les probabilités q de la formule (4.2). Le script applique la même opération aux logarithmes des probabilités non calibrées, écartées de zéro à 10⁻¹² près : le résultat est équivalent, car le softmax ne change pas quand on retire la même constante à tous les logits.

L'erreur de calibration attendue (ECE) est mesurée sur 15 intervalles de largeur égale de la probabilité maximale (Guo et al., 2017), nombre repris de cette publication. Sur le corpus v13, la calibration faisait passer l'ECE de 0,149 à 0,0004 et la log-loss de 0,165 à 0,0028. Sur le corpus v15, T vaut en moyenne 0,198 selon les entraînements de la validation croisée, avec un minimum de 0,05 et un maximum de 0,269. Une température inférieure à 1 rend les probabilités plus tranchées : le réseau, entraîné avec lissage d'étiquettes, est sous-confiant avant calibration (interprétation, non testée par une ablation dédiée). Le minimum observé coïncide avec la borne inférieure de l'intervalle de recherche, ce qui signifie que pour au moins un entraînement la valeur retenue est contrainte par cet intervalle et non par les données ; l'intervalle n'a pas été élargi après coup, parce qu'il avait été fixé avant les mesures.

L'ECE se calcule ainsi :

$$\mathrm{ECE} = \sum_{b=1}^{15} \frac{|B_b|}{n} \left| \mathrm{acc}(B_b) - \mathrm{conf}(B_b) \right| \qquad (D.2)$$

où B\_b est l'ensemble des lignes dont la probabilité maximale appartient à l'intervalle \](b−1)/15 ; b/15\], n le nombre total de lignes, acc(B\_b) la part de prédictions correctes dans B\_b et conf(B\_b) la probabilité maximale moyenne dans B\_b ; les intervalles vides sont ignorés.

### D.5 Abstention

Pour un seuil τ, avec c\_i la confiance de la ligne i et ŷ\_i sa classe prédite, la couverture et le risque valent :

$$\mathrm{couverture}(\tau) = \frac{|\{ i : c_i \ge \tau \}|}{n}, \qquad \mathrm{risque}(\tau) = \frac{|\{ i : c_i \ge \tau,\ \hat{y}_i \ne y_i \}|}{|\{ i : c_i \ge \tau \}|} \qquad (D.3)$$

L'analyse des prédictions hors pli accepte les lignes dont la confiance est au moins égale au seuil ; l'application s'abstient quand la confiance est au plus égale au seuil. Les deux conventions ne diffèrent que pour une confiance exactement égale au seuil.

Les quatre seuils du tableau 4.1 sont plus élevés que ceux obtenus sur la version antérieure du corpus (0,9895, 0,9965, 0,9988 et 0,9995) : le réseau étant devenu plus confiant, il faut un seuil plus haut pour écarter la même part de prédictions. Le programme qui produit le modèle final calcule ces quatre quantiles à partir des 25 fichiers de prédictions hors pli (211 177 lignes du corpus v15, moyenne des 5 graines) et les enregistre avec le modèle, de sorte que le seuil servi par l'application est toujours celui mesuré sur le corpus qui a entraîné ce modèle.

L'analyse de couverture-risque menée sur le corpus v15 (section 6.3) donne une aire sous la courbe ROC de 0,870 pour la confiance employée comme indicateur d'erreur ; les 1 % de lignes les moins confiantes contiennent 77,0 % des erreurs. En revanche, à un seuil de 0,90, 32,0 des 47,4 situations à éviter manquées restent acceptées : ce sont des erreurs commises avec une confiance élevée, que l'abstention ne peut pas détecter. Un seuil spécifique sur la probabilité de la classe EVITER a été exploré après coup sur les mêmes plis ; il n'est pas utilisable tel quel, car un tel seuil doit être fixé a priori sur la validation interne ; il n'a pas été fixé de cette façon dans ce travail, et l'application n'en comporte pas.

L'aire sous la courbe ROC de la confiance, comme indicateur d'erreur, est calculée ainsi :

$$\mathrm{AUROC} = \frac{1}{n_{+}\, n_{-}} \sum_{i \in \mathcal{C}} \sum_{j \in \mathcal{E}} \left[ \mathbf{1}(c_i > c_j) + \tfrac{1}{2}\, \mathbf{1}(c_i = c_j) \right] \qquad (D.4)$$

où 𝒞 est l'ensemble des lignes correctement prédites, ℰ celui des lignes erronées, n\_+ = |𝒞| et n\_− = |ℰ|. C'est la probabilité qu'une ligne correcte ait une confiance supérieure à celle d'une ligne erronée, les égalités comptant pour une demi-unité.

### D.6 Réseau de choix

**Objectif.** Pour un profil donné et une classe ATC de niveau 4 contenant au moins deux médicaments étiquetés (44 classes dans le corpus v15), ordonner les médicaments candidats de la classe. Le seuil de deux médicaments est ce qui définit la tâche : en deçà, il n'y a rien à ordonner.

**Cible.** La cible est une convention du projet, non une recommandation de guideline : parmi les médicaments étiquetés de la classe, l'ensemble S contient ceux de la meilleure action disponible dans l'ordre STANDARD, puis SURVEILLER, puis ADAPTER\_DOSE. Un médicament EVITER n'entre jamais dans S. Aucune guideline ne départage les médicaments de S ; la cible d'entraînement est donc la loi uniforme sur S, choix qui exprime l'absence de préférence documentée plutôt qu'une préférence inventée.

**Modèle.** Deux couches cachées de 256 unités avec normalisation par lots, ReLU et Dropout de 0,3 ; la sortie donne un score par médicament, et un softmax restreint aux candidats de la classe donne la probabilité de choix. Perte : entropie croisée avec la cible uniforme. Adam (pas 10⁻³, décroissance des poids 10⁻⁴, lots de 64), arrêt après 25 époques sans amélioration de la perte de validation interne. Ces réglages ont été fixés à l'avance et ne sont pas ajustés : aucune recherche d'hyperparamètres n'a été menée pour ce réseau, ce qui est une asymétrie avec le réseau de profil et une limite (section 4.10).

**Lecture.** L'ensemble recommandé est formé des candidats dont la probabilité vaut au moins la moitié de la probabilité maximale. Ce rapport d'un demi est une convention d'affichage, retenue parce que les probabilités de médicaments équivalents sont quasi égales et qu'un seuil absolu les départagerait arbitrairement. Cette probabilité est une probabilité de choix selon la convention de la cible, non une probabilité de succès clinique.

**Métriques.** Choix dans S (cas « informatifs », où S est plus petit que l'ensemble des médicaments étiquetés) ; ensemble exact retrouvé ; indice de Jaccard entre ensemble prédit et S ; part des cas où un médicament EVITER est choisi quand un tel médicament existe dans la classe. Comparaison à une référence qui ignore le profil (médicaments les plus fréquemment dans S à l'entraînement, identiques pour tous les patients) et à un choix au hasard. La référence sans profil est indispensable : sans elle, une métrique peut sembler excellente alors qu'elle ne mesure pas l'apport du profil (section 6.4).

### D.7 Modèles de comparaison

- **XGBoost** (Chen et Guestrin, 2016) : objectif multi:softprob, arrêt anticipé sur la log-loss de la validation interne ;
- **Random Forest** (Breiman, 2001) : max\_features = racine carrée du nombre de variables ; le nombre d'arbres n'est pas une valeur à régler, la performance étant monotone en ce paramètre (Probst et Boulesteix, 2018).

Les arbres reçoivent une ligne par couple (profil, médicament), avec les 34 colonnes du profil et l'identifiant du médicament codé en une colonne par médicament, en valeurs brutes et sans mise à l'échelle, avec des poids d'échantillon inversement proportionnels à la fréquence des classes. Cette forme diffère de celle du réseau, qui est multitâche : l'égalité de protocole porte sur les plis, le budget de réglage et la calibration, non sur la forme du problème posé à chaque modèle, et cette différence est une limite de la comparaison (section 6.5).

**Égalité de traitement.** Dans les comparaisons antérieures du projet, le réseau avait bénéficié d'une recherche de 40 configurations et les arbres non, ce qui invalidait toute conclusion. La comparaison du corpus v15 supprime cette asymétrie : mêmes plis et même validation interne, 40 configurations par modèle choisies par recherche imbriquée, 5 graines, calibration par température pour les trois modèles, protocole figé avant tout résultat.

**Pourquoi les recherches ont été refaites pour la v15.** Le corpus v15 partage les plis du précédent et n'en diffère que de 0,85 % des lignes. Reprendre des hyperparamètres sélectionnés sur l'autre version reviendrait donc à les avoir choisis en ayant vu, sous une forme presque identique, les profils qui servent de test — exactement ce que la validation croisée imbriquée est censée écarter. Les trois recherches ont été refaites intégralement, pour un coût d'environ neuf heures de calcul supplémentaires. La seule exception est la configuration 35, qui n'est pas re-sélectionnée parce qu'elle est par définition le réglage figé du modèle déployé et que la re-sélectionner la priverait de ce qu'elle mesure. Les résultats sont donnés en section 6.5. Le modèle XGBoost de l'application est un second avis entraîné avec les mêmes réglages.

### D.8 Protocole d'évaluation : détail

Les métriques du protocole se calculent ainsi, P\_c et R\_c désignant la précision et le rappel de la classe c sur les lignes hors pli :

$$\mathrm{F1}_c = \frac{2\, P_c\, R_c}{P_c + R_c}, \qquad \mathrm{F1\ macro} = \frac{1}{K} \sum_{c=1}^{K} \mathrm{F1}_c, \qquad \text{EVITER manqués} = 1 - R_{\mathrm{EVITER}} \qquad (D.5)$$

- **Découpage :** celui de la section 3.6 (138 profils finaux mis de côté ; StratifiedGroupKFold à 5 plis, graine 42, groupé par identifiant de profil, parenté traitée en section 3.8), appliqué sans modification à tous les modèles via le même fichier de protocole (protocole\_commun\_v10.py). Aucun modèle ne définit son propre découpage.
- **Répétitions :** 5 graines d'initialisation × 5 plis = 25 entraînements par condition. Les résultats sont donnés en moyenne ± écart-type sur ces 25 entraînements ; cet écart-type mesure la variabilité d'entraînement, non un intervalle de confiance sur les patients, car les graines partagent les mêmes lignes. Pour comparer deux modèles, un bootstrap par identifiant de profil (2 000 tirages ; les profils apparentés sont traités comme indépendants) fournit des intervalles de confiance à 95 %. Le rééchantillonnage porte sur les profils et non sur les lignes, parce que les lignes d'un même profil ne sont pas indépendantes.
- **Métriques :** F1 macro (moyenne non pondérée des quatre classes) ; exactitude ; « EVITER manqués » = 1 − rappel de la classe EVITER ; précision de la classe EVITER ; log-loss ; ECE ; F1 macro par niveau de source. Le F1 macro est la métrique principale parce que le corpus est fortement déséquilibré et que l'exactitude y serait trompeuse : prédire STANDARD partout donnerait déjà plus de 85 % d'exactitude. « EVITER manqués » est la mesure de sécurité, parce que c'est la seule erreur dont la conséquence clinique serait grave.

Le rappel R\_EVITER est la part des lignes dont la classe vraie est EVITER et qui sont prédites EVITER ; « EVITER manqués » est donc la part des lignes EVITER que le modèle ne reconnaît pas.

### D.9 Modèles finaux de l'application

Le réseau de profil final est entraîné une fois (graine 42) sur 1 116 profils, avec 125 profils de validation interne pour l'arrêt anticipé et la température, qui vaut T = 0,222 ; l'entraînement s'arrête à 61 époques. Les 138 profils finaux ne sont pas utilisés, ce que le programme vérifie et rapporte. Le réseau de choix final est entraîné de la même façon et s'arrête à 167 époques. Les valeurs obtenues sur la validation interne ont servi à l'arrêt anticipé : elles sont optimistes et ne tiennent pas lieu d'estimation de performance, laquelle vient de la validation croisée (chapitre 6). La répartition 1 116 + 125 reprend les 1 241 profils de développement, l'ensemble final restant intact.

Les valeurs de validation interne du réseau de profil final sont un F1 macro de 0,9997, une exactitude de 0,9999, une précision de la classe EVITER de 1,0 et une ECE de 0,0002 ; celles de XGBoost atteignent 1,0 de F1 macro. Elles ne sont rapportées que pour mémoire : mesurées sur l'ensemble qui a servi à l'arrêt anticipé, elles sont optimistes par construction et ne constituent pas une estimation de performance.

### D.10 Versions des bibliothèques et origine des valeurs numériques

Les versions des bibliothèques n'ont pas été enregistrées à chaque entraînement ; celles de l'environnement, relevées après coup, sont PyTorch 2.11.0, scikit-learn 1.8.0 et XGBoost 3.3.0.

Le tableau D.1 indique d'où vient chaque valeur numérique du protocole : d'une mesure, d'une recherche, d'un calcul ou d'une convention fixée avant les essais. Aucune n'est un réglage choisi au vu des résultats.

::: {custom-style="LegendeTableau"}
Tableau D.1 : Origine des valeurs numériques du protocole
:::

| Valeur | Ce qu'elle désigne | Origine |
| --- | --- | --- |
| 5 plis | Validation croisée groupée par profil | Valeur usuelle ; chaque profil de développement est testé une fois, dans un pli d'environ 248 profils (section 3.6) |
| 5 graines, 25 entraînements | Répétitions | 5 graines pour chacun des 5 plis, afin de mesurer la variabilité due à l'entraînement (section 4.8) |
| Graine 42 | Découpage | Convention fixée avant les essais, pour la reproductibilité |
| 40 configurations | Recherche d'hyperparamètres | Recherche aléatoire, avec le même budget pour les trois modèles ; c'est l'égalité du budget qui compte, non sa valeur (sections 4.3 et 4.7) |
| 2 couches de 1 024 unités, Dropout 0,1, lissage 0,05 | Réseau de profil | Configuration 35, la meilleure des 40 dans les cinq plis sur la validation interne (section 4.3) |
| 756 sorties | Couche de sortie | 189 médicaments × 4 classes (section 4.2) |
| 1 860 340 | Paramètres du réseau | Résulte de l'architecture : (34 × 1 024 + 1 024) + (1 024 × 1 024 + 1 024) + (1 024 × 756 + 756) |
| 15 intervalles | Calcul de l'ECE | Valeur de la publication dont la méthode est reprise (Guo et al., 2017) |
| \[0,05 ; 5\] | Bornes de recherche de la température | Fixées avant les mesures ; la borne basse est atteinte par au moins un entraînement (section 4.4) |
| 0,9934 / 0,9981 / 0,9994 / 0,9998 | Seuils d'abstention | Quantiles à 0,5 %, 1 %, 2 % et 5 % de la confiance sur les prédictions hors pli du corpus v15 (section 4.5) |
| 44 classes | Portée du réseau de choix | Classes ATC4 contenant au moins deux médicaments étiquetés (section 4.6) |
| 2 000 tirages | Bootstrap par profil | Intervalles de confiance à 95 % des différences entre modèles (section 4.8) |
| 0,001 | Marge d'équivalence pratique | Fixée avant toute mesure ; sert de règle de décision aux comparaisons de modèles (section 4.8) |
