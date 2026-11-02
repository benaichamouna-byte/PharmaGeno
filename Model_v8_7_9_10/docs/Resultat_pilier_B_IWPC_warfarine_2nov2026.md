# Résultat du pilier B — validation de la règle warfarine du corpus sur patients réels (IWPC), 2 novembre 2026
Protocole : `docs/Protocole_pilier_B_IWPC_2nov2026.md` (fixé à 18 h 19, empreinte e5be689f130bb8af, avant toute comparaison de groupes). Script : `scripts/valider_warfarine_iwpc_v1.py`. Sorties : `results/pilier_B_iwpc_v1/resultats_pilier_B_iwpc.{csv,txt}`. Chiffres principaux recoupés par un second calcul indépendant (pandas ; scikit-learn pour les R²).

## Données
IWPC « Ethnicity Data Set 2009 » (PS215192) : 6 922 sujets. Le fichier 2008 (5 700) y est inclus en totalité, non utilisé. Population principale : dose stable atteinte, dose renseignée, génotype CYP2C9 dans la correspondance : **5 774 patients** (1 423 ADAPTER_DOSE selon le corpus, 4 351 *1/*1). Exclus : 128 sans génotype CYP2C9, 17 avec un autre génotype (*5, *6, *11, *13, *14).

## H1 (principale) : SOUTENUE
Dose d'entretien des patients étiquetés ADAPTER_DOSE par le corpus, par rapport aux *1/*1 : rapport des moyennes géométriques **0,830 [0,804 ; 0,857]** (médianes 25,0 contre 30,0 mg/semaine). Borne haute < 1 : la règle va dans le bon sens.

## Ce qui est bien soutenu (IC à 95 %, bootstrap sur les patients)
| Génotype / classe | n | Rapport de dose vs *1/*1 | Médiane (mg/sem) |
|---|---|---|---|
| *1/*3 | 503 | 0,727 [0,689 ; 0,762] | 21,0 |
| *2/*2 | 59 | 0,728 [0,633 ; 0,837] | 22,8 |
| *2/*3 | 69 | 0,534 [0,461 ; 0,619] | 15,0 |
| *3/*3 | 20 | 0,350 [0,254 ; 0,477] | 11,0 |
| classe « lent » (*2/*3, *3/*3) | 89 | 0,486 [0,422 ; 0,558] | 14,0 |
| classe « intermédiaire » | 1 334 | 0,860 [0,833 ; 0,887] | 26,2 |
Ajusté (âge, taille, poids, amiodarone, origine ; erreurs robustes HC3) : ×0,771 [0,747 ; 0,795] (n = 3 641 ; la baisse de n vient des valeurs manquantes), inchangé après ajout de VKORC1 (×0,770 [0,747 ; 0,794], n = 3 095).
Gradient attendu : plus le génotype est défavorable, plus la dose baisse (0,73 -> 0,53 -> 0,35).

## Ce qui n'est PAS soutenu tel quel (à écrire dans le mémoire)
1. ***1/*2 (valeur 0,75, classée « intermédiaire » avec ADAPTER_DOSE par le corpus)** : rapport brut 0,972 [0,937 ; 1,008], médianes 28,0 contre 30,0. Dans la population complète, la dose de ce groupe n'est pas distinguable de celle des *1/*1. C'est le groupe le plus nombreux (772) de la classe « intermédiaire ».
   - Analyse **post hoc** (non prévue au protocole, vue après S1/S4) chez les patients White seulement : *1/*2 = 0,833 [0,800 ; 0,869]. Le brut proche de 1 vient donc en grande partie de la composition de la population (origines mélangées dans le groupe de référence), pas d'une absence d'effet. L'explication est plausible, mais elle reste post hoc et non testée formellement.
2. **Pouvoir de discrimination faible** (S5) : 39,6 % de doses basses (≤ 21 mg/sem) chez ADAPTER_DOSE contre 29,3 % chez *1/*1 ; sensibilité de l'étiquette pour les doses basses 0,307 [0,286 ; 0,328], spécificité 0,782 [0,769 ; 0,794]. L'étiquette indique une direction moyenne, elle ne prédit pas bien la dose individuelle.
3. **Les pourcentages de la règle DPWG** (20 % lent, 65 % intermédiaire) concernent la dose INITIALE ; les rapports observés (0,49 lent, 0,86 intermédiaire) concernent la dose d'ENTRETIEN. Description seulement, pas de test (S2).

## Limite majeure de la règle du corpus (S6, exploratoire)
La règle warfarine du corpus n'utilise que CYP2C9. Part de variance de log-dose : CYP2C9 seul **R² = 0,048** ; VKORC1 -1639 seul **R² = 0,294** ; les deux 0,356 (n = 4 629). VKORC1 A/G contre G/G : ×0,724 [0,702 ; 0,748] ; A/A : ×0,478 [0,463 ; 0,494]. Dans ces données, VKORC1 explique environ six fois plus de variance que CYP2C9 : l'étiquette du corpus pour la warfarine passe à côté du déterminant génétique principal. À présenter comme limite (et piste d'amélioration), sans l'attribuer au DL : c'est une limite de la règle source utilisée.

## Portée et limites
- Valide la règle sur une molécule (warfarine), pas les 189 médicaments. Le DL n'est pas testé directement (il reproduit les règles) ; un test direct demande les modèles entraînés.
- Associations observationnelles, doses d'entretien issues de plusieurs centres ; analyse ajustée sur cas complets.
- Confusion par l'origine : les fréquences alléliques CYP2C9 et VKORC1 diffèrent selon l'origine, d'où l'écart entre analyses brute et White.
- Références à citer après vérification : article IWPC (Klein et al., N Engl J Med 2009, PMID 19228618, https://pubmed.ncbi.nlm.nih.gov/19228618/) ; fichiers PharmGKB/ClinPGx PS215192. Non relus dans cette session : à vérifier avant citation.
