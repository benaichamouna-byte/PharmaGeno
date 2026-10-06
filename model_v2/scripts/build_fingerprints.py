"""
build_fingerprints.py — Recalcul des empreintes moleculaires de Morgan

Constat a l origine de ce script : les fichiers drug_fingerprints.pkl et drug_fp_ref.pkl
contiennent, pour les 437 medicaments, un vecteur de 518 variables dont les 512 premieres
sont nulles sans exception. Les empreintes de Morgan n ont donc jamais contribue a aucune
prediction. Seuls les six descripteurs physico-chimiques finaux portaient de l information.

Le script qui avait produit ces fichiers n a pas ete conserve et les structures SMILES
n avaient pas ete sauvegardees, ce qui a empeche de diagnostiquer l erreur plus tot.

Ce script recupere les structures depuis PubChem, recalcule les empreintes avec RDKit,
et conserve les six descripteurs existants. Les SMILES sont enregistres separement afin
que le calcul soit reproductible et verifiable.

Sorties :
  data/drug_smiles.csv            structures recuperees, avec identifiant PubChem
  data/drug_fingerprints_v2.pkl   518 variables : 512 bits de Morgan + 6 descripteurs
  docs/fingerprints_report.md     rapport de couverture

Les fichiers existants ne sont pas modifies.
"""
import pickle, time, json, os, csv
import numpy as np
import urllib.request, urllib.parse, urllib.error
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator, Descriptors
RDLogger.DisableLog('rdApp.*')

DATA_DIR = '/home/mouna/projet_memoire/model_v2/data'
DOCS_DIR = '/home/mouna/projet_memoire/model_v2/docs'
os.makedirs(DOCS_DIR, exist_ok=True)

PUBCHEM = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'
N_BITS, RAYON = 512, 2

with open(f'{DATA_DIR}/drug_fingerprints.pkl', 'rb') as f:
    anciens = pickle.load(f)
with open('/home/mouna/projet_memoire/model_v2/results/drug_props_pgx.pkl', 'rb') as f:
    props = pickle.load(f)

medicaments = sorted(anciens.keys())
print(f'Medicaments a traiter : {len(medicaments)}')
print(f'Descripteurs physico-chimiques disponibles : {len(props)}\n')

def interroger_pubchem(nom, tentatives=4):
    """Recupere le SMILES et le CID depuis PubChem.

    L API PUG REST a change de nomenclature : la propriete autrefois nommee
    CanonicalSMILES est desormais renvoyee sous la cle ConnectivitySMILES.
    Le script accepte donc plusieurs noms de cle, et repart de la premiere
    valeur trouvee dans la reponse.

    Le serveur renvoie regulierement un code 503 PUGREST.ServerBusy lorsque
    les requetes s enchainent trop vite. Chaque echec est donc suivi d une
    attente croissante avant nouvelle tentative.
    """
    q = urllib.parse.quote(nom)
    url = f'{PUBCHEM}/compound/name/{q}/property/ConnectivitySMILES,IsomericSMILES,CanonicalSMILES/JSON'

    for essai in range(tentatives):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                d = json.loads(r.read().decode())
            props_rep = d['PropertyTable']['Properties'][0]
            for cle in ('IsomericSMILES', 'ConnectivitySMILES', 'CanonicalSMILES', 'SMILES'):
                s = props_rep.get(cle)
                if s:
                    return s, props_rep.get('CID')
            return None, None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, None
            time.sleep(2.0 * (essai + 1))
        except Exception:
            time.sleep(2.0 * (essai + 1))
    return None, None

gen = rdFingerprintGenerator.GetMorganGenerator(radius=RAYON, fpSize=N_BITS)

smiles_table, empreintes = {}, {}
echecs_pubchem, echecs_rdkit = [], []

for i, nom in enumerate(medicaments, 1):
    if i % 25 == 0 or i == 1:
        print(f'  {i}/{len(medicaments)} — {len(empreintes)} empreintes obtenues', flush=True)

    smi, cid = interroger_pubchem(nom)
    time.sleep(0.45)

    if not smi:
        echecs_pubchem.append(nom)
        continue

    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        echecs_rdkit.append(nom)
        continue

    bits = np.array(gen.GetFingerprintAsNumPy(mol), dtype=float)

    d = props.get(nom)
    if d:
        desc = [d['MW'], d['LogP'], d['HBD'], d['HBA'], d['RB'], d['TPSA']]
    else:
        desc = [Descriptors.MolWt(mol), Descriptors.MolLogP(mol),
                Descriptors.NumHDonors(mol), Descriptors.NumHAcceptors(mol),
                Descriptors.NumRotatableBonds(mol), Descriptors.TPSA()]

    empreintes[nom] = np.concatenate([bits, np.array(desc, dtype=float)])
    smiles_table[nom] = {'smiles': smi, 'cid': cid, 'bits_actifs': int(bits.sum())}

# --- Sauvegardes ------------------------------------------------------------
with open(f'{DATA_DIR}/drug_smiles.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['medicament', 'pubchem_cid', 'smiles', 'bits_actifs'])
    for n, v in sorted(smiles_table.items()):
        w.writerow([n, v['cid'], v['smiles'], v['bits_actifs']])

with open(f'{DATA_DIR}/drug_fingerprints_v2.pkl', 'wb') as f:
    pickle.dump(empreintes, f)

# --- Verification -----------------------------------------------------------
M = np.array([v[:N_BITS] for v in empreintes.values()])
nulles = int((M.sum(axis=1) == 0).sum())
moy    = float(M.sum(axis=1).mean())
utiles = int((M.sum(axis=0) > 0).sum())

print(f'\n{"="*58}')
print('RESULTAT')
print('='*58)
print(f'Empreintes calculees      : {len(empreintes)} / {len(medicaments)}')
print(f'Introuvables sur PubChem  : {len(echecs_pubchem)}')
print(f'Non lisibles par RDKit    : {len(echecs_rdkit)}')
print(f'Empreintes nulles         : {nulles}   (avant correction : 437)')
print(f'Bits actifs en moyenne    : {moy:.1f} / {N_BITS}')
print(f'Bits jamais actifs        : {N_BITS - utiles} / {N_BITS}')

if echecs_pubchem:
    print(f'\nIntrouvables : {", ".join(echecs_pubchem[:12])}')
    if len(echecs_pubchem) > 12:
        print(f'  et {len(echecs_pubchem)-12} autres')

# --- Rapport ----------------------------------------------------------------
r = ['# Empreintes moleculaires — recalcul', '',
     '## Constat initial', '',
     'Les fichiers `drug_fingerprints.pkl` et `drug_fp_ref.pkl` contenaient, pour chacun des',
     '437 medicaments, un vecteur de 518 variables dont les 512 premieres etaient nulles sans',
     'exception. Les empreintes de Morgan n ont donc contribue a aucune prediction des modeles',
     'entraines jusque-la : seuls les six descripteurs physico-chimiques finaux portaient de',
     'l information moleculaire.', '',
     'Le script ayant produit ces fichiers n avait pas ete conserve, et les structures SMILES',
     'n avaient pas ete sauvegardees — ce qui a empeche un diagnostic plus precoce.', '',
     '## Methode de recalcul', '',
     '| Parametre | Valeur |', '|---|---|',
     '| Source des structures | PubChem PUG REST, interrogation par nom |',
     '| Bibliotheque | RDKit ' + Chem.rdBase.rdkitVersion + ' |',
     f'| Type d empreinte | Morgan (circulaire), rayon {RAYON} |',
     f'| Longueur | {N_BITS} bits |',
     '| Descripteurs conserves | MW, LogP, HBD, HBA, RB, TPSA |',
     f'| Dimension totale | {N_BITS + 6} |', '',
     'Les structures recuperees sont enregistrees dans `drug_smiles.csv` avec leur identifiant',
     'PubChem, ce qui rend le calcul reproductible et verifiable.', '',
     '## Couverture obtenue', '',
     '| | Nombre |', '|---|---|',
     f'| Medicaments traites | {len(medicaments)} |',
     f'| Empreintes calculees | {len(empreintes)} |',
     f'| Introuvables sur PubChem | {len(echecs_pubchem)} |',
     f'| Non lisibles par RDKit | {len(echecs_rdkit)} |', '',
     '## Verification', '',
     '| Indicateur | Avant | Apres |', '|---|---|---|',
     f'| Empreintes entierement nulles | 437 | {nulles} |',
     f'| Bits actifs en moyenne | 0,0 | {moy:.1f} |',
     f'| Bits jamais actifs | 512 | {N_BITS - utiles} |', '',
     '## Portee', '',
     'Les resultats obtenus avec les empreintes nulles restent valides comme mesure de ce que',
     'les modeles realisent a partir des seuls descripteurs globaux. L ecart entre ces resultats',
     'et ceux obtenus apres recalcul mesure directement l apport de la representation structurale',
     'du medicament — question de recherche RQ4.']

if echecs_pubchem:
    r += ['', '## Medicaments introuvables', '',
          'Ces entrees n ont pas de correspondance dans PubChem par recherche nominale. Elles',
          'relevent pour la plupart des categories deja documentees dans le dictionnaire des',
          'medicaments : classes therapeutiques, biologiques, combinaisons.', '']
    r += ['- ' + n for n in echecs_pubchem]

with open(f'{DOCS_DIR}/fingerprints_report.md', 'w') as f:
    f.write('\n'.join(r))

print('\nFichiers : data/drug_smiles.csv, data/drug_fingerprints_v2.pkl')
print('Rapport  : docs/fingerprints_report.md')
