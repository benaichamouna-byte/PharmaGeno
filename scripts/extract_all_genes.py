import pysam
import pandas as pd
import numpy as np
from collections import defaultdict

OUTPUT_DIR = '/home/mouna/projet_memoire/data/vcf_genes/'

# Mapping gène -> chromosome, région, variant clé, encodage phénotype
GENES_CONFIG = {
    'VKORC1': {
        'chr': 'chr16', 'start': 31096000, 'end': 31112000,
        'rsid': 'rs9923231',
        'encode': {
            # rs9923231 C>T : TT=Sensitive(0.0), CT=Intermediate(0.5), CC=Normal(1.0)
            # allele T = risk allele (warfarine dose réduite)
            (0,0): 1.0,  # CC = Normal
            (0,1): 0.5,  # CT = Intermediate
            (1,0): 0.5,  # TC = Intermediate
            (1,1): 0.0,  # TT = Sensitive (Poor)
        }
    },
    'IFNL3': {
        'chr': 'chr19', 'start': 39729000, 'end': 39741000,
        'rsid': 'rs12979860',
        'encode': {
            # rs12979860 C>T : CC=Favorable(1.0), CT=Intermediate(0.5), TT=Unfavorable(0.0)
            (0,0): 1.0,  # CC = Favorable Response
            (0,1): 0.5,  # CT = Intermediate
            (1,0): 0.5,
            (1,1): 0.0,  # TT = Unfavorable Response
        }
    },
    'G6PD': {
        'chr': 'chrX', 'start': 154530000, 'end': 154542000,
        'rsid': 'rs1050828',
        'encode': {
            # rs1050828 G>A : GG/G=Normal(1.0), GA=Carrier(0.5), AA/A=Deficient(0.0)
            (0,0): 1.0,  # GG = Normal
            (0,1): 0.5,  # GA = Carrier
            (1,0): 0.5,
            (1,1): 0.0,  # AA = Deficient
        }
    },
    'NAT2': {
        'chr': 'chr8', 'start': 18248000, 'end': 18261000,
        'rsid': 'rs1799930',
        'encode': {
            # rs1799930 G>A : 2 slow alleles=Poor(0.0), 1 slow=Intermediate(0.5), 0 slow=Normal(1.0)
            (0,0): 1.0,  # GG = Normal/Rapid
            (0,1): 0.5,  # GA = Intermediate
            (1,0): 0.5,
            (1,1): 0.0,  # AA = Slow (Poor)
        }
    },
    'CYP4F2': {
        'chr': 'chr19', 'start': 15989000, 'end': 16009000,
        'rsid': 'rs2108622',
        'encode': {
            # rs2108622 C>T : CC=Normal(1.0), CT=Intermediate(0.5), TT=Poor(0.0)
            (0,0): 1.0,
            (0,1): 0.5,
            (1,0): 0.5,
            (1,1): 0.0,
        }
    },
    'CYP1A2': {
        'chr': 'chr15', 'start': 74715000, 'end': 74762000,
        'rsid': 'rs762551',
        'encode': {
            # rs762551 A>C : AA=Rapid(2.0), AC=Normal(1.0), CC=Poor(0.0)
            (0,0): 2.0,  # AA = Rapid
            (0,1): 1.0,  # AC = Normal
            (1,0): 1.0,
            (1,1): 0.0,  # CC = Poor
        }
    },
    'CYP2A6': {
        'chr': 'chr19', 'start': 40842000, 'end': 40851000,
        'rsid': 'rs1801272',
        'encode': {
            # rs1801272 A>T : AA=Normal(1.0), AT=Intermediate(0.5), TT=Poor(0.0)
            (0,0): 1.0,
            (0,1): 0.5,
            (1,0): 0.5,
            (1,1): 0.0,
        }
    },
    'CYP3A4': {
        'chr': 'chr7', 'start': 99757000, 'end': 99784000,
        'rsid': 'rs2740574',
        'encode': {
            # rs2740574 A>G : AA=Normal(1.0), AG=Rapid(1.5), GG=Rapid(2.0)
            (0,0): 1.0,
            (0,1): 1.5,
            (1,0): 1.5,
            (1,1): 2.0,
        }
    },
    'SLC19A1': {
        'chr': 'chr21', 'start': 43822000, 'end': 43837000,
        'rsid': 'rs1051266',
        'encode': {
            # rs1051266 A>G : AA=Normal(1.0), AG=Intermediate(0.5), GG=Poor(0.0)
            (0,0): 1.0,
            (0,1): 0.5,
            (1,0): 0.5,
            (1,1): 0.0,
        }
    },
    'ACE': {
        'chr': 'chr17', 'start': 63477000, 'end': 63498000,
        'rsid': 'rs1799752',
        'encode': {
            # rs1799752 del/ins : II=Normal(1.0), ID=Intermediate(0.5), DD=Poor(0.0)
            (0,0): 1.0,
            (0,1): 0.5,
            (1,0): 0.5,
            (1,1): 0.0,
        }
    },
    'ADRB2': {
        'chr': 'chr5', 'start': 148205000, 'end': 148215000,
        'rsid': 'rs1042713',
        'encode': {
            # rs1042713 G>A : GG=Normal(1.0), GA=Intermediate(0.5), AA=Poor(0.0)
            (0,0): 1.0,
            (0,1): 0.5,
            (1,0): 0.5,
            (1,1): 0.0,
        }
    },
    'MTHFR': {
        'chr': 'chr1', 'start': 11785000, 'end': 11807000,
        'rsid': 'rs1801133',
        'encode': {
            # rs1801133 C>T : CC=Normal(1.0), CT=Intermediate(0.5), TT=Poor(0.0)
            (0,0): 1.0,
            (0,1): 0.5,
            (1,0): 0.5,
            (1,1): 0.0,
        }
    },
}

BASE_URL = "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20201028_3202_raw_GT_with_annot/20201028_CCDG_14151_B01_GRM_WGS_2020-08-05_{chrom}.recalibrated_variants.annotated.vcf.gz"

results = {}

for gene, config in GENES_CONFIG.items():
    chrom = config['chr']
    url = BASE_URL.format(chrom=chrom)
    print(f"\n{'='*50}")
    print(f"Extraction {gene} ({chrom}) — {config['rsid']}")
    
    try:
        with pysam.VariantFile(url) as vcf:
            samples = list(vcf.header.samples)
            print(f"  {len(samples)} échantillons disponibles")
            
            variant_found = None
            for rec in vcf.fetch(chrom, config['start'], config['end']):
                rec_id = str(rec.id) if rec.id else ''
                if config['rsid'] in rec_id:
                    variant_found = rec
                    print(f"  ✅ {config['rsid']} trouvé à position {rec.pos}")
                    break
            
            if variant_found is None:
                print(f"  ❌ {config['rsid']} non trouvé dans la région")
                results[gene] = None
                continue
            
            # Extraire les génotypes
            gene_phenos = {}
            for sample in samples:
                gt = variant_found.samples[sample]['GT']
                if gt is None or None in gt:
                    gene_phenos[sample] = 1.0  # défaut
                else:
                    key = tuple(gt)
                    gene_phenos[sample] = config['encode'].get(key, 1.0)
            
            results[gene] = gene_phenos
            vals = pd.Series(list(gene_phenos.values())).value_counts()
            print(f"  Distribution phénotypes: {vals.to_dict()}")
            
    except Exception as e:
        print(f"  ❌ Erreur: {str(e)[:100]}")
        results[gene] = None

# Résumé
print(f"\n{'='*50}")
print("RÉSUMÉ")
print(f"{'='*50}")
for gene, data in results.items():
    if data:
        non_default = sum(1 for v in data.values() if v != 1.0)
        print(f"✅ {gene}: {len(data)} individus, {non_default} non-défaut")
    else:
        print(f"❌ {gene}: ÉCHEC")

# Sauvegarder
import pickle
with open('/home/mouna/projet_memoire/data/vcf_genotypes_all_genes.pkl', 'wb') as f:
    pickle.dump(results, f)
print("\nRésultats sauvegardés")
