# Couverture moleculaire du dataset v2

Medicaments distincts : **530**
Avec Morgan Fingerprint : **437** (82.5 %)
Lignes couvertes : **46117 / 46371** (99.5 %)

## Repartition par statut

| Statut | Medicaments | Lignes |
|---|---|---|
| OK_FINGERPRINT | 437 | 46117 |
| PETITE_MOLECULE_MANQUANTE | 21 | 52 |
| CLASSE_THERAPEUTIQUE | 20 | 49 |
| METABOLITE_SANS_FP | 20 | 46 |
| BIOLOGIQUE | 13 | 62 |
| COMBINAISON | 10 | 20 |
| PARSING_ERROR | 8 | 19 |
| FORME_GALENIQUE | 1 | 6 |

## Interpretation

Les 93 medicaments sans fingerprint ne constituent pas une lacune homogene. Quatre situations distinctes :

1. **Classes therapeutiques** — un nom de classe ne correspond a aucune structure chimique unique. Exclusion methodologiquement justifiee.
2. **Biologiques** — les Morgan Fingerprints encodent les sous-structures de petites molecules. Proteines, anticorps et polymeres sont hors du perimetre de la methode.
3. **Erreurs de parsing** — fragments produits par des virgules non protegees dans le fichier source (ex. 1,3,7-trimethylxanthine scinde en trois entrees). Defaut technique identifie, corrigeable.
4. **Metabolites** — produits de transformation d une molecule mere (ex. cotinine pour la nicotine, losartan E-3174 pour le losartan). Leur structure existe mais n a pas ete recuperee lors de la construction du referentiel. Molecules chimiquement distinctes de leur molecule mere : elles ne doivent pas etre fusionnees avec elle.
5. **Petites molecules manquantes** — lacune reelle. Structures disponibles sur PubChem, fingerprints recuperables.

## Formes salines

25 groupes ou une molecule apparait sous forme libre et sous forme saline 
(ex. warfarin / warfarin sodium). Ces paires designent le meme principe actif et pourraient etre fusionnees.
Fusion non appliquee a ce stade : elle modifierait les profils et invaliderait les resultats de validation croisee.

## Metabolites — distinction importante

Les entrees prefixees nor-, N-des-, O-des-, R-, S-, hydroxy- designent des **metabolites**, 
molecules chimiquement distinctes de la molecule mere. Elles ne doivent pas etre fusionnees.
Le dataset en contient 34.

## Impact sur les resultats

Les modeles sont entraines sur les 46117 lignes disposant d un fingerprint, 
soit 99.5 % du dataset. Les entrees non couvertes sont exclues 
en amont et n influencent aucune metrique rapportee.