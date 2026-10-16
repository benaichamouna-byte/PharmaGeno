#!/usr/bin/env python3
"""
normaliser_hla_dbmhc_v1.py : normalise les typages HLA dbMHC (sortie de extraire_hla_dbmhc_v1.py) en allèles à 2 champs (ex. 57:01) et les joint
aux profils 1000 Genomes du corpus (colonne sample_id). Ne modifie aucun fichier d'entrée.
Règles : liste ambiguë "a/b/c" -> ensemble de candidats ; ancien format B*5701 / B*070201 converti en 57:01 / 07:02 ;
statut par allèle cible : 'certain' (tous les candidats d'au moins une copie = la cible), 'possible' (la cible est parmi les candidats), 'absent'.
Source préférée : PA 0811 (étiquette des 1000 Genomes dans dbMHC, provenance probable Gourraud 2014, NON prouvée), sinon "cell 050808".
Usage : python3 normaliser_hla_dbmhc_v1.py --brut hla_1000g_dbmhc_brut_v1.csv --profils phenotype_drug_dataset_v3_croise.csv --sortie hla_profils_v1.csv
"""
import argparse, re
import pandas as pd

CIBLES = {'HLA-B': ['15:02', '15:11', '57:01', '58:01'], 'HLA-A': ['31:01', '02:01']}


def cands(x):
    out = set()
    for a in str(x).split('/'):
        a = re.sub(r'^[A-Za-z0-9]+\*', '', a.strip())
        if re.search(r'\d[A-Za-z]$', a):
            a = a[:-1]
        if ':' in a:
            p = a.split(':')[:2]
        else:
            m = re.match(r'^(\d{2})(\d{2})', a)
            if not m:
                continue
            p = [m.group(1), m.group(2)]
        if len(p) == 2:
            out.add(':'.join(p))
    return out


def statut(c1, c2, t):
    if any(c == {t} for c in (c1, c2)):
        return 'certain'
    return 'possible' if any(t in c for c in (c1, c2)) else 'absent'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--brut', required=True); ap.add_argument('--profils', required=True); ap.add_argument('--sortie', required=True)
    a = ap.parse_args()
    d = pd.read_csv(a.brut, dtype=str)
    prof = pd.read_csv(a.profils, usecols=['sample_id'], dtype=str).drop_duplicates()
    d['c1'] = d.allele1.map(cands); d['c2'] = d.allele2.map(cands)
    d['src'] = d.load_info.map({'PA 0811': 'PA0811', 'cell 050808': 'cell'})
    best = d.sort_values('src').drop_duplicates(['id', 'locus_name'], keep='first')
    out = prof.copy()
    for loc, ts in CIBLES.items():
        x = best[best.locus_name == loc].set_index('id')
        out[loc + '_source'] = out.sample_id.map(x.src)
        out[loc + '_allele1_brut'] = out.sample_id.map(x.allele1); out[loc + '_allele2_brut'] = out.sample_id.map(x.allele2)
        for t in ts:
            st = {i: statut(r.c1, r.c2, t) for i, r in x.iterrows()}
            out[loc + '*' + t] = out.sample_id.map(st).fillna('non_type')
    out.to_csv(a.sortie, index=False)
    print(len(out), 'profils ->', a.sortie)
    print('profils avec HLA-B dbMHC :', int(out['HLA-B_source'].notna().sum()), '| sans :', int(out['HLA-B_source'].isna().sum()))
    print(out['HLA-B_source'].value_counts(dropna=False).to_string())
    for c in [c for c in out.columns if '*' in c and not c.endswith('brut')]:
        print(c, out[c].value_counts().to_dict())


if __name__ == '__main__':
    main()
