# Chapitre 7 v15 — notes

**Ce document ne fait pas partie du mémoire.** Il accompagne `Chapitre7_v15_MEMOIRE.md`, qui remplace le chapitre 7 de `Memoire_texte_v6.md`.

## 1. Provenance des chiffres
- Tous les résultats IWPC (5 774 ; 0,830 ; tableau 7.2 ; S3, S4, S5, S6, post hoc) : relus dans `Model_v8_7_9_10/results/pilier_B_iwpc_v1/resultats_pilier_B_iwpc.txt` (script `valider_warfarine_iwpc_v1.py`). Inchangés : l'analyse ne dépend pas du corpus.
- Warfarine dans le corpus v15 : **1 378 lignes, 938 STANDARD, 440 ADAPTER_DOSE**, recomptées ce jour dans `phenotype_drug_dataset_v15.csv` (tableau croisé CYP2C9 × VKORC1 : ADAPTER_DOSE si CYP2C9 ≤ 0,5 ou VKORC1 = 0).
- \*1/\*2 « aucune action » selon la DPWG : texte PharmCAT lu dans `detail_A1` (« no action is required », règle CYP2C9 \*1/\*2).
- VKORC1 CT « aucune action », TT 60 % : `Justification_regle_warfarine_et_omission_VKORC1_11nov2026.md` (PA166182841).

## 2. Ce qui a changé par rapport au texte v6
- Règle 6 (pas de date d'étape) : « fixé le 2 novembre 2026 à 18 h 19 » remplacé par « écrit et enregistré avec son empreinte avant toute comparaison ».
- Tableaux renumérotés dans l'ordre d'apparition (7.1 directives, 7.2 résultats ; le v6 avait 7.2 avant 7.1). Ligne \*1/\*2 ajoutée au tableau des résultats.
- Tableau 7.1 : colonnes corpus v14 / corpus v15.
- 7.2 : nouveau paragraphe « La règle du corpus v15 ».
- 7.6 : nouveau paragraphe « Ce que ces résultats disent de la règle du corpus v15 », avec deux réserves (A/G non distingués ; règle v15 non testée).
- 7.7 : deux limites ajoutées (règle v15 non testée ; allèles rares exclus).
- Justification de 21 mg et de 2 000 tirages : écrites honnêtement (fixés au protocole, pas de source) ; marqueur pour 2 000.

## 3. Marqueurs restants
1. CPNDS et RNPGx (warfarine) non examinés (tableau 7.1).
2. Nombre de tirages bootstrap non justifié (7.3).
3. **H1 et S5 avec l'étiquette v15** (7.6) : faisable en quelques minutes avec le fichier IWPC qui est sur ta machine (`valider_warfarine_iwpc_v1.py` + une étiquette v15). À présenter comme post hoc. À décider.

## 4. Cohérence avec les autres chapitres (à reporter)
- **Chapitre 9 v15** (points 3 et « Corrections de règles identifiées ») et **résumé** : disent encore que VKORC1 est absent et que les défauts ne sont pas corrigés. À mettre à jour (tâche 4).
- Chapitre 3 v15 renvoie au chapitre 7 pour VKORC1 et CYP4F2 : cohérent.

## 5. Sauvegarde
WSL → Windows → GitHub → Drive (Docs › DOCs Memoire).
