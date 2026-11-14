# Journal de Bord du Projet — 14 novembre 2026

Document de transfert. À coller en tête d'une nouvelle conversation avec la phrase : « Voici l'état actuel de notre projet et les règles strictes à respecter. Prends-en note et poursuis le travail. »

**Dépôt : 25 novembre 2026. Encadrant disponible depuis le 15 novembre.**

---

## 1. Décisions prises et validées

### Corpus et données
- Le corpus **v15** est gelé. Empreintes SHA-256 vérifiées trois fois, depuis trois sources indépendantes : corpus `68b564ce265728b6`, règles mono-gène `9d5512543016cb89`, règles multi-gènes `1cb99ff632466696`.
- 234 632 lignes, 1 379 profils, 189 médicaments. Classes : STANDARD 201 273, ADAPTER_DOSE 20 272, EVITER 8 031, SURVEILLER 5 056. Zéro doublon, statut d'étiquette « ok » partout.
- Découpage **recalculé** (pas recopié d'un log) : développement 1 241 profils / 211 177 lignes (dont 7 215 EVITER) ; ensemble final 138 profils / 23 455 lignes, **jamais lu**.
- 709 règles à un gène (CPIC 363, DPWG 145, FDA 95, FDA-étiquette 84, HCSC 8, RNPGx 8, EMA 6) et 124 règles à plusieurs gènes sur 6 paires et 9 médicaments. 18 règles « conditionnel », 2 « ambigu ».
- Trois corrections de règles en v15 : règle VKORC1 de la warfarine, actions DPWG des diplotypes CYP2C9, grille TPMT × NUDT15 des thiopurines. 433 lignes modifiées, 1 968 ajoutées, aucune supprimée.

### Résultats mesurés (corpus v15)
- **Réseau déployé (configuration 35)** : F1 macro 0,99820 ± 0,00075 ; exactitude 0,99951 ; rappel EVITER 0,99342 ; log-loss 0,00260 ; ECE 0,00029 ; 81,4 époques ; T moyenne 0,198. 103,2 erreurs, 47,4 EVITER manqués sur 7 215 (0,66 %), 8,8 faux EVITER.
- **Comparaison à protocole identique** : DL imbriqué 0,997943 ; XGBoost 0,998288 ; Random Forest 0,992687 ; DL c35 0,998197.
- **DL − XGBoost = −0,000345 [−0,00106 ; +0,00034] → NON TRANCHÉ.** XGBoost − DL c35 = +0,000091 [−0,00052 ; +0,00076] → **ÉQUIVALENTS**. DL − RF = +0,00526 → DL supérieur.
- **Sécurité : le réseau manque 38,0 EVITER de plus que XGBoost, IC [23,2 ; 54,4] excluant zéro.** XGBoost reste meilleur sur ce critère.
- **Recouvrement des erreurs** (statistique d'ensemble) : DL 94, XGBoost 80, RF 650, **9 communes seulement**. Résultat neuf : les deux modèles échouent sur des situations presque disjointes, ce qui fonde après coup le second avis de l'application.
- **Couverture-risque** : AUROC 0,8696 ; 77,0 % des erreurs dans le premier centile. Nouveaux quantiles : 0,9934 / **0,9981** / 0,9994 / 0,9998. Résultat défavorable conservé : les EVITER manqués résistent deux fois plus à l'abstention que les autres erreurs.
- **Cas EMA-étiquette** élucidé : 2 440 lignes, 2 médicaments, une seule ligne ADAPTER_DOSE (lonafarnib / CYP3A4 = 0), portée par le seul profil sur 1 379 ayant cette valeur. Le F1 ≈ 2/3 est un artefact de taille d'échantillon, pas une performance.

### Rédaction
- **Règles de rédaction 1 à 8** en vigueur (document `Regles_redaction_memoire_11nov2026.md`), la règle 8 (formulaire ISBST) primant sur toutes.
- **Deux fichiers par livraison** : `*_MEMOIRE.md` (texte du mémoire seul) et `*_NOTES.md`.
- Chapitres livrés en v15 : **1, 2, 3, 6, 9, annexe A, front matter**. Résumé et abstract ramenés à **197 et 200 mots**, 5 mots clés chacun, conformes au formulaire.
- **Chaîne de fabrication validée chez Mouna** : `fabriquer_memoire.py` + `reference_memoire.docx` (copie zéro v6, 13 styles) sous pandoc 2.9.2.1, LibreOffice 7.3.7.2, python-docx 1.2.0. Produit le .docx et le PDF, marqueurs surlignés en jaune. Dossier `~/projet_memoire/fabrication`.
- Figures 6.1 et 6.2 produites par `figures_chapitre6_v15.py`, qui ne calcule rien : toutes les valeurs y sont recopiées des sorties mesurées.

---

## 2. Erreurs spécifiques à ne plus jamais reproduire

1. **Ne pas réutiliser une estimation d'avant exécution quand le log de l'exécution précédente existe.** (Durée de la recherche RF annoncée à 5-6 h d'après le protocole alors que le log v14 disait 13 h 59.)
2. **Ne pas lire un cumul comme une durée unitaire.** (« 402 s » pris pour le temps d'un entraînement, d'où une prévision de 14 h 30 au lieu de 21 min 30 par entraînement.)
3. **Vérifier un commit avec `git log --oneline -1`.** « nothing added to commit » et « Everything up-to-date » signifient que le bloc a été lancé deux fois, pas que la sauvegarde a échoué.
4. **Supprimer l'ancien fichier dans les téléchargements avant d'en re-télécharger un de même nom.** Windows crée `nom (1).md` et `sauver.sh` peut sauvegarder la version périmée en silence. C'est arrivé le 14 novembre avec `Chapitre3_v15_MEMOIRE.md`.
5. **Ne jamais laisser dans un chapitre un renvoi vers une mesure qui n'a pas été recalculée dans la version courante.** (Chapitre 9, RQ1, renvoyait à une ventilation des erreurs par médicament qui n'existe plus en v15.)
6. **Ne pas transporter une conclusion d'une version du corpus à la suivante.** Chaque énoncé porte la version sur laquelle il est établi.
7. **Ne pas surévaluer une contribution.** (Guo 2017 et Geifman 2017 annoncés comme « manquants » alors qu'ils étaient déjà cités ; seules leurs métadonnées étaient incomplètes.)
8. **Ne jamais coller un bloc multi-lignes dans le terminal** : les sauts de ligne sont avalés. Découper en collages courts.
9. **Un essai complet à échelle réduite avant tout calcul long.** Jamais de lancement après l'échec d'un script de vérification.
10. **Zéro date d'étape de travail dans le mémoire** (règle 6). Seules restent les dates porteuses d'information : versions d'outils et de directives, dates de consultation des sources.
11. **Ne pas transformer une mesure non concluante en argument.** L'inversion de l'ECE entre v14 et v15 n'est pas exploitée : trois valeurs sous 0,0004 sans intervalle de confiance ne décident rien.

---

## 3. Plan exact de ce qu'il reste à faire

### Bloquant — deux décisions de Mouna
- **D1. Seuil d'abstention de l'application : 0,9965 (hérité v14) ou 0,9981 (quantile à 1 % mesuré sur la v15) ?** Recommandation : 0,9981, par cohérence avec la méthode du chapitre 4. Coût : configuration de l'application, tests T1–T68, sections 4.5 et 5.4, tableau 4.1, et la comparaison des 104 personnes si elle est refaite après. Repli honnête : garder 0,9965 **en écrivant pourquoi** et en déclarant qu'il n'écarte plus que 0,56 % des prédictions.
- **D2. Réseau de choix : réentraîner sur la v15, ou déclarer la limite ?** Recommandation : réentraîner (réseau petit, ordre de grandeur l'heure). Vérifier d'abord si `train_dl_choix_v3.py` accepte un chemin de corpus ; sinon créer une copie `v4` paramétrée, la v3 restant intacte, avec vérification d'empreinte.

### Ensuite, dans cet ordre
1. **Section 4.5 et tableau 4.1** : reporter les quatre quantiles v15, une fois D1 tranchée.
2. **Régénérer l'application sur les modèles v15**, rejouer les tests T1–T68.
3. **Refaire la comparaison des 104 personnes contre PharmCAT** sur l'application v15, puis **réécrire les chapitres 7 et 8** (sections 7.2 et 7.6 : VKORC1 n'est plus une omission ; section 8.3 : trois défauts de règles corrigés).
4. **Captures d'écran** de l'application v15 et mise à jour de la section 5.11.
5. **Point de contrôle**, puis **gel écrit du protocole d'évaluation finale**.
6. **Évaluation finale sur les 138 profils — lecture unique et irréversible.** Rien d'autre ce jour-là. Retirer d'abord de l'entraînement les 34 profils de développement reliés par le pedigree à un profil final.
7. **Écrire les résultats finaux** et les limites.
8. **Mise en conformité ISBST** : créer une section « Objectifs » distincte, ramener l'introduction à 1-2 pages, arbitrer « Matériel et méthodes » (chapitres 3, 4 et 5 dépassent largement les 5 à 10 pages attendues), vérifier le corps à 36-60 pages et « Résultats et discussion » à 15-30 pages — le chapitre 6 seul en fait déjà 10.
9. **Mise en page** : page de garde, sommaire automatique, listes des figures, des tableaux et des abréviations. Impression recto-verso obligatoire.
10. **Relecture complète** d'un bout à l'autre.

### Marqueurs restants
- **Chapitre 3** (3) : courbe d'apprentissage selon le nombre de profils ; définition des niveaux de confiance ; résidu du codage CYP2C9.
- **Chapitre 6** (13) : détaillés dans `Chapitre6_v15_NOTES.md`. Le seul obligatoire avant dépôt est le tableau 6.3, dont trois colonnes sont vides alors que les valeurs sont déjà dans le log.
- **Chapitre 9** (3) et **chapitre 1** (1) : l'audit de déterminisme non refait sur la v15.
- **Bibliographie** : pagination de Geifman et El-Yaniv ; métadonnées de Walsh et al. (DOME) ; volume de Kalinin et al. non vérifié sur Crossref ; date de consultation de la page CPIC Genes–Drugs ; référence exacte du tableau GeT-RM V4 ; **chiffre « 34 gènes et 164 médicaments » du chapitre 1, attribué à Caudle et al. 2025 et jamais vérifié** — à remplacer par un décompte daté sur le site de CPIC, ou à retirer.

### Abandonné et déclaré comme limite
Courbe d'apprentissage selon le nombre de profils ; audit de déterminisme sur la v15 ; attribution cause par cause des désaccords de génotype avec GeT-RM ; second relecteur pharmacologue pour les 285 règles.

---

## 4. Règles d'interaction en vigueur

- Zéro hallucination, zéro falsification. Un résultat négatif est analysé, jamais atténué.
- Toute valeur, tout choix, toute stratégie est justifié : pourquoi cette valeur, et ce qui empêche d'en avoir plus ou moins.
- Chapitres livrés **complets**, jamais section par section.
- **Deux fichiers par livraison** : mémoire et notes séparés.
- Sauvegarde quadruple, dans l'ordre : **WSL → Windows (`C:\Users\MSI\Desktop\memoire\`) → GitHub → Google Drive (`PharmaGeno_Memoire/`)**, via `bash ~/sauver.sh "message" fichiers...`. Les `.png` ne sont pas routés par le script et se copient à la main.
- Claude n'a **aucun accès à la machine de Mouna** : toutes les commandes sont exécutées par elle.
- Bloc « Sauvegarde / État d'avancement » à la fin de chaque réponse majeure.
