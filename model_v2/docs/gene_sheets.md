# Annexe A — Fiches par gene

Panel : **31 genes**
Colonnes porteuses de variance : **24**
Colonnes constantes : **7**

## Origine des phenotypes

| Origine | Genes |
|---|---|
| Extraction directe des VCF 1000 Genomes | 12 |
| PyPGx (alleles etoile precalcules) | 15 |
| Jeu de donnees initial (PharmGKB, CPIC, ClinVar, FDA) | 4 |

## Tableau de synthese

| Gene | Variant | Niveaux | % non-normal | Echelle | Constante |
|---|---|---|---|---|---|
| ABCG2 | Diplotype (alleles etoile) | 3 | 20.41 | Fonction de transport (ordinal) |  |
| ACE | rs4343 (proxy de rs1799752) | 1 | 0.0 | Code de genotype SNP (proxy insertion/deletion) | oui |
| ADRB2 | rs1042713 | 1 | 0.0 | Code de genotype SNP | oui |
| CACNA1S | Diplotype (alleles etoile) | 2 | 96.6 | Susceptibilite binaire (hyperthermie maligne) |  |
| CFTR | Diplotype (alleles etoile) | 1 | 0.0 | Reponse au traitement (binaire) | oui |
| CYP1A2 | rs762551 | 4 | 0.12 | Code de genotype SNP |  |
| CYP2A6 | rs1801272 | 3 | 0.06 | Code de genotype SNP |  |
| CYP2B6 | Diplotype (alleles etoile) | 5 | 62.56 | Score d activite |  |
| CYP2C19 | Diplotype (alleles etoile) | 5 | 69.57 | Score d activite |  |
| CYP2C9 | Diplotype (alleles etoile) | 3 | 28.9 | Score d activite |  |
| CYP2D6 | Diplotype (alleles etoile) | 5 | 51.08 | Score d activite (somme des deux alleles) |  |
| CYP3A4 | rs2740574 | 4 | 0.24 | Code de genotype SNP |  |
| CYP3A5 | Diplotype (alleles etoile) | 3 | 82.16 | Phenotype ordinal (expresseur / non-expresseur) |  |
| CYP4F2 | rs2108622 | 3 | 8.32 | Code de genotype SNP |  |
| DPYD | Diplotype (alleles etoile) | 3 | 7.46 | Score d activite |  |
| EGFR | NON_DOCUMENTE | 1 | 0.0 | NON_DOCUMENTE | oui |
| F5 | Diplotype (alleles etoile) | 2 | 1.7 | Reponse au traitement (binaire) |  |
| G6PD | rs1050828 | 3 | 1.37 | Code de genotype SNP (lie a l X) |  |
| HLA-A | NON_DOCUMENTE | 3 | 0.02 | Portage d allele a risque |  |
| HLA-B | NON_DOCUMENTE | 3 | 0.06 | Portage d allele a risque |  |
| IFNL3 | rs12979860 | 3 | 10.93 | Code de genotype SNP (CC / CT / TT) |  |
| MT-RNR1 | NON_DOCUMENTE | 1 | 0.0 | NON_DOCUMENTE | oui |
| MTHFR | rs1801133 | 1 | 0.0 | Code de genotype SNP | oui |
| NAT2 | rs1799930 | 4 | 12.26 | Code de genotype SNP (acetyleur) |  |
| NUDT15 | Diplotype (alleles etoile) | 3 | 10.25 | Phenotype ordinal |  |
| RYR1 | Diplotype (alleles etoile) | 3 | 96.61 | Susceptibilite binaire (hyperthermie maligne) |  |
| SLC19A1 | rs1051266 | 1 | 0.0 | Code de genotype SNP | oui |
| SLCO1B1 | Diplotype (alleles etoile) | 4 | 31.48 | Fonction de transport (ordinal) |  |
| TPMT | Diplotype (alleles etoile) | 3 | 11.47 | Phenotype ordinal |  |
| UGT1A1 | Diplotype (alleles etoile) | 3 | 61.87 | Phenotype ordinal |  |
| VKORC1 | rs9923231 | 3 | 11.9 | Code de genotype SNP (CC / CT / TT) |  |

## Fiches detaillees

### ABCG2

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Fonction de transport (ordinal)
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 9465 (20.41 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : acenocoumarol, allopurinol, amitriptyline, antineoplastic agents, apixaban, atazanavir, atomoxetine, atorvastatin

### ACE

- **Variant** : rs4343 (proxy de rs1799752)
- **Position (GRCh38)** : chr17:63488670
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP (proxy insertion/deletion)
- **Valeurs observees** : [np.float64(1.0)]
- **Lignes non-normales** : 0 (0.0 %)
- **Niveau CPIC** : Pas de ligne directrice CPIC niveau A
- **Medicaments associes** : AUCUN
- **Limite connue** : Le variant de reference rs1799752 est une insertion Alu de 287 pb, non representee dans un VCF de SNP. Le proxy rs4343 a ete utilise.

### ADRB2

- **Variant** : rs1042713
- **Position (GRCh38)** : chr5:148826877
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP
- **Valeurs observees** : [np.float64(1.0)]
- **Lignes non-normales** : 0 (0.0 %)
- **Niveau CPIC** : Pas de ligne directrice CPIC niveau A
- **Medicaments associes** : AUCUN

### CACNA1S

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Susceptibilite binaire (hyperthermie maligne)
- **Valeurs observees** : [np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 44796 (96.6 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : acenocoumarol, allopurinol, amitriptyline, atazanavir, atomoxetine, atorvastatin, azathioprine, bupropion
- **Limite connue** : Cohorte de sujets sains : faible variance attendue.

### CFTR

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Reponse au traitement (binaire)
- **Valeurs observees** : [np.float64(1.0)]
- **Lignes non-normales** : 0 (0.0 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : AUCUN
- **Limite connue** : Cohorte 1000 Genomes composee de sujets sains : variance quasi nulle attendue.

### CYP1A2

- **Variant** : rs762551
- **Position (GRCh38)** : chr15:74749576
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0), np.float64(2.0)]
- **Lignes non-normales** : 57 (0.12 %)
- **Niveau CPIC** : Pas de ligne directrice CPIC niveau A
- **Medicaments associes** : abrocitinib, antidepressants, antipsychotics, atomoxetine, atomoxetine hydrochloride, belzutifan, caffeine, carbamazepine

### CYP2A6

- **Variant** : rs1801272
- **Position (GRCh38)** : chr19:40848628
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 28 (0.06 %)
- **Niveau CPIC** : Pas de ligne directrice CPIC niveau A
- **Medicaments associes** : "1, "caffeine", 3-hydroxycotinine, 3-hydroxycotinine glucuronide, 7-dimethylxanthine", bupropion, caffeine, cotinine

### CYP2B6

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Score d activite
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0), np.float64(1.5), np.float64(2.0)]
- **Lignes non-normales** : 29010 (62.56 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : 3, 4-methylenedioxymethamphetamine, abrocitinib, acenocoumarol, allopurinol, amitriptyline, artemether, atazanavir

### CYP2C19

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Score d activite
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0), np.float64(1.5), np.float64(2.0)]
- **Lignes non-normales** : 32259 (69.57 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : 3, 4-hydroxybupropion, 4-hydroxytamoxifen, 4-methylenedioxymethamphetamine, 7-carboxycannabidiol, 7-hydroxycannabidiol, abrocitinib, acenocoumarol

### CYP2C9

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Score d activite
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 13399 (28.9 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : 4-hydroxytamoxifen, abrocitinib, aceclofenac, acenocoumarol, allopurinol, amitriptyline, anastrozole, apatinib

### CYP2D6

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Score d activite (somme des deux alleles)
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0), np.float64(1.5), np.float64(2.0)]
- **Lignes non-normales** : 23688 (51.08 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : 3, 4-hydroxytamoxifen, 4-methylenedioxymethamphetamine, 6-orthoquinone, abrocitinib, acebutolol, acenocoumarol, allopurinol
- **Limite connue** : Non appelable depuis un VCF de SNP et d indels : variation structurale et nombre de copies. Phenotype fourni par PyPGx.

### CYP3A4

- **Variant** : rs2740574
- **Position (GRCh38)** : chr7:99784473
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0), np.float64(1.5)]
- **Lignes non-normales** : 111 (0.24 %)
- **Niveau CPIC** : Pas de ligne directrice CPIC niveau A
- **Medicaments associes** : 1-hydroxymidazolam, 2-hydroxyatorvastatin, 4-hydroxytamoxifen, abrocitinib, alectinib, alprazolam, amlodipine, anastrozole

### CYP3A5

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Phenotype ordinal (expresseur / non-expresseur)
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 38098 (82.16 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : 3, 4-dehydrocilostazol, 4-hydroxycyclophosphamide, 7-carboxycannabidiol, acenocoumarol, allopurinol, amitriptyline, amlodipine

### CYP4F2

- **Variant** : rs2108622
- **Position (GRCh38)** : chr19:15879621
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 3856 (8.32 %)
- **Niveau CPIC** : CPIC niveau A — warfarine (2017)
- **Medicaments associes** : acenocoumarol, apixaban, aspirin, chloroquine, clopidogrel, dapsone, hydralazine, isoniazid

### DPYD

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Score d activite
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 3461 (7.46 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : 3-aminoisobutyrate, acenocoumarol, allopurinol, amitriptyline, atazanavir, atomoxetine, atorvastatin, azathioprine

### EGFR

- **Variant** : NON_DOCUMENTE
- **Position (GRCh38)** : NON_DOCUMENTE
- **Origine du phenotype** : Jeu de donnees initial (PharmGKB / CPIC / ClinVar / FDA)
- **Echelle numerique** : NON_DOCUMENTE
- **Valeurs observees** : [np.float64(1.0)]
- **Lignes non-normales** : 0 (0.0 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : AUCUN
- **Limite connue** : Variants pharmacogenomiques somatiques, caracterises dans le tissu tumoral. Absents d un VCF germinal. Colonne constante.

### F5

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Reponse au traitement (binaire)
- **Valeurs observees** : [np.float64(0.0), np.float64(1.0)]
- **Lignes non-normales** : 789 (1.7 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : acenocoumarol, allopurinol, amitriptyline, atazanavir, atomoxetine, atorvastatin, azathioprine, bupropion

### G6PD

- **Variant** : rs1050828
- **Position (GRCh38)** : chrX:154536002
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP (lie a l X)
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 635 (1.37 %)
- **Niveau CPIC** : CPIC niveau A — deficit en G6PD (2022)
- **Medicaments associes** : acenocoumarol, chloroquine, chlorpropamide, dabrafenib, dapsone, daunorubicin, gliclazide, glimepiride
- **Limite connue** : Gene porte par le chromosome X. Les genotypes hemizygotes masculins ne sont pas traites specifiquement dans l encodage actuel.

### HLA-A

- **Variant** : NON_DOCUMENTE
- **Position (GRCh38)** : NON_DOCUMENTE
- **Origine du phenotype** : Jeu de donnees initial (PharmGKB / CPIC / ClinVar / FDA)
- **Echelle numerique** : Portage d allele a risque
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 8 (0.02 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : bcr-abl tyrosine kinase inhibitors, carbamazepine, oxcarbazepine, peginterferon alfa-2a, peginterferon alfa-2b, ribavirin, tebentafusp
- **Limite connue** : Non appelable depuis un VCF. Typage HLA requis. Quasi constant dans le jeu de donnees.

### HLA-B

- **Variant** : NON_DOCUMENTE
- **Position (GRCh38)** : NON_DOCUMENTE
- **Origine du phenotype** : Jeu de donnees initial (PharmGKB / CPIC / ClinVar / FDA)
- **Echelle numerique** : Portage d allele a risque
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 26 (0.06 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : "interferon alfa-2a, "ribavirin", abacavir, allopurinol, bcr-abl tyrosine kinase inhibitors, carbamazepine, etanercept, flucloxacillin
- **Limite connue** : Non appelable depuis un VCF. Typage HLA requis. Quasi constant dans le jeu de donnees.

### IFNL3

- **Variant** : rs12979860
- **Position (GRCh38)** : chr19:39248147
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP (CC / CT / TT)
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 5070 (10.93 %)
- **Niveau CPIC** : CPIC — interferon / ribavirine
- **Medicaments associes** : acenocoumarol, chloroquine, dapsone, hydralazine, isoniazid, nitrofurantoin, phenprocoumon, primaquine

### MT-RNR1

- **Variant** : NON_DOCUMENTE
- **Position (GRCh38)** : NON_DOCUMENTE
- **Origine du phenotype** : Jeu de donnees initial (PharmGKB / CPIC / ClinVar / FDA)
- **Echelle numerique** : NON_DOCUMENTE
- **Valeurs observees** : [np.float64(1.0)]
- **Lignes non-normales** : 0 (0.0 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : AUCUN
- **Limite connue** : Gene mitochondrial, hors perimetre d un VCF nucleaire standard. Colonne constante.

### MTHFR

- **Variant** : rs1801133
- **Position (GRCh38)** : chr1:11796321
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP
- **Valeurs observees** : [np.float64(1.0)]
- **Lignes non-normales** : 0 (0.0 %)
- **Niveau CPIC** : Pas de ligne directrice CPIC niveau A
- **Medicaments associes** : AUCUN

### NAT2

- **Variant** : rs1799930
- **Position (GRCh38)** : chr8:18400593
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP (acetyleur)
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0), np.float64(1.5)]
- **Lignes non-normales** : 5684 (12.26 %)
- **Niveau CPIC** : CPIC — hydralazine
- **Medicaments associes** : acenocoumarol, acetylisoniazid, caffeine, chloroquine, dapsone, dipyrone, hydralazine, iguratimod

### NUDT15

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Phenotype ordinal
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 4753 (10.25 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : acenocoumarol, acyclovir, allopurinol, amitriptyline, atazanavir, atomoxetine, atorvastatin, azathioprine

### RYR1

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Susceptibilite binaire (hyperthermie maligne)
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 44800 (96.61 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : acenocoumarol, allopurinol, amitriptyline, anesthesiques, atazanavir, atomoxetine, atorvastatin, azathioprine
- **Limite connue** : Cohorte de sujets sains : faible variance attendue.

### SLC19A1

- **Variant** : rs1051266
- **Position (GRCh38)** : chr21:45537880
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP
- **Valeurs observees** : [np.float64(1.0)]
- **Lignes non-normales** : 0 (0.0 %)
- **Niveau CPIC** : Pas de ligne directrice CPIC niveau A
- **Medicaments associes** : AUCUN

### SLCO1B1

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Fonction de transport (ordinal)
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0), np.float64(1.5)]
- **Lignes non-normales** : 14596 (31.48 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : 2-hydroxyatorvastatin, 2-hydroxyatorvastatin lactone, 4-hydroxyatorvastatin, 4-hydroxyatorvastatin lactone, acenocoumarol, allopurinol, amitriptyline, amprenavir

### TPMT

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Phenotype ordinal
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 5319 (11.47 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : acenocoumarol, allopurinol, amitriptyline, atazanavir, atomoxetine, atorvastatin, azathioprine, azathioprine sodium

### UGT1A1

- **Variant** : Diplotype (alleles etoile)
- **Position (GRCh38)** : NON_APPLICABLE
- **Origine du phenotype** : PyPGx — Sherman, Claw & Lee, Sci Rep 2024
- **Echelle numerique** : Phenotype ordinal
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 28688 (61.87 %)
- **Niveau CPIC** : NON_DOCUMENTE
- **Medicaments associes** : 2-hydroxyatorvastatin lactone, 4-hydroxyatorvastatin lactone, abrocitinib, acenocoumarol, allopurinol, amitriptyline, atazanavir, atazanavir / ritonavir

### VKORC1

- **Variant** : rs9923231
- **Position (GRCh38)** : chr16:31096368
- **Origine du phenotype** : Extraction directe des VCF 1000 Genomes (plages d octets HTTP)
- **Echelle numerique** : Code de genotype SNP (CC / CT / TT)
- **Valeurs observees** : [np.float64(0.0), np.float64(0.5), np.float64(1.0)]
- **Lignes non-normales** : 5516 (11.9 %)
- **Niveau CPIC** : CPIC niveau A — warfarine (2017)
- **Medicaments associes** : acenocoumarol, chloroquine, dapsone, fluindione, hydralazine, isoniazid, nitrofurantoin, phenprocoumon

## Heterogeneite des echelles

Les colonnes du panel ne partagent pas une echelle commune. Trois natures coexistent :

1. **Scores d activite** — somme des contributions fonctionnelles des deux alleles 
(CYP2D6, CYP2C19, CYP2B6, CYP2C9, DPYD). Grandeur additive et ordonnee.
2. **Phenotypes ordinaux** — categories de fonction enzymatique ou de transport 
(TPMT, NUDT15, SLCO1B1, UGT1A1, ABCG2, CYP3A5).
3. **Codes de genotype SNP** — encodage du genotype a un locus unique 
(VKORC1, IFNL3, CYP4F2, G6PD, NAT2 et les genes extraits des VCF). 
La valeur 0,5 y designe un heterozygote, non une demi-activite.

Une normalisation commune appliquee a l ensemble des colonnes suppose implicitement 
que ces echelles sont commensurables. Cette hypothese est fausse et constitue une 
limite methodologique documentee du travail.