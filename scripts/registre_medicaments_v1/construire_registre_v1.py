#!/usr/bin/env python3
"""
construire_registre_v1.py : registre des médicaments PharmaGeno (v1).
Objectif : un tableau, une ligne par médicament, qui croise TOUTES les sources disponibles pour décider du périmètre du jeu de données,
avant tout entraînement. Aucune étiquette n'est créée ici et aucun fichier existant n'est modifié.

Sources lues (toutes fournies par l'utilisatrice ou produites par le projet) :
  1. PharmGKB guidelineAnnotations_json.zip (217 guidelines : DPWG, CPIC, RNPGx, CPNDS, AIOM, ACR, CFF, SEFF/SEOM, AusNZ, AHA)
  2. PharmGKB relationships.tsv (liens gène-médicament avec le type de preuve : GuidelineAnnotation, LabelAnnotation, ClinicalAnnotation...)
  3. PharmGKB clinicalVariants.tsv (niveau de preuve 1A..4 par variant-médicament)
  4. regles_v2_monogene.csv / regles_v2_multigene.csv (règles extraites des guidelines CPIC et DPWG, v2)
  5. corpus_v3_couverture_par_medicament.csv (médicaments réellement étiquetés dans le corpus v3)
  6. dataset_ORIGINAL_39259.csv (corpus d'origine : 530 médicaments)
  7. Table FDA des biomarqueurs pharmacogénomiques, version 12/2025 (extraction automatique approximative, fichier --fda)
  8. Alshabeeb et al. 2022, Front. Med. 9:1001876, tableaux 2 et 3 (50 gènes, 152 médicaments)

Usage : python3 construire_registre_v1.py --ga DOSSIER_JSON --rel relationships.tsv --cv clinicalVariants.tsv --dossier-projet DOSSIER --fda fda_rows.csv --sortie registre_medicaments_v1.csv
"""
import argparse, glob, json, os, re, collections
import pandas as pd

# Alshabeeb et al. 2022, Tableau 3 (152 médicaments) ; la cellule « Streptomycin, Succinylcholine » compte pour deux médicaments
LISTE_152 = """Abacavir, Dimercaprol, Irinotecan, Ondansetron, Sertraline, Acenocoumarol, Divalproex sodium, Isoflurane, Oxcarbazepine, Sevoflurane, Allopurinol, Doxepin, Isoniazid, Oxycodone, Simvastatin, Amikacin, Efavirenz, Ivacaftor, Pantoprazole, Siponimod, Amitriptyline, Eliglustat, Kanamycin, Paromomycin, SN-38, Aripiprazole, Enflurane, Lamotrigine, Paroxetine, Sodium nitrite, Aspirin, Erlotinib, Lansoprazole, Peginterferon Alfa-2a, Streptomycin, Succinylcholine, Atazanavir, Estradiol containing contraceptives, Lornoxicam, Peginterferon Alfa-2b, Sulfacetamide, Sulfadiazine, Atomoxetine, Escitalopram, Lovastatin, Pegloticase, Sulfamethoxazole/Trimethoprim, Atorvastatin, Etanercept, Mafenide, Phenazopyridine, Sulfasalazine, Azathioprine, Fentanyl, Meloxicam, Phenprocoumon, Sulfisoxazole, Belinostat, Flecainide, Mercaptopurine, Phenytoin, Tacrolimus, Brivaracetam, Flucloxacillin, Mesalazine, Pimozide, Tafenoquine, Bupropion, Fluorouracil, Methadone, Piroxicam, Tamoxifen, Capecitabine, Flurbiprofen, Methazolamide, Pitavastatin, Tegafur, Captopril, Fluvastatin, Methotrexate, Pitolisant, Telaprevir, Carbamazepine, Fluvoxamine, Methoxyflurane, Plazomicin, Tenoxicam, Carglumic acid, Fosphenytoin, Methylene blue, Pravastatin, Tetrabenazine, Celecoxib, Gefitinib, Metoprolol, Primaquine, Thioguanine, Chloramphenicol, Gentamicin, Mirtazapine, Probenecid, Tobramycin, Chlorpropamide, Glibenclamide, Moxifloxacin, Propafenone, Tramadol, Ciprofloxacin, Glimepiride, Mycophenolic acid, Quetiapine, Trimipramine, Citalopram, Glipizide, Nalidixic acid, Quinine, Tropisetron, Clomipramine, Haloperidol, Nevirapine, Rabeprazole, Valproic acid, Clopidogrel, Halothane, Nicotine, Rasburicase, Velaglucerase alfa, Codeine, Hydralazine, Nitrofurantoin, Ribavirin, Venlafaxine, Dapsone, Hydrochlorothiazide, Norfloxacin, Rituximab, Voriconazole, Desflurane, Hydrocodone, Nortriptyline, Risperidone, Vortioxetine, Desipramine, Ibuprofen, Oliceridine, Rosuvastatin, Warfarin, Dexlansoprazole, Imipramine, Omeprazole, Salmeterol, Zuclopenthixol"""

GENES_50 = set("ABCG2 ACE ADD1 ADRB2 APOE ATIC CACNA1S CES1 CFTR CHRNA5 CPS1 CYP2A6 CYP2B6 CYP2C9 CYP2C19 CYP2D6 CYP3A4 CYP3A5 CYP4F2 DPYD EGFR FCGR3A F5 G6PD HLA-A HLA-B HLA-C HLA-DPB1 HLA-DRB1 HPRT1 IFNL3 IFNL4 ITPA KIF6 MTHFR MT-RNR1 NAGS NAT2 NUDT15 OTC POLG RYR1 SCN1A SLC19A1 SLCO1B1 TNF TPMT UGT1A1 VKORC1".split())
GENES_12_ENTREE = set("ABCG2 CYP2B6 CYP2C19 CYP2C9 CYP2D6 CYP3A5 DPYD F5 NUDT15 SLCO1B1 TPMT UGT1A1".split())
ORDRE_NIVEAU = ['1A', '1B', '2A', '2B', '3', '4']


def norm(s):
    return re.sub(r'\s+', ' ', str(s).strip().lower())


def lire_guidelines(dossier):
    """drug -> {sources, genes, n, dosage, alternative, test}"""
    out = collections.defaultdict(lambda: {'sources': set(), 'genes': set(), 'ids': set(), 'dosing': False, 'alt': False, 'test': False})
    for f in sorted(glob.glob(os.path.join(dossier, 'PA*.json'))):
        g = json.load(open(f, encoding='utf-8'))['guideline']
        drugs = [norm(c['name']) for c in g.get('relatedChemicals', [])]
        genes = {x['symbol'] for x in g.get('relatedGenes', [])}
        for d in drugs:
            o = out[d]
            o['sources'].add(str(g.get('source'))); o['genes'] |= genes; o['ids'].add(g['id'])
            o['dosing'] |= str(g.get('dosingInformation')).lower() == 'true'
            o['alt'] |= str(g.get('alternateDrugAvailable')).lower() == 'true'
            o['test'] |= str(g.get('hasTestingInfo')).lower() == 'true'
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ga', required=True); ap.add_argument('--rel', required=True); ap.add_argument('--cv', required=True)
    ap.add_argument('--dossier-projet', required=True); ap.add_argument('--fda', default=None); ap.add_argument('--sortie', required=True)
    a = ap.parse_args()
    P = lambda n: os.path.join(a.dossier_projet, n)

    guid = lire_guidelines(a.ga)

    rel = pd.read_csv(a.rel, sep='\t', dtype=str).fillna('')
    gc = rel[(rel.Entity1_type == 'Gene') & (rel.Entity2_type == 'Chemical')].copy()
    gc['drug'] = gc.Entity2_name.map(norm)
    etiq = collections.defaultdict(set); clin = collections.defaultdict(set)
    for _, r in gc.iterrows():
        if 'LabelAnnotation' in r.Evidence: etiq[r.drug].add(r.Entity1_name)
        if 'ClinicalAnnotation' in r.Evidence and r.Association == 'associated': clin[r.drug].add(r.Entity1_name)

    cv = pd.read_csv(a.cv, sep='\t', dtype=str).fillna('')
    niv = {}
    for _, r in cv.iterrows():
        for c in r['chemicals'].split(','):
            c = norm(c)
            if c and (c not in niv or ORDRE_NIVEAU.index(r['level of evidence']) < ORDRE_NIVEAU.index(niv[c])): niv[c] = r['level of evidence']

    mono = pd.read_csv(P('regles_v2_monogene.csv')); multi = pd.read_csv(P('regles_v2_multigene.csv'))
    regles = collections.defaultdict(lambda: {'n': 0, 'ambigu': 0, 'cond': 0, 'codage': 0, 'conflit': 0, 'sources': set(), 'genes': set()})
    for _, r in mono.iterrows():
        o = regles[norm(r.medicament)]; o['n'] += 1; o['ambigu'] += bool(r.ambigu); o['cond'] += bool(r.conditionnel)
        o['codage'] += bool(r.codage_a_valider); o['conflit'] += bool(r.conflit_intra_source); o['sources'].add(r.source); o['genes'].add(r.gene)
    for _, r in multi.iterrows():
        o = regles[norm(r.medicament)]; o['n'] += 1; o['ambigu'] += bool(r.ambigu); o['cond'] += bool(r.conditionnel)
        o['conflit'] += bool(r.conflit_intra_source); o['sources'].add(r.source); o['genes'] |= {r.gene_a, r.gene_b}

    cov = pd.read_csv(P('corpus_v3_couverture_par_medicament.csv'))
    etiquete = set(cov.loc[cov['v3'] > 0, 'drug'].map(norm))
    d530 = set(pd.read_csv(P('dataset_ORIGINAL_39259.csv'), usecols=['drug'])['drug'].map(norm))

    liste152 = [norm(x) for x in LISTE_152.replace('Streptomycin, Succinylcholine', 'Streptomycin, Succinylcholine').split(', ')]
    d152 = set(liste152)

    fda = {}
    if a.fda and os.path.exists(a.fda):
        f = pd.read_csv(a.fda).fillna('')
        for _, r in f.iterrows():
            genes = set(re.findall(r'[A-Z][A-Z0-9\-]{2,}', r.bio)) & GENES_50
            if genes:
                for tok in {norm(r.drug)}:
                    fda.setdefault(tok, set()).update(genes)

    univers = set(guid) | set(etiq) | set(clin) | d530 | d152 | set(regles) | {d for d, l in niv.items() if l in ('1A', '1B', '2A', '2B')}
    lignes = []
    for d in sorted(univers):
        G = guid.get(d); R = regles.get(d)
        fda_g = set()
        for k, v in fda.items():
            if k == d or re.search(r'(^|[ /,])' + re.escape(d) + r'($|[ /,])', k): fda_g |= v
        genes_all = set()
        if G: genes_all |= G['genes']
        genes_all |= etiq.get(d, set()) & GENES_50 | fda_g
        lignes.append({
            'medicament': d,
            'dans_corpus_530': d in d530, 'etiquete_corpus_v3': d in etiquete, 'dans_liste_152_article': d in d152,
            'guideline_sources': ';'.join(sorted(G['sources'])) if G else '',
            'guideline_n': len(G['ids']) if G else 0,
            'guideline_dosage': bool(G and G['dosing']), 'guideline_alternative': bool(G and G['alt']), 'guideline_test': bool(G and G['test']),
            'guideline_genes': ';'.join(sorted(G['genes'])) if G else '',
            'regles_v2_n': R['n'] if R else 0, 'regles_v2_sources': ';'.join(sorted(R['sources'])) if R else '',
            'regles_ambigues': R['ambigu'] if R else 0, 'regles_conditionnelles': R['cond'] if R else 0,
            'regles_codage_a_valider': R['codage'] if R else 0, 'regles_conflit': R['conflit'] if R else 0,
            'etiquette_reglementaire_pharmgkb': d in etiq, 'etiquette_genes': ';'.join(sorted(etiq.get(d, set()) & GENES_50)),
            'table_fda_2025_genes_des_50': ';'.join(sorted(fda_g)),
            'pharmgkb_niveau_variant_meilleur': niv.get(d, ''),
            'pharmgkb_annotations_cliniques_genes': ';'.join(sorted(clin.get(d, set()))),
            'genes_des_50_impliques': ';'.join(sorted(genes_all & GENES_50)),
            'genes_hors_12_entree': ';'.join(sorted((genes_all & GENES_50) - GENES_12_ENTREE)),
        })
    df = pd.DataFrame(lignes)

    def palier(r):
        if r.etiquete_corpus_v3: return 'P1_etiquete_corpus_v3'
        if r.guideline_n > 0 and r.regles_v2_n > 0: return 'P1b_guideline_regles_exclues'
        if r.guideline_n > 0: return 'P1c_guideline_sans_regle_extraite'
        if r.etiquette_genes or r.table_fda_2025_genes_des_50: return 'P2_etiquette_reglementaire_gene_des_50'
        if r.pharmgkb_niveau_variant_meilleur in ('1A', '1B', '2A', '2B'): return 'P3_association_niveau_2B_ou_mieux'
        return 'P4_autre'
    df['palier_provisoire'] = df.apply(palier, axis=1)
    df.to_csv(a.sortie, index=False)

    print('Registre :', len(df), 'médicaments ->', a.sortie)
    print(df.palier_provisoire.value_counts().to_string())
    print('\nGuidelines (217) par organisme :', {s: sum(1 for d in guid.values() if s in d['sources']) for s in sorted({x for d in guid.values() for x in d['sources']})}, '(nombre de médicaments par organisme)')
    print('Médicaments avec au moins une guideline :', int((df.guideline_n > 0).sum()))
    print('  dont dans le corpus 530 :', int(((df.guideline_n > 0) & df.dans_corpus_530).sum()), '| étiquetés corpus v3 :', int(((df.guideline_n > 0) & df.etiquete_corpus_v3).sum()))
    print('Liste 152 (article) : %d lue, %d avec guideline, %d avec étiquette réglementaire PharmGKB, %d étiquetés v3' % (
        len(d152), int(((df.guideline_n > 0) & df.dans_liste_152_article).sum()), int(((df.etiquette_genes != '') & df.dans_liste_152_article).sum()),
        int((df.etiquete_corpus_v3 & df.dans_liste_152_article).sum())))


if __name__ == '__main__':
    main()
