# Journal de Bord du Projet PharmaGeno : 23 octobre 2026, addendum de 13 h 50

Complète le journal de l'après-midi (rien n'est écrasé). Les deux phrases du journal de l'après-midi « rend warfarine/citalopram testables » et « récupère les 15 médicaments » sont FAUSSES (voir section 2).

## 1. Décisions validées par Mouna
- Groupe A : 67 règles, 16 médicaments (« ok » de 12 h 01).
- Règle de décision pour les règles ambiguës : on retient la première instruction du texte publié (« ok » de 12 h 41 puis 13 h 11). 59 règles mono-gène : 53 gardées (36 éviter, 15 adapter la dose, 2 standard), 1 corrigée (halopéridol CYP2D6 UM : standard -> adapter la dose), 5 exclues (quétiapine, mavacamten, méloxicam, piroxicam, ténoxicam).
- Antivitamines K : étiquetage v8 gardé (acénocoumarol et phenprocoumone, DPWG VKORC1 TT -> 50 % de la dose initiale ; warfarine inchangée). À écrire dans le mémoire comme un changement par rapport à v7.
- Réponse à Pr. Ghedira (13 h 44) : réunion lundi 26 oct. après-midi (heure à confirmer) ; projet partagé pour déploiement et tests une fois finalisé.

## 2. Mesures et corrections
- 59 règles mono-gène (aperçu, non officiel) : corpus 152 600 -> 156 696 (+4 096), 30 médicaments, 0 étiquette existante modifiée, médicaments dépendant du génotype 63 -> 74.
- 22 règles multi-gènes ambiguës (amitriptyline 4, fluvastatine 6, rosuvastatine 3, sertraline 9) : proposition = 22 gardées, 0 corrigée, 0 exclue ; 5 restent inutilisées (conditionnelles, le moteur écarte les multi-gènes conditionnelles). Effet : +27 lignes (rosuvastatine seulement), 0 étiquette modifiée. Pour les 18 règles (amitriptyline, fluvastatine, sertraline) dont le génotype existe chez les profils réels, la classe est identique à l'étiquette déjà obtenue par les règles mono-gène (cohérence, pas validation indépendante). Total aperçu : 156 723 lignes.
- CORRECTION : la warfarine n'est pas parmi les 35 médicaments des 59 règles ; sur les vrais VCF, les 59 règles ne récupèrent que 3 médicaments sur 25 (NA19472) et 0 sur 15 (NA19085). Les 15 médicaments sans prédiction ne sont donc PAS récupérés par ces règles.
- Note du 12 h 40 corrigée : 53 gardées = 36 éviter, 15 adapter la dose, 2 standard (une version avait écrit 16 et 1).

## 3. Erreurs à ne plus reproduire
- Annoncer un gain (warfarine, 15 médicaments) sans l'avoir mesuré.
- Ajouter une règle qui change un choix documenté dans les scripts (antivitamines K) sans le dire avant le « ok ».
- Écrire un compte dans une note sans le recalculer (16/1 au lieu de 15/2 ; 19 au lieu de 18 règles).
- Interpréter un « ok » ambigu sans dire la lecture retenue dans le même message.

## 4. Plan exact de ce qui reste
1. « ok » de Mouna sur les 22 règles multi-gènes ; puis règles v9 + corpus v9 (fichiers à côté des anciens, anciennes lignes vérifiées inchangées) ; un seul réentraînement (protocole v9, ensemble final de 138 profils non lu) ; domaine v10 ; application à côté de v8m ; tests ; journal. Question ouverte : réentraîner maintenant ou avec le groupe B.
2. Sauvegarde du lot du 23 oct. AVANT la réunion de lundi (demande de l'encadrant : avancement sur Drive et par email) : WSL -> Windows -> GitHub -> Drive. Rien du 23 oct. n'était sauvegardé avant ce lot.
3. Email à Pr. Ghedira (brouillon prêt : message à coller, avancement, lien Drive) ; captures de l'écran v8m à joindre.
4. Paquet de déploiement et de test pour l'encadrant (code, modèles, installation, README, versions des paquets, md5), quand la version est figée.
5. Groupe B (27 médicaments, nouveaux gènes) puis groupe C (24) ; médicaments FDA (226) et 2B (23) non utilisés ; les 22 médicaments du groupe A non utilisables restent sans étiquette.
6. Cas « aucune ligne » pour des vrais profils (valeurs CYP2D6/G6PD sans règle : aripiprazole, brexpiprazole, halopéridol, rispéridone, dapsone, primaquine) ; décision sur un support minimal du domaine (flucytosine, amitriptyline, rosuvastatine, sertraline).
7. Validation indépendante du DL (tamoxifène/CYP2D6 ITPC ; sources manquantes pour thiopurines, UGT1A1/irinotécan, IPP, tacrolimus, G6PD, tricycliques) ; figures et statistiques ; protocole d'évaluation gelé ; évaluation finale unique (138 profils, 14 731 lignes) ; chapitres 3 à 8 ; Plan Excel ; date de dépôt (~12 nov., non confirmée).
8. Corrections de l'application : rouge trop sévère CYP2C19 rapide ; simvastatine/tamoxifène ; ibuprofène (ATC) ; indication non demandée ; noms français des groupes (« vitamin k antagonists ») ; accord des verbes ; « aucun gène lisible » ; multi-gènes « non interprété » ; atorvastatine/SLCO1B1 ; anciens test_moteur_v8*.py.
9. Ménage : copies Drive mal placées, fichier parasite à la racine GitHub, commit 494a50e « Unverified », uploads Drive en attente, doublon `pharmageno_v8j (1).zip`.
