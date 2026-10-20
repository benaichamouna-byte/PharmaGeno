# Journal de Bord du Projet PharmaGeno - 20 octobre 2026, matin (suite des journaux du 19 oct. soir et addendum 21h40)

## 0. Règles absolues (inchangées)
- Le DL est le CŒUR du sujet et de l'application : ne jamais le reléguer ; un mauvais résultat est un problème à résoudre avec le DL au centre.
- Rien n'est écrasé (nouvelles versions à côté) ; une seule action demandée à Mouna à la fois ; chaîne de sauvegarde WSL -> Windows -> GitHub -> Drive.

## 1. Fait (vérifié dans les fichiers)
- Lecture de deux articles : Drouin et al., Sci Rep 2019;9:4071 (doi 10.1038/s41598-019-40561-2) : résistance aux antibiotiques bactérienne, modèles à règles CART/SCM comparables à 5 méthodes de référence, argument d'interprétabilité ; pas de pharmacogénomique humaine. Zack et al., npj Digit Med 2026;9:541 (doi 10.1038/s41746-026-02590-w) : agent LLM générant des recommandations de type CPIC ; extraction 91,9 % sur 22 articles ; évaluation experts sur 24 recommandations, 17 paires gène-médicament CPIC ; couverture limitée des guidelines ; pas de niveau patient.
- Intégrité : l'ancien ensemble final (15 oct., protocole v7, 7 620 lignes, 138 familles) et le nouveau (protocole v8/corpus v7, 12 524 lignes, 138 familles) ont 13 familles en commun ; les 125 autres n'ont jamais servi d'ensemble final. Rien n'a été choisi sur l'ensemble final. À mentionner dans le mémoire. L'ensemble final du nouveau protocole n'a JAMAIS été lu.
- Modèles de l'application v8 (modele_final_v8.py ; DL film identifiant, poids racine, EVITER x2 ; XGBoost identifiant ; entraînés sur les ~90 % ; ensemble final non lu). Validation interne (11 335 lignes, familles à part) : DL F1 0,9984, EVITER manqués 0,0051 ; XGBoost F1 1,0000. Seuils d'abstention calculés sur les probabilités hors-plis de la validation croisée (confiance <= 0,930 pour 1 %).
- Référence CPIC (regle_cpic_v8.py) : redonne exactement les 130 578 étiquettes du corpus v7 (0 différence) ; aucune action sur les 30 765 lignes non étiquetées. 30 765 des 161 343 paires profil x médicament (19,1 %) n'ont aucune action de référence.
- Domaine de validité (domaine_v8.json) : 117 médicaments, 113 dans le modèle, 4 en référence CPIC seule ; 60 médicaments à étiquette variable.
- Moteur v8 (moteur_v8.py) : DL = moteur ; XGBoost = second avis ; référence CPIC affichée avec sa source ; couche de sécurité ; abstention ; alertes incertain / desaccord_xgboost / desaccord_cpic. Tests T1 à T5 PASS (mécanique sur lignes d'entraînement, pas de performance).
- Sauvegardé sur les 4 supports : lot_app_v8_moteur_20oct2026.zip (1 648 661 octets ; GitHub d51bbcc ; Drive 1,6 Mo).

## 2. Plan restant : voir Journal_de_Bord_20oct2026_midi.md
