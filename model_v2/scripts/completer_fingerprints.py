"""
completer_fingerprints.py — Rattrapage des empreintes manquantes

Sur les 437 medicaments, 402 empreintes ont ete obtenues au premier passage.
Les 35 manquants sont pour la plupart des molecules courantes — mirtazapine,
methadone, midazolam, paroxetine — dont la presence dans PubChem est certaine.
Leur echec provient de reponses 503 PUGREST.ServerBusy, et non d une absence.

Ce script les reprend avec une cadence nettement plus lente et davantage de
tentatives. Pour les formes salines, il essaie egalement le nom du principe
actif seul : une empreinte moleculaire decrit la structure, et la forme saline
ne modifie pas la partie active.

Complete drug_fingerprints_v2.pkl et drug_smiles.csv sans les reecrire.
"""
import pickle, time, json, csv, os
import numpy as np
import urllib.request, urllib.parse, urllib.error
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator, Descriptors
RDLogger.DisableLog('rdApp.*')

DATA_DIR = '/home/mouna/projet_memoire/model_v2/data'
PUBCHEM  = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'
N_BITS, RAYON = 512, 2

with open(f'{DATA_DIR}/drug_fingerprints.pkl','rb') as f:
    tous = set(pickle.load(f).keys())
with open(f'{DATA_DIR}/drug_fingerprints_v2.pkl','rb') as f:
    empreintes = pickle.load(f)
with open('/home/mouna/projet_memoire/model_v2/results/drug_props_pgx.pkl','rb') as f:
    props = pickle.load(f)

manquants = sorted(tous - set(empreintes.keys()))
print(f'A reprendre : {len(manquants)}\n')

SELS = [' hydrochloride',' sodium',' sulfate',' maleate',' tartrate',' citrate',
        ' mesylate',' besylate',' succinate',' acetate',' phosphate',' potassium',
        ' calcium',' bromide',' fumarate',' hemihydrate',' dimesylate']

def variantes(nom):
    """Nom tel quel, puis principe actif seul si forme saline."""
    v = [nom]
    b = nom.lower()
    for s in SELS:
        if s in b:
            b = b.replace(s, '')
    b = b.strip()
    if b and b != nom.lower():
        v.append(b)
    return v

def interroger(nom, tentatives=7):
    q = urllib.parse.quote(nom)
    url = f'{PUBCHEM}/compound/name/{q}/property/ConnectivitySMILES,IsomericSMILES,CanonicalSMILES/JSON'
    for essai in range(tentatives):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                d = json.loads(r.read().decode())
            p = d['PropertyTable']['Properties'][0]
            for cle in ('IsomericSMILES','ConnectivitySMILES','CanonicalSMILES','SMILES'):
                if p.get(cle):
                    return p[cle], p.get('CID')
            return None, None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, None
            time.sleep(3.0 * (essai + 1))
        except Exception:
            time.sleep(3.0 * (essai + 1))
    return None, None

gen = rdFingerprintGenerator.GetMorganGenerator(radius=RAYON, fpSize=N_BITS)
nouveaux, toujours_absents = {}, []

for i, nom in enumerate(manquants, 1):
    smi = cid = None
    utilise = nom
    for v in variantes(nom):
        smi, cid = interroger(v)
        if smi:
            utilise = v
            break
        time.sleep(1.2)

    if not smi:
        toujours_absents.append(nom)
        print(f'  {i:2d}/{len(manquants)}  {nom[:40]:40s} introuvable', flush=True)
        time.sleep(1.2)
        continue

    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        toujours_absents.append(nom)
        continue

    bits = np.array(gen.GetFingerprintAsNumPy(mol), dtype=float)
    d = props.get(nom) or props.get(utilise)
    if d:
        desc = [d['MW'], d['LogP'], d['HBD'], d['HBA'], d['RB'], d['TPSA']]
    else:
        desc = [Descriptors.MolWt(mol), Descriptors.MolLogP(mol),
                Descriptors.NumHDonors(mol), Descriptors.NumHAcceptors(mol),
                Descriptors.NumRotatableBonds(mol), Descriptors.TPSA()]

    empreintes[nom] = np.concatenate([bits, np.array(desc, dtype=float)])
    nouveaux[nom] = {'smiles': smi, 'cid': cid, 'bits': int(bits.sum()), 'via': utilise}
    via = '' if utilise == nom else f'  (via {utilise})'
    print(f'  {i:2d}/{len(manquants)}  {nom[:40]:40s} {int(bits.sum()):3d} bits{via}', flush=True)
    time.sleep(1.2)

with open(f'{DATA_DIR}/drug_fingerprints_v2.pkl','wb') as f:
    pickle.dump(empreintes, f)

if nouveaux:
    with open(f'{DATA_DIR}/drug_smiles.csv','a',newline='') as f:
        w = csv.writer(f)
        for n, v in sorted(nouveaux.items()):
            w.writerow([n, v['cid'], v['smiles'], v['bits']])

M = np.array([v[:N_BITS] for v in empreintes.values()])
print(f'\n{"="*56}')
print(f'Empreintes totales     : {len(empreintes)} / {len(tous)}')
print(f'Recuperees ce passage  : {len(nouveaux)}')
print(f'Toujours introuvables  : {len(toujours_absents)}')
print(f'Empreintes nulles      : {int((M.sum(axis=1)==0).sum())}')
print(f'Bits actifs en moyenne : {M.sum(axis=1).mean():.1f} / {N_BITS}')
if toujours_absents:
    print(f'\nIntrouvables : {", ".join(toujours_absents)}')
