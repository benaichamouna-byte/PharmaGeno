# Chapitre 9 — notes de vérification et de suivi

**Ce document ne fait pas partie du mémoire.** Il accompagne `Chapitre9_MEMOIRE.md`.

## 1. Origine de chaque chiffre employé

Aucun chiffre du chapitre 9 n'est nouveau : tous sont repris de chapitres antérieurs, sans recalcul. Table de correspondance pour vérification.

| Chiffre | Section 9 | Source dans le mémoire |
| --- | --- | --- |
| F1 macro 0,9979 ± 0,0012 | 9.1, RQ3 | Tableau 6.1 |
| 0,83 % d'EVITER manqués | 9.1 | Tableau 6.1 |
| ECE 0,0003 | 9.1, RQ3 | Tableau 6.1 |
| 209 415 lignes hors pli | 9.1 | Section 3.6 |
| 97,8 % sur 3 534 lignes | 9.1, RQ6 | Section 8.3 |
| 99,92 % sur 2 600 unités | 9.1, RQ6 | Section 8.4 |
| 5 774 patients, rapport 0,830 [0,804 ; 0,857] | 9.1, RQ7 | Sections 7.1 et 7.4 |
| 121 des 133 médicaments | RQ1 | Section 1.4 (audit corpus v12) |
| 12 médicaments multi-gènes nommés | RQ1 | Section 1.4 |
| F1 0,99941 / 0,99676 / 0,99333 | RQ2 | Tableau 6.4 |
| 47 EVITER manqués de plus | RQ2 | Section 6.5 |
| AUROC 0,870 ; 71,6 % des erreurs | RQ3 | Section 6.3 |
| AUROC 0,774 contre 0,817 | RQ4 | Section 6.7 |
| 6 lignes sur 6 172 (0,1 %) | RQ5 | Section 8.4 |
| 8,0 % sur profils partiels | RQ5 | Section 8.5 |
| 36 lignes sur 36 | RQ6 | Tableau 8.3 |
| 31 % des doses basses (sensibilité 0,307) | RQ7 | Section 7.5 |
| R² 0,294 contre 0,048 | RQ7 | Section 7.6 |
| 374 des 1 379 profils apparentés | 9.4 point 6 | Section 3.8 point 3 |
| 1 379 sur 3 202 échantillons | 9.4 point 6 | Section 3.8 point 2 |

## 2. Chiffres à actualiser après le passage au corpus v15

Le chapitre 9 reprend les valeurs du corpus v14. Après le réentraînement v15, les valeurs suivantes devront être remplacées **dans le chapitre 9 en même temps que dans les chapitres 6 à 8**, sous peine d'incohérence entre chapitres :

- F1 macro du réseau déployé et son écart-type (9.1, RQ3)
- Taux d'EVITER manqués (9.1)
- ECE (9.1, RQ3)
- Effectif de développement : 209 415 lignes (9.1)
- Les trois F1 macro de la comparaison et l'écart sur les EVITER manqués (RQ2)
- AUROC de la confiance et part des erreurs dans le premier centile (RQ3)

**Les valeurs des chapitres 7 et 8 ne changent pas** avec le v15 : elles portent sur des données externes (IWPC, GeT-RM, PharmCAT, patients publiés) et non sur le corpus.

**Point de vigilance sur RQ2** : si le classement des modèles change avec le v15 — ce qui n'est pas attendu mais n'est pas exclu —, la réponse à RQ2 et le paragraphe de justification du choix du réseau doivent être réécrits, pas seulement les chiffres.

## 3. Marqueurs `[à compléter]` posés dans ce chapitre

| Emplacement | Ce qui manque | Comment le lever |
| --- | --- | --- |
| RQ1 | Audit de déterminisme non refait sur v14 | Relancer l'audit sur le corpus courant ; marqueur déjà présent en section 1.4 |
| 9.3 | Test des 8 couples fait avec des modèles v8 et des profils construits | Refaire avec les modèles courants ; marqueur déjà présent en section 6.6 |
| 9.4 point 4 | Causes des désaccords GeT-RM non attribuées cas par cas | Marqueur déjà présent en section 8.2 |

Ces trois marqueurs ne sont pas nouveaux : ils reprennent des marqueurs existants ailleurs dans le mémoire. Les lever dans le chapitre 9 suppose de les lever d'abord à leur source.

## 4. Ce qui n'est délibérément pas dans ce chapitre

- **Aucun résultat nouveau, aucune mesure nouvelle, aucune extrapolation.** Le chapitre interprète ce qui a été mesuré ailleurs.
- **Aucune mention de l'évaluation finale sur les 138 profils**, qui n'a pas été faite. Si elle est réalisée avant le dépôt, un paragraphe devra être ajouté en 9.1 et la conclusion 9.6 ajustée.
- **Aucune recommandation de remplacer le modèle de l'application par XGBoost.** Le protocole prévoit que ce choix se discute avec l'encadrant ; le chapitre se borne à déplacer la justification du choix du réseau, ce qui est ce que le protocole autorise.

## 5. Conformité au formulaire officiel de dépôt

Le formulaire attend une section **« Conclusion » d'une page**, distincte de la discussion, qui relève de « Résultats et discussion ». Le chapitre 9 tel qu'écrit mélange les deux.

Lors de la mise en conformité, la découpe naturelle est la suivante : les sections 9.1 à 9.5 rejoignent « Résultats et discussion », et la section **9.6 devient la « Conclusion »** — elle est calibrée pour une page.

## 6. Points sur lesquels un jury interrogera probablement

Par ordre de probabilité :

1. **« Votre réseau est moins bon que XGBoost. Pourquoi avoir gardé le réseau ? »** La réponse est au RQ2 : sortie simultanée pour 189 médicaments en une passe, probabilités calibrées, extensibilité du jeu d'entrées. Il faut pouvoir la donner sans hésiter.
2. **« Que mesurez-vous exactement ? »** La réponse est en 9.1 et 9.3 : une fidélité à des recommandations, pas une justesse clinique.
3. **« Qu'est-ce qui sort de la circularité ? »** Trois choses, et seulement trois : GeT-RM pour les génotypes, l'IWPC pour une molécule, huit études pour la direction de l'effet.
4. **« Pourquoi 1 379 profils ? »** La réponse honnête est au point 6 de 9.4 : la règle de sélection n'a pas été retrouvée. C'est une limite déclarée, pas un choix justifié.
5. **« Que se passe-t-il si un gène manque ? »** RQ5 : la divergence passe de 0,1 % à 8,0 %, et c'est la règle affichée qui protège.

## 7. Cohérence vérifiée avec le reste du mémoire

- Les sept questions de recherche sont reprises dans l'ordre et dans les termes exacts de la section 1.6.
- Les six limites de 9.4 recoupent sans les contredire celles des sections 3.8, 4.10, 5.10, 6.8, 7.7 et 8.8 ; elles les regroupent au niveau de l'interprétation d'ensemble.
- Les quatre défauts de règles du point 3 sont ceux listés en section 5.10 point 7 et en section 7.2.
- La phrase finale sur le statut de prototype reprend celle de la section 5.1.
