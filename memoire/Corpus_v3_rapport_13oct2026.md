# Corpus v3 : étiquettes recalculées depuis les guidelines (13 oct 2026)

Statut : **construit et testé** (19 cas de référence sur 19 conformes). Les étiquettes sont celles des règles CPIC/DPWG v2, **pas** un jugement de ma part. Le fichier d'origine `phenotype_drug_dataset_FINAL.csv` n'est pas modifié.

## 1. Pourquoi
Les anciennes étiquettes (table PharmGKB : Toxicity/Efficacy → EVITER, Dosage → ADAPTER_DOSE…) s'accordent avec les règles des guidelines dans **19 % des cas** seulement. Exemples : codéine, clopidogrel, oméprazole, tramadol, tacrolimus, fluorouracile : accord de 0 à 1 %.

## 2. Règles de construction (écrites dans `construire_corpus_v3.py`)
1. Règle utilisable : non ambiguë, codage de valeur vérifié, sans conflit interne à la source. Les règles « conditionnelles » sont exclues, sauf 14 acceptées après **lecture du texte complet** de la guideline (la condition ne change pas la classe d'action) : clopidogrel PM/IM, thiopurines TPMT/NUDT15 IM, irinotécan UGT1A1 PM, siponimod CYP2C9 IM, brexpiprazole, capécitabine/fluorouracile DPYD normal. Restent exclues : eliglustat PM (dépend de la co-médication), flécaïnide IM (« aucune action » pour le test de Brugada).
2. Plusieurs gènes pour un médicament : action la plus sévère (EVITER > ADAPTER_DOSE > SURVEILLER > STANDARD). Une règle multi-gènes remplace les règles mono-gène de ses deux gènes. Les règles multi-gènes avec HLA-B, G6PD ou MT-RNR1 sont exclues (codage des valeurs encore à valider).
3. Valeur sans règle (ex. CYP2D6 = 1.5 pour la codéine, ou « normal » absent de la guideline warfarine) : ligne **exclue**, sauf si un autre gène impose déjà EVITER. Rien n'est inventé.
4. Médicament sans règle utilisable : aucune étiquette.

## 3. Résultats
| Fichier | Lignes | Médicaments | Échantillons | STANDARD / ADAPTER / EVITER / SURVEILLER |
|---|---|---|---|---|
| `phenotype_drug_dataset_v3.csv` (lignes d'origine ré-étiquetées) | 23 667 | 76 | 3 131 | 13 092 / 7 120 / 3 454 / 1 |
| `phenotype_drug_dataset_v3_croise.csv` (voir §4) | 76 028 | 76 | 1 379 | 59 706 / 10 059 / 5 634 / 629 |

- 78 médicaments ont au moins une règle utilisable (sur 530 du corpus). 76 apparaissent avec des lignes étiquetées. 32 à 39 d'entre eux n'ont qu'une seule classe (par ex. aucune règle EVITER non ambiguë) : ils n'apprennent pas de contraste.
- Lignes écartées (« incomplètes ») : 6 334 sur le corpus d'origine, car la guideline ne couvre pas la valeur : warfarine (le normal n'est pas listé), ésoméprazole (une seule règle, UM), thiopurines (PM ambigus), citalopram/escitalopram (règles PM/UM ambiguës).
- Tests de référence (`corpus_v3_tests_reference.csv`) : codéine, tramadol, clopidogrel, simvastatine, fluorouracile, tacrolimus, oméprazole, 19 couples gène/valeur, accord 100 %. **Ces tests vérifient la chaîne de construction, pas les guidelines elles-mêmes** : les étiquettes sont déterministes à partir des règles.

## 4. Défaut du corpus d'origine découvert : biais de sélection
Dans le corpus d'origine, les médicaments d'un échantillon sont choisis à partir de ses variants. Le gène « normal » n'apparaît donc presque jamais avec son médicament : pour la codéine, 1 ligne CYP2D6 = 1.0 sur 635. Un modèle apprendrait « gène non normal ⇒ médicament à risque » au lieu de lire le profil.
→ Fichier **croisé** : chacun des 1 379 profils réels 1000 Genomes est associé à chaque médicament à règle (codéine : 748 lignes CYP2D6 normal au lieu de 1). Les profils DOC (artificiels) ne sont pas croisés.

## 5. Limites à connaître
- Les étiquettes viennent des règles : les métriques mesureront la **fidélité aux guidelines**, pas un résultat clinique. L'apport propre du DL se jugera sur les médicaments non vus (RQ5), les profils rares et la calibration.
- Seuls ~76 médicaments (15 gènes) reposent sur une guideline. Pour les ~450 autres, l'application devra afficher « non couvert par une guideline ».
- RYR1 et CACNA1S valent 0.5 sur toute ligne 1KGP, et 1.0 sur 275 lignes DOC : ils permettent de deviner l'origine de la ligne. À retirer des entrées avant l'entraînement (avec les 9 gènes constants : ACE, ADRB2, CFTR, EGFR, HLA-A, HLA-B, MT-RNR1, MTHFR, SLC19A1).
- 59 règles mono-gène et 22 multi-gènes ambiguës attendent tes verdicts (`controle_regles_v2.csv`) ; elles sont exclues par défaut.
- Dans `phenotype_drug_dataset_v3.csv`, la colonne `origine` vaut `1KGP_HG`, `1KGP_NA` ou `DOC` (« NA » seul serait lu comme valeur manquante par pandas).

## Journal de Bord (extrait)
1) Décisions validées : étiquettes depuis les guidelines v2 ; nouveau fichier, ancien intact. À valider : 14 règles conditionnelles acceptées ; usage du corpus croisé pour l'entraînement.
2) Erreurs à ne plus reproduire : se fier à l'ancienne table PharmGKB pour étiqueter ; accepter « conditionnel = exclu » sans lire le texte complet (cela supprimait clopidogrel PM/IM, cas central).
3) Reste à faire : retirer RYR1/CACNA1S et gènes constants ; entraîner DL, XGBoost, RF séquentiellement ; RQ1, RQ3, RQ4, RQ5, RQ6, calibration ; couche de recommandation et application.
