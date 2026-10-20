# Journal de Bord du Projet PharmaGeno - 20 octobre 2026, après-midi (suite du journal de midi)

## 0. Règles absolues (inchangées)
- Le DL est le CŒUR du sujet et de l'application : ne jamais le reléguer ; un résultat limitant est un problème à résoudre avec le DL au centre, écrit honnêtement dans le mémoire.
- Nouvelles versions à côté des anciennes ; une seule action demandée à Mouna par message ; ne jamais annoncer une suite sans l'exécuter dans le même tour.
- Réponses courtes, en français simple, sans mots compliqués.
- Chaîne de sauvegarde : WSL (~/projet_memoire) -> Windows (C:\Users\MSI\Desktop\memoire\) -> GitHub (benaichamouna-byte/PharmaGeno) -> Google Drive (dépôt à la main par Mouna ; accès lecture seule pour Claude).

## 1. Décisions validées
- Tout le Drive sert à l'encadrant pour vérifier le travail : fichiers LISIBLES (pas seulement des zips), rangés PAR TYPE (data, docs, journal de bord, results, scripts). Pas de dossier « pour l'encadrant », pas de dossiers datés pour naviguer.
- Mouna nomme elle-même le dossier de destination : `Model_v8_7_9_10` (sans espaces ni parenthèses). Un seul téléchargement à la fois ; peu de fichiers à manipuler.
- Contenu du dossier (lot du 20 oct.) : 198 fichiers = data 13, docs 8, journal de bord 4, scripts 36, results 137.
- Application web v8 : construite par Claude sur délégation de Mouna (« fais comme tu veux »), à côté de la v7 (v7 intacte). Position du DL : moteur de la recommandation ; règle CPIC affichée à côté avec alerte de désaccord ; XGBoost second avis ; « non évalué » pour médicament inconnu ou gène non déterminé.

## 2. État des 4 supports (vérifié 20 oct., ~15h) : lot de 198 fichiers
- Drive, Windows, WSL : `Model_v8_7_9_10`, 198 fichiers. GitHub : commit e4e521e, 198 fichiers suivis.
- NOUVEAU (fin d'après-midi) : fichiers de l'application v8 prêts dans un lot « delta » ; PAS ENCORE sur les 4 supports.
- Ouvert : fichier parasite à la racine GitHub `rf, columns, classes = load_rf_model()` (proposer un renommage, ne pas supprimer sans décision) ; memoire/*.py (v6/v7) non suivis ; commit 494a50e affiché « Unverified » (ses commits ; pas de réécriture d'historique).

## 3. Application v8 : ce qui est fait (20 oct.)
- Fichiers : scripts/app_pharmageno_v8.py, rapport_pdf_v8.py, templates_v8/ (6 pages), test_app_v8.py ; results/test_app_v8_sortie.txt, test_vcf_reel_app_v8.txt ; docs/LISEZ_MOI_application_v8.md.
- 22 tests automatiques (23 contrôles) : TOUT PASSE.
- Test réel avec un VCF (HG00101, formulaire web, PyPGx 0.27.0) : 20 gènes comparés au profil d'entraînement, 19 identiques ; la seule différence est HLA-B*57:01, saisi « non porteur » à la main pour le test (le corpus indique porteur). CYP2D6 non déterminé (attendu). Résultat Cardiologie : 1 à éviter (simvastatine, SLCO1B1 fonction diminuée), 64 compatibles, 48 non évalués.
- Pages vérifiées visuellement : accueil, résultats, panneau « Pourquoi ? », page patient, page Méthode, PDF (3 pages).
- Corrections faites pendant le test : phrase du résumé sans accord grammatical fragile ; PDF sans grand blanc en page 1 ; libellé « les guidelines ne concordent pas entre elles pour ce cas » (avant : « autres sources en désaccord », ambigu).
- Limite : test sur données 1000 Genomes propres, pas sur patient réel ni VCF clinique épars.

## 4. Erreurs à ne plus reproduire
- Nom de dossier livré proche d'un nom déjà utilisé par Mouna (a_deposer_drive).
- Livrer seulement des zips ou un dossier daté/« pour l'encadrant ».
- Dépôt Drive avec le dossier enveloppe : double imbrication (Drive ET Windows). Demander de déposer le CONTENU, ou aplatir avant.
- Plusieurs téléchargements / zips inutiles.
- Déclarer « sauvegardé » sans comptage récursif sur chaque support.
- Réponses compliquées avec un résultat médiocre : rester bref, simple, vérifier avant d'annoncer.
- Lancer pkill -f dans la même commande que le motif cherché (tue la commande elle-même) : utiliser ps + kill par PID.

## 5. Plan restant
1. Mettre le lot « delta » application v8 sur les 4 supports (Drive -> WSL -> Windows -> GitHub), comptage récursif de chaque support.
2. Comparaison avec une prédiction réelle d'une étude publiée (à choisir).
3. Décision de Mouna : rôle propre du DL (A variants / B abstention + robustesse / piste 1 ClinPGx).
4. Hyperparamètres sur validation seulement (même budget XGBoost/RF, plusieurs graines) ; évaluation finale UNE SEULE FOIS sur l'ensemble final (12 524 lignes, 138 familles, jamais lu).
5. Chapitres 3 à 8 ; mise à jour du Plan Excel ; liste des limites.
6. Ouvert : date du dépôt (~12 nov.) vs encadrant (15 nov.) ; envois Drive en attente (Tableau_de_bord_PharmaGeno_15oct2026.pdf, pharmageno_app_v7b.zip) ; NAT2/CYP2A6 vs GeT-RM ; HLA vs GeT-RM ; DPYD/ABCG2 PyPGx ; nettoyage Windows (zips inutiles, après listing).
