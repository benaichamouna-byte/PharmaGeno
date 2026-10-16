#!/usr/bin/env python3
"""
lire_hla_v2.py : correction et enrichissement de hla_consignes_v1.csv (le v1 reste intact) après lecture des TEXTES COMPLETS (JSON PharmGKB)
pour carbamazepine CPIC, phenytoin CPIC et carbamazepine DPWG (HLA-B), et relevé des forces CPIC par mots-clés.
CORRECTION par rapport au v1 : DPWG carbamazepine HLA-B*15:02 = "Avoid carbamazepine" (le résumé PharmGKB disait seulement "consider an alternative").
Usage : python3 lire_hla_v2.py --entree hla_consignes_v1.csv --sortie hla_consignes_v2.csv
"""
import argparse
import pandas as pd

FORCE = {'PA166104997': 'Strong', 'PA166105003': 'Strong', 'PA166105008': 'A Strong; B et C Optional', 'PA166122806': 'Strong (patients naïfs); Optional (usage antérieur >3 mois)',
         'PA166176623': 'A Strong; B Optional (texte B non lu)'}
TEXTE_COMPLET = {'PA166105008', 'PA166122806', 'PA166265162'}
MAJ = {
 'PA166105008': 'Patients naïfs : ne pas utiliser (porteur B*15:02 ; porteur A*31:01 si alternative disponible). A*31:01 sans alternative : envisager avec surveillance accrue. Usage continu >3 mois sans réaction cutanée : envisager avec prudence (Optional). Autres anticonvulsivants aromatiques : pas de recommandation pour A*31:01.',
 'PA166122806': 'Patients naïfs de phénytoïne : ne pas utiliser ; éviter aussi carbamazépine et oxcarbazépine (Strong). Usage continu >3 mois sans réaction cutanée : envisager avec prudence (Optional). Si HLA-B*15:02 négatif : CYP2C9 score 1 -> environ 25 % de dose d\'entretien en moins ; score 0-0,5 -> environ 50 % en moins (Moderate) ; un test négatif n\'élimine pas le risque.',
 'PA166265162': 'DPWG 2024, B*15:02 positif : "Avoid carbamazepine". Risque SJS/TEN 1,8-7,7 % les 3 premiers mois. Phénytoïne, lamotrigine, oxcarbazépine : risque aussi accru mais 5 à 10 fois plus faible.',
}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--entree', required=True); ap.add_argument('--sortie', required=True); a = ap.parse_args()
    d = pd.read_csv(a.entree).fillna('')
    d['force_lue'] = d.id_guideline.map(FORCE).fillna('non relevée')
    d['correction_vs_v1'] = ''
    m = d.id_guideline == 'PA166265162'
    d.loc[m, ['alleles', 'action_provisoire']] = ['HLA-B*15:02', 'EVITER']
    d.loc[m, 'correction_vs_v1'] = 'v1 : ENVISAGER_ALTERNATIVE (résumé) ; texte complet : Avoid carbamazepine'
    ligne = d[m].iloc[0].copy()
    ligne['alleles'] = 'HLA-B*15:11'; ligne['action_provisoire'] = 'EVITER_SI_ALTERNATIVE'
    ligne['condition_ou_precision'] = 'Peser risque/bénéfice ; éviter si alternative possible ; sinon signaler toute éruption immédiatement (DPWG 2024)'
    ligne['correction_vs_v1'] = 'ligne ajoutée : séparée de B*15:02 (v1 les regroupait)'
    d = pd.concat([d, ligne.to_frame().T], ignore_index=True)
    for gid, txt in MAJ.items():
        mm = (d.id_guideline == gid) & (d.alleles != 'HLA-B*15:11')
        d.loc[mm, 'condition_ou_precision'] = txt
    d['statut_lecture'] = d.id_guideline.map(lambda g: 'texte complet lu (partiel)' if g in TEXTE_COMPLET else 'résumé PharmGKB + force par mots-clés; texte complet non relu')
    d = d.sort_values(['medicament', 'organisme', 'alleles'])
    d.to_csv(a.sortie, index=False)
    print(len(d), 'lignes ->', a.sortie)

if __name__ == '__main__':
    main()
