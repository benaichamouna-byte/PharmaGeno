import joblib, pickle, torch, torch.nn as nn
import numpy as np, warnings
warnings.filterwarnings('ignore')

RESULTS_DIR = '/home/mouna/projet_memoire/model_v2/results'
ACTION_ICONS  = {'EVITER':'⛔','ADAPTER_DOSE':'⚠️','SURVEILLER':'👁️','STANDARD':'✅'}
ACTION_LABELS = {'EVITER':'À éviter — risque élevé','ADAPTER_DOSE':'Adapter la dose','SURVEILLER':'Surveillance renforcée','STANDARD':'Dose standard applicable'}
ACTION_COLORS = {'EVITER':'danger','ADAPTER_DOSE':'warning','SURVEILLER':'info','STANDARD':'success'}
GENO_TO_PHENO = {'0/0':1.0,'0|0':1.0,'0/1':0.5,'1/0':0.5,'0|1':0.5,'1|0':0.5,'1/1':0.0,'1|1':0.0}

_rf=_dl=_le=_GENES=_scaler=_drug_fp=_n_genes=_n_drug_fp=None

class GeneAttention(nn.Module):
    def __init__(self,n):
        super().__init__()
        self.attn=nn.Linear(n,n)
    def forward(self,x):
        return x*torch.softmax(self.attn(x),dim=1)

class PharmDL_v3(nn.Module):
    def __init__(self,ng,nd,no):
        super().__init__()
        self.gene_attention=GeneAttention(ng)
        self.gene_branch=nn.Sequential(nn.Linear(ng,64),nn.BatchNorm1d(64),nn.ReLU(),nn.Dropout(0.3),nn.Linear(64,32),nn.BatchNorm1d(32),nn.ReLU())
        self.drug_branch=nn.Sequential(nn.Linear(nd,256),nn.BatchNorm1d(256),nn.ReLU(),nn.Dropout(0.4),nn.Linear(256,128),nn.BatchNorm1d(128),nn.ReLU(),nn.Dropout(0.3),nn.Linear(128,64),nn.ReLU())
        self.combined=nn.Sequential(nn.Linear(96,64),nn.BatchNorm1d(64),nn.ReLU(),nn.Dropout(0.3),nn.Linear(64,32),nn.ReLU(),nn.Linear(32,no))
    def forward(self,x):
        g=self.gene_branch(self.gene_attention(x[:,:_n_genes]))
        d=self.drug_branch(x[:,_n_genes:])
        return self.combined(torch.cat([g,d],dim=1))

def load_models_v2():
    global _rf,_dl,_le,_GENES,_scaler,_drug_fp,_n_genes,_n_drug_fp
    _rf=joblib.load(RESULTS_DIR+'/rf_pgx_final.pkl')
    with open(RESULTS_DIR+'/le_pgx.pkl','rb') as f: _le=pickle.load(f)
    with open(RESULTS_DIR+'/genes_pgx.pkl','rb') as f: _GENES=pickle.load(f)
    with open(RESULTS_DIR+'/scaler_pgx.pkl','rb') as f: _scaler=pickle.load(f)
    with open(RESULTS_DIR+'/drug_fp_ref.pkl','rb') as f: _drug_fp=pickle.load(f)
    _n_genes=len(_GENES); _n_drug_fp=518
    _dl=PharmDL_v3(_n_genes,_n_drug_fp,len(_le.classes_))
    _dl.load_state_dict(torch.load(RESULTS_DIR+'/dl_pgx_final.pth',map_location='cpu'))
    _dl.eval()
    print('[predict_v2] OK — '+str(len(_GENES))+' genes, '+str(len(_drug_fp))+' medicaments')

def predict_action(gene,drug,genotype):
    gene_val=GENO_TO_PHENO.get(str(genotype).strip(),0.5)
    gv=np.ones(_n_genes)
    if gene in _GENES: gv[_GENES.index(gene)]=gene_val
    dl=str(drug).lower().strip()
    if dl not in _drug_fp:
        return {'action':'SURVEILLER','confidence':0.0,'icon':ACTION_ICONS['SURVEILLER'],'label':ACTION_LABELS['SURVEILLER'],'color':ACTION_COLORS['SURVEILLER'],'known_drug':False}
    fp=_scaler.transform(_drug_fp[dl].reshape(1,-1))
    X=np.hstack([gv,fp[0]]).reshape(1,-1).astype(float)
    with torch.no_grad():
        probs_dl=torch.softmax(_dl(torch.FloatTensor(X)),dim=1).numpy()[0]
    probs_rf=_rf.predict_proba(X)[0]
    ens=(2.0*probs_dl+1.0*probs_rf)/3.0
    y=np.argmax(ens); action=_le.inverse_transform([y])[0]
    return {'action':action,'confidence':round(float(ens[y])*100,1),'icon':ACTION_ICONS.get(action,''),'label':ACTION_LABELS.get(action,action),'color':ACTION_COLORS.get(action,'secondary'),'known_drug':True}

def predict_for_variant(gene,rsid,genotype,drug_list):
    drugs=[d for d in drug_list if d and d!='Aucune recommandation trouvée'][:10]
    if not drugs: drugs=list(_drug_fp.keys())[:5]
    results=[]
    for drug in drugs:
        p=predict_action(gene,drug,genotype)
        p.update({'gene':gene,'rsid':rsid,'genotype':genotype,'drug':drug})
        results.append(p)
    results.sort(key=lambda x:['EVITER','ADAPTER_DOSE','SURVEILLER','STANDARD'].index(x['action']) if x['action'] in ['EVITER','ADAPTER_DOSE','SURVEILLER','STANDARD'] else 4)
    return results


def build_patient_profile(variants_list):
    gene_vector = [1.0] * _n_genes
    for v in variants_list:
        gene = v.get('gene','')
        genotype = v.get('genotype','0/0')
        if gene in _GENES:
            gene_val = GENO_TO_PHENO.get(str(genotype).strip(), 0.5)
            idx = _GENES.index(gene)
            if gene_val < gene_vector[idx]:
                gene_vector[idx] = gene_val
    return gene_vector

GENE_DRUGS = {
    'CYP2C19': ['clopidogrel','omeprazole','citalopram','sertraline','voriconazole','esomeprazole','lansoprazole','pantoprazole','escitalopram','amitriptyline','clomipramine','imipramine'],
    'CYP2D6':  ['codeine','tramadol','tamoxifen','risperidone','amitriptyline','fluoxetine','paroxetine','atomoxetine','metoprolol','propafenone','haloperidol','clomipramine'],
    'CYP2C9':  ['warfarin','ibuprofen','celecoxib','phenytoin','flurbiprofen','piroxicam','losartan'],
    'CYP2B6':  ['efavirenz','methadone','bupropion','cyclophosphamide','nevirapine'],
    'DPYD':    ['fluorouracil','capecitabine','tegafur'],
    'TPMT':    ['azathioprine','mercaptopurine','thioguanine'],
    'NUDT15':  ['azathioprine','mercaptopurine','thioguanine'],
    'SLCO1B1': ['simvastatin','atorvastatin','rosuvastatin','pravastatin'],
    'UGT1A1':  ['irinotecan','atazanavir','belinostat'],
    'VKORC1':  ['warfarin','acenocoumarol','phenprocoumon'],
    'G6PD':    ['rasburicase','primaquine','dapsone'],
    'HLA-B':   ['abacavir','carbamazepine','allopurinol','oxcarbazepine'],
    'HLA-A':   ['abacavir','carbamazepine'],
    'RYR1':    ['desflurane','sevoflurane','isoflurane','succinylcholine'],
    'CYP3A5':  ['tacrolimus','cyclosporine','sirolimus'],
    'CYP4F2':  ['warfarin','vitamin k'],
    'CYP2A6':  ['nicotine','efavirenz','valproic acid'],
    'CYP1A2':  ['clozapine','caffeine','theophylline','olanzapine'],
    'NAT2':    ['isoniazid','hydralazine','sulfamethoxazole'],
    'ABCG2':   ['allopurinol','rosuvastatin','atorvastatin'],
    'CYP3A4':  ['tacrolimus','midazolam','simvastatin','atorvastatin'],
}

PHENO_EXPLAIN = {
    0.0: 'Poor Metabolizer — enzyme inactive ou très réduite',
    0.5: 'Intermediate Metabolizer — enzyme partiellement active',
    1.0: 'Normal Metabolizer — enzyme normale',
    1.5: 'Rapid Metabolizer — enzyme plus active que la normale',
    2.0: 'Ultrarapid Metabolizer — enzyme très active',
}

def predict_for_patient(variants_list, extra_drugs=None):
    gene_vector = build_patient_profile(variants_list)
    mutated_genes = []
    for v in variants_list:
        gene = v.get('gene','')
        if gene in _GENES:
            idx = _GENES.index(gene)
            if gene_vector[idx] < 1.0:
                mutated_genes.append(gene)
    drugs_to_check = set()
    for gene in mutated_genes:
        for drug in GENE_DRUGS.get(gene, []):
            drugs_to_check.add(drug)
    if extra_drugs:
        for d in extra_drugs:
            if d and d != 'Aucune recommandation trouvee':
                drugs_to_check.add(d.lower().strip())
    results = []
    for drug in drugs_to_check:
        dl = str(drug).lower().strip()
        if dl not in _drug_fp:
            continue
        fp = _scaler.transform(_drug_fp[dl].reshape(1,-1))
        X = np.hstack([gene_vector, fp[0]]).reshape(1,-1).astype(float)
        with torch.no_grad():
            probs_dl = torch.softmax(_dl(torch.FloatTensor(X)),dim=1).numpy()[0]
        probs_rf = _rf.predict_proba(X)[0]
        ens = (2.0*probs_dl + 1.0*probs_rf) / 3.0
        y = np.argmax(ens)
        action = _le.inverse_transform([y])[0]
        responsible_genes = [g for g in mutated_genes if drug in GENE_DRUGS.get(g,[])]
        gene_val = gene_vector[_GENES.index(responsible_genes[0])] if responsible_genes else 1.0
        results.append({
            'drug':             drug,
            'action':           action,
            'confidence':       round(float(ens[y])*100, 1),
            'icon':             ACTION_ICONS.get(action,''),
            'label':            ACTION_LABELS.get(action, action),
            'color':            ACTION_COLORS.get(action,'secondary'),
            'known_drug':       True,
            'responsible_gene': ', '.join(responsible_genes) if responsible_genes else 'N/A',
            'phenotype_explain': PHENO_EXPLAIN.get(gene_val, 'Metabolisme inconnu'),
            'probabilities':    {_le.classes_[i]: round(float(ens[i])*100,1) for i in range(len(_le.classes_))},
        })
    results.sort(key=lambda x: ['EVITER','ADAPTER_DOSE','SURVEILLER','STANDARD'].index(x['action']) if x['action'] in ['EVITER','ADAPTER_DOSE','SURVEILLER','STANDARD'] else 4)
    return results, mutated_genes, gene_vector
