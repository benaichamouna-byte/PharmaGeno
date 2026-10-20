#!/usr/bin/env python3
"""
construire_profils_genes_v3.py : table des profils génétiques RÉELS (1 379 échantillons 1000 Genomes x 31 gènes) pour le corpus v5.
Correction par rapport à la v2 : CYP4F2 compte désormais les allèles *3 ET *4 (dans PyPGx, *4 = variant de *3 (V433M, chr19:15879621 GRCh38) + variant de *2) ;
la v2 ne comptait que *3 et sous-estimait 279 profils sur 1 379. Vérifié contre GeT-RM (20/20 contre 16/20). Aucune règle du corpus n'utilise CYP4F2.
Aucun fichier existant n'est modifié.
Sources (une par gène, écrite dans la colonne <gène>_source) :
  - 12 gènes déjà validés (ABCG2, CYP2B6, CYP2C19, CYP2C9, CYP2D6, CYP3A5, DPYD, F5, NUDT15, SLCO1B1, TPMT, UGT1A1) : valeurs reprises du corpus v3 croisé, inchangées.
  - G6PD : phénotype CPIC calculé par PyPGx 0.27.0 (Normal / Variable / Deficient / Indeterminate).
  - NAT2, CYP3A4 : génotype PyPGx 0.27.0 -> phénotype par les tables CPIC distribuées dans le dépôt PharmCAT (phenotype/<GENE>.json).
  - RYR1, CACNA1S, CFTR : phénotype PharmCAT/CPIC (table diplotype -> phénotype) sur le génotype PyPGx.
  - VKORC1 (rs9923231) et CYP4F2 (*3 ou *4 = V433M) : nombre d'allèles variants lu dans le génotype PyPGx.
  - HLA-B*15:02, *57:01, *58:01, HLA-A*31:01 : typages publiés dbMHC (hla_profils_v1.csv) ; non typé -> valeur manquante.
  - ADRB2, MTHFR, CYP1A2, CYP2A6, IFNL3 : génotype conservé en texte ; PAS de valeur (aucune table de fonction CPIC/PharmCAT ; IFNL3 : PyPGx lit rs12980275, pas rs12979860 de CPIC).
  - ACE, EGFR, SLC19A1, MT-RNR1 : aucune donnée 1000 Genomes dans le bundle PyPGx -> valeur manquante.
Codage des valeurs (0 = fonction nulle/risque maximal ... 1 = normal) : voir CODAGE ci-dessous ; codage_a_valider = True pour tout ce qui n'est pas PM/IM/NM.
Usage (environnement pgxenv) : python construire_profils_genes_v3.py --pgxrun pgxrun --corpus phenotype_drug_dataset_v3_croise.csv --hla hla_profils_v1.csv --phenodir DOSSIER_PHENOTYPE_PHARMCAT --sortie profils_genes_v3.csv
"""
import argparse, json, os
import numpy as np, pandas as pd
from pypgx import sdk

OLD12 = ['ABCG2', 'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP2D6', 'CYP3A5', 'DPYD', 'F5', 'NUDT15', 'SLCO1B1', 'TPMT', 'UGT1A1']
GENES31 = ['ABCG2', 'ACE', 'ADRB2', 'CACNA1S', 'CFTR', 'CYP1A2', 'CYP2A6', 'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP2D6', 'CYP3A4', 'CYP3A5', 'CYP4F2', 'DPYD', 'EGFR', 'F5', 'G6PD',
           'HLA-A', 'HLA-B', 'IFNL3', 'MT-RNR1', 'MTHFR', 'NAT2', 'NUDT15', 'RYR1', 'SLC19A1', 'SLCO1B1', 'TPMT', 'UGT1A1', 'VKORC1']
CODAGE = {'Poor Metabolizer': 0.0, 'Intermediate Metabolizer': 0.5, 'Normal Metabolizer': 1.0, 'Rapid Metabolizer': 1.5,  # même codage que codage_pypgx_valeur_v7.csv et regles_v2 (hydralazine : NAT2 rapide = 1.5)
          'G6PD Deficient': 0.0, 'G6PD Variable': 0.5, 'G6PD Normal': 1.0,
          'Malignant Hyperthermia Susceptibility': 0.0, 'Uncertain Susceptibility': 0.5}  # RYR1/CACNA1S : un résultat négatif n'est PAS « normal » (CPIC) -> 0.5


def arch(run, g, kind):
    p = os.path.join(run, g, kind + '.zip')
    return sdk.Archive.from_file(p).data.iloc[:, 0] if os.path.exists(p) else None


def pharmcat_pheno(phdir, gene):
    d = json.load(open(os.path.join(phdir, gene + '.json')))
    T = {}
    for x in d['diplotypes']:
        T[frozenset(x['diplotypekey'].items())] = x['phenotype']
    return T


def lookup(T, gt):
    a = gt.split('/')
    if len(a) != 2: return None
    k = frozenset({a[0]: 1}.items()) if a[0] == a[1] and False else None
    cnt = {}
    for x in a: cnt[x] = cnt.get(x, 0) + 1
    return T.get(frozenset(cnt.items()))


def n_alt(gt, ref=('Reference', '*1')):
    return sum(1 for x in gt.split('/') if x not in ref)


def main():
    ap = argparse.ArgumentParser()
    for k in ('pgxrun', 'corpus', 'hla', 'phenodir', 'sortie'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args()
    c = pd.read_csv(a.corpus)
    base = c.drop_duplicates('sample_id').set_index('sample_id')[OLD12].astype(float)
    ids = list(base.index)
    P = pd.DataFrame(index=ids, columns=GENES31, dtype=float)
    S = pd.DataFrame(index=ids, columns=[g + '_source' for g in GENES31], dtype=object)
    GT = pd.DataFrame(index=ids)
    for g in OLD12:
        P[g] = base[g]; S[g + '_source'] = 'corpus_v3_valide'
    note = []
    # G6PD
    ph = arch(a.pgxrun, 'G6PD', 'phenotypes'); gt = arch(a.pgxrun, 'G6PD', 'genotypes')
    P['G6PD'] = ph.reindex(ids).map(CODAGE); S['G6PD_source'] = 'PyPGx 0.27.0 (phénotype CPIC)'; GT['G6PD_genotype'] = gt.reindex(ids); GT['G6PD_phenotype'] = ph.reindex(ids)
    # gènes via tables CPIC (PharmCAT)
    for g in ('NAT2', 'CYP3A4', 'RYR1', 'CACNA1S', 'CFTR'):
        gt = arch(a.pgxrun, g, 'genotypes')
        if gt is None: note.append(g + ' : absent'); continue
        T = pharmcat_pheno(a.phenodir, g)
        phn = gt.reindex(ids).map(lambda s: lookup(T, s) if isinstance(s, str) else None)
        GT[g + '_genotype'] = gt.reindex(ids); GT[g + '_phenotype'] = phn
        if g == 'CFTR':
            val = phn.map(lambda p: 0.5 if isinstance(p, str) and 'responsive' in p and 'non' not in p else (0.0 if isinstance(p, str) and 'non' in p else np.nan))
            val = val.where(phn.notna(), np.nan)
            val = pd.Series([v if not np.isnan(v) else (1.0 if (isinstance(s, str) and set(s.split('/')) == {'Reference'}) else np.nan) for v, s in zip(val, gt.reindex(ids))], index=ids)
            P[g] = val
        else:
            P[g] = phn.map(CODAGE)
        S[g + '_source'] = 'PyPGx 0.27.0 + table phénotype CPIC (PharmCAT)'
        note.append('%s : %d profils sans phénotype CPIC' % (g, int(P[g].isna().sum())))
    # VKORC1 rs9923231 et CYP4F2 *3
    gt = arch(a.pgxrun, 'VKORC1', 'genotypes'); GT['VKORC1_genotype'] = gt.reindex(ids)
    n = gt.reindex(ids).map(lambda s: sum(1 for x in s.split('/') if x == 'rs9923231') if isinstance(s, str) else np.nan)
    other = gt.reindex(ids).map(lambda s: any(x not in ('Reference', 'rs9923231') for x in s.split('/')))
    P['VKORC1'] = n.map({0: 1.0, 1: 0.5, 2: 0.0}); S['VKORC1_source'] = 'PyPGx 0.27.0 (nombre d\'allèles rs9923231)'
    note.append('VKORC1 : profils avec un autre allèle que rs9923231 : %d' % int(other.sum()))
    gt = arch(a.pgxrun, 'CYP4F2', 'genotypes'); GT['CYP4F2_genotype'] = gt.reindex(ids)
    n = gt.reindex(ids).map(lambda s: sum(1 for x in s.split('/') if x in ('*3', '*4')) if isinstance(s, str) else np.nan)
    P['CYP4F2'] = n.map({0: 1.0, 1: 0.5, 2: 0.0}); S['CYP4F2_source'] = 'PyPGx 0.27.0 (nombre d\'allèles *3 ou *4 = V433M)'
    # génotype seul
    for g in ('ADRB2', 'MTHFR', 'CYP1A2', 'CYP2A6', 'IFNL3'):
        gt = arch(a.pgxrun, g, 'genotypes')
        if gt is not None: GT[g + '_genotype'] = gt.reindex(ids)
        S[g + '_source'] = 'génotype PyPGx conservé ; pas de table de fonction -> valeur manquante'
    for g in ('ACE', 'EGFR', 'SLC19A1', 'MT-RNR1'): S[g + '_source'] = 'aucune donnée 1000 Genomes dans le bundle PyPGx -> valeur manquante'
    # HLA
    h = pd.read_csv(a.hla).set_index('sample_id').reindex(ids)
    H = pd.DataFrame(index=ids)
    for col, gene in (('HLA-B*15:02', 'HLA-B'), ('HLA-B*57:01', 'HLA-B'), ('HLA-B*58:01', 'HLA-B'), ('HLA-B*15:11', 'HLA-B'), ('HLA-A*31:01', 'HLA-A'), ('HLA-A*02:01', 'HLA-A')):
        typed = h[gene + '_source'].notna() & (h[gene + '_source'] != 'non_type')
        v = h[col].map({'certain': 1.0, 'possible': 0.5, 'absent': 0.0})
        H[col] = v.where(typed, np.nan)
    S['HLA-A_source'] = 'dbMHC (hla_profils_v1.csv)'; S['HLA-B_source'] = 'dbMHC (hla_profils_v1.csv)'
    out = pd.concat([P, H, GT, S], axis=1); out.index.name = 'sample_id'
    out.to_csv(a.sortie)
    print('profils :', len(out), '| colonnes :', out.shape[1])
    print('valeurs non manquantes par gène :'); print(P.notna().sum().to_string())
    for g in ('G6PD', 'NAT2', 'CYP3A4', 'RYR1', 'CACNA1S', 'CFTR', 'VKORC1', 'CYP4F2'): print(g, P[g].value_counts(dropna=False).sort_index().to_dict())
    print('HLA typés :'); print(H.notna().sum().to_string()); print('HLA porteurs (certain=1, possible=0.5) :'); print(H.apply(lambda s: s.value_counts().to_dict()).to_string())
    print('\n'.join(note))

if __name__ == '__main__': main()
