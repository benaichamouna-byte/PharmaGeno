# moteur_v9i.py = copie de moteur_v8i.py (reste intact) branchée sur moteur_v9g ; modèle de choix modele_final_choix_v2.pt (corpus v8, 23 oct. 2026).
#!/usr/bin/env python3
"""
moteur_v8i.py : moteur de l'application PharmaGeno v8i = moteur_v8g.MoteurPGxProfilG + le DL « CHOIX du médicament » (train_dl_choix_v1.py / modele_final_choix_v1.py).

choix(profil, code_classe) : le réseau reçoit le profil complet et produit un score par médicament ; dans la classe thérapeutique demandée (ATC niveau 4, OMS), un softmax sur les médicaments
EVALUABLES pour ce patient (la couche de sécurité de moteur_v8 écarte les médicaments dont un gène requis n'est pas lu ou dont la combinaison de gènes n'a jamais été apprise) donne la probabilité de choix.
Ensemble prédit = médicaments dont la probabilité est >= 0,5 x la meilleure (règle fixée avant la mesure, identique à train_dl_choix_v1.py). Il ne départage pas les médicaments équivalents :
aucune guideline ne dit lequel est « le meilleur », la cible d'entraînement est une loi uniforme sur les médicaments acceptables (convention écrite dans la thèse).
genes_decisifs_choix : analyse de sensibilité (un gène remplacé par la valeur normale, le reste du profil inchangé) : description du comportement du réseau, pas une preuve de causalité.
"""
import os
import numpy as np
import torch
from moteur_v9g import MoteurPGxProfilG
from train_dl_choix_v2 import DLChoix, log_choix

SEUIL_RELATIF = 0.5


class MoteurPGxChoix(MoteurPGxProfilG):
    def __init__(self, dossier_modeles, dossier_choix, fichier_domaine, fichier_mono, fichier_multi, niveau_abstention='0.010', dossier_xgb=None):
        super().__init__(dossier_modeles, fichier_domaine, fichier_mono, fichier_multi, niveau_abstention, dossier_xgb)
        d = torch.load(os.path.join(dossier_choix, 'modele_final_choix_v2.pt'), map_location='cpu', weights_only=True)
        assert d['arch'] == 'choix_v1', 'modèle de choix inattendu : %s' % d['arch']
        assert d['genes'] == self.features and d['medicaments'] == self.meds and d['classes'] == self.classes, 'le modèle de choix et le modèle profil ne partagent pas les mêmes variables / médicaments / classes'
        # le réseau n'a une sortie que pour les médicaments appartenant à au moins une classe (indices < n_sortie) : la taille est lue dans les poids enregistrés
        n_sortie = int(d['state_dict']['sortie.weight'].shape[0]); assert all(self._idx[m] < n_sortie for c in d['classes_choix'] for m in c['medicaments'])
        self.dlc = DLChoix(d['n_in'], n_sortie, d['h'], d['p']); self.dlc.load_state_dict(d['state_dict']); self.dlc.eval()
        self.mu_c = np.asarray(d['scaler_mean'], dtype=np.float32); self.sd_c = np.asarray(d['scaler_scale'], dtype=np.float32)
        self.classes_choix = {c['code']: c for c in d['classes_choix']}

    def _probas_choix(self, V, meds_classe, cand):
        """V (n, n_variables) ; cand : liste de médicaments candidats parmi meds_classe. Retourne probabilités (n, len(meds_classe)) ; 0 hors candidats."""
        with torch.no_grad(): S = self.dlc(torch.from_numpy(((np.asarray(V, dtype=np.float32) - self.mu_c) / self.sd_c).astype(np.float32)))
        idx = torch.tensor([[self._idx[m] for m in meds_classe]]); ok = torch.tensor([[m in cand for m in meds_classe]]).repeat(len(S), 1)[:, None, :]
        return log_choix(S, idx, ok)[:, 0, :].exp().numpy()

    def choix(self, profil, code, res=None):
        """Retourne dict(code, nom, candidats=[dict(medicament, proba_choix, dans_ensemble)] trié par probabilité, ensemble=[médicaments], non_evalues=[(médicament, statut, message)])."""
        c = self.classes_choix[code]; ms = c['medicaments']
        res = res if res is not None else self.predire(profil, ms); par = {r['medicament']: r for r in res if r['medicament'] in ms}
        cand = [m for m in ms if 'action_dl' in par.get(m, {})]; non = [(m, par[m]['statut'], par[m].get('message', '')) for m in ms if m not in cand]
        out = dict(code=code, nom=c['nom'], candidats=[], ensemble=[], non_evalues=non)
        if len(cand) < 2: out['motif'] = "Moins de 2 médicaments de cette classe sont évaluables pour ce profil : pas de choix possible."; return out
        vec, _ = self.vecteur(profil); p = self._probas_choix(vec[None, :], ms, cand)[0]; pmax = max(p)
        for m, pm in sorted(zip(ms, p), key=lambda t: -t[1]):
            if m in cand: out['candidats'].append(dict(medicament=m, proba_choix=float(pm), dans_ensemble=bool(pm >= SEUIL_RELATIF * pmax)))
        out['ensemble'] = [d['medicament'] for d in out['candidats'] if d['dans_ensemble']]
        return out

    def genes_decisifs_choix(self, profil, code, res=None):
        """Gènes lus (valeur non normale) dont le remplacement par la valeur normale change l'ensemble prédit. Liste de dict(gene, ensemble_si_normal, retires, ajoutes)."""
        base = self.choix(profil, code, res)
        if not base['ensemble']: return []
        c = self.classes_choix[code]; ms = c['medicaments']; cand = [d['medicament'] for d in base['candidats']]
        vec, _ = self.vecteur(profil); dec = []
        for g in self.genes_modele:
            v = profil.get(g)
            if v is None or (isinstance(v, float) and v != v): continue
            i = self.features.index(g)
            if float(vec[i]) == self._normal(g): continue
            w = vec.copy(); w[i] = self._normal(g); p = self._probas_choix(w[None, :], ms, cand)[0]; pm = max(p)
            ens = [m for m, x in zip(ms, p) if m in cand and x >= SEUIL_RELATIF * pm]
            if set(ens) != set(base['ensemble']):
                dec.append(dict(gene=g, ensemble_si_normal=ens, retires=[m for m in base['ensemble'] if m not in ens], ajoutes=[m for m in ens if m not in base['ensemble']]))
        return dec
