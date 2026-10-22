#!/usr/bin/env python3
"""
moteur_v8f.py : moteur de l'application PharmaGeno v8f. moteur_v8.py reste intact.

Différence avec moteur_v8.py : le DL est le modèle « profil génétique -> conseil pour chaque médicament » (train_dl_profil_v1.py / modele_final_profil_v1.py) :
le profil est la SEULE entrée, un passage du réseau donne les 113 médicaments d'un coup (113 x 4 classes). Le médicament n'est plus une entrée.
Tout le reste est repris de moteur_v8.py sans changement : statuts, couche de sécurité (« hors domaine », gène requis non lu), abstention, règle CPIC/DPWG affichée à côté
(jamais utilisée pour calculer la prédiction), second avis XGBoost (ancien modèle, facultatif : dossier_xgb).
Fichiers lus dans dossier_modeles : modele_final_profil_v1.pt, abstention_seuils_profil_v1.json.
"""
import json, os
import numpy as np
import torch
from moteur_v8 import MoteurPGx
from regle_cpic_v8 import RegleCPIC
from train_dl_profil_v1 import DLProfil


class MoteurPGxProfil(MoteurPGx):
    def __init__(self, dossier_modeles, fichier_domaine, fichier_mono, fichier_multi, niveau_abstention='0.010', dossier_xgb=None):
        d = torch.load(os.path.join(dossier_modeles, 'modele_final_profil_v1.pt'), map_location='cpu', weights_only=True)
        assert d['arch'] == 'profil_v1', 'modèle inattendu : %s' % d['arch']
        self.features, self.classes, self.meds = d['genes'], d['classes'], d['medicaments']
        self.dl = DLProfil(d['n_in'], d['n_med'], d['K'], d['h'], d['p']); self.dl.load_state_dict(d['state_dict']); self.dl.eval()
        assert d['n_in'] == len(self.features) and d['n_med'] == len(self.meds) and d['K'] == len(self.classes)
        self.mu = np.asarray(d['scaler_mean'], dtype=np.float32); self.sd = np.asarray(d['scaler_scale'], dtype=np.float32)
        self.xgb = None
        if dossier_xgb:
            from xgboost import XGBClassifier
            meta = json.load(open(os.path.join(dossier_xgb, 'modele_final_v8_xgb_id_meta.json')))
            assert meta['genes'] == self.features and meta['classes'] == self.classes and meta['medicaments'] == self.meds, "DL et XGBoost n'ont pas les mêmes variables / classes / médicaments"
            self.xgb = XGBClassifier(); self.xgb.load_model(os.path.join(dossier_xgb, 'modele_final_v8_xgb_id.json'))
        dom = json.load(open(fichier_domaine, encoding='utf-8'))
        assert dom['genes_modele'] == [g for g in self.features if not g.endswith('_manquant')], 'domaine_v8.json ne correspond pas aux variables du modèle'
        self.dom, self.genes_profil, self.genes_modele = dom['medicaments'], dom['genes_profil'], dom['genes_modele']
        self._seen = {m: {tuple(c) for c in v['combos_vues']} for m, v in self.dom.items()}
        self._idx = {m: i for i, m in enumerate(self.meds)}
        seuils = json.load(open(os.path.join(dossier_modeles, 'abstention_seuils_profil_v1.json')))['seuils_confiance']
        assert niveau_abstention in seuils, 'niveaux disponibles : %s' % list(seuils)
        self.niveau_abstention, self.seuil = niveau_abstention, float(seuils[niveau_abstention])
        self.cpic = RegleCPIC(fichier_mono, fichier_multi, self.genes_profil)
        self._avec_indic = {g for g in self.genes_modele if g + '_manquant' in self.features}

    def probas_toutes(self, G):
        """G : (n, n_variables) brutes dans l'ordre self.features. Retourne (n, n_medicaments, n_classes) : tous les médicaments en un passage."""
        G = np.asarray(G, dtype=np.float32)
        with torch.no_grad():
            return torch.softmax(self.dl(torch.from_numpy((G - self.mu) / self.sd)), -1).numpy()

    def probas(self, G, noms_med):
        """Même interface que MoteurPGx.probas : ligne i = profil G[i] et médicament noms_med[i]. Retourne (P_dl, P_xgb) de forme (n, 4)."""
        G = np.asarray(G, dtype=np.float32); Pall = self.probas_toutes(G)
        P = Pall[np.arange(len(G)), [self._idx[m] for m in noms_med]]
        Px = None
        if self.xgb is not None:
            ID = np.eye(len(self.meds), dtype=np.float32)[[self._idx[m] for m in noms_med]]
            Px = self.xgb.predict_proba(np.hstack([G, ID]))
        return P, Px
