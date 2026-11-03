# Journal de Bord du Projet : 3 novembre 2026 (migration application v14)

## 1) Décisions validées / prises (par défaut, sur délégation « fait ce que tu veux »)
- Pilier A (DL sensible au médicament) : résultat négatif documenté, non intégré à l'application. Pilier B (IWPC warfarine) : validation positive avec réserves (VKORC1 non pris en compte par la règle source).
- Corpus v14 gelé (189 médicaments, 232 664 lignes, 1 379 profils) ; ensemble final 138 familles jamais lu.
- Application v8q = v8p + corpus v14 ; DL profil config 35 calibré (T = 0,233) ; DL choix v3 ; second avis v3. v8p / modeles_v9 intacts.
- 8 médicaments sans code ATC fiable et 3 sans spécialité : limites documentées (pas de nouvelle spécialité).
- Chiffre à rapporter : 189 médicaments (pas 210).

## 2) Erreurs à ne plus reproduire
- Ne pas annoncer un test (ex. ADAPTER_DOSE vs STANDARD) sans vérifier le contenu du corpus.
- Ne pas déclarer un fichier absent du Drive après une seule recherche (index en retard) : re-chercher par dossier parent ; vérifier fichier par fichier.
- Ne pas supposer que tous les ajouts ont besoin d'une ligne ATC (18 étaient déjà dans la table v1).
- Ne pas écrire « 210 » sans avoir vérifié l'affichage dans l'application cible (non affiché).
- Lancer les scripts avec `python3 -I` impose `sys.path.insert` dans le script.
- Ne jamais donner mot de passe / jeton dans le chat ; push GitHub depuis son WSL.

## 3) Plan restant
- Sauvegarde lot F (scripts, modeles_v10, modeles_v10x, domaine_v10.json, templates_v8q, app v8q, logs, docs) : WSL -> Windows -> GitHub -> Drive.
- Test VCF réel avec v8q (PyPGx) ; décision sur l'intégration des 21 médicaments « règle seule ».
- Optionnel : test direct du DL v14 sur IWPC ; tamoxifène (ITPC) ; règle cisplatine pédiatrique ; lectures restantes.
- Côté Mouna : sécurité Google, suppression du jeton inutilisé `wsl-sauvegarde-nov2026`, visibilité du dépôt avant le 25 nov.
- Rédaction : chapitres 1-3 (5-8 nov), 4-8 (9-16 nov), relecture (17-20 nov), marge (21-24 nov), dépôt 25 nov.
