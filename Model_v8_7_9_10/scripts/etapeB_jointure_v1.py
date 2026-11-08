#!/usr/bin/env python3
"""
etapeB_jointure_v1.py (8 nov. 2026) : ÉTAPE B de la grille v1.1 (vérification d'implémentation application PharmaGeno vs PharmCAT, PAS une validation indépendante).
Lit : le fichier d'étiquettes de l'étape A (figé AVANT de voir les réponses de l'application) et les fiches JSON de l'application (moteur[]).
Précisions de l'étape B, écrites AVANT la première lecture des réponses de l'application :
 - unité = (personne, guide, médicament) ; lignes PharmCAT = populations. Étiquettes distinctes hors AUCUNE -> "dépend de l'indication" (aussi si une ligne porte déjà indication=oui).
 - toutes les lignes AUCUNE -> AUCUNE.
 - application : action_dl (affichée) et action_cpic (règle) comparées séparément ; action absente (statut non ok) = abstention.
 - médicament PharmCAT absent des 189 médicaments de l'application = "absent" (compté à part de l'abstention).
 - distance sur l'ordre STANDARD<SURVEILLER<ADAPTER_DOSE<EVITER : 0 identique ; 1 mineure ; >=2 majeure.
 - sensibilité : même calcul avec la lecture alternative (colonne alt) quand elle existe ; rapportée à part.
Usage : python3 -I etapeB_jointure_v1.py ETIQUETTES.csv SORTIE_DIR JSON_NA19472 JSON_NA19085 ...
"""
import csv, json, os, sys, collections
ORD = {'STANDARD': 0, 'SURVEILLER': 1, 'ADAPTER_DOSE': 2, 'EVITER': 3}
ET, OUT, *JS = sys.argv[1:]
os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(ET)))
APP = {}
for j in JS:
    d = json.load(open(j)); s = d['id'] if False else os.path.basename(j).replace('sortie_', '').replace('.json', '')
    APP[s] = {m['medicament'].lower(): m for m in d['moteur']}
def agreg(rs):
    labs = {r['label'] for r in rs if r['label'] != 'AUCUNE'}
    ind = len(labs) > 1 or any(r['indication'] == 'oui' for r in rs)
    if not labs: return 'AUCUNE', False, False
    lab = max(labs, key=lambda x: ORD[x]); mix = any(r['mixte'] == 'oui' for r in rs if r['label'] == lab)
    return lab, ind, mix
def issue(ph, ind, act):
    if ph == 'AUCUNE': return '5 application seule' if act else '0 aucune action des deux côtés'
    if ind: return '6 depend de l\'indication'
    if act is None: return '4 abstention de l\'application'
    d = abs(ORD[act] - ORD[ph]); return {0: '1 identique', 1: '2 mineure'}.get(d, '3 majeure')
G = collections.defaultdict(list)
for r in rows: G[(r['sample'], r['source'], r['drug'].lower())].append(r)
out = []
for (s, src, drug), rs in sorted(G.items()):
    ph, ind, mix = agreg(rs)
    alts = [r['alt'] for r in rs if r['alt']]
    m = APP[s].get(drug)
    if m is None:
        out.append(dict(sample=s, guide=src, drug=drug, pharmcat=ph, indication=ind, mixte=mix, app_statut='ABSENT', app_dl='', app_regle='', sources_regle='', guide_dans_regle='', issue_dl='absent de l\'application' if ph != 'AUCUNE' else '0 absent (PharmCAT sans action)', issue_regle='absent de l\'application' if ph != 'AUCUNE' else '0 absent (PharmCAT sans action)', issue_dl_alt='', texte_cue=rs[0]['cue'])); continue
    dl = m.get('action_dl'); rg = m.get('action_cpic')
    sources = sorted({x.get('source', '') for x in m.get('regle_cpic', [])})
    srcset = {'FDA': {'FDA', 'FDA-etiquette'}}.get(src, {src})
    dans = bool(srcset & set(sources))
    iss_dl = issue(ph, ind, dl); iss_rg = issue(ph, ind, rg)
    alt = ''
    if alts and ph != 'AUCUNE' and not ind and dl is not None:
        alt = ' | '.join(sorted({issue(a, False, dl) for a in alts} | {iss_dl}))
    out.append(dict(sample=s, guide=src, drug=drug, pharmcat=ph, indication=ind, mixte=mix, app_statut=m['statut'], app_dl=dl or '', app_regle=rg or '', sources_regle='+'.join(sources), guide_dans_regle=dans, issue_dl=iss_dl, issue_regle=iss_rg, issue_dl_alt=alt, texte_cue=rs[0]['cue']))
fn = os.path.join(OUT, 'etapeB_detail_v1.csv')
w = csv.DictWriter(open(fn, 'w', newline=''), fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
def tab(titre, sel, key):
    c = collections.Counter(o[key] for o in out if sel(o)); n = sum(c.values())
    print('\n%s (n=%d)' % (titre, n))
    for k in sorted(c): print('  %-34s %4d' % (k, c[k]))
print('Unités (personne, guide, médicament) :', len(out), '| personnes :', sorted(APP))
for key, nom in (('issue_dl', 'application = action_dl (DL affiché)'), ('issue_regle', 'application = action_cpic (règle)')):
    print('\n=========', nom, '=========')
    tab('TOUTES', lambda o: True, key)
    for g in ('CPIC', 'DPWG', 'FDA'): tab('guide ' + g, lambda o, g=g: o['guide'] == g, key)
    for s in sorted(APP): tab('personne ' + s, lambda o, s=s: o['sample'] == s, key)
    tab('guide cité par la règle de l\'application', lambda o: o['guide_dans_regle'] is True, key)
    tab('guide NON cité par la règle de l\'application', lambda o: o['guide_dans_regle'] is False, key)
print('\nSensibilité (lecture alternative disponible) :', sum(1 for o in out if o['issue_dl_alt']), 'unités')
print('\n=== Différences majeures (DL) ===')
for o in out:
    if o['issue_dl'] == '3 majeure': print('  %s %-5s %-24s PharmCAT=%-12s DL=%-12s règle=%-12s sources_règle=%s' % (o['sample'], o['guide'], o['drug'], o['pharmcat'], o['app_dl'], o['app_regle'], o['sources_regle']))
print('\n=== Médicaments PharmCAT absents de l\'application ===')
print('  ', sorted({o['drug'] for o in out if o['app_statut'] == 'ABSENT' and o['pharmcat'] != 'AUCUNE'}))
