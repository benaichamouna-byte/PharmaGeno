#!/usr/bin/env python3
"""Construit un VCF multi-échantillons (GRCh38) à partir des VCF 1KGP par gène du pypgx-bundle, pour N profils de DÉVELOPPEMENT tirés au hasard (graine fixée, ensemble final exclu).
Lecture seule des données du projet ; écrit uniquement dans le dossier de sortie."""
import sys, os, random
import numpy as np, pandas as pd, pysam
B = '/tmp/claude-0/-home-claude/8409b04b-17f7-52aa-bb79-1c3b814505b7/scratchpad/p1/pypgx-bundle/1kgp/GRCh38'
D = '/home/claude/appdev/Model_v8_7_9_10/data'
N = int(sys.argv[1]); out = sys.argv[2]; graine = 2026
GENES = ['ABCG2', 'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP3A4', 'CYP3A5', 'CYP4F2', 'DPYD', 'NUDT15', 'SLCO1B1', 'TPMT', 'UGT1A1', 'VKORC1', 'NAT2', 'IFNL3', 'CFTR', 'RYR1', 'CACNA1S']
P = pd.read_csv(os.path.join(D, 'profils_genes_v6_complet.csv')).set_index('sample_id')
final = {l.strip() for l in open(os.path.join(D, 'profils_ensemble_final_v1.txt')) if l.strip() and not l.startswith('#')}
dispo = set(pysam.VariantFile(os.path.join(B, 'TPMT.vcf.gz')).header.samples)
cand = sorted(s for s in P.index if s not in final and s in dispo)
rng = random.Random(graine); ech = sorted(rng.sample(cand, N))
print('candidats %d, tirés %d (graine %d), ensemble final exclu : %d' % (len(cand), len(ech), graine, len(final)))
open(out + '.echantillons.txt', 'w').write('\n'.join(ech) + '\n')
fich = []
for g in GENES:
    f = os.path.join(B, g + '.vcf.gz')
    if not os.path.exists(f): print('absent :', g); continue
    v = pysam.VariantFile(f); r = next(v, None)
    if r is None: continue
    fich.append((r.contig, r.pos, g, f))
def cle(x):
    c = x[0].replace('chr', ''); return (int(c) if c.isdigit() else 99, x[1])
fich.sort(key=cle)
v0 = pysam.VariantFile(fich[0][3]); v0.subset_samples(ech); hdr = v0.header.copy()
for c, _, g, f in fich:
    for ctg in pysam.VariantFile(f).header.contigs.values():
        if ctg.name not in hdr.contigs: hdr.contigs.add(ctg.name, ctg.length)
n = 0
with pysam.VariantFile(out, 'w', header=hdr) as w:
    for c, _, g, f in fich:
        v = pysam.VariantFile(f); v.subset_samples(ech); k = 0
        for r in v:
            rec = w.new_record(contig=r.contig, start=r.start, stop=r.stop, alleles=r.alleles, id=r.id)
            for s in ech: rec.samples[s]['GT'] = r.samples[s]['GT']; rec.samples[s].phased = r.samples[s].phased
            w.write(rec); k += 1
        n += k; print(g, k, 'enregistrements')
print('total', n, '->', out)
