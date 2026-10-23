# Règles multi-gènes ambiguës : proposition de décision (23 oct 2026)

Statut : PROPOSITION. Aucun fichier officiel modifié, aucun réentraînement. Même règle de décision que pour les 59 règles mono-gène : on retient la première instruction du texte publié.

## Contenu
22 règles ambiguës dans `regles_v2_corrigees_multigene_v7.csv` : amitriptyline (4, CYP2C19×CYP2D6), fluvastatine (6, CYP2C9×SLCO1B1), rosuvastatine (3, ABCG2×SLCO1B1), sertraline (9, CYP2B6×CYP2C19).
Détail : `regles_ambigues_multi_decisions_proposees_v1.csv` (colonnes : décision, raison, début du texte publié).

## Décision
- 22 gardées avec la classe extraite : amitriptyline 4 éviter ; fluvastatine 6 adapter la dose ; rosuvastatine 3 adapter la dose ; sertraline 5 adapter la dose + 4 standard.
- 0 corrigée, 0 exclue (la classe extraite correspond à la première instruction dans les 22 cas).
- 5 de ces règles sont « conditionnelles » (fluvastatine CYP2C9=1.0×SLCO1B1=0.0 ; sertraline 4 règles standard). Le moteur exclut les règles multi-gènes conditionnelles ; je ne change pas le moteur. Elles restent donc non utilisées.

## Effet mesuré (aperçu, dossier de test)
- Corpus : 156 696 → 156 723 lignes (+27), toutes pour la rosuvastatine (aucune règle mono-gène pour ce médicament). Avec les 59 règles mono-gène : 152 600 → 156 723 (+4 123).
- Étiquettes existantes modifiées : 0.
- Médicaments dépendant du génotype : 74 avant et après (rosuvastatine déjà comptée).
- Contrôle de cohérence : pour les 18 règles (amitriptyline, fluvastatine, sertraline) dont le génotype existe dans les profils réels (1 379), la classe de la règle multi-gène est identique à l'étiquette déjà obtenue par les règles mono-gène (amitriptyline 141 profils, fluvastatine 393, sertraline 203, y compris les 5 règles conditionnelles). Les 2 règles rosuvastatine avec profils (27 lignes) n'avaient pas d'étiquette avant ; 2 règles n'ont aucun profil réel (rosuvastatine ABCG2=0.0×SLCO1B1=1.5 ; sertraline CYP2B6=2.0×CYP2C19=2.0).
- Limite : ce contrôle montre une cohérence entre deux jeux de règles CPIC, pas une validation indépendante.
