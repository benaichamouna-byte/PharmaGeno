#!/usr/bin/env python3
"""
figures_chapitre6_v15.py — produit les figures 6.1 et 6.2 du chapitre 6 (corpus v15).

Toutes les valeurs sont recopiees des sorties mesurees :
  - figure 6.1 : analyse de couverture-risque v15 (couverture_risque_v2.py), bras c35,
                 prédictions hors pli calibrees, moyenne des 5 graines, 211 177 lignes.
  - figure 6.2 : comparaison equitable v15, statistique principale « moyenne des graines »,
                 IC 95 % bootstrap sur les 1 241 identifiants de profil (2 000 tirages).
Aucune valeur n'est calculee ici : ce script ne fait que dessiner.
Sortie : fig_6_1.png et fig_6_2.png, 300 dpi, sans couleur de fond.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np, sys, os

def fr(x, n=1):
    """Nombre au format francais : virgule decimale, espace fine pour les milliers."""
    t = ('%.*f' % (n, x)).replace('.', ',')
    e, _, d = t.partition(',')
    if len(e) > 3: e = e[:-3] + '\u202f' + e[-3:]
    return e + (',' + d if d else '')

VIRGULE = FuncFormatter(lambda v, _: ('%g' % v).replace('.', ','))
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({'font.size': 10, 'font.family': 'DejaVu Sans',
                     'axes.spines.top': False, 'axes.spines.right': False})

# ---------------------------------------------------------------- figure 6.1
seuils   = [0.70, 0.90, 0.95, 0.99, 0.9965]
etiq     = ['0,70', '0,90', '0,95', '0,99', '0,9965']
erreurs  = [75.4, 49.6, 42.2, 32.0, 28.6]
eviter   = [38.4, 32.0, 29.2, 25.2, 23.6]
ecartees = [59.2, 170.4, 269.8, 669.4, 1180.6]
TOT_ERR, TOT_EV, N = 103.2, 47.4, 211177

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.1))
x = np.arange(len(seuils)); w = 0.38
a1.bar(x - w/2, erreurs, w, label='Erreurs restantes', color='#4a6fa5', edgecolor='white')
a1.bar(x + w/2, eviter,  w, label='EVITER manqués acceptés', color='#b5651d', edgecolor='white')
a1.axhline(TOT_ERR, ls='--', lw=1, color='#4a6fa5')
a1.axhline(TOT_EV,  ls=':',  lw=1, color='#b5651d')
a1.text(len(seuils)-0.45, TOT_ERR+1.5, 'sans abstention : ' + fr(TOT_ERR),
        color='#4a6fa5', fontsize=8, ha='right')
a1.text(len(seuils)-0.45, TOT_EV+1.5, 'sans abstention : ' + fr(TOT_EV),
        color='#b5651d', fontsize=8, ha='right')
for i, (e, v) in enumerate(zip(erreurs, eviter)):
    a1.text(i - w/2, e + 1, fr(e), ha='center', fontsize=8)
    a1.text(i + w/2, v + 1, fr(v), ha='center', fontsize=8)
a1.set_xticks(x); a1.set_xticklabels(etiq)
a1.set_xlabel('Seuil de confiance'); a1.set_ylabel("Nombre de lignes (moyenne de 5 graines)")
a1.set_ylim(0, TOT_ERR * 1.22); a1.legend(frameon=False, fontsize=9, loc='upper right')
a1.set_title("(a) Erreurs non écartées par l'abstention", fontsize=10, loc='left')

part_err = [e / TOT_ERR * 100 for e in erreurs]
part_ev   = [v / TOT_EV  * 100 for v in eviter]
a2.plot(x, part_err, 'o-', color='#4a6fa5', label='Part des erreurs restantes')
a2.plot(x, part_ev,  's-', color='#b5651d', label='Part des EVITER manqués restants')
for i in range(len(x)):
    a2.text(x[i], part_err[i] - 4.5, fr(part_err[i], 0) + ' %', ha='center', fontsize=8, color='#4a6fa5')
    a2.text(x[i], part_ev[i] + 2.5, fr(part_ev[i], 0) + ' %', ha='center', fontsize=8, color='#b5651d')
a2.set_xticks(x)
a2.set_xticklabels(['%s\n(%s %% écartées)' % (etiq[i], fr(ecartees[i] / N * 100, 2))
                    for i in range(len(x))], fontsize=8)
a2.set_xlabel('Seuil de confiance'); a2.set_ylabel("Part restante de chaque type d'erreur (%)")
a2.yaxis.set_major_formatter(VIRGULE)
a2.set_ylim(0, 105); a2.legend(frameon=False, fontsize=9, loc='lower left')
a2.set_title("(b) Les EVITER manqués résistent plus à l'abstention", fontsize=10, loc='left')
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_6_1.png'), dpi=300, facecolor='white')
plt.close(fig)

# ---------------------------------------------------------------- figure 6.2
noms = ['Réseau\n(recherche\nimbriquée)', 'XGBoost', 'Random\nForest',
        'Réseau\nconfiguration 35\n(application)']
f1   = [0.997943, 0.998288, 0.992687, 0.998197]
lo   = [0.997316, 0.997676, 0.990923, 0.997651]
hi   = [0.998484, 0.998828, 0.994187, 0.998674]
taux = [0.72, 0.19, 1.50, 0.66]
coul = ['#4a6fa5', '#6a8f3c', '#9a9a9a', '#2f4b78']

fig, (b1, b2) = plt.subplots(1, 2, figsize=(11, 4.3))
y = np.arange(len(noms))
err = [[f1[i] - lo[i] for i in range(4)], [hi[i] - f1[i] for i in range(4)]]
b1.barh(y, f1, 0.55, xerr=err, color=coul, edgecolor='white',
        error_kw=dict(ecolor='#333333', capsize=4, lw=1.1))
for i in range(4):
    b1.text(hi[i] + 0.00025, y[i], fr(f1[i], 5), va='center', fontsize=8.5)
b1.set_yticks(y); b1.set_yticklabels(noms, fontsize=8.5); b1.invert_yaxis()
b1.xaxis.set_major_formatter(VIRGULE)
b1.set_xlim(0.9900, 0.99955); b1.set_xlabel('F1 macro (IC 95 % bootstrap sur les profils)')
b1.set_title('(a) Accord avec les règles', fontsize=10, loc='left')

b2.barh(y, taux, 0.55, color=coul, edgecolor='white')
for i in range(4):
    b2.text(taux[i] + 0.03, y[i], fr(taux[i], 2) + ' %', va='center', fontsize=8.5)
b2.set_yticks(y); b2.set_yticklabels([]); b2.invert_yaxis()
b2.xaxis.set_major_formatter(VIRGULE)
b2.set_xlim(0, 1.75); b2.set_xlabel("Taux d'EVITER manqués (sur 7\u202f215 lignes EVITER)")
b2.set_title('(b) Critère de sécurité', fontsize=10, loc='left')
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_6_2.png'), dpi=300, facecolor='white')
plt.close(fig)
print('fig_6_1.png et fig_6_2.png ecrits dans', os.path.abspath(OUT))
