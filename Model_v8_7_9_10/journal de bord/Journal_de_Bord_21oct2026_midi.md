# Journal de Bord du Projet PharmaGeno : 21 octobre 2026 (midi)

Couvre le 20 octobre soir et le 21 octobre jusqu'à 14 h. Un résultat n'est cité que s'il a été mesuré ; « validé » = validé par Mouna.

## 1. Décisions validées
- Écran de l'application : VCF + spécialité seulement ; 1 à 3 médicaments avec prédiction et explication ; HLA et CYP2D6 facultatifs, APRÈS les résultats (v8b).
- Tableau des 117 médicaments supprimé ; « non évalués » en une phrase avec détail repliable.
- Termes pour le clinicien, tirés de sources (CPIC termes finaux, guide britannique de pharmacogénomique, UF Health, ARUP) : « À dose standard », « Éviter », « Aucune recommandation (gène non déterminé ou profil trop rare) ». Gène affiché en phénotype seul (« CYP2D6 : métaboliseur lent »), le chiffre interne reste dans le détail de vérification. HLA : « positif / négatif » (choix B ; « ok » de Mouna interprété comme B), « non testé », « probable » supprimé (v8e).
- Rôle du DL : il doit combiner les gènes du profil pour prédire (image de Mouna : gènes = lettres, profil = mot, recommandation = sens). Le DL est le cœur et le premier sujet ; XGBoost et RF sont des comparaisons optionnelles (une ligne au plus).
- Test Direction B lancé et validé (« ok ») : retrait de combinaisons entières de gènes, DL seul.
- Mail à l'encadrant : version courte, sans chiffres ni termes techniques (rédigée, non envoyée).

## 2. Mesures (DL seul ; ensemble final de 12 524 lignes non lu)
- Importance des gènes par permutation (`importance_genes_dl_v1.py`) : sur 58 médicaments dépendants du génotype, 55 ont pour gènes les plus influents exactement ceux de la règle CPIC ; part médiane de l'influence sur les gènes CPIC : 96,5 %. Exceptions : allopurinol (HLA-B*58:01 : 1,9 %), carbamazépine (19 %), rosuvastatine (63 %). Avec HLA-B*58:01 positif : règle = Éviter, DL = Dose standard (P(EVITER) = 1,6 %).
- Médicaments indépendants du génotype (aspirine, ibuprofène, warfarine...) : influence totale quasi nulle (médiane 0,011) ; la « confiance 99,7 % » de l'aspirine n'apporte aucune information génétique.
- Combinaisons jamais vues dans la validation croisée (`combinaisons_jamais_vues_oof_v1.py`) : 1 ligne sur 112 654. La validation actuelle ne teste pas la combinaison de gènes.
- Retrait de combinaisons (`test_combinaisons_retirees_dl_v1.py`, 3 tirages) : variante B (classe encore vue) : 100 % sur les lignes informatives pour 5 tricycliques (CYP2C19 + CYP2D6) ; rosuvastatine et sertraline 92,5 % (référence majoritaire 100 %). Variante A : 0 % sur les thiopurines (NUDT15 + TPMT) car la seule combinaison « standard » est retirée. Combinaisons vues : 99,7 %. Variante A reproduite chez Mouna (0,319 contre 0,321, écarts d'environ 0,004).
- Étiquettes d'entraînement = règles CPIC : l'accord DL/CPIC n'est pas une validation indépendante. Données : 99 médicaments à 1 gène, 14 à 2 gènes, aucun à 3 gènes ou plus.
- Fichier réel `mother_annotated.vcf` : uniquement chr21 (216 857 variants), aucun gène de l'application lisible.

## 3. Erreurs à ne plus reproduire
- Prendre un « ok » ambigu pour un choix sans le dire ; reposer une question déjà tranchée (relire le Journal avant de poser une question sur le rôle du DL).
- Envoyer un script par carte de téléchargement : plusieurs échecs. Utiliser un zip, ou créer le fichier par `cat > ... <<'EOF'` dans le terminal de Mouna.
- Écrire un test qui passe toujours (`or True`) ; couper un test au mauvais endroit (regex sur HTML imbriqué).
- Présenter « le DL regarde les mêmes gènes que CPIC » comme une bonne nouvelle : c'est le problème de fond.
- Mentionner XGBoost ou RF comme sujet principal.
- Présenter des captures faites dans mon environnement comme preuve ; Mouna doit lancer et voir elle-même.
- Annoncer qu'une v8x est « corrigée » sans que Mouna l'ait vue à l'écran.
- J'ai modifié v8b en place (libellés) dans mon environnement après l'avoir livrée, avant de copier en v8c : la v8b de référence est celle du zip livré à Mouna (déjà chez elle) ; la copie de mon environnement ne fait pas foi et n'est pas incluse dans le lot de sauvegarde. Toujours créer une nouvelle version à côté, jamais modifier une version livrée.

## 4. Plan restant (chaque étape validée par Mouna)
1. Variante B chez Mouna (commande donnée) ; chaîne de sauvegarde WSL, Windows, GitHub, Drive pour tous les nouveaux fichiers.
2. v8f : explication contradictoire sur les règles à deux gènes (« non interprété »), libellé « version 8b » dans le bandeau, message explicite « aucun gène lisible » (fichier chr21), signalement/classement des médicaments indépendants du génotype (aspirine en tête).
3. Test de `HG00101.vcf` chez Mouna dans la v8e ; captures faites chez elle pour le mail à l'encadrant.
4. Explication fondée sur le DL dans l'application : en attente du choix (mesure globale par médicament déjà faite, ou calcul par patient).
5. Comparaison avec deux références publiées : PharmCAT (fichier `~/pharmcat_test/out/HG00101.report.json`) et une étude publiée (concordances PharmCAT/GeT-RM, 59 échantillons).
6. Contenu clinique plus riche (alternatives, doses sourcées) ; défaut du DL sur HLA-B*58:01 (allopurinol) à traiter ou à documenter.
7. Réglage léger des hyperparamètres sur validation seule ; évaluation finale unique sur l'ensemble de 12 524 lignes ; chapitres 3 à 8 ; plan Excel ; date de dépôt (~12 nov., non confirmée) face à la disponibilité de l'encadrant (15 nov.).
8. Ouverts : fichier parasite à la racine GitHub (`rf, columns, classes = load_rf_model()`, proposition de renommage, ne pas supprimer) ; envois Drive en attente (Tableau_de_bord_PharmaGeno_15oct2026.pdf, pharmageno_app_v7b.zip) ; nettoyage des zips Windows après liste.
