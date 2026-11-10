# Résultat — Même profil génétique, même médicament : l'application et PharmCAT donnent-ils la même recommandation ? (104 personnes, 8 novembre 2026)

## Ce qui a été fait
- 104 personnes GeT-RM/1000G hors corpus (liste figée sha256 730c05b908641075…), même fichier VCF d'entrée pour les deux outils (`multi104.vcf`, sha a94152dd418d06aa…) ; 18 gènes présents (pas de CYP2D6 ni de HLA dans ce VCF).
- Côté A : application v8s (chaîne complète VCF → PyPGx 0.27.0 → règles), non modifiée, un VCF par personne (seul l'en-tête a été complété avec les longueurs de chromosomes GRCh38 pour que l'application accepte le fichier).
- Côté B : PharmCAT 3.4.0 (recommandations CPIC et DPWG).
- Comparaison automatique des textes de recommandation (règles figées avant le calcul, empreintes dans `EMPREINTES_COMPARAISON_v1_8nov2026.txt`). 2 personnes sur 104 avaient été vues pendant la mise au point (disclosure).

## Résultat principal (amendement 1, décidé après avoir vu la v1)
Pour chaque recommandation CPIC/DPWG que l'application affiche pour une personne : se retrouve-t-elle parmi les recommandations PharmCAT de la même personne, même médicament, même guide ?

| | Lignes | % |
|---|---|---|
| Recommandations affichées par l'application (104 personnes) | 4 635 | |
| PharmCAT n'a aucune recommandation pour ce médicament/guide (non comparables) | 1 101 | 23,8 |
| Comparables | 3 534 | |
| Retrouvées chez PharmCAT (3 339 textes concordants + 116 équivalents lus à la main) | 3 455 | **97,8 % des comparables** |
| Non retrouvées | 79 | 2,2 |

CPIC : 98,8 % des comparables ; DPWG : 85,8 % (équivalences de langue incluses). Par personne × médicament × guide : 3 191 sur 3 264 (97,8 %) sont entièrement retrouvés.
Métrique v1 (centrée sur PharmCAT, conservée) : 3 298 annotations PharmCAT identiques sur 3 734 couvertes (88,3 %) ; la différence avec A1 vient des annotations alternatives de PharmCAT (diplotypes ambigus, adulte/pédiatrique, indications du clopidogrel) que l'application n'affiche pas.

## Les 79 recommandations non retrouvées (15 motifs, lus un par un)
| Cause | Lignes | Nature |
|---|---|---|
| Thiopurines CPIC (azathioprine, mercaptopurine, thioguanine), 10 personnes | 36 | **Différence réelle.** La règle CPIC de l'application n'utilise qu'un seul gène (TPMT ou NUDT15) alors que PharmCAT combine les deux. Texte affiché « dose standard » là où PharmCAT recommande une réduction de 30–80 %. Sur ces 10 personnes : action finale de l'application correcte (ADAPTER_DOSE) pour 6 ; STANDARD pour 2 (TPMT intermédiaire chez PharmCAT, normal chez PyPGx) ; aucune recommandation pour 2 (NUDT15 non appelé par PyPGx, intermédiaire chez PharmCAT). |
| CYP2C9 DPWG (siponimod, warfarine), génotype *1/*2 | 24 | **Différence réelle.** DPWG : aucune action pour *1/*2 ; l'application applique une réduction (règle par score d'activité). |
| CYP2C9 DPWG, génotype *2/*3 | 4 | **Différence réelle.** L'application affiche le texte du génotype le plus défavorable (*3/*3 : « éviter » / 20 %), DPWG indique 50 % / 45 %. |
| CYP2C9 DPWG, *1/*3 warfarine (7) et *2 seul (2) | 9 | Même dose (65 %) mais suite du texte différente (7) ; *2 seul : cas à relire (2). |
| Flucytosine DPYD | 4 | Même contenu (« rester attentif aux effets graves »), texte français / anglais : équivalent. |
| Fluvastatine, 1 personne | 1 | PharmCAT appelle SLCO1B1 « Poor Function » (≤ 40 mg) ; la règle de l'application ne tient compte que de CYP2C9. |
| Sertraline, 1 personne | 1 | CYP2B6 pris en compte par l'application, pas par PharmCAT. |

Équivalences lues à la main (déclarées avant le calcul A1) : 116 lignes VKORC1 (acénocoumarol, phenprocoumon), texte français de l'application, même contenu que PharmCAT (aucune action pour CT ; 50 % de dose et suivi INR pour TT).

## Le DL (réseau de neurones) face à PharmCAT
Unité : personne × médicament dont toutes les règles CPIC/DPWG de l'application sont retrouvées chez PharmCAT et dont l'action finale vient d'un texte soutenu par PharmCAT (définition écrite avant calcul dans `dl_vs_pharmcat_v1.py`). 2 600 unités ; l'action du DL est la même que l'action soutenue par PharmCAT dans **2 598 cas (99,92 %)**. Parmi les 620 unités non « standard », 618 sont correctes. 2 désaccords (sertraline : règle EVITER, DL ADAPTER_DOSE). Limite : le DL a été entraîné sur des étiquettes issues des mêmes règles ; ce résultat montre qu'il reproduit la bonne action pour de nouvelles personnes, pas que le guide est juste.

## Recherche d'une étude publiée avec VCF + recommandation (8 nov., 22h)
Aucun jeu public « VCF → recommandation finale par personne » indépendant de PharmCAT n'a été trouvé. Pratique du domaine : vérité génotype = GeT-RM ; vérité recommandation = tables CPIC/DPWG ; logiciel de référence = PharmCAT (Sangkuhl et al., 2020, https://ascpt.onlinelibrary.wiley.com/doi/full/10.1002/cpt.1568). Voir le message de session pour les sources lues et celles non accessibles.

## Ce que ce test montre et ne montre pas
- Montre : à partir du même VCF, l'application sélectionne et affiche la même recommandation que PharmCAT dans 97,8 % des cas comparables, et les écarts ont des causes identifiées (3 défauts de règles à corriger ou documenter : thiopurines à deux gènes, CYP2C9 DPWG par allèle, SLCO1B1 ignoré pour la fluvastatine ; et des différences d'appel de génotype TPMT/NUDT15).
- Ne montre pas : que les recommandations sont correctes. Les textes de l'application viennent des mêmes guides (CPIC/DPWG, dont les fichiers PharmCAT) : l'indépendance porte sur la lecture du VCF, le calcul du phénotype et le choix de la règle, pas sur le contenu des guides.
- Limites : 18 gènes seulement ; comparaison de textes (la concordance est évaluée par similarité figée, pas par un pharmacologue) ; 23,8 % des règles de l'application n'ont pas de recommandation PharmCAT comparable ; couverture : PharmCAT émet des recommandations pour des couples médicament–guide absents de l'application (DPWG : 25 médicaments, ex. clopidogrel, simvastatine, voriconazole ; CPIC : 18, ex. phénytoïne, anesthésiques volatils, succinylcholine, ivacaftor) et l'application en émet que PharmCAT n'émet pas (gliclazide, glimépiride, mirtazapine, moclobémide, prasugrel, ticagrelor, paclitaxel…) ; 7 AINS CPIC sans texte de recommandation dans l'application (texte de remplissage).
- Un seul lecteur ; à faire relire par le pharmacologue (en priorité les 5 causes réelles ci-dessus).

## Fichiers
`detail_A1_centre_app_104.csv`, `motifs_NON_RETROUVEE_A1.csv`, `detail_reco_104.csv`, `motifs_differences_104.csv`, scripts `comparer_reco_v1.py` (figé), `agreger_reco_v1.py`, `agreger_reco_v1_1.py`, `lancer_lot_v1.py`.

## Sauvegarde
WSL (développement) → Windows (cp vers C:\Users\MSI\Desktop\memoire\) → GitHub (git add/commit/push) → Google Drive (PharmaGeno_Memoire/).
