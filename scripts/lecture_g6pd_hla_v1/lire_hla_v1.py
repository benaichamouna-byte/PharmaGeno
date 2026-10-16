#!/usr/bin/env python3
"""
lire_hla_v1.py : tableau de lecture HLA (HLA-A, HLA-B) à partir des 20 annotations PharmGKB de guidelines (CPIC, DPWG, CPNDS, ACR, RNPGx), JSON fournis.
Médicaments et organismes viennent du JSON. Allèle et action sont ceux LUS dans le RÉSUMÉ PharmGKB de chaque annotation (texte complet non relu ;
force de recommandation non relevée). Les désaccords entre organismes sont conservés, jamais tranchés.
Usage : python3 lire_hla_v1.py --ga DOSSIER_JSON --sortie hla_consignes_v1.csv
"""
import argparse, json, os, re
import pandas as pd

R = {  # id : (allèles, action provisoire, condition / précision lue dans le résumé)
 'PA166104947': ('HLA-B*44', 'AUCUNE_RECOMMANDATION', 'Pas de recommandation de dose pour ribavirine chez HLA-B*44 positifs'),
 'PA166104991': ('HLA-B*57:01', 'EVITER', ''),
 'PA166104993': ('HLA-B*58:01', 'TESTER_AVANT', 'Test conditionnellement recommandé chez patients d\'ascendance sud-est asiatique ou afro-américaine'),
 'PA166104997': ('HLA-B*57:01', 'EVITER', 'A considérer seulement dans des circonstances exceptionnelles'),
 'PA166105003': ('HLA-B*58:01', 'EVITER', 'Risque accru de SCAR'),
 'PA166105008': ('HLA-B*15:02; HLA-A*31:01', 'EVITER_ALTERNATIVE', 'Patients naïfs de carbamazépine, au moins une copie de l\'allèle ; SJS/TEN (B*15:02, A*31:01), DRESS/MPE (A*31:01)'),
 'PA166117280': ('HLA-A*31:01; HLA-B*15:02', 'EVITER', 'Patients naïfs de carbamazépine, au moins un allèle'),
 'PA166122806': ('HLA-B*15:02', 'EVITER', 'Phénytoïne/fosphénytoïne ; en plus : CYP2C9 métaboliseur lent (score 0 ou 0,5) ou score 1 -> doses réduites possibles'),
 'PA166176623': ('HLA-B*15:02', 'EVITER_ALTERNATIVE', 'Patients naïfs d\'oxcarbazépine, au moins une copie'),
 'PA166182810': ('HLA-B*57:01', 'SURVEILLER', 'Surveiller la fonction hépatique ; alternative si enzymes hépatiques ou bilirubine élevées'),
 'PA166264881': ('HLA-B*15:02', 'EVITER_SI_POSSIBLE', ''),
 'PA166265141': ('HLA-B*58:01', 'ALTERNATIVE_OU_INDUCTION_TOLERANCE', 'Alternative, ou induction de tolérance à l\'allopurinol'),
 'PA166265161': ('HLA-A*31:01', 'ENVISAGER_ALTERNATIVE', ''),
 'PA166265162': ('HLA-B*15:02; HLA-B*15:11', 'ENVISAGER_ALTERNATIVE', ''),
 'PA166265201': ('HLA-B*15:02', 'EVITER_SI_POSSIBLE', 'Si une alternative est disponible'),
 'PA166265341': ('HLA-B*15:02', 'EVITER_SI_POSSIBLE', 'Si impossible : signaler immédiatement toute éruption'),
 'PA166422141': ('HLA-B*57:01', 'CONTRE_INDIQUE', 'Test HLA obligatoire avant prescription (SFHI)'),
 'PA166422161': ('HLA-B*58:01', 'TESTER_AVANT', 'Test avant prescription pour éviter les SCAR (SFHI)'),
 'PA166422181': ('HLA-A*02:01', 'SELECTION_PATIENTS', 'Test pour sélectionner les patients éligibles (mélanome uvéal métastatique) : logique inverse, le médicament exige l\'allèle'),
 'PA166422201': ('HLA-B*15:02; HLA-A*31:01', 'ORIENTATION_SANS_ACTION_DETAILLEE', 'Résumé : "guidance" sur la toxicité ; action non précisée dans le résumé'),
}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ga', required=True); ap.add_argument('--sortie', required=True); a = ap.parse_args()
    L = []
    for gid, (all_, act, cond) in R.items():
        G = json.load(open(os.path.join(a.ga, gid + '.json'), encoding='utf-8'))['guideline']
        for c in G.get('relatedChemicals', []):
            L.append({'medicament': re.sub(r'\s+', ' ', c['name'].strip().lower()), 'organisme': G['source'], 'id_guideline': gid, 'alleles': all_,
                      'action_provisoire': act, 'condition_ou_precision': cond, 'statut_lecture': 'lu dans le résumé PharmGKB; texte complet et force non relus',
                      'lien_pharmgkb': 'https://www.pharmgkb.org/guidelineAnnotation/' + gid})
    out = pd.DataFrame(L).sort_values(['medicament', 'organisme'])
    out.to_csv(a.sortie, index=False)
    print(len(out), 'lignes,', out.medicament.nunique(), 'médicaments ->', a.sortie)
    print(out.groupby('medicament').organisme.apply(lambda s: ','.join(s)).to_string())

if __name__ == '__main__':
    main()
