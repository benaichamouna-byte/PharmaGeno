# Registre des sources externes « profil génétique du patient + recommandation » (9 novembre 2026)

Définition de la validation (Mouna, 9 nov.) : chercher partout (études, articles, logiciels, bases) un profil génétique de patient (VCF ou génotype) ET la recommandation médicamenteuse correspondante ; tester le même profil sur l'application ; comparer.

## Sources utilisées
| Source | Type | Contenu | Test sur l'application | Résultat |
|---|---|---|---|---|
| PharmCAT 3.4.0 (https://github.com/PharmGKB/PharmCAT) | logiciel de référence CPIC | recommandations CPIC/DPWG pour les 104 VCF | fait le 8 nov. | 97,8 % des règles affichées retrouvées chez PharmCAT |
| Étude pilote 11 patients atteints d'insuffisance rénale (PMC12639823, https://pmc.ncbi.nlm.nih.gov/articles/PMC12639823/), Tableau 1 | article, patients 1, 5, 7, 8 | génotype, phénotype, recommandation (CPIC) pour 7 lignes patient–gène | 9 nov. : personnes GeT-RM de même génotype (CYP2C19 *1/*2 n=12 ; *1/*17 n=11 ; CYP3A5 *1/*3 n=18 ; SLCO1B1 *1B/*1B n=12 ; *1/*15 n=5) | 4 lignes identiques (IPP *1/*2 ×3, tacrolimus), 3 compatibles (IPP *1/*17 : +50–100 %, doses fractionnées, mais « IPP plus puissant » absent ; SLCO1B1 normal et réduit : même sens) ; 0 contradiction |

Limites du test PMC12639823 : 4 patients, génotypes sans VCF (remplacés par des personnes GeT-RM de même génotype), recommandations CPIC (mêmes guides), compatibilité lue à la main par un seul lecteur ; 3 personnes sur 12 *1B/*1B n'avaient pas de ligne SLCO1B1 dans l'application.

## Sources lues, non utilisables telles quelles
- Bousman 2019 (Pharmacogenomics J, https://www.nature.com/articles/s41397-018-0027-3) : 5 patients simulés, 4 outils commerciaux, accord 55–84 % entre outils ; données non lues.
- Man vs machine 2021 (https://pmc.ncbi.nlm.nih.gov/articles/PMC8926977/) : 200 patients, aucune donnée publique.
- VSPGx (bioRxiv 2025, https://www.biorxiv.org/content/10.1101/2025.11.24.690276.full.pdf) : 3 655 VCF synthétiques CYP2C9 vs PharmCAT ; données non publiées.
- PharmInform (https://github.com/NosakhareOsaro/pharminform) : validation GeT-RM, pas de concordance de recommandations.
- lmPGX (J Mol Diagn 2022, https://www.sciencedirect.com/science/article/pii/S1525157822000034) : logiciel indépendant de PharmCAT, code public (GitHub MGB-Personalized-Medicine/PGx), rapports d'exemple en annexes S1/S2 ; entrée BAM/CRAM (à vérifier : VCF ?) ; pas de comparaison de recommandations avec une source externe.
- AgenticGenomics (Zenodo 21710394) : cas synthétiques de modèles de langage, sans VCF.
- OpenPGx : n'accepte pas les VCF ; pas de validation.
- Pages non lues (accès bloqué) : article PharmCAT 2020 (Wiley), GenomeGuard (SSRN), PMC12746526, PMC9988947.

## À faire
- Vérifier si lmPGX peut tourner sur nos VCF (deuxième logiciel indépendant).
- Chercher d'autres articles avec tableaux patient par patient (génotype + recommandation) ; lire PMC12639823 Tableau S3 (11 patients).
- Tests sur diplotypes synthétiques générés depuis les tables CPIC (lecture B).

## Sauvegarde
WSL (développement) → Windows (cp vers C:\Users\MSI\Desktop\memoire\) → GitHub (git add/commit/push) → Google Drive (PharmaGeno_Memoire/).
