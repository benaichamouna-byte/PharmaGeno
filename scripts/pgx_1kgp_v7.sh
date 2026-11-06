#!/bin/bash
# pgx_1kgp_v7.sh : traçabilité du calcul PyPGx 0.27.0 sur les VCF 1KGP du paquet pypgx-bundle (GRCh38), échantillons du corpus uniquement.
# Assemblé à partir des deux petits scripts réellement exécutés (run_pgx_1kgp.sh puis chain.sh) ; cet assemblage n'a pas été relancé tel quel.
# Prérequis : environnement Python isolé avec  pypgx==0.27.0 , "pandas<3" , pysam ;  git clone --branch 0.27.0 https://github.com/sbslee/pypgx-bundle
# Les VCF 1KGP du bundle sont déjà phasés : on n'utilise donc pas Beagle (étape import -> predict-alleles -> call-genotypes -> call-phenotypes).
# Durée observée (2 cœurs, 1 379 échantillons) : de ~10 min (petits gènes) à plus de 35 min de calcul (DPYD, non terminé à la livraison).
# Usage : bash pgx_1kgp_v7.sh GENE CORPUS.csv    (ex. bash pgx_1kgp_v7.sh CYP2C19 phenotype_drug_dataset_v3_croise.csv)
set -e
G=$1; CORPUS=$2; D=pgxrun/$G; mkdir -p $D
python - <<PY
import pysam, pandas as pd
ids = set(pd.read_csv('$CORPUS', usecols=['sample_id']).sample_id)
v = pysam.VariantFile('pypgx-bundle/1kgp/GRCh38/$G.vcf.gz'); keep = [s for s in v.header.samples if s in ids]
v.subset_samples(keep)
o = pysam.VariantFile('$D/sub.vcf.gz', 'wz', header=v.header)
for r in v.fetch(): o.write(r)
o.close(); pysam.tabix_index('$D/sub.vcf.gz', preset='vcf', force=True)
PY
pypgx import-variants $G $D/sub.vcf.gz $D/imported.zip --assembly GRCh38
pypgx predict-alleles $D/imported.zip $D/alleles.zip
pypgx call-genotypes $D/genotypes.zip --alleles $D/alleles.zip
pypgx call-phenotypes $D/genotypes.zip $D/phenotypes.zip
