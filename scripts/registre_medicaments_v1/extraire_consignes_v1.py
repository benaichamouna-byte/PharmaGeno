#!/usr/bin/env python3
"""
extraire_consignes_v1.py : pour une liste de médicaments du registre, extrait des guidelines PharmGKB (fichiers JSON fournis) le résumé,
le texte de la consigne, les liens et les références. Ne classe rien : la lecture et la classification se font ensuite, à valider.
Usage : python3 extraire_consignes_v1.py --ga DOSSIER_JSON --registre registre_medicaments_v1.csv --palier P1b_guideline_regles_exclues,P1c_guideline_sans_regle_extraite --genes-autorises "ABCG2 CYP2B6 ..." --sortie consignes.csv
"""
import argparse, glob, html, json, os, re
import pandas as pd


def texte(h):
    h = re.sub(r'<(br|/p|/h\d|/li|/tr)[^>]*>', '\n', h or '')
    h = re.sub(r'<[^>]+>', '', h)
    return re.sub(r'\n\s*\n+', '\n', html.unescape(h)).strip()


def liens(h):
    return sorted(set(re.findall(r'href="(https?://[^"]+)"', h or '')))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ga', required=True); ap.add_argument('--registre', required=True)
    ap.add_argument('--palier', required=True); ap.add_argument('--genes-autorises', required=True); ap.add_argument('--sortie', required=True)
    a = ap.parse_args()
    ok = set(a.genes_autorises.split())
    reg = pd.read_csv(a.registre).fillna('')
    reg = reg[reg.palier_provisoire.isin(a.palier.split(','))]
    meds = [m for m, g in zip(reg.medicament, reg.guideline_genes) if set(x for x in g.split(';') if x) <= ok]
    lignes = []
    for f in sorted(glob.glob(os.path.join(a.ga, 'PA*.json'))):
        G = json.load(open(f, encoding='utf-8'))['guideline']
        drugs = [re.sub(r'\s+', ' ', c['name'].strip().lower()) for c in G.get('relatedChemicals', [])]
        for d in drugs:
            if d in meds:
                th = (G.get('textMarkdown') or {}).get('html', '')
                lignes.append({
                    'medicament': d, 'organisme': G.get('source'), 'guideline': G.get('name'), 'id': G['id'],
                    'genes': ';'.join(x['symbol'] for x in G.get('relatedGenes', [])),
                    'dosage': G.get('dosingInformation'), 'alternative_medicamenteuse': G.get('alternateDrugAvailable'), 'test': G.get('hasTestingInfo'),
                    'resume': texte((G.get('summaryMarkdown') or {}).get('html', '')),
                    'texte_debut': texte(th)[:1500], 'liens_fichiers': ' | '.join(liens(th)[:4]),
                    'references_pmid': ';'.join(str(c.get('_sameAs', '')).split('/')[-1] for c in G.get('literature', [])[:5]),
                    'lien_pharmgkb': 'https://www.pharmgkb.org/guidelineAnnotation/' + G['id'],
                })
    out = pd.DataFrame(lignes).sort_values(['medicament', 'organisme'])
    out.to_csv(a.sortie, index=False)
    print(len(meds), 'médicaments,', len(out), 'lignes (médicament x guideline) ->', a.sortie)


if __name__ == '__main__':
    main()
