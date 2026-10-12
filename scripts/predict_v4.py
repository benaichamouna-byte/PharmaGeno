"""
predict_v4.py — Moteur d inference de PharmaGeno

Remplace predict_v3.py. Aucun fichier existant n est modifie.

CORRECTIONS PAR RAPPORT A predict_v3.py
----------------------------------------

1. SUPPRESSION DE L ENSEMBLE NON VALIDE
   predict_v2 et v3 combinaient (2*DL + 1*RF)/3. Cette ponderation n a jamais ete
   evaluee experimentalement : aucune mesure du corpus ne la justifie. Elle brouillait
   de plus la lecture de ce que produit reellement le reseau, qui est l objet du
   memoire.
   La sortie principale est desormais celle du RESEAU PROFOND seul. XGBoost et Random
   Forest sont calcules et exposes comme comparateurs, avec leurs taux d erreur mesures,
   ce qui donne a voir le resultat de RQ2 au lieu de le dissimuler.

2. PHENOTYPES PAR CATEGORIE DE GENE
   predict_v3 affichait « Metaboliseur intermediaire » pour un genotype 0/1, quel que
   soit le gene. C est biologiquement faux hors des enzymes de metabolisation :
     - HLA-B*57:01 n est pas un metaboliseur, une seule copie suffit a porter le risque
     - VKORC1 est une cible pharmacologique, pas une enzyme de metabolisation
     - G6PD est lie a l X : un homme hemizygote n est pas une femme heterozygote
     - IFNL3 est un marqueur de reponse au traitement
   L encodage numerique reste inchange — c est l entree documentee du modele — mais le
   libelle affiche depend desormais de la categorie du gene.

3. AUCUN NOMBRE DE MEDICAMENTS CODE EN DUR
   predict_v3 et app_v3 mentionnaient « 531 medicaments », nombre qui n existe dans
   aucun fichier du projet. Le corpus en contient 530, le referentiel d empreintes 437.
   Toute mention passe maintenant par len(_drug_fp).

4. PROVENANCE EXPLICITE
   Chaque sortie porte un champ 'provenance' valant 'modele'. Les libelles cliniques
   sont conserves, mais l interface doit indiquer qu il s agit d une prediction et non
   d une recommandation reglementaire.

ACQUIS DE predict_v3, CONSERVES
-------------------------------
   - VERSION lie le modele et le fichier d empreintes : un modele _neg avec des
     empreintes reparees produirait des predictions depourvues de sens.
   - Random Forest et XGBoost recoivent les variables brutes ; seul le reseau applique
     le scaler, et uniquement sur les 518 colonnes du medicament, conformement a
     l entrainement.
   - Le profil genetique complet du patient est utilise a chaque inference.
   - Aucun filtre manuel n ecarte de medicament : le modele voit tout le referentiel.
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
# 'neg' : modeles du 7 octobre 19:12. Empreintes de Morgan nulles : seuls les
#         6 descripteurs physico-chimiques portent l information moleculaire.
# 'fp'  : modeles de train_fp.py, memes donnees, empreintes reparees
#         (437/437 medicaments, 42,9 bits actifs en moyenne).
VERSION = 'fp'

RESULTS_DIR = '/home/mouna/projet_memoire/model_v2/results'
DATA_DIR    = '/home/mouna/projet_memoire/model_v2/data'

CONFIGS = {
    'neg': {'rf': 'rf_pgx_neg.pkl', 'xgb': 'xgb_pgx_neg.pkl', 'dl': 'dl_pgx_neg.pth',
            'le': 'le_pgx_neg.pkl', 'genes': 'genes_pgx_neg.pkl',
            'scaler': 'scaler_pgx_neg.pkl', 'fp': 'drug_fingerprints.pkl'},
    'fp':  {'rf': 'rf_pgx_fp.pkl', 'xgb': 'xgb_pgx_fp.pkl', 'dl': 'dl_pgx_fp.pth',
            'le': 'le_pgx_fp.pkl', 'genes': 'genes_pgx_fp.pkl',
            'scaler': 'scaler_pgx_fp.pkl', 'fp': 'drug_fingerprints_v2.pkl'},
}

# Taux d erreur critique mesures en validation croisee groupee, 5 plis, recouvrement 0.
# CER strict = proportion de contre-indications non detectees = 1 - rappel(EVITER).
# Source : model_v2/results/neg_scores.json
CER_MESURE = {'DL': 10.18, 'XGBoost': 4.41, 'RandomForest': 6.18}
F1_MESURE  = {'DL': 0.9093, 'XGBoost': 0.9763, 'RandomForest': 0.9574}

# ---------------------------------------------------------------------------
# Libelles
# ---------------------------------------------------------------------------
# Etiquettes du modele — ne jamais modifier : elles correspondent aux classes du
# jeu de donnees et a tous les resultats deja produits.
ORDRE_GRAVITE = ['EVITER', 'ADAPTER_DOSE', 'SURVEILLER', 'STANDARD']

# Libelles cliniques — affichage uniquement.
ACTION_LABELS = {
    'EVITER':       'Contre-indiqué',
    'ADAPTER_DOSE': 'Ajuster la dose',
    'SURVEILLER':   'Utiliser avec précaution',
    'STANDARD':     'Prescrivable normalement',
}

ACTION_DETAIL = {
    'EVITER':       "Éviter cette molécule ; envisager une alternative thérapeutique.",
    'ADAPTER_DOSE': "Posologie à adapter en fonction du profil pharmacogénomique.",
    'SURVEILLER':   "Prescription possible sous surveillance clinique ou biologique renforcée.",
    'STANDARD':     "Aucune adaptation pharmacogénomique documentée pour ce profil.",
}

ACTION_ICONS  = {'EVITER': '⛔', 'ADAPTER_DOSE': '⚠️', 'SURVEILLER': '👁️', 'STANDARD': '✅'}
ACTION_COLORS = {'EVITER': 'danger', 'ADAPTER_DOSE': 'warning',
                 'SURVEILLER': 'info', 'STANDARD': 'success'}

# ---------------------------------------------------------------------------
# Phenotypes par categorie de gene
# ---------------------------------------------------------------------------
# La notion de « metaboliseur » ne s applique qu aux enzymes de metabolisation.
# Pour les autres familles, le libelle decrit ce que la variation signifie
# reellement : fonction de transport, portage d un allele a risque, sensibilite
# a une cible, deficit enzymatique, susceptibilite, ou marqueur de reponse.

GENE_CATEGORIE = {
    # Enzymes de metabolisation — phenotype de metaboliseur
    'CYP1A2': 'metaboliseur', 'CYP2A6': 'metaboliseur', 'CYP2B6': 'metaboliseur',
    'CYP2C19': 'metaboliseur', 'CYP2C9': 'metaboliseur', 'CYP2D6': 'metaboliseur',
    'CYP3A4': 'metaboliseur', 'CYP3A5': 'metaboliseur', 'CYP4F2': 'metaboliseur',
    'DPYD': 'metaboliseur', 'NAT2': 'metaboliseur', 'NUDT15': 'metaboliseur',
    'TPMT': 'metaboliseur', 'UGT1A1': 'metaboliseur',
    # Transporteurs — fonction de transport
    'ABCG2': 'transporteur', 'SLCO1B1': 'transporteur',
    # Systeme HLA — portage d un allele a risque, pas un phenotype enzymatique
    'HLA-A': 'hla', 'HLA-B': 'hla',
    # Cible pharmacologique
    'VKORC1': 'cible',
    # Deficit enzymatique lie a l X
    'G6PD': 'deficit',
    # Susceptibilites
    'RYR1': 'susceptibilite', 'CACNA1S': 'susceptibilite', 'MT-RNR1': 'susceptibilite',
    # Marqueurs de reponse ou de risque
    'IFNL3': 'marqueur', 'ACE': 'marqueur', 'ADRB2': 'marqueur', 'CFTR': 'marqueur',
    'EGFR': 'marqueur', 'F5': 'marqueur', 'MTHFR': 'marqueur', 'SLC19A1': 'marqueur',
}

PHENO_PAR_CATEGORIE = {
    'metaboliseur': {
        0.0: 'Métaboliseur lent — activité enzymatique nulle ou très réduite',
        0.5: 'Métaboliseur intermédiaire — activité enzymatique partielle',
        1.0: 'Métaboliseur normal',
        1.5: 'Métaboliseur rapide',
        2.0: 'Métaboliseur ultrarapide',
    },
    'transporteur': {
        0.0: 'Fonction de transport fortement réduite',
        0.5: 'Fonction de transport réduite',
        1.0: 'Fonction de transport normale',
        1.5: 'Fonction de transport augmentée',
        2.0: 'Fonction de transport fortement augmentée',
    },
    'hla': {
        0.0: 'Allèle à risque présent sur les deux chromosomes',
        0.5: 'Allèle à risque présent — une seule copie suffit à porter le risque',
        1.0: 'Allèle à risque non détecté',
    },
    'cible': {
        0.0: 'Sensibilité accrue à la molécule ciblant ce gène (homozygote)',
        0.5: 'Sensibilité intermédiaire (hétérozygote)',
        1.0: 'Réponse attendue standard',
    },
    'deficit': {
        0.0: 'Déficit enzymatique',
        0.5: 'Variant présent à une copie — gène lié à l’X, interprétation dépendante du sexe',
        1.0: 'Activité enzymatique normale',
    },
    'susceptibilite': {
        0.0: 'Variant de susceptibilité présent sur les deux chromosomes',
        0.5: 'Variant de susceptibilité présent',
        1.0: 'Variant de susceptibilité non détecté',
    },
    'marqueur': {
        0.0: 'Génotype associé à une réponse défavorable',
        0.5: 'Génotype hétérozygote',
        1.0: 'Génotype de référence',
    },
}

# Genes dont le phenotype ne peut pas etre etabli de maniere fiable a partir d un VCF
# contenant seulement SNP et indels : variations structurales, nombre de copies, ou
# nomenclature non resolue par un encodage par variant.
GENES_APPEL_SPECIALISE = {'CYP2D6', 'HLA-A', 'HLA-B', 'MT-RNR1'}

AVERTISSEMENT_APPEL = ("Encodage approximatif : ce gène requiert un appel spécialisé "
                       "(variations structurales, nombre de copies ou nomenclature "
                       "d’allèles) non résolu par un VCF de SNP et indels.")

GENO_TO_PHENO = {'0/0': 1.0, '0|0': 1.0, '0/1': 0.5, '1/0': 0.5,
                 '0|1': 0.5, '1|0': 0.5, '1/1': 0.0, '1|1': 0.0}


def phenotype_libelle(gene, valeur):
    """Libelle du phenotype adapte a la categorie du gene."""
    cat = GENE_CATEGORIE.get(gene, 'marqueur')
    table = PHENO_PAR_CATEGORIE[cat]
    if valeur in table:
        return table[valeur]
    proche = min(table, key=lambda v: abs(v - valeur))
    return table[proche]


# Associations gene-medicament documentees. Ne filtre aucune prediction : sert a
# nommer le gene responsable et a signaler qu une association est documentee.
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


def poids_attention(gene_vector):
    """Poids d attention du reseau sur les 31 genes, pour un profil donne.

    Signal interne du modele, utile a l interpretation. Ne constitue pas une preuve
    de causalite biologique (Jain et Wallace, NAACL-HLT 2019).
    """
    x = torch.FloatTensor(np.asarray(gene_vector, dtype=float).reshape(1, -1))
    with torch.no_grad():
        w = torch.softmax(_dl.gene_attention.attn(x), dim=1).numpy()[0]
    return {_GENES[i]: round(float(w[i]), 4) for i in range(_n_genes)}


# ---------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------
def load_models(version=None):
    """Charge modeles et empreintes de la version demandee, ensemble."""
    global _rf, _xgb, _dl, _le, _GENES, _scaler, _drug_fp, _n_genes, VERSION

    if version is not None:
        VERSION = version
    cfg = CONFIGS[VERSION]

    chemins = {k: os.path.join(RESULTS_DIR, v) for k, v in cfg.items() if k != 'fp'}
    chemins['fp'] = os.path.join(DATA_DIR, cfg['fp'])

    manquants = [f'{k} -> {p}' for k, p in chemins.items() if not os.path.exists(p)]
    if manquants:
        raise FileNotFoundError("Version '" + VERSION + "' incomplete. Fichiers absents :\n  "
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
    print(f"[predict_v4] version={VERSION} | {_n_genes} gènes | "
          f"{len(_drug_fp)} médicaments | empreintes nulles : {nulles}", flush=True)
    print(f"[predict_v4] sortie principale : réseau profond "
          f"(F1 {F1_MESURE['DL']:.3f}, CER {CER_MESURE['DL']} %) | "
          f"comparateur XGBoost (F1 {F1_MESURE['XGBoost']:.3f}, "
          f"CER {CER_MESURE['XGBoost']} %)", flush=True)
    if nulles:
        print("[predict_v4] AVERTISSEMENT : empreintes de Morgan nulles — la branche "
              "moléculaire ne reçoit que les 6 descripteurs.", flush=True)


load_models_v2 = load_models   # compatibilite avec l ancien nom


def nb_medicaments():
    """Taille reelle du referentiel moleculaire. A utiliser partout plutot qu un
    nombre code en dur."""
    return len(_drug_fp) if _drug_fp else 0


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
def _probabilites(X_brut):
    """Probabilites des trois modeles sur un lot de vecteurs NON normalises.

    Le reseau recoit la partie medicament normalisee ; Random Forest et XGBoost
    recoivent le vecteur brut, conformement a l entrainement.
    """
    X_brut = np.asarray(X_brut, dtype=float)
    if X_brut.ndim == 1:
        X_brut = X_brut.reshape(1, -1)

    X_dl = X_brut.copy()
    X_dl[:, _n_genes:] = _scaler.transform(X_brut[:, _n_genes:])

    with torch.no_grad():
        p_dl = torch.softmax(_dl(torch.FloatTensor(X_dl)), dim=1).numpy()

    return p_dl, _rf.predict_proba(X_brut), _xgb.predict_proba(X_brut)


def _fiche(drug, p_dl, p_rf, p_xgb, gene_vector, mutated_genes):
    """Fiche d un medicament. La decision affichee est celle du RESEAU PROFOND ;
    Random Forest et XGBoost figurent comme comparateurs."""
    y = int(np.argmax(p_dl))
    action = _le.inverse_transform([y])[0]
    action_rf = _le.inverse_transform([int(np.argmax(p_rf))])[0]
    action_xgb = _le.inverse_transform([int(np.argmax(p_xgb))])[0]

    responsables = [g for g in mutated_genes if drug in GENE_DRUGS.get(g, [])]
    if responsables:
        gene_ref = responsables[0]
        gene_val = gene_vector[_GENES.index(gene_ref)]
        gene_aff = ', '.join(dict.fromkeys(responsables))
        documente = True
    else:
        gene_ref = None
        gene_val = min(gene_vector) if mutated_genes else 1.0
        gene_aff = 'Profil pharmacogénomique global'
        documente = False

    return {
        'drug':              drug,
        'action':            action,
        'confidence':        round(float(p_dl[y]) * 100, 1),
        'icon':              ACTION_ICONS.get(action, ''),
        'label':             ACTION_LABELS.get(action, action),
        'detail':            ACTION_DETAIL.get(action, ''),
        'color':             ACTION_COLORS.get(action, 'secondary'),
        'known_drug':        True,
        'provenance':        'modele',
        'modele_principal':  'Réseau profond',
        'association_documentee': documente,
        'responsible_gene':  gene_aff,
        'phenotype_explain': (phenotype_libelle(gene_ref, gene_val) if gene_ref
                              else 'Profil combiné sur plusieurs gènes'),
        'appel_specialise':  bool(gene_ref in GENES_APPEL_SPECIALISE) if gene_ref else False,
        # Comparateurs
        'action_xgboost':    action_xgb,
        'label_xgboost':     ACTION_LABELS.get(action_xgb, action_xgb),
        'confiance_xgboost': round(float(np.max(p_xgb)) * 100, 1),
        'action_rf':         action_rf,
        'accord_dl_xgboost': bool(action == action_xgb),
        'probabilities':     {_le.classes_[k]: round(float(p_dl[k]) * 100, 1)
                              for k in range(len(_le.classes_))},
    }


# ---------------------------------------------------------------------------
# Profil patient
# ---------------------------------------------------------------------------
def build_patient_profile(variants_list):
    """Vecteur des genes. Pour un gene porte par plusieurs variants, la valeur la
    plus defavorable est retenue."""
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
    """Soumet au modele l integralite du referentiel moleculaire."""
    if mutated_genes is None:
        mutated_genes = genes_mutes(gene_vector)

    noms = list(_drug_fp.keys())
    G = np.tile(np.asarray(gene_vector, dtype=float), (len(noms), 1))
    FP = np.vstack([np.asarray(_drug_fp[d], dtype=float) for d in noms])
    p_dl, p_rf, p_xgb = _probabilites(np.hstack([G, FP]))

    resultats = []
    for i, drug in enumerate(noms):
        action = _le.inverse_transform([int(np.argmax(p_dl[i]))])[0]
        if action == 'STANDARD' and not inclure_standard:
            continue
        resultats.append(_fiche(drug, p_dl[i], p_rf[i], p_xgb[i],
                                gene_vector, mutated_genes))

    resultats.sort(key=lambda r: (ORDRE_GRAVITE.index(r['action'])
                                  if r['action'] in ORDRE_GRAVITE else 4,
                                  not r['association_documentee'], -r['confidence']))
    return resultats


def predict_drug_for_patient(gene_vector, drug, mutated_genes=None):
    """Predit l action pour UN medicament, avec le profil genetique complet."""
    nom = str(drug).lower().strip()
    if nom not in _drug_fp:
        return {
            'drug': nom, 'action': None, 'confidence': 0.0, 'known_drug': False,
            'icon': '❔', 'color': 'secondary', 'provenance': 'modele',
            'label': 'Médicament hors référentiel',
            'detail': (f"Cette molécule ne figure pas parmi les {nb_medicaments()} "
                       f"médicaments du référentiel moléculaire. Aucune prédiction "
                       f"n'est produite."),
        }

    if mutated_genes is None:
        mutated_genes = genes_mutes(gene_vector)

    X = np.hstack([np.asarray(gene_vector, dtype=float),
                   np.asarray(_drug_fp[nom], dtype=float)]).reshape(1, -1)
    p_dl, p_rf, p_xgb = _probabilites(X)
    return _fiche(nom, p_dl[0], p_rf[0], p_xgb[0], gene_vector, mutated_genes)


def predict_for_patient(variants_list, extra_drugs=None, inclure_standard=False):
    """Point d entree principal. Retourne (predictions, genes_mutes, gene_vector)."""
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
                                      not r['association_documentee'], -r['confidence']))

    return resultats, mutes, gene_vector


def resume_modele_par_gene(predictions, gene_vector, mutated_genes):
    """Synthese par gene, fondee sur les predictions du modele.

    Anciennement nomme cpic_by_gene dans app.py — nom trompeur, puisque ce resume
    provient du modele et non des recommandations CPIC.
    """
    attention = poids_attention(gene_vector)
    resume = {}
    for gene in dict.fromkeys(mutated_genes):
        liees = [p for p in predictions if gene in p.get('responsible_gene', '')]
        if liees:
            pire = min(liees, key=lambda p: ORDRE_GRAVITE.index(p['action'])
                       if p['action'] in ORDRE_GRAVITE else 4)
            action = pire['action']
        else:
            action = 'STANDARD'

        val = gene_vector[_GENES.index(gene)] if gene in _GENES else 1.0
        resume[gene] = {
            'action':          action,
            'label':           ACTION_LABELS.get(action, action),
            'icon':            ACTION_ICONS.get(action, ''),
            'color':           ACTION_COLORS.get(action, 'secondary'),
            'phenotype':       phenotype_libelle(gene, val),
            'categorie':       GENE_CATEGORIE.get(gene, 'marqueur'),
            'valeur_encodee':  val,
            'poids_attention': attention.get(gene, 0.0),
            'appel_specialise': gene in GENES_APPEL_SPECIALISE,
            'avertissement':   AVERTISSEMENT_APPEL if gene in GENES_APPEL_SPECIALISE else '',
            'recommendations': liees[:5],
            'provenance':      'modele',
        }
    return resume


if __name__ == '__main__':
    load_models()
    print(f"\nClasses : {list(_le.classes_)}")

    gv = [1.0] * _n_genes
    for g, v in [('CYP2C19', 0.0), ('HLA-B', 0.5), ('VKORC1', 0.5)]:
        if g in _GENES:
            gv[_GENES.index(g)] = v

    print("\nLibellés de phénotype par catégorie de gène :")
    for g in ['CYP2C19', 'HLA-B', 'VKORC1', 'SLCO1B1', 'G6PD', 'IFNL3']:
        if g in _GENES:
            print(f"  {g:9s} ({GENE_CATEGORIE.get(g):14s}) "
                  f"valeur {gv[_GENES.index(g)]} -> "
                  f"{phenotype_libelle(g, gv[_GENES.index(g)])}")

    r = predict_drug_for_patient(gv, 'clopidogrel')
    print(f"\nclopidogrel -> {r['label']} ({r['confidence']} %)")
    print(f"  comparateur XGBoost : {r['label_xgboost']} "
          f"({r['confiance_xgboost']} %) — accord : {r['accord_dl_xgboost']}")

    tous = predict_all_drugs(gv)
    print(f"\n{len(tous)} médicaments non STANDARD sur {nb_medicaments()} du référentiel")
    for p in tous[:5]:
        print(f"  {p['action']:13s} {p['drug']:20s} {p['confidence']:5.1f} %")
