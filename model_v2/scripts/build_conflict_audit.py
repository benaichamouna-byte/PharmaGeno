"""
build_conflict_audit.py — Audit documentaire de la resolution des conflits de labels

Niveau documentaire : ne modifie ni dataset ni modeles.
Consolide les trois passes de resolution (v1, v2, v3) en un document unique
tracant l origine de chaque decision de label.

Sorties : docs/conflict_audit.csv, docs/conflict_audit_report.md
"""
import pandas as pd, os

DATA_DIR = '/home/mouna/projet_memoire/model_v2/data'
DOCS_DIR = '/home/mouna/projet_memoire/model_v2/docs'
os.makedirs(DOCS_DIR, exist_ok=True)

v1 = pd.read_csv(f'{DATA_DIR}/resolution_conflits_rapport.csv')
v2 = pd.read_csv(f'{DATA_DIR}/resolution_conflits_rapport_v2.csv')
v3 = pd.read_csv(f'{DATA_DIR}/resolution_conflits_rapport_v3.csv')

audit = v3[['gene','drug','statut','valides','invalides_supprimees']].copy()
audit = audit.rename(columns={
    'statut': 'statut_final',
    'valides': 'actions_retenues',
    'invalides_supprimees': 'n_lignes_supprimees'})

audit = audit.merge(
    v1[['gene','drug','statut','source']].rename(
        columns={'statut':'statut_passe1','source':'source_passe1'}),
    on=['gene','drug'], how='left')
audit = audit.merge(
    v2[['gene','drug','statut','source_utilisee']].rename(
        columns={'statut':'statut_passe2','source_utilisee':'source_passe2'}),
    on=['gene','drug'], how='left')

INTERPRETATION = {
    'aucune_guideline':          'Aucune guideline CPIC identifiee pour cette paire',
    'texte_sans_signal':         'Guideline trouvee mais aucune action extractible du texte',
    'coherent_apres_nettoyage':  'Coherence retablie par suppression des lignes invalides',
    'conflit_persiste_niveau3':  'Actions multiples legitimes selon le phenotype — non reductible a une action unique',
}
audit['interpretation'] = audit['statut_final'].map(INTERPRETATION)

ordre = ['gene','drug','statut_final','actions_retenues','n_lignes_supprimees',
         'interpretation','statut_passe1','source_passe1','statut_passe2','source_passe2']
audit = audit[ordre].sort_values(['statut_final','gene','drug'])
audit.to_csv(f'{DOCS_DIR}/conflict_audit.csv', index=False)

stats = audit['statut_final'].value_counts().to_dict()
n_supp = int(audit['n_lignes_supprimees'].sum())
persist = audit[audit['statut_final']=='conflit_persiste_niveau3']

r = ['# Audit de resolution des conflits de labels', '',
     f'Paires gene-medicament auditees : **{len(audit)}**',
     f'Lignes supprimees au total : **{n_supp}**', '',
     '## Procedure', '',
     'Trois passes successives ont ete appliquees aux paires gene-medicament portant des actions contradictoires :', '',
     '| Passe | Methode | Paires resolues |',
     '|---|---|---|',
     f"| 1 | Recherche de guideline CPIC par paire | {int((v1['statut']=='resolu').sum())} |",
     f"| 2 | Recherche elargie, sources multiples | {int((v2['statut']=='resolu').sum())} |",
     f"| 3 | Suppression des lignes invalides | {stats.get('coherent_apres_nettoyage',0)} |",
     '', '## Etat final', '',
     '| Statut | Paires | Interpretation |', '|---|---|---|']
for s, n in sorted(stats.items(), key=lambda x: -x[1]):
    r.append(f'| {s} | {n} | {INTERPRETATION.get(s,"")} |')

r += ['', '## Conflits persistants — analyse', '',
      f'{len(persist)} paires conservent plusieurs actions apres les trois passes. ',
      'Ces cas ne constituent pas des erreurs de donnees : l action clinique recommandee ',
      'depend du phenotype precis du patient, et non uniquement de la paire gene-medicament.', '',
      '| Gene | Medicament | Actions | Justification clinique |',
      '|---|---|---|---|']

JUSTIF = {
 ('CYP2D6','tamoxifen'):      'Poor Metabolizer : alternative recommandee. Intermediate : surveillance ou dose ajustee.',
 ('CYP2C19','voriconazole'):  'Ultrarapid : risque d echec therapeutique. Poor : risque de toxicite. Actions opposees.',
 ('CYP3A5','tacrolimus'):     'Expresseur : augmentation de dose requise. Non-expresseur : dose standard.',
 ('CYP2C9','fluvastatin'):    'Selon le degre de reduction d activite : dose reduite ou alternative.',
 ('SLCO1B1','fluvastatin'):   'Fonction de transport reduite : risque de myopathie variable selon le genotype.',
 ('CYP2C19','mavacamten'):    'Guideline recente, recommandations variables selon la source.',
}
for _, row in persist.iterrows():
    j = JUSTIF.get((row['gene'], row['drug']), '')
    r.append(f"| {row['gene']} | {row['drug']} | {row['actions_retenues']} | {j} |")

r += ['', '## Consequence methodologique', '',
      'L existence de ces conflits legitimes justifie la formulation du probleme adoptee dans ce travail. ',
      'Une table de correspondance gene -> action serait insuffisante : la meme paire gene-medicament ',
      'appelle des actions differentes selon le phenotype. Le modele doit donc apprendre une fonction ',
      'de la forme (profil genetique complet, medicament) -> action, ce qui correspond a l architecture ',
      'dual-branch retenue.', '',
      '## Tracabilite', '',
      'Le fichier `conflict_audit.csv` conserve pour chaque paire le statut obtenu a chacune des trois passes ',
      'ainsi que la source utilisee, permettant de retracer l origine de toute decision de label.']

with open(f'{DOCS_DIR}/conflict_audit_report.md','w') as f:
    f.write('\n'.join(r))

print(f'Paires auditees : {len(audit)}')
print(f'Lignes supprimees : {n_supp}')
for s, n in sorted(stats.items(), key=lambda x: -x[1]):
    print(f'  {s:28s} {n:3d}')
print(f'\nFichiers : docs/conflict_audit.csv, docs/conflict_audit_report.md')
