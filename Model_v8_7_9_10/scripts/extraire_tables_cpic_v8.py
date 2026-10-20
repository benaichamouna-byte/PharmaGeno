#!/usr/bin/env python3
"""
extraire_tables_cpic_v8.py : extrait des tables de phénotype CPIC distribuées dans le dépôt PharmCAT (src/main/resources/org/pharmgkb/pharmcat/phenotype/<GENE>.json)
uniquement la correspondance « diplotype (comptage des allèles) -> phénotype » pour les 6 gènes dont le profil d'entraînement est calculé par cette méthode
(NAT2, CYP3A4, CFTR : construire_profils_genes_v3.py ; NUDT15, TPMT, SLCO1B1 : calculer_phenotypes_cpic_12genes_v1.py / construire_profils_genes_v4.py).
Écrit tables_cpic_v8.json (petit fichier, lu par vcf_to_profile_v8.py) avec la provenance. Ne modifie aucun autre fichier.
Usage : python3 extraire_tables_cpic_v8.py --phenodir DOSSIER_PHENOTYPE_PHARMCAT --depot DOSSIER_DEPOT_PHARMCAT --sortie tables_cpic_v8.json
"""
import argparse, json, os, subprocess
GENES = ['NAT2', 'CYP3A4', 'CFTR', 'NUDT15', 'TPMT', 'SLCO1B1']

def main():
    ap = argparse.ArgumentParser()
    for k in ('phenodir', 'depot', 'sortie'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args(); out = {}
    for g in GENES:
        d = json.load(open(os.path.join(a.phenodir, g + '.json'), encoding='utf-8'))
        out[g] = [[x['diplotypekey'], x['phenotype']] for x in d['diplotypes']]
    git = lambda *c: subprocess.run(['git', '-C', a.depot] + list(c), capture_output=True, text=True).stdout.strip()
    meta = dict(source='PharmCAT, src/main/resources/org/pharmgkb/pharmcat/phenotype/<GENE>.json (tables CPIC diplotype -> phénotype)', commit=git('rev-parse', 'HEAD'),
                date_commit=git('log', '-1', '--format=%ci'), genes=GENES, n_diplotypes={g: len(out[g]) for g in GENES})
    json.dump(dict(meta=meta, tables=out), open(a.sortie, 'w'), ensure_ascii=False, separators=(',', ':'))
    print(json.dumps(meta, indent=1, ensure_ascii=False)); print('écrit :', a.sortie, os.path.getsize(a.sortie), 'octets')

if __name__ == '__main__': main()
