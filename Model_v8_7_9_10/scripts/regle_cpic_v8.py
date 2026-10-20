#!/usr/bin/env python3
"""
regle_cpic_v8.py : RÉFÉRENCE CPIC/DPWG de l'application v8 (ce n'est PAS le moteur de recommandation : le moteur est le DL).
Rôle : pour un profil et un médicament, retrouver l'action que les règles de guidelines donnent, avec le texte de la recommandation et sa source,
afin de l'AFFICHER à côté de la prédiction du DL et de signaler un désaccord.

Même logique que le moteur d'étiquetage du corpus (construire_corpus_v3.py, non modifié ; ses constantes sont importées, pas recopiées) :
  - règles utilisables : non ambiguës, non conditionnelles (sauf CONDITIONNELS_ACCEPTES), codage vérifié, sans conflit interne ;
  - une règle multi-gènes qui correspond remplace les règles mono-gène de ses deux gènes ;
  - action finale = la plus sévère (EVITER > ADAPTER_DOSE > SURVEILLER > STANDARD) ;
  - un gène du médicament dont la valeur n'a pas de règle (ou est manquante), sans EVITER établi -> pas d'action (None) : on n'invente rien.
Le test test_moteur_v8.py vérifie que cette classe redonne EXACTEMENT les étiquettes du corpus v7 (130 578 lignes).
"""
import math
import pandas as pd
import construire_corpus_v3 as eng

SEVERITE, INV = eng.SEVERITE, eng.INV


def _nan(v):
    return v is None or (isinstance(v, float) and math.isnan(v))


class RegleCPIC:
    def __init__(self, fichier_mono, fichier_multi, genes_profil):
        mono = pd.read_csv(fichier_mono); multi = pd.read_csv(fichier_multi)
        for t in (mono, multi): t['medicament'] = t['medicament'].str.lower().str.strip()
        self.genes_profil = list(genes_profil)
        acc = pd.Series([(r.medicament, r.gene, float(r.valeur)) in eng.CONDITIONNELS_ACCEPTES for r in mono.itertuples()], index=mono.index)
        b = eng.b
        mono_u = mono[(~b(mono.ambigu)) & ((~b(mono.conditionnel)) | acc) & (~b(mono.codage_a_valider)) & b(mono.gene_dans_les_31) & (~b(mono.conflit_intra_source))]
        multi_u = multi[(~b(multi.ambigu)) & (~b(multi.conditionnel)) & (~b(multi.conflit_intra_source))]
        multi_u = multi_u[multi_u.gene_a.isin(self.genes_profil) & multi_u.gene_b.isin(self.genes_profil)
                          & ~multi_u.gene_a.isin(eng.GENES_CODAGE_A_VALIDER) & ~multi_u.gene_b.isin(eng.GENES_CODAGE_A_VALIDER)]
        self.R1, self.G1, self.R2, self.M2 = {}, {}, {}, {}
        for r in mono_u.itertuples(index=False):
            self.R1[(r.medicament, r.gene, float(r.valeur))] = dict(action=r.action, desaccord=isinstance(r.desaccord_autres_sources, str),
                                                                    texte=str(r.recommandation), phenotype=str(r.phenotype), source=str(r.source), fichier=str(r.fichier))
            self.G1.setdefault(r.medicament, set()).add(r.gene)
        for r in multi_u.itertuples(index=False):
            self.R2[(r.medicament, r.gene_a, float(r.valeur_a), r.gene_b, float(r.valeur_b))] = dict(
                action=r.action, desaccord=isinstance(r.desaccord_autres_sources, str), texte=str(r.recommandation),
                phenotype='%s ; %s' % (r.phenotype_a, r.phenotype_b), source=str(r.source), fichier=str(r.fichier))
            self.M2.setdefault(r.medicament, set()).add((r.gene_a, r.gene_b))
        self.medicaments = sorted(set(self.G1) | set(self.M2))
        # tous les gènes cités par des règles (utilisables ou non) : pour signaler un gène de règle que le modèle ne reçoit pas
        self.genes_toutes_regles = {}
        for m, g in zip(mono.medicament, mono.gene): self.genes_toutes_regles.setdefault(m, set()).add(g)
        for m, ga, gb in zip(multi.medicament, multi.gene_a, multi.gene_b): self.genes_toutes_regles.setdefault(m, set()).update([ga, gb])

    def genes_du_medicament(self, med):
        """gènes dont les règles utilisables concernent ce médicament"""
        g = set(self.G1.get(med, ()))
        for ga, gb in self.M2.get(med, ()): g |= {ga, gb}
        return sorted(g)

    def appliquer(self, profil, med):
        """profil : {gène: valeur ou None}. Retourne dict(action ou None, regles utilisées, confiance, raison si None)."""
        d = med.lower().strip()
        if d not in self.G1 and d not in self.M2:
            return dict(action=None, regles=[], raison='aucune règle utilisable pour ce médicament')
        val = {g: (float('nan') if _nan(profil.get(g)) else float(profil[g])) for g in self.genes_profil}
        actions, regles, couverts, desacc = [], [], set(), False
        for (ga, gb) in sorted(self.M2.get(d, ())):
            k = (d, ga, val[ga], gb, val[gb])
            if k in self.R2:
                r = self.R2[k]; actions.append(r['action']); desacc |= r['desaccord']; couverts |= {ga, gb}
                regles.append(dict(genes=[ga, gb], valeurs=[val[ga], val[gb]], **r))
        inconnu = []
        for g in sorted(self.G1.get(d, ())):
            if g in couverts: continue
            k = (d, g, val[g])
            if k in self.R1:
                r = self.R1[k]; actions.append(r['action']); desacc |= r['desaccord']
                regles.append(dict(genes=[g], valeurs=[val[g]], **r))
            else:
                inconnu.append((g, None if math.isnan(val[g]) else val[g]))
        if actions and max(SEVERITE[a] for a in actions) == 3:
            fin = 'EVITER'
        elif inconnu or not actions:
            fin = None
        else:
            fin = INV[max(SEVERITE[a] for a in actions)]
        out = dict(action=fin, regles=regles, confiance=('moyenne' if desacc else 'haute') if fin else '')
        if fin is None:
            out['raison'] = 'gène manquant ou valeur sans règle : %s' % ', '.join('%s=%s' % (g, v) for g, v in inconnu) if inconnu else 'aucune règle applicable'
        return out
