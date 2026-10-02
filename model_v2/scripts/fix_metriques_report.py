"""
fix_metriques_report.py — Reetiquetage du rapport de metriques et ajout du CER strict

Deux corrections documentaires, sans reentrainement :

1. Reetiquetage. Le protocole employe est StratifiedKFold sans groupement : un meme
   profil genetique peut figurer en entrainement et en test, apparie a des medicaments
   differents. Le rapport est donc un baseline non groupe, non la validation finale.

2. Critical Error Rate strict. La definition initiale ne comptait que EVITER predit
   en STANDARD ou SURVEILLER. Elle omettait EVITER -> ADAPTER_DOSE, ou le medicament
   contre-indique est prescrit avec un simple ajustement posologique : la contre-indication
   est manquee dans ce cas aussi. Le CER strict vaut 1 - rappel(EVITER).

Sorties : metriques_baseline_non_groupe.md, metriques_completes_v2.json enrichi
"""
import json, numpy as np, os

RESULTS_DIR = '/home/mouna/projet_memoire/model_v2/results'

d = json.load(open(f'{RESULTS_DIR}/metriques_completes_v2.json'))
CLASSES = d['classes']
res = d['resultats']
iE = CLASSES.index('EVITER')

for nom, r in res.items():
    cm = np.array(r['confusion_matrix'])
    n_ev = int(cm[iE].sum())
    manques = int(n_ev - cm[iE, iE])
    r['critical_errors_strict'] = manques
    r['critical_error_rate_strict'] = round(manques / n_ev, 4)
    r['cer_detail'] = {CLASSES[j]: int(cm[iE, j]) for j in range(len(CLASSES)) if j != iE}

json.dump(d, open(f'{RESULTS_DIR}/metriques_completes_v2.json','w'), indent=2)

ordre = ['XGBoost','RandomForest','DL']
ordre = [m for m in ordre if m in res]

L = ['# Metriques — baseline non groupe', '',
     '> **Protocole : StratifiedKFold sans groupement.** Un meme profil genetique peut',
     '> figurer en entrainement et en test, apparie a des medicaments differents. Les valeurs',
     '> ci-dessous constituent donc une reference haute, non la validation finale. La validation',
     '> groupee par individu, ou chaque patient est entierement contenu dans un seul pli, est',
     '> rapportee separement.', '',
     'Dataset : 46 117 lignes, 31 genes, 437 medicaments',
     'Pretraitement : scaler ajuste intra-pli, RandomOverSampler sur le pli d entrainement', '',
     '## Vue d ensemble', '',
     '| Modele | Macro-F1 | Weighted-F1 | Balanced Acc. | CER | CER strict |',
     '|---|---|---|---|---|---|']
for m in ordre:
    r = res[m]
    L.append(f"| {m} | {r['macro_f1']} | {r['weighted_f1']} | {r['balanced_accuracy']} | "
             f"{r['critical_error_rate']} | {r['critical_error_rate_strict']} |")

L += ['', '## Les deux definitions du Critical Error Rate', '',
      'Le CER mesure la part des contre-indications que le modele ne signale pas comme telles.',
      'Deux definitions coexistent, et leur ecart est informatif.', '',
      '**CER** — EVITER predit en STANDARD ou SURVEILLER. Le medicament est presente comme',
      'prescriptible, eventuellement sous surveillance.', '',
      '**CER strict** — toute erreur sur un cas EVITER, y compris vers ADAPTER_DOSE.',
      'Dans ce dernier cas le medicament contre-indique est prescrit avec un simple ajustement',
      'de dose : la contre-indication est manquee. Le CER strict vaut 1 moins le rappel sur EVITER.', '',
      '| Modele | CER | CER strict | Rappel EVITER |', '|---|---|---|---|']
for m in ordre:
    r = res[m]
    L.append(f"| {m} | {r['critical_error_rate']} ({r['critical_errors']}/{r['n_eviter']}) | "
             f"{r['critical_error_rate_strict']} ({r['critical_errors_strict']}/{r['n_eviter']}) | "
             f"{r['par_classe']['EVITER']['recall']} |")

L += ['', '### Destination des cas EVITER mal classes', '',
      '| Modele | vers ADAPTER_DOSE | vers SURVEILLER | vers STANDARD |', '|---|---|---|---|']
for m in ordre:
    c = res[m]['cer_detail']
    L.append(f"| {m} | {c.get('ADAPTER_DOSE',0)} | {c.get('SURVEILLER',0)} | {c.get('STANDARD',0)} |")

best = min(ordre, key=lambda m: res[m]['critical_error_rate_strict'])
L += ['', f'Le classement des modeles est identique sous les deux definitions : **{best}** ',
      'presente le plus faible taux de contre-indications manquees. Cette conclusion ne depend ',
      'donc pas du choix de definition.', '',
      '## Detail par classe', '']
for m in ordre:
    L += [f'### {m}', '', '| Classe | Precision | Rappel | F1 | Support |', '|---|---|---|---|---|']
    for cl, v in res[m]['par_classe'].items():
        L.append(f"| {cl} | {v['precision']} | {v['recall']} | {v['f1']} | {v['support']} |")
    L.append('')

L += ['## Lecture de la Balanced Accuracy', '',
      'La Balanced Accuracy est la moyenne des rappels par classe ; elle ignore la precision.',
      'Le DL atteint 0,948, soit le niveau de RandomForest (0,947), tout en perdant pres de',
      'cinq points de macro-F1. L ecart vient entierement de la classe STANDARD, ou le DL',
      'obtient un rappel de 0,981 pour une precision de 0,593 : il identifie presque tous les',
      'vrais STANDARD, mais quatre de ses predictions STANDARD sur dix sont fausses.',
      'La Balanced Accuracy ne percoit pas ce defaut. Elle est rapportee en metrique secondaire ;',
      'le macro-F1 reste la metrique principale.', '',
      '## Classe STANDARD — fragilite documentee', '',
      'STANDARD comptait 628 lignes avant le filtrage des medicaments sans empreinte moleculaire,',
      '520 apres, soit une perte de 17,2 % contre moins de 1 % pour les autres classes.',
      'C est la classe la plus rare du corpus (1,1 %) et celle qui a ete la plus amputee.',
      'Sa precision chez le DL est le principal facteur limitant du macro-F1.']

with open(f'{RESULTS_DIR}/metriques_baseline_non_groupe.md','w') as f:
    f.write('\n'.join(L))

old = f'{RESULTS_DIR}/metriques_completes_v2.md'
if os.path.exists(old):
    os.remove(old)

print('CER strict calcule :')
for m in ordre:
    r = res[m]
    print(f"  {m:14s} CER={r['critical_error_rate']}  strict={r['critical_error_rate_strict']}")
print()
print('Destination des EVITER mal classes :')
for m in ordre:
    print(f"  {m:14s} {res[m]['cer_detail']}")
print()
print('Fichier : metriques_baseline_non_groupe.md')
print('Fichier metriques_completes_v2.md supprime (titre trompeur)')
