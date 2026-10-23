# Couverture des médicaments : état au 23 octobre 2026

Mesuré avec le registre `registre_medicaments_v1.csv` (16 oct., 1 126 médicaments, 8 sources croisées) et `data/corpus_v7_couverture_par_medicament.csv`.

## Chiffres
- 208 médicaments ont une directive publiée dans ClinPGx (CPIC, DPWG, RNPGx, CPNDS, CFF...).
- 117 sont dans le corpus v7 (règles extraites de CPIC et DPWG seulement : 408 règles à un gène, 81 à plusieurs gènes).
- 91 ne sont PAS dans le corpus v7 : 80 « directive sans règle extraite », 11 « règles exclues ».
- Dans le modèle actuel : 113 médicaments, dont 58 seulement avec une vraie réponse du DL (au moins 2 actions différentes vues à l'entraînement, dépendent du génotype).
- Hors directive : 226 médicaments avec une étiquette réglementaire (FDA) liée à un gène suivi, 23 avec une association de niveau 2B ou mieux (non utilisés pour l'instant).

## Les 91 médicaments à ajouter, par difficulté
A. Tous les gènes déjà dans le modèle : 40 médicaments (faisable en premier, y compris prasugrel et ticagrelor, les alternatives au clopidogrel) :
aceclofenac, acenocoumarol, amiodarone, antidepressants, chlorpropamide, cisplatin, clonidine, dabrafenib, dipyrone, disopyramide, flucytosine, fluindione, flupenthixol, gliclazide, glimepiride, glipizide, hmg-coa reductase inhibitors, indomethacin, ivacaftor, lumiracoxib, mesalazine, mirtazapine, moclobemide, moxifloxacin, nabumetone, naproxen, nicorandil, nitrofurazone, paclitaxel, phenprocoumon, prasugrel, probenecid, quinacrine, quinidine, rabeprazole, sodium nitrate, sulfacetamide, ticagrelor, tolazamide, trametinib

B. Gènes déjà dans le fichier de profils mais pas dans le modèle (MT-RNR1, RYR1, CACNA1S, HLA-B, CYP1A2...) : 27 médicaments :
amikacin, clozapine, desflurane, dibekacin, enflurane, flucloxacillin, folic acid, gentamicin, halothane, isoflurane, kanamycin, lamotrigine, methoxyflurane, neomycin, netilmicin, olanzapine, paromomycin, peginterferon alfa-2a, peginterferon alfa-2b, plazomicin, ribavirin, ribostamycin, sevoflurane, streptomycin, succinylcholine, tebentafusp, tobramycin

C. Au moins un gène sans données de profil (COMT, OPRM1, ADRB1, CYP2C8, HTR2A, SLC6A4...) : 24 médicaments :
alfentanil, atenolol, buprenorphine, daunorubicin, desvenlafaxine, diclofenac, duloxetine, esmolol, fentanyl, hydromorphone, labetalol, levomethadone, levomilnacipran, methotrexate, methylphenidate, milnacipran, morphine, nadolol, naltrexone, pindolol, remifentanil, sotalol, sufentanil, vilazodone

Certaines lignes sont des classes et non des médicaments (ex. « antidepressants », « hmg-coa reductase inhibitors ») : à traiter à part.

## Ce que cela ne règle pas
- Plus de médicaments = plus de couverture, pas une preuve clinique : les étiquettes viennent toujours des directives.
- Chaque règle doit être lue avant d'être extraite (une directive peut dire « pas de recommandation »).
- Les 59 règles « ambiguës » (35 médicaments) déjà écartées restent un trou : sans elles, warfarine et citalopram n'ont aucune réponse variable.
- Le jeu final (138 profils) ne change pas ; les nouveaux médicaments sont étiquetés sur les mêmes profils et restent hors apprentissage pour ces 138 profils.
