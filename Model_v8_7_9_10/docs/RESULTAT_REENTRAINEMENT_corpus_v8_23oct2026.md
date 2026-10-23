# Réentraînement sur le corpus v8 (23 octobre 2026) : 16 médicaments ajoutés

Rappel du sujet : PharmaGeno RECOMMANDE des médicaments à partir du VCF du patient ; le DL lit tout le profil et combine les gènes ; la page donne une réponse claire en haut.

## Ce qui a été fait (ordre)
1. Règles v8 = règles v7 + 67 lignes du groupe A, validées par Mouna le 23 oct. à 12 h 01 (`scripts/construire_regles_v8_v1.py` -> `data/regles_v8_monogene.csv`).
2. Corpus v8 (`scripts/construire_corpus_v8.py`, même moteur d'étiquetage que v3/v7, non modifié) : 152 600 lignes, 133 médicaments, 1 379 profils. CONTRÔLE : les 130 578 lignes des 117 anciens médicaments sont identiques au corpus v7 (mêmes lignes, mêmes valeurs, mêmes étiquettes). Nouvelles lignes : 22 022 (16 x 1 379, moins 42 profils CYP3A4 manquants pour paclitaxel).
3. Protocole `protocole_commun_v9.py` (v8 reste intact) : seule différence = l'ENSEMBLE FINAL est FIXÉ aux 138 familles de `data/profils_ensemble_final_v1.txt` (vérifié : l'ancien découpage sur le corpus v7 redonne exactement ces 138 profils). Sans cela, ajouter des médicaments aurait changé le tirage du jeu final. Il compte maintenant 14 731 lignes (138 profils x médicaments) au lieu de 12 524. NON LU.
4. Entraînement (réglages inchangés, fixés à l'avance) : DL profil et DL choix en validation croisée 5 plis x 5 graines ; modèles finaux ; XGBoost (second avis) réentraîné ; domaine v9 (`construire_domaine_v8.py` inchangé, sortie `data/domaine_v9.json`).
5. App v8m (v8l reste intacte) : `app_pharmageno_v8m.py`, `moteur_v9f/g/i.py`, `templates_v8m`, chiffres affichés mis à jour depuis `results/dl_profil_v2/resume.json` et `results/dl_choix_v2/resume.json` ; les lignes de performance non refaites sont marquées « corpus v7, non refait ».

## Résultats mesurés (validation croisée, patients nouveaux ; ensemble final non lu)
| | corpus v7 (avant) | corpus v8 (maintenant) |
|---|---|---|
| Médicaments dans le corpus / dans le modèle | 117 / 113 | 133 / 129 |
| Médicaments où le DL décide selon le génotype | 58 | 61 (+ acénocoumarol, phenprocoumone, flucytosine) |
| DL profil : F1 macro | 0,9985 ± 0,0002 | 0,9981 ± 0,0002 |
| DL profil : cas « à éviter » manqués | 0,0015 ± 0,0002 | 0,0018 ± 0,0003 |
| DL profil : précision « à éviter » | 0,992 (réf. 19 oct.) | 0,995 |
| DL choix : ensemble exact (cas informatifs) | 99,55 % ± 0,06 | 99,75 % ± 0,04 |
| DL choix : référence sans profil | 6,9 % | 33,4 % |
| DL choix : choix « à éviter » | 0 cas | 0 cas |
| Classes de choix / médicaments dans ces classes | 30 / 75 | 33 / 88 |
| Part de cas (profil, classe) où la réponse dépend du profil | 6,7 % | 9,0 % |
Lecture : le DL profil perd 0,0004 de F1 macro (écart du même ordre que l'écart-type) ; la référence sans profil monte à 33,4 % parce que les nouvelles classes (ex. antiagrégants avec prasugrel et ticagrelor) ont plus souvent une même réponse pour tous. Pas de comparaison appariée faite : les deux colonnes ne portent pas sur les mêmes lignes.
Par médicament (OOF, 5 graines moyennées) : 13 médicaments « STANDARD partout » = 100 % ; acénocoumarol et phenprocoumone 99,60 % (5 erreurs sur 1 241 : STANDARD prédit ADAPTER_DOSE, aucun ADAPTER_DOSE manqué) ; flucytosine 99,92 % (1 erreur sur 1 241).

## Vérifications faites
- Tests de l'application v8m : 46 PASS sur 46 (`results/test_app_v8m_sortie.txt`). Un test (T22) vérifiait les anciens chiffres affichés ; il a été mis à jour avec les nouveaux chiffres mesurés.
- 23 anciennes interrogations du DL (profils construits) : actions identiques à la v1 (23/23). 
- Nouvelles interrogations (profils construits) : VKORC1 0,0 -> ADAPTER_DOSE, 0,5 et 1,0 -> STANDARD (acénocoumarol et phenprocoumone) ; DPYD 0,5 -> SURVEILLER, 1,0 -> STANDARD (flucytosine) ; les 13 autres -> STANDARD. Fichier : `results/comparaison_etudes_v1/dl_couples_etudes_v2.csv`.
- 2 vrais VCF (NA19085, NA19472) via la chaîne complète (PyPGx -> DL -> écran v8m), `results/test_vcf_reel_v2/` : NA19085 clopidogrel toujours ✖ (CYP2C19 intermédiaire) et prasugrel + ticagrelor maintenant visibles en vert dans le même groupe (alternatives) ; « 0 à vérifier » pour les deux profils (DL, XGBoost et règle d'accord sur tous les médicaments évalués).

## Limites et problèmes constatés (à ne pas cacher)
1. Flucytosine, DPYD = 0,0 : UN SEUL profil du corpus (1 sur 1 379). Le DL répond SURVEILLER (règle : EVITER) et XGBoost aussi. La couche de sécurité de l'application signale « à vérifier » (désaccord avec la règle) et affiche la règle, mais le DL ne sait pas apprendre ce cas.
2. Six médicaments dépendent de CYP2D6 seul ou en partie (amiodarone, disopyramide, quinidine, clonidine, flupenthixol, mirtazapine) : la règle dit STANDARD pour toutes les valeurs, mais CYP2D6 n'est pas lisible depuis un VCF, donc ces 6 médicaments restent « non évalués » dans l'application (+6 par rapport à avant : 48 -> 54 sur NA19085).
3. Antivitamines K : le corpus v7 NE les étiquetait volontairement PAS (« dose par algorithme pour tous »). Les règles v8 ajoutent l'ajustement DPWG pour acénocoumarol et phenprocoumone (VKORC1 TT -> 50 % de la dose initiale). La warfarine reste inchangée (règle CYP2C9 seule). À écrire dans le mémoire.
4. « Pas d'interaction gène-médicament » (DPWG) = « pas d'ajustement génétique recommandé », pas preuve d'innocuité ; les 13 médicaments STANDARD n'ajoutent aucune décision au DL.
5. Nom de groupe en anglais « vitamin k antagonists » dans l'écran (point déjà connu : noms français des groupes).
6. XGBoost du modèle final : 1 000 arbres (limite atteinte, l'arrêt anticipé n'a pas déclenché) ; réglages hérités de la v8, non modifiés.
7. Lignes de performance XGBoost, Random Forest, ancien DL et « médicament jamais vu » : mesurées sur le corpus v7, non refaites.
8. Toujours vrai : DL = règle est une fidélité aux règles, pas une validation indépendante ; aucun résultat clinique mesuré.

## Empreintes (md5)
modele_final_profil_v2.pt 2602bcb3b6e29ace2434325df954a423 | modele_final_choix_v2.pt 82ed7954437b321980886eb5cc0b208c | modele_final_v8_xgb_id.json (v9x) 5f4edbb72d57ff84bf2963b4277ce834 | phenotype_drug_dataset_v8.csv 7c8b97a01de86dbcd540b8bbb80d59ca | regles_v8_monogene.csv 5dce52f079c69a5d1408ed99a815ec68 | domaine_v9.json 0d1d1687aa9fbb48ec8f60dab1434d34
Les modèles sont ceux de l'environnement de Claude ; à comparer chez Mouna après copie.

## Fichiers nouveaux (rien d'ancien modifié)
scripts : construire_regles_v8_v1.py, construire_corpus_v8.py, protocole_commun_v9.py, train_dl_profil_v2.py, train_dl_choix_v2.py, modele_final_profil_v2.py, modele_final_choix_v2.py, modele_final_xgb_v2.py, lancer_entrainement_v10.sh, moteur_v9f.py, moteur_v9g.py, moteur_v9i.py, app_pharmageno_v8m.py, templates_v8m/, test_app_v8m.py, lancer_test_vcf_reel_v2.py, interroger_dl_couples_etudes_v2.py
données : data/regles_v8_monogene.csv, data/corpus_v8/, data/domaine_v9.json ; modèles : modeles_v9/, modeles_v9x/ ; résultats : results/dl_profil_v2/, results/dl_choix_v2/, results/*_v2_log.txt, results/test_app_v8m_sortie.txt, results/test_vcf_reel_v2/, results/comparaison_etudes_v1/dl_couples_etudes_v2.csv
