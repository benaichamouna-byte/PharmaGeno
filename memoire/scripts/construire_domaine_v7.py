#!/usr/bin/env python3
"""
construire_domaine_v7.py : construit le DOMAINE DE VALIDITÉ de chaque médicament pour l'application (fichier domaine_v7.json).

Pourquoi : un modèle ne peut apprendre que ce qu'il a vu. Pour chaque médicament, ce script enregistre
  - les gènes qui concernent le médicament (ceux des tables de règles CPIC/DPWG, restreints aux 12 gènes du modèle),
  - les gènes des règles que le modèle NE reçoit PAS (ex. HLA-B pour la phénytoïne) : l'application doit l'afficher,
  - les combinaisons de valeurs de ces gènes présentes dans le corpus d'entraînement (combos_vues),
  - les valeurs des règles jamais vues dans le corpus (règles_non_vues) : pour ces cas le modèle n'a rien à apprendre,
    l'application répondra « non déterminé » au lieu d'une prédiction non fondée.
Les règles ne servent PAS à prédire : seulement à définir quels gènes concernent chaque médicament et à rendre visible ce qui manque.

Usage : python3 construire_domaine_v7.py --data phenotype_drug_dataset_v3_croise.csv --mono regles_v2_monogene.csv --multi regles_v2_multigene.csv --out domaine_v7.json
"""
import argparse, json
import pandas as pd

GENES_MODELE = ['ABCG2', 'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP2D6', 'CYP3A5', 'DPYD', 'F5', 'NUDT15', 'SLCO1B1', 'TPMT', 'UGT1A1']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True); ap.add_argument('--mono', required=True); ap.add_argument('--multi', required=True)
    ap.add_argument('--out', default='domaine_v7.json')
    a = ap.parse_args()
    df = pd.read_csv(a.data); mono = pd.read_csv(a.mono); multi = pd.read_csv(a.multi)
    dom = {}
    for m in sorted(df.drug.unique()):
        rm, rg = mono[mono.medicament == m], multi[multi.medicament == m]
        gr = set(rm.gene) | set(rg.gene_a) | set(rg.gene_b)
        genes = sorted(gr & set(GENES_MODELE)); hors = sorted(gr - set(GENES_MODELE))
        d = df[df.drug == m]
        vues = sorted({tuple(float(x) for x in r) for r in d[genes].values}) if genes else []
        # valeurs de règles (par gène) que le corpus ne contient jamais pour ce médicament
        non_vues = []
        for _, r in rm.iterrows():
            if r.gene in GENES_MODELE and float(r.valeur) not in set(d[r.gene].astype(float)):
                non_vues.append(dict(gene=r.gene, valeur=float(r.valeur), action_regle=r.action))
        # une règle conditionnelle ou ambiguë est signalée (traçabilité), pas utilisée pour prédire
        dom[m] = dict(genes=genes, genes_regle_hors_modele=hors, combos_vues=[list(c) for c in vues],
                      n_lignes=int(len(d)), classes_vues=sorted(d.action.unique().tolist()),
                      regles_non_vues=non_vues,
                      depend_du_genotype=bool(len(d.action.unique()) > 1))
    json.dump(dict(genes_modele=GENES_MODELE, medicaments=dom), open(a.out, 'w'), indent=1, ensure_ascii=False)
    n_dep = sum(v['depend_du_genotype'] for v in dom.values())
    n_nv = {m: v['regles_non_vues'] for m, v in dom.items() if v['regles_non_vues']}
    print('Médicaments :', len(dom), '| dont étiquette variable dans le corpus :', n_dep)
    print('Médicaments dont au moins une valeur de règle n\'est jamais vue dans le corpus :', len(n_nv))
    for m, l in n_nv.items():
        print('  %-16s classes vues %s | règles non vues : %s' % (m, dom[m]['classes_vues'],
              '; '.join('%s=%s -> %s' % (x['gene'], x['valeur'], x['action_regle']) for x in l)))
    print('Gènes de règle hors modèle :', {m: v['genes_regle_hors_modele'] for m, v in dom.items() if v['genes_regle_hors_modele']})
    print('Écrit :', a.out)


if __name__ == '__main__':
    main()
