# Contrôle des règles contre leur texte de recommandation — 27 oct. 2026

Méthode : un écran automatique par mots-clés (ecran_texte_regles.py) SIGNALE les règles dont l'action semble contredire le texte ; il ne classe rien. Les règles signalées ont été lues une par une (monogènes : 123 signalées sur 501 ; multigènes : 39 sur 97). Les 35 règles « anti-inflammatoires » (texte = référence API) ont été relues ligne par ligne le même jour (API CPIC, guideline 110058). Limite : l'écran ne voit pas une erreur dont le texte ne contient aucun de ces mots.

## Erreur confirmée (corrigée dans les règles v10)
- Métoprolol, CYP2D6 = 0 (lent), source CPIC : action STANDARD alors que le texte dit « Initiate therapy with lowest recommended starting dose. Carefully titrate… monitor more closely for bradycardia. Alternatively, consider selecting another beta-blocker. » -> ADAPTER_DOSE. Effet : 66 lignes du corpus (STANDARD 133 606 -> 133 540 ; ADAPTER_DOSE 14 601 -> 14 667). Fichiers : data/regles_v10_monogene.csv (colonne decision_v10).

## Signalées puis vérifiées, pas d'erreur
- Phénytoïne / fosphénytoïne, CYP2C9 lent + HLA-B*15:02 négatif : règle CPIC « STANDARD » mais le texte dit « environ 50 % de moins » ; l'étiquette finale du corpus est ADAPTER_DOSE car la règle DPWG monogène (ADAPTER_DOSE pour CYP2C9 0 à 0,75) l'emporte (action la plus grave). Vérifié dans le corpus (162 lignes). La table CPIC distingue bien AS 1,0 (« environ 25 % de moins », classification Moderate) et AS 1,5 (« aucun ajustement ») : relu sur l'API CPIC (lecture par morceaux de 100 caractères), lignes HLA-B négatif / positif / sans résultat.
- Règles G6PD « résumé du texte » (rasburicase, dapsone, primaquine…) : texte générique, actions cohérentes avec les directives.

## À trancher (non modifié)
- Sertraline, citalopram, escitalopram, CYP2C19 intermédiaire (0,5) et sertraline CYP2B6 intermédiaire : texte « Initiate therapy with recommended starting dose. Consider a slower titration schedule and lower maintenance dose » (classification Optional ou Moderate selon la ligne). Étiquette actuelle STANDARD. Question : une dose de maintenance plus basse « à envisager » est-elle ADAPTER_DOSE ? Aucune règle écrite pour l'instant ; à décider avec la force de recommandation (Optional/Moderate/Strong) lue sur CPIC.
- Oxycodone (CYP2D6 0 ; 0,5 ; 2,0) « autre médicament OU rester attentif aux effets » : actuellement EVITER (type « alternative d'abord ») ; propafénone et flécaïnide : SURVEILLER. À harmoniser avec les types de l'audit des 81 règles.

## Pas encore fait
- Relecture de TPMT, NUDT15, SLCO1B1, UGT1A1 contre les classes CPIC qui regroupent plusieurs scores.
