#!/usr/bin/env python3
"""interroger_dl_couples_etudes_v1.py : demande au DL (profils CONSTRUITS : tous les gènes à 1,0, HLA à 0, un seul gène changé) son action pour les couples gène-médicament étudiés dans la littérature. Ce sont des tests construits, pas de vrais patients.
Usage (depuis scripts/) : python3 interroger_dl_couples_etudes_v1.py ../results/comparaison_etudes_v1/dl_couples_etudes.csv [../modeles_v8f]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); os.chdir(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from moteur_v8i import MoteurPGxChoix
D = '../data/'
mo = MoteurPGxChoix((sys.argv[2] if len(sys.argv) > 2 else '../modeles_v8f'), '../modeles_v8i', D+'domaine_v8.json', D+'regles_v7_monogene.csv', D+'regles_v2_corrigees_multigene_v7.csv')
base = {g: 1.0 for g in mo.genes_modele}
for g in base:
    if g.startswith('HLA'): base[g] = 0.0
print('gènes du modèle:', mo.genes_modele)
tests = [('SLCO1B1',0.5,'simvastatin'),('SLCO1B1',0.0,'simvastatin'),('SLCO1B1',1.0,'simvastatin'),
 ('HLA-B*57:01',1.0,'abacavir'),('HLA-B*57:01',0.0,'abacavir'),
 ('HLA-B*15:02',1.0,'carbamazepine'),('HLA-B*15:02',0.0,'carbamazepine'),
 ('HLA-B*58:01',1.0,'allopurinol'),('HLA-B*58:01',0.0,'allopurinol'),
 ('DPYD',0.5,'fluorouracil'),('DPYD',0.0,'fluorouracil'),('DPYD',1.0,'fluorouracil'),
 ('CYP2C19',0.0,'clopidogrel'),('CYP2C19',0.5,'clopidogrel'),('CYP2C19',1.0,'clopidogrel'),('CYP2C19',2.0,'clopidogrel'),
 ('CYP2D6',2.0,'codeine'),('CYP2D6',1.0,'codeine'),('CYP2D6',0.0,'codeine'),
 ('CYP2D6',0.0,'tamoxifen'),('CYP2D6',0.5,'tamoxifen'),('CYP2D6',1.0,'tamoxifen'),('CYP2D6',2.0,'tamoxifen')]
out = []
R = pd.read_csv(D+'regles_v7_monogene.csv')
for g, v, m in tests:
    p = dict(base); p[g] = v
    a = mo.sortie_complete(p)['actions'].get(m)
    reg = R[(R.medicament == m) & (R.gene == g) & (R.valeur == v)]
    out.append(dict(gene=g, valeur=v, medicament=m, action_dl=a, regle_corpus=(reg.action.iloc[0] if len(reg) else None), regle_ambigue=(bool(reg.ambigu.iloc[0]) if len(reg) else None)))
df = pd.DataFrame(out); print(df.to_string(index=False)); df.to_csv(sys.argv[1], index=False)
