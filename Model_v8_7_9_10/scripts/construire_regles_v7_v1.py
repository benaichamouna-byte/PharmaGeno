"""
construire_regles_v7_v1.py : regles_v2_corrigees_monogene_v7.csv / regles_v2_corrigees_multigene_v7.csv = regles_v2_* + 2 corrections TRACÉES (aucun fichier existant modifié).
(1) Thiopuriniques : ajout de « TPMT normal -> STANDARD » et « NUDT15 normal -> STANDARD » pour azathioprine, mercaptopurine, thioguanine.
    Raison : DPWG n'a pas de recommandation pour les métaboliseurs normaux ; CPIC (guideline TPMT/NUDT15 et thiopurines) donne « standard starting dose » pour TPMT normal et NUDT15 normal.
    Source des règles : prescribing_guidance.json du dépôt PharmCAT (annotation PharmGKB de la guideline CPIC, ligne lookupKey {TPMT: Normal Metabolizer, NUDT15: Normal Metabolizer}).
    Vérifié : avec « l'action la plus sévère gagne », le moteur redonne les 32 combinaisons CPIC à phénotype connu, pour chacun des 3 médicaments.
(2) SLCO1B1 « Increased function » : les règles utilisaient la valeur 2.0 alors que le codage des profils (codage_pypgx_valeur_v7.csv) donne 1.5 -> 22 profils exclus à tort. Règles recodées 2.0 -> 1.5 (mono : 6 lignes ; multi : 6 lignes). Actions inchangées.
Usage : python3 construire_regles_v7_v1.py --mono regles_v2_monogene.csv --multi regles_v2_multigene.csv --guidance prescribing_guidance.json --sortie DOSSIER
"""
import argparse, json, os, re
import numpy as np, pandas as pd

DRUGS = ('azathioprine', 'mercaptopurine', 'thioguanine')

def clean(h): return re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', h)).strip()

def main():
    ap = argparse.ArgumentParser()
    for k in ('mono', 'multi', 'guidance', 'sortie'): ap.add_argument('--' + k, required=True)
    a = ap.parse_args(); os.makedirs(a.sortie, exist_ok=True)
    mono = pd.read_csv(a.mono); multi = pd.read_csv(a.multi); log = []
    guid = json.load(open(a.guidance, encoding='utf-8'))['guidelines']
    # ---- (1) thiopuriniques
    tpl = mono[(mono.medicament == 'mercaptopurine') & (mono.gene == 'TPMT') & (mono.valeur == 0.5)].iloc[0]
    new = []
    for g in guid:
        nm = g['guideline'].get('name', '')
        m = re.match(r'Annotation of CPIC Guideline for (azathioprine|mercaptopurine|thioguanine) and', nm)
        if not m: continue
        drug = m.group(1)
        rec = [r for r in g['recommendations'] if any(k.get('TPMT') == 'Normal Metabolizer' and k.get('NUDT15') == 'Normal Metabolizer' for k in r['lookupKey'])]
        assert len(rec) == 1, (drug, len(rec))
        txt = clean(rec[0]['text']['html']); assert 'standard starting dose' in txt.lower(), txt
        for gene in ('TPMT', 'NUDT15'):
            if ((mono.medicament == drug) & (mono.gene == gene) & (mono.valeur == 1.0)).any(): continue
            x = tpl.copy(); x['gene'] = gene; x['valeur'] = 1.0; x['medicament'] = drug; x['action'] = 'STANDARD'; x['ambigu'] = False; x['source'] = 'CPIC'
            x['n_valeurs'] = 1; x['phenotype'] = f'{gene} Normal Metabolizer (TPMT Normal + NUDT15 Normal)'; x['recommandation'] = txt
            x['fichier'] = 'prescribing_guidance.json (PharmCAT) ' + g['guideline']['id'] + ' / ' + rec[0]['id']
            for c, v in (('conditionnel', False), ('conflit_intra_source', False), ('divergence_autre_table_meme_source', False), ('gene_dans_les_31', True), ('codage_a_valider', False)):
                if c in x.index: x[c] = v
            if 'desaccord_autres_sources' in x.index: x['desaccord_autres_sources'] = np.nan
            new.append(x); log.append(dict(correction='thiopuriniques_normal_standard', fichier='mono', gene=gene, medicament=drug, avant='(absent)', apres='1.0 -> STANDARD', source=x['fichier']))
    mono = pd.concat([mono, pd.DataFrame(new)], ignore_index=True)
    # ---- (2) SLCO1B1 increased function 2.0 -> 1.5
    s = (mono.gene == 'SLCO1B1') & (mono.valeur == 2.0) & mono.phenotype.astype(str).str.lower().str.contains('increased function')
    for i in mono.index[s]: log.append(dict(correction='slco1b1_increased_2.0_vers_1.5', fichier='mono', gene='SLCO1B1', medicament=mono.at[i, 'medicament'], avant='2.0', apres='1.5', source='codage_pypgx_valeur_v7.csv'))
    mono.loc[s, 'valeur'] = 1.5
    sm = (multi.gene_b == 'SLCO1B1') & (multi.valeur_b == 2.0)
    for i in multi.index[sm]: log.append(dict(correction='slco1b1_increased_2.0_vers_1.5', fichier='multi', gene=multi.at[i, 'gene_a'] + '+SLCO1B1', medicament=multi.at[i, 'medicament'], avant=f"{multi.at[i,'valeur_a']}/2.0", apres=f"{multi.at[i,'valeur_a']}/1.5", source='codage_pypgx_valeur_v7.csv'))
    multi.loc[sm, 'valeur_b'] = 1.5
    assert (multi.gene_a != 'SLCO1B1').all()
    mono.to_csv(os.path.join(a.sortie, 'regles_v2_corrigees_monogene_v7.csv'), index=False); multi.to_csv(os.path.join(a.sortie, 'regles_v2_corrigees_multigene_v7.csv'), index=False)
    L = pd.DataFrame(log); L.to_csv(os.path.join(a.sortie, 'regles_v2_corrigees_v7_journal_corrections.csv'), index=False)
    print('mono :', len(mono), 'lignes | multi :', len(multi), 'lignes'); print(L.groupby(['correction', 'fichier']).size().to_string())

if __name__ == '__main__':
    main()
