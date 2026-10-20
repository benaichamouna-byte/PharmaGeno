#!/usr/bin/env python3
"""
construire_domaine_v8.py : DOMAINE DE VALIDITÉ par médicament pour l'application v8 (domaine_v8.json ; domaine_v7.json reste intact).
Pour chaque médicament du corpus v7 :
  - genes : gènes des règles UTILISABLES (mêmes filtres que le moteur d'étiquetage) ;
  - genes_requis_hors_modele : gènes requis que le modèle ne reçoit pas (ex. RYR1 retiré du modèle) -> l'application l'affiche ;
  - combos_vues : combinaisons de valeurs de ces gènes présentes dans le corpus d'entraînement, une valeur manquante étant notée null
    (un profil à gène manquant ne sera prédit que si ce cas précis a été vu avec une étiquette) ;
  - dans_modele : le médicament a une empreinte, donc une entrée dans le DL (4 médicaments n'en ont pas : référence CPIC seule).
Les règles ne servent PAS à prédire : seulement à définir les gènes concernés et à rendre visible ce que le modèle n'a pas appris.
Usage : python3 construire_domaine_v8.py --data corpus_v7/phenotype_drug_dataset_v7.csv --mono corpus_v7/regles_v7_monogene.csv --multi regles_v2_corrigees_multigene_v7.csv --profils profils_genes_v4.csv --modele resultats_final_v8/modele_final_v8_dl_film_id.pt --out domaine_v8.json
"""
import argparse, json
import numpy as np, pandas as pd, torch
from regle_cpic_v8 import RegleCPIC


def main():
    ap = argparse.ArgumentParser()
    for k in ('data', 'mono', 'multi', 'profils', 'modele', 'out'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args()
    P = pd.read_csv(a.profils, nrows=1); vals = [c for c in P.columns if c != 'sample_id' and not c.endswith(('_source', '_genotype', '_phenotype'))]
    R = RegleCPIC(a.mono, a.multi, vals)
    ck = torch.load(a.modele, map_location='cpu', weights_only=True)
    genes_modele = [g for g in ck['genes'] if not g.endswith('_manquant')]; meds_modele = set(ck['medicaments'])
    df = pd.read_csv(a.data); dom = {}
    for m in sorted(df.drug.unique()):
        d = df[df.drug == m]; gr = R.genes_du_medicament(m)
        vues = sorted({tuple(None if pd.isna(x) else float(x) for x in r) for r in d[gr].values}, key=lambda t: [(-1 if v is None else v) for v in t])
        dom[m] = dict(genes=gr, genes_requis_hors_modele=sorted(set(gr) - set(genes_modele)),
                      genes_regle_hors_profil=sorted(R.genes_toutes_regles.get(m, set()) - set(vals)),
                      combos_vues=[list(c) for c in vues], n_lignes=int(len(d)), classes_vues=sorted(d.action.unique().tolist()),
                      depend_du_genotype=bool(d.action.nunique() > 1), dans_modele=m in meds_modele)
    json.dump(dict(genes_profil=vals, genes_modele=genes_modele, medicaments=dom), open(a.out, 'w'), indent=1, ensure_ascii=False)
    print('Médicaments :', len(dom), '| dans le modèle :', sum(v['dans_modele'] for v in dom.values()), '| étiquette variable :', sum(v['depend_du_genotype'] for v in dom.values()))
    print('Hors modèle (référence CPIC seule) :', [m for m, v in dom.items() if not v['dans_modele']])
    print('Gènes requis que le modèle ne reçoit pas :', {m: v['genes_requis_hors_modele'] for m, v in dom.items() if v['genes_requis_hors_modele']})
    print('Gènes de règle absents du profil :', {m: v['genes_regle_hors_profil'] for m, v in dom.items() if v['genes_regle_hors_profil']})
    print('Écrit :', a.out)

if __name__ == '__main__': main()
