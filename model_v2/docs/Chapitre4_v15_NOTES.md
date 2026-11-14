# Chapitre 4 v15 — notes de vérification

**Ce document ne fait pas partie du mémoire.** Il accompagne `Chapitre4_v15_MEMOIRE.md`.

## 1. Ce qui a changé, et pourquoi

### Chiffres substitués
| Emplacement | avant | après |
| --- | --- | --- |
| § 4.4, température | « entre 0,16 et 0,31 », T = 0,2328 pour le modèle final | **moyenne 0,198, de 0,05 à 0,269** ; la valeur du modèle final passe en marqueur |
| § 4.5, lignes hors pli | 209 415 (v14) | **211 177 (v15)** |
| § 4.5 et tableau 4.1 | 0,9895 / 0,9965 / 0,9988 / 0,9995 | **0,9934 / 0,9981 / 0,9994 / 0,9998** |
| § 4.5, erreurs au premier centile | 71,6 % | **77,0 %** |
| § 4.5, EVITER manqués acceptés à 0,90 | 46,6 sur 60,2 | **32,0 sur 47,4** |
| § 4.1, script d'évaluation | evaluer\_dl\_imbrique\_v5.py | **v6** |
| § 4.6, classes ATC4 | 44 (corpus v14) | **44 (corpus v15), confirmé par la sortie du script de réentraînement** |

Les 44 classes ATC4 ont été **vérifiées et non supposées** : le script affiche `profils 1379 | médicaments 189 | classes 44 | cas (profil, classe) avec cible : 50278`. Un décompte approximatif fait de mon côté donnait 37 ; c'est ma méthode qui était fausse, pas le chapitre. Les sections 4.6 et 6.4 gardent donc 44.

### Ajouts de justification (règle 1)
Le chapitre v14 donnait beaucoup de valeurs sans dire pourquoi. Sont désormais justifiés dans le texte :

- **Pourquoi la mise à l'échelle de la température** plutôt qu'une autre calibration : un seul paramètre, ne change pas la classe prédite, ne demande pas de données supplémentaires.
- **Pourquoi 15 intervalles** pour l'ECE : valeur de la publication dont la méthode est reprise.
- **Pourquoi une recherche aléatoire** et non une grille : à budget égal, elle explore mieux un espace où peu de dimensions comptent.
- **Pourquoi 40 configurations** : c'est l'égalité du budget entre les trois modèles qui rend la comparaison équitable, pas la valeur absolue.
- **Pourquoi le F1 macro comme métrique principale** : prédire STANDARD partout donnerait déjà plus de 85 % d'exactitude.
- **Pourquoi le bootstrap porte sur les profils** et non sur les lignes : les lignes d'un même profil ne sont pas indépendantes.
- **Pourquoi pas de rééchantillonnage synthétique** : interpoler entre deux profils produirait des génotypes qui n'existent pas.
- **Pourquoi le seuil de deux médicaments** pour une classe ATC4 : en deçà il n'y a rien à ordonner.
- **Pourquoi le rapport d'un demi** dans la lecture du réseau de choix : les probabilités de médicaments équivalents sont quasi égales, un seuil absolu les départagerait arbitrairement.
- **Pourquoi les recherches ont été refaites sur la v15** : les deux corpus ne diffèrent que de 0,85 % des lignes, reprendre les réglages reviendrait à les avoir choisis en ayant vu les profils de test. Coût assumé : neuf heures de calcul.
- **La règle de décision du protocole** (marge de 0,001, supérieur / équivalent / non tranché) est maintenant énoncée au chapitre 4, où elle a sa place, et non découverte au chapitre 6.

### Limites ajoutées
Le point 4 de la section 4.10 est nouveau : **le réseau de choix n'a bénéficié d'aucune recherche d'hyperparamètres**, contrairement au réseau de profil. C'est la même asymétrie que celle reprochée aux comparaisons antérieures entre le réseau et les arbres ; ne pas la signaler aurait été incohérent.

## 2. Les marqueurs : deux levés, quatre restants

**Levés par la régénération des modèles finaux sur le corpus v15 :**

- **§ 4.5, seuil de l'application : 0,9981.** Il n'est pas choisi, il est calculé. `modele_final_profil_v3.py` lit les 25 fichiers hors pli `oof_c35_cal_pli*_graine*.npz` et en écrit les quantiles à 0,5 %, 1 %, 2 % et 5 % dans `abstention_seuils_profil_v3.json`, livré avec le modèle. Valeurs obtenues : 0,993351 / 0,998120 / 0,999421 / 0,999791. **Elles coïncident avec celles annoncées par l'analyse de couverture-risque** (0,9934 / 0,9981 / 0,9994 / 0,9998), ce qui valide les deux chemins de calcul l'un par l'autre.
- **§ 4.9, modèles finaux :** T = 0,222, 61 époques pour le réseau de profil, 167 pour le réseau de choix. Validation interne du réseau de profil : F1 macro 0,9997, exactitude 0,9999, précision EVITER 1,0, ECE 0,0002 ; XGBoost 1,0 de F1 macro.

**Restants :**

| § | Ce qui manque | Comment le lever |
| --- | --- | --- |
| 4.2 | contrôle de la perte avec la version de PyTorch de l'entraînement | relancer le contrôle numérique sur un lot d'essai |
| 4.5 | seuil a priori sur P(EVITER) | ne pas lever : doit être fixé sur la validation interne |
| 4.8 | évaluation finale sur les 138 profils | après gel écrit du protocole |
| 4.10 | versions des bibliothèques | `pip freeze` ; si c'est perdu, le marqueur devient une limite écrite |

**La décision sur le seuil est close, et elle ne t'appartenait pas vraiment.** Tu avais choisi de trancher après le point de contrôle ; en réalité le pipeline calcule le seuil tout seul. Conserver 0,9965 aurait exigé d'écraser à la main un fichier produit par le programme — ce qui ne se défend pas. La section 4.5 dit maintenant explicitement que le seuil est calculé et non saisi.

## 3. Point de vigilance

Le § 4.9 ne porte plus aucune valeur numérique de modèle final : T = 0,2328, les 79 époques et le F1 de validation interne de 0,9998 étaient ceux des modèles v14. Les laisser aurait été une erreur de version invisible, puisque ces nombres sont plausibles et qu'aucun contrôle ne les aurait signalés. Ils reviendront, mesurés sur les modèles v15.

La phrase « la répartition 1 116 + 125 reprend les 1 241 profils de développement » reste vraie en v15, le découpage développement / ensemble final étant inchangé. Elle a été vérifiée, pas supposée.

## 4. Sauvegarde

**WSL → Windows → GitHub → Google Drive.** Supprime d'abord les éventuels doublons dans les téléchargements.

```bash
cd ~/projet_memoire/model_v2/docs
bash ~/sauver.sh "chapitre 4 v15" Chapitre4_v15_MEMOIRE.md Chapitre4_v15_NOTES.md
```
