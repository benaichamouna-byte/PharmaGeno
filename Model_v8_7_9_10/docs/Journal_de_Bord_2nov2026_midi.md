# Journal de Bord — 2 novembre 2026, midi

## 1) Décisions validées par Mouna
- Le DL est le cœur du projet, l'application aussi ; le corpus doit être étendu (« corpus plus grand »). C'est Mouna qui décide de l'extension et du gel ; rien n'est gelé sans son accord.
- Groupe A (6 étiquettes) : « corpus plus étendu OK » -> règles ajoutées (nilotinib, erlotinib, carisoprodol, cevimeline, lonafarnib, glyburide), puis fluindione (RNPGx 2017). Corpus v14b : 189 médicaments, 232 646 lignes, dossier `data/corpus_v14b/` (v14 inchangé, v13 gelé).
- Groupe B (9 substances à forte association sans action publiée) : sans préférence -> vérification CPIC/DPWG faite : aucune n'a de recommandation d'action sur un gène des profils ; restent au niveau association.
- Pilier A choisi (« pilier A », 11 h 18) : DL qui généralise au médicament, évalué sur des médicaments jamais vus.
- Règle permanente : ne pas mentionner XGBoost / RF quand on parle du DL.

## 2) Erreurs à ne plus reproduire
- Décrire le contenu de fichiers sans les ouvrir (j'ai affirmé que les xlsx SLCO1B1, TPMT, CYP2C19, CYP2D6-codéine étaient des cohortes ; ce sont des tables de décision CPIC). Ouvrir chaque fichier avant d'en parler.
- Présenter un gel ou un arrêt de l'extension comme une décision prise alors que Mouna ne l'avait pas validée.
- Redemander « ok ? » en boucle : donner la recommandation et agir quand le périmètre est validé.
- Lancer des appels WebFetch en parallèle vers un même hôte (limitation de débit) ; PubMed Central bloque l'accès (anti-robot) : demander le texte à Mouna.
- Comparer à tort un nombre de médicaments entre sources sans préciser la méthode de comptage.
- Ne pas utiliser les colonnes « Dosing Guideline », « Top CPIC Pairs Level », « Top FDA Label Testing Level », « Label Has Dosing Info » des exports ClinPGx comme descripteurs (fuite d'étiquette).

## 3) Chiffres et faits établis aujourd'hui
- CPIC (présentation du 2 oct. 2025) : 29 guidelines, 16 mises à jour, 35 gènes, plus de 160 médicaments. PharmCAT local (commit du 25 sept. 2026) : 197 médicaments, 31 gènes (CPIC 88/22, DPWG 58/15, FDA 164/27).
- Sherman 2024 (Sci Rep) : PyPGx sur 1000 Genomes (N = 2 504), 58 pharmacogènes ; G6PD sans phénotype CPIC dans PyPGx -> notre codage G6PD est un codage du projet.
- Niveaux N1 (204 substances) : tous au corpus ou en règle seule. 705 substances sans règle sont liées à un gène des profils ; 440 ont une structure moléculaire.
- Lecture DPWG : atenolol, duloxetine, olanzapine (CYP2D6), sotalol, méthotrexate (MTHFR), ribavirine : « not a gene-drug interaction », aucune recommandation. Cisplatine/TPMT (CPNDS) : enfants seulement ; non codé (règle conditionnelle).
- Données patients réelles avec issue : IWPC (warfarine, 5 700 et 6 923 sujets) et ITPC (tamoxifène). Les xlsx CPIC ne sont pas des cohortes.

## 4) En cours
- Pilier A : `scripts/construire_descripteurs_medicaments_v1.py`, `scripts/evaluer_dl_medicament_v1.py`, `scripts/analyser_dl_medicament_v1.py` ; résultats dans `results/dl_medicament_v1/` (en cours, ~2 h). Ensemble final de 138 familles exclu (jamais lu).

## 5) Plan restant (exhaustif)
1. Terminer le pilier A : analyse (IC par bootstrap sur les médicaments), fiche de résultat, intégration à l'application seulement si le DL dépasse les références.
2. Pilier B (optionnel, au choix de Mouna) : IWPC (warfarine) et ITPC (tamoxifène), validation de l'étiquette par issue réelle.
3. Décisions du gel : carisoprodol (garder/retirer), 6 ajouts faibles de v14, v14b ou v14 comme corpus final ; puis fiche GEL avec empreintes (v14b : corpus b3e3a608a1d6e802, règles 469fb67969c80967).
4. Vérifier que les 21 médicaments « règle seule » s'affichent dans la version cible de l'application.
5. Migration de l'application (v8p -> v13/v14), chapitres 1 à 3 (5-8 nov.), chapitres 4 à 8 (9-16 nov.), sauvegarde et relecture (17-20 nov.), marge (21-24 nov.), dépôt 25 nov.
6. Sauvegarde : copier les nouveaux fichiers dans le dépôt un par un (jamais `git add .`), pousser la branche `sauvegarde-2026-11-01` (GitHub non lié à la session), puis Windows (C:\Users\MSI\Desktop\memoire\) et Google Drive (PharmaGeno_Memoire/).
7. Lectures restantes optionnelles : méthylphénidate, acide folique, olanzapine (CYP1A2), tebentafusp ; cisplatine pédiatrique si le moteur gère les conditions.
