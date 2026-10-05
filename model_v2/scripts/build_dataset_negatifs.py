"""
build_dataset_negatifs.py — Ajout de paires sans association documentee

Le modele actuel ne sait pas repondre "ce medicament ne concerne pas ce patient".
En cause : la classe STANDARD ne represente que 1,4 % du corpus (628 lignes sur 46 371).
Le reseau n a jamais vu de contre-exemple et tranche donc toujours dans les classes
qu il connait — d ou 326 medicaments predits EVITER sur 437 pour un patient n ayant
que deux genes mutes.

Methode. Les associations gene-medicament documentees sont extraites des 217 fichiers
d annotation de guidelines CPIC et DPWG presents dans le projet, soit 386 paires sur
41 genes et 208 medicaments. Pour chaque profil genetique du corpus, on tire des
medicaments dont aucun n est associe aux genes mutes de ce profil, et on les etiquette
STANDARD.

Ces paires ne sont pas inventees : si un patient presente une seule deficience CYP2C19,
la metformine ne requiert aucun ajustement. C est un fait clinique que le jeu de donnees
actuel ne contient simplement jamais.

Cible : porter STANDARD a environ un quart du corpus final.
Le fichier source n est pas modifie.

Sortie : data/phenotype_drug_dataset_NEG.csv, docs/negatifs_report.md
"""
import pandas as pd, numpy as np, json, glob, pickle, os, hashlib

DATA_DIR = '/home/mouna/projet_memoire/model_v2/data'
DOCS_DIR = '/home/mouna/projet_memoire/model_v2/docs'
GUIDE    = '/home/mouna/projet_memoire/data/cpic_guidelines'
os.makedirs(DOCS_DIR, exist_ok=True)
rng = np.random.default_rng(42)

# --- 1. Table des associations documentees ----------------------------------
SYMBOLE = {}
paires, sources = set(), {}
for f in sorted(glob.glob(f'{GUIDE}/PA*.json')):
    try:
        g = json.load(open(f))['guideline']
    except Exception:
        continue
    src = g.get('source', 'inconnue')
    gl = [x.get('symbol','') for x in g.get('relatedGenes', []) if isinstance(x, dict) and x.get('symbol')]
    cl = [x.get('name','').lower().strip() for x in g.get('relatedChemicals', []) if isinstance(x, dict)]
    for a in gl:
        for b in cl:
            paires.add((a, b))
            sources.setdefault(src, set()).add((a, b))

assoc = {}
for gene, drug in paires:
    assoc.setdefault(gene, set()).add(drug)

print(f'Associations documentees : {len(paires)} paires, {len(assoc)} genes')
for s, v in sorted(sources.items(), key=lambda x: -len(x[1])):
    print(f'  {s:10s} {len(v)} paires')

# --- 2. Corpus et referentiel moleculaire -----------------------------------
df = pd.read_csv(f'{DATA_DIR}/phenotype_drug_dataset_FINAL.csv')
with open(f'{DATA_DIR}/drug_fingerprints.pkl','rb') as f:
    drug_fp = pickle.load(f)

META  = ['drug','action','sample_id','family_id']
GENES = sorted([c for c in df.columns if c not in META])
df = df[df['drug'].isin(drug_fp)].copy()

print(f'\nCorpus : {len(df)} lignes')
print(f'Distribution initiale : {df["action"].value_counts().to_dict()}')

med_dispo = sorted(drug_fp.keys())

# --- 3. Generation des paires sans association ------------------------------
profils = df[GENES + ['sample_id']].drop_duplicates(subset=GENES).reset_index(drop=True)
print(f'Profils genetiques distincts : {len(profils)}')

CIBLE = 12000
par_profil = max(1, CIBLE // len(profils))
print(f'Objectif : {CIBLE} lignes, soit {par_profil} par profil')

lignes, rejets = [], 0
for _, prof in profils.iterrows():
    mutes = [g for g in GENES if prof[g] != 1.0]
    if not mutes:
        continue

    # Medicaments associes a au moins un gene mute : a exclure
    exclus = set()
    for g in mutes:
        exclus |= assoc.get(g, set())

    candidats = [m for m in med_dispo if m not in exclus]
    if len(candidats) < par_profil:
        rejets += 1
        continue

    for m in rng.choice(candidats, size=par_profil, replace=False):
        r = {g: float(prof[g]) for g in GENES}
        r['drug']      = m
        r['action']    = 'STANDARD'
        r['sample_id'] = prof['sample_id']
        r['family_id'] = prof['sample_id']
        lignes.append(r)

neg = pd.DataFrame(lignes)
print(f'\nLignes generees : {len(neg)}  (profils ecartes : {rejets})')

# --- 4. Fusion ---------------------------------------------------------------
final = pd.concat([df, neg[df.columns]], ignore_index=True)
final = final.drop_duplicates(subset=GENES + ['drug'])
print(f'Corpus final : {len(final)} lignes')

d0 = df['action'].value_counts()
d1 = final['action'].value_counts()
print('\n| Action | Avant | Apres |')
for a in ['ADAPTER_DOSE','EVITER','SURVEILLER','STANDARD']:
    print(f'| {a:13s} | {d0.get(a,0):6d} | {d1.get(a,0):6d} ({d1.get(a,0)/len(final)*100:4.1f} %) |')

out = f'{DATA_DIR}/phenotype_drug_dataset_NEG.csv'
final.to_csv(out, index=False)
sha = hashlib.sha256(open(out,'rb').read()).hexdigest()
print(f'\nFichier : phenotype_drug_dataset_NEG.csv')
print(f'SHA256  : {sha}')

# --- 5. Rapport --------------------------------------------------------------
r = ['# Paires sans association documentee', '',
     '## Motif', '',
     'Le modele entraine sur le corpus precedent ne sait pas repondre qu un medicament ne',
     'concerne pas un patient donne. Interroge sur les 437 medicaments du referentiel pour',
     'un patient ne presentant que deux genes mutes, il en classe 326 en contre-indication,',
     'avec des niveaux de confiance parfois superieurs a ceux des medicaments reellement',
     'concernes.', '',
     'La cause est l absence de contre-exemples : la classe STANDARD ne representait que',
     f'{d0.get("STANDARD",0)} lignes sur {len(df)}, soit {d0.get("STANDARD",0)/len(df)*100:.1f} %. Le reseau n a jamais appris a reconnaitre',
     'une absence de lien.', '',
     '## Source des associations', '',
     f'Les {len(paires)} paires gene-medicament documentees proviennent des {len(glob.glob(f"{GUIDE}/PA*.json"))} fichiers',
     'd annotation de guidelines presents dans le projet.', '',
     '| Source | Paires |', '|---|---|']
for s, v in sorted(sources.items(), key=lambda x: -len(x[1])):
    r.append(f'| {s} | {len(v)} |')
r += ['', f'Couverture : {len(assoc)} genes, {len(set(b for _, b in paires))} medicaments.', '',
      '## Methode', '',
      'Pour chaque profil genetique du corpus, les genes non normaux sont identifies.',
      'Les medicaments associes a l un d eux dans la table documentee sont exclus.',
      f'Parmi les medicaments restants, {par_profil} sont tires au hasard et etiquetes STANDARD.',
      '', 'Le tirage est reproductible — graine fixee a 42.', '',
      'Ces paires ne sont pas inventees. Un patient porteur d une seule deficience CYP2C19',
      'ne requiert aucun ajustement pour la metformine : c est un fait clinique etabli, que',
      'le corpus initial ne contenait simplement pas.', '',
      '## Resultat', '',
      '| Action | Avant | Apres | Part finale |', '|---|---|---|---|']
for a in ['ADAPTER_DOSE','EVITER','SURVEILLER','STANDARD']:
    r.append(f'| {a} | {d0.get(a,0)} | {d1.get(a,0)} | {d1.get(a,0)/len(final)*100:.1f} % |')
r += ['', f'Corpus : {len(df)} vers {len(final)} lignes.',
      f'Lignes ajoutees : {len(final)-len(df)}.', '',
      f'SHA256 : `{sha}`', '',
      '## Limite', '',
      'L absence d association repose sur les guidelines CPIC et DPWG disponibles. Une paire',
      'non documentee n est pas necessairement sans interaction : elle peut relever d une',
      'association non encore etablie. Le modele apprend donc l etat des connaissances',
      'publiees, non une verite biologique.']

with open(f'{DOCS_DIR}/negatifs_report.md','w') as f:
    f.write('\n'.join(r))
print('Rapport : docs/negatifs_report.md')
