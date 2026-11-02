# Résultat DL corpus v14 : config 35 + calibration par température (2 novembre 2026)
Protocole identique à v13 (`protocole_commun_v10` : StratifiedGroupKFold groupé par famille, graine 42, 5 plis × 5 graines = 25 entraînements ; ensemble final de 138 familles NON lu ; 209 415 lignes hors finale). **Aucun nouveau réglage** : configuration 35 choisie sur v13 par recherche imbriquée (2 couches de 1024, ReLU, sans BatchNorm, dropout 0,1, lissage 0,05, Adam 1e-3, poids de classes en puissance 0,5, EVITER ×1), température ajustée sur la validation interne (10 % des familles). Script : `scripts/evaluer_dl_imbrique_v5.py` (copie de v4 ; v4 intact). Sorties : `results/dl_imbrique_v14/`.

## Résultats (moyenne ± écart-type sur 25 entraînements)
| Mesure | v14 (189 médicaments) | v13 (176 médicaments, 31 oct.) |
|---|---|---|
| F1 macro | 0,9979 ± 0,0012 | 0,9980 ± 0,0010 |
| Exactitude | 0,9995 ± 0,0003 | — |
| Log-loss | 0,0030 ± 0,0017 | 0,0028 |
| ECE | 0,0003 ± 0,0002 | 0,0004 |
| EVITER manqués (moy. 5 graines) | 60,2 / 7 227 (0,83 %) | 55 / 7 227 (0,76 %) |
| Faux EVITER | 8,4 | 2 |
| Erreurs totales | 113,0 sur 209 415 lignes (0,054 %) | 94 sur 193 332 lignes (0,049 %) |
| Température T | 0,16 à 0,31 | 0,21 à 0,32 |
F1 macro par pli : 0,9979 / 0,9989 / 0,9992 / 0,9961 / 0,9972.

## Lecture (sans extrapoler)
- Les performances sont équivalentes à celles de v13 ; l'extension du corpus ne les dégrade pas. Les 13 médicaments ajoutés depuis v13 n'ajoutent que 1,4 erreur en moyenne sur 16 084 lignes évaluées.
- Ces nombres ne sont pas appariés avec v13 : le corpus change, donc le découpage en plis change ; les écarts de comptes (EVITER manqués 60,2 contre 55, faux EVITER 8,4 contre 2) ne sont pas interprétables comme une dégradation ou une amélioration sans analyse appariée (non faite).
- Erreurs concentrées sur des médicaments déjà présents : rosuvastatin 16,0 ; sertraline 16,0 ; azathioprine 13,8 ; fluvastatin 11,6 ; meloxicam 9,6 ; faux EVITER surtout meloxicam (3,8).
- Par niveau de source (F1 macro moyen) : CPIC 0,9984 ; DPWG 0,9923 ; FDA 0,9995 ; FDA-étiquette 0,9986 ; RNPGx 0,9997 ; HCSC-étiquette 1,0 ; **EMA-étiquette 0,9333** (très peu de lignes non STANDARD, notamment lonafarnib : 1 ligne ADAPTER_DOSE ; chiffre peu stable).
- Rappel de portée : le F1 mesure l'accord avec le moteur de règles qui a produit les étiquettes, pas la justesse clinique (voir pilier B pour une validation indépendante sur la warfarine).

## Suite
Entraînement des modèles finaux (profil et choix) sur v14, domaine v14, moteur, application v8q.
