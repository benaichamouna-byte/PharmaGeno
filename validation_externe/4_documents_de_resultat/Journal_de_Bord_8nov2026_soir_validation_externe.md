# Journal de Bord — 8 novembre 2026, soir : validation externe par les études publiées

## 1) Décisions prises et validées
- Mouna a validé le plan (« go » à 19:31) : comparer les alertes de l'application aux études publiées pour le même gène/état/médicament. PharmCAT + lecture de phrases = vérification d'implémentation seulement.
- Source : fichiers bruts ClinPGx var_drug_ann + var_pheno_ann (27 590 lignes, résultats nuls inclus). Le CSV du projet (6 063 lignes, significatifs seulement, sans toxicité) est abandonné pour ce volet.
- Protocole figé avant calcul (PROTOCOLE_validation_externe_v1.md) ; amendement 1 daté, décidé après v1 : A1 hétérozygote sans fonction = IM ; A2 sens de dose lu à la main sur le texte des règles ; A3 indicateur descriptif part concordante.
- Résultat v1.1 (285 règles) : soutenue 44, mixte 63, non soutenue 23, signal non orienté 32, non tranchable 2, non appariées 51, aucune étude 70. Verdict auto ajusté dans 4 règles sur 30 de l'échantillon aléatoire (13 %).

## 2) Erreurs à ne plus reproduire
- Ne pas annoncer des chiffres de couverture calculés sur un fichier filtré (76 couples / 163 règles : faux ; 109 couples ont des lignes).
- Ne pas laisser une règle de dose lue par expression régulière sans relecture (textes statines lus « hausse » à tort).
- Ne pas compter un hétérozygote avec les métaboliseurs lents.
- Ne pas étiqueter une règle sans compter les lignes (tamoxifène : étiquette « non soutenue sur l'efficacité » fausse, corrigée après comptage : 12 PMID survie/récidive dans le sens de l'alerte).
- Ne pas mettre un hash de zip dans un fichier du zip.
- Valider = comparer à une source externe pour le même profil ; ne pas proposer de lecture de phrases comme validation.

## 3) Reste à faire
- Mouna : sauvegarde triple du paquet validation_externe_v1_1_8nov2026.zip ; noms de 2–3 relecteurs ; copie zéro (« Reconstruire » / « Demain ») ; visibilité GitHub ; message à Pr. Ghedira dès le 15 nov.
- Moi : demain contrôle qualité n°2 à l'aveugle (10 nouvelles paires) ; relire à la main les 51 règles non appariées et les EVITER « signal non orienté » ; lire les études pivots (HLA-B*58:01, EU-PACT, COAG, TAILOR-PCI, G6PD, MT-RNR1, PREPARE) via sources accessibles ; 10 profils aléatoires parmi les 150 ; cas de discordance catégorie 5 de la partie 1 (NA12717, NA06991, NA10847) ; nouveau Doc mémoire (résultats d'abord).
- Un second relecteur humain (pharmacologue) pour les alertes EVITER.
