# Journal de Bord du Projet : 3 novembre 2026 (soir : app v8r et envoi à l'encadrant)

## 1) Décisions validées
- Paquet de déploiement v8r envoyé à l'encadrant (Pr. Ghedira) le 3 nov. au soir : lien Drive (dossier `PharmaGeno_Webtool_Deploiement_Encadrant` : zip « (3) » + 2 captures d'écran), mail sans pièce jointe, puis WhatsApp court.
- Contenu du mail : pas de somme de contrôle, pas de partage d'écran ni de créneau proposé, mention que la copie draft du rapport sera finalisée d'ici quelques jours.
- PDF d'exemple non envoyé à l'encadrant.
- Affichage v8r : quatre avis avec score 0-1 (DL, directive officielle, XGBoost, Random Forest), références, plus de décompte de gènes ni de « confiance x % », profil de démonstration retiré de l'interface (téléversement VCF = chemin principal).
- Chiffres de référence : zip final 45 026 792 octets, sha256 c582882ba6d6fb0c9b8d71a4b8b9fb26828d08dcd277de0a51b1fef1ed06c0aa ; 73 contrôles de test réussis ; 189 médicaments.

## 2) Erreurs à ne plus reproduire
- Livrer un paquet sans avoir vérifié le PDF exporté : à chaque changement d'affichage, contrôler l'écran ET le PDF.
- Donner une commande sans dire dans quel terminal la lancer (PowerShell Windows ou WSL) ni où se trouve le fichier ; donner chaque test avec but, commande et résultat attendu.
- Donner une étape Drive sans préciser « Importer des fichiers » (et non « Importer un dossier »).
- Épingler `torch==2.14.1` dans requirements.txt (remplace le torch CPU par une version CUDA).
- Proposer un partage d'écran ou un créneau dans les mails à l'encadrant.
- Présenter une référence générale de source comme la publication précise de la directive.
- Affirmer qu'une donnée existe (ex. force de recommandation CPIC) sans l'avoir vérifiée dans ses données.
- Poser plusieurs questions floues ou reformuler ses consignes avec mes propres mots.
- Taille Explorateur Windows en Ko de 1024 octets : ne pas chercher « 45026792 » tel quel (43 972 Ko).

## 3) Plan exact de ce qui reste
- Sauvegarde du jour (un seul lot, lot I) : WSL -> Windows (C:\Users\MSI\Desktop\memoire\) -> GitHub (sans le zip de 45 Mo) -> Drive (PharmaGeno_Memoire/, rangé par type).
- Répondre aux retours de l'encadrant sur l'installation ; si erreur, diagnostiquer à partir du message copié ou du résultat de verifier_installation.py.
- Copie zéro du mémoire (Claude Doc « Mémoire PharmaGeno : copie zéro (3 nov. 2026) ») : Résumé et chapitre 1 faits ; à rédiger : chapitre 2 (état de l'art, revue de littérature), 3 (prochaine étape proposée : données et prétraitement), 4, 5, 6, 7 (IWPC), 8, références et annexes.
- Pilier C (dose de warfarine, protocole figé hash 1c2e7550d617fc36) : à lancer après accord de Mouna.
- Comparaison équitable DL / XGBoost / RF sur le corpus v14 et lecture unique des 138 familles finales.
- Concordance avec PharmCAT (à valider par Mouna).
- Association précise directive -> publication (environ 152 identifiants PA ; API CPIC inaccessible depuis le shell).
- Calendrier : chapitres 1-3 (5-8 nov.), 4-8 (9-16 nov.), relecture (17-20 nov.), marge (21-24 nov.), dépôt 25 nov. ; soutenance en décembre.
- Côté Mouna : sécurité Google, suppression du jeton `wsl-sauvegarde-nov2026`, visibilité du dépôt avant le 25 nov.
