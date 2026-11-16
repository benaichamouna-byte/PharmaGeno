# Fabrication du mémoire complet v15 (Word et PDF) — notes

**Ce document ne fait pas partie du mémoire.**

## 1. Comment le mémoire est fabriqué
1. `fabrication/fabriquer_memoire_complet.py` assemble les fichiers `*_MEMOIRE.md` dans l'ordre du formulaire ISBST : page de garde de la copie zéro v6 (logos compris), Remerciements, Résumé, Abstract, Sommaire, Liste des figures, Liste des tableaux, Liste des abréviations, Chapitre 1, Chapitre 2, Objectifs, Chapitres 3 à 9, Références, Annexe A, Annexe B. Les styles viennent de la copie zéro v6.
2. `fabrication/mettre_a_jour_index.py` remplit le sommaire et les deux listes avec LibreOffice et exporte le PDF.
   - Dans Word, Ctrl+A puis F9 remet les champs à jour.

## 2. Figures corrigées
Les images de la copie zéro v6 portaient des valeurs v14.
- **Figure 3.1** : refaite à partir de `phenotype_drug_dataset_v15.csv`.
  - Valeurs recomptées : 201 273 / 20 272 / 8 031 / 5 056, soit 234 632 lignes, identiques au tableau 3.2.
  - Script : `scripts/figures_v15_fig3_1_fig5_1.py`.
  - Les pourcentages sont maintenant écrits avec une virgule.
- **Figure 5.1** : seuil d'abstention 0,9965 (v14) remplacé par 0,9981 (application v8u, § 5.4). Le reste est inchangé et conforme au chapitre 5 v15.
- **Figures 4.1 et 8.1** : reprises telles quelles de la copie zéro v6.
  - Valeurs vérifiées contre le texte v15 : 1 860 340 paramètres, 34 entrées, 2 × 1 024 ; concordances GeT-RM 65/65 … 18/58.
  - Elles n'étaient pas encore sur GitHub et y sont ajoutées.

## 3. Liste des abréviations
Liste v6 reprise, avec ces changements :
- **retiré :** « RF », absent du texte v15, qui écrit « Random Forest » ;
- **ajoutés :** « F1 » (62 occurrences) et « JSON ».

## 4. Nombre réel de pages (PDF de 121 pages, sommaire mis à jour)
| Section ISBST | Pages réelles | Limite ISBST |
|---|---|---|
| Introduction (ch. 1) | 2 | 1-2 ✔ |
| Données bibliographiques (ch. 2) | 10 | 12-15 (2 en dessous) |
| Objectifs | 1 page + 2 lignes | 1 |
| Matériel et méthodes (ch. 3-5) | 37 (9 + 10 + 18) | 5-10 |
| Résultats et discussion (ch. 6-8 + discussion du ch. 9) | 37 + environ 8 | 15-30 |
| Conclusion (fin du ch. 9) | environ 1 | 1 |
| **Corps total (ch. 1 à 9)** | **97** | **36-60** |

Hors corps :
- références : 3 pages ;
- annexe A : 5 pages ;
- annexe B : 4 pages ;
- pages liminaires : 11 pages.

## 5. Points visibles sur le PDF
- Les cases de la page de garde (lieu, date, jury, institutions) sont des marqueurs surlignés en jaune, à remplir.
- La section « Objectifs » déborde de 2 lignes sur une deuxième page.
