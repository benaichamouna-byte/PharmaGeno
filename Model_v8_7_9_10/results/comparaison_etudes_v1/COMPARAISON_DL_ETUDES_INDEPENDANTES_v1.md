# Comparaison du DL avec des études publiées (23 octobre 2026)

Rappel du sujet : PharmaGeno recommande des médicaments à partir du VCF du patient (le DL lit tout le profil). Ici on vérifie, pour 8 couples gène-médicament, si ce que dit le DL va dans le même sens que des études de vrais patients, indépendantes de CPIC/DPWG.

## Méthode
1. Liste des couples où le DL fait une vraie différence (58 médicaments, `data/domaine_v8.json`) : vérifié AVANT de choisir les études.
2. Pour chaque couple : une étude clé, retrouvée puis LUE (résumé uniquement ; le texte complet n'était pas accessible). Chiffres recopiés du résumé.
3. Le DL est interrogé avec des profils CONSTRUITS (tous les gènes normaux, un seul gène changé) : `scripts/interroger_dl_couples_etudes_v1.py`, résultat `dl_couples_etudes.csv`. Ce sont des tests construits, pas de vrais patients. Modèles : ceux de l'environnement de Claude (à refaire avec les modèles de Mouna).

## Résultats
| # | Couple | Ce que dit le DL | Étude (type, effectif) | Résultat de l'étude (résumé) | Verdict |
|---|---|---|---|---|---|
| 1 | SLCO1B1 / simvastatine | EVITER si fonction diminuée (0,5) ou très diminuée (0,0) ; STANDARD si normal | SEARCH, NEJM 2008 ; étude génomique, 85 cas de myopathie + 90 témoins (simvastatine 80 mg), réplication dans un essai à 40 mg | Myopathie : OR 4,5 par allèle C (IC 95 % 2,6-7,7) ; CC vs TT : OR 16,9 (4,7-61,1) | Même sens. L'étude porte sur 80 mg : « à éviter » est plus fort que ce qu'elle montre. |
| 2 | HLA-B*57:01 / abacavir | EVITER si porteur | PREDICT-1, NEJM 2008 ; essai randomisé en double aveugle, 1 956 patients | Hypersensibilité confirmée : 0 % avec dépistage vs 2,7 % sans (P<0,001) | Concordant, preuve forte (essai randomisé). |
| 3 | HLA-B*15:02 / carbamazépine | EVITER si porteur | Chen, NEJM 2011 ; dépistage prospectif à Taïwan, 4 877 patients | Aucun SJS/TEN chez les non-porteurs traités ; attendu environ 10 cas d'après l'incidence historique (0,23 %) | Concordant (population taïwanaise ; comparaison à une incidence historique, pas à un groupe témoin). |
| 4 | HLA-B*58:01 / allopurinol | EVITER si porteur | Hung, PNAS 2005 ; cas-témoins, 51 cas + 228 témoins | Allèle présent chez 51/51 cas ; 15 % des témoins tolérants ; OR 580 (34-9 781) | Même sens (population chinoise Han). L'allèle est aussi chez 15 % des tolérants : seul, il ne suffit pas à prédire. |
| 5 | DPYD / fluorouracile | ADAPTER_DOSE si 0,5 ; STANDARD si 1,0 ; 0,0 hors domaine | Henricks, Lancet Oncol 2018 ; essai prospectif, 1 103 patients dont 85 porteurs | Dose réduite au départ : toxicité de grade >=3, RR 1,31 (0,63-2,73) avec réduction vs 2,87 (2,14-3,86) en cohorte historique pour DPYD*2A | Concordant. |
| 6 | CYP2C19 / clopidogrel | EVITER si 0,0 ou 0,5 ; STANDARD si 1,0 ou 2,0 | Mega, JAMA 2010 ; méta-analyse, 9 études, 9 685 patients (angioplastie) | 1 allèle réduit : HR 1,55 (1,11-2,17) ; 2 allèles : 1,76 (1,24-2,50) ; thrombose de stent : 2,67 et 3,97 | Concordant, pour les patients traités par angioplastie ; le DL ne connaît pas l'indication. |
| 7 | CYP2D6 / codéine | EVITER si ultra-rapide (2,0) ou lent (0,0) | Gasche, NEJM 2004 ; rapport de cas (1 patient) | Intoxication aux opiacés chez un métaboliseur ultra-rapide, avec d'autres facteurs (inhibition CYP3A4, baisse de la fonction rénale) | Même sens pour l'ultra-rapide, mais niveau de preuve faible (1 cas). Le cas « lent » n'est pas couvert. |
| 8 | CYP2D6 / tamoxifène | EVITER si 0,0 ou 0,5 ; STANDARD si 1,0 ou 2,0 | Province et ITPC, CPT 2014 ; méta-analyse, 4 973 patientes | Mauvais métaboliseurs : HR 1,25 (1,06-1,47) pour la survie sans maladie, mais seulement avec des critères stricts ; non significatif avec des critères plus larges (P=0,25 et P=0,38) | Partiel. La preuve est discutée ; « à éviter » est plus fort que ce que la méta-analyse établit. Le cas « 0,5 » (intermédiaire) n'est pas étudié dans le résumé. |

Bilan : l'étude va dans le même sens que le DL pour 8 couples sur 8, avec une preuve discutée pour le tamoxifène (résultat seulement sous critères stricts). Dans 2 cas, l'intensité de l'action (« à éviter ») dépasse ce que montre l'étude : simvastatine (étude à 80 mg) et tamoxifène. L'accord DL = étude concerne la direction ; ce n'est pas une preuve que la recommandation sauve des patients.

## Ce qui n'a pas été fait / pas lu
- Textes complets : non lus (PubMed/PMC bloquent ; revues payantes). Tout vient de résumés affichés sur des dépôts institutionnels.
- Pas encore de source pour : thiopurines (TPMT, NUDT15), UGT1A1 / irinotécan (une méta-analyse de Hoskins a été trouvée, non lue), inhibiteurs de pompe à protons, tacrolimus, médicaments G6PD, tricycliques.
- Pas de test avec données patient par patient (accès ITPC non vérifié).

## Sources lues (résumés)
1. SEARCH Collaborative Group, NEJM 2008;359(8):789-799, DOI 10.1056/NEJMoa0801936 : https://researchportal.ukhsa.gov.uk/en/publications/slco1b1-variants-and-statin-induced-myopathy-a-genomewide-study/
2. Mallal et al., NEJM 2008;358(6):568-579, DOI 10.1056/NEJMoa0706135 : https://researchportal.murdoch.edu.au/esploro/outputs/journalArticle/HLA-B5701-screening-for-hypersensitivity-to-Abacavir/991005542234207891
3. Chen et al., NEJM 2011;364(12):1126-1133, DOI 10.1056/NEJMoa1009717 : https://scholars.lib.ntu.edu.tw/handle/123456789/568520?locale=en
4. Hung et al., PNAS 2005;102(11):4134-4139, DOI 10.1073/pnas.0409500102 : https://scholars.lib.ntu.edu.tw/handle/123456789/434994?locale=en
5. Henricks et al., Lancet Oncol 2018;19(11):1459-1467 (chapitre de thèse de Leiden reprenant l'article, essai NCT02324452) : https://scholarlypublications.universiteitleiden.nl/access/item%3A2910333/view
6. Mega et al., JAMA 2010;304(16):1821-1830, DOI 10.1001/jama.2010.1543 : https://scholars.duke.edu/publication/1117056
7. Gasche et al., NEJM 2004;351(27):2827-2831, DOI 10.1056/NEJMoa041888 : https://archive-ouverte.unige.ch/unige:90087
8. Province et al. (ITPC), Clin Pharmacol Ther 2014;95(2):216-227, DOI 10.1038/clpt.2013.186 : https://profiles.wustl.edu/en/publications/cyp2d6-genotype-and-adjuvant-tamoxifen-meta-analysis-of-heterogen/
Les DOI sont ceux affichés par les pages ci-dessus ; je n'ai pas ouvert les sites des éditeurs.
