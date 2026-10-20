#!/usr/bin/env python3
"""
valider_vcf_v8.py : valide de bout en bout le lecteur vcf_to_profile_v8.py sur de VRAIS échantillons 1000 Genomes du corpus.
Pour chaque échantillon : (1) construit un VCF patient à un seul échantillon (GRCh38, un enregistrement par variant) à partir des VCF 1KGP par gène du pypgx-bundle ;
(2) lance lire_vcf (PyPGx run-chip-pipeline gène par gène, codage v8) ; (3) compare chaque gène à la valeur du profil d'entraînement (profils_genes_v4.csv).
Écrit dans --sortie : validation_vcf_v8_detail.csv (échantillon x gène : valeur lue, valeur du profil, statut), validation_vcf_v8_resume.csv (par gène), validation_vcf_v8_resume.txt.
Limites : (a) les VCF du bundle sont déjà phasés et contiennent les positions définissantes des gènes : ce test valide la chaîne lecture -> appel -> codage sur des données
propres, pas la robustesse à des VCF cliniques épars ; (b) CYP2D6 n'est pas comparé (jamais appelé) ; (c) les profils d'entraînement des 8 gènes ABCG2, CYP2B6, CYP2C19, CYP2C9,
CYP3A5, DPYD, F5, UGT1A1 viennent du corpus v3 : un écart est attendu pour ABCG2 (~4 %) et CYP2B6 (~7 %), voir concordance_pypgx_corpus_v7_resume.csv ; (d) un échantillon à un seul
patient ne teste pas le chemin « plusieurs échantillons ».
Sélection des échantillons : --echantillons HG00101,NA12878 ou --n 10 (tirage reproductible, graine 42, parmi les échantillons du profil présents dans le bundle ; au moins un échantillon
porteur d'une valeur différente de 1,0 par gène est ajouté quand --enrichir est donné, pour ne pas ne tester que des profils « normaux »).
Usage : python3 valider_vcf_v8.py --bundle ~/pypgx-bundle --profils profils_genes_v4.csv --codage codage_pypgx_valeur_v7.csv --tables tables_cpic_v8.json --workdir val_vcf --sortie val_vcf_sortie --n 10 --enrichir --pgx-python ~/pgxenv/bin/python
"""
import argparse, os, random, sys, time
import numpy as np, pandas as pd
import pysam
import vcf_to_profile_v8 as v8

LONG38 = {'1': 248956422, '2': 242193529, '3': 198295559, '4': 190214555, '5': 181538259, '6': 170805979, '7': 159345973, '8': 145138636, '9': 138394717, '10': 133797422,
          '11': 135086622, '12': 133275309, '13': 114364328, '14': 107043718, '15': 101991189, '16': 90338345, '17': 83257441, '18': 80373285, '19': 58617616, '20': 64444167,
          '21': 46709983, '22': 50818468, 'X': 156040895, 'Y': 57227415}
ORDRE = [str(i) for i in range(1, 23)] + ['X', 'Y']


def construire_vcf(bundle, echantillon, genes, chemin):
    """VCF texte à un échantillon (GRCh38) : tous les enregistrements des VCF 1KGP par gène (une seule fois chacun), triés par chromosome et position."""
    recs, vus = [], set()
    for g in genes:
        f = os.path.join(os.path.expanduser(bundle), '1kgp', 'GRCh38', g + '.vcf.gz')
        if not os.path.exists(f): continue
        v = pysam.VariantFile(f)
        if echantillon not in v.header.samples: continue
        v.subset_samples([echantillon])
        for r in v.fetch():
            c = r.chrom.replace('chr', ''); k = (c, r.pos, r.ref, r.alts)
            if k in vus: continue
            vus.add(k); gt = r.samples[echantillon]; a = gt['GT']
            if a is None or any(x is None for x in a): continue
            sep = '|' if gt.phased else '/'
            recs.append((ORDRE.index(c), r.pos, 'chr%s\t%d\t%s\t%s\t%s\t.\t.\t.\tGT\t%s' % (c, r.pos, r.id or '.', r.ref, ','.join(r.alts or ('.',)), sep.join(str(x) for x in a))))
        v.close()
    recs.sort(key=lambda t: (t[0], t[1]))
    with open(chemin, 'w') as o:
        o.write('##fileformat=VCFv4.2\n')
        for c in ORDRE: o.write('##contig=<ID=chr%s,length=%d>\n' % (c, LONG38[c]))
        o.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t%s\n' % echantillon)
        for _, _, l in recs: o.write(l + '\n')
    return len(recs)


def main():
    ap = argparse.ArgumentParser()
    for k in ('bundle', 'profils', 'codage', 'tables', 'workdir', 'sortie'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--echantillons', default=''); ap.add_argument('--n', type=int, default=0); ap.add_argument('--enrichir', action='store_true')
    ap.add_argument('--pgx-python', default=None, dest='pgx_python')
    a = ap.parse_args(); os.makedirs(a.workdir, exist_ok=True); os.makedirs(a.sortie, exist_ok=True)
    P = pd.read_csv(a.profils).set_index('sample_id')
    ref_vcf = pysam.VariantFile(os.path.join(os.path.expanduser(a.bundle), '1kgp', 'GRCh38', 'NAT2.vcf.gz')); presents = set(ref_vcf.header.samples); ref_vcf.close()
    dispo = [s for s in P.index if s in presents]
    if a.echantillons: choix = [s.strip() for s in a.echantillons.split(',') if s.strip()]
    else:
        rnd = random.Random(42); choix = rnd.sample(dispo, min(a.n or 5, len(dispo)))
        if a.enrichir:   # un échantillon par gène avec une valeur différente de 1,0 (le plus petit identifiant, déterministe) : couvre les cas non « normaux »
            for g in v8.GENES_VCF:
                if g == 'CYP2D6': continue
                for s in sorted(dispo):
                    if s not in choix and P.loc[s, g] == 0.0:
                        choix.append(s); break
    print('Échantillons testés (%d) :' % len(choix), ', '.join(choix), flush=True)
    lignes = []; t0 = time.time()
    for s in choix:
        vcf = os.path.join(a.workdir, s + '.vcf'); n = construire_vcf(a.bundle, s, v8.GENES_VCF, vcf)
        print('\n== %s : VCF patient de %d enregistrements | %.0f s' % (s, n, time.time() - t0), flush=True)
        try:
            res = v8.lire_vcf(vcf, a.bundle, os.path.join(a.workdir, 'run_' + s), a.codage, a.tables, hla=None, echantillon=None, pgx_python=a.pgx_python, verbose=True)
        except Exception as e:
            print('  ÉCHEC pour', s, ':', e); lignes.append(dict(echantillon=s, gene='*', statut='echec_lecteur', motif=str(e)[:300])); continue
        for g in v8.GENES_VCF:
            d = res['detail'][g]; ref = P.loc[s, g]; val = d['valeur']
            if g == 'CYP2D6': st = 'non_compare'
            elif val is None and pd.isna(ref): st = 'identique_manquant'
            elif val is None: st = 'lecteur_manquant_profil_valeur'
            elif pd.isna(ref): st = 'lecteur_valeur_profil_manquant'
            else: st = 'identique' if float(val) == float(ref) else 'different'
            lignes.append(dict(echantillon=s, gene=g, valeur_lue=val, valeur_profil=None if pd.isna(ref) else float(ref), statut=st, genotype_pypgx=d['genotype'], phenotype_utilise=d['phenotype_utilise'], motif=d['motif']))
    D = pd.DataFrame(lignes); D.to_csv(os.path.join(a.sortie, 'validation_vcf_v8_detail.csv'), index=False)
    C = D[(D.gene != '*') & (D.statut != 'non_compare')]
    R = C.groupby('gene').statut.value_counts().unstack(fill_value=0).reset_index(); R['n'] = R.drop(columns='gene').sum(axis=1)
    R['concordance_pct'] = (100 * (R.get('identique', 0) + R.get('identique_manquant', 0)) / R['n']).round(1)
    R.to_csv(os.path.join(a.sortie, 'validation_vcf_v8_resume.csv'), index=False)
    txt = 'Échantillons : %d | comparaisons : %d | identiques (valeur ou manquant) : %d | différentes : %d\n\n%s\n' % (
        len(choix), len(C), int(C.statut.isin(['identique', 'identique_manquant']).sum()), int((~C.statut.isin(['identique', 'identique_manquant'])).sum()), R.to_string(index=False))
    pb = C[~C.statut.isin(['identique', 'identique_manquant'])]
    if len(pb): txt += '\nÉcarts :\n' + pb[['echantillon', 'gene', 'valeur_lue', 'valeur_profil', 'genotype_pypgx', 'phenotype_utilise', 'statut']].to_string(index=False) + '\n'
    open(os.path.join(a.sortie, 'validation_vcf_v8_resume.txt'), 'w').write(txt); print('\n' + txt)

if __name__ == '__main__': main()
