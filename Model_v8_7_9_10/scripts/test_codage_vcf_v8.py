#!/usr/bin/env python3
"""
test_codage_vcf_v8.py : vérifie que le codage de vcf_to_profile_v8.coder_gene redonne, à partir des GÉNOTYPES PyPGx enregistrés dans profils_genes_v4.csv,
EXACTEMENT les valeurs des profils d'entraînement, pour les 10 gènes dont le codage dépend du génotype (G6PD, NAT2, CYP3A4, CFTR, NUDT15, TPMT, SLCO1B1, VKORC1, CYP4F2).
Ce test ne lance PAS PyPGx et ne lit pas de VCF : il vérifie la logique de codage et les tables CPIC (tables_cpic_v8.json), pas l'appel d'allèles.
Pour les 8 gènes codés par phénotype PyPGx (ABCG2, CYP2B6, CYP2C19, CYP2C9, CYP3A5, DPYD, F5, UGT1A1), le phénotype PyPGx n'est pas enregistré dans les profils :
seuls des tests unitaires du codage sont faits ici (T2) ; la concordance avec les profils se mesure par valider_vcf_v8.py sur de vrais VCF.
Usage : python3 test_codage_vcf_v8.py --profils profils_genes_v4.csv --codage codage_pypgx_valeur_v7.csv --tables tables_cpic_v8.json
"""
import argparse, sys
import numpy as np, pandas as pd
import vcf_to_profile_v8 as v8


def main():
    ap = argparse.ArgumentParser()
    for k in ('profils', 'codage', 'tables'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args(); ok = True
    P = pd.read_csv(a.profils).set_index('sample_id'); codage = v8.charger_codage(a.codage); tables, meta = v8.charger_tables(a.tables)
    print('Tables CPIC : PharmCAT', meta['commit'][:8], meta['date_commit'], meta['n_diplotypes'])
    print('\nT1 : codage à partir du génotype PyPGx enregistré vs valeur du profil d\'entraînement')
    for g in ['G6PD', 'NAT2', 'CYP3A4', 'CFTR', 'NUDT15', 'TPMT', 'SLCO1B1', 'VKORC1', 'CYP4F2']:
        gt = P[g + '_genotype']; phen = P['G6PD_phenotype'] if g == 'G6PD' else pd.Series([None] * len(P), index=P.index)
        res = [v8.coder_gene(g, (x if isinstance(x, str) else None), (p if isinstance(p, str) else None), tables, codage) for x, p in zip(gt, phen)]
        val = pd.Series([r[0] for r in res], index=P.index, dtype=float); ref = P[g].astype(float)
        diff = ~((val == ref) | (val.isna() & ref.isna())); n = int(diff.sum())
        print('  %-8s profils %d | valeurs identiques %d | différentes %d | manquants (profil / codage) %d / %d' % (g, len(P), len(P) - n, n, int(ref.isna().sum()), int(val.isna().sum())))
        if n:
            ok = False; print(pd.DataFrame(dict(genotype=gt[diff], profil=ref[diff], codage=val[diff])).drop_duplicates().head(8).to_string())
    print('\nT2 : tests unitaires')
    cas = [('CYP2C19', None, 'Poor Metabolizer', 0.0), ('CYP2C19', None, 'Indeterminate', None), ('ABCG2', None, 'Decreased Function', 0.5), ('CYP2B6', None, 'Rapid Metabolizer', 1.5),
           ('G6PD', None, 'G6PD Indeterminate', None), ('CFTR', 'Reference/Reference', 'Indeterminate', 1.0), ('CFTR', 'Reference/F508del', None, None),
           ('VKORC1', 'rs9923231/rs9923231', None, 0.0), ('VKORC1', 'Reference/Reference', None, 1.0), ('CYP4F2', '*3/*4', None, 0.0), ('CYP4F2', '*1/*1', None, 1.0),
           ('CYP2D6', '*1/*1', 'Normal Metabolizer', None), ('NAT2', 'texte_invalide', None, None), ('TPMT', None, None, None)]
    for g, gt, ph, att in cas:
        v = v8.coder_gene(g, gt, ph, tables, codage)[0]; bon = (v == att) or (v is None and att is None); ok &= bon
        print('  %-8s %-22s %-28s attendu %-5s obtenu %-5s %s' % (g, gt, ph, att, v, 'OK' if bon else 'ÉCHEC'))
    print('\nT3 : saisie HLA')
    h = v8.lire_hla('HLA-B*57:01=non_porteur,HLA-B*15:02=inconnu,HLA-A*31:01=porteur'); bon = h == {'HLA-B*15:02': None, 'HLA-B*57:01': 0.0, 'HLA-B*58:01': None, 'HLA-A*31:01': 1.0}; ok &= bon
    print('  lecture :', h, 'OK' if bon else 'ÉCHEC')
    for mauvais in ('HLA-B*99:99=porteur', 'HLA-B*57:01=oui'):
        try: v8.lire_hla(mauvais); ok = False; print('  ÉCHEC : accepté :', mauvais)
        except ValueError as e: print('  refusé comme attendu :', mauvais)
    print('\nT4 : chrX haploïde (homme) converti en homozygote diploïde ; chrX diploïde (femme) et autosomes inchangés')
    import os, tempfile, pysam
    d = tempfile.mkdtemp(); p = os.path.join(d, 't.vcf')
    open(p, 'w').write('##fileformat=VCFv4.2\n##contig=<ID=chr1,length=248956422>\n##contig=<ID=chrX,length=156040895>\n##FORMAT=<ID=GT,Number=1,Type=String,Description="g">\n'
                       '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\thomme\tfemme\n'
                       'chr1\t100\t.\tA\tG\t.\t.\t.\tGT\t0|1\t1|1\nchrX\t154531390\t.\tA\tG\t.\t.\t.\tGT\t1\t0|1\nchrX\t154531400\t.\tC\tT\t.\t.\t.\tGT\t0\t1|1\n')
    q = pysam.VariantFile(p); b = os.path.join(d, 't.vcf.gz'); o = pysam.VariantFile(b, 'wz', header=q.header)
    for r in q: o.write(r)
    o.close(); pysam.tabix_index(b, preset='vcf', force=True)
    res, n = v8.normaliser_chrX_haploide(b, d); w = pysam.VariantFile(res)
    lu = [(r.contig, tuple(r.samples['homme']['GT']), tuple(r.samples['femme']['GT'])) for r in w]
    bon = n == 2 and lu == [('chr1', (0, 1), (1, 1)), ('chrX', (1, 1), (0, 1)), ('chrX', (0, 0), (1, 1))]; ok &= bon
    print('  convertis :', n, '| enregistrements :', lu, 'OK' if bon else 'ÉCHEC')
    print('\nRÉSULTAT :', 'TOUS LES TESTS PASSENT' if ok else 'ÉCHEC'); sys.exit(0 if ok else 1)

if __name__ == '__main__': main()
