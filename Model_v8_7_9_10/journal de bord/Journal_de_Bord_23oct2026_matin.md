# Journal de Bord du Projet — 23 octobre 2026, matin (suite du journal du 22 oct. fin 23 h 50)

## 0. Le cœur du sujet (à rappeler à chaque livraison)
Webtool de RECOMMANDATION : VCF du patient + spécialité -> le DL lit tout le profil et combine les gènes -> la page recommande, réponse claire en haut (✔ / ▲ / ✖). Pas un test médicament par médicament.

## 1. Décisions et résultats
- Test de 2 vrais VCF fait (NA19472, NA19085 ; tirage aléatoire hors jeu final, hors HG00101, hors 19 validés ; `scripts/choisir_profils_test_vcf_v1.py`). Zip livré : `pharmageno_test_vcf_reel_v1.zip` (md5 f96c18a75bc576e4a2eafa13f542ba8c) ; détail : `results/test_vcf_reel_v1/LISEZ_MOI_test_vcf_reel_v1.md` et Projet `claude/Test_2_VCF_reels_23oct2026.md`.
  - Lecteur : 16 gènes sur 17 identiques au corpus (écarts CYP2B6 et ABCG2, déjà documentés).
  - DL = règle CPIC/DPWG sur 54/54 et 65/65 médicaments prédits (fidélité aux règles, PAS une validation indépendante).
  - NA19085 : clopidogrel ✖ (CYP2C19 intermédiaire) ; API officielle CPIC (api.cpicpgx.org) : SCA/angioplastie « éviter la dose standard, prasugrel ou ticagrelor » (Strong) ; hors SCA : pas de recommandation ; neurovasculaire : « envisager une alternative » (Moderate).
  - Modèles utilisés : ceux de l'environnement de Claude (mêmes tailles que sur Drive, md5 non comparé) : à refaire chez Mouna.
- Mouna veut une validation INDÉPENDANTE de CPIC/DPWG (étude/recherche avec de vrais patients). Méthode en 3 niveaux proposée : (1) données observées patient par patient, (2) littérature primaire par couple gène-médicament (études lues avant citation), (3) PharmCAT + GeT-RM. Validation explicite de Mouna : non encore donnée.
- Jeux de données vus sur https://www.clinpgx.org/downloads (capture de Mouna) : ITPC (tamoxifène/CYP2D6), ISPC (865 patients, antidépresseurs ; page https://purl.stanford.edu/bg091gk8548, génotypes non confirmés, restrictions possibles). IWPC (warfarine) : NON visible sur la capture ; existence sourcée par la doc R https://search.r-project.org/CRAN/refmans/simsl/html/warfarin.html seulement.
- Couverture du DL vérifiée (data/domaine_v8.json) : warfarine = CYP2C9 0,0 et 0,5 seulement, toujours ADAPTER_DOSE (ne regarde pas VKORC1) ; citalopram et escitalopram = CYP2C19 0,5 et 1,0 seulement, toujours STANDARD ; tamoxifène = CYP2D6 0,0 et 0,5 EVITER, 1,0 et 2,0 STANDARD. Seul le tamoxifène permet un vrai test (le DL peut se tromper).

## 2. Erreurs à ne plus reproduire
- NOUVEAU : avoir proposé un test (IWPC/warfarine) sans avoir vérifié avant ce que le DL a appris pour ce médicament (Mouna l'a relevé à 9 h 27). RÈGLE : avant toute proposition de validation, lire `domaine_v8.json` pour les médicaments concernés (gènes, combinaisons vues, classes vues) et écrire si le test peut discriminer.
- Ne jamais oublier le cœur du sujet dans un plan.
- Ne jamais tirer ni comparer des profils du jeu final (138) hors évaluation finale ; exclure `data/profils_ensemble_final_v1.txt`.
- Ne pas déposer dans l'ancien dossier `scripts` de Drive (avril).
- Ne citer aucune source non lue. Non lues : PMC6977333, PMC9705957, page méthodes PharmCAT, rapport d'exemple PharmCAT, annotation ClinPGx clopidogrel. PubMed/PMC bloquent (anti-robot) ; ClinPGx demande JavaScript ; mon environnement n'atteint pas clinpgx.org (non contourné). L'API CPIC a été lue via un outil de lecture qui résume : reconfirmer sur le JSON brut.
- Messages courts, simples, une seule action ; ne pas annoncer sans exécuter ; ne jamais écrire « Claude a vérifié ».

## 3. Problèmes trouvés dans l'application / le DL (à traiter)
1. Combinaisons jamais vues : NA19472 perd 15 médicaments (méloxicam, piroxicam, ténoxicam, fluvastatine, citalopram, escitalopram, dapsone, primaquine...). Cause probable : les 59 règles ambiguës écartées du corpus (à confirmer règle par règle). Elles expliquent aussi pourquoi warfarine et citalopram ne permettent pas de test.
2. Rouge trop sévère : CYP2C19 « rapide » -> tricycliques et voriconazole affichés ✖ « à éviter » ; CPIC (API) = « envisager une alternative » (Optional/Moderate), voriconazole a 2 lignes publiées (alternative OU dose standard + suivi). Nuancer l'écran.
3. Ibuprofène en vert dans « autres préparations cardiaques » (ATC) : trompeur.
4. Pas d'alternative proposée pour clopidogrel (prasugrel/ticagrelor hors modèle) ; l'indication n'est pas demandée.

## 4. Plan exact de ce qui reste
1. Mouna : télécharger `pharmageno_test_vcf_reel_v1.zip`, puis sauvegarde WSL -> Windows -> GitHub -> Drive (commandes à donner une par une).
2. Refaire le test des 2 VCF avec les modèles de Mouna (commande `lancer_test_vcf_reel_v1.py` ou envoi du VCF dans l'application) ; comparer avec PharmCAT.
3. Validation indépendante : tamoxifène/CYP2D6 (ITPC) : trouver l'accès aux données ; sinon résultats publiés lus ; vérifier avant d'affirmer ce que le DL dit pour chaque génotype. Si les 59 règles ambiguës sont remises dans le corpus et le DL réentraîné, warfarine et citalopram deviennent testables.
4. Décision sur les 59 règles ambiguës (corpus, réentraînement, nouveau test des combinaisons).
5. Corrections de l'application (points 2 et 3 de la section 3 ; message « aucun gène lisible » ; accord des verbes ; noms français des groupes ; anomalie atorvastatine/SLCO1B1).
6. Protocole d'évaluation finale gelé ; figures et statistiques (à partir des fichiers de résultats uniquement) ; évaluation finale unique sur 138 profils / 12 524 lignes.
7. Mémoire chapitres 3 à 8 ; Plan Excel ; mail à l'encadrant (brouillon non envoyé) ; date de dépôt (~12 nov., non confirmée) ; encadrant disponible dès le 15 nov. ; soutenance décembre 2026.
8. Ménage : 2 copies Drive mal placées ; fichier parasite racine GitHub ; fichiers `??` ; commit 494a50e « Unverified » ; uploads Drive en attente.
