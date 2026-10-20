# Journal de Bord du Projet PharmaGeno - 19 octobre 2026, soir (mis à jour 21h30)

Titre : A Deep Learning based Webtool for Mutation-Aware Drug Recommendation. Dépôt vers le 12 nov. (non confirmé) ; soutenance en décembre 2026 ; encadrant (Pr. Ghedira) disponible à partir du 15 nov. Ce journal complète celui du matin (Journal_de_Bord_19oct2026.md), qui reste intact.

## 0. RÈGLE ABSOLUE (rappelée plusieurs fois par Mouna, à relire avant toute décision)
- **Le DL est le CŒUR du sujet et de l'application.** Ne jamais le reléguer (« CPIC en priorité, DL en option », « le DL copie les règles donc on le laisse », « second avis »). Quand un résultat est mauvais ou montre une limite, le traiter comme un problème à résoudre EN GARDANT le DL au centre, jamais comme une raison de reculer.
- Une limite mesurée (ex. médicament jamais vu : 0,467) s'écrit honnêtement dans le mémoire et sert à orienter la recherche ; elle ne change pas le rôle central du DL.
- Application : le DL produit la recommandation ; la règle CPIC est affichée à côté comme référence/explication, avec alerte claire en cas de désaccord ; pour un médicament hors liste (non vu à l'entraînement), afficher « non évalué » au lieu d'une prédiction DL non fiable. (Position à confirmer par Mouna ; la partie « DL = moteur » est certaine.)

## 1. Décisions prises et validées par Mouna
- Objectif DL : le DL le plus optimal pour le sujet. XGBoost et RF sont seulement des références ; ne jamais présupposer que le DL les bat ou non (« j'ai jamais dit DL bat XGBoost »).
- Priorités : jeu de données fiable et optimal ; application avec une rigueur absolue (v8 pas encore commencée) ; rester centré sur le sujet du master (DL + application). Les données CPIC/corpus sont un moyen borné, pas une fin.
- Règles de travail : nouvelles versions à côté des anciennes (rien n'est écrasé) ; une seule action par message ; expliquer avant d'agir ; elle colle les résultats (pas la commande) ; mots simples en français ; vérifié / déduit séparés ; liste complète des fichiers à télécharger avec tailles mesurées.
- Chaîne de sauvegarde : WSL (~/projet_memoire/lots_19oct2026) -> Windows (C:\Users\MSI\Desktop\memoire\lots_19oct2026) -> GitHub -> Drive (PharmaGeno_Memoire/ -> lots_19oct2026, déposé à la main).
- Corpus v7 (130 578 lignes) : profils v4 (NUDT15, TPMT, SLCO1B1 recalculés par PyPGx 0.27.0 puis table CPIC ; indéterminé ou diplotype absent de la table = manquant), 6 règles « normal -> STANDARD » pour azathioprine, mercaptopurine, thioguanine (CPIC, TPMT NM + NUDT15 NM), SLCO1B1 « increased function » recodé de 2,0 à 1,5. Le moteur de règles construire_corpus_v3.py est inchangé.
- Protocole v8 inchangé : StratifiedGroupKFold(5) groupé par famille, graine 42, 10 % des familles à part (ensemble final jamais utilisé à ce jour, à utiliser une seule fois à la fin), validation interne 10 % des familles, 551 variables.
- Configuration DL retenue : DL film, identifiant de médicament, poids de classes « racine », poids EVITER x2, tous les gènes.
- Sauvegardé sur les 4 supports (tailles vérifiées) : lot_profils_v4_corpus_v6 (bbef102), lot_corpus_v7_final (e86ca4e), lot_dl_v9 40 246 380 octets (2648a43), lot_dl_v10 15 410 132 octets (9d60150).

## 2. Constats établis (mesurés dans les fichiers)
Corpus v7, moyenne des 5 plis, une graine, F1 macro / EVITER manqués (CER strict) :
- XGBoost 0,9999 / 0,0011 ; Random Forest 0,9817 / 0,0489.
- DL film empreinte, poids inverse (référence v9) : 0,9687 / 0,0131. Poids « racine » : 0,9931 / 0,0176. Sans poids : 0,7374 (SURVEILLER jamais appris).
- Poids EVITER x2 : 0,9896 / 0,0053 ; x4 : 0,9880 / 0,0045 ; x8 : 0,9651 / 0,0030.
- Identifiant de médicament : 0,9981 / 0,0051. Identifiant + EVITER x2 : 0,9973 / 0,0032.
- Graines multiples (5 graines, même découpage, identifiant + EVITER x2) : F1 macro 0,9980 +/- 0,0010 (0,9966 à 0,9987) ; EVITER manqués 0,0029 +/- 0,0010 (0,0015 à 0,0043) ; précision EVITER 0,992 +/- 0,005. XGBoost n'a qu'une graine : l'écart sur les EVITER manqués (0,0029 contre 0,0011) n'est pas tranché.
- Médicament jamais vu (5 plis groupés par médicament, empreinte identique = même groupe, ensemble final non utilisé), F1 macro / exactitude / EVITER manqués : témoin majorité 0,261 / 0,853 / 1,000 ; gènes seuls 0,219 / 0,414 / 0,626 ; RF 0,502 / 0,877 / 0,698 ; XGBoost 0,454 / 0,825 / 0,629 ; DL empreinte 0,467 / 0,807 / 0,641. Écarts entre modèles du même ordre que l'écart-type entre plis (0,08 à 0,09), aucun test statistique fait. DL : exactitude >= 95 % pour 54 médicaments sur 113, < 50 % pour 18 ; parmi les 35 médicaments avec EVITER, rappel EVITER >= 90 % pour 9 et < 10 % pour 20.
- Interprétation non vérifiée : l'empreinte ne dit pas quel gène gouverne le médicament.
- **Cause structurelle du « le DL copie CPIC » (déduite)** : les entrées du DL sont des phénotypes déjà calculés (PyPGx puis table CPIC : 0 ; 0,5 ; 1 ; 1,5 ; 2) et l'étiquette est la règle CPIC appliquée à ces phénotypes. Toute l'intelligence « mutation » est faite avant le DL. À traiter par la conception (direction A ci-dessous), pas en rétrogradant le DL.
- Lecture : Tremmel et al., Pharmacogenomics 2025;26(5-6):171-182 (doi:10.1080/14622416.2025.2504863 ; lue par résumé automatique, à vérifier dans l'article avant de citer) : le ML apporte surtout pour les variants rares/nouveaux de fonction non établie, les effets propres à un médicament (ex. SLCO1B1*15 simvastatine/atorvastatine), les effets combinés sur un haplotype, l'imputation/phase des haplotypes, les scores polygéniques ; les auteurs ne comparent pas le ML aux tables CPIC/PharmVar.
- Grinsztajn et al., arXiv 2207.08815 (pages 1 à 9) : banc d'essai sans cibles déterministes, ~10 000 exemples ; notre cible est déterministe. Autres références (Shwartz-Ziv & Armon 2022, Gorishniy 2021 et 2022, Perez 2018 FiLM) pas ouvertes : à vérifier avant de citer.

## 3. Erreurs à ne plus reproduire
- **Reléguer le DL (« option », « second avis », « copieur ») ou proposer de le laisser tomber après un résultat décevant.** Partir toujours de « le DL est le cœur » et chercher comment lui donner un rôle propre. Ne pas attendre les résultats pour soulever un problème de conception : le dire AVANT d'entraîner.
- Annoncer un effet ou un nombre sans l'avoir compté.
- Annoncer le score d'une version sans noter les différences de variables avec la suivante.
- Estimer une durée sans base (annoncé 25 à 35 min pour « médicament jamais vu », réel environ 7 min).
- Excuses vagues suivies d'un changement de sujet : donner la justification réelle.
- Colonnes `<GENE>_genotype_pypgx` prises pour des gènes par le moteur : les colonnes `_source`, `_genotype`, `_phenotype` sont exclues.
- sed sur un script en cours de modification ; deux fichiers de règles codant SLCO1B1 différemment (relancer controle_codage_regles_profils_v1.py à chaque changement) ; demander un téléchargement sans liste complète ; affirmer le contenu d'un zip sans l'ouvrir ; lancer un entraînement sans validation ; prendre un indéterminé pour un normal.

## 4. Limites à écrire dans le mémoire
- 18 profils TPMT/NUDT15 métaboliseurs lents exclus pour les thiopurines (règle ambiguë selon l'indication) ; 72 profils avec un seul des deux gènes connu exclus.
- DPYD non recalculé (valeurs v3 ; 14/15 en accord avec GeT-RM, 34 non comparables).
- 4 médicaments sans empreinte (5 400 lignes) : pegloticase, rasburicase, sulfaméthoxazole/triméthoprime, vitamine K.
- HLA partiel : typé pour 508 profils sur 1 379 ; valeurs 0,5 « possible » exclues ; porteurs EVITER rares (B*58:01 : 3, A*31:01 : 4).
- Environ 16 médicaments sans règle « normal -> standard » (quétiapine, ésoméprazole, flécaïnide, warfarine, antipsychotiques CYP2D6, etc.).
- Étiquettes déterministes (issues de règles) ; une seule graine pour XGBoost/RF ; un seul découpage en plis ; identifiant de médicament limité aux médicaments connus ; ensemble final non encore utilisé.
- NAT2 (4) et CYP2A6 (8) : désaccords avec GeT-RM non expliqués ; GeT-RM ne teste qu'une liste limitée d'allèles.

## 5. Plan restant (état du 19 oct. soir ; voir le journal du 20 oct. pour l'état à jour)
1. Décision en attente de Mouna : rôle propre du DL (A = niveau mutation ; B = niveau recommandation avec abstention).
2. Réglage léger des hyperparamètres (recherche aléatoire) sur la validation uniquement ; mêmes réglages équitables pour XGBoost et RF ; plusieurs graines pour tous.
3. Utiliser l'ensemble final de 10 % une seule fois, à la fin.
4. Application v8 ; comparaison avec une prédiction réelle d'une étude publiée ; rédaction des chapitres 3 à 8 ; mise à jour du plan Excel.
