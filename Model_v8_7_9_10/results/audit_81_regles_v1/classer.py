import pandas as pd, json, re
G='../guide_json/'
m=pd.read_csv('out_complet/regles_v2_monogene.csv'); x=pd.read_csv('out_complet/regles_v2_multigene.csv')
a=m[m.ambigu].copy(); b=x[x.ambigu].copy()
def nett(s): return re.sub(r'\s*Classification of recommendation.*','',s)
def liens(f):
    j=json.load(open(G+f))['guideline']
    L=[l.get('_sameAs') for l in j.get('literature',[]) if l.get('_sameAs')]
    pid=f.replace('.json','')
    return f"ClinPGx/PharmGKB {pid} (https://www.clinpgx.org/guidelineAnnotation/{pid}) ; " + ' ; '.join(L[:2])
# types
T1='1_EVITER_d_abord'          # le texte commence par éviter / choisir une alternative; dose réduite seulement si impossible
T2='2_DOSE_d_abord'            # le texte commence par une dose adaptée; l'alternative n'est qu'un recours
T3='3_deux_options_au_choix'   # "dose réduite OU alternative", sur un pied d'égalité
T4='4_depend_autre_chose'      # dépend de la co-médication ou de l'indication
T5='5_depend_score_activite'   # dépend du score d'activité non codé (1 ou 1,5)
T6='6_standard_d_abord'        # traitement standard; alternative seulement si échec
def typ_mono(r):
    med,g,v=r.medicament,r.gene,r.valeur
    tca={'amitriptyline','clomipramine','desipramine','doxepin','imipramine','nortriptyline','trimipramine'}
    if med in tca: return T1
    if g=='NUDT15' or (g=='DPYD'): return T1
    if g=='TPMT': return T3
    if med=='voriconazole' or med=='lovastatin': return T1
    if med in {'citalopram','escitalopram'}: return T6 if v==1.5 else T1
    if med=='vortioxetine': return T1 if v==2.0 else T3
    if med in {'celecoxib','flurbiprofen','ibuprofen','lornoxicam'}: return T2
    if med in {'fluvastatin','pitavastatin','pravastatin','metoprolol'}: return T2
    if med in {'fluvoxamine','sertraline','haloperidol','risperidone'}: return T3
    if med in {'quetiapine','mavacamten'}: return T4
    if med in {'meloxicam','piroxicam','tenoxicam'}: return T5
    return '?'
def typ_multi(r):
    if r.medicament=='amitriptyline': return T1
    if r.medicament in {'fluvastatin','rosuvastatin'}: return T2
    if r.medicament=='sertraline':
        return T6 if (r.valeur_a>=1.5 and r.valeur_b>=1.5) else T3
a['type']=a.apply(typ_mono,axis=1); b['type']=b.apply(typ_multi,axis=1)
prop={T1:'EVITER',T2:'ADAPTER_DOSE',T3:'A DECIDER (voir note)',T4:'EXCLURE (non décidable par le génotype seul)',T5:'A DECIDER (voir note)',T6:'STANDARD'}
for d in (a,b):
    d['proposition']=d.type.map(prop); d['texte_complet']=d.recommandation.map(nett); d['liens']=d.fichier.map(liens)
a['regle']=a.apply(lambda r:f"{r.medicament} | {r.gene}={r.valeur}",axis=1)
b['regle']=b.apply(lambda r:f"{r.medicament} | {r.gene_a}={r.valeur_a} x {r.gene_b}={r.valeur_b}",axis=1)
out=pd.concat([a.assign(nature='mono-gene')[['nature','regle','source','type','proposition','texte_complet','liens']],
               b.assign(nature='multi-gene')[['nature','regle','source','type','proposition','texte_complet','liens']]])
out.to_csv('audit_81_regles_texte_complet.csv',index=False)
print(out.groupby(['nature','type']).size().unstack(0).fillna(0).astype(int)); print(len(out), (out.type=='?').sum())
