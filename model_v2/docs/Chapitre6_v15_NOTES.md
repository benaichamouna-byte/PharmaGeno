# Chapitre 6 v15 — notes de vérification

**Ce document ne fait pas partie du mémoire.** Il accompagne `Chapitre6_v15_MEMOIRE.md`.

## 1. Le fait le plus important : la conclusion de RQ2 a changé

C'est le seul endroit du mémoire où une conclusion s'inverse entre deux versions du corpus. Il faut le traiter de front, parce que le jury le verra.

| | v14 | v15 |
| --- | --- | --- |
| Réseau − XGBoost (F1 macro) | −0,00265 \[−0,00393 ; −0,00164\] | −0,000345 \[−0,00106 ; +0,00034\] |
| Verdict du protocole | **XGBoost supérieur**, statistiquement et en pratique | **Non tranché** |
| XGBoost − réseau c35 | +0,00155 \[0,00098 ; 0,00222\] | +0,000091 \[−0,00052 ; +0,00076\] → **équivalents** |
| Sécurité (EVITER manqués, réseau − XGB) | +47,0 \[22,2 ; 76,8\] | +38,0 \[23,2 ; 54,4\] |
| ECE : qui est le mieux calibré | XGBoost | le réseau |

**Ce qu'il faut et ne faut pas écrire.** « Non tranché » n'est pas « équivalent », et « équivalent » n'est pas « meilleur ». Le chapitre 6 tel que rédigé dit les trois choses dans cet ordre et ajoute explicitement que l'hypothèse principale du mémoire n'est pas confirmée. **Ne pas céder à la tentation de présenter la v15 comme une victoire du Deep Learning** : la différence a disparu, elle ne s'est pas inversée, et le critère de sécurité reste en faveur de XGBoost avec un intervalle qui exclut zéro. Un jury qui verra la v14 dans l'historique du projet posera la question ; la réponse défendable est celle écrite en section 6.5 (deux mouvements arithmétiques, une hypothèse sur les règles révisées, explicitement non démontrée).

**Attention au point faible de cette explication** : les erreurs de XGBoost *augmentent* (41,8 → 82,0) en même temps que celles du réseau diminuent (187,2 → 123,6). L'hypothèse des règles multi-gènes explique la baisse du réseau, pas la hausse de XGBoost. Le texte le dit. Si tu veux une explication complète, il faut la mesurer : comparer les erreurs par médicament entre les deux versions, ce qui demande les sorties hors pli de la v14 (voir § 4).

## 2. Deux décisions à prendre, et ma recommandation

### Décision 1 — seuil d'abstention de l'application : 0,9965 ou 0,9981 ?

La méthode du chapitre 4 définit le seuil comme **le quantile à 1 % de la confiance hors pli**. Sur la v15 ce quantile vaut **0,9981**. Garder 0,9965 reviendrait à appliquer à un modèle v15 un quantile calculé sur un corpus v14, c'est-à-dire à conserver un nombre sans sa justification — exactement ce que la règle 1 interdit.

**Ma recommandation : passer à 0,9981.** Ce n'est pas un choix de performance mais de cohérence : la méthode est inchangée, seule la mesure change.

**Ce que cela coûte**, à mesurer avant de décider : le fichier de configuration de l'application, les tests T1–T68 (au moins ceux qui portent sur le statut « à vérifier »), la section 5.4, le tableau 4.1, et la comparaison des 104 personnes avec PharmCAT si elle est refaite après. Si ce coût ne tient pas dans le calendrier, la solution honnête de repli est de **garder 0,9965 et d'écrire pourquoi** en section 4.5 : « seuil hérité de la version antérieure du corpus, conservé pour ne pas invalider la suite de tests ; sur la v15 il écarte 0,56 % des prédictions au lieu de 1 % ». C'est une limite déclarée, pas une faute. Ce qui serait une faute, c'est de garder 0,9965 en le présentant comme le quantile à 1 %.

Le chapitre 6 rédigé **ne dépend pas de cette décision** : il rapporte les quantiles mesurés sans choisir. La décision s'écrit en 4.5 et 5.4.

### Décision 2 — réseau de choix (§ 6.4) : réentraîner ou déclarer la limite ?

Il n'a pas été réentraîné sur la v15, et ses résultats v14 ne sont pas transposables : la cible du réseau de choix est construite à partir des actions du moteur de règles, et les règles révisées touchent trois thiopurines et deux statines, qui entrent dans des classes ATC4 à plusieurs médicaments.

**Ma recommandation : réentraîner.** Le réseau de choix est petit (2 couches de 256, contre 2 × 1 024 pour le réseau de profil) et le bras c35 du réseau de profil a demandé sept minutes pour ses 25 entraînements. L'ordre de grandeur est donc l'heure, pas la nuit. Le coût de ne pas le faire est une section de résultats vide dans un chapitre de résultats, ce qui se voit.

Avant de lancer, vérifie que le script existe et accepte un chemin de corpus :

```bash
cd ~/projet_memoire/Model_v8_7_9_10/scripts
ls -la *choix*
grep -n "add_argument\|--data\|v14\|v13" train_dl_choix_v3.py | head -20
```

S'il lit le corpus v14 en dur, il faut une copie `v4` paramétrée, exactement comme pour `evaluer_dl_imbrique_v6.py` : v3 reste intacte, le diff se limite à l'argument de chemin, et l'empreinte du nouveau fichier est vérifiée. Si le script n'existe pas ou ne tourne pas, la section 6.4 telle qu'elle est rédigée tient : elle déclare la limite et ne présente aucun chiffre v14 comme s'il était v15.

## 3. Marqueurs `[à compléter]` du chapitre et comment les lever

| § | Ce qui manque | Comment |
| --- | --- | --- |
| 6.1 | F1 macro sans SURVEILLER, rappels des 4 classes | sortie de `evaluer_dl_imbrique_v6.py` (bras c35) : les colonnes existent déjà, il suffit de les relire |
| 6.1 | erreurs par médicament, F1 par niveau de source (v15) | même sortie ; la ventilation par médicament est dans le fichier détaillé |
| 6.2 | diagramme de fiabilité | à produire depuis les prédictions hors pli c35 ; une figure de plus dans un chapitre déjà dense — **à arbitrer** |
| 6.3 | seuil a priori sur P(EVITER) | ne pas lever : il faut le fixer sur la validation interne, pas ici. Le marqueur dit pourquoi |
| 6.4 | résultats v15 du réseau de choix | décision 2 ci-dessus |
| 6.5 | ECE de Random Forest, log-loss des 4 bras, IC des comptes d'erreurs | toutes ces colonnes sont imprimées par le script de comparaison : relire le log |
| 6.5 | IC des différences réseau − RF et XGB − RF | idem, le script les imprime |
| 6.5 | contrôle des égalités à 5 décimales (amendement 1) | contrôle post hoc, jamais fait ; s'il n'est pas fait avant le dépôt, le marqueur devient une limite écrite |
| 6.6 | refaire les 8 couples avec les modèles v15 | les profils construits sont faciles à reconstruire ; coût faible, à faire si le temps le permet |

**Un seul de ces marqueurs me paraît obligatoire avant dépôt** : celui de la section 6.5 sur les intervalles manquants du tableau 6.3, parce qu'un tableau de comparaison dont trois colonnes sont vides se remarque immédiatement. Les valeurs sont déjà dans ton log, il n'y a aucun calcul à relancer.

## 4. Ce qui se propage dans le reste du mémoire

À faire après validation du chapitre 6. Par ordre de gravité :

1. **Chapitre 9, RQ2** — la réponse change entièrement. Actuellement : « XGBoost reproduit mieux les règles ». Doit devenir : non tranché sur le F1 macro, équivalent pour la configuration déployée, désavantage maintenu sur la sécurité, hypothèse principale non confirmée.
2. **Résumé et abstract** — la phrase « XGBoost reproduit les règles mieux que le réseau (F1 macro 0,9994 contre 0,9968) » est fausse sur la v15. Les valeurs à substituer : 0,99820 pour le réseau de l'application, 0,66 % d'EVITER manqués, 234 632 lignes, 211 177 en développement.
3. **Section 1.3** — les effectifs du corpus (232 664 → 234 632 et la répartition des classes).
4. **Section 1.5** — « XGBoost reproduit les règles mieux que le réseau » : même correction qu'au point 1.
5. **Section 4.5 et tableau 4.1** — les quatre seuils de quantile, selon la décision 1.
6. **Section 4.7, dernière phrase** — renvoie à « section 6.5 », toujours valable.
7. **Annexe A**, ligne « XGBoost contre DL sur étiquettes de règles » — à réécrire : le constat v12 reste vrai pour la v12, mais la ligne ne doit pas laisser croire qu'il vaut encore.
8. **Chapitre 8** — les sections 8.3 à 8.5 citent des chiffres produits par l'application v14 ; ils changeront quand l'application sera régénérée sur les modèles v15 et les 104 personnes refaites.

## 5. Figures

`fig_6_1.png` (abstention) et `fig_6_2.png` (comparaison) sont produites par `figures_chapitre6_v15.py`, livré avec le chapitre. Le script ne calcule rien : toutes les valeurs y sont recopiées des sorties mesurées et commentées en tête, de sorte qu'on peut vérifier chaque nombre du graphique contre le log.

**Une correction a été faite au passage** : dans la version v14 du mémoire, `fig_6_1.png` portait la légende « Figure 6.2 » et `fig_6_2.png` la légende « Figure 6.1 ». Les noms de fichiers correspondent désormais aux numéros. Vérifie qu'aucun autre chapitre ne pointe vers ces deux fichiers en comptant sur l'ancien croisement.

La figure 6.1 porte le résultat défavorable de la section 6.3 (les EVITER manqués résistent plus à l'abstention que les autres erreurs) : c'est voulu, une figure qui ne montrerait que la baisse des erreurs serait flatteuse et trompeuse.

## 6. Longueur

Le chapitre fait environ 4 700 mots, soit de l'ordre de 12 pages avec les tableaux et les deux figures. Le formulaire officiel alloue **15 à 30 pages à « Résultats et discussion »**, c'est-à-dire aux chapitres 6, 7, 8 et 9 réunis. À ce rythme l'ensemble dépassera la borne haute.

Deux coupes possibles, par ordre de préférence :
- **§ 6.7 (résultats négatifs)** peut descendre en annexe A, qui existe déjà pour cela, en ne gardant dans le chapitre que trois phrases de conclusion. Gain : environ une page et demie. C'est la coupe la moins coûteuse, parce que ces résultats ne portent aucune des questions principales.
- **§ 6.6 (8 couples, exploratoire)** peut être réduit au tableau et à deux phrases. Gain : une demi-page.

Je ne recommande de couper ni § 6.3 ni § 6.5 : ce sont les deux sections que le jury lira en premier.

## 7. Contrôles faits sur les chiffres du chapitre

- Les quatre effectifs du développement (211 177 lignes, 1 241 profils, et la répartition 181 262 / 18 188 / 7 215 / 4 512) ont été **recalculés directement sur le corpus v15**, à partir du fichier de l'ensemble final de 138 profils et du même critère que `protocole_commun_v10.py`. Ils ne sont pas recopiés d'un log.
- Les empreintes SHA-256 du corpus et des deux tables de règles ont été recontrôlées : `68b564ce265728b6`, `9d5512543016cb89`, `1cb99ff632466696`, identiques aux valeurs figées.
- Le rappel EVITER a été vérifié par deux chemins indépendants : 1 − 0,99342 = 0,00658 et 47,4 / 7 215 = 0,00657. Ce contrôle est écrit dans le mémoire, parce qu'il justifie que les deux programmes lisent bien les mêmes prédictions.
- Le cas « EMA-étiquette » a été reconstitué sur le corpus v15 : 2 440 lignes, 2 médicaments, une seule ligne ADAPTER\_DOSE (lonafarnib), portée par le seul profil des 1 379 dont CYP3A4 vaut 0. Le F1 de ce niveau mesure donc la taille de l'échantillon, et non la performance.
- Les taux d'EVITER manqués du tableau 6.3 sont calculés par moi à partir des comptes et des 7 215 lignes EVITER ; **ce ne sont pas les taux imprimés par le script** (amendement 1, point A2), qui sont accompagnés d'intervalles. Si les deux diffèrent, c'est le script qui fait foi.

## 8. Deux marqueurs du chapitre 3 ont été levés au passage

En recalculant le corpus pour ce chapitre, deux valeurs manquantes du chapitre 3 ont pu être établies et `Chapitre3_v15_MEMOIRE.md` a été corrigé :

- **Tableau 3.3** : le tableau est exhaustif ; les 124 règles se répartissent en TPMT + NUDT15 (27), CYP2B6 + CYP2C19 (25), CYP2C19 + CYP2D6 (20), CYP2C9 + HLA-B (20), CYP2C9 + SLCO1B1 (20), ABCG2 + SLCO1B1 (12). Un seul des neuf médicaments multi-gènes, la rosuvastatine, n'a pas de règle à un gène, ce qui explique le passage de 188 à 189 médicaments.
- **Section 3.8, point 11** : 18 règles portent le drapeau « conditionnel » et 2 le drapeau « ambigu ».

Il reste trois marqueurs au chapitre 3 : la courbe d'apprentissage, la définition des niveaux de confiance, et le résidu du codage CYP2C9.

**Une piste pour ce dernier, à vérifier et non à écrire en l'état** : 146 des 1 379 profils portent la valeur CYP2C9 = 0,5. Le nombre 146 est celui annoncé pour le résidu dans l'analyse de la voie A. La coïncidence est frappante mais ce n'est **pas** une démonstration : le résidu se compte en lignes d'un médicament, pas en profils, et il faut vérifier sur la table de règles quels diplotypes la DPWG sépare avant d'écrire quoi que ce soit.

## 9. Sauvegarde

Ordre strict, pour les quatre fichiers livrés (`Chapitre6_v15_MEMOIRE.md`, `Chapitre6_v15_NOTES.md`, `figures_chapitre6_v15.py`, et `Chapitre3_v15_MEMOIRE.md` corrigé) :

**WSL → Windows (`C:\Users\MSI\Desktop\memoire\`) → GitHub → Google Drive (`PharmaGeno_Memoire/`)**

```bash
bash ~/sauver.sh "chapitre 6 v15 + figures + correction chapitre 3" \
  Chapitre6_v15_MEMOIRE.md Chapitre6_v15_NOTES.md figures_chapitre6_v15.py Chapitre3_v15_MEMOIRE.md
```

Les deux `.png` ne passent pas par `sauver.sh` (il ne route que `.md`, `.py`, `.sh`, `.csv`, `.json`, `.txt`) : copie-les à la main dans `Model_v8_7_9_10/fig/` puis dans le dossier `fig/` utilisé par la chaîne de fabrication du document.
