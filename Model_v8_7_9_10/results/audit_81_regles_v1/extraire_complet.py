"""Extraction v2 des recommandations par phenotype depuis les guidelines (JSON PharmGKB/ClinPGx).

Difference avec v1 (extraire_regles_guidelines.py, conserve intact) :
  1. les phenotypes sont lus sur l'ETIQUETTE du phenotype (avant '(' ou ','), pas sur la description
     (v1 lisait « two decreased function alleles » dans une description et classait « Low function » en 0.5) ;
  2. les phrases de conseil d'interaction (« Avoid moderate and strong CYP2D6 inhibitors ») ne servent plus
     a classer l'action (v1 : tamoxifene Normal => EVITER) ;
  3. plus de recommandations ecartees : « alternative statin », « consider alternative drug », etc. ;
  4. DPYD « Activity Score » converti sur l'echelle du projet (0.0 / 0.5 / 1.0) au lieu d'etre copie ;
  5. les grilles a DEUX GENES de CPIC (ex. CYP2C19 x CYP2D6, CYP2C19 x CYP2B6, SLCO1B1 x CYP2C9)
     sont extraites dans un fichier a part : regles_multigene ;
  6. chaque regle porte un drapeau « ambigu » quand le texte contient a la fois EVITER et ADAPTER_DOSE,
     et les autres sources en desaccord sont listees.
Usage : python3 -I extraire_regles_v2.py <dossier_json_guidelines> <dossier_sortie>
"""
import json, glob, re, html, os, sys
from collections import Counter, defaultdict
import pandas as pd

GUIDE, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

GENES31 = ['ABCG2','ACE','ADRB2','CACNA1S','CFTR','CYP1A2','CYP2A6','CYP2B6','CYP2C19','CYP2C9','CYP2D6',
           'CYP3A4','CYP3A5','CYP4F2','DPYD','EGFR','F5','G6PD','HLA-A','HLA-B','IFNL3','MT-RNR1','MTHFR',
           'NAT2','NUDT15','RYR1','SLC19A1','SLCO1B1','TPMT','UGT1A1','VKORC1']

def H(x): return x.get('html', '') if isinstance(x, dict) else str(x or '')
def nett(s): return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', s))).strip()

# ----------------------------------------------------------------------------- phenotype -> valeurs
def valeurs(label, gene=None):
    """Retourne la liste des valeurs (echelle projet 0.0/0.5/1.0/1.5/2.0) couvertes par l'etiquette.
    [] = indetermine ou non reconnu."""
    s = label.lower()
    s = re.split(r'\(', s)[0]            # coupe les descriptions « (~1-13% of patients) »
    s = re.split(r',', s)[0] if 'function' in s.split(',')[0] else s
    if 'indeterminate' in s or 'unknown' in s or s.strip() in ('n/a', ''): return []
    m = re.search(r'activity score\s*(?:of\s*)?([0-9.]+)', s)
    if m and not re.search(r'metaboli|function', s):
        a = float(m.group(1))
        if gene == 'DPYD':                 # CPIC/DPWG : AS 0-0.5 = PM ; 1-1.5 = IM ; 2 = NM
            return [0.0] if a <= 0.5 else [0.5] if a <= 1.5 else [1.0]
        return []                          # autre gene : on ne devine pas
    out = set()
    if re.search(r'\bum\b', s): out.add(2.0)
    if re.search(r'\brm\b', s): out.add(1.5)
    if re.search(r'\bnm\b|\bem\b', s): out.add(1.0)
    if re.search(r'\bim\b', s): out.add(0.5)
    if re.search(r'\bpm\b', s): out.add(0.0)
    if re.search(r'\bdeficient', s): out.add(0.0)       # G6PD
    if re.search(r'\bvariable\b', s): out.add(0.5)      # G6PD
    if re.search(r'increased risk', s): out.add(0.0)      # MT-RNR1 (codage a valider)
    if re.search(r'ultra-?rapid', s): out.add(2.0)
    if re.search(r'(?<!ultra)(?<!ultra-)\brapid', s): out.add(1.5)
    if re.search(r'normal|extensive', s) and not re.search(r'poor|intermediate', s): out.add(1.0)
    if re.search(r'normal', s) and re.search(r'poor|intermediate', s): out.add(1.0)
    if re.search(r'intermediate', s): out.add(0.5)
    if re.search(r'poor', s): out.add(0.0)
    if re.search(r'possible increased function|increased function', s): out.add(2.0)
    if re.search(r'possible decreased function|(?<!possible )decreased function', s): out.add(0.5)
    if re.search(r'\blow function|no function', s): out.add(0.0)
    if re.search(r'normal function', s): out.add(1.0)
    return sorted(out)

# ----------------------------------------------------------------------------- recommandation -> classe
NEG   = r'no reason to (?:avoid|withhold)|not necessary to avoid|no need to avoid'
EVIT  = (r'\bavoid\b|contraindicat|do not use|\bnot recommended\b|(?:select|choose|consider|prescribe|recommend|use)\w*\s+'
         r'(?:an?\s+|the\s+)?(?:clinically appropriate\s+|non-tramadol\s+|other\s+)?'
         r'(?:alternat\w+|(?:\w+\s+){0,3}not (?:predominantly|primarily) metabolized)'
         r'|\balternative (?:drug|therap|agent|statin|antidepressant|opioid|antiplatelet|hormonal)|consider (?:an? )?aromatase inhibitor')
ADAPT = (r'(?:increase|reduce|decrease|lower|raise|double|triple)\s+(?:the\s+)?(?:\w+\s+){0,3}?(?:dos|starting)|decreased dose|reduced dose'
         r'|dose reduction|dose increase|start with \d|\d+\s*%\s*(?:of|reduction)|\d+-fold higher dos|titrat'
         r'|adjust (?:the )?dos|consider a (?:lower|higher)|initiate with a dose of|≤\s*\d+\s*mg|<=\s*\d+\s*mg'
         r'|lower (?:starting )?dose|lower maintenance|do not (?:exceed|give doses exceeding)|total daily dose of \d')
SURV  = r'\bmonitor\b|\balert\b|cautiously|with caution|therapeutic drug monitoring|be alert|careful'
STD   = (r'label[- ]recommended|standard (?:starting |of care )?dos|recommended (?:starting )?dos|no (?:action|adjustment|change)s?'
         r'(?: is| are)?\s*(?:needed|required|recommended)|no indication to change|usual dos|normal dos|'
         r'initiate (?:therapy|treatment)?\s*(?:with\s+)?(?:the\s+)?(?:standard|recommended|desired|typical)|'
         r'prescribe (?:the )?(?:desired|standard|recommended)|use (?:the )?label|typical (?:initial|dosing)|'
         r'initiate standard|without an increase in (?:the )?side effects|therapy adjustment is not required|negligible effect|minor effect on')
RIEN  = r'no recommendation|insufficient data|insufficient evidence|no guideline'

def nettoie_reco(rec):
    rec = re.split(r'\s*Classification of recommendation', rec, flags=re.I)[0]
    phrases = re.split(r'(?<=[.;])\s+', rec)
    garde = [p for p in phrases if not re.search(r'\bavoid\b[^.]*\binhibitors?\b|drug-drug interaction', p, re.I)]
    return ' '.join(garde) if garde else rec

def classe(rec):
    """-> (action, ambigu). Action = famille de la PREMIERE instruction du texte nettoye."""
    r = nettoie_reco(rec).lower().replace('alterantive', 'alternative')
    if re.search(NEG, r): return 'STANDARD', False
    pos = {}
    for nom, pat in (('EVITER', EVIT), ('ADAPTER_DOSE', ADAPT), ('SURVEILLER', SURV), ('STANDARD', STD)):
        m = re.search(pat, r)
        if m: pos[nom] = m.start()
    if re.match(r'\s*(?:no recommendation|no pharmacotherapeutic)', r) and not (set(pos) & {'EVITER', 'ADAPTER_DOSE', 'SURVEILLER'}): return None, False
    if not pos: return None, False
    first = min(pos, key=pos.get)
    ambigu = ('EVITER' in pos and 'ADAPTER_DOSE' in pos) or (first == 'STANDARD' and 'EVITER' in pos)
    return first, ambigu

# ----------------------------------------------------------------------------- lecture des tables
def cells_of(tr): return [nett(c) for c in re.findall(r'<t[dh].*?</t[dh]>', tr, re.S)]

def gene_dans(texte, genes):
    for g in genes:
        if re.search(r'(?<![A-Z0-9])' + re.escape(g) + r'(?![A-Z0-9])', texte): return g
    return None

mono, multi, sans_classe = [], [], Counter()
for f in sorted(glob.glob(f'{GUIDE}/PA*.json')):
    try: g = json.load(open(f))['guideline']
    except Exception: continue
    src = g.get('source', '?')
    genes = [x.get('symbol', '') for x in g.get('relatedGenes', []) if isinstance(x, dict) and x.get('symbol')]
    meds = [x.get('name', '').lower().strip() for x in g.get('relatedChemicals', []) if isinstance(x, dict) and x.get('name')]
    if not genes or not meds: continue
    fn = os.path.basename(f)
    for ti, tb in enumerate(re.findall(r'<table.*?</table>', H(g.get('textMarkdown')), re.S)):
        trs = re.findall(r'<tr.*?</tr>', tb, re.S)
        if len(trs) < 2: continue
        ent = [c.lower() for c in cells_of(trs[0])]

        # ---- cas A : grille a deux genes (en-tetes de colonnes = phenotypes d'un autre gene)
        col_genes = [gene_dans(c.upper() if False else cells_of(trs[0])[i], genes) for i, c in enumerate(ent)]
        if len(ent) >= 3 and sum(1 for i, cg in enumerate(col_genes) if i > 0 and cg) >= 2 and 'recommendation' not in ' '.join(ent):
            for tr in trs[1:]:
                cl = cells_of(tr)
                if len(cl) != len(ent): continue
                g1 = gene_dans(cl[0], genes)
                if not g1: continue
                v1 = valeurs(cl[0], g1)
                for j in range(1, len(cl)):
                    g2 = col_genes[j]
                    if not g2 or g2 == g1: continue
                    v2 = valeurs(cells_of(trs[0])[j], g2)
                    a, amb = classe(cl[j])
                    if not v1 or not v2: continue
                    if a is None:
                        sans_classe[('grille', cl[j][:400])] += 1; continue
                    for x in v1:
                        for y in v2:
                            for md in meds:
                                (ga, va, gb, vb) = (g1, x, g2, y) if g1 < g2 else (g2, y, g1, x)
                                multi.append(dict(gene_a=ga, valeur_a=va, gene_b=gb, valeur_b=vb, medicament=md, action=a,
                                                  ambigu=amb, source=src, phenotype_a=cl[0][:60], phenotype_b=cells_of(trs[0])[j][:60],
                                                  recommandation=cl[j], fichier=fn, table=ti))
            continue

        # ---- cas B : table HLA-B*15:02 positif/negatif x phenotype CYP2C9 (phenytoine, version actuelle)
        if len(ent) >= 6 and 'hla-b' in ent[0] and 'cyp2c9' in ent[1]:
            for tr in trs[1:]:
                cl = cells_of(tr)
                if len(cl) < 6: continue
                hla = 'positif' if 'positive' in cl[0].lower() or 'positif' in cl[0].lower() else 'negatif'
                ph = cl[1]
                vv = valeurs(ph, 'CYP2C9') if 'any' not in ph.lower() else [0.0, 0.5, 1.0]
                rec = cl[5]
                a, amb = classe(rec)
                if a is None or not vv: continue
                for x in vv:
                    for md in meds:
                        multi.append(dict(gene_a='CYP2C9', valeur_a=x, gene_b='HLA-B', valeur_b=1.0 if hla == 'negatif' else 0.0,
                                          medicament=md, action=a, ambigu=amb, source=src, phenotype_a=ph[:60],
                                          phenotype_b='HLA-B*15:02 ' + hla, recommandation=rec, fichier=fn, table=ti))
            continue

        # ---- cas C : table a un gene
        i_ph = next((i for i, c in enumerate(ent) if 'phenotype' in c or 'genotype' in c or 'function' in c or 'activity' in c), None)
        i_re = next((i for i, c in enumerate(ent) if 'recommendation' in c and 'classification' not in c and 'level' not in c), None)
        if i_ph is None or i_re is None: continue
        if any(('positive' in c or 'negative' in c) for c in ent): continue   # tables HLA-B x CYP2C9 : traitees comme multigene
        entete_gene = gene_dans(cells_of(trs[0])[i_ph], genes)
        for tr in trs[1:]:
            cl = cells_of(tr)
            if len(cl) <= max(i_ph, i_re): continue
            ph, rec = cl[i_ph], cl[i_re]
            if not ph or not rec or len(rec) < 8: continue
            gn = gene_dans(ph, genes) or entete_gene or (genes[0] if len(genes) == 1 else None)
            if gn is None: continue
            if re.search(r'cnsha', ph, re.I): continue          # sous-type G6PD rare (anemie hemolytique chronique) : non codable dans l'echelle projet
            vv = valeurs(ph, gn)
            if not vv: continue
            a, amb = classe(rec)
            if a is None:
                sans_classe[('mono', )] += 1; continue
            for x in vv:
                for md in meds:
                    mono.append(dict(gene=gn, valeur=x, medicament=md, action=a, ambigu=amb, source=src, n_valeurs=len(vv),
                                     phenotype=ph[:70], recommandation=rec, fichier=fn, table=ti,
                                     guideline_multigene=len(genes) > 1))

RANG = {'CPIC': 0, 'DPWG': 1, 'RNPGx': 2}

SEV = {'EVITER': 3, 'ADAPTER_DOSE': 2, 'SURVEILLER': 1, 'STANDARD': 0}

def dedupe(df, cle):
    df = df.copy()
    df['rang'] = df['source'].map(lambda s: RANG.get(s, 3))
    df = df.sort_values(cle + ['rang', 'fichier', 'table'])
    lignes = []
    for _, sub in df.groupby(cle, sort=False):
        top = sub[sub.rang == sub.rang.min()]
        courant = top[top.table == top.table.min()]       # table la plus haute = version courante de la guideline
        if 'n_valeurs' in courant: courant = courant[courant.n_valeurs == courant.n_valeurs.min()]   # etiquette precise avant etiquette-intervalle
        intra = courant.action.nunique() > 1               # conflit reel dans la MEME table
        autre_version = top.action.nunique() > 1           # divergence avec une table plus ancienne / autre fichier
        p = (courant.sort_values('action', key=lambda c: c.map(SEV), ascending=False).iloc[0] if intra else courant.iloc[0]).copy()
        if intra: p['ambigu'] = True
        o = sub[sub.action != p.action]
        p['desaccord_autres_sources'] = ';'.join(sorted({f"{r.source}:{r.action}" for r in o.itertuples()}))
        p['conflit_intra_source'] = bool(intra)
        p['divergence_autre_table_meme_source'] = bool(autre_version)
        lignes.append(p)
    return pd.DataFrame(lignes).drop(columns='rang').reset_index(drop=True)

def conditionnel(t):
    return bool(re.search(r'co-?medication|comedication|immunosuppression|indication|if the patient|if patient', t, re.I))

m = dedupe(pd.DataFrame(mono), ['gene', 'valeur', 'medicament'])
m['gene_dans_les_31'] = m.gene.isin(GENES31)
m['conditionnel'] = m.recommandation.map(conditionnel)           # l'action depend d'une co-medication / indication : a relire
m['codage_a_valider'] = m.gene.isin(['G6PD', 'MT-RNR1', 'HLA-B'])  # genes non metaboliseurs : codage projet a definir
x = dedupe(pd.DataFrame(multi), ['gene_a', 'valeur_a', 'gene_b', 'valeur_b', 'medicament'])
x['conditionnel'] = x.recommandation.map(conditionnel)
m.to_csv(f'{OUT}/regles_v2_monogene.csv', index=False)
x.to_csv(f'{OUT}/regles_v2_multigene.csv', index=False)

print(f'MONOGENE : {len(m)} regles | couples gene-medicament {m.groupby(["gene","medicament"]).ngroups} | genes {m.gene.nunique()} | medicaments {m.medicament.nunique()}')
print('  actions :', m.action.value_counts().to_dict(), '| sources :', m.source.value_counts().to_dict())
print('  ambigues :', int(m.ambigu.sum()), '| avec desaccord inter-sources :', int((m.desaccord_autres_sources.fillna("") != "").sum()))
print('  genes :', m.gene.value_counts().to_dict())
print(f'MULTIGENE : {len(x)} regles | paires de genes {x.groupby(["gene_a","gene_b"]).ngroups} | medicaments {x.medicament.nunique()}')
print('  paires :', x.groupby(['gene_a', 'gene_b']).size().to_dict())
print('  actions :', x.action.value_counts().to_dict(), '| ambigues :', int(x.ambigu.sum()))
print('NON CLASSEES :', sum(sans_classe.values()))
for (k, t), v in sans_classe.most_common(15): print(f'   {v:3d} [{k}] {t}')

pd.DataFrame([dict(type=k, texte=t, n=v) for (k, t), v in sans_classe.most_common()]).to_csv(f'{OUT}/non_classees_v2.csv', index=False)
