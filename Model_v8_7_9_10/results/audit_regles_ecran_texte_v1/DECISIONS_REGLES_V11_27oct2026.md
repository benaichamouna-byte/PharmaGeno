# Décisions sur les règles — version v11 — 27 oct. 2026 (validée par Mouna : « ok fais », option A)

Règle écrite à l'avance, fondée sur la force de recommandation CPIC lue sur l'API CPIC (api.cpicpgx.org/v1/recommendation, lecture ligne par ligne) :
- Une recommandation CPIC « Moderate » ou « Strong » qui demande une dose d'entretien plus basse = ADAPTER_DOSE. « Optional » = inchangé (STANDARD).
- « Alternative OU surveillance » (deux options au choix) = action du milieu, comme pour le type 3 de l'audit des 81 règles (SURVEILLER quand l'une des deux options est la surveillance).
- Entre sources en désaccord, l'action la plus grave (convention déjà utilisée dans le corpus).

## Règles modifiées (9) — data/regles_v11_monogene.csv (7) et regles_v11_multigene.csv (2), colonne decision_v11
1. Citalopram, escitalopram, sertraline, CYP2C19 intermédiaire (0,5) : STANDARD -> ADAPTER_DOSE. CPIC Moderate (« Consider a slower titration schedule and lower maintenance dose »). Sertraline : ligne CYP2B6 « No Result » x CYP2C19 intermédiaire, Moderate.
2. Sertraline, multigène : CYP2B6 0,5 x CYP2C19 1,0 et CYP2B6 1,0 x CYP2C19 0,5 : STANDARD -> ADAPTER_DOSE (Moderate). CYP2B6 0,5 x CYP2C19 0,5 reste STANDARD (Optional). Sertraline CYP2B6 intermédiaire seul : Optional, reste STANDARD.
3. Oxycodone, CYP2D6 0 ; 0,5 ; 2,0 : EVITER -> SURVEILLER (texte : « sélectionner un autre médicament OU rester attentif aux effets »).
4. Azathioprine, TPMT lent (0) : ADAPTER_DOSE -> EVITER. CPIC Strong (TPMT lent x NUDT15 sans résultat) : « Consider alternative nonthiopurine immunosuppressant therapy ». DPWG : alternative ou 10 % de la dose. Action la plus grave. Mercaptopurine (CPIC : réduire 10 fois pour une malignité, alternative sinon) et thioguanine (réduire 10 fois) : ADAPTER_DOSE conservé.

## Effet sur le corpus v11 (157 432 lignes, 133 médicaments, 1 379 profils)
STANDARD 132 286 | ADAPTER_DOSE 15 912 | EVITER 7 831 | SURVEILLER 1 403. Par rapport à v10 : 1 894 étiquettes changées (oxycodone 631 EVITER -> SURVEILLER ; citalopram 444, escitalopram 444, sertraline 366 STANDARD -> ADAPTER_DOSE ; azathioprine 9 ADAPTER_DOSE -> EVITER).

## Vérifié, rien à changer
- NUDT15 faible (0) = alternative (CPIC), TPMT/NUDT15 intermédiaires = dose réduite : cohérent avec les règles.
- SLCO1B1 : les 5 catégories CPIC (augmentée, normale, diminuée possible, diminuée, faible) correspondent aux valeurs 1,5 ; 1,0 ; 0,5 ; 0,0. « Diminuée possible » et « diminuée » ont la même recommandation sur les lignes lues (atorvastatine, fluvastatine). Limite : la requête a renvoyé 60 lignes ; les lignes de simvastatine, pravastatine, rosuvastatine, lovastatine et pitavastatine n'ont pas toutes été relues.
- UGT1A1 : non relu contre l'API (reste à faire).
