# Propagation du changement RQ2 — notes de vérification

**Ce document ne fait pas partie du mémoire.** Il accompagne `Front_matter_v15_MEMOIRE.md`, `Chapitre1_v15_MEMOIRE.md` et `Chapitre9_v15_MEMOIRE.md`.

## 1. Ce qui a été corrigé, et pourquoi

### Résumé et abstract

| | avant | après |
| --- | --- | --- |
| Lignes du corpus | 232 664 | **234 632** |
| F1 macro | 0,9979 | **0,9982** |
| EVITER manqués | 0,83 % | **0,66 %** |
| Comparaison | « XGBoost reproduit les règles mieux que le réseau (0,9994 contre 0,9968) » | « aucune supériorité du réseau sur XGBoost n'est établie ; les deux sont équivalents pour la configuration déployée, et XGBoost manque moins de situations à éviter » |
| Longueur | 207 et 198 mots | **197 et 200 mots** |

La contrainte des 200 mots a obligé à récupérer une douzaine de mots ailleurs, la phrase de comparaison étant plus longue que celle qu'elle remplace. Les coupes portent uniquement sur des mots redondants (« du patient » après « profil génétique », « comparables » après « lignes », « recommandations » devant la liste des sources) : **aucune affirmation n'a été retirée**. Le décompte traite « 1 379 » comme un mot, ce qui est la convention d'un correcteur humain.

Les cinq mots clés de chaque langue sont inchangés et conformes au formulaire.

### Chapitre 1

Quatre corrections, dont une qui est un gain de justification et non une substitution :

- **§ 1.4** : les 58 / 131 médicaments à action constante / variable étaient repris de la v14. Recalculés sur la v15 : **57 constants et 132 variables**, avec une ventilation qui n'existait pas — des 57 constants, 52 sont toujours STANDARD, 4 toujours ADAPTER\_DOSE et 1 toujours EVITER. Cette ventilation renforce l'argument du paragraphe : la grande majorité des médicaments à action constante le sont parce qu'aucune règle ne les rend variables, et non parce que le profil serait sans effet.
- **§ 1.4** : « un nouveau test sur le corpus v14 » devient « un nouveau test, mené sur une version ultérieure du corpus », parce que le test du pilier A n'a **pas** été refait sur la v15. Écrire « v15 » ici aurait été faux.
- **§ 1.3 et § 1.9** : effectifs et numéro de version.
- **§ 1.5 et § 1.8** : la conclusion de la comparaison.

### Chapitre 9

Neuf modifications. Deux méritent ton attention :

1. **§ RQ2 entièrement réécrit.** La réponse passe de « négative pour XGBoost » à « aucune supériorité du réseau n'est établie », avec les trois précautions écrites explicitement : l'hypothèse principale n'est pas confirmée, le critère de sécurité reste défavorable, et la conclusion dépend de la version des règles. La dernière phrase est celle qui protège le mémoire : *« Une conclusion qui change avec la version des règles est une conclusion qui dépend des règles, et non une propriété des modèles. »*

2. **§ RQ1 : une affirmation a été retirée.** Le texte disait que les médicaments à règle multi-gènes « sont aussi ceux sur lesquels le réseau commet l'essentiel de ses erreurs (section 6.1) ». **Cette phrase renvoyait à une ventilation des erreurs par médicament qui n'existe plus** : elle n'a pas été recalculée sur la v15, et le chapitre 6 v15 porte un marqueur à cet endroit. Laisser le renvoi aurait créé une affirmation sans support dans le chapitre cité — exactement le type d'erreur qu'un examinateur relève. Le texte dit maintenant que la correspondance était vraie sur une version antérieure et n'est pas vérifiée pour la version actuelle.

Les autres modifications : effectifs du constat d'ouverture, ECE 0,0003 → 0,00029, part des erreurs au premier centile 71,6 % → 77,0 %, inversion de la calibration, conclusion générale.

## 2. Un point à trancher sur l'argument de la calibration

Dans le chapitre 9 v14, la calibration servait d'argument *contre* le réseau (« XGBoost obtient une erreur de calibration meilleure ou équivalente »). Sur la v15, l'ordre s'inverse. **La tentation serait d'en faire un argument pour le réseau. Je ne l'ai pas fait**, et le texte dit pourquoi : trois valeurs toutes inférieures à 0,0004, sur une tâche où plus de 99,9 % des lignes sont correctes, sans intervalle de confiance. L'énoncé retenu est que les trois modèles sont bien calibrés et que leurs écarts ne sont pas interprétables.

Si tu veux pouvoir en faire un argument, il faut une mesure : des intervalles de confiance sur l'ECE par bootstrap sur les profils, comme pour le F1. Le calcul est peu coûteux à partir des prédictions hors pli déjà enregistrées. Tant qu'il n'est pas fait, l'énoncé actuel est le seul défendable.

## 3. Ce qui reste à propager

- **Annexe A**, ligne « XGBoost contre DL sur étiquettes de règles » : le constat v12 reste vrai pour la v12, mais la ligne ne doit pas laisser croire qu'il vaut encore. À reformuler avec la version entre parenthèses.
- **Section 4.5 et tableau 4.1** : les quatre seuils de quantile, selon la décision sur le seuil d'abstention (voir les notes du chapitre 6).
- **Chapitres 7 et 8** : les chiffres produits par l'application changeront quand elle sera régénérée sur les modèles v15 et les 104 personnes refaites.
- **Section 1.2, « 34 gènes et 164 médicaments »** : ce chiffre est attribué à Caudle et al. 2025 et **n'a pas pu être vérifié**, le texte de l'éditeur étant inaccessible. Il est signalé depuis la relecture bibliographique. Deux issues conformes : le remplacer par un décompte fait sur le site de CPIC avec sa date de consultation, ou le retirer. Il figure toujours dans le chapitre 1 livré, en l'état.

## 4. Contrôles faits

- Aucune occurrence de « v14 » ne subsiste dans les trois fichiers livrés.
- Les trois fichiers ont été fabriqués ensemble en document Word puis en PDF : 14 pages, 7 marqueurs surlignés, styles du mémoire conservés.
- Les 57 / 132 médicaments et la ventilation 52 / 4 / 1 sont calculés directement sur le corpus v15, empreinte `68b564ce265728b6` vérifiée.
- Le décompte des résumés a été fait deux fois, la seconde en traitant les nombres à espace insécable comme un seul mot.

## 5. Sauvegarde

**WSL → Windows → GitHub → Google Drive**, et **supprime d'abord les anciens fichiers de même nom dans les téléchargements**.

```bash
cd ~/projet_memoire/model_v2/docs
bash ~/sauver.sh "propagation RQ2 v15 : front matter, chapitre 1, chapitre 9" \
  Front_matter_v15_MEMOIRE.md Chapitre1_v15_MEMOIRE.md Chapitre9_v15_MEMOIRE.md Propagation_RQ2_v15_NOTES.md
```
