"""
controle_codage_regles_profils_v1.py : contrôle de COHÉRENCE DU CODAGE entre les profils (profils_genes_v4.csv) et les règles réellement utilisées par le corpus v7
(corpus_v7/regles_v7_monogene.csv + regles_v2_corrigees_multigene_v7.csv). Pour chaque gène : valeurs présentes dans les profils / valeurs couvertes par au moins une règle.
Signale (a) une valeur de profil sans aucune règle (profils exclus pour tous les médicaments du gène), (b) une valeur de règle jamais présente dans les profils.
Cas déjà trouvé et corrigé : SLCO1B1 « increased function » = 1.5 (profils) contre 2.0 (règles).
Aucun fichier n'est modifié. Usage : python3 controle_codage_regles_profils_v1.py --profils profils_genes_v4.csv --mono corpus_v7/regles_v7_monogene.csv --multi regles_v2_corrigees_multigene_v7.csv --sortie controle_codage_regles_profils_v1.csv
"""
import argparse
import numpy as np, pandas as pd

def main():
    ap = argparse.ArgumentParser()
    for k in ('profils', 'mono', 'multi', 'sortie'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args()
    P = pd.read_csv(a.profils); mono = pd.read_csv(a.mono); multi = pd.read_csv(a.multi)
    cols = [c for c in P.columns if c != 'sample_id' and not c.endswith(('_source', '_genotype', '_phenotype'))]
    R = {}
    for g, v in zip(mono.gene, mono.valeur): R.setdefault(g, set()).add(float(v))
    for ga, va, gb, vb in zip(multi.gene_a, multi.valeur_a, multi.gene_b, multi.valeur_b):
        R.setdefault(ga, set()).add(float(va)); R.setdefault(gb, set()).add(float(vb))
    rows = []
    for g in cols:
        vc = P[g].value_counts(dropna=True); prof = {float(k): int(v) for k, v in vc.items()}
        regle = R.get(g, set())
        sans = {k: v for k, v in prof.items() if regle and k not in regle}
        jamais = sorted(k for k in regle if k not in prof)
        rows.append(dict(gene=g, nb_manquants=int(P[g].isna().sum()), valeurs_profils=prof, valeurs_regles=sorted(regle) if regle else 'AUCUNE REGLE',
                         profils_valeur_sans_regle=sans if sans else '', valeurs_regle_absentes_des_profils=jamais if jamais else '',
                         statut=('SANS_REGLE' if not regle else 'A_VERIFIER' if (sans or jamais) else 'OK')))
    D = pd.DataFrame(rows); D.to_csv(a.sortie, index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 80)
    print(D.statut.value_counts().to_dict()); print()
    print(D[D.statut != 'OK'][['gene', 'statut', 'valeurs_profils', 'valeurs_regles', 'profils_valeur_sans_regle', 'valeurs_regle_absentes_des_profils']].to_string(index=False))
    print('\nGènes OK :', ', '.join(D[D.statut == 'OK'].gene))

if __name__ == '__main__':
    main()
