# Journal de Bord — 2 novembre 2026, après-midi

## 1) Décisions validées
- Corpus v14 GELÉ (2 nov., ~11 h 40) : 189 médicaments, 232 664 lignes ; décisions déléguées par Mouna à la pratique de la littérature : carisoprodol retiré (table FDA = pharmacocinétique seule, comme tamsulosine) ; avatrombopag-F5 ajouté (même texte que eltrombopag et lusutrombopag) ; six ajouts à preuve plus faible conservés (confiance « moyenne », analyse de sensibilité) ; v14 gelée = ancienne v14b corrigée. Empreinte corpus v14 : b876bb469e562d6e ; règles mono-gène : 39a736892cf6cc58. Fiche `data/corpus_v14/GEL_v14_2nov2026.txt`.
- Pilier A choisi par Mouna et évalué (3 schémas, 3 graines, bootstrap sur les médicaments).
- Résultat du pilier A : négatif (voir `Resultat_pilier_A_DL_medicament_2nov2026.md`) : le DL à descripteurs de médicament ne dépasse pas `prior_gene_phenotype` ni `voisins_k5` ; pas d'intégration à l'application ; à rapporter comme résultat exploratoire négatif.
- Sauvegarde du jour sans GitHub : archives `lot_2nov_corpus_scripts_docs.zip` et `lot_2nov_B_predictions_pilierA.zip` ; push à faire depuis le WSL de Mouna avec ses propres identifiants (jamais de mot de passe ou jeton dans le chat).

## 2) Erreurs à ne plus reproduire
- Décrire des fichiers sans les ouvrir ; présenter un gel comme décidé sans validation ; demander « ok ? » en boucle ; WebFetch parallèle vers un même hôte ; comparer des nombres de médicaments sans méthode de comptage ; utiliser comme descripteurs les colonnes de guideline des exports ClinPGx (fuite d'étiquette).
- Lancer un bootstrap non optimisé (recalcul sklearn sur 209 000 lignes à chaque tirage) : plus de 30 min sans résultat. Toujours précalculer le tri des scores et vérifier la version rapide contre la référence.
- Proposer à Mouna de « lier GitHub dans Connecteurs » sans vérifier : le connecteur de chat GitHub n'ouvre pas l'accès Git de la session ; la session n'a jamais réussi de push (clone en lecture + commit local `e30cedd` sur `sauvegarde-2026-11-01`, non poussé).
- Ne pas mentionner XGBoost / RF quand on parle du DL ; ne pas fournir de formulation pour le jury sans demande.

## 3) Plan restant (exhaustif)
1. Décider du sort du pilier A (résultat négatif) : rapporter tel quel dans le mémoire ; reprise éventuelle seulement avec un nouveau protocole fixé à l'avance.
2. Sauvegarde : Mouna pousse le lot A depuis WSL (commandes données), copie vers C:\Users\MSI\Desktop\memoire\ et Google Drive (PharmaGeno_Memoire/), lot B (prédictions) sur Drive/Windows.
3. Compte Google : codes de secours, clé d'accès Windows, déconnexion du Galaxy A10s ; vérification d'identité temporairement bloquée, attendre sans réessayer.
4. Vérifier que les 21 médicaments « règle seule » s'affichent dans la version cible de l'application avant d'écrire « 210 ».
5. Migration de l'application (v8p -> v14) 2-4 nov. ; chapitres 1 à 3 (5-8 nov.) ; chapitres 4 à 8 (9-16 nov.) ; sauvegarde et relecture (17-20 nov.) ; marge (21-24 nov.) ; dépôt 25 nov.
6. Optionnel au choix de Mouna : pilier B (IWPC warfarine, ITPC tamoxifène) ; lectures restantes (méthylphénidate, acide folique, olanzapine CYP1A2, tebentafusp).
