#!/usr/bin/env python3
"""interroger_dl_couples_etudes_v2.py : demande au DL (profils CONSTRUITS : tous les gènes à 1,0, HLA à 0, un seul gène changé) son action pour les couples gène-médicament étudiés dans la littérature. Ce sont des tests construits, pas de vrais patients.
Usage (depuis scripts/) : python3 interroger_dl_couples_etudes_v2.py ../results/comparaison_etudes_v1/dl_couples_etudes.csv [../modeles_v8f]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); os.chdir(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from moteur_v9i import MoteurPGxChoix
D = '../data/'
mo = MoteurPGxChoix((sys.argv[2] if len(sys.argv) > 2 else '../modeles_v9'), (sys.argv[2] if len(sys.argv) > 2 else '../modeles_v9'), D+'domaine_v9.json', D+'regles_v8_monogene.csv', D+'regles_v2_corrigees_multigene_v7.csv')
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
 ('CYP2D6',0.0,'tamoxifen'),('CYP2D6',0.5,'tamoxifen'),('CYP2D6',1.0,'tamoxifen'),('CYP2D6',2.0,'tamoxifen'),
 # --- v2 : 16 médicaments ajoutés le 23 oct. 2026 (groupe A)
 ('VKORC1',0.0,'acenocoumarol'),('VKORC1',0.5,'acenocoumarol'),('VKORC1',1.0,'acenocoumarol'),('VKORC1',0.0,'phenprocoumon'),('VKORC1',0.5,'phenprocoumon'),('VKORC1',1.0,'phenprocoumon'),
 ('DPYD',0.0,'flucytosine'),('DPYD',0.5,'flucytosine'),('DPYD',1.0,'flucytosine'),
 ('CYP2C19',0.0,'prasugrel'),('CYP2C19',0.5,'ticagrelor'),('CYP2C19',2.0,'prasugrel'),('CYP2C19',0.0,'moclobemide'),('CYP2C19',2.0,'rabeprazole'),
 ('CYP2D6',0.0,'amiodarone'),('CYP2D6',2.0,'quinidine'),('CYP2D6',0.0,'mirtazapine'),('CYP2C9',0.0,'gliclazide'),('CYP2C9',0.5,'glimepiride'),('CYP3A4',0.5,'paclitaxel')]
out = []
R = pd.read_csv(D+'regles_v8_monogene.csv')
for g, v, m in tests:
    p = dict(base); p[g] = v
    a = mo.sortie_complete(p)['actions'].get(m)
    reg = R[(R.medicament == m) & (R.gene == g) & (R.valeur == v)]
    out.append(dict(gene=g, valeur=v, medicament=m, action_dl=a, regle_corpus=(reg.action.iloc[0] if len(reg) else None), regle_ambigue=(bool(reg.ambigu.iloc[0]) if len(reg) else None)))
df = pd.DataFrame(out); print(df.to_string(index=False)); df.to_csv(sys.argv[1], index=False)
