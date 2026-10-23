import json, sys, pandas as pd
ech = sys.argv[1]
J = json.load(open(sys.argv[2] + '/sortie_%s.json' % ech))
P = pd.read_csv('../data/profils_genes_v4.csv').set_index('sample_id')
pr = J['profil']
print('== profil lu depuis le VCF vs corpus (specialité du job: %s)' % J['specialite'])
ident = diff = manq = 0; lignes = []
for g, v in pr.items():
    if g not in P.columns or g.startswith('HLA') or g == 'CYP2D6': continue
    ref = P.at[ech, g]
    a = None if v is None or (isinstance(v, float) and pd.isna(v)) else float(v); b = None if pd.isna(ref) else float(ref)
    if a == b: ident += 1
    else: diff += 1; lignes.append((g, a, b))
print('gènes comparés identiques: %d | différents: %d' % (ident, diff)); [print('  DIFF', l) for l in lignes]
print('non normaux lus:', {g: v for g, v in pr.items() if v not in (None, 1.0) and not g.startswith('HLA') and g != 'CYP2D6' and isinstance(v, (int, float)) and not pd.isna(v)})
print('résumé:', json.dumps(J['resume'], ensure_ascii=False)[:600])
print('bloquants:', J['bloquants'])
print('synthèse feux:', json.dumps(J['synthese'], ensure_ascii=False)[:1500])
print('à éviter toutes spécialités:', J['a_eviter_toutes_specialites'])
for c in J['choix']:
    print('GROUPE', c.get('code'), c.get('nom') if 'nom' in c else '', '| fiches:', [(f['medicament'], f.get('action')) for f in c['fiches']][:8], '| écartés:', [(e.get('medicament'), e.get('action') or e.get('raison')) for e in c.get('ecartes', [])][:8])
