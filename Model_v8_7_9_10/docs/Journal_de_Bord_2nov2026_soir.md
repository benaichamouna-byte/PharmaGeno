# Journal de Bord — 2 novembre 2026, soir (pilier B)
## 1) Décisions validées
- Mouna : « fais ce que tu veux » -> pilier B (validation sur patients réels) lancé, protocole fixé avant analyse (18 h 19).
- Données : seul le fichier IWPC 2009 (6 922 sujets) est utilisé ; le fichier 2008 est un sous-ensemble.
- Corpus v14 gelé non modifié.
## 2) Erreurs à ne plus reproduire
- Avoir annoncé « ADAPTER_DOSE contre STANDARD » pour la warfarine sans avoir vérifié le corpus : il n'y a aucune ligne STANDARD pour cette molécule (comparaison réelle : ADAPTER_DOSE contre *1/*1). Vérifier le contenu du corpus avant d'annoncer un test.
- Bootstrap S6 : graine recréée à chaque tirage (IC dégénéré) ; corrigé. Toujours créer le générateur aléatoire une seule fois.
- Libellé d'heure erroné (11 h au lieu de 18 h 19) dans une étiquette post hoc ; corrigé.
- Ne pas mettre de données patients (IWPC) dans un dépôt GitHub public.
## 3) Plan restant
- Sauvegarder le lot du pilier B (WSL -> Windows -> GitHub -> Drive), sans les données IWPC.
- Décider : test direct du DL sur IWPC si les modèles entraînés sont disponibles ; tamoxifène (ITPC) sur le même principe.
- Migration de l'application vers le corpus v14 (2-4 nov.) ; chapitres 1-3 (5-8 nov.), 4-8 (9-16 nov.), relecture (17-20 nov.), marge (21-24 nov.), dépôt 25 nov.
- Mouna : sécurité Google (codes de secours, passkey), supprimer le jeton inutilisé, décider de la visibilité du dépôt avant dépôt.
