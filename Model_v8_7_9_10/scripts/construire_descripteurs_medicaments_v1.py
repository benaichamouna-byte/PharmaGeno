#!/usr/bin/env python3
"""
construire_descripteurs_medicaments_v1.py (2 nov. 2026) : descripteurs de médicaments pour le pilier A (DL qui généralise au médicament).

Descripteurs construits (aucun n'est issu d'une guideline d'action, pour éviter une fuite d'étiquette) :
  1. empreinte de Morgan (rayon 2, 512 bits) calculée depuis le SMILES des exports ClinPGx (chemicals, drugs) ; combinaison « a / b » = maximum des composants résolus ;
  2. classe ATC (colonne « ATC Identifiers » des exports ClinPGx ; à défaut data/atc_mapping_medicaments_v1.csv) ;
  3. liens gène-médicament de data/couverture_maximale_gene_substance_v14.csv, SANS la source « regle_action » (= guideline) :
     canal 1 « relationships » (0/1), canal 2 « var_drug_ann_significatif » (0/1), canal 3 niveau le plus fort d'annotation clinique (1A=1,0 ; 1B=0,9 ; 2A=0,75 ; 2B=0,6 ; 3=0,4 ; 4=0,2).
INTERDITS (fuite) : colonnes « Dosing Guideline », « Top CPIC Pairs Level », « Top FDA Label Testing Level », « Label Has Dosing Info » des exports ClinPGx : jamais lues.
Usage : python3 -I construire_descripteurs_medicaments_v1.py CORPUS.csv COUVERTURE.csv CHEMICALS.tsv DRUGS.tsv ATC_MAPPING.csv SORTIE_DIR
"""
import sys, os, re
import numpy as np, pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator
RDLogger.DisableLog('rdApp.*')

corpus, couv, chem, drugs, atcmap, sortie = sys.argv[1:7]
os.makedirs(sortie, exist_ok=True)
SEL = set('hydrochloride hydrobromide hydrate monohydrate sodium potassium phosphate sulfate sulphate mesylate maleate tartrate succinate citrate acetate besylate fumarate calcium magnesium disodium bromide chloride nitrate lauroxil acid'.split())
NIV = {'1A': 1.0, '1B': 0.9, '2A': 0.75, '2B': 0.6, '3': 0.4, '4': 0.2}

head = pd.read_csv(corpus, nrows=1)
non_genes = {'drug', 'action', 'sample_id', 'family_id', 'action_ancienne', 'action_v3', 'statut_etiquette', 'confiance', 'nb_regles_appliquees', 'origine'}
cols_profil = [c for c in head.columns if c not in non_genes]
genes = sorted({re.sub(r'\*.*$', '', c) for c in cols_profil})
print('colonnes de profil', len(cols_profil), '| gènes de base', len(genes))

cv = pd.read_csv(couv); cv['sub'] = cv.substance.str.lower()
meds = sorted(set(pd.read_csv(corpus, usecols=['drug']).drug.str.lower()))
toutes = sorted(set(meds) | set(cv['sub']))
print('médicaments du corpus', len(meds), '| substances au total', len(toutes))

# --- SMILES et ATC (colonnes autorisées uniquement)
S, ATC = {}, {}
for f in (chem, drugs):
    t = pd.read_csv(f, sep='\t', dtype=str, usecols=['Name', 'SMILES', 'ATC Identifiers'])
    for n, s, a in zip(t.Name.str.lower(), t.SMILES, t['ATC Identifiers']):
        if isinstance(s, str): S.setdefault(n, s)
        if isinstance(a, str): ATC.setdefault(n, a)
M = pd.read_csv(atcmap); M['m'] = M.medicament.str.lower()
PA = {m: (p if isinstance(p, str) else None) for m, p in zip(M.m, M.principe_actif)}
for m, a in zip(M.m, M.atc_codes):
    if isinstance(a, str) and a: ATC.setdefault(m, a.replace(';', ','))
gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=512)
def smiles_de(nom):
    cand = [nom, PA.get(nom)]
    cand.append(' '.join(w for w in nom.split() if w not in SEL))
    for c in cand:
        if c and c.lower() in S: return S[c.lower()]
    return None
def fp_de(nom):
    parts = [p.strip() for p in re.split(r' / |, | and ', nom) if p.strip()]
    fps = []
    for p in parts:
        s = smiles_de(p)
        m = Chem.MolFromSmiles(s) if s else None
        if m is not None: fps.append(np.array(gen.GetFingerprintAsNumPy(m), dtype=np.uint8))
    if not fps: return None, 0.0
    return np.maximum.reduce(fps), len(fps) / len(parts)

def atc_de(nom):
    for c in [nom, PA.get(nom), ' '.join(w for w in nom.split() if w not in SEL)]:
        if c and c.lower() in ATC: return ATC[c.lower()]
    parts = [p.strip() for p in re.split(r' / |, | and ', nom) if p.strip()]
    if len(parts) > 1:
        codes = [ATC.get(p.lower()) for p in parts]
        codes = [c for c in codes if c]
        if codes: return ','.join(codes)
    return ''

n = len(toutes); FP = np.zeros((n, 512), np.uint8); COV = np.zeros(n, np.float32); ATCL = []
for i, nom in enumerate(toutes):
    f, c = fp_de(nom)
    if f is not None: FP[i] = f
    COV[i] = c; ATCL.append(atc_de(nom))

# --- liens gène-médicament sans la source « regle_action »
idx = {m: i for i, m in enumerate(toutes)}; gi = {g: i for i, g in enumerate(genes)}
LINK = np.zeros((n, len(genes), 3), np.float32)
for g, s, src in zip(cv.gene, cv['sub'], cv.sources):
    base = re.sub(r'\*.*$', '', g)
    if base not in gi: continue
    parts = [p for p in src.split('+') if p != 'regle_action']
    if not parts: continue
    i, j = idx[s], gi[base]
    if 'relationships' in parts: LINK[i, j, 0] = 1.0
    if 'var_drug_ann_significatif' in parts: LINK[i, j, 1] = 1.0
    best = 0.0
    for p in parts:
        if p.startswith('clinical_annotation_niv_'): best = max(best, NIV.get(p.split('_')[-1], 0.0))
    LINK[i, j, 2] = max(LINK[i, j, 2], best)
np.savez_compressed(os.path.join(sortie, 'descripteurs_v1.npz'), noms=np.array(toutes), fp=FP, fp_couverture=COV, atc=np.array(ATCL), lien=LINK, genes=np.array(genes))
Dm = [idx[m] for m in meds]
print('--- couverture sur les %d médicaments du corpus ---' % len(meds))
print('empreinte (≥ un composant résolu) : %d | complète : %d' % ((COV[Dm] > 0).sum(), (COV[Dm] == 1).sum()))
print('ATC renseigné : %d' % sum(1 for i in Dm if ATCL[i]))
print('au moins un lien gène (hors guideline) : %d' % int((LINK[Dm].sum((1, 2)) > 0).sum()))
print('--- sur les %d substances hors corpus ---' % (n - len(meds)))
ho = [i for i, m in enumerate(toutes) if m not in set(meds)]
print('empreinte : %d | ATC : %d | lien : %d' % ((COV[ho] > 0).sum(), sum(1 for i in ho if ATCL[i]), int((LINK[ho].sum((1, 2)) > 0).sum())))
