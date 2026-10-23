# moteur_v9g.py = copie de moteur_v8g.py (reste intact) branchée sur moteur_v9f.
#!/usr/bin/env python3
"""
moteur_v8g.py : moteur de l'application PharmaGeno v8g = moteur_v8f.MoteurPGxProfil + deux fonctions qui rendent visible ce que fait le DL « profil -> médicaments » :
  - sortie_complete(profil)        : ce que le réseau produit en UN passage pour TOUS les médicaments (avant la couche de sécurité) ;
  - genes_decisifs(profil, med)    : analyse de sensibilité du réseau : quels gènes du patient font changer sa prédiction pour ce médicament.
moteur_v8.py et moteur_v8f.py restent intacts.

Méthode de genes_decisifs (analyse de sensibilité par substitution, sans réentraînement) : pour chaque gène lu du patient dont la valeur n'est pas déjà « normale », on remplace UNIQUEMENT ce gène
par la valeur normale (phénotype « normal » = 1,0 ; HLA négatif = 0,0), tout le reste du profil inchangé, et on relit la sortie du réseau pour ce médicament. Si la classe prédite change, le gène est « décisif »
pour ce patient et ce médicament. Pour les médicaments qui dépendent de deux gènes, la substitution des deux gènes ensemble est aussi essayée (combinaison). C'est une description du comportement du modèle,
pas une preuve de causalité biologique.
"""
import numpy as np
from moteur_v9f import MoteurPGxProfil


class MoteurPGxProfilG(MoteurPGxProfil):
    def _normal(self, g):
        return 0.0 if g.startswith('HLA-') else 1.0

    def sortie_complete(self, profil):
        """Un passage du réseau pour le profil entier. Retourne dict(n_medicaments, comptes={classe: n}, actions={medicament: classe})."""
        vec, _ = self.vecteur(profil)
        P = self.probas_toutes(vec[None, :])[0]                       # (n_medicaments, n_classes)
        act = P.argmax(1)
        comptes = {c: int((act == k).sum()) for k, c in enumerate(self.classes)}
        return dict(n_medicaments=len(self.meds), comptes=comptes, actions={m: self.classes[int(act[i])] for i, m in enumerate(self.meds)})

    def genes_decisifs(self, profil, medicament):
        """Liste triée de dicts(genes, action_si_normal, proba_si_normal, proba_actuelle) pour les substitutions qui changent la classe prédite. [] si aucune."""
        if medicament not in self._idx: return []
        vec, _ = self.vecteur(profil); j = self._idx[medicament]
        candidats = []                                                 # gènes lus, pas déjà à la valeur normale
        for g in self.genes_modele:
            v = profil.get(g)
            if v is None or (isinstance(v, float) and v != v): continue
            i = self.features.index(g)
            if float(vec[i]) != self._normal(g): candidats.append((g, i))
        variantes = [((g,), [i]) for g, i in candidats]
        req = [g for g in self.dom[medicament]['genes'] if g in {c[0] for c in candidats}]
        if len(req) == 2: variantes.append((tuple(req), [self.features.index(g) for g in req]))
        if not variantes: return []
        V = np.tile(vec, (len(variantes) + 1, 1))
        for r, (gs, ix) in enumerate(variantes, start=1):
            for g, i in zip(gs, ix): V[r, i] = self._normal(g)
        P = self.probas_toutes(V)[:, j, :]; base = int(P[0].argmax()); sorties = []
        for r, (gs, _) in enumerate(variantes, start=1):
            a = int(P[r].argmax())
            if a != base: sorties.append(dict(genes=list(gs), action_si_normal=self.classes[a], proba_si_normal=round(float(P[r, a]), 4), proba_actuelle=round(float(P[0, base]), 4)))
        sorties.sort(key=lambda d: (len(d['genes']), -d['proba_si_normal']))
        return sorties
