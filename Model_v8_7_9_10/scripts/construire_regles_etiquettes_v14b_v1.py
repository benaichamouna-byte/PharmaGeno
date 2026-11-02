#!/usr/bin/env python3
"""
construire_regles_etiquettes_v14b_v1.py (2 nov. 2026) : regles_v14_monogene.csv = regles_v14 précédente (copie datée du 1 nov.) + règles tirées de 6 étiquettes ClinPGx
(texte lu le 1-2 nov. 2026 sur api.clinpgx.org/v1/data/labelAnnotation/<PA...>). v14 reste PROVISOIRE (aucun gel).

Hypothèses (documentées, réversibles, mêmes principes que la v14 du 1 nov.) :
 - H-FDA-1 : valeur non citée comme concernée -> STANDARD.
 - H-FDA-2 : texte d'étiquette de type « caution / treated with caution » lié à un génotype -> SURVEILLER (jamais EVITER), confiance moyenne.
 - H-FDA-3 (nouvelle) : étiquette qui indique une dose réduite pour un génotype nommé (« 50 % de la dose », « lower dose regimen should be considered ») -> ADAPTER_DOSE, confiance moyenne.
Correspondance texte -> valeur de profil (choix de codage, à relire) :
 - nilotinib : UGT1A1 (TA)7/(TA)7 = Poor Metabolizer (0.0) ; erlotinib : « low expression of UGT1A1 / Gilbert » -> 0.0 seulement.
 - carisoprodol : « reduced CYP2C19 activity » -> PM (0.0) et IM (0.5). cevimeline : « deficient in CYP2D6 activity » -> PM (0.0).
 - lonafarnib : « known dysfunctional polymorphism in CYP3A4 » -> PM (0.0) seulement ; l'IM (0.5) n'est pas cité -> STANDARD (H-FDA-1).
 - glyburide : « poor metaboliser (CYP2C9*3) … *3/*3 and *2/*3 » -> PM (0.0 et 0.25) ; IM non cité -> STANDARD. Glyburide avait déjà des règles G6PD (CPIC) : le moteur prend l'action la plus sévère.
Point de vigilance (résolu le 2 nov. : carisoprodol RETIRÉ, avatrombopag-F5 AJOUTÉ) : la table FDA classe carisoprodol-CYP2C19 « pharmacocinétique seulement » (PA166329631) alors que le texte d'étiquette (PA166104832) dit « should be used with caution in patients with reduced CYP2C19 activity ».
 Le 1 nov., avatrombopag et tamsulosine avaient été retirés pour ce motif (table FDA = PK seulement, sans recommandation). Carisoprodol est AJOUTÉ ici parce que le texte d'étiquette contient une recommandation explicite ; décision à confirmer par Mouna.
Ajout 2 nov. : fluindione (RNPGx 2017, H-RNPGx-1).
Usage : python3 construire_regles_etiquettes_v14b_v1.py PHARMCAT_JSON data/regles_v14_monogene_avant_etiquettes_2nov.csv data/regles_v14_monogene.csv
"""
import sys, json, re
import pandas as pd
S, ST, AD = 'SURVEILLER', 'STANDARD', 'ADAPTER_DOSE'
NOM = {'UGT1A1': {0.0: 'Poor Metabolizer', 0.5: 'Intermediate Metabolizer', 1.0: 'Extensive Metabolizer'},
       'CYP2C19': {0.0: 'CYP2C19 Poor metabolizer', 0.5: 'CYP2C19 Intermediate metabolizer', 1.0: 'CYP2C19 Normal metabolizer', 1.5: 'CYP2C19 Rapid metabolizer', 2.0: 'CYP2C19 Ultrarapid metabolizer'},
       'CYP2D6': {0.0: 'CYP2D6 Poor metabolizer', 0.5: 'CYP2D6 Intermediate metabolizer', 1.0: 'Normal metabolizer', 2.0: 'CYP2D6 Ultrarapid metabolizer'},
       'CYP3A4': {0.0: 'CYP3A4 PM', 0.5: 'CYP3A4 IM', 1.0: 'CYP3A4 NM'},
       'VKORC1': {0.0: 'VKORC1 rs9923231 homozygote variant', 0.5: 'VKORC1 rs9923231 hétérozygote', 1.0: 'VKORC1 référence'},
       'F5': {0.0: 'Facteur V Leiden (porteur)', 1.0: 'F5 non porteur'},
       'CYP2C9': {0.0: 'CYP2C9 Poor Metabolizer (AS 0.5 and 0)', 0.25: 'CYP2C9 Poor Metabolizer (AS 0.5 and 0)', 0.5: 'CYP2C9 Intermediate Metabolizer (AS of 1 and 1.5)',
                  0.75: 'CYP2C9 Intermediate Metabolizer (AS of 1 and 1.5)', 1.0: 'CYP2C9 Normal Metabolizer'}}
# (médicament, gène, {valeur: action}, hypothèse, source, mot-clé PharmCAT (étiquette FDA) ou None, (texte, identifiant) si hors PharmCAT)
AJOUTS = [
 ('nilotinib', 'UGT1A1', {0.0: S}, 'H-FDA-2', 'HCSC-etiquette', None,
  ("Monographie HCSC (Tasigna), ClinPGx PA166151974 : « the (TA)7/(TA)7 genotype was associated with a statistically significant increase [in] the risk of hyperbilirubinemia relative to the (TA)6/(TA)6 and (TA)6/(TA)7 genotypes » ; « Caution is recommended in patients with (TA)7/(TA)7 genotype. »", 'PA166151974')),
 ('erlotinib', 'UGT1A1', {0.0: S}, 'H-FDA-2', 'EMA-etiquette', None,
  ("EPAR EMA (erlotinib), ClinPGx PA166182949 : « Patients with low expression levels of UGT1A1 or genetic glucuronidation disorders (e.g. Gilbert's disease) may exhibit increased serum concentrations of bilirubin and must be treated with caution. »", 'PA166182949')),
 # carisoprodol RETIRÉ le 2 nov. 2026 (décision déléguée) : la table FDA le classe « pharmacocinétique seulement » ; même critère que tamsulosine.
 # avatrombopag-F5 AJOUTÉ (même texte d'étiquette FDA que eltrombopag et lusutrombopag, déjà inclus) : cohérence de traitement.
 ('avatrombopag', 'F5', {0.0: S}, 'H-FDA-2', 'FDA-etiquette', 'avatrombopag', None),
 ('cevimeline', 'CYP2D6', {0.0: S}, 'H-FDA-2', 'FDA-etiquette', 'cevimeline', None),
 ('lonafarnib', 'CYP3A4', {0.0: AD}, 'H-FDA-3', 'EMA-etiquette', None,
  ("EPAR EMA (lonafarnib), ClinPGx PA166355801 : « Subjects with a known dysfunctional polymorphism in CYP3A4 should start therapy at 50% of the indicated dose. » ; « The patient's daily dose of lonafarnib should be reduced by 50% and the reduced daily dose should be divided into two equal doses. »", 'PA166355801')),
 ('glyburide', 'CYP2C9', {0.0: AD, 0.25: AD}, 'H-FDA-3', 'HCSC-etiquette', None,
  ("Monographie HCSC (glyburide), ClinPGx PA166345321 (extrait relevé le 1 nov. 2026) : « A lower dose regimen in poor metaboliser (CYP2C9*3 variant) should be considered… CYP2C9*3/*3 and *2/*3 genotypes may have an increased risk of hypoglycemia. »", 'PA166345321')),
 # RNPGx (guideline nationale française, 2017, PubMed 28237404) : fluindione (antivitamine K), effets de CYP2C9 et VKORC1 cumulatifs -> deux règles mono-gène, le moteur prend l'action la plus sévère.
 ('fluindione', 'CYP2C9', {0.0: AD, 0.25: AD, 0.5: AD, 0.75: AD}, 'H-RNPGx-1', 'RNPGx', None,
  ("RNPGx 2017 (PubMed 28237404), ClinPGx PA166202621 : « Patients who are carriers of homozygous or heterozygous alleles CYP2C9*2 or *3 exhibit reduced liver metabolism of VKA and are at risk of over exposure. » ; « the VKA should be initiated at a lower dose (from 20% to 80% of standard dose) ».", 'PA166202621')),
 ('fluindione', 'VKORC1', {0.0: AD, 0.5: AD}, 'H-RNPGx-1', 'RNPGx', None,
  ("RNPGx 2017 (PubMed 28237404), ClinPGx PA166202621 : « In subjects with a homozygous or heterozygous c.-1639A variant of gene VKORC1 a standard VKA dose is associated with higher risk of hemorrhage due to overexposure. » ; « the VKA should be initiated at a lower dose (from 20% to 80% of standard dose) ».", 'PA166202621')),
]
UNIV = {g: sorted(NOM[g]) for g in NOM}
HYP = {'H-FDA-2': "texte d'étiquette « prudence » lié au génotype -> SURVEILLER, confiance moyenne.",
       'H-FDA-3': "étiquette indiquant une dose réduite pour un génotype nommé -> ADAPTER_DOSE, confiance moyenne.",
       'H-RNPGx-1': "guideline RNPGx indiquant une dose initiale réduite (20 à 80 %) pour les porteurs -> ADAPTER_DOSE ; non porteurs -> STANDARD, confiance moyenne."}
def clean(x): return ' '.join(re.sub('<[^>]+>', ' ', x or '').replace('&quot;', '"').split())
G = json.load(open(sys.argv[1]))['guidelines']
R = pd.read_csv(sys.argv[2]); R['decision_v14'] = R['decision_v14'] if 'decision_v14' in R else None
def annot(mot, gene):
    for e in G:
        x = e['guideline']
        if x['source'] != 'FDA' or 'Label' not in x['name']: continue
        if mot in [c['name'].lower() for c in (x['relatedChemicals'] or [])] and gene in [t['symbol'] for t in (x['relatedGenes'] or [])]:
            return x['id'], ' | '.join(sorted({clean(r['text']['html']) for r in e['recommendations']}))
    return None, None
lignes = []
for med, gene, vals, hyp, src, mot, secours in AJOUTS:
    if mot:
        fid, txt = annot(mot, gene)
        if not txt: print('ANNOTATION ABSENTE pour', med, gene, '-> NON ajouté'); continue
    else:
        txt, fid = secours
    assert not ((R.medicament == med) & (R.gene == gene)).any(), med + ' ' + gene + ' déjà présent'
    for v in UNIV[gene]:
        act = vals.get(v, ST)
        d = (f"v14b {hyp} : {HYP[hyp]}" if act != ST else f"v14b H-FDA-1 : valeur non citée comme sous-groupe concerné -> STANDARD (posologie générale de l'étiquette).")
        lignes.append(dict(gene=gene, valeur=v, medicament=med, action=act, ambigu=False, source=src, n_valeurs=1, phenotype=NOM[gene][v],
                           recommandation=txt if act != ST else "Valeur hors sous-groupe concerné : posologie générale de l'étiquette. Texte source : " + txt,
                           fichier=fid, table=None, guideline_multigene=0,
                           desaccord_autres_sources="Source étiquette réglementaire (" + src.split('-')[0] + ") : niveau de preuve inférieur à CPIC/DPWG ; texte interprété (" + hyp + ")",
                           conflit_intra_source=False, divergence_autre_table_meme_source=False, gene_dans_les_31=True, conditionnel=False, codage_a_valider=False, decision_v14=d))
A = pd.DataFrame(lignes)
out = pd.concat([R, A], ignore_index=True)
out.to_csv(sys.argv[3], index=False)
print('avant :', len(R), 'règles | ajoutées :', len(A), '| médicaments concernés :', A.medicament.nunique(), '| après :', len(out))
print(A.groupby(['medicament', 'gene']).apply(lambda d: '; '.join('%s=%s' % (v, a) for v, a in zip(d.valeur, d.action))).to_string())
