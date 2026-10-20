"""
resume_dl_v9.py : tableau récapitulatif de TOUTES les configurations du DL (film) et des références XGBoost / RF, sur le corpus v7, protocole v8 (moyenne et écart-type sur 5 plis).
Lecture seule. Usage : python3 resume_dl_v9.py   (depuis le dossier qui contient resultats_v9/)  -> resultats_v9/RESUME_phase1_phase2_v9.csv
"""
import pandas as pd
C = [('XGBoost (empreinte)', 'resultats_v9/xgb/arbres_v7_xgb_fp_resultats_par_pli.csv'),
     ('RF (empreinte)', 'resultats_v9/rf/arbres_v7_rf_fp_resultats_par_pli.csv'),
     ('DL film : empreinte, poids inverse (référence v9)', 'resultats_v9/dl_film/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : empreinte, gènes règles, poids inverse', 'resultats_v9/ablations/dl_film_regles_inverse/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : empreinte, tous gènes, poids racine', 'resultats_v9/ablations/dl_film_tous_racine/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : empreinte, gènes règles, poids racine', 'resultats_v9/ablations/dl_film_regles_racine/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : empreinte, tous gènes, sans poids', 'resultats_v9/ablations/dl_film_tous_aucun/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : empreinte, gènes règles, sans poids', 'resultats_v9/ablations/dl_film_regles_aucun/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : empreinte, racine, EVITER x2', 'resultats_v9/phase2/dl_film_racine_evit2/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : empreinte, racine, EVITER x4', 'resultats_v9/phase2/dl_film_racine_evit4/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : empreinte, racine, EVITER x8', 'resultats_v9/phase2/dl_film_racine_evit8/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : identifiant, racine', 'resultats_v9/phase2/dl_film_racine_id/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : identifiant, racine, EVITER x2', 'resultats_v9/phase2b/dl_film_racine_id_evit2/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : empreinte+identifiant, racine', 'resultats_v9/phase2b/dl_film_racine_hybride/dl_v7_film_resultats_par_pli.csv'),
     ('DL film : empreinte+identifiant, racine, EVITER x2', 'resultats_v9/phase2b/dl_film_racine_hybride_evit2/dl_v7_film_resultats_par_pli.csv')]
cols = ['f1_macro', 'f1_hors_surveiller', 'exactitude', 'CER_strict', 'precision_EVITER', 'rappel_EVITER', 'rappel_STANDARD', 'rappel_SURVEILLER', 'logloss', 'ECE']
rows = []
for nom, f in C:
    d = pd.read_csv(f); r = {'configuration': nom, 'plis': len(d)}
    for c in cols:
        if c in d.columns: r[c] = round(float(d[c].mean()), 4); r[c + '_std'] = round(float(d[c].std(ddof=0)), 4)
    rows.append(r)
T = pd.DataFrame(rows); T.to_csv('resultats_v9/RESUME_phase1_phase2_v9.csv', index=False)
pd.set_option('display.width', 250); print(T[['configuration', 'f1_macro', 'CER_strict', 'precision_EVITER', 'logloss', 'ECE']].to_string(index=False))
