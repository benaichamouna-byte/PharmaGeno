# Journal de Bord PharmaGeno — 27 octobre 2026

## 1) Décisions validées
- Les 81 règles ambiguës sont lues dans le texte publié (CPIC/DPWG) et classées par formulation (data/audit_81_regles_decisions_v1.csv) :
  type 1 (éviter d'abord, 36) = EVITER ; type 2 (dose d'abord, 20) = ADAPTER_DOSE ; type 3 (deux options au choix, 14) = ADAPTER_DOSE ;
  type 4 (dépend de la co-médication/indication : mavacamten, quétiapine, 2) = EXCLURE ; type 6 (standard d'abord, 6) = STANDARD ;
  type 5 (3 AINS CYP2C9 intermédiaire) = règles par score d'activité.
- CYP2C9 recodé en score d'activité / 2 : 0 ; 0,25 ; 0,5 ; 0,75 ; 1,0 (diplotype PyPGx + table CPIC des allèles, API CPIC /allele).
- Les 7 AINS (célécoxib, flurbiprofène, ibuprofène, lornoxicam, méloxicam, piroxicam, ténoxicam) : règles écrites pour les 5 valeurs d'après l'API CPIC (guideline 110058).
- Objectif de couverture : 133 médicaments d'abord ; groupe B (27) puis C (24) ensuite si le temps et les données le permettent. Dépôt en novembre (date exacte inconnue).

## 2) Résultat du jour : corpus v9 (data/corpus_v9/phenotype_drug_dataset_v9.csv)
- 157 809 lignes (v8 : 152 600), 133 médicaments, 1 379 profils. STANDARD 133 931 | ADAPTER_DOSE 14 655 | EVITER 8 446 | SURVEILLER 777.
- Vs v8 : 5 224 lignes nouvelles (règles ambiguës tranchées), 589 étiquettes corrigées (588 STANDARD -> ADAPTER_DOSE pour les 146+1 profils CYP2C9 au score 1,0 sur célécoxib/flurbiprofène/ibuprofène/lornoxicam ; 1 ADAPTER_DOSE -> EVITER pour siponimod), 15 lignes retirées (CYP2C9 indéterminé ou recodé).
- Contrôle croisé : étiquettes AINS par génotype conformes à la table CPIC (*1/*2 standard ; *1/*3 dose réduite ; piroxicam et ténoxicam éviter).
- Entraînement : NON refait. Le corpus v9 n'a pas encore servi à entraîner quoi que ce soit.
- Données : profils_genes_v5.csv (CYP2C9 recodé ; colonne CYP2C9_ancien_codage conservée). 4 profils avaient un CYP2C9 différent du diplotype PyPGx dans v4 : HG00288 et NA18637 (*1/*1 codés 0,5), HG01855 (*3/*29 codé 0,5 au lieu de PM), HG03887 (*1/*66 indéterminé codé 1,0).

## 3) Erreurs à ne plus reproduire
- Classer une règle sur un mot-clé (« alternative statin ») sans lire le texte : 20 règles étaient de faux ambigus.
- Fusionner deux scores d'activité dans une même valeur sans lire la directive (CYP2C9 AS 1,0 et 1,5 : 146 patients mal étiquetés sur 4 AINS).
- Copier le codage d'un gène depuis un corpus ancien au lieu de le recalculer avec la même chaîne que le lecteur VCF (4 profils CYP2C9 incohérents).
- Présenter un résumé automatique d'API comme vérifié ligne par ligne (la liste CPIC AINS a été relue ligne par ligne, 42 lignes ; phénytoïne/fosphénytoïne non).
- Annoncer des durées ou des chiffres non mesurés.

## 4) Plan restant (dépôt en novembre)
S1 (27 oct-2 nov) : [fait] audit 81 règles ; [fait] corpus v9 ; reste : relire ligne par ligne l'API CPIC pour phénytoïne/fosphénytoïne ; vérifier TPMT/NUDT15/SLCO1B1/UGT1A1 (classes qui regroupent plusieurs scores) ; ajouter CYP2C9_manquant (34 entrées) ; adapter le lecteur VCF (score d'activité) ; mesurer le temps d'un entraînement ; Journal ; protocole v9 écrit (à montrer avant tout entraînement).
S3 (10-16 nov) : recherche d'hyperparamètres (validation seule) -> un seul réentraînement -> combinaisons cachées ; chapitres 3 à 5 en parallèle.
S4 (17-23 nov) : validation indépendante (tamoxifène/CYP2D6) ; gel du protocole par écrit ; UNE lecture du jeu final de 138 patients ; paquet de déploiement.
S5 (24-30 nov) : chapitres 6 à 8, relecture, dépôt. Groupes B et C en perspectives si le temps manque.
Application : corriger vue patient/détails ; moteur et règles de l'app à passer en v9 (CYP2C9 recodé).
Sauvegarde : WSL -> Windows (cp vers C:\Users\MSI\Desktop\memoire\) -> GitHub (git add fichier par fichier) -> Drive (PharmaGeno_Memoire/).
