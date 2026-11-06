#!/usr/bin/env python3
"""
diagnostic_niveau_source_v1.py (6 nov. 2026) : LECTURE SEULE, aucun modèle entraîné, aucun fichier du protocole modifié, ensemble final non lu.
Question : pourquoi le F1 macro par niveau de source vaut-il 0,6666 pour EMA-etiquette avec les quatre modèles ?
Le script reprend exactement les prédictions hors-pli de comparaison_equitable_v14_v1.py (ensemble des graines de chaque bras) et affiche, pour les niveaux demandés :
classes réellement présentes (vraies / prédites), matrice de confusion, F1 par classe, médicaments concernés. Sortie purement descriptive (analyse « décidée après », étiquetée comme telle).
Usage (depuis scripts/) : python3 diagnostic_niveau_source_v1.py --dl ../results/dl_imbrique_v14_equitable:choisie_cal --xgb ../results/eval_arbres_v14_xgb:choisie_cal --rf ../results/eval_arbres_v14_rf:choisie_cal --niveaux EMA-etiquette HCSC-etiquette
"""
import argparse, os, sys
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from sklearn.metrics import f1_score, confusion_matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import protocole_commun_v10 as pc
from evaluer_dl_imbrique_v5 import niveau_par_medicament
from comparaison_equitable_v14_v1 import charger


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data', default='../data/corpus_v14/phenotype_drug_dataset_v14.csv')
    for k in ('dl', 'xgb', 'rf'): ap.add_argument('--' + k, required=True, help='dossier:quoi')
    ap.add_argument('--niveaux', nargs='+', default=['EMA-etiquette'])
    a = ap.parse_args()
    d = pc.charger(a.data, None); classes = d['classes']; K = len(classes)
    bras = {'DL': a.dl, 'XGBoost': a.xgb, 'Forêt aléatoire': a.rf}
    niv = niveau_par_medicament(); meds_all = np.array(d['meds']); lig0 = None; y0 = None; pred = {}
    for nom, spec in bras.items():
        dos, quoi = spec.rsplit(':', 1); lig, y, Ps = charger(dos, quoi)
        if lig0 is None: lig0, y0 = lig, y
        assert (lig == lig0).all() and (y == y0).all()
        pred[nom] = np.mean(Ps, 0).argmax(1)
    meds = meds_all[d['drug_idx'][lig0]]; dn = np.array([niv[m] for m in meds_all])[d['drug_idx'][lig0]]
    print('classes (indice : nom) :', dict(enumerate(classes)))
    for lvl in a.niveaux:
        mk = dn == lvl; print('\n' + '=' * 78 + '\nNIVEAU %s : %d lignes, %d médicaments' % (lvl, mk.sum(), len(set(meds[mk]))))
        print('classes vraies présentes   :', {classes[c]: int((y0[mk] == c).sum()) for c in range(K) if (y0[mk] == c).any()})
        for nom, p in pred.items():
            print('\n-- %s' % nom)
            print('classes prédites présentes :', {classes[c]: int((p[mk] == c).sum()) for c in range(K) if (p[mk] == c).any()})
            lab = sorted(set(y0[mk]) | set(p[mk]))
            print('F1 macro (labels = présentes dans vrai OU prédit, comme le script v1) : %.4f ; labels : %s' % (f1_score(y0[mk], p[mk], average='macro'), [classes[c] for c in lab]))
            print('F1 par classe :', {classes[c]: round(float(f), 4) for c, f in zip(lab, f1_score(y0[mk], p[mk], labels=lab, average=None, zero_division=0))})
            print('confusion (lignes = vrai, colonnes = prédit ; ordre %s) :' % [classes[c] for c in lab]); print(confusion_matrix(y0[mk], p[mk], labels=lab))
        t = pd.crosstab(meds[mk], [classes[c] for c in y0[mk]]); print('\nmédicaments du niveau (lignes par classe vraie) :'); print(t.to_string())


if __name__ == '__main__':
    main()
