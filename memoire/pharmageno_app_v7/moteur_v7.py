#!/usr/bin/env python3
"""
moteur_v7.py : moteur de prédiction de l'application PharmaGeno (aucune interface ici : uniquement calcul + couche de sécurité).

Entrée  : un profil = {gène: valeur} pour les 12 gènes du modèle (valeur 0, 0.5, 1, 1.5 ou 2 ; None si le gène n'a pas pu être lu).
Sortie  : pour chacun des 76 médicaments, une prédiction du DL (moteur) et de XGBoost (second avis), plus un STATUT de sécurité.

Couche de sécurité (appliquée AVANT d'afficher une prédiction ; elle ne remplace jamais le modèle, elle l'empêche de parler hors de ce qu'il connaît) :
  - gène requis non lu            -> statut 'non_determine_gene'      (jamais remplacé par 1.0 : « normal » et « non lu » sont deux choses différentes)
  - combinaison jamais vue         -> statut 'hors_domaine'            (le modèle n'a pas appris cette situation ; voir domaine_v7.json)
  - DL et XGBoost en désaccord     -> statut 'desaccord'               (prédiction DL affichée, désaccord signalé)
  - médicament hors des 76         -> statut 'medicament_non_couvert'
  - gène de règle hors modèle      -> alerte (ex. HLA-B pour la phénytoïne : non évalué)
Les gènes non requis par un médicament mais non lus sont remplacés par 1.0 uniquement pour permettre le calcul (ils ne changent pas la décision : voir test_moteur_v7.py).
Le moteur DL est le modèle 'film_id' ; XGBoost est le modèle 'id' (modele_final_v7.py). Aucun des deux n'est ré-entraîné ici.
"""
import json, os
import numpy as np
import torch
from train_dl_v7b import PharmaGenoDL

ORDRE_GRAVITE = ['EVITER', 'ADAPTER_DOSE', 'SURVEILLER', 'STANDARD']


class MoteurPGx:
    def __init__(self, dossier_modeles, fichier_domaine, avec_xgb=True):
        d = torch.load(os.path.join(dossier_modeles, 'modele_final_v7_dl_film_id.pt'), map_location='cpu', weights_only=True)
        self.genes, self.classes, self.meds = d['genes'], d['classes'], d['medicaments']
        self.dl = PharmaGenoDL(d['n_genes'], d['fp_dim'], len(self.classes), d['arch'])
        self.dl.load_state_dict(d['state_dict']); self.dl.eval()
        self.mu = np.asarray(d['scaler_mean'], dtype=np.float32); self.sd = np.asarray(d['scaler_scale'], dtype=np.float32)
        self.xgb = None
        if avec_xgb:
            from xgboost import XGBClassifier
            meta = json.load(open(os.path.join(dossier_modeles, 'modele_final_v7_xgb_id_meta.json')))
            assert meta['genes'] == self.genes and meta['classes'] == self.classes and meta['medicaments'] == self.meds, 'DL et XGBoost n\'ont pas les mêmes gènes / classes / médicaments'
            self.xgb = XGBClassifier(); self.xgb.load_model(os.path.join(dossier_modeles, 'modele_final_v7_xgb_id.json'))
        dom = json.load(open(fichier_domaine))
        assert dom['genes_modele'] == self.genes, 'domaine_v7.json ne correspond pas aux gènes du modèle'
        self.dom = dom['medicaments']
        self._idx = {m: i for i, m in enumerate(self.meds)}
        self._seen = {m: {tuple(c) for c in v['combos_vues']} for m, v in self.dom.items()}

    # ---- calcul brut (sans couche de sécurité) : sert aux tests et à predire() ----
    def probas(self, G, noms_med):
        """G : (n, 12) valeurs brutes dans l'ordre self.genes ; noms_med : n noms. Retourne (P_dl, P_xgb) de forme (n, 4)."""
        G = np.asarray(G, dtype=np.float32); n = len(G)
        ID = np.eye(len(self.meds), dtype=np.float32)[[self._idx[m] for m in noms_med]]
        with torch.no_grad():
            P = torch.softmax(self.dl(torch.from_numpy((G - self.mu) / self.sd), torch.from_numpy(ID)), 1).numpy()
        Px = self.xgb.predict_proba(np.hstack([G, ID])) if self.xgb is not None else None
        return P, Px

    def predire(self, profil, medicaments=None):
        """profil : {gène: valeur ou None}. Retourne une liste de dictionnaires (un par médicament demandé, défaut : les 76)."""
        inconnus_profil = sorted(set(profil) - set(self.genes))
        meds = list(medicaments) if medicaments else list(self.meds)
        res, lignes = {}, []
        for m in meds:
            if m not in self._idx:
                res[m] = dict(medicament=m, statut='medicament_non_couvert',
                              message="Pas de recommandation pharmacogénétique disponible pour ce médicament dans PharmaGeno."); continue
            dm = self.dom[m]; req = dm['genes']
            valeurs = {g: profil.get(g) for g in self.genes}
            manq = [g for g in req if valeurs[g] is None or (isinstance(valeurs[g], float) and np.isnan(valeurs[g]))]
            base = dict(medicament=m, genes_requis=req, genes_regle_hors_modele=dm['genes_regle_hors_modele'])
            if manq:
                res[m] = dict(base, statut='non_determine_gene', genes_manquants=manq,
                              message='Gène(s) non déterminé(s) : %s.' % ', '.join(manq)); continue
            combo = tuple(float(valeurs[g]) for g in req)
            if combo not in self._seen[m]:
                res[m] = dict(base, statut='hors_domaine', combinaison={g: float(valeurs[g]) for g in req},
                              regles_non_apprises=dm['regles_non_vues'],
                              message="Combinaison génétique que le modèle n'a jamais rencontrée pour ce médicament : pas de prédiction."); continue
            res[m] = base; lignes.append(m)
        if lignes:
            G = np.array([[1.0 if profil.get(g) is None else float(profil[g]) for g in self.genes]] * len(lignes), dtype=np.float32)
            P, Px = self.probas(G, lignes)
            for i, m in enumerate(lignes):
                a_dl = self.classes[int(P[i].argmax())]
                r = res[m]; r.update(action=a_dl, proba_dl={c: round(float(p), 4) for c, p in zip(self.classes, P[i])}, statut='ok')
                imput = [g for g in self.genes if profil.get(g) is None]
                if imput: r['genes_remplaces_par_1_0_pour_le_calcul'] = imput
                if Px is not None:
                    a_x = self.classes[int(Px[i].argmax())]
                    r.update(action_xgboost=a_x, proba_xgboost={c: round(float(p), 4) for c, p in zip(self.classes, Px[i])})
                    if a_x != a_dl:
                        r['statut'] = 'desaccord'
                        r['message'] = 'Le DL (%s) et XGBoost (%s) ne sont pas d\'accord : à vérifier par un professionnel.' % (a_dl, a_x)
        out = [res[m] for m in meds]
        if inconnus_profil:
            for r in out: r['avertissement_profil'] = 'gènes ignorés (hors modèle) : %s' % ', '.join(inconnus_profil)
        return out
