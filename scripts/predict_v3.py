"""
predict_v3.py — Moteur d inference de PharmaGeno

Remplace predict_v2.py. Aucun fichier existant n est modifie.

QUATRE CORRECTIONS PAR RAPPORT A predict_v2.py
-----------------------------------------------

1. MODELE ET EMPREINTES CHOISIS ENSEMBLE
   Les modeles _neg ont ete entraines avec drug_fingerprints.pkl, dont les 512 bits de
   Morgan sont nuls. Les modeles _fp le sont avec drug_fingerprints_v2.pkl, empreintes
   recalculees (437/437 medicaments, 42,9 bits actifs en moyenne). Fournir a un modele
   des empreintes autres que celles de son entrainement produit des predictions
   depourvues de sens. La variable VERSION ci-dessous choisit les deux ensemble.

2. NORMALISATION CONFORME A L ENTRAINEMENT
   A l entrainement, rf.fit(X, y) et xgb.fit(X, y) recoivent les variables brutes ;
   seule la fonction entrainer_dl applique un StandardScaler, et uniquement sur les
   518 colonnes du medicament. predict_v2.py donnait le vecteur normalise aux trois
   modeles : Random Forest recevait donc des entrees qu il n avait jamais vues.

3. PROFIL COMPLET DU PATIENT
   predict_action construisait un vecteur de 1.0 sur les 31 genes et n en renseignait
   qu un seul : quel que soit le profil reel, le modele voyait un patient normal sur
   trente genes. Toutes les fonctions de ce fichier utilisent le profil complet.

4. PLUS DE FILTRE MANUEL SUR LES MEDICAMENTS
   predict_for_patient ecartait tout medicament absent du dictionnaire GENE_DRUGS
   (ligne « if not responsible: continue »). Le modele voit desormais l integralite du
   referentiel moleculaire. GENE_DRUGS ne sert plus qu a nommer le gene responsable
   dans l affichage.

Les libelles cliniques sont separes des etiquettes du modele : les classes du jeu de
donnees restent EVITER / ADAPTER_DOSE / SURVEILLER / STANDARD.
"""

import os
import pickle
import warnings

import joblib
import numpy as np
import torch
import torch.nn as nn

warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# CHOIX DE LA VERSION — un seul mot a changer
# ---------------------------------------------------------------------------
# 'neg' : modeles du 7 octobre 19:12, corpus avec exemples negatifs,
#         empreintes de Morgan nulles (seuls les 6 descripteurs portent
#         l information moleculaire).
# 'fp'  : modeles de train_fp.py, memes donnees, empreintes reparees.
#         A activer des que fp_scores.json et les modeles *_fp existent.
VERSION = 'neg'

RESULTS_DIR = '/home/mouna/projet_memoire/model_v2/results'
DATA_DIR    = '/home/mouna/projet_memoire/model_v2/data'

CONFIGS = {
    'neg': {
        'rf':     'rf_pgx_neg.pkl',
        'xgb':    'xgb_pgx_neg.pkl',
        'dl':     'dl_pgx_neg.pth',
        'le':     'le_pgx_neg.pkl',
        'genes':  'genes_pgx_neg.pkl',
        'scaler': 'scaler_pgx_neg.pkl',
        'fp':     'drug_fingerprints.pkl',       # 512 bits nuls
    },
    'fp': {
        'rf':     'rf_pgx_fp.pkl',
        'xgb':    'xgb_pgx_fp.pkl',
        'dl':     'dl_pgx_fp.pth',
        'le':     'le_pgx_fp.pkl',
        'genes':  'genes_pgx_fp.pkl',
        'scaler': 'scaler_pgx_fp.pkl',
        'fp':     'drug_fingerprints_v2.pkl',    # empreintes reparees
    },
}

# ---------------------------------------------------------------------------
# Libelles
# ---------------------------------------------------------------------------
# Etiquettes du modele — ne jamais modifier, elles correspondent aux classes
# du jeu de donnees et aux resultats deja publies.
ORDRE_GRAVITE = ['EVITER', 'ADAPTER_DOSE', 'SURVEILLER', 'STANDARD']

# Libelles destines au clinicien — affichage uniquement.
ACTION_LABELS = {
    'EVITER':       'Contre-indiqué',
    'ADAPTER_DOSE': 'Ajuster la dose',
    'SURVEILLER':   'Utiliser avec précaution',
    'STANDARD':     'Prescrivable normalement',
}

ACTION_DETAIL = {
    'EVITER':       "Éviter cette molécule ; envisager une alternative thérapeutique.",
    'ADAPTER_DOSE': "Posologie à adapter en fonction du phénotype pharmacogénétique.",
    'SURVEILLER':   "Prescription possible sous surveillance clinique ou biologique renforcée.",
    'STANDARD':     "Aucune adaptation pharmacogénétique indiquée pour ce profil.",
}

ACTION_ICONS  = {'EVITER': '⛔', 'ADAPTER_DOSE': '⚠️', 'SURVEILLER': '👁️', 'STANDARD': '✅'}
ACTION_COLORS = {'EVITER': 'danger', 'ADAPTER_DOSE': 'warning',
                 'SURVEILLER': 'info', 'STANDARD': 'success'}

PHENO_EXPLAIN = {
    0.0: 'Métaboliseur lent — enzyme inactive ou très réduite',
    0.5: 'Métaboliseur intermédiaire — enzyme partiellement active',
    1.0: 'Métaboliseur normal',
    1.5: 'Métaboliseur rapide — enzyme plus active que la normale',
    2.0: 'Métaboliseur ultrarapide — enzyme très active',
}

GENO_TO_PHENO = {'0/0': 1.0, '0|0': 1.0, '0/1': 0.5, '1/0': 0.5,
                 '0|1': 0.5, '1|0': 0.5, '1/1': 0.0, '1|1': 0.0}

# Associations gene-medicament documentees. Ne filtre plus les predictions :
# sert uniquement a nommer le gene responsable et a signaler qu une association
# est documentee dans les referentiels.
GENE_DRUGS = {
    'CYP2C19': ['clopidogrel', 'omeprazole', 'citalopram', 'sertraline', 'voriconazole',
                'esomeprazole', 'lansoprazole', 'pantoprazole', 'escitalopram',
                'amitriptyline', 'clomipramine', 'imipramine'],
    'CYP2D6':  ['codeine', 'tramadol', 'tamoxifen', 'risperidone', 'amitriptyline',
                'fluoxetine', 'paroxetine', 'atomoxetine', 'metoprolol', 'propafenone',
                'haloperidol', 'clomipramine'],
    'CYP2C9':  ['warfarin', 'ibuprofen', 'celecoxib', 'phenytoin', 'flurbiprofen',
                'piroxicam', 'losartan'],
    'CYP2B6':  ['efavirenz', 'methadone', 'bupropion', 'cyclophosphamide', 'nevirapine'],
    'DPYD':    ['fluorouracil', 'capecitabine', 'tegafur'],
    'TPMT':    ['azathioprine', 'mercaptopurine', 'thioguanine'],
    'NUDT15':  ['azathioprine', 'mercaptopurine', 'thioguanine'],
    'SLCO1B1': ['simvastatin', 'atorvastatin', 'rosuvastatin', 'pravastatin'],
    'UGT1A1':  ['irinotecan', 'atazanavir', 'belinostat'],
    'VKORC1':  ['warfarin', 'acenocoumarol', 'phenprocoumon'],
    'G6PD':    ['rasburicase', 'primaquine', 'dapsone'],
    'HLA-B':   ['abacavir', 'carbamazepine', 'allopurinol', 'oxcarbazepine'],
    'HLA-A':   ['abacavir', 'carbamazepine'],
    'RYR1':    ['desflurane', 'sevoflurane', 'isoflurane', 'succinylcholine'],
    'CYP3A5':  ['tacrolimus', 'cyclosporine', 'sirolimus'],
    'CYP4F2':  ['warfarin', 'vitamin k'],
    'CYP2A6':  ['nicotine', 'efavirenz', 'valproic acid'],
    'CYP1A2':  ['clozapine', 'caffeine', 'theophylline', 'olanzapine'],
    'NAT2':    ['isoniazid', 'hydralazine', 'sulfamethoxazole'],
    'ABCG2':   ['allopurinol', 'rosuvastatin', 'atorvastatin'],
    'CYP3A4':  ['tacrolimus', 'midazolam', 'simvastatin', 'atorvastatin'],
}

# ---------------------------------------------------------------------------
# Architecture — identique a celle de l entrainement
# ---------------------------------------------------------------------------
_rf = _xgb = _dl = _le = _GENES = _scaler = _drug_fp = None
_n_genes = None
_n_drug = 518


class GeneAttention(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.attn = nn.Linear(n, n)

    def forward(self, x):
        return x * torch.softmax(self.attn(x), dim=1)


class PharmDL(nn.Module):
    def __init__(self, n_genes, n_out):
        super().__init__()
        self._ng = n_genes
        self.gene_attention = GeneAttention(n_genes)
        self.gene_branch = nn.Sequential(
            nn.Linear(n_genes, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 32), nn.BatchNorm1d(32), nn.ReLU())
        self.drug_branch = nn.Sequential(
            nn.Linear(518, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 64), nn.ReLU())
        self.combined = nn.Sequential(
            nn.Linear(96, 64), nn.BatchNorm1d(64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, n_out))

    def forward(self, x):
        g = self.gene_branch(self.gene_attention(x[:, :self._ng]))
        d = self.drug_branch(x[:, self._ng:])
        return self.combined(torch.cat([g, d], dim=1))


# ---------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------
def load_models(version=None):
    """Charge modeles et empreintes de la version demandee.

    Leve une erreur explicite si un fichier manque, plutot que de charger
    silencieusement une combinaison incoherente.
    """
    global _rf, _xgb, _dl, _le, _GENES, _scaler, _drug_fp, _n_genes, VERSION

    if version is not None:
        VERSION = version
    cfg = CONFIGS[VERSION]

    chemins = {k: os.path.join(RESULTS_DIR, v) for k, v in cfg.items() if k != 'fp'}
    chemins['fp'] = os.path.join(DATA_DIR, cfg['fp'])

    manquants = [f'{k} -> {p}' for k, p in chemins.items() if not os.path.exists(p)]
    if manquants:
        raise FileNotFoundError(
            "Version '" + VERSION + "' incomplete. Fichiers absents :\n  "
            + "\n  ".join(manquants))

    _rf = joblib.load(chemins['rf'])
    _xgb = joblib.load(chemins['xgb'])
    with open(chemins['le'], 'rb') as f:
        _le = pickle.load(f)
    with open(chemins['genes'], 'rb') as f:
        _GENES = pickle.load(f)
    with open(chemins['scaler'], 'rb') as f:
        _scaler = pickle.load(f)
    with open(chemins['fp'], 'rb') as f:
        _drug_fp = pickle.load(f)

    _n_genes = len(_GENES)
    _dl = PharmDL(_n_genes, len(_le.classes_))
    _dl.load_state_dict(torch.load(chemins['dl'], map_location='cpu'))
    _dl.eval()

    M = np.array([np.asarray(v)[:512] for v in _drug_fp.values()])
    nulles = int((M.sum(axis=1) == 0).sum())
    print(f"[predict_v3] version={VERSION} | {_n_genes} genes | "
          f"{len(_drug_fp)} medicaments | empreintes nulles : {nulles}", flush=True)
    if nulles:
        print("[predict_v3] AVERTISSEMENT : empreintes de Morgan nulles — "
              "la branche moleculaire ne recoit que les 6 descripteurs.", flush=True)


# Compatibilite avec l ancien nom utilise par app.py
load_models_v2 = load_models


# ---------------------------------------------------------------------------
# Coeur de l inference
# ---------------------------------------------------------------------------
def _probabilites(X_brut):
    """Probabilites des trois modeles sur un lot de vecteurs NON normalises.

    X_brut : tableau (n, n_genes + 518), variables genetiques puis moleculaires.

    Le reseau recoit la partie medicament normalisee par le scaler ; Random Forest et
    XGBoost recoivent le vecteur brut. C est la convention de l entrainement : seule
    entrainer_dl applique un StandardScaler, et uniquement sur les colonnes [n_genes:].
    """
    X_brut = np.asarray(X_brut, dtype=float)
    if X_brut.ndim == 1:
        X_brut = X_brut.reshape(1, -1)

    X_dl = X_brut.copy()
    X_dl[:, _n_genes:] = _scaler.transform(X_brut[:, _n_genes:])

    with torch.no_grad():
        p_dl = torch.softmax(_dl(torch.FloatTensor(X_dl)), dim=1).numpy()

    p_rf = _rf.predict_proba(X_brut)
    p_xgb = _xgb.predict_proba(X_brut)

    return p_dl, p_rf, p_xgb


def _ensemble(p_dl, p_rf):
    """Ponderation 2/3 reseau, 1/3 Random Forest — inchangee depuis predict_v2."""
    return (2.0 * p_dl + 1.0 * p_rf) / 3.0


def _fiche(drug, p_ens, p_dl, p_rf, p_xgb, gene_vector, mutated_genes):
    """Construit le dictionnaire affiche pour un medicament."""
    y = int(np.argmax(p_ens))
    action = _le.inverse_transform([y])[0]

    responsables = [g for g in mutated_genes if drug in GENE_DRUGS.get(g, [])]
    if responsables:
        gene_val = gene_vector[_GENES.index(responsables[0])]
        gene_aff = ', '.join(dict.fromkeys(responsables))
        documente = True
    else:
        gene_val = min(gene_vector) if mutated_genes else 1.0
        gene_aff = 'Profil pharmacogénomique global'
        documente = False

    action_dl = _le.inverse_transform([int(np.argmax(p_dl))])[0]
    action_xgb = _le.inverse_transform([int(np.argmax(p_xgb))])[0]

    return {
        'drug':              drug,
        'action':            action,
        'confidence':        round(float(p_ens[y]) * 100, 1),
        'icon':              ACTION_ICONS.get(action, ''),
        'label':             ACTION_LABELS.get(action, action),
        'detail':            ACTION_DETAIL.get(action, ''),
        'color':             ACTION_COLORS.get(action, 'secondary'),
        'known_drug':        True,
        'association_documentee': documente,
        'responsible_gene':  gene_aff,
        'phenotype_explain': PHENO_EXPLAIN.get(gene_val, 'Phénotype non déterminé'),
        'action_dl':         action_dl,
        'action_xgboost':    action_xgb,
        'accord_modeles':    bool(action == action_dl == action_xgb),
        'probabilities':     {_le.classes_[k]: round(float(p_ens[k]) * 100, 1)
                              for k in range(len(_le.classes_))},
    }


# ---------------------------------------------------------------------------
# Profil patient
# ---------------------------------------------------------------------------
def build_patient_profile(variants_list):
    """Vecteur des 31 genes. Pour un gene porte par plusieurs variants, la valeur
    la plus defavorable est retenue."""
    gene_vector = [1.0] * _n_genes
    for v in variants_list:
        gene = v.get('gene', '')
        if gene in _GENES:
            val = GENO_TO_PHENO.get(str(v.get('genotype', '0/0')).strip(), 0.5)
            i = _GENES.index(gene)
            if val < gene_vector[i]:
                gene_vector[i] = val
    return gene_vector


def genes_mutes(gene_vector):
    return [_GENES[i] for i, v in enumerate(gene_vector) if v < 1.0]


# ---------------------------------------------------------------------------
# API publique
# ---------------------------------------------------------------------------
def predict_all_drugs(gene_vector, mutated_genes=None, inclure_standard=False):
    """Soumet au modele TOUS les medicaments du referentiel moleculaire.

    Aucune liste manuelle ne filtre en amont : le modele recoit le profil genetique
    complet du patient et l empreinte de chaque molecule, puis decide.
    """
    if mutated_genes is None:
        mutated_genes = genes_mutes(gene_vector)

    noms = list(_drug_fp.keys())
    G = np.tile(np.asarray(gene_vector, dtype=float), (len(noms), 1))
    FP = np.vstack([np.asarray(_drug_fp[d], dtype=float) for d in noms])
    X = np.hstack([G, FP])

    p_dl, p_rf, p_xgb = _probabilites(X)
    p_ens = _ensemble(p_dl, p_rf)

    resultats = []
    for i, drug in enumerate(noms):
        action = _le.inverse_transform([int(np.argmax(p_ens[i]))])[0]
        if action == 'STANDARD' and not inclure_standard:
            continue
        resultats.append(_fiche(drug, p_ens[i], p_dl[i], p_rf[i], p_xgb[i],
                                gene_vector, mutated_genes))

    resultats.sort(key=lambda r: (ORDRE_GRAVITE.index(r['action'])
                                  if r['action'] in ORDRE_GRAVITE else 4,
                                  not r['association_documentee'],
                                  -r['confidence']))
    return resultats


def predict_drug_for_patient(gene_vector, drug, mutated_genes=None):
    """Predit l action pour UN medicament, avec le profil genetique complet."""
    dl_nom = str(drug).lower().strip()
    if dl_nom not in _drug_fp:
        return {
            'drug': dl_nom, 'action': None, 'confidence': 0.0,
            'known_drug': False,
            'icon': '❔', 'color': 'secondary',
            'label': 'Médicament hors référentiel',
            'detail': ("Cette molécule ne figure pas dans le référentiel moléculaire "
                       "du modèle. Aucune prédiction n'est produite."),
        }

    if mutated_genes is None:
        mutated_genes = genes_mutes(gene_vector)

    X = np.hstack([np.asarray(gene_vector, dtype=float),
                   np.asarray(_drug_fp[dl_nom], dtype=float)]).reshape(1, -1)
    p_dl, p_rf, p_xgb = _probabilites(X)
    p_ens = _ensemble(p_dl, p_rf)

    return _fiche(dl_nom, p_ens[0], p_dl[0], p_rf[0], p_xgb[0],
                  gene_vector, mutated_genes)


def predict_for_patient(variants_list, extra_drugs=None, inclure_standard=False):
    """Point d entree principal de l application.

    Retourne (predictions, genes_mutes, gene_vector).
    Contrairement a predict_v2, aucun medicament n est ecarte par GENE_DRUGS ;
    extra_drugs ne sert plus qu a garantir la presence d une molecule precise
    dans la liste, meme si elle est predite STANDARD.
    """
    gene_vector = build_patient_profile(variants_list)
    mutes = genes_mutes(gene_vector)

    resultats = predict_all_drugs(gene_vector, mutes, inclure_standard=inclure_standard)

    if extra_drugs:
        presents = {r['drug'] for r in resultats}
        for d in extra_drugs:
            nom = str(d).lower().strip()
            if nom and nom != 'aucune recommandation trouvee' and nom not in presents:
                fiche = predict_drug_for_patient(gene_vector, nom, mutes)
                if fiche.get('known_drug'):
                    resultats.append(fiche)

        resultats.sort(key=lambda r: (ORDRE_GRAVITE.index(r['action'])
                                      if r['action'] in ORDRE_GRAVITE else 4,
                                      not r['association_documentee'],
                                      -r['confidence']))

    return resultats, mutes, gene_vector


def resume_par_gene(predictions, gene_vector, mutated_genes):
    """Resume par gene mute, fonde sur les predictions du modele.

    Remplace la regle ecrite a la main de app.py ligne 61, qui deduisait l action
    d un seuil sur la valeur du gene et ignorait la sortie du modele.
    L action retenue pour un gene est la plus grave parmi les medicaments qui lui
    sont attribues ; a defaut, STANDARD.
    """
    resume = {}
    for gene in dict.fromkeys(mutated_genes):
        liees = [p for p in predictions if gene in p.get('responsible_gene', '')]
        if liees:
            pire = min(liees, key=lambda p: ORDRE_GRAVITE.index(p['action'])
                       if p['action'] in ORDRE_GRAVITE else 4)
            action = pire['action']
        else:
            action = 'STANDARD'

        gene_val = gene_vector[_GENES.index(gene)] if gene in _GENES else 1.0
        resume[gene] = {
            'action':          action,
            'label':           ACTION_LABELS.get(action, action),
            'icon':            ACTION_ICONS.get(action, ''),
            'color':           ACTION_COLORS.get(action, 'secondary'),
            'phenotype':       PHENO_EXPLAIN.get(gene_val, 'Phénotype non déterminé'),
            'recommendations': liees[:5],
            'origine':         'modèle',
        }
    return resume


if __name__ == '__main__':
    load_models()
    print(f"Classes : {list(_le.classes_)}")
    print(f"Genes   : {_GENES}")

    # Patient fictif : CYP2C19 metaboliseur lent
    gv = [1.0] * _n_genes
    if 'CYP2C19' in _GENES:
        gv[_GENES.index('CYP2C19')] = 0.0

    r = predict_drug_for_patient(gv, 'clopidogrel')
    print(f"\nclopidogrel, CYP2C19 lent -> {r['action']} ({r['confidence']} %)")
    print(f"  reseau   : {r['action_dl']}")
    print(f"  xgboost  : {r['action_xgboost']}")
    print(f"  libelle  : {r['label']}")

    tous = predict_all_drugs(gv)
    print(f"\n{len(tous)} medicaments non STANDARD sur {len(_drug_fp)} du referentiel")
    for p in tous[:5]:
        print(f"  {p['action']:13s} {p['drug']:20s} {p['confidence']:5.1f} %  "
              f"{'documente' if p['association_documentee'] else 'non documente'}")
