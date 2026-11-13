# Remerciements, résumé et abstract — notes de vérification

**Ce document ne fait pas partie du mémoire.** Il accompagne `Front_matter_MEMOIRE.md`.

## 1. Conformité au formulaire officiel

| Exigence | État |
| --- | --- |
| Résumé français, 200 mots | **200 mots exactement** (marqueur `[à compléter]` non compté) |
| Abstract anglais, 200 mots | **198 mots** |
| 5 mots clés en français | **5** : pharmacogénomique, apprentissage profond, aide à la décision, calibration, VCF |
| 5 keywords en anglais | **5** : pharmacogenomics, deep learning, decision support, calibration, VCF |
| Résumés sur 1 page | à vérifier après mise en page |

Le décompte exclut le marqueur `[à compléter]`, qui disparaîtra. Si le jury ou l'encadreur compte ce marqueur, le résumé français passera à 202 mots : prévoir de retirer deux mots au moment où le marqueur sera levé, ou de lever le marqueur avant le dépôt.

## 2. Ce qui a été retiré du résumé précédent

Le résumé initial comptait environ 345 mots. Ont été retirés, par ordre de volume :

- Le détail du second réseau de choix au sein des classes ATC4 — il relève du corps du mémoire et n'est pas le résultat principal.
- Les écarts-types et les intervalles de confiance — un résumé de 200 mots ne peut pas porter l'incertitude de chaque chiffre ; les valeurs complètes sont aux tableaux 6.1 et 6.4.
- Le détail de la concordance des génotypes avec GeT-RM par gène — remplacé par la seule concordance avec PharmCAT, plus directement liée à ce que l'outil produit.
- Le rapport de dose chiffré de la warfarine et son intervalle — remplacé par « va dans le bon sens », la précision étant au chapitre 7.
- Le résultat négatif sur les médicaments jamais vus — il subsiste au chapitre 6 et au chapitre 9 ; il ne tient pas en 200 mots.
- La mention de Flask et de l'écoute sur la machine locale — détail technique, chapitre 5.

## 3. Ce qui a été délibérément conservé

- **La nature des étiquettes et la réserve qu'elle impose.** C'est la phrase la plus importante du résumé : sans elle, les chiffres qui suivent seraient lus comme une performance clinique.
- **Le fait que XGBoost reproduit les règles mieux que le réseau.** Un résumé qui tairait ce résultat et un chapitre 6 qui l'annonce seraient en contradiction ; un jury le relèverait.
- **L'omission de VKORC1** dans la règle de la warfarine, qui est la limite la plus démonstrative du travail.
- **L'ensemble final non évalué**, pour que personne ne croie l'évaluation finale faite.

## 4. Mots clés : pourquoi ces cinq

Les sept mots clés précédents étaient : pharmacogénomique, apprentissage profond, CPIC, DPWG, calibration, VCF, aide à la décision.

**CPIC** et **DPWG** ont été retirés. Ce sont des sources nommées dans le corps du mémoire, non des termes d'indexation : personne ne cherche un mémoire par le nom du consortium dont il applique les recommandations. Les cinq conservés décrivent respectivement le domaine, la méthode, la finalité, une propriété méthodologique revendiquée et la nature de l'entrée.

Si un autre arbitrage est préféré, les candidats les plus défendables en remplacement sont *1000 Genomes* (la source des profils) ou *classification multi-tâche* (la nature du modèle).

## 5. Chiffres à actualiser après le passage au corpus v15

Dans le résumé **et** dans l'abstract, de façon synchrone :

- F1 macro du réseau : 0,9979
- Taux de situations à éviter manquées : 0,83 %
- Les deux F1 de la comparaison : 0,9994 et 0,9968
- Effectifs du corpus : 1 379 profils, 189 médicaments, 232 664 lignes

**Les chiffres 104, 97,8 % et 5 774 ne changent pas** : ils portent sur des données externes.

## 6. Remerciements — à personnaliser

Le texte proposé est volontairement sobre et sans effusion. Cinq destinataires : l'encadrant, le lieu de stage, les établissements de formation, le jury, les proches.

Points à vérifier ou à compléter :

- **Le nom exact du laboratoire d'accueil** à l'Institut Pasteur de Tunis, si tu souhaites le nommer plutôt que de remercier l'institution.
- **Les personnes à nommer individuellement** : toute personne de l'équipe ayant contribué concrètement devrait l'être.
- **Un financement ou une bourse** éventuels doivent être mentionnés ; leur omission peut poser problème.
- La formule sur l'encadrant peut être rendue plus ou moins chaleureuse selon ce que tu juges approprié. Le ton actuel est neutre et professionnel.

## 7. Ce qui reste à produire pour les pages liminaires

- Les champs de la page de garde : lieu et date de soutenance, noms et institutions des deux membres du jury autres que l'encadrant, institution de l'encadrant.
- La liste des abréviations existe et compte 23 entrées ; vérifier qu'elle couvre les sigles introduits par les chapitres 2 et 9.
