# Journal de Bord du Projet PharmaGeno : 21 octobre 2026 (après-midi, 14 h 45)

Complète `Journal_de_Bord_21oct2026_midi.md` (rien n'est écrasé). Un résultat n'est cité que s'il a été mesuré ; « validé » = validé par Mouna.

## 1. Décision de Mouna (règle absolue, répétée plusieurs fois par elle)
- **Objectif du DL : il prend le profil génétique du patient et prédit le médicament** (entrée = profil ; sortie = recommandation sur les médicaments). Les gènes et les médicaments sont les lettres, le profil est le mot, la recommandation est le sens. Le DL doit apprendre à combiner les gènes ; il ne doit pas recopier les règles CPIC.
- Cet objectif n'est plus à valider : il est acquis. Ne plus le soumettre à validation.
- Priorité : l'application et un DL le plus optimal possible.

## 2. Écart constaté avec le DL actuel (à corriger)
- Le DL actuel reçoit le profil ET le médicament (identifiant = simple numéro) et rend l'action pour CE médicament. Ce n'est pas « profil -> médicament ».
- Structure des données (mesurée le 21 oct., corpus v7) : 130 578 lignes = 1 379 profils x 117 médicaments, sans doublon ; médicaments étiquetés par profil : min 53, médiane 95, max 105 ; actions : STANDARD 112 013, ADAPTER_DOSE 11 902, EVITER 5 995, SURVEILLER 668. Un tableau « 1 profil -> une action par médicament » (valeurs manquantes masquées) se construit donc directement à partir des données existantes.
- Mesures déjà faites (journaux 19-20 oct.) : médicament jamais vu, F1 macro DL 0,467 (RF 0,502, XGBoost 0,454) ; modèle final avec identifiant de médicament F1 0,9980 ; retrait de combinaisons de gènes : 100 % tricycliques, 0 % thiopurines, défaut HLA-B*58:01.

## 3. Erreurs à ne plus reproduire
- Redemander une validation sur l'objectif du DL après qu'elle l'a répété plusieurs fois ; proposer des plans longs et techniques quand elle demande simple.
- Garder le médicament comme ENTRÉE du DL alors que son objectif est profil -> médicament.
- Faire des tests de variantes (combinaisons) sans avoir d'abord vérifié que la formulation du problème correspond à son objectif.

## 4. Plan (chaque entraînement validé avant lancement ; ensemble final de 12 524 lignes fermé)
1. Construire le tableau profil -> 113 médicaments à partir du corpus v7 (aucun entraînement) et le montrer.
2. Modèle « profil -> toutes les recommandations » : entrée = profil, une sortie par médicament ; protocole inchangé (StratifiedGroupKFold(5) par famille, graine 42). Comparaison avec le DL actuel sur les mêmes plis.
3. Test du retrait de combinaisons de gènes sur ce modèle ; correction HLA-B*58:01 documentée.
4. Application v8f ; sortie « 1 à 3 médicaments » par spécialité issue de ce modèle.
5. Comparaison PharmCAT et étude publiée ; chapitres 3 à 8 ; date de dépôt.
