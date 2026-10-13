# P1 — Lecteur de VCF : résultats des tests (12 oct 2026)

Statut : **tests exécutés et vérifiés** (sorties lues, concordance recalculée). Rien n'est encore intégré à l'application.

## 1. Outils et versions
- PyPGx 0.27.0 (`run-chip-pipeline`, GRCh38, bundle `sbslee/pypgx-bundle` 0.27.0). Nécessite pandas < 3 (pandas 3.0 provoque une erreur dans `call-genotypes`) ; installé dans un environnement isolé.
- PharmCAT v3.0.0 (jar, sha256 e4b168d8…9482f), lancé sur les VCF avec Java.
- Parseur local `vcf_parser.py` (4 814 octets), lu et exécuté.

## 2. Fichiers de test
patient_dpyd.vcf, patient_multi_gene.vcf, patient_sans_mutation.vcf, pharmacat.example2.vcf (Drive), plus 2 VCF diagnostiques construits pour l'occasion (t_diag_complet, t_diag_un_seul).

## 3. Résultats

### 3.1 pharmacat.example2.vcf (VCF réel d'exemple de PharmCAT, GRCh38, 1 207 lignes)
| Gène | PharmCAT | PyPGx | Parseur local (+ règle génotype→valeur) |
|---|---|---|---|
| CYP2C19 | *2/*2 (PM) | *2/*2 (PM) | 3 variants, 1/1 → PM |
| CYP2B6 | *1/*6 (IM) | *1/*6 (IM) | 2 variants 0/1 → IM |
| DPYD | Reference/Reference (NM) | idem | rien → normal |
| TPMT, SLCO1B1, UGT1A1, CYP2C9, CYP3A5 | *1/*1 | *1/*1 | rien → normal |

Concordance PharmCAT / PyPGx : **8 gènes sur 8** identiques. CYP2D6 : PharmCAT « Unknown/Unknown » (non appelable depuis un VCF de SNP).
Le parseur local ne lit que 5 variants (2 gènes) sur 1 207 lignes et ne produit ni diplotype ni allèle étoile. Il compte aussi comme « mutation » rs3758581 (1/1), que PyPGx range dans l'haplotype *1 (fonction normale).

### 3.2 VCF synthétiques minimaux
| Fichier | Parseur local | PyPGx | PharmCAT |
|---|---|---|---|
| patient_dpyd (rs3918290 1/1) | DPYD 1/1 → PM | Reference/Reference (NM) | Unknown/Unknown |
| patient_multi_gene (CYP2C19 1/1, DPYD 0/1, gène inconnu) | 3 variants dont « UNKNOWNGENE » | CYP2C19 *38/*38 (NM), DPYD Ref/Ref | CYP2C19 *2/*2 (PM), reste Unknown |
| patient_sans_mutation (0/0) | 0 variant | CYP2C19 *38/*38, CYP2B6 *1/*1 | CYP2C19 *1/*1 ou *1/*38, CYP2B6 *1/*1 |

Causes identifiées (vérifiées dans `pypgx/api/data/variant-table.csv`) :
1. **Builds mélangés dans les fichiers de test.** rs3918290 est à chr1:97915614 en GRCh37 et chr1:97450058 en GRCh38. Les deux VCF DPYD utilisent la position GRCh37, les autres rsID sont en GRCh38. PyPGx et PharmCAT, qui lisent la position, ne reconnaissent donc pas la variante. Le parseur local, qui ignore la position, l'accepte quand même.
2. **VCF épars.** Pour CYP2C19, PyPGx définit *2 par 2 variants (rs12769205 + rs4244285). Avec rs4244285 seul, il renvoie *38/*38 (normal) ; PharmCAT renvoie *2/*2. Avec les 2 variants (t_diag_complet), les deux outils donnent *2/*2. Avec DPYD à la position GRCh38 (0/1), PyPGx donne Reference/*2A (IM) et PharmCAT *2A hétérozygote (IM, score 1.0).

### 3.3 Gène absent du VCF : les deux outils divergent
- PharmCAT : « Unknown/Unknown — No Result » (absent = non déterminé).
- PyPGx : traite l'absence comme référence (ex. DPYD Reference/Reference sur t_diag_un_seul, chr1 déclaré sans enregistrement) ; si le chromosome du gène n'existe pas dans l'index du VCF, il s'arrête (`invalid contig`).
→ La convention « gène absent = référence (normal) » prévue au plan n'est **pas** confirmée par PharmCAT. À trancher (voir §5).

### 3.4 Corpus et empreintes (fichiers reçus)
- 46 371 lignes, 31 gènes, 530 médicaments, 11 701 échantillons. Classes : ADAPTER_DOSE 23 516, EVITER 13 202, SURVEILLER 9 025, **STANDARD 628 (1,4 %)**.
- Origines (préfixe sample_id) : HG 27 734 lignes (1 070 échantillons, 50 médicaments), NA 8 315 (309, 50), **DOC 10 322 (une ligne par « échantillon », 529 médicaments)**. **Les 628 STANDARD proviennent tous de DOC** ; aucune ligne 1KGP n'est STANDARD.
- 529 lignes ont les 31 gènes à 1.0 ; 508 sont STANDARD, 14 EVITER, 4 ADAPTER_DOSE, 3 SURVEILLER.
- 7 gènes sont toujours à 1.0 (ADRB2, CFTR, ACE, MTHFR, MT-RNR1, EGFR, SLC19A1) : aucune information.
- **RYR1 et CACNA1S valent 0.5 dans presque toutes les lignes** (RYR1 ≠ 1.0 : 44 800 lignes sur 46 371). Cause non vérifiée (probable artefact de profil) ; à examiner avant l'entraînement.
- Empreintes : 437 médicaments. Sans empreinte : 93 « médicaments » mais seulement **254 lignes (0,55 %)**. Ces 93 noms contiennent surtout des classes (antidepressants, proton pump inhibitors…), des métabolites, des biologiques et des noms cassés par la lecture du CSV (`"1`, `7-dimethylxanthine"`, `"caffeine"`, `3`), avec une quinzaine de vraies petites molécules (amoxicillin, cilostazol, donepezil, sorafenib, oxaliplatin…). Correction du chiffre donné plus tôt : ce n'est pas un quart du corpus mais une poignée de lignes.
- Le fichier qui a construit les profils 1KGP (valeurs 0/0.5/1/1.5/2 à partir de PyPGx) n'est pas parmi les fichiers reçus : la règle exacte phénotype → valeur reste **non vérifiée**.

## 4. Conséquences pour la conception
1. Le lecteur ne peut pas reposer sur les étiquettes `PX=`/`GENE=`/`ANN=` ni sur une table de ~50 rsID : il faut un appel d'allèles étoiles (PyPGx, concordant à 8/8 avec PharmCAT sur un VCF réel).
2. Contrôler l'assemblage (GRCh37/38) avant tout appel ; refuser ou convertir si incohérent.
3. Distinguer trois états par gène : appelé / référence prouvée par des 0/0 ou une région couverte / non déterminé. Le dernier alimente l'indicateur d'absence en entrée du modèle.
4. Les VCF de test doivent être refaits en GRCh38 avec toutes les positions définissantes (ou provenir de PharmCAT/1KGP/GeT-RM).
5. Nettoyer le corpus (noms de médicaments cassés, classes et métabolites) et examiner RYR1/CACNA1S avant le corpus v3.

## 5. Décisions à valider
- Convention gène absent : (a) référence si le gène est couvert par des 0/0, sinon « non déterminé » (recommandée) ; (b) PyPGx seul ; (c) PharmCAT seul. Détail à confirmer par toi.
- Outil principal à l'inférence : PyPGx (cohérent avec les profils d'entraînement) avec PharmCAT en contrôle ; PharmCAT gère mieux les VCF épars.

## Journal de Bord (extrait)
1) Décisions validées : spec écran (1 à 4 médicaments classés, profil combiné), PyPGx + PharmCAT comme comparateur, sauvegarde 4 supports.
2) Erreurs à ne plus reproduire : annoncer « 93 médicaments sans empreinte » comme un quart du corpus (c'est 0,55 % des lignes) ; supposer le build des VCF de test sans vérifier ; poser « absent = référence » avant test.
3) Reste à faire : valider la convention d'absence ; P2 tables spécialité↔ATC et alternatives ; P3 corpus v3 (labels règles v2, nettoyage, RYR1/CACNA1S) ; P4 entraînement séquentiel ; P5 couche de recommandation ; P6 application v5 ; P7 tests de bout en bout, chapitres 4–8.
