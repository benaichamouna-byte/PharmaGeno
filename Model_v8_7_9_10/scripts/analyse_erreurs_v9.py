"""
analyse_erreurs_v9.py : erreurs hors-pli (out-of-fold) du DL (film) et de XGBoost sur le corpus v7, protocole v8. Lecture seule : aucun fichier n'est modifié, aucun entraînement.
Usage : python3 analyse_erreurs_v9.py   (depuis le dossier resultats_v9/)
"""
import numpy as np, pandas as pd
pd.set_option('display.width', 250)
cl = ['ADAPTER_DOSE', 'EVITER', 'STANDARD', 'SURVEILLER']
d = np.load('dl_film/dl_v7_film_oof.npz', allow_pickle=True); x = np.load('xgb/arbres_v7_xgb_fp_oof.npz', allow_pickle=True)
assert (d['ligne'] == x['ligne']).all() and (d['y'] == x['y']).all()
y = d['y']; pdl = d['proba'].argmax(1); px = x['proba'].argmax(1)
D = pd.DataFrame(dict(ligne=d['ligne'], drug=d['drug'], y=y, dl=pdl, xgb=px, pli=d['pli']))
print('lignes CV :', len(D), '| erreurs DL :', int((D.y != D.dl).sum()), f"({(D.y != D.dl).mean()*100:.2f} %) | erreurs XGB :", int((D.y != D.xgb).sum()))
print('\nmatrice de confusion DL (lignes = vrai, colonnes = prédit) :'); print(pd.crosstab(pd.Series(y).map(dict(enumerate(cl))), pd.Series(pdl).map(dict(enumerate(cl)))).to_string())
e = D[D.y != D.dl]; tot = D.groupby('drug').size(); err = e.groupby('drug').size().reindex(tot.index).fillna(0); r = (err / tot).sort_values(ascending=False)
print("\ntaux d'erreur DL par médicament (top 15) :"); print(pd.DataFrame(dict(taux_pct=(r*100).round(1), erreurs=err[r.index].astype(int), lignes=tot[r.index])).head(15).to_string())
print('\nmédicaments avec 0 erreur DL :', int((err == 0).sum()), 'sur', len(tot), '| part des erreurs dans les 10 premiers médicaments (en nombre) :', round(float(err.sort_values(ascending=False).head(10).sum()/err.sum())*100, 1), '%')
print('\nerreurs XGB par médicament :', D[D.y != D.xgb].groupby('drug').size().sort_values(ascending=False).to_dict())
ev = D[D.y == 1]; print('\nEVITER manqués : DL', int((ev.dl != 1).sum()), 'sur', len(ev), '| XGB', int((ev.xgb != 1).sum()))
print('EVITER manqués DL par médicament :', ev[ev.dl != 1].groupby('drug').size().sort_values(ascending=False).head(10).to_dict())
print('EVITER manqués XGB par médicament :', ev[ev.xgb != 1].groupby('drug').size().sort_values(ascending=False).to_dict())
