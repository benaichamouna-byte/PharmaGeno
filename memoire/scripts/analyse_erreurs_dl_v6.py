#!/usr/bin/env python3
"""
analyse_erreurs_dl_v6.py : analyse des erreurs du DL (prédictions hors-pli de train_dl_v6.py). Lecture seule.
Usage : python3 analyse_erreurs_dl_v6.py dl_v6_oof.npz phenotype_drug_dataset_v3_croise.csv regles_v2_monogene.csv
Sortie : texte affiché (matrice de confusion, erreurs par médicament, EVITER manqués, calibration, détail de 5 médicaments).
"""
import sys
NPZ, CSV, MONO = sys.argv[1:4]
import numpy as np, pandas as pd
from sklearn.metrics import f1_score, confusion_matrix, recall_score, precision_score
z=np.load(NPZ,allow_pickle=True)
P=z['proba'];y=z['y'];pli=z['pli'];drug=z['drug']
df=pd.read_csv(CSV)
assert (df.drug.values==drug).all()
cl=['ADAPTER_DOSE','EVITER','STANDARD','SURVEILLER']
assert (np.array(cl)[y]==df.action.values).all()
pred=P.argmax(1)
print('F1 oof',f1_score(y,pred,average='macro'),'acc',(pred==y).mean())
print(pd.DataFrame(confusion_matrix(y,pred),index=cl,columns=cl))
print('precision',dict(zip(cl,precision_score(y,pred,average=None).round(4))),'recall',dict(zip(cl,recall_score(y,pred,average=None).round(4))))
m=y!=3
print('F1 3 classes (hors SURVEILLER)',f1_score(y[m],pred[m],average=None,labels=[0,1,2]).mean(), 'F1 par classe',f1_score(y,pred,average=None).round(4))
df['pred']=np.array(cl)[pred]; df['ok']=pred==y; df['pli']=pli
# erreurs par medicament
g=df.groupby('drug').agg(n=('ok','size'),acc=('ok','mean'),n_ev=('action',lambda s:(s=='EVITER').sum()))
g['err']=(1-g.acc)*g.n
ev=df[df.action=='EVITER'].groupby('drug').ok.agg(['size','mean']); ev.columns=['n_ev','rappel_ev']
print('\n10 medicaments avec le plus d erreurs'); print(g.sort_values('err',ascending=False).head(12).round(3))
print('\nEVITER manques par medicament'); e=ev.assign(manques=(ev.n_ev*(1-ev.rappel_ev)).round()); print(e[e.manques>0].sort_values('manques',ascending=False).head(12).round(3))
print('total EVITER manques',int(e.manques.sum()),'/',int(e.n_ev.sum()))
# pli 3
print('\nPli 3 EVITER manques par medicament'); d3=df[(df.pli==2)&(df.action=='EVITER')]
print(d3.groupby('drug').ok.agg(['size','mean']).assign(m=lambda t:(t['size']*(1-t['mean'])).round()).query('m>0').sort_values('m',ascending=False).head(10))
print('\nconfiance:',df.groupby('confiance').ok.mean().round(4).to_dict(), df.confiance.value_counts().to_dict())
print('nb regles:',df.groupby('nb_regles_appliquees').ok.agg(['size','mean']).round(4).to_dict('index'))
# erreurs: STANDARD predit autre
s=df[df.action=='STANDARD']; print('\nSTANDARD -> autre :',s.pred.value_counts().to_dict())
print('STANDARD mal classes par medicament (top)'); print(s.groupby('drug').ok.agg(['size','mean']).assign(m=lambda t:(t['size']*(1-t['mean'])).round()).sort_values('m',ascending=False).head(10).round(3))
# par pli: erreurs par ligne gene
print('\npar pli (idx 0-based dans pli) acc:',df.groupby('pli').ok.mean().round(4).to_dict())
# calibration
conf=P.max(1);ok=(pred==y)
for lo,hi in [(0,.5),(.5,.7),(.7,.9),(.9,.99),(.99,1.01)]:
    mm=(conf>=lo)&(conf<hi); print(f'conf [{lo},{hi}) n={mm.sum()} acc={ok[mm].mean():.3f} conf_moy={conf[mm].mean():.3f}')
# erreurs par nombre de genes non normaux
G=['ABCG2','CYP2B6','CYP2C19','CYP2C9','CYP2D6','CYP3A5','DPYD','F5','NUDT15','SLCO1B1','TPMT','UGT1A1']
df['nnn']=(df[G]!=1.0).sum(axis=1); print('\nacc par nb genes non normaux:',df.groupby('nnn').ok.agg(['size','mean']).round(3).to_dict('index'))
# profils uniques dans erreurs
print('profils par famille: n familles',df.family_id.nunique())


# ---- detail de 5 medicaments ----
import numpy as np, pandas as pd
z=np.load(NPZ,allow_pickle=True)
cl=np.array(['ADAPTER_DOSE','EVITER','STANDARD','SURVEILLER'])
df=pd.read_csv(CSV); df['pred']=cl[z['proba'].argmax(1)]
mono=pd.read_csv(MONO); mono['medicament']=mono.medicament.str.lower()
for d,gn in [('tacrolimus','CYP3A5'),('efavirenz','CYP2B6'),('atazanavir','UGT1A1'),('irinotecan','UGT1A1'),('atorvastatin','SLCO1B1')]:
    s=df[df.drug==d]
    print('\n==',d,gn, 'regles utilisables:'); 
    r=mono[(mono.medicament==d)&(mono.gene==gn)][['valeur','action','ambigu','conditionnel']]; print(r.to_string(index=False))
    t=s.groupby([gn,'action','pred']).size().rename('n').reset_index(); print(t.to_string(index=False))
# ensemble des genes dont les valeurs sont rares
G=['ABCG2','CYP2B6','CYP2C19','CYP2C9','CYP2D6','CYP3A5','DPYD','F5','NUDT15','SLCO1B1','TPMT','UGT1A1']
for g in ['CYP3A5','CYP2B6','UGT1A1','SLCO1B1']:
    print(g, df.drop_duplicates('sample_id')[g].value_counts().sort_index().to_dict())
