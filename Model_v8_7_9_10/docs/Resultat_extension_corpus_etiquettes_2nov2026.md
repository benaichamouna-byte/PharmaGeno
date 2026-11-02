# Extension du corpus par étiquettes ClinPGx — 2 novembre 2026 (corpus v14 GELÉ à 11 h 40)

## Décisions
- Mouna : « corpus plus étendu » (groupe A, 6 étiquettes) ; groupe B sans préférence -> vérification CPIC/DPWG, aucune action publiée.
- Mouna a ensuite délégué les trois décisions du gel (« fait ce que la littérature fait, sois professionnel et fiable ») ; critère appliqué : la classe de preuve propre à la FDA (table ClinPGx des étiquettes).
  1. Carisoprodol-CYP2C19 : RETIRÉ (table FDA = pharmacocinétique seulement, PA166329631) ; même traitement que tamsulosine et que l'avatrombopag-CYP.
  2. Avatrombopag-F5 : AJOUTÉ (SURVEILLER pour porteur du facteur V Leiden, H-FDA-2) : son texte d'étiquette est le même que celui d'eltrombopag et de lusutrombopag, déjà inclus ; l'omission du 1 nov. était une incohérence.
  3. Six ajouts de la v14 du 1 nov. à preuve plus faible (chlorpropamide, glipizide, tolazamide, nitrite de sodium, eltrombopag, lusutrombopag) : CONSERVÉS, confiance « moyenne » ; ils sont évalués séparément (analyse de sensibilité sans eux).
  4. Corpus final : v14 gelé = ancienne « v14b » corrigée (retrait carisoprodol, ajout avatrombopag). L'ancienne v14 de 183 médicaments est conservée dans `data/corpus_v14_REMPLACE_183_provisoire/`, l'ancienne v14b dans `data/corpus_v14b_REMPLACE_avec_carisoprodol/`.

## Résultat (corpus v14 gelé)
- 189 médicaments (v13 : 176), 232 664 lignes, 1 379 profils (1 241 hors ensemble final de 138 familles). Dossier `data/corpus_v14/` : `phenotype_drug_dataset_v14.csv`, couverture par médicament, `GEL_v14_2nov2026.txt` (empreintes SHA-256 complètes), fichiers en lecture seule.
- 13 médicaments ajoutés depuis v13 : avatrombopag, cevimeline, chloroprocaine, chlorpropamide, eltrombopag, erlotinib, fluindione, glipizide, lonafarnib, lusutrombopag, nilotinib, sodium nitrite, tolazamide.
- Contrôles : 231 285 lignes communes avec l'ancienne v14b : 0 action et 0 confiance différentes (hors avatrombopag, carisoprodol). Par rapport à v13, seul glyburide change : 29 profils STANDARD -> ADAPTER_DOSE (CYP2C9 PM) ; glyburide compte 1 376 lignes au lieu de 1 377.
- Règles : 676 -> 704 (+28). Script `scripts/construire_regles_etiquettes_v14b_v1.py` ; copie de l'ancien fichier : `data/regles_v14_monogene_avant_etiquettes_2nov.csv`.
- Empreintes (16 premiers hex) : corpus v14 b876bb469e562d6e ; regles_v14_monogene 39a736892cf6cc58 ; règles avant 2 nov. c0d3fd61d7e5f861.

| Médicament | Gène | Texte d'étiquette | Action | Lignes |
|---|---|---|---|---|
| nilotinib | UGT1A1 PM | HCSC PA166151974 : « Caution is recommended in patients with (TA)7/(TA)7 » | SURVEILLER | 277 |
| erlotinib | UGT1A1 PM | EMA PA166182949 : « must be treated with caution » (faible expression UGT1A1, Gilbert) | SURVEILLER | 277 |
| avatrombopag | F5 (porteur) | étiquette FDA, même texte que eltrombopag / lusutrombopag | SURVEILLER | 29 |
| cevimeline | CYP2D6 PM | FDA PA166104787 : « caution in individuals … deficient in CYP2D6 activity » | SURVEILLER | 66 |
| lonafarnib | CYP3A4 PM | EMA PA166355801 : « start therapy at 50% of the indicated dose » | ADAPTER_DOSE | 1 |
| fluindione | CYP2C9 (valeurs < 1) + VKORC1 (hom./hét.) | RNPGx 2017 PA166202621 : « initiated at a lower dose (from 20% to 80% of standard dose) » ; effets cumulatifs | ADAPTER_DOSE (porteur), STANDARD | 888 / 490 |
| glyburide (déjà au corpus) | CYP2C9 PM | HCSC PA166345321 : « lower dose regimen in poor metaboliser (CYP2C9*3) should be considered » | ADAPTER_DOSE | 29 |

Hypothèses : H-RNPGx-1, H-FDA-1 (valeur non citée -> STANDARD), H-FDA-2 (prudence liée au génotype -> SURVEILLER), H-FDA-3 (dose réduite explicite -> ADAPTER_DOSE). Confiance « moyenne » pour toutes les lignes ajoutées le 1-2 nov.

## Limites à écrire dans le mémoire
- Lonafarnib : une seule ligne ADAPTER_DOSE (1 profil CYP3A4 PM) ; aucun apprentissage possible pour cette classe sur ce médicament.
- Fluindione : aucune empreinte moléculaire (SMILES absent des exports ClinPGx) ; ATC et liens gène présents.
- Textes erlotinib, lonafarnib, glyburide : lus via l'API ClinPGx (résumeur), pas dans le JSON PharmCAT ; glyburide : extrait partiel.
- Les 13 ajouts depuis v13 ont tous une confiance « moyenne » (étiquettes réglementaires ou guideline nationale, niveau de preuve inférieur à CPIC/DPWG).

## Groupe B (9 substances : bupropion, nevirapine, norclobazam, fentanyl, isoniazid, dextromethorphan, debrisoquine, atazanavir/ritonavir, contraceptifs hormonaux)
Aucune n'a de recommandation d'action CPIC/DPWG sur un gène des profils. Fentanyl : guideline CPIC opioïdes concerne COMT et OPRM1 (absents des profils). Atazanavir, simvastatine, lovastatine : déjà au corpus. -> niveau association seulement.

## Pourquoi pas plus
- ~1 000 substances de N3 : association publiée, aucune action écrite.
- 21 médicaments « règle seule » (CACNA1S, RYR1, CFTR, MT-RNR1, HLA-B*15:02, HLA-B*57:01) : la règle existe, mais 0 à 3 porteurs dans la cohorte ; hors corpus d'entraînement.

## Deux chiffres à rapporter séparément (jamais additionnés sans mention)
- 189 médicaments avec règle ET données pour le DL (corpus v14b).
- 21 médicaments supplémentaires par règle de guideline seule (catégorie « Règle de guideline seule » déjà présente dans l'application, versions v8 à v8n) : soit 210 médicaments traités par l'outil, dont 21 sans DL. Vérifier dans la version cible de l'application que ces 21 s'affichent bien avant d'écrire 210.

## Lectures du 2 nov. sans règle (DPWG « not a gene-drug interaction » ou hors périmètre)
- DPWG, aucune recommandation : atenolol (CYP2D6), duloxetine (CYP2D6), olanzapine (CYP2D6), sotalol (CYP2D6), méthotrexate (MTHFR), ribavirine (HLA-B*44).
- Non lues (même schéma probable, à confirmer) : méthylphénidate (COMT/CYP2D6), acide folique (MTHFR), olanzapine (CYP1A2).
- Cisplatine / TPMT (CPNDS PA166170751) : recommandations limitées aux patients pédiatriques (adultes : test NON recommandé) ; le moteur exclut les règles conditionnelles -> non codé, décision de Mouna.
- CPIC : les 24 paires restantes dont le gène est dans les profils (AINS CYP2C9, bêtabloquants ADRB2, G6PD mésalazine/moxifloxacine…, setrons CYP2D6) sont absentes des paires CPIC « utilisées pour recommandation » et de PharmCAT : pas de recommandation à coder.
- Tebentafusp (HLA-A*02:01, RNPGx) : indication réservée aux patients HLA-A*02:01 positifs ; non lu, non codé.
