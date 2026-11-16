# Marqueurs « [à compléter] » levés — notes

**Ce document ne fait pas partie du mémoire.** Il dit, pour chacun des 19 marqueurs, ce qui a été fait et d'où vient chaque chiffre. **Résultat : 0 marqueur restant, 0 renvoi cassé** (vérifié par script sur les 12 fichiers du mémoire).

| # | Chapitre | Marqueur | Ce qui a été fait | Source / contrôle |
|---|---|---|---|---|
| 1 | 1 (§ 1.4) et 9 (RQ1) | Audit de déterminisme v15 | **Calculé** : 57 constants + 118 un seul gène = 175 / 189 ; 14 multi-gènes (les 12 de v12 + fluindione + warfarine) | `phenotype_drug_dataset_v15.csv`, toutes les colonnes génétiques ; phénytoïne est déterminée par CYP2C9 seul **ou** par HLA-B\*15:02 seul (classée « un seul gène ») |
| 2 | 1 (§ 1.2) et 2 | « 34 gènes et 164 médicaments » | **Source corrigée** : le chiffre ne vient pas de Caudle 2025 mais de Suarez-Kurtz 2025 (accès aux recommandations CPIC du 25 mai 2025 ; 315 couples) | PMC12746351 lu (Br J Clin Pharmacol 2026;92(1):109-118, doi 10.1002/bcp.70278) |
| 3 | 2 | Caudle 2025 : volume, pages | **Trouvé** : Clin Pharmacol Ther 2025;118(6):1512-1519, doi 10.1002/cpt.70005 | Référence 1 de PMC13477175 ; l'article lui-même n'a pas pu être ouvert (Wiley refuse l'accès automatique) : il n'est plus cité pour un chiffre |
| 4 | 2 | Farmaki 2024 : conclusions | **Écrit** à partir du résumé : PRISMA, 29 articles, 19 systèmes, surtout aux États-Unis, adoption lente | Notice MEDLINE PMID 39136110 (OMICS 2024;28(9):442-460) ; **texte intégral non lu** |
| 5 | 3 (§ 3.1) | Courbe d'apprentissage | Déclarée non mesurée, renvoi en perspective (§ 9.5) | Décision du 12 nov. (travaux abandonnés) |
| 6 | 3 (§ 3.1) | Définition des niveaux de confiance | **Lue dans le code** : « moyenne » si une règle appliquée a la colonne `desaccord_autres_sources` remplie | `construire_corpus_v3.py`, ligne 26 et lignes 80-128 (moteur utilisé par `construire_corpus_v8.py`) |
| 7 | 3 (§ 3.8, point 4) | Résidu CYP2C9 | **146 lignes, siponimod, valeur 0,50** (\*1/\*3 : 50 % ; \*2/\*2 : aucune action), 0,06 % | Recompté dans le corpus v15 ; texte DPWG dans `regles_corrigees_v15.md` |
| 8 | 3 (§ 3.8, point 3) | Futur « seront retirés / rapportés » | Passé au passé composé + renvoi § 6.7 | Faits (modèles d'évaluation sur 1 207 profils) |
| 9 | 4 (§ 4.2) | Formule de perte avec la version de PyTorch d'entraînement | **Vérifié** avec PyTorch **2.11.0+cu130** (version de ta machine) : écart 0 en double précision ; aussi 0 avec 2.15.0 | Script `controle_perte_v1.py` (dans ce lot) |
| 10 | 4 (§ 4.5) | Seuil propre à EVITER | Déclaré : non fixé a priori, absent de l'application | — |
| 11 | 4 (§ 4.8) | Évaluation finale | Renvoi § 6.7 | — |
| 12 | 4 (§ 4.10, point 7) | Versions des bibliothèques | **PyTorch 2.11.0, scikit-learn 1.8.0, XGBoost 3.3.0**, relevées après coup ; réserve écrite | Ta commande du 16 nov. |
| 13 | 6 (§ 6.2) | Diagramme de fiabilité | **Tracé** (nouvelle figure 6.1) ; ECE recalculée 0,000292 = valeur publiée 0,00029 | 25 fichiers `oof_c35_cal_pli*_graine*.npz` (commit 96af010). Écart-type recalculé 0,000114, publié 0,00012 : petit écart non expliqué (arrondi ou convention), la valeur publiée n'est pas modifiée |
| 14 | 7 (tableau 7.1) | CPNDS et RNPGx | **Lu** : CPNDS = algorithme ; RNPGx = dose réduite de 20 à 80 % pour tout porteur, hétérozygotes compris | `data/PA166170752.json`, `data/PA166202621.json` |
| 15 | 7 (§ 7.3) | Nombre de tirages | **Contrôlé** : 10 000 tirages donnent les mêmes bornes à la 3e décimale | Recalcul sur le fichier IWPC (graines 0 et 1) |
| 16 | 8 (§ 8.2) et 9 | Causes des désaccords GeT-RM | Déclaré comme limite | — |
| 17 | 8 (§ 8.6) | Définition des verdicts | **Écrite** d'après le protocole figé | `validation_externe_v1_1/protocole/PROTOCOLE_validation_externe_v1.md` |
| 18 | 8 (§ 8.6) | Analyse refaite sur les règles v15 | Déclaré comme limite | — |

## Autres corrections faites au passage
- **Chapitre 5, § 5.9** : « PyTorch 2.14.1 ou plus récent » était **faux** (l'application tourne et passe ses tests avec 2.11.0 sur ta machine) ; remplacé.
- **Chapitre 6** : figures renumérotées dans l'ordre d'apparition : 6.1 diagramme de fiabilité (nouveau), 6.2 abstention (ancienne 6.1), 6.3 comparaison (ancienne 6.2). Les fichiers d'image `fig_6_1.png` et `fig_6_2.png` gardent leur nom.
- **Chapitre 7, § 7.7** : la directive RNPGx est plus proche des doses observées que la DPWG sur \*1/\*2 et A/G : phrase ajoutée.

## À reporter dans la bibliographie (tâche suivante)
- Suarez-Kurtz G. Pharmacogenomics in clinical practice: biomarker information in Brazilian drug labels. Br J Clin Pharmacol 2026;92(1):109-118. doi:10.1002/bcp.70278
- Caudle KE, Whirl-Carrillo M, Relling MV, et al. Advancing clinical pharmacogenomics worldwide through the Clinical Pharmacogenetics Implementation Consortium (CPIC). Clin Pharmacol Ther 2025;118(6):1512-1519. doi:10.1002/cpt.70005
- Farmaki A, Manolopoulos E, Natsiavas P. Will precision medicine meet digital health? A systematic review of pharmacogenomics clinical decision support systems used in clinical practice. OMICS 2024;28(9):442-460. PMID 39136110
- CPNDS : Shaw K, et al. Ther Drug Monit 2015 (PMID 26186657) — **à vérifier avant citation** (seul le PMID est dans la fiche ClinPGx).
