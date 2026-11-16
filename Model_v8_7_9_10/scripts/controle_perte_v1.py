"""Contrôle : la perte de PyTorch (CrossEntropyLoss avec poids de classes et lissage d'étiquettes, réduction moyenne)
est-elle égale à la formule (4.2) du chapitre 4 ? Lot d'essai aléatoire, graine 0."""
import torch
torch.manual_seed(0)
K, n, eps, alpha = 4, 512, 0.05, 0.5
z = torch.randn(n, K, dtype=torch.float64) * 3
y = torch.randint(0, K, (n,))
nc = torch.tensor([181262., 18188., 7215., 4512.], dtype=torch.float64)  # effectifs des classes (développement v15)
w = (nc.sum() / (K * nc)) ** alpha
L_torch = torch.nn.CrossEntropyLoss(weight=w, label_smoothing=eps)(z, y)
logp = torch.log_softmax(z, 1)
num = (-(1 - eps) * w[y] * logp[torch.arange(n), y] - (eps / K) * (w * logp).sum(1)).sum()
L_formule = num / w[y].sum()
print('torch', torch.__version__, '| perte PyTorch %.15f | formule 4.2 %.15f | ecart %.3e' % (L_torch.item(), L_formule.item(), abs(L_torch - L_formule).item()))
