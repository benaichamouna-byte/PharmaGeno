# Règle de la Partie 1 (génotype contre GeT-RM) — v1, gelée le 7 nov. 2026 AVANT tout calcul sur ces échantillons
Personnes : les 104 de liste_104_gelee.txt = présentes dans le tableau consolidé GeT-RM (V4, 22 janv. 2025 ; modifs 1 août 2025), ABSENTES du corpus v14, PRÉSENTES dans le bundle 1KGP GRCh38. Les 7 personnes de l'ensemble final sont exclues par construction (elles sont dans le corpus).
Outils comparés à GeT-RM : (1) PyPGx 0.27.0, commande identique à celle de l'application (run-chip-pipeline, bundle 1KGP, GRCh38) ; (2) PharmCAT (version indiquée dans le rapport, jamais -0 / --absent-to-ref).
Gènes : ceux présents à la fois dans l'application et dans le tableau GeT-RM, à génotype de type diplotype : CYP2B6, CYP2C19, CYP2C9, CYP3A5, DPYD, NUDT15, SLCO1B1, TPMT, UGT1A1 (+ CYP3A4, NAT2, CYP4F2, VKORC1 : lus et rapportés à part si l'écriture n'est pas comparable). CYP2D6 : non appelable depuis ces VCF, exclu.
Catégories par (personne, gène, outil), liste fermée :
 1. identique : mêmes deux allèles (ordre ignoré) ;
 2. identique au sous-allèle près : même allèle principal (ex. *1A / *1B / *1 ; *3A / *3C selon la numérotation) — comptée à part, listée ;
 3. GeT-RM incertain : référence entre parenthèses, « or », ou texte non diplotype — comptée à part, non incluse dans le dénominateur ;
 4. non appelé par l'outil (indéterminé / absent) — compté à part ;
 5. discordant : tout le reste. Chaque cas de 5 est relu à la main et reçoit une cause : (a) écriture non comparable, (b) variant non couvert par l'outil, (c) allèle récent dans GeT-RM absent de la version de l'outil, (d) erreur de l'outil, (e) autre.
On rapporte : effectifs entiers avec n par gène et par outil, listes complètes des catégories 2, 4 et 5. Aucun pourcentage sans n. Toute analyse ajoutée après coup est étiquetée « décidée après ».
