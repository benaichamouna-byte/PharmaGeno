# drug_recommender.py
# Phase 4 - Moteur de recommandation
# Sources : PharmGKB + CPIC + DPWG

import pandas as pd
import json
import os
import sys
sys.path.append('/home/mouna/projet_memoire/scripts')
from vcf_parser import parse_vcf

def load_pharmgkb(tsv_file):
    df = pd.read_csv(tsv_file, sep='\t', low_memory=False)
    df = df[df['Significance'] == 'yes']
    return df

def load_clinical_variants(tsv_file):
    df = pd.read_csv(tsv_file, sep='\t', low_memory=False)
    return df

def load_guidelines(json_dir):
    guidelines = []
    for f in os.listdir(json_dir):
        if f.endswith('.json'):
            try:
                with open(os.path.join(json_dir, f), 'r') as jf:
                    data = json.load(jf)
                    guidelines.append(data)
            except:
                continue
    return guidelines

def get_guideline_source(guidelines, gene):
    sources = []
    for g in guidelines:
        try:
            name = g.get('guideline', {}).get('name', '')
            if gene in name:
                if 'CPIC' in name:
                    sources.append('CPIC')
                if 'DPWG' in name:
                    sources.append('DPWG')
        except:
            continue
    return list(set(sources)) if sources else ['PharmGKB']

def get_recommendations(variants_df, pharmgkb_df, clinical_df, guidelines):
    results = []
    for _, variant in variants_df.iterrows():
        rsid = variant['rsid']
        gene = variant['gene']
        gt   = variant['genotype']

        # Source des guidelines pour ce gène
        sources = get_guideline_source(guidelines, gene)
        source_str = ' + '.join(sources)

        # Chercher dans PharmGKB
        matches = pharmgkb_df[
            pharmgkb_df['Variant/Haplotypes'].str.contains(rsid, na=False)
        ]

        # Chercher niveau de preuve dans clinicalVariants
        clin_match = clinical_df[
            clinical_df['Variant'].str.contains(rsid, na=False)
        ] if 'Variant' in clinical_df.columns else pd.DataFrame()

        level = clin_match.iloc[0]['Level of Evidence'] \
                if not clin_match.empty else '-'

        if matches.empty:
            results.append({
                'gene':             gene,
                'rsid':             rsid,
                'genotype':         gt,
                'drug':             'Aucune recommandation trouvée',
                'phenotype':        '-',
                'level_of_evidence': level,
                'source':           source_str
            })
        else:
            for _, match in matches.iterrows():
                results.append({
                    'gene':             gene,
                    'rsid':             rsid,
                    'genotype':         gt,
                    'drug':             match.get('Drug(s)', '-'),
                    'phenotype':        match.get('Phenotype Category', '-'),
                    'level_of_evidence': level,
                    'source':           source_str
                })
    return pd.DataFrame(results)

def main():
    vcf_file      = '/home/mouna/projet_memoire/data/pharmacat.example2.vcf'
    pharmgkb_file = '/home/mouna/projet_memoire/data/var_drug_ann.tsv'
    clinical_file = '/home/mouna/projet_memoire/data/clinicalVariants.tsv'
    json_dir      = '/home/mouna/projet_memoire/data'

    print("Étape 1 — Lecture du VCF...")
    variants_df = parse_vcf(vcf_file)
    print(f"{len(variants_df)} variants détectés")

    print("\nÉtape 2 — Chargement PharmGKB...")
    pharmgkb_df = load_pharmgkb(pharmgkb_file)
    print(f"{len(pharmgkb_df)} associations chargées")

    print("\nÉtape 3 — Chargement Clinical Variants...")
    clinical_df = load_clinical_variants(clinical_file)
    print(f"{len(clinical_df)} variants cliniques chargés")

    print("\nÉtape 4 — Chargement guidelines CPIC + DPWG...")
    guidelines = load_guidelines(json_dir)
    print(f"{len(guidelines)} guidelines chargées")

    print("\nÉtape 5 — Recommandations...")
    results_df = get_recommendations(
        variants_df, pharmgkb_df, clinical_df, guidelines
    )

    print(f"\n{len(results_df)} recommandations trouvées :")
    print(results_df.to_string(index=False))

    results_df.to_csv(
        '/home/mouna/projet_memoire/results/recommandations.csv',
        index=False
    )
    print("\nSauvegardé dans results/recommandations.csv")

if __name__ == '__main__':
    main()
