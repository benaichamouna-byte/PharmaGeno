#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""filtrer_corpus_sans34_v1.py (15 nov. 2026) : retire du corpus v15 les lignes des 34 profils de
développement apparentés à un profil de l'ensemble final (règle du 5 nov. 2026, liste recalculée par
audit_parente_recalcul_v1.py). Entrée 68b564ce265728b6 -> sortie a2e9ce9450d44b9f
(5 821 lignes retirées, 228 811 gardées, 1 345 profils restants ; réécrit par le module csv)."""
import csv, sys
A34 = set(l.strip() for l in open(sys.argv[1]) if l.strip() and l.strip() != "profil_developpement")
assert len(A34) == 34
with open(sys.argv[2], newline="") as f, open(sys.argv[3], "w", newline="") as g:
    r = csv.reader(f); w = csv.writer(g)
    head = next(r); w.writerow(head); i = head.index("sample_id")
    for row in r:
        if row[i] not in A34: w.writerow(row)
