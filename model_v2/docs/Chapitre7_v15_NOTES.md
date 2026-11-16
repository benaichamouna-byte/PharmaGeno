# Chapitre 7 v15 — notes

**Ce document ne fait pas partie du mémoire.** Il accompagne `Chapitre7_v15_MEMOIRE.md`, qui remplace le chapitre 7 de `Memoire_texte_v6.md`.

## 1. Provenance des chiffres
- Tous les résultats IWPC (5 774 ; 0,830 ; tableau 7.2 ; S3, S4, S5, S6, post hoc) : relus dans `Model_v8_7_9_10/results/pilier_B_iwpc_v1/resultats_pilier_B_iwpc.txt` (script `valider_warfarine_iwpc_v1.py`). Inchangés : l'analyse ne dépend pas du corpus.
- Warfarine dans le corpus v15 : **1 378 lignes, 938 STANDARD, 440 ADAPTER_DOSE**, recomptées ce jour dans `phenotype_drug_dataset_v15.csv` (tableau croisé CYP2C9 × VKORC1 : ADAPTER_DOSE si CYP2C9 ≤ 0,5 ou VKORC1 = 0).
- \*1/\*2 « aucune action » selon la DPWG : texte PharmCAT lu dans `detail_A1` (« no action is required », règle CYP2C9 \*1/\*2).
- VKORC1 CT « aucune action », TT 60 % : `Justification_regle_warfarine_et_omission_VKORC1_11nov2026.md` (PA166182841).

- **Section 7.7 (analyse post hoc, règle v15)** : `scripts/valider_warfarine_iwpc_v2_regle_v15.py` lancé sur le fichier IWPC que tu as envoyé (`PS215192-569836982_1.xls`, sha256 ee23fbb1595abf00). **Contrôle** : le script v1 relancé sur ce fichier redonne exactement les résultats archivés (5 774 ; 0,830 [0,804 ; 0,857] ; S1 à S5 identiques) : c'est bien le même fichier. Sorties : `results/pilier_B_iwpc_v2_regle_v15/resultats_iwpc_regle_v15.{txt,csv}` et le contrôle v1 dans `results/pilier_B_iwpc_v1_controle/`.

## 2. Ce qui a changé par rapport au texte v6
- Règle 6 (pas de date d'étape) : « fixé le 2 novembre 2026 à 18 h 19 » remplacé par « écrit et enregistré avec son empreinte avant toute comparaison ».
- Tableaux renumérotés dans l'ordre d'apparition (7.1 directives, 7.2 résultats ; le v6 avait 7.2 avant 7.1). Ligne \*1/\*2 ajoutée au tableau des résultats.
- Tableau 7.1 : colonnes corpus v14 / corpus v15.
- 7.2 : nouveau paragraphe « La règle du corpus v15 ».
- 7.6 : paragraphe final « Ce que ces résultats ont changé » (renvoi aux deux modifications v15).
- Nouvelle section 7.7 (analyse post hoc v15, tableau 7.3) ; anciennes 7.7 et 7.8 deviennent 7.8 et 7.9.
- 7.8 : deux limites ajoutées (règle v15 examinée seulement en post hoc ; allèles rares exclus).
- Justification de 21 mg et de 2 000 tirages : écrites honnêtement (fixés au protocole, pas de source) ; marqueur pour 2 000.

## 3. Marqueurs restants
1. CPNDS et RNPGx (warfarine) non examinés (tableau 7.1).
2. Nombre de tirages bootstrap non justifié (7.3).
3. ~~H1 et S5 avec l'étiquette v15~~ : **fait** (section 7.7, post hoc). Marqueur levé.

## 3 bis. Points d'honnêteté pour la soutenance
- La règle v15 sépare beaucoup mieux les doses (0,559 au lieu de 0,828 ; sensibilité 0,75 au lieu de 0,32). Ce n'est **pas** une validation indépendante : VKORC1 a été ajouté après avoir vu son effet dans ces mêmes données (S6). Le texte le dit.
- **Résultat défavorable à la v15** : \*1/\*2 sans VKORC1 A/A a une dose de 0,837 [0,805 ; 0,875] contre la référence. Le choix STANDARD suit la DPWG mais pas les doses. Gardé tel quel.
- 991 patients exclus (VKORC1 non renseigné) : population 4 783, différente des 5 774 du protocole.
- Les deux fichiers IWPC (.xls) : à garder sur Windows et Drive, **pas sur GitHub** (dépôt public ; données de patients redistribuées par ClinPGx).

## 4. Cohérence avec les autres chapitres (à reporter)
- **Chapitre 9 v15** (points 3 et « Corrections de règles identifiées ») et **résumé** : disent encore que VKORC1 est absent et que les défauts ne sont pas corrigés. À mettre à jour (tâche 4).
- Chapitre 3 v15 renvoie au chapitre 7 pour VKORC1 et CYP4F2 : cohérent.

## 5. Sauvegarde
WSL → Windows → GitHub → Drive (Docs › DOCs Memoire).
