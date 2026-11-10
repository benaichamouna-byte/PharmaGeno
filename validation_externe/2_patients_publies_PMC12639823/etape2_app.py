import sys, os, json
APP='/home/claude/appdev/Model_v8_7_9_10'; sys.path.insert(0, APP+'/scripts'); sys.path.insert(0,'.')
import vcf_to_profile_v9 as L
from moteur_v10j import MoteurPGxChoix
from patients_S3 import PAT, ART_PHEN
D=APP+'/data'; ph=json.load(open('phen_pypgx.json'))
tables,_=L.charger_tables(D+'/tables_cpic_v8.json'); codage=L.charger_codage(D+'/codage_pypgx_valeur_v7.csv')
mo=MoteurPGxChoix(APP+'/modeles_v10',APP+'/modeles_v10',D+'/domaine_v10.json',D+'/regles_v14_monogene.csv',D+'/regles_v13_multigene.csv',dossier_xgb=APP+'/modeles_v10x',dossier_rf=APP+'/modeles_v10rf')
SORTIE={}
for p,d in PAT.items():
    prof={g:None for g in mo.genes_modele}; lect={}
    for g,v in d.items():
        if g=='HLAB58': prof['HLA-B*58:01']=0.0 if v[1]=='non_porteur' else 1.0; lect[g]='saisi : '+v[1]; continue
        if g=='HLAA3101': prof['HLA-A*31:01']=1.0 if v[1]=='porteur' else 0.0; lect[g]='saisi : '+v[1]; continue
        if isinstance(v,tuple): prof[g]=v[1]; lect[g]='saisi : %s'%v[1]; continue
        if g=='VKORC1': geno={'AA':'rs9923231/rs9923231','GA':'Reference/rs9923231','GG':'Reference/Reference'}[v]; phen=None
        else: geno=v; phen=ph.get('%s|%s'%(g,v))
        val,motif,pu=L.coder_gene(g,geno,phen,tables,codage)
        prof[g]=val; lect[g]='%s -> %s (%s)%s'%(v,val,pu,'' if motif is None else ' MOTIF: '+motif)
    res=mo.predire(prof)
    SORTIE[p]=dict(profil={g:v for g,v in prof.items() if v is not None},lecture=lect,res=[{k:r.get(k) for k in ('medicament','statut','action_cpic','action_dl','proba_dl','regle_cpic','genes_manquants','alertes')} for r in res])
json.dump(SORTIE,open('sortie_app_S3.json','w'),indent=1,ensure_ascii=False,default=str)
for p in SORTIE: print(p,SORTIE[p]['lecture'])
