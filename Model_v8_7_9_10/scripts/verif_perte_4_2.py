#!/usr/bin/env python3
"""verif_perte_4_2.py (7 nov. 2026) : compare nn.CrossEntropyLoss(weight, ignore_index=-1, label_smoothing) à la formule (4.2) du mémoire.
Aucune donnée du projet, aucun fichier lu ou écrit. Données tirées au hasard (graine fixe)."""
import numpy as np, torch, torch.nn as nn
print('torch', torch.__version__)
K, eps = 4, 0.05
for dtype, tol in ((torch.float64, 1e-10), (torch.float32, 1e-6)):
    for graine in range(5):
        g = np.random.RandomState(graine); N = 4000
        z = torch.tensor(g.randn(N, K) * 3, dtype=dtype); y = g.randint(0, K, N); y[g.rand(N) < 0.2] = -1          # 20 % de cases sans étiquette
        w = torch.tensor(g.uniform(0.2, 5, K), dtype=dtype)
        ref = nn.CrossEntropyLoss(weight=w, ignore_index=-1, label_smoothing=eps)(z, torch.tensor(y))
        m = y >= 0; lp = torch.log_softmax(z[m], 1); yy = torch.tensor(y[m]); wy = w[yy]
        formule = ((-(1 - eps) * wy * lp[torch.arange(len(yy)), yy] - (eps / K) * (w[None, :] * lp).sum(1)).sum()) / wy.sum()
        d = abs(float(ref) - float(formule)); print(str(dtype).split('.')[-1], 'graine', graine, 'PyTorch %.9f' % float(ref), 'formule %.9f' % float(formule), 'écart %.2e' % d, 'OK' if d < tol else 'ÉCART TROP GRAND')
