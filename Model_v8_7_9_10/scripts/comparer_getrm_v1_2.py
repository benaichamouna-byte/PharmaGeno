#!/usr/bin/env python3
"""
comparer_getrm_v1_2.py (7 nov. 2026 ; v1.2 = v1.0 + norm_ecriture, ajoutée après lecture des résultats v1.0, voir fonction) : VÉRIFICATION DU GÉNOTYPE contre la référence GeT-RM (consensus de laboratoires). LECTURE SEULE.
Règle écrite AVANT tout calcul : regle_partie1_v1.md (+ précision v1.1, ci-dessous, décidée avant tout calcul de concordance).
Entrées : tableau consolidé GeT-RM (xlsx), liste gelée des 104 personnes, sorties PyPGx (results.zip par gène, même commande que l'application), sorties PharmCAT (*.report.tsv).
Catégories par (personne, gène, outil) : 1 identique | 2 identique au sous-allèle près | 3 GeT-RM incertain ou texte non diplotype (hors dénominateur) | 4 outil non appelé ou ambigu | 5 discordant (relu à la main).
Précision v1.1 : une parenthèse contenant « + », ex. « (*28 + *60) », désigne des variants portés par un même haplotype (appel certain) ; elle est comparée jeton par jeton ;
toute autre parenthèse, « or », ou texte « c. … », « het », « no variants » = GeT-RM incertain ou non diplotype (catégorie 3).
Usage : python3 comparer_getrm_v1.py TABLEAU.xlsx LISTE104.txt DOSSIER_PYPGX DOSSIER_PHARMCAT DOSSIER_SORTIE
"""
import glob, io, os, re, sys, zipfile
import pandas as pd, openpyxl

XLSX, LISTE, PGX, PC, OUT = sys.argv[1:6]
os.makedirs(OUT, exist_ok=True)
GENES = ['CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP3A5', 'DPYD', 'NUDT15', 'SLCO1B1', 'TPMT', 'UGT1A1', 'CYP3A4', 'NAT2', 'CYP4F2']   # VKORC1 : écriture non comparable (GG/GA/AA contre variants rs), rapporté à part
ech = [l.strip() for l in open(LISTE) if l.strip()]

# ---- GeT-RM
ws = openpyxl.load_workbook(XLSX, data_only=True)['PGx HLA Genotypes']
rows = list(ws.iter_rows(min_row=2, values_only=True)); ent = [(str(x).split('\n')[0].strip() if x is not None else '') for x in rows[0]]
G = pd.DataFrame(rows[1:], columns=range(len(ent)))
idcol = 1; G[idcol] = G[idcol].astype(str).str.strip(); G = G[G[idcol].isin(ech)].set_index(idcol)
def col_gene(g):
    c = [i for i, n in enumerate(ent) if n.split(' ')[0] == g and 'Reference' not in n]
    return c[0]
REF = {g: G[col_gene(g)].map(lambda x: None if x is None or str(x).strip() in ('', 'None', 'nan') else str(x).strip()) for g in GENES}

# ---- normalisation
TOK = re.compile(r'\*[0-9]+[A-Za-z]*(?:\.[0-9]+)?')
def decouper(s):
    """découpe 'a/b' sur les '/' hors parenthèses ou crochets"""
    p, niv, cur = [], 0, ''
    for ch in s:
        if ch in '([': niv += 1
        if ch in ')]': niv -= 1
        if ch == '/' and niv == 0: p.append(cur); cur = ''
        else: cur += ch
    p.append(cur); return [x.strip() for x in p]
def haplotypes(s):
    """liste de 2 haplotypes (frozenset de jetons) ou None si non diplotype"""
    parts = decouper(s)
    if len(parts) != 2: return None
    out = []
    for p in parts:
        t = TOK.findall(p)
        if not t: return None
        out.append(frozenset(t))
    return out
def principal(hap): return frozenset('*' + re.match(r'\*([0-9]+)', t).group(1) for t in hap)
def ref_incertain(s):
    if re.search(r'\bor\b|c\.|het|no variants|del|dup', s, re.I): return True
    for m in re.finditer(r'\(([^)]*)\)', s):
        if '+' not in m.group(1): return True
    return haplotypes(s) is None
def comparer(ref, outil):
    h1, h2 = haplotypes(ref), haplotypes(outil)
    if h2 is None: return 5
    if sorted(map(sorted, h1)) == sorted(map(sorted, h2)): return 1
    if sorted(map(sorted, map(principal, h1))) == sorted(map(sorted, map(principal, h2))): return 2
    return 5

# ---- outils
def lire_pgx(g):
    f = os.path.join(PGX, 'pgx_' + g, 'results.zip')
    if not os.path.exists(f): return None
    z = zipfile.ZipFile(f); n = [x for x in z.namelist() if x.endswith('data.tsv')][0]
    r = pd.read_csv(io.BytesIO(z.read(n)), sep='\t', index_col=0)
    return r['Genotype'].map(lambda x: None if pd.isna(x) else str(x).strip())
PGXD = {g: lire_pgx(g) for g in GENES}
PCD = {}
for f in sorted(glob.glob(os.path.join(PC, '*.report.tsv'))):
    s = os.path.basename(f).split('.')[-3]
    lignes = open(f).read().splitlines()
    ver = lignes[0]
    import csv
    for r in csv.DictReader(lignes[1:], delimiter='\t'): PCD[(s, r['Gene'])] = (r['Source Diplotype'] or '').strip()
VERSION_PC = ver if PCD else 'non disponible'

def norm_ecriture(v):
    """v1.2 (décidée APRÈS lecture des résultats v1.0 ; ne change ni les catégories ni la règle, seulement l'écriture des sorties d'outils) :
    'Reference' = *1 ; 'c.85T>C (*9A)' -> '*9A' (haplotype à un seul variant)."""
    if v is None: return v
    v = re.sub(r'\bReference\b', '*1', v)
    v = re.sub(r'(?<![\[+] )c\.[^ ()\[\]+/]+ \((\*[0-9A-Za-z.]+)\)', r'\1', v)
    return v
def sortie_outil(nom, valeur):
    valeur = norm_ecriture(valeur)
    if valeur is None or valeur == '' or re.search(r'indeterminate|no call|unassigned|\bor\b|unknown', valeur, re.I): return None
    return valeur

rows = []
for g in GENES:
    for s in ech:
        ref = REF[g].get(s) if s in REF[g].index else None
        if ref is None or pd.isna(ref): continue   # gène non testé dans GeT-RM pour cette personne
        for outil in ('PyPGx', 'PharmCAT'):
            if outil == 'PyPGx':
                if PGXD[g] is None: continue
                v = PGXD[g].get(s) if s in PGXD[g].index else None
            else:
                if (s, g) not in PCD and not any(k[0] == s for k in PCD): continue
                v = PCD.get((s, g))
            if ref_incertain(ref): cat = 3
            else:
                vv = sortie_outil(outil, v)
                cat = 4 if vv is None else comparer(ref, vv)
            rows.append(dict(sample=s, gene=g, outil=outil, getrm=ref, genotype_outil=v, categorie=cat))
R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, 'getrm_detail.csv'), index=False)
lab = {1: 'identique', 2: 'sous-allele', 3: 'GeT-RM incertain', 4: 'outil non appele/ambigu', 5: 'discordant'}
T = R.pivot_table(index=['gene', 'outil'], columns='categorie', values='sample', aggfunc='count', fill_value=0).rename(columns=lab).reset_index()
for c in lab.values():
    if c not in T.columns: T[c] = 0
T['n_comparables'] = T['identique'] + T['sous-allele'] + T['discordant']
T = T[['gene', 'outil', 'n_comparables', 'identique', 'sous-allele', 'discordant', 'outil non appele/ambigu', 'GeT-RM incertain']]; T.to_csv(os.path.join(OUT, 'getrm_resume.csv'), index=False)
print('PharmCAT :', VERSION_PC, '| PyPGx 0.27.0 | personnes :', len(ech), '| lignes (personne, gène, outil) :', len(R))
print(T.to_string(index=False))
for c in (2, 4, 5):
    d = R[R.categorie == c]
    print('\n=== catégorie %d (%s) : %d cas ===' % (c, lab[c], len(d)))
    for _, r in d.sort_values(['gene', 'outil', 'sample']).iterrows(): print('  %-8s %-9s %-8s GeT-RM=%-34s outil=%s' % (r.gene, r.outil, r['sample'], r.getrm, r.genotype_outil))
print('\nVKORC1 (écriture non comparable) : non évalué ici.')
