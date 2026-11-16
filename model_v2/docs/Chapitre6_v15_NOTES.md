# Chapitre 6 v15 (version avec évaluation finale) — notes

**Ce document ne fait pas partie du mémoire.** Il accompagne `Chapitre6_v15_MEMOIRE.md` (version du 15 nov., qui remplace la précédente).

## 1. Ce qui a changé
- **Nouvelle section 6.7 « Évaluation unique sur l'ensemble final »**, avec les tableaux 6.7 et 6.8. Elle est placée dans le chapitre 6 et non dans un chapitre à part, parce qu'elle mesure la même chose que les sections 6.1 à 6.5 (accord avec les règles), alors que les chapitres 7 et 8 portent sur des patients réels. Cela épargne aussi le budget de 15 à 30 pages des « Résultats et discussion ».
- Renumérotation : 6.7 (négatifs) → 6.8 ; 6.8 (synthèse) → 6.9. Tableaux : 6.2 (nouveau, F1 par source), 6.3 (abstention), 6.4 (choix), 6.5 (comparaison), 6.6 (8 couples), 6.7 et 6.8 (ensemble final). **Vérifie les renvois depuis les autres chapitres** : « tableau 6.3 », « section 6.7 », etc. Les chapitres 1, 4, 5, 8 et 9 citent probablement les anciens numéros.
- **Marqueurs levés (8)** : F1 sans SURVEILLER et rappels (tableau 6.1) ; erreurs par médicament ; F1 par source (tableau 6.2) ; seuil sur P(EVITER), transformé en limite déclarée ; ECE de Random Forest ; log-loss des 4 bras ; intervalles des comptes d'erreurs ; intervalles réseau − RF et XGB − RF ; contrôle des égalités à 5 décimales ; 8 couples refaits avec la v15.
- **Marqueur restant (1)** : diagramme de fiabilité (§ 6.2). Il demande les 25 fichiers `oof_c35_cal_pli*_graine*.npz` de `results/dl_imbrique_v15/`, qui sont sur ta machine et pas sur GitHub. Si tu veux la figure, envoie-les ; sinon la phrase devient une limite déclarée.

## 2. Corrections apportées au texte précédent
- « Random Forest … commet **six fois** plus d'erreurs que XGBoost » était faux : 655,6 / 82,0 = 8,0. Corrigé en « huit fois ».
- La phrase « la calibration est devenue un avantage du réseau » ne tenait plus une fois la log-loss rapportée : la log-loss est plus basse pour XGBoost. Le paragraphe dit maintenant que l'ECE et la log-loss ne s'accordent pas, et que les écarts ne sont pas interprétables.

## 3. Sources des chiffres (tous relus, aucun recopié de mémoire)
- Tableau 6.1, tableau 6.2 : moyennes et écarts-types des 25 lignes de `results/dl_imbrique_v15/resultats_c35_cal_part*.csv`. Les lignes par source viennent de `resume_comparaison_v2.json` (somme vérifiée = 211 177).
- Erreurs par médicament : `erreurs_par_medicament_ensemble_graines_v2.csv`, colonne du bras c35 (statistique « ensemble des graines », total 76, à ne pas confondre avec 103,2 qui est la moyenne des graines).
- Tableau 6.5 et intervalles : `mesures_avec_ic_v2.csv`, `differences_appariees_v2.csv`, `resume_comparaison_v2.json` (bloc calibration).
- Égalités : recalculées sur `dl_hp_v15/essais_part*.csv`, `hp_arbres_v15_xgb/` et `hp_arbres_v15_rf/` ; configurations effectivement retenues relues dans `eval_arbres_v15_*/resultats_choisie_cal_part0.csv`.
- § 6.7 : `results/evaluation_finale_138/resultats_evaluation_finale_138.json` et `predictions_138.csv` ; détail dans `Resultat_evaluation_finale_138_15nov2026.md`.

## 4. À vérifier avant dépôt
- **Efron et Tibshirani** : la citation a été retirée du § 6.7 (non vérifiable dans la source primaire ; une source secondaire attribue le minimum de 1 000 tirages à l'article de 1986 dans *Statistical Science*, sans le lier aux intervalles percentiles). La justification des 10 000 tirages est désormais faite sans référence. Point clos.
- **Domaine de l'application** (à reporter au chapitre 5, pas au 6) : `domaine_v15.json` a été construit sur les 1 379 profils, ensemble final compris, alors que le script le décrit comme « corpus d'entraînement ». Mesuré : 1 combinaison sur 821 (fluvastatine, CYP2C9 = 0 et SLCO1B1 = 0,5 ; 1 ligne) n'a été vue que dans l'ensemble final. Sans effet sur l'évaluation du § 6.7, où le domaine n'intervient pas. Deux options : reconstruire le domaine sur les 1 241 profils de développement (correction propre, à refaire avant les captures d'écran) ou écrire la limite au chapitre 5. Ma recommandation : reconstruire, c'est une commande, puis relancer les 78 tests.
- **HG03684 et le contrôle de domaine** : le § 6.7 dit qu'un contrôle portant sur le profil complet n'a pas été mis en œuvre. Ne pas en ajouter un maintenant : il serait conçu au vu de l'ensemble final.

## 5. Ce qui se propage ailleurs
- **Chapitre 9 (RQ2)** : ajouter que l'ensemble final confirme le classement (XGBoost 0,9989 et 3 EVITER manqués ; réseau 0,9940 et 10 ; non tranché).
- **Résumé et abstract** : une phrase sur l'évaluation finale. Attention, ils sont déjà à 197 et 200 mots : il faudra en retirer autant que tu en ajoutes.
- **Chapitre 5** : limite du contrôle de domaine (cas HG03684) et point du domaine construit sur les 1 379 profils.
- **Section 3.8, point 3** : « seront retirés » → « ont été retirés » (temps du verbe).
- **Chapitre 4** : si le protocole de l'évaluation finale y est décrit au futur, passer au passé et renvoyer au § 6.7.

## 6. Longueur
Le chapitre gagne environ 1 500 mots (≈ 3,5 pages) : il fait maintenant environ 15 pages. Avec les chapitres 7, 8 et 9, le total « Résultats et discussion » dépassera 30 pages. Les coupes déjà proposées tiennent : § 6.8 (négatifs) en annexe A, en gardant trois phrases (≈ 1,5 page) ; § 6.6 réduit au tableau et à deux phrases (≈ 0,5 page).

## 7. Sauvegarde
WSL → Windows (`C:\Users\MSI\Desktop\memoire\`) → GitHub → Drive (`PharmaGeno_Memoire/`) :
`bash ~/sauver_v2.sh "chapitre 6 v15 avec évaluation finale 138" chapitre6_v15_final.zip`
