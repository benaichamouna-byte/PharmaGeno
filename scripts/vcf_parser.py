# vcf_parser.py
# Phase 3 - Parseur VCF
# Projet : Mutation-Aware Drug Recommendation

import pandas as pd

def parse_vcf(vcf_file):
    variants = []
    with open(vcf_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            cols = line.strip().split('\t')
            if len(cols) < 8:
                continue
            chrom    = cols[0]
            pos      = cols[1]
            rsid     = cols[2]
            ref      = cols[3]
            alt      = cols[4]
            info     = cols[7]
            # Gérer VCF avec ou sans génotype
            if len(cols) > 9:
                genotype = cols[9]
            else:
                genotype = '1/1'  # VCF sans génotype = variant présent
            gene = None
            for field in info.split(';'):
                if field.startswith('PX='):
                   gene = field.replace('PX=', '')
                   break
                elif field.startswith('GENE='):
                    gene = field.replace('GENE=', '')
                    break
                elif field.startswith('ANN='):
                    ann = field.replace('ANN=', '')
                    parts = ann.split('|')
                    if len(parts) > 3:
                       gene = parts[3]
                    break
            if gene is None:
                continue
            gt = genotype.split(':')[0]
            if gt == '0/0' or gt == './.':
                continue
            variants.append({
                'chromosome': chrom,
                'position':   pos,
                'rsid':       rsid,
                'gene':       gene,
                'ref':        ref,
                'alt':        alt,
                'genotype':   gt
            })
    return pd.DataFrame(variants)

def main():
    vcf_file = '/home/mouna/projet_memoire/data/pharmacat.example2.vcf'
    print("Lecture du fichier VCF...")
    df = parse_vcf(vcf_file)
    print(f"\nNombre de variants avec mutation : {len(df)}")
    print("\nVariants détectés :")
    print(df.to_string(index=False))
    df.to_csv('/home/mouna/projet_memoire/results/variants_extraits.csv', index=False)
    print("\nRésultats sauvegardés dans results/variants_extraits.csv")

if __name__ == '__main__':
    main()
