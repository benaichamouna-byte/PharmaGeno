# moteur_v10j.py (3 nov. 2026) = moteur_v10i.py (INTACT) + avis Random Forest INFORMATIF (modele_final_rf_v3.py, dossier modeles_v10rf).
# L'avis Random Forest (action_rf, proba_rf) est ajouté APRÈS le calcul du moteur : il ne crée aucune alerte et ne change aucun statut ; il sert à comparer le DL, XGBoost, le Random Forest et la règle.
import json, os
import numpy as np
from moteur_v10i import MoteurPGxChoix as _Base


class MoteurPGxChoix(_Base):
    def __init__(self, dossier_modeles, dossier_choix, fichier_domaine, fichier_mono, fichier_multi, niveau_abstention='0.010', dossier_xgb=None, dossier_rf=None):
        super().__init__(dossier_modeles, dossier_choix, fichier_domaine, fichier_mono, fichier_multi, niveau_abstention, dossier_xgb)
        self.rf = None
        if dossier_rf:
            import joblib
            meta = json.load(open(os.path.join(dossier_rf, 'modele_final_rf_meta.json'), encoding='utf-8'))
            assert meta['genes'] == self.features and meta['classes'] == self.classes and meta['medicaments'] == self.meds, "DL et Random Forest n'ont pas les mêmes variables / classes / médicaments"
            self.rf = joblib.load(os.path.join(dossier_rf, 'modele_final_rf.joblib'))

    def predire(self, profil, medicaments=None):
        out = super().predire(profil, medicaments)
        if self.rf is None: return out
        ev = [r for r in out if 'action_dl' in r]
        if ev:
            vec, _ = self.vecteur(profil)
            G = np.tile(np.asarray(vec, dtype=np.float32), (len(ev), 1))
            ID = np.eye(len(self.meds), dtype=np.float32)[[self._idx[r['medicament']] for r in ev]]
            P = np.zeros((len(ev), len(self.classes)), dtype=np.float32); P[:, self.rf.classes_.astype(int)] = self.rf.predict_proba(np.hstack([G, ID]))
            for r, p in zip(ev, P):
                r['action_rf'] = self.classes[int(p.argmax())]; r['proba_rf'] = {c: round(float(x), 4) for c, x in zip(self.classes, p)}
        return out
