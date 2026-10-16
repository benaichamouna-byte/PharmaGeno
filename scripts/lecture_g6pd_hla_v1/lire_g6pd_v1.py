#!/usr/bin/env python3
"""
lire_g6pd_v1.py : tableau de lecture G6PD à partir des 6 annotations PharmGKB de la guideline CPIC G6PD 2022 (fichiers JSON fournis).
Les médicaments viennent du JSON (relatedChemicals). La catégorie et l'action sont celles LUES dans le texte de chaque annotation
(écrites en dur ci-dessous, avec la citation). Rien n'est déduit hors texte. Article source (PMC10281211) non relu.
Usage : python3 lire_g6pd_v1.py --ga DOSSIER_JSON --sortie g6pd_consignes_v1.csv
"""
import argparse, json, os, re
import pandas as pd

ID = {
 'PA166119846': dict(cat='HAUT_RISQUE', deficient='EVITER', cnsha='EVITER', variable='Activité enzymatique à mesurer (mosaïcisme chez les femmes hétérozygotes)',
                     force_def='Strong (Moderate pour methylene blue et toluidine blue)', force_cnsha='Strong', note='Rasburicase/pegloticase : le risque doit être pesé contre l\'hyperuricémie (texte).'),
 'PA166279621': dict(cat='HAUT_RISQUE_DEPENDANT_DOSE', deficient='EVITER_SAUF_SCHEMAS_PALUDISME', cnsha='EVITER', variable='Activité enzymatique à mesurer',
                     force_def='Strong', force_cnsha='Strong', note='Exceptions cités (OMS/CDC) : 0.75 mg/kg 1x/sem x8 sem ou 45 mg 1x/sem x8 sem avec surveillance ; 0.25 mg/kg dose unique contre P. falciparum.'),
 'PA166279721': dict(cat='RISQUE_MOYEN', deficient='SURVEILLER', cnsha='EVITER', variable='Activité enzymatique à mesurer si jugé nécessaire',
                     force_def='Optional', force_cnsha='Moderate', note='Surveillance plus importante à doses élevées, traitement chronique, infection ou stress oxydant.'),
 'PA166279561': dict(cat='FAIBLE_A_AUCUN_RISQUE_ASPIRINE', deficient='PAS_D_ACTION', cnsha='SURVEILLER', variable='Pas d\'action',
                     force_def='Level C (CPIC)', force_cnsha='non relevé', note='Aspirine <=1 g/j : pas d\'action ; CNSHA : prudence et surveillance. >1 g/j : "no recommendation".'),
 'PA166279741': dict(cat='FAIBLE_A_AUCUN_RISQUE', deficient='PAS_D_ACTION', cnsha='SURVEILLER', variable='Pas d\'action',
                     force_def='Level C (CPIC)', force_cnsha='non relevé', note='Résumé du texte : prudence et surveillance de l\'hémolyse chez les patients CNSHA.'),
 'PA166279481': dict(cat='AUCUNE_RECOMMANDATION', deficient='AUCUNE_RECOMMANDATION', cnsha='AUCUNE_RECOMMANDATION', variable='Aucune recommandation',
                     force_def='Level C (CPIC)', force_cnsha='Level C (CPIC)', note='Citation : pas d\'article publié reliant le médicament à une anémie hémolytique aiguë chez les déficients.'),
}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ga', required=True); ap.add_argument('--sortie', required=True); a = ap.parse_args()
    L = []
    for gid, d in ID.items():
        G = json.load(open(os.path.join(a.ga, gid + '.json'), encoding='utf-8'))['guideline']
        for c in G.get('relatedChemicals', []):
            L.append({'medicament': re.sub(r'\s+', ' ', c['name'].strip().lower()), 'gene': 'G6PD', 'organisme': G['source'], 'id_guideline': gid,
                      'categorie_risque_cpic': d['cat'], 'action_deficient': d['deficient'], 'action_deficient_CNSHA': d['cnsha'],
                      'action_variable_ou_indetermine': d['variable'], 'force_deficient': d['force_def'], 'force_CNSHA': d['force_cnsha'],
                      'note': d['note'], 'statut_lecture': 'lu dans le texte PharmGKB; article source non relu',
                      'lien_pharmgkb': 'https://www.pharmgkb.org/guidelineAnnotation/' + gid})
    out = pd.DataFrame(L).sort_values(['categorie_risque_cpic', 'medicament'])
    out.to_csv(a.sortie, index=False)
    print(len(out), 'lignes,', out.medicament.nunique(), 'médicaments ->', a.sortie)
    print(out.groupby('categorie_risque_cpic').size().to_string())

if __name__ == '__main__':
    main()
