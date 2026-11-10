# Résultat — Validation externe des recommandations par les études publiées (8 novembre 2026)

Statut : calcul terminé et relu (partiellement). Paquet : `validation_externe_v1_1_8nov2026.zip`. Protocole figé avant calcul (empreintes dans `EMPREINTES_PROTOCOLE_v1.txt`), amendement 1 daté (décidé après avoir vu les résultats v1).

## Ce qui a été comparé
Les 285 règles d'alerte de l'application (EVITER 96, ADAPTER_DOSE 131, SURVEILLER 58 ; 152 couples gène–médicament ; 249 combinaisons uniques gène–médicament–état–alerte) contre les annotations d'études de ClinPGx (octobre 2026) : `var_drug_ann` + `var_pheno_ann`, 27 590 lignes, avec les résultats nuls. Aucun des 83 articles de guides CPIC/DPWG cités dans ClinPGx n'apparaît dans ces annotations (vérifié).
Correction d'une erreur de départ : le fichier CSV du projet (6 063 lignes) ne gardait que les associations significatives et omettait les études de toxicité. Les chiffres de couverture annoncés avant (76 couples, 163 règles) venaient de ce fichier filtré et sont remplacés par ceux-ci.

## Résultats (verdict final après relecture, 285 règles)
| Alerte | n | Soutenue | Mixte (pour et contre) | Non soutenue (nuls seuls) | Signal non orienté | Non tranchable | Études non appariées auto | Aucune étude |
|---|---|---|---|---|---|---|---|---|
| EVITER | 96 | 22 | 20 | 5 | 18 | 2 | 22 | 7 |
| ADAPTER_DOSE | 131 | 19 | 41 | 18 | 13 | 0 | 26 | 14 |
| SURVEILLER | 58 | 3 | 2 | 0 | 1 | 0 | 3 | 49 |
| Total | 285 | 44 | 63 | 23 | 32 | 2 | 51 | 70 |

- Au moins une étude concordante (soutenue ou mixte) : 107 règles sur 285 (38 %) ; seulement des résultats nuls : 23 (8 %) ; aucune étude : 70 (25 %, dont 49 alertes SURVEILLER).
- Pour 122 règles ayant au moins une étude concordante ou « contre », la part de PMID concordants a pour médiane 0,80 (quartiles 0,33 et 1,00) : indicateur descriptif décidé après coup (amendement 1).
- Seulement 13 lignes d'études vont franchement en sens opposé de façon significative (dans l'appariement v1.1) ; l'essentiel du « contre » est constitué de résultats nuls (499 lignes pertinentes), souvent sur des groupes mélangés ou de petite taille.
- Couples gène–médicament avec au moins une ligne d'étude (nom de médicament identique) : 109 sur 152.
- Par source de la règle : CPIC 136 règles sur 138 ont des lignes (76 soutenues ou mixtes) ; DPWG 55 sur 57 (27) ; FDA 14 sur 31 (3) ; étiquettes FDA 1 sur 48 (0) ; EMA 0 sur 2 ; HCSC 3 sur 3 (1) ; RNPGx 6 sur 6 (0).

## Exemples vérifiés (décomptes recalculés depuis les fichiers bruts, PMID distincts)
- HLA-B*15:02 et carbamazépine : 42 PMID positifs (toxicité accrue). Pour les seuls effets SJS/NET/réactions cutanées sévères : 41 positifs contre 4 nuls ; les autres nuls portent sur d'autres effets (DRESS, exanthème, sous-groupes).
- HLA-B*58:01 et allopurinol : 28 positifs, dont 28 contre 3 nuls sur SJS/NET/RCS. HLA-B*57:01 et abacavir : 9 positifs, 0 nul. HLA-A*31:01 et carbamazépine : 17 positifs, 7 nuls (RCS : 9 contre 6 : association moins nette).
- HLA-B*15:02 et phénytoïne : 10 positifs, 7 à 9 nuls : preuves partagées.
- CYP2C9 et warfarine (dose) : environ 90 à 100 PMID concordants contre 8 nuls ou discordants.
- CYP3A5 et tacrolimus (dose, décompte assisté par expressions régulières) : 48 PMID concordants, 0 discordant, 9 nuls.
- CYP2D6 et tamoxifène (alerte éviter, métaboliseur lent) : la méthode automatique donnait un verdict trompeur. Lecture des phrases : 12 PMID de survie ou de récidive défavorables aux porteurs (critères non orientés par le protocole), 2 PMID en sens inverse, 2 PMID nuls sur la réponse au traitement, plusieurs nuls de tolérance. Verdict final : mixte, avec une majorité de preuves de survie ou de récidive dans le sens de l'alerte.
- CYP2C19 et voriconazole (lent) : 4 PMID nuls sur la toxicité, 22 PMID montrant une exposition accrue (PK non orientée car la règle n'a pas de sens de dose).
- G6PD (déficient) : preuves surtout cliniques (signification non indiquée par ClinPGx) : rasburicase 26 PMID de cas + 1 positif vs 1 nul ; bleu de méthylène 17 vs 2 nuls ; dapsone 5 ; pégloticase 2 ; primaquine mixte ; nitrofurantoïne 4.

## Qualité de la méthode
- Relecture : toutes les règles uniques « mixtes » ou « non soutenues » (76 combinaisons), les règles G6PD, les règles HLA, plus 30 règles tirées au hasard (graine 20261108) dont 11 non mixtes. Dans l'échantillon aléatoire, le verdict automatique a dû être ajusté pour 4 règles sur 30 (13 %, IC 95 % de Wilson 5 à 30 %). Sur l'ensemble : 87 règles confirmées, 20 ajustées, 178 non relues (70 sans étude, 30 signaux non orientés, 51 non appariées, 27 soutenues hors échantillon).
- Un seul lecteur (moi) ; pas de second relecteur humain. À faire valider par le pharmacologue sur au moins les alertes EVITER.
- Deux corrections décidées après avoir vu les résultats v1 : (A1) un hétérozygote « sans fonction + normal » est classé IM, plus apparié aux règles métaboliseurs lents ; (A2) sens de dose de chaque règle lu à la main sur son seul texte. Les sorties v1 et v1.1 sont conservées.

## Limites
- ClinPGx est une base curée de littérature, sujette au biais de publication ; association n'est pas bénéfice clinique ; la taille des études n'est pas pondérée (un petit résultat nul compte autant qu'une grande étude positive).
- « Efficacité diminuée » compte comme concordant pour toute alerte, même si l'alerte repose sur la toxicité (biais en faveur du soutien).
- Pour les règles sans sens de dose, la pharmacocinétique n'est pas orientée (18 alertes EVITER sont classées « signal non orienté » ; pour le tamoxifène, la relecture a montré que ce classement masque des preuves de survie et de récidive dans le sens de l'alerte).
- Noms de médicaments appariés exactement : couverture sous-estimée (sels, métabolites, synonymes non rapprochés).
- Pas de distinction fine lent/intermédiaire quand l'étude ne la fait pas.
- Gènes F5 et CYP3A5, G6PD : pas de classification automatique ; lecture manuelle partielle ; F5 sans étude dans ClinPGx pour les médicaments concernés.
- Les 51 règles « études présentes non appariées » et les 70 « aucune étude » ne sont pas évaluées par cette méthode ; elles ne sont ni validées ni invalidées.
- Les alertes issues des étiquettes FDA/EMA (54) ont presque aucune étude dans ClinPGx : leur validité reste à établir par un autre moyen.
- Les connaissances de fond de ClinPGx et des guides se recoupent : ce n'est pas une indépendance totale des preuves, mais les articles de guides eux-mêmes ne sont pas utilisés.

## Texte proposé pour le mémoire (à relire, chiffres à reprendre du tableau)
« Les 285 règles d'alerte de l'application ont été comparées aux annotations d'études publiées de ClinPGx (27 590 lignes, octobre 2026), en incluant les résultats non significatifs. Les règles d'appariement ont été figées avant le calcul ; deux corrections datées ont été apportées ensuite. Pour 107 règles (38 %), au moins une étude concordante a été retrouvée ; pour 23 règles (8 %), seuls des résultats nuls étaient disponibles ; pour 70 règles (25 %), dont 49 alertes de surveillance, aucune étude n'était annotée. Les résultats contradictoires significatifs sont rares (13 lignes appariées) ; l'essentiel des résultats défavorables sont des résultats nuls. Une relecture manuelle d'un échantillon aléatoire de 30 règles a conduit à ajuster le verdict automatique dans 4 cas (13 %). Cette comparaison montre la cohérence des alertes avec la littérature annotée ; elle ne constitue pas une preuve de bénéfice clinique. »

## Sauvegarde
WSL (développement) → Windows (cp vers C:\Users\MSI\Desktop\memoire\) → GitHub (git add/commit/push) → Google Drive (dossier racine « A Deep Learning based Webtool for Mutation-Aware Drug Recommendation »).
