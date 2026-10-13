#!/usr/bin/env python3
"""Tests de référence du corpus v3.
Les étiquettes attendues ont été écrites À LA MAIN d'après le texte des guidelines (CPIC/DPWG),
indépendamment du code qui construit le corpus. Usage : python3 tests_reference_corpus_v3.py phenotype_drug_dataset_v3.csv sortie.csv"""
import sys, pandas as pd
v3 = pd.read_csv(sys.argv[1])
ATT = {('codeine','CYP2D6',0.0):'EVITER',('codeine','CYP2D6',0.5):'STANDARD',('codeine','CYP2D6',1.0):'STANDARD',('codeine','CYP2D6',2.0):'EVITER',
('tramadol','CYP2D6',0.0):'EVITER',('tramadol','CYP2D6',1.0):'STANDARD',('tramadol','CYP2D6',2.0):'EVITER',
('clopidogrel','CYP2C19',0.0):'EVITER',('clopidogrel','CYP2C19',0.5):'EVITER',('clopidogrel','CYP2C19',1.0):'STANDARD',('clopidogrel','CYP2C19',1.5):'STANDARD',('clopidogrel','CYP2C19',2.0):'STANDARD',
('simvastatin','SLCO1B1',0.0):'EVITER',('simvastatin','SLCO1B1',0.5):'EVITER',('simvastatin','SLCO1B1',1.0):'STANDARD',
('fluorouracil','DPYD',0.5):'ADAPTER_DOSE',('tacrolimus','CYP3A5',0.0):'STANDARD',('tacrolimus','CYP3A5',0.5):'ADAPTER_DOSE',
('omeprazole','CYP2C19',2.0):'ADAPTER_DOSE'}
res = []
for (d, g, val), a in ATT.items():
    s = v3[(v3.drug.str.lower() == d) & (v3[g] == val)]
    if len(s) == 0:
        res.append((d, g, val, a, 0, None, 'aucune ligne dans v3')); continue
    # les autres gènes peuvent modifier l'action (pire cas) : on compare donc seulement les lignes où
    # l'action v3 ne dépasse pas l'attendu en sévérité d'un autre gène -> ici on compte simplement l'accord brut
    res.append((d, g, val, a, len(s), round((s.action == a).mean(), 3), ''))
r = pd.DataFrame(res, columns=['medicament', 'gene', 'valeur', 'attendu_guideline', 'n_lignes', 'accord', 'remarque'])
r.to_csv(sys.argv[2], index=False); print(r.to_string())
print('Accord = 1.0 partout :', bool((r.accord.dropna() == 1.0).all()))
