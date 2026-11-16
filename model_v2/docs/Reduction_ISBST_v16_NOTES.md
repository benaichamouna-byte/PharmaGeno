# Mise en conformité ISBST : réduction du corps du mémoire — notes

**Ce document ne fait pas partie du mémoire.**

## 1. Principe : rien n'est supprimé, tout est déplacé

Le corps du mémoire passe de **97 à 61 pages**. Aucun contenu scientifique n'a été retiré : les développements, les tableaux de détail, les contrôles et les analyses secondaires sont déplacés dans cinq nouvelles annexes.

| Nouvelle annexe | Contenu | Venait de |
|---|---|---|
| **C** Compléments sur les données | effectifs et leur origine, codage des gènes, sources et évolution des règles, entrées du modèle, métadonnées, description complète des 11 limites | chapitre 3 |
| **D** Compléments sur les méthodes | architecture antérieure, écriture de la perte, recherche d'hyperparamètres, calibration, abstention, réseau de choix, comparaison des modèles, modèles finaux, origine de chaque valeur numérique, versions des bibliothèques | chapitre 4 |
| **E** Compléments sur l'application | modules et routes, lecture du VCF et choix du pipeline PyPGx, moteur et sorties, tests, installation, description complète des 9 limites | chapitre 5 |
| **F** Les 189 médicaments du corpus | tableau produit par programme : ATC4, gènes des règles, lignes, actions | nouveau |
| **G** Compléments sur les résultats | tableaux de détail, contrôles de programme, études indépendantes, amendements de protocole, détail de l'évaluation finale, réseau de choix, protocole warfarine, définition des verdicts, les 136 lignes PharmCAT | chapitres 6, 7 et 8 |

L'ancienne annexe B est devenue **B.1**, et l'illustration sur NA06991 (ancienne section 8.7) **B.2**.

## 2. Autres changements de structure

- La **conclusion** est une section de premier niveau d'une page, séparée du chapitre 9, qui devient « Discussion, limites et perspectives ».
- Les limites des chapitres 3, 4, 5 et 8 sont des listes courtes dans le corps, renumérotées, avec la description complète en annexe.
- Figures 4.1 et 5.1 réduites ; §5.6 et §5.7 fusionnées ; §5.8 et §5.9 fusionnées.

## 3. Nombre de pages mesuré sur le PDF (135 pages)

| Section ISBST | Pages | Limite | État |
|---|---|---|---|
| Introduction (ch. 1) | 2 | 1-2 | conforme |
| Données bibliographiques (ch. 2) | 11 | 12-15 | 1 page en dessous |
| Objectifs | 1 | 1 | conforme |
| Matériel et méthodes (ch. 3-5) | 12 | 5-10 | 2 pages au-dessus |
| Résultats et discussion (ch. 6-9) | 34 | 15-30 | 4 pages au-dessus |
| Conclusion | 1 | 1 | conforme |
| **Corps total** | **61** | **36-60** | 1 page au-dessus |

Hors corps : liminaires 11, références 4, annexes A à G 59.

L'écart restant tient aux tableaux de résultats, qui ne peuvent pas aller en annexe sans vider les chapitres de ce que le jury doit lire. Il est assumé et déclaré.

## 4. Corrections de fond apportées au même moment

1. **Fluvastatine** : le mémoire comptait « quatre corrections de règles » alors que la quatrième était une vérification sans modification. Partout : trois corrections (warfarine/VKORC1, CYP2C9 selon la DPWG, thiopurines) et une vérification.
2. **Résumé et abstract** : les étiquettes ne viennent pas seulement de CPIC et DPWG ; « principalement CPIC et DPWG, complétées par RNPGx et des étiquettes réglementaires ». 198 et 185 mots.
3. **Classe ATC4** : « médicaments interchangeables » remplacé par « sous-groupe ATC4 », avec la réserve de la méthodologie officielle, qui dit que le classement d'une substance n'est pas une recommandation d'usage et ne convient pas pour décider d'une substitution thérapeutique (référence ajoutée).
4. **Pipeline PyPGx** : le choix de `run-chip-pipeline` sur des VCF est désormais explicité en annexe E.2 : VCF comme unique entrée, sans imputation, aucun appel de variation structurale revendiqué, pipeline NGS non comparé, garantie externe = GeT-RM (section 8.2). Référence à la documentation ajoutée.
5. **Taille du corpus (ch. 2)** : « plus de vingt fois plus » remplacé par la formulation exacte — 1 241 profils indépendants produisant 211 177 couples, qui ne sont pas 211 177 individus indépendants.
6. **Codes ATC manquants** : recomptés dans la table employée par l'application v8u (atc\_mapping\_medicaments\_v14.csv) : **14** médicaments sans code utilisable, dont 8 absents de la table et 6 sans code fiable. Le mémoire disait « huit ».
7. **Mentions de travail inachevé** : « reste à faire », « n'est pas encore », « une relecture est prévue » → « n'a pas été réalisé dans le cadre de ce travail ». La section 8.6 reste exploratoire sans annoncer de suite.
8. **H-RNPGx-1** : hypothèse définie à partir de la table des règles (8 règles RNPGx, toutes pour la fluindione).
9. **Bibliographie** : Caudle 2025 pages 1512-**1522** (et non 1519) ; Hodel 2024 complété (17(9):e70009, doi 10.1111/cts.70009) ; Farmaki doi 10.1089/omi.2024.0131 ; compléments Chen 785-794, Jithesh 7(1):10, Kapoor 4(9):100804, Lim 10(11). Les 31 références à DOI ont été vérifiées une par une dans Crossref. 55 références.
10. **Figure 6.1** : la légende donne l'ECE ; les axes et la diagonale sont expliqués dans le texte.
11. **Allèles étoile** : `*1, *2` s'affichaient « 1, 2 » dans la liste des abréviations ; corrigé dans le script de fabrication.
12. **Médicaments non évalués** : la limite 4 du chapitre 5 donne les vrais chiffres (72 sur 189, dont 60 pour CYP2D6, ramenés à 25 après saisie).

## 5. Ce qui n'a pas été fait, et pourquoi

- **RQ1 n'est pas reformulée.** Réécrire une question de recherche après avoir vu les résultats, pour qu'elle corresponde à ce qui a pu être mesuré, est une pratique critiquable (HARKing). RQ1 reste telle qu'elle a été posée ; le chapitre 9 y répond avec l'audit de déterminisme et dit explicitement qu'aucun modèle « un seul gène » n'a été entraîné.
- **Le titre n'est pas modifié.**
- **La page de garde n'est pas remplie** (lieu, date, jury).

## 6. Contrôle automatique

`fabrication/controle_memoire.py` vérifie les renvois de section, de chapitre, d'annexe, de tableau, de figure et de formule ; les marqueurs restants ; les citations sans référence et les références jamais citées ; la numérotation continue des tableaux et des figures ; les tableaux et figures jamais appelés dans le texte.

Résultat sur la version finale : **18 fichiers, 30 tableaux, 24 figures, 55 références, aucun problème.**

## 7. Fabrication

`fabrication/fabriquer_memoire_complet.py` assemble le document, `mettre_a_jour_index.py` remplit le sommaire et les listes et exporte le PDF, `compter_pages.py` mesure les pages par section.

## 8. Sauvegarde

WSL → Windows → GitHub → Drive (Models › Model V2 › docs).
