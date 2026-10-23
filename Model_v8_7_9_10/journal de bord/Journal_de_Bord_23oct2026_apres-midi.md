# Journal de Bord du Projet — 23 octobre 2026, après-midi (suite du journal du matin)

## 0. Le cœur du sujet (à rappeler à chaque livraison)
Webtool de RECOMMANDATION : VCF du patient + spécialité -> le DL lit tout le profil et combine les gènes -> la page recommande, réponse claire en haut (✔ / ▲ / ✖). Pas un test médicament par médicament.

## 1. Décisions validées
- Agrandissement de la liste (demande de Mouna) : groupe A lu (38 médicaments + 2 entrées de classe) ; 16 médicaments utilisables (3 règles par génotype : acénocoumarol, phenprocoumone, flucytosine ; 13 « pas d'interaction / aucune action » -> STANDARD) ; 22 sans recommandation utilisable (aucune étiquette inventée). « ok » de Mouna le 23 oct. à 12 h 01 sur les 67 lignes (`results/elargissement_liste_v1/regles_proposees_groupe_A_v1.csv`).
- Corpus v8 (133 médicaments) ; ensemble final FIXÉ aux 138 familles de `profils_ensemble_final_v1.txt` (`protocole_commun_v9.py`) ; réentraînement DL profil, DL choix, XGBoost ; app v8m. Détail et chiffres : `results/elargissement_liste_v1/RESULTAT_REENTRAINEMENT_corpus_v8_23oct2026.md`.
- Résultat : médicaments 117 -> 133 (modèle 113 -> 129) ; décision selon génotype 58 -> 61.

## 2. Erreurs à ne plus reproduire
- (hérité) Ne jamais oublier le cœur du sujet dans un plan ; ne jamais tirer ni lire les 138 profils finaux hors évaluation finale ; vérifier la couverture du DL (`domaine_v8.json`/`domaine_v9.json`) AVANT de proposer un test ; messages courts, une action ; ne pas annoncer sans exécuter ; ne jamais écrire « Claude a vérifié ».
- NOUVEAU : en ajoutant des médicaments, ne jamais laisser le découpage retirer au sort un nouveau jeu final ; le fixer par fichier et vérifier qu'il redonne les 138 profils.
- NOUVEAU : avant d'annoncer un ajout de règles, relire les choix déjà documentés dans les scripts (les antivitamines K étaient volontairement non étiquetées en v7) et le dire à Mouna dans le même message.
- NOUVEAU : annoncer clairement que « STANDARD partout » n'ajoute pas de décision au DL (le gain réel est +3, pas +16).

## 3. Problèmes constatés (à traiter)
1. Flucytosine DPYD 0,0 : 1 seul profil ; DL et XGBoost se trompent (SURVEILLER au lieu de EVITER) ; l'application signale « à vérifier » grâce à la règle. Décision possible : seuil de support minimal pour le domaine (affecte aussi 3 autres couples à 1 profil : amitriptyline, rosuvastatine, sertraline).
2. 6 médicaments CYP2D6 « non évalués » depuis un VCF.
3. Hérités : rouge trop sévère CYP2C19 rapide (tricycliques, voriconazole) ; ibuprofène en vert dans « autres préparations cardiaques » ; indication non demandée ; noms de groupes en anglais ; 15 médicaments sans prédiction (combinaisons jamais vues, 59 règles ambiguës) ; simvastatine/tamoxifène « éviter » plus fort que l'évidence ; accord des verbes ; message « aucun gène lisible » ; multi-gènes « non interprété » ; anomalie atorvastatine/SLCO1B1 ; anciens `test_moteur_v8*.py` tirent tout le corpus.

## 4. Plan exact de ce qui reste
1. Validation de Mouna du compte rendu de l'étape (chiffres, limites 1 à 3 ci-dessus).
2. Les 59 règles ambiguës (35 médicaments) : lecture règle par règle, décision, nouveau corpus v9, réentraînement (rend warfarine/citalopram testables et récupère les 15 médicaments).
3. Groupe B (27 médicaments, nouveaux gènes MT-RNR1, RYR1, CACNA1S, HLA-B, CYP1A2...) puis groupe C (24, données manquantes) ; médicaments à étiquette réglementaire FDA (226) et association 2B (23) non encore utilisés.
4. Validation indépendante (tamoxifène/CYP2D6 ITPC ; sources manquantes thiopurines, UGT1A1/irinotécan, IPP, tacrolimus, G6PD, tricycliques) ; refaire les tests (2 VCF, couples étude) avec les modèles de Mouna.
5. Corrections de l'application (liste section 3) ; alternatives clopidogrel : prasugrel et ticagrelor apparaissent désormais en vert (NA19085).
6. Protocole d'évaluation finale gelé ; figures et statistiques (fichiers de résultats seulement, IC bootstrap par famille) ; évaluation finale UNIQUE sur 138 profils / 14 731 lignes (nouveau nombre) ; mémoire chapitres 3 à 8 ; Plan Excel ; mail encadrant (brouillon non envoyé) ; dépôt ~12 nov. (non confirmé) ; encadrant dispo dès le 15 nov. ; soutenance décembre 2026.
7. UNE SEULE sauvegarde plus tard (demande de Mouna) : WSL -> Windows -> GitHub -> Drive, avec tous les fichiers du 23 oct. (liste en fin de RESULTAT_REENTRAINEMENT_corpus_v8_23oct2026.md + zips test_vcf_reel_v1, comparaison_etudes_v1 + journaux) ; ménage Drive/GitHub (copies mal placées, fichier parasite, commit 494a50e « Unverified », uploads en attente, doublon `pharmageno_v8j (1).zip`).
