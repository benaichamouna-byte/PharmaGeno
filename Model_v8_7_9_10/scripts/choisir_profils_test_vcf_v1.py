#!/usr/bin/env python3
"""
choisir_profils_test_vcf_v1.py : choisit 2 profils réels 1000 Genomes pour tester la chaîne complète (VCF -> lecteur -> DL -> écran).

CRITÈRES ÉCRITS AVANT LE TIRAGE (le tirage est aléatoire, graine fixée : aucun profil n'est choisi à la main) :
  1. exclus : les 138 profils de l'ensemble final (data/profils_ensemble_final_v1.txt), HG00101 (déjà testé), les 19 échantillons déjà utilisés
     dans la validation du lecteur (results/validation_vcf_v8/validation_vcf_v8_detail.csv) ;
  2. présent dans les VCF 1KGP du pypgx-bundle (sinon pas de VCF reconstructible) ;
  3. au moins 3 gènes LISIBLES depuis un VCF (hors CYP2D6) avec une valeur différente de 1,0 (profil non « tout normal », donc la combinaison de gènes compte) ;
  4. parmi eux, au moins 2 gènes « clés » (CYP2C19, CYP2C9, SLCO1B1, TPMT, NUDT15, DPYD, UGT1A1, CYP3A5, VKORC1, CYP2B6) et aucune valeur manquante sur ces gènes clés ;
  5. tirage de 2 profils parmi les éligibles avec numpy RandomState(2026).
Usage : python3 choisir_profils_test_vcf_v1.py --data ../data --resultats ../results
"""
import argparse, sys
import numpy as np, pandas as pd
import pysam, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vcf_to_profile_v8 as v8

CLES = ['CYP2C19', 'CYP2C9', 'SLCO1B1', 'TPMT', 'NUDT15', 'DPYD', 'UGT1A1', 'CYP3A5', 'VKORC1', 'CYP2B6']


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data', default='../data'); ap.add_argument('--resultats', default='../results')
    ap.add_argument('--bundle', default=os.path.expanduser('~/pypgx-bundle')); ap.add_argument('--graine', type=int, default=2026)
    a = ap.parse_args()
    P = pd.read_csv(os.path.join(a.data, 'profils_genes_v4.csv')).set_index('sample_id')
    final = {l.strip() for l in open(os.path.join(a.data, 'profils_ensemble_final_v1.txt')) if l.strip() and not l.startswith('#')}
    deja = set(pd.read_csv(os.path.join(a.resultats, 'validation_vcf_v8', 'validation_vcf_v8_detail.csv')).echantillon) | {'HG00101'}
    ref = pysam.VariantFile(os.path.join(a.bundle, '1kgp', 'GRCh38', 'NAT2.vcf.gz')); presents = set(ref.header.samples); ref.close()
    lisibles = [g for g in v8.GENES_VCF if g != 'CYP2D6']
    cles = [g for g in CLES if g in lisibles]
    cand = [s for s in P.index if s in presents and s not in final and s not in deja]
    elig = []
    for s in cand:
        v = P.loc[s, lisibles]
        non_normaux = [g for g in lisibles if pd.notna(v[g]) and v[g] != 1.0]
        cles_nn = [g for g in non_normaux if g in cles]
        if len(non_normaux) >= 3 and len(cles_nn) >= 2 and not P.loc[s, cles].isna().any():
            elig.append((s, non_normaux))
    print('profils du corpus : %d | exclus ensemble final : %d | déjà utilisés : %d | candidats : %d | éligibles : %d' %
          (len(P), len(final), len(deja), len(cand), len(elig)))
    rs = np.random.RandomState(a.graine); idx = rs.choice(len(elig), 2, replace=False)
    for i in idx:
        s, nn = elig[i]
        print('CHOISI :', s, '| gènes non normaux lisibles :', ', '.join('%s=%s' % (g, P.loc[s, g]) for g in nn))
    assert not ({elig[i][0] for i in idx} & final), 'ERREUR : un profil de l ensemble final a été tiré'


if __name__ == '__main__': main()
