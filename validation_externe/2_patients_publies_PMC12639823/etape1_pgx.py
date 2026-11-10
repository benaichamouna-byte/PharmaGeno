import sys, json; sys.path.insert(0,'.')
from patients_S3 import PAT
import pypgx.api.core as c
out={}
for p,d in PAT.items():
    for g,v in d.items():
        if g in ('CYP2C19','CYP3A5','CYP2B6','UGT1A1') and isinstance(v,str):
            a,b=v.split('/'); out['%s|%s'%(g,v)]=c.predict_phenotype(g,a,b)
json.dump(out,open('phen_pypgx.json','w'),indent=1); print(out)
