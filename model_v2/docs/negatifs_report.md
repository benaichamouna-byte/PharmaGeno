# Paires sans association documentee

## Motif

Le modele entraine sur le corpus precedent ne sait pas repondre qu un medicament ne
concerne pas un patient donne. Interroge sur les 437 medicaments du referentiel pour
un patient ne presentant que deux genes mutes, il en classe 326 en contre-indication,
avec des niveaux de confiance parfois superieurs a ceux des medicaments reellement
concernes.

La cause est l absence de contre-exemples : la classe STANDARD ne representait que
520 lignes sur 46117, soit 1.1 %. Le reseau n a jamais appris a reconnaitre
une absence de lien.

## Source des associations

Les 386 paires gene-medicament documentees proviennent des 217 fichiers
d annotation de guidelines presents dans le projet.

| Source | Paires |
|---|---|
| CPIC | 315 |
| DPWG | 111 |
| RNPGx | 31 |
| CPNDS | 13 |
| AIOM | 4 |
| SEFF/SEOM | 3 |
| ACR | 1 |
| CFF | 1 |
| AusNZ | 1 |
| AHA | 1 |

Couverture : 41 genes, 208 medicaments.

## Methode

Pour chaque profil genetique du corpus, les genes non normaux sont identifies.
Les medicaments associes a l un d eux dans la table documentee sont exclus.
Parmi les medicaments restants, 3 sont tires au hasard et etiquetes STANDARD.

Le tirage est reproductible — graine fixee a 42.

Ces paires ne sont pas inventees. Un patient porteur d une seule deficience CYP2C19
ne requiert aucun ajustement pour la metformine : c est un fait clinique etabli, que
le corpus initial ne contenait simplement pas.

## Resultat

| Action | Avant | Apres | Part finale |
|---|---|---|---|
| ADAPTER_DOSE | 23454 | 23454 | 41.1 % |
| EVITER | 13120 | 13120 | 23.0 % |
| SURVEILLER | 9023 | 9023 | 15.8 % |
| STANDARD | 520 | 11456 | 20.1 % |

Corpus : 46117 vers 57053 lignes.
Lignes ajoutees : 10936.

SHA256 : `3c04b5cc66edcf3c2e43d63c2695466514e457303ca0b956d7c6b694ef5ddfb4`

## Limite

L absence d association repose sur les guidelines CPIC et DPWG disponibles. Une paire
non documentee n est pas necessairement sans interaction : elle peut relever d une
association non encore etablie. Le modele apprend donc l etat des connaissances
publiees, non une verite biologique.