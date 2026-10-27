#!/usr/bin/env python3
"""Écran automatique règle <-> texte de recommandation (27 oct. 2026). NE CLASSE RIEN : il SIGNALE les règles dont l'action semble en désaccord avec leur texte ; chaque règle signalée a été LUE à la main (voir AUDIT_REGLES_ECRAN_TEXTE_27oct2026.md).
Usage : python3 ecran_texte_regles.py ../../data/regles_v9_monogene.csv ../../data/regles_v9_multigene.csv"""
import re, sys, pandas as pd
ev=re.compile(r"avoid|do not use|contraindicat|not recommended|alternative|éviter|contre-indiqu|ne pas|déconseill|pas recommand",re.I)
ad=re.compile(r"reduc|lower|decreas|increas|dose|titrat|adjust|dosage|réduire|diminuer|augment|adapter|posologie|mg",re.I)
st=re.compile(r"standard|no change|normal dose|label|no recommendation|aucune|pas de raison|no action|usual|routine|regular",re.I)
for f in sys.argv[1:]:
    d=pd.read_csv(f); n=0
    for _,r in d.iterrows():
        t=str(r.recommandation); a=r.action; e=bool(ev.search(t)); dd=bool(ad.search(t)); s=bool(st.search(t)); fl=None
        if t.startswith('API CPIC'): continue
        if a=='STANDARD' and (e or (dd and not s)): fl='STANDARD mais mot evitement/dose'
        elif a=='EVITER' and not e: fl='EVITER sans mot evitement'
        elif a=='ADAPTER_DOSE' and not dd: fl='ADAPTER sans mot dose'
        elif a=='SURVEILLER': fl='SURVEILLER a lire'
        if fl: n+=1; print(fl,'|',r.medicament,'|',t[:160])
    print(f,':',n,'signalées sur',len(d))
