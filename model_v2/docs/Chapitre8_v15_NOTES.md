# Chapitre 8 v15 — notes

**Ce document ne fait pas partie du mémoire.** Il accompagne `Chapitre8_v15_MEMOIRE.md`, qui remplace le chapitre 8 de `Memoire_texte_v6.md`.

## 1. Provenance de chaque chiffre (tout a été relu dans le fichier source)
| Chiffre | Source |
|---|---|
| 4 589 / 3 357 / 3 221 (95,9 %) ; CPIC 2 950/2 976 ; DPWG 271/381 ; 136 lignes, 21 motifs | `results/validation_externe_pharmcat_v8t/detail_A1_centre_app_104.csv` et `motifs_NON_RETROUVEE_A1.csv` (recomptés) |
| 34 / 104 personnes sans ligne non retrouvée | recompté sur `detail_A1` (v14 : 70 / 104) |
| Motifs warfarine : 41 + 30 + 12 + 8 (formulation/structure) = 91 ; 5 (\*1/\*2 appliqué à \*1/\*5, \*1/\*8, \*1/\*11) ; 2 (20 % contre 45 %) | lecture ligne par ligne de `detail_A1` |
| Siponimod 8 ; thiopurines 8 × 3 (6 NUDT15 appelé différemment, 2 règle TPMT seule) ; flucytosine 4 (traduction) ; fluvastatine 1 ; sertraline 1 | idem |
| Warfarine 65 / 70, 34 sans reco, 5 écarts | `Resultat_comparaison_v8t_vs_PharmCAT_104_15nov2026.md` |
| Parenté : 18 personnes ; 2 657/2 771 (95,9 %) et 564/586 (96,2 %) | **recalculé ce jour** sur `detail_A1` v8t + `data/1kGP_3202_pedigree.txt` + corpus v15 (même règle parent-enfant + fratrie que le 9 nov. ; les 18 retrouvés à l'identique) |
| 2 593 / 2 600 (99,73 %) et les 7 désaccords | `desaccords_DL_vs_PharmCAT_104.csv` |
| Réseau ≠ règle : 10 / 6 322 (complets) ; 50 / 439 (partiels) | `Resultat_11_patients_et_8_couples_v15_15nov2026.md` |
| 11 patients : 32 conformes, 1 compatible, 3 erronés | **recompté ce jour** sur `s3/grille.xlsx` + `sortie_app_S3_v15.json` (patients 1, 2, 4 tacrolimus \*3/\*3 : réseau ADAPTER_DOSE, règle STANDARD, statut « à vérifier » ; patient 7 corrigé) |
| Section 8.7 (NA06991) | **analyse refaite ce jour avec l'application actuelle** (v8u rév. 3, app 5ce6a85b40b9b5b3, modèles v15) sur `zips/vcf_test/NA06991_GRCh38.vcf`, Cardiologie, 84 s ; génotypes identiques à la lecture archivée sur les 22 gènes ; 31 médicaments, 9 évalués, 22 non évalués ; scores lus à l'écran. PharmCAT SLCO1B1 = \*15/\*45 « Poor Function » lu dans `pharmcat/pc104/multi104.NA06991.phenotype.json` |
| 363 personnes GeT-RM ; critères des 104 | `Resultat_partie1_genotype_GeTRM_104_7nov2026.md` |

## 2. Figures (nouvelles, à mettre dans `fabrication/fig` et `Model_v8_7_9_10/fig`)
- `fig_8_2.png` **refaite** avec les valeurs v15 (0,2 % et 11,4 %) ; l'ancienne portait 0,1 % et 8,0 %.
- `cap8_genes.png`, `cap8_modeles.png`, `cap8_fluvastatine.png` **refaites** avec l'application actuelle (mêmes noms de fichier : elles remplacent les captures v8s).
- `cap8_warfarine.png` **nouvelle** (figure 8.6).
- `fig_8_1.png` inchangée (l'appel de génotype n'a pas changé).
- Numérotation : tableaux 8.1 à 8.7 (le tableau des désaccords réseau/PharmCAT est nouveau : 8.4 ; les anciens 8.3, 8.4, 8.5 deviennent 8.5, 8.6, 8.7). Figures 8.1 à 8.6.

## 3. Ce qui a changé par rapport au texte v6
- 8.1 : seconde limite structurelle (corrections v15 trouvées sur ces 104 personnes : non indépendant) ; critères de sélection des 104.
- 8.3 : 95,9 % au lieu de 97,8 % ; lecture complète des 136 lignes ; « Action finale de la warfarine » ; parenté recalculée.
- 8.4 : 99,73 % ; tableau des 7 désaccords ; 5/7 sous le seuil 0,9981. **La phrase « parmi les 620 unités non standard, 618 correctes » est retirée** : le chiffre équivalent v8t n'est pas dans les fichiers disponibles (script `dl_vs_pharmcat_v1.py` sur ta machine).
- 8.5 : 32/1/3 au lieu de 34/1/1 ; 11,4 % au lieu de 8,0 %. **Le « test préliminaire à 6 lignes » est retiré** : fait avec les modèles v14, non refait.
- 8.6 : inchangé, avec la mention que l'analyse porte sur les règles v14 + marqueur.
- 8.7 : refaite entièrement (warfarine désormais « adapter la dose » grâce à VKORC1 ; flucytosine : cause établie = traduction ; fluvastatine : SLCO1B1 « Poor Function » chez les trois sources).
- 8.8 : 79 textes sur 709 (au lieu de 81 sur 704) ; points 3 et 4 ajoutés.

## 4. Marqueurs restants
1. Cause de chaque désaccord GeT-RM (8.2).
2. Définition des verdicts + analyse refaite sur les règles v15 (8.6).
- Bibliographie : référence exacte GeT-RM V4 ; auteurs de l'article Kidney Int Rep 2025 (PMC12639823).

## 5. Cohérence avec les autres chapitres (à reporter)
- **Chapitre 9 v15 et résumé** : contiennent encore 97,8 %, 99,92 %, 8,0 %, « 34 conformes », « trois défauts non tous corrigés », « VKORC1 absent ». À mettre à jour (tâche 4 de la liste).
- Chapitre 5 : renvois « section 8.2 », « section 8.5 » toujours justes.

## 6. Pour la soutenance
- La baisse 97,8 → 95,9 % est un résultat défavorable apparent ; l'explication (formulation et structure, 91 lignes sans différence d'action) est vérifiable ligne par ligne dans `detail_A1`. Le seul écart de contenu systématique est le codage CYP2C9 par score d'activité.
- Les erreurs du réseau sur le tacrolimus ont changé de patients entre v14 et v15 : à dire franchement si on le demande.

## 7. Sauvegarde
WSL → Windows → GitHub → Drive (Docs › DOCs Memoire, et `fig` dans Model_v8_7_9_10).
