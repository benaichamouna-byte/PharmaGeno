#!/usr/bin/env python3
"""
moteur_v8.py : moteur de l'application PharmaGeno v8 (calcul + couche de sécurité ; aucune interface). moteur_v7.py reste intact.

Rôle de chaque composant :
  - DL (film, identifiant de médicament)  = MOTEUR : c'est lui qui produit la recommandation affichée ;
  - XGBoost                               = second avis ;
  - Référence CPIC/DPWG (regle_cpic_v8)   = référence affichée à côté, avec sa source ; jamais utilisée pour calculer la prédiction du DL ;
  - Couche de sécurité                    = empêche le modèle de parler hors de ce qu'il a appris.

Statuts (champ 'statut') :
  ok                      : DL, XGBoost et référence CPIC concordent, confiance du DL au-dessus du seuil d'abstention
  a_verifier              : au moins une alerte (voir 'alertes') : 'incertain' (confiance du DL <= seuil d'abstention), 'desaccord_xgboost', 'desaccord_cpic'
  non_determine_gene      : un gène requis n'a pas pu être lu et ce cas n'a jamais été vu à l'entraînement -> pas de prédiction DL
  hors_domaine            : combinaison de valeurs jamais vue pour ce médicament -> pas de prédiction DL
  dl_indisponible         : médicament sans empreinte (pas d'entrée dans le DL) ; référence CPIC seule
  medicament_non_couvert  : médicament inconnu de PharmaGeno
Une valeur manquante n'est JAMAIS remplacée par « normal » pour un gène requis. Pour un gène non requis sans indicateur d'absence dans le modèle,
une valeur neutre est utilisée uniquement pour le calcul (et listée) ; test_moteur_v8.py mesure que cela ne change pas la décision.
Abstention : seuil de confiance fixé sur les probabilités hors-plis de la validation croisée (abstention_seuils_v8.json), jamais sur l'ensemble final.
"""
import json, math, os
import numpy as np
import torch
from train_dl_v9_graines import PharmaGenoDL
from regle_cpic_v8 import RegleCPIC

ORDRE_GRAVITE = ['EVITER', 'ADAPTER_DOSE', 'SURVEILLER', 'STANDARD']


def _manquant(v):
    return v is None or (isinstance(v, float) and math.isnan(v))


class MoteurPGx:
    def __init__(self, dossier_modeles, fichier_domaine, fichier_mono, fichier_multi, niveau_abstention='0.010', avec_xgb=True):
        d = torch.load(os.path.join(dossier_modeles, 'modele_final_v8_dl_film_id.pt'), map_location='cpu', weights_only=True)
        self.features, self.classes, self.meds = d['genes'], d['classes'], d['medicaments']
        self.dl = PharmaGenoDL(d['n_genes'], d['fp_dim'], len(self.classes), d['arch']); self.dl.load_state_dict(d['state_dict']); self.dl.eval()
        self.mu = np.asarray(d['scaler_mean'], dtype=np.float32); self.sd = np.asarray(d['scaler_scale'], dtype=np.float32)
        self.xgb = None
        if avec_xgb:
            from xgboost import XGBClassifier
            meta = json.load(open(os.path.join(dossier_modeles, 'modele_final_v8_xgb_id_meta.json')))
            assert meta['genes'] == self.features and meta['classes'] == self.classes and meta['medicaments'] == self.meds, "DL et XGBoost n'ont pas les mêmes variables / classes / médicaments"
            self.xgb = XGBClassifier(); self.xgb.load_model(os.path.join(dossier_modeles, 'modele_final_v8_xgb_id.json'))
        dom = json.load(open(fichier_domaine, encoding='utf-8'))
        assert dom['genes_modele'] == [g for g in self.features if not g.endswith('_manquant')], 'domaine_v8.json ne correspond pas aux variables du modèle'
        self.dom, self.genes_profil, self.genes_modele = dom['medicaments'], dom['genes_profil'], dom['genes_modele']
        self._seen = {m: {tuple(c) for c in v['combos_vues']} for m, v in self.dom.items()}
        self._idx = {m: i for i, m in enumerate(self.meds)}
        seuils = json.load(open(os.path.join(dossier_modeles, 'abstention_seuils_v8.json')))['seuils_confiance']
        assert niveau_abstention in seuils, 'niveaux disponibles : %s' % list(seuils)
        self.niveau_abstention, self.seuil = niveau_abstention, float(seuils[niveau_abstention])
        self.cpic = RegleCPIC(fichier_mono, fichier_multi, self.genes_profil)
        self._avec_indic = {g for g in self.genes_modele if g + '_manquant' in self.features}

    # ---- variables du modèle à partir d'un profil (reproduit protocole_commun_v8.charger) ----
    def vecteur(self, profil):
        v, remplaces = [], []
        for f in self.features:
            if f.endswith('_manquant'):
                v.append(1.0 if _manquant(profil.get(f[:-len('_manquant')])) else 0.0)
            elif _manquant(profil.get(f)):
                if f in self._avec_indic: v.append(0.0)                      # comme à l'entraînement : 0 + indicateur d'absence = 1
                else: v.append(0.0 if f.startswith('HLA-') else 1.0); remplaces.append(f)   # pas d'indicateur appris : valeur neutre, listée
            else:
                v.append(float(profil[f]))
        return np.asarray(v, dtype=np.float32), remplaces

    def probas(self, G, noms_med):
        """G : (n, n_variables) brutes dans l'ordre self.features. Retourne (P_dl, P_xgb) (n, 4)."""
        G = np.asarray(G, dtype=np.float32); ID = np.eye(len(self.meds), dtype=np.float32)[[self._idx[m] for m in noms_med]]
        with torch.no_grad():
            P = torch.softmax(self.dl(torch.from_numpy((G - self.mu) / self.sd), torch.from_numpy(ID)), 1).numpy()
        return P, (self.xgb.predict_proba(np.hstack([G, ID])) if self.xgb is not None else None)

    def predire(self, profil, medicaments=None):
        meds = list(medicaments) if medicaments else sorted(self.dom)
        ignores = sorted(set(profil) - set(self.genes_profil))
        res, lignes = {}, []
        for m in meds:
            if m not in self.dom:
                res[m] = dict(medicament=m, statut='medicament_non_couvert', alertes=[], message="Pas de recommandation pharmacogénétique disponible pour ce médicament dans PharmaGeno."); continue
            dm = self.dom[m]; req = dm['genes']
            combo = tuple(None if _manquant(profil.get(g)) else float(profil[g]) for g in req)
            ref = self.cpic.appliquer(profil, m)
            base = dict(medicament=m, alertes=[], genes_requis=req, valeurs_requises=dict(zip(req, combo)),
                        genes_requis_hors_modele=dm['genes_requis_hors_modele'], genes_regle_hors_profil=dm['genes_regle_hors_profil'],
                        action_cpic=ref['action'], regle_cpic=ref['regles'], confiance_regle_cpic=ref.get('confiance', ''))
            if ref['action'] is None: base['raison_pas_de_regle_cpic'] = ref.get('raison', '')
            if not dm['dans_modele']:
                res[m] = dict(base, statut='dl_indisponible', message="Ce médicament n'a pas d'entrée dans le modèle d'apprentissage : seule la règle de guideline est affichée."); continue
            manq = [g for g, c in zip(req, combo) if c is None]
            if combo not in self._seen[m]:
                if manq:
                    res[m] = dict(base, statut='non_determine_gene', genes_manquants=manq, message='Gène(s) non déterminé(s) : %s. Pas de prédiction du modèle.' % ', '.join(manq))
                else:
                    res[m] = dict(base, statut='hors_domaine', message="Combinaison génétique jamais rencontrée à l'entraînement pour ce médicament : pas de prédiction du modèle.")
                continue
            res[m] = base; lignes.append(m)
        if lignes:
            vec, remplaces = self.vecteur(profil)
            P, Px = self.probas(np.tile(vec, (len(lignes), 1)), lignes)
            for i, m in enumerate(lignes):
                r = res[m]; a_dl = self.classes[int(P[i].argmax())]; conf = float(P[i].max())
                r.update(action_dl=a_dl, confiance_dl=round(conf, 4), proba_dl={c: round(float(p), 4) for c, p in zip(self.classes, P[i])})
                if remplaces: r['variables_remplacees_pour_le_calcul'] = remplaces
                if conf <= self.seuil: r['alertes'].append('incertain')
                if Px is not None:
                    a_x = self.classes[int(Px[i].argmax())]
                    r.update(action_xgboost=a_x, proba_xgboost={c: round(float(p), 4) for c, p in zip(self.classes, Px[i])})
                    if a_x != a_dl: r['alertes'].append('desaccord_xgboost')
                if r['action_cpic'] is not None and r['action_cpic'] != a_dl: r['alertes'].append('desaccord_cpic')
                r['statut'] = 'a_verifier' if r['alertes'] else 'ok'
        out = [res[m] for m in meds]
        if ignores:
            for r in out: r['avertissement_profil'] = 'gènes ignorés (hors modèle) : %s' % ', '.join(ignores)
        return out
