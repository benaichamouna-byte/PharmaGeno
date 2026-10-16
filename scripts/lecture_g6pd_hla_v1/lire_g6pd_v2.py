#!/usr/bin/env python3
"""
lire_g6pd_v2.py : enrichit g6pd_consignes_v1.csv (le v1 reste intact) avec le TABLEAU 2 de l'article source :
Gammal et al., Clin Pharmacol Ther 2023 (manuscrit auteur PMC10281211, fourni par l'utilisatrice, pages 17-18), et les tableaux 3 à 5.
Ajoute : risque et force de recommandation par médicament, correspondance de nom PharmGKB / article, force CNSHA (tableaux 3-5).
Usage : python3 lire_g6pd_v2.py --entree g6pd_consignes_v1.csv --sortie g6pd_consignes_v2.csv
"""
import argparse
import pandas as pd

T2 = {  # nom article : (risque, force)   [Table 2, pages 17-18 du manuscrit]
 'dapsone': ('High', 'Strong'), 'methylene blue': ('High', 'Moderate'), 'pegloticase': ('High', 'Strong'), 'rasburicase': ('High', 'Strong'),
 'tafenoquine': ('High', 'Strong'), 'toluidine blue': ('High', 'Moderate'), 'nitrofurantoin': ('Medium', 'Optional'),
 'primaquine': ('Dépend de la dose : High (>= 0,25-0,5 mg/kg/j x14 j, Strong) ; Medium (0,75 mg/kg ou 45 mg 1x/sem x8 sem, P. vivax, Strong) ; Low-to-no (0,25 mg/kg dose unique, P. falciparum, Strong)', 'Strong (3 niveaux de dose)'),
 '4-aminosalicylic acid': ('Low-to-no', 'Optional'), 'aspirin': ('Low-to-no (<=1 g/j) ; >1 g/j : no recommendation', 'Moderate'), 'chloramphenicol': ('Low-to-no', 'Moderate'),
 'chloroquine': ('Low-to-no', 'Moderate'), 'ciprofloxacin': ('Low-to-no', 'Optional'), 'dimercaprol': ('Low-to-no', 'Optional'), 'doxorubicin': ('Low-to-no', 'Optional'),
 'furazolidone': ('Low-to-no', 'Optional'), 'glyburide': ('Low-to-no', 'Optional'), 'hydroxychloroquine': ('Low-to-no', 'Moderate'), 'mafenide': ('Low-to-no', 'Optional'),
 'nalidixic acid': ('Low-to-no', 'Optional'), 'norfloxacin': ('Low-to-no', 'Optional'), 'ofloxacin': ('Low-to-no', 'Optional'), 'phenazopyridine': ('Low-to-no', 'Optional'),
 'quinine': ('Low-to-no', 'Optional'), 'sulfadiazine': ('Low-to-no', 'Optional'), 'sulfadimidine': ('Low-to-no', 'Optional'), 'sulfamethoxazole': ('Low-to-no', 'Optional'),
 'sulfanilamide': ('Low-to-no', 'Optional'), 'sulfasalazine': ('Low-to-no', 'Optional'), 'sulfisoxazole': ('Low-to-no', 'Optional'), 'tolbutamide': ('Low-to-no', 'Optional'),
 'vitamin c': ('Low-to-no', 'Moderate'), 'vitamin k': ('Low-to-no', 'Moderate'),
 'chlorpropamide': ('n/a', 'No recommendation'), 'dabrafenib': ('n/a', 'No recommendation'), 'gliclazide': ('n/a', 'No recommendation'), 'glimepiride': ('n/a', 'No recommendation'),
 'glipizide': ('n/a', 'No recommendation'), 'mepacrine': ('n/a', 'No recommendation'), 'mesalazine': ('n/a', 'No recommendation'), 'moxifloxacin': ('n/a', 'No recommendation'),
 'nicorandil': ('n/a', 'No recommendation'), 'nitrofural': ('n/a', 'No recommendation'), 'probenecid': ('n/a', 'No recommendation'), 'sodium nitrite': ('n/a', 'No recommendation'),
 'sulfacetamide': ('n/a', 'No recommendation'), 'tolazamide': ('n/a', 'No recommendation'), 'trametinib': ('n/a', 'No recommendation'),
}
NOM = {'aminosalicylic acid': '4-aminosalicylic acid', 'sulfamethazine': 'sulfadimidine', 'vitamin k and analogues': 'vitamin k', 'quinacrine': 'mepacrine',
       'nitrofurazone': 'nitrofural', 'sodium nitrate': 'sodium nitrite'}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--entree', required=True); ap.add_argument('--sortie', required=True); a = ap.parse_args()
    d = pd.read_csv(a.entree).fillna('')
    R, F, C, N = [], [], [], []
    for m in d.medicament:
        nom = NOM.get(m, m)
        if nom in T2:
            r, f = T2[nom]; R.append(r); F.append(f)
            C.append('oui' if nom == m else 'nom différent (article : %s)' % nom)
            N.append('DISCORDANCE à signaler : l\'article liste "sodium nitrite", PharmGKB liste "sodium nitrate"' if m == 'sodium nitrate' else '')
        else:
            R.append('non listé'); F.append('non listé'); C.append('absent du tableau 2'); N.append('PharmGKB le rattache à la guideline ; le tableau 2 de l\'article ne le liste pas sous ce nom')
    d['risque_article_tableau2'] = R; d['force_article_tableau2'] = F; d['concordance_nom_pharmgkb_article'] = C; d['remarque_v2'] = N
    cn = d.categorie_risque_cpic.isin(['FAIBLE_A_AUCUN_RISQUE', 'FAIBLE_A_AUCUN_RISQUE_ASPIRINE'])
    d.loc[cn, 'force_CNSHA'] = 'Optional (tableau 5)'
    d.loc[d.categorie_risque_cpic == 'RISQUE_MOYEN', 'force_CNSHA'] = 'Moderate (tableau 4)'
    d['statut_lecture'] = 'lu dans le texte PharmGKB + tableaux 2 à 5 de l\'article source (manuscrit auteur)'
    d.to_csv(a.sortie, index=False)
    print(len(d), 'lignes ->', a.sortie); print(d.concordance_nom_pharmgkb_article.value_counts().to_string())
    print(d[d.concordance_nom_pharmgkb_article != 'oui'][['medicament', 'concordance_nom_pharmgkb_article']].to_string())

if __name__ == '__main__':
    main()
