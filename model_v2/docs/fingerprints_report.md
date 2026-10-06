# Empreintes moleculaires — recalcul

## Constat initial

Les fichiers `drug_fingerprints.pkl` et `drug_fp_ref.pkl` contenaient, pour chacun des
437 medicaments, un vecteur de 518 variables dont les 512 premieres etaient nulles sans
exception. Les empreintes de Morgan n ont donc contribue a aucune prediction des modeles
entraines jusque-la : seuls les six descripteurs physico-chimiques finaux portaient de
l information moleculaire.

Le script ayant produit ces fichiers n avait pas ete conserve, et les structures SMILES
n avaient pas ete sauvegardees — ce qui a empeche un diagnostic plus precoce.

## Methode de recalcul

| Parametre | Valeur |
|---|---|
| Source des structures | PubChem PUG REST, interrogation par nom |
| Bibliotheque | RDKit 2026.03.6 |
| Type d empreinte | Morgan (circulaire), rayon 2 |
| Longueur | 512 bits |
| Descripteurs conserves | MW, LogP, HBD, HBA, RB, TPSA |
| Dimension totale | 518 |

Les structures recuperees sont enregistrees dans `drug_smiles.csv` avec leur identifiant
PubChem, ce qui rend le calcul reproductible et verifiable.

## Couverture obtenue

| | Nombre |
|---|---|
| Medicaments traites | 437 |
| Empreintes calculees | 402 |
| Introuvables sur PubChem | 35 |
| Non lisibles par RDKit | 0 |

## Verification

| Indicateur | Avant | Apres |
|---|---|---|
| Empreintes entierement nulles | 437 | 0 |
| Bits actifs en moyenne | 0,0 | 43.1 |
| Bits jamais actifs | 512 | 0 |

## Portee

Les resultats obtenus avec les empreintes nulles restent valides comme mesure de ce que
les modeles realisent a partir des seuls descripteurs globaux. L ecart entre ces resultats
et ceux obtenus apres recalcul mesure directement l apport de la representation structurale
du medicament — question de recherche RQ4.

## Medicaments introuvables

Ces entrees n ont pas de correspondance dans PubChem par recherche nominale. Elles
relevent pour la plupart des categories deja documentees dans le dictionnaire des
medicaments : classes therapeutiques, biologiques, combinaisons.

- atazanavir
- atomoxetine hydrochloride
- dexamethasone
- dexlansoprazole
- dexmedetomidine
- diclofenac
- dimercaprol
- esomeprazole sodium
- exemestane
- ibrutinib
- iguratimod
- levomethadone
- lisdexamfetamine
- lopinavir
- methadone
- methazolamide
- metoclopramide
- metoprolol
- metronidazole
- midazolam
- mirtazapine
- nebivolol
- nevirapine
- nimodipine
- nortriptyline
- ondansetron
- ondansetron hydrochloride
- opioids
- oxcarbazepine
- pantoprazole
- pantoprazole sodium
- paramethoxymethamphetamine
- paroxetine
- paroxetine hydrochloride hemihydrate
- phenytoin sodium