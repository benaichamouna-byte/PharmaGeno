# Protocole — comparaison équitable DL / XGBoost / forêt aléatoire sur le corpus v14

Rédigé le 4 novembre 2026, AVANT toute exécution des nouveaux bras (recherche d'hyperparamètres des arbres, réévaluation du DL, calibration des arbres). Statut : en attente de validation de Mouna. Une fois validé, ce texte est figé et haché ; toute modification ultérieure sera datée et justifiée à part (jamais écrasée).

## 1. Question et pourquoi les comparaisons précédentes ne suffisent pas
Question : à protocole égal (mêmes données, mêmes plis, même effort de réglage, même calibration, même critère d'arrêt), le DL (MLP de profil) fait-il aussi bien, mieux ou moins bien que XGBoost et la forêt aléatoire (RF) pour reproduire l'étiquette du moteur de règles ?

Les comparaisons v8 (25 oct.) et v12 (29 oct.) partageaient les données, les plis et les métriques, mais avaient cinq asymétries (déjà notées dans le chapitre 6 / Annexe A) : (1) DL moyenné sur 5 graines, arbres sur 1 exécution ; (2) DL réglé ensuite (40 configurations), arbres jamais réglés ; (3) critère d'arrêt différent (F1 macro pour le DL, log-loss pour XGBoost, aucun pour RF) ; (4) seul le DL calibré ; (5) le réglage du DL (config 35) a été choisi sur le corpus v13 ; les familles de test de chaque pli v14 ont très probablement servi, dans la v13, d'entraînement ou de validation interne à d'autres plis (biais de sélection probablement faible vu l'écart de la config 35 sur la suivante, 0,9987 contre 0,9977 de F1 de validation, mais non nul en principe).
Le présent protocole supprime ces cinq asymétries en refaisant aussi la recherche du DL sur la v14.

## 2. Ce que j'ai déjà vu (transparence, avant ce protocole)
- v13, XGBoost non réglé, 1 exécution par pli, 1 000 arbres atteints à chaque pli (plafond, donc non convergé) : F1 macro 0,9994 ± 0,0003, ECE 0,0178 non calibré. DL v13 (config 35 + calibration) : F1 macro 0,9980 ± 0,0010. Ces chiffres viennent de protocoles non équitables ; ils ne sont pas des résultats de ce protocole.
- DL v14 figé (config 35 + calibration, 25 entraînements) : F1 macro 0,9979 ± 0,0012 ; EVITER manqués 60,2 / 7 227 ; faux EVITER 8,4 ; erreurs 113,0 / 209 415 ; ECE 0,0003.
- Attente déclarée a priori : XGBoost est au moins aussi bon que le DL en F1 macro. Cette attente ne guide aucun choix de ce protocole ; elle est notée pour que son éventuelle confirmation ne soit pas présentée comme une surprise.
- Aucun résultat des nouveaux bras n'a été lu. Les essais de fonctionnement (« smoke », 1/20 des lignes) n'ont servi qu'à vérifier que le code tourne et à chronométrer ; leurs métriques n'ont pas été examinées.

## 3. Données et découpage (identiques pour les trois bras)
- Corpus v14 gelé, SHA-256 `b876bb469e562d6e…` (fiche GEL du 2 nov.) : 189 médicaments, 232 664 lignes, 1 379 profils. Étiquette = sortie du moteur de règles (CPIC / DPWG / RNPGx / FDA) : on mesure l'accord avec les règles, pas l'exactitude clinique.
- Ensemble final : 138 familles (23 249 lignes), NON lu par aucune étape (vérifié par assertions de `protocole_commun_v10.py`). Développement : 1 241 profils, 209 415 lignes.
- Plis externes : `protocole_commun_v10.decouper` (StratifiedGroupKFold, 5 plis, graine 42, groupe = family_id).
- Validation interne : mêmes familles pour les trois bras. Découpage fait sur les profils de l'entraînement du pli (GroupShuffleSplit par famille) puis reporté sur les lignes : 15 % (graine 49) pendant la recherche, 10 % (graine 42) pendant l'entraînement final. Pour le DL ce sont exactement les appels de `recherche_hp_dl_v4.py` et `evaluer_dl_imbrique_v5.py` ; pour les arbres, `arbres_coeur_v1.decoupe_interne` reproduit le même découpage.

## 4. Modèles et entrées
- DL : MLP de profil (`dl_coeur_v4.py`) ; 34 entrées (20 variables génétiques + 14 indicatrices de valeur manquante), 189 × 4 sorties.
- XGBoost et RF : mêmes 34 variables + 189 colonnes indicatrices du médicament ; une ligne = un couple profil × médicament.
- Différence de nature, assumée et documentée : le DL est multi-tâche (couches partagées, tous les médicaments d'un profil d'un coup) ; les arbres sont un modèle unique à identifiant de médicament. Une autre représentation (un modèle par médicament, médicament en variable catégorielle) n'est pas testée ici : c'est une limite, pas un choix de confort.

## 5. Réglage (même budget, même critère, même imbrication)
- Recherche aléatoire (Bergstra & Bengio 2012, JMLR 13:281-305, https://jmlr.org/papers/v13/bergstra12a.html), 40 configurations par modèle, configuration 0 = réglage de référence, graine de tirage 0, pour chacun des 5 plis externes ; le pli de test n'est jamais lu. Critère : F1 macro de la validation interne ; la configuration retenue pour un pli est celle de meilleur F1 macro de ce pli (égalité : plus petit indice).
- DL (inchangé, refait sur v14) : espace de `recherche_hp_dl_v4.py` (couches, largeur, dropout, BatchNorm, activation, pas d'apprentissage, décroissance des poids, taille de lot, exposant des poids, facteur EVITER, lissage), 40 configurations, tour 1 seul. Le tour 2 (recherche locale, interrompu) n'est pas utilisé. La config 35 figée de l'application reste un bras de référence supplémentaire.
- XGBoost : max_depth {4, 6, 8, 10, 12} ; eta {0,03 ; 0,1 ; 0,3} ; min_child_weight {1, 3, 10} ; subsample {0,6 ; 0,8 ; 1,0} ; colsample_bytree {0,5 ; 0,8 ; 1,0} ; reg_lambda {0, 1, 10} ; w_exp {0,5 ; 0,75 ; 1,0} ; ev_x {1, 2, 4}. Référence (config 0) : profondeur 6, eta 0,1, poids ~ 1/fréquence (réglage de `train_arbres_v10.py`). Plafond 2 000 arbres.
- RF : max_features {sqrt, log2, 0,1, 0,3, 0,5} ; min_samples_leaf {1, 2, 5, 10} ; max_depth {illimitée, 16, 32} ; criterion {gini, entropy} ; max_samples {tout, 0,5, 0,8} ; w_exp et ev_x comme ci-dessus. 500 arbres fixes (Probst & Boulesteix 2018, JMLR 18, https://jmlr.org/papers/v18/17-269.html : plus d'arbres n'aggrave pas la performance en moyenne). Les hyperparamètres que recense l'article de synthèse de Probst, Wright & Boulesteix (arXiv 1804.03515, DOI 10.1002/widm.1301 ; revue, volume et pages à vérifier avant citation dans le mémoire) — taille d'échantillon, nombre de variables par coupure, règle de coupure, taille minimale de nœud, nombre d'arbres — sont dans l'espace ou fixés, sauf le tirage avec/sans remise (non testé).
- Les espaces ont été fixés par moi avant tout résultat, à partir de la documentation de XGBoost et de la littérature citée ; ils ne sont pas strictement identiques à celui du DL (paramètres différents par nature) mais le budget (40 configurations × 5 plis) et le critère sont identiques.
- Poids de classes : formule du DL (`(N / (K·n_classe))^w_exp`, EVITER × ev_x) appliquée aux lignes d'entraînement, pour les trois bras.

## 6. Entraînement final et calibration
- Pour chaque pli : configuration choisie ci-dessus, entraînée sur 90 % des familles d'entraînement, 5 graines (graine = 42 + 100·s + k, comme le DL). Critère d'arrêt/sélection : F1 macro de la validation interne ; XGBoost évalue ce F1 tous les 25 arbres (patience 6 contrôles = 150 arbres, gain minimal 1e-4, comme le DL : patience 25 époques, 1e-4) et garde le meilleur nombre d'arbres. RF : aucun arrêt.
- Calibration : mise à l'échelle de la température sur la validation interne, même fonction pour les trois bras ; les probabilités brutes des arbres sont aussi conservées (ECE et log-loss bruts rapportés).
- Remarque honnête : une configuration XGBoost sans sous-échantillonnage (subsample = colsample = 1) est déterministe ; ses 5 « graines » donnent alors le même modèle. La dispersion entre graines des arbres peut donc être nulle ou faible sans que cela mesure une stabilité réelle. Ce point sera rapporté tel quel.
- Bras supplémentaires, hors règle de décision : (a) arbres en configuration de référence (non réglés) ; (b) DL config 35 figé (modèle de l'application).

## 7. Mesures, statistique et règle de décision (fixées maintenant)
- Mesures, sur l'ensemble des 209 415 lignes hors-pli : F1 macro (primaire) ; EVITER manqués, faux EVITER, erreurs totales, précision EVITER ; log-loss et ECE ; F1 macro par niveau de source ; erreurs par médicament et recouvrement des erreurs entre modèles.
- Statistique principale : moyenne sur les 5 graines de la mesure calculée sur l'ensemble des prédictions hors-pli (modèle unique, aucun bonus d'ensemble). Statistique secondaire : moyenne des probabilités des 5 graines.
- Incertitude : bootstrap par famille (Field & Welsh 2007, J. R. Stat. Soc. B 69:369-390), 2 000 tirages, graine 42, mêmes familles tirées pour tous les modèles ; différences appariées avec leur propre intervalle à 95 %. Limite connue : 1 379 profils = 1 379 identifiants de famille ; la parenté réelle des génomes 1000 Genomes n'est pas prise en compte, on ne dira pas « familles indépendantes ».
- Règle de décision sur la différence de F1 macro A − B (IC 95 % [lo ; hi]), avec une marge d'équivalence pratique δ = 0,001 (convention de ma part : de l'ordre de l'écart-type entre plis du DL, 0,0012 ; ce n'est pas un standard publié) : A supérieur si lo > 0 ; B supérieur si hi < 0 ; équivalents si lo > −δ et hi < +δ ; sinon non tranché. Trois comparaisons (DL−XGB, DL−RF, XGB−RF), sans correction pour comparaisons multiples (à signaler).
- EVITER manqués est rapporté comme critère de sécurité avec son intervalle, sans règle formelle (le nombre d'événements est faible : 7 227 lignes EVITER).

## 8. Usage des résultats (fixé à l'avance)
- Quel que soit le résultat, il est rapporté en entier dans le chapitre 6 et l'Annexe A, y compris si XGBoost ou la RF surpassent le DL. Aucun réglage ni changement de métrique après lecture des résultats ; toute analyse supplémentaire est étiquetée « exploratoire, décidée après ».
- Aucun modèle de l'application n'est remplacé automatiquement. Si un arbre est supérieur, la justification du DL dans le mémoire change (par exemple : calibration native, sorties multi-médicaments, extension prévue à de nouvelles entrées) et le choix du modèle de référence est discuté avec Pr. Ghedira.
- L'ensemble final de 138 familles n'est lu qu'une fois, après gel écrit du protocole d'évaluation finale et validation de Mouna ; pas dans cette comparaison.

## 9. Fichiers, exécution et traçabilité
Nouveaux scripts (empreintes SHA-256 enregistrées avant exécution) :
- `arbres_coeur_v1.py` 99389477c3ab63fe…
- `recherche_hp_arbres_v1.py` c67b5cbe94783c6f…
- `evaluer_arbres_imbrique_v1.py` 26e1fe5bce46fc65…
- `comparaison_equitable_v14_v1.py` c92a8d41e82bd56c…
- `lancer_comparaison_equitable_v14.sh` 6ea5d070a7d19e7a…
Scripts existants réutilisés sans modification : `dl_coeur_v4.py` 63658d26…, `protocole_commun_v10.py` e95f0903…, `evaluer_dl_imbrique_v5.py` 5b387919…, `recherche_hp_dl_v4.py` 73176f3d….
Vérification du script d'analyse : appliqué trois fois au DL figé, il retrouve les chiffres connus (F1 macro 0,99787 ; EVITER manqués 60,2 ; faux EVITER 8,4 ; erreurs 113,0) et des différences nulles.
Temps estimé (chronométrages sur un pli v14, 2 cœurs) : XGBoost 37 à 126 s par entraînement, RF 28 à 319 s ; au total environ 11 h à 2 cœurs pour les six étapes (recherche DL ~35 min, recherche XGBoost ~4 h, recherche RF ~5-6 h, évaluations ~1,5 h), proportionnellement moins avec plus de cœurs. Estimation, non garantie. Tout est reprenable après interruption.
Commande : `bash lancer_comparaison_equitable_v14.sh <nproc>` depuis le dossier `scripts/` dans WSL.
Sauvegarde après exécution : WSL → Windows (`C:\Users\MSI\Desktop\memoire\`) → GitHub (fichier par fichier, pas de données IWPC) → Google Drive (`PharmaGeno_Memoire/`).
