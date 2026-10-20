#!/usr/bin/env python3
"""
recommandation_v8.py : couche de recommandation de l'application PharmaGeno v8 (logique pure, sans interface). recommandation_v7.py reste intact.
Entrée : la sortie de moteur_v8.MoteurPGx.predire(profil) + une spécialité. Sortie : un dictionnaire pour la page de résultats et le PDF.

Principes (le DL est le moteur ; rien n'est recalculé ici) :
  - « Proposés » (<= 4) = médicaments de la spécialité dont le statut est « ok » (DL, XGBoost et règle CPIC concordent, confiance du DL au-dessus du seuil d'abstention)
    et dont l'action n'est pas EVITER. Compatibilité PHARMACOGÉNÉTIQUE uniquement : ce n'est pas une prescription (indication, interactions, contre-indications non évaluées).
  - « À éviter » = DL, XGBoost OU règle CPIC donne EVITER (un seul avis suffit à le signaler : prudence).
  - « À vérifier » = au moins une alerte (confiance faible du DL, désaccord XGBoost, désaccord avec la règle CPIC) sans avis EVITER.
  - « Non évalués » = gène requis non déterminé, combinaison jamais vue : jamais proposés, jamais classés comme normaux.
  - « Référence de guideline seule » = médicaments sans entrée dans le DL (pas de prédiction DL) ; la règle de guideline est affichée, sans classement.
  - Chaque fiche affiche la règle CPIC/DPWG correspondante (phénotype, texte de la guideline en anglais, source) : le texte n'est pas traduit pour ne pas le déformer.
  - Alternatives d'un médicament à éviter : même sous-groupe ATC (4e niveau) ET statut « ok » avec action STANDARD pour ce patient ; équivalence clinique NON affirmée.
  - La lecture d'un gène (« activité réduite »…) vient du phénotype de la règle appliquée ; sans règle, la valeur brute de codage est affichée, sans interprétation.
"""
import pandas as pd

ORDRE_PROPOSITION = {'STANDARD': 0, 'SURVEILLER': 1, 'ADAPTER_DOSE': 2}
LIBELLE_PRO = {
    'EVITER': 'À éviter pour ce profil génétique',
    'ADAPTER_DOSE': 'Adaptation de dose à envisager',
    'SURVEILLER': 'Surveillance renforcée',
    'STANDARD': 'Aucune adaptation liée aux gènes analysés',
}
TEXTE_PATIENT = {
    'EVITER': "Vos gènes indiquent que ce médicament peut ne pas vous convenir. Ne le prenez pas sans en parler à votre médecin ou à votre pharmacien.",
    'ADAPTER_DOSE': "Vos gènes indiquent que la dose de ce médicament pourrait devoir être ajustée. Votre médecin ou votre pharmacien peut s'en charger ; ne modifiez pas vous-même votre traitement.",
    'SURVEILLER': "Vos gènes indiquent qu'un suivi plus attentif peut être utile avec ce médicament. Parlez-en à votre médecin.",
    'STANDARD': "Pour les gènes analysés, rien n'indique qu'il faille changer la manière habituelle de prendre ce médicament.",
    'A_VERIFIER': "Les analyses ne donnent pas une réponse assez sûre pour ce médicament : demandez l'avis de votre médecin ou de votre pharmacien.",
    'NON_EVALUE': "Ce médicament n'a pas pu être évalué pour votre profil. Cela ne veut pas dire qu'il vous convient : demandez l'avis de votre médecin ou de votre pharmacien.",
}
LIBELLE_ALERTE = {
    'incertain': "Confiance du modèle trop faible pour ce cas.",
    'desaccord_xgboost': "Le second modèle (XGBoost) ne donne pas la même réponse.",
    'desaccord_cpic': "La règle de guideline (CPIC/DPWG) ne donne pas la même réponse que le modèle.",
}
AVERTISSEMENT_GENERAL = ("Cet outil analyse un nombre limité de gènes et de médicaments ; il ne remplace ni l'avis d'un médecin ou d'un pharmacien, "
                         "ni une prescription. Il ne tient pas compte des autres médicaments, des maladies ni de l'âge. Résultat à discuter avec un professionnel de santé.")
FRANCAIS_VERS_INN = {'warfarine': 'warfarin', 'aspirine': 'aspirin', 'fluorouracile': 'fluorouracil', 'tamoxifene': 'tamoxifen', 'tamoxifène': 'tamoxifen',
                     'codeine': 'codeine', 'codéine': 'codeine', 'omeprazole': 'omeprazole', 'oméprazole': 'omeprazole'}   # liste à compléter (sources à fournir)


def _codes(s):
    return [c for c in str(s).split(';') if c and c != 'nan']


class Recommandeur:
    def __init__(self, atc_csv, specialites_csv, alternatives_csv, medicaments):
        self.meds = list(medicaments)
        a = pd.read_csv(atc_csv); self.atc = a[a.medicament.isin(self.meds)].set_index('medicament')
        s = pd.read_csv(specialites_csv); s = s[s.code_atc != 'TOTAL'].dropna(subset=['code_atc'])
        self.classes = {sp: sorted(set(g.code_atc)) for sp, g in s.groupby('specialite')}
        alt = pd.read_csv(alternatives_csv)
        self._noms = {m: m for m in self.meds}
        for m, r in self.atc.iterrows():
            for n in {m, str(r.principe_actif), str(r.nom_utilise_pour_la_recherche)}: self._noms[n.lower().strip()] = m
        self._noms.update({k: v for k, v in FRANCAIS_VERS_INN.items() if v in self.meds})

    def specialites(self):
        return sorted(self.classes)

    def medicaments_de_specialite(self, specialite):
        pref = tuple(self.classes[specialite])
        return [m for m in self.meds if m in self.atc.index and any(c.startswith(pref) for c in _codes(self.atc.loc[m, 'atc_codes']))]

    def _alternatives(self, med, par_med):
        out = []
        if med not in self.atc.index: return out
        classes4 = {c[:5] for c in _codes(self.atc.loc[med, 'atc_codes'])}
        for m2, r in self.atc.iterrows():
            if m2 == med or m2 not in par_med: continue
            if classes4 & {c[:5] for c in _codes(r.atc_codes)}:
                x = par_med[m2]
                if x['statut'] == 'ok' and x['action_dl'] == 'STANDARD': out.append(dict(medicament=m2, confiance=x['proba_dl']['STANDARD']))
        return sorted(out, key=lambda d: -d['confiance'])

    @staticmethod
    def _avis(r):
        return {k: v for k, v in (('DL', r.get('action_dl')), ('XGBoost', r.get('action_xgboost')), ('règle CPIC/DPWG', r.get('action_cpic'))) if v}

    @staticmethod
    def _explication(r):
        """une ligne par gène requis : valeur brute, lecture = phénotype de la règle appliquée (sinon valeur brute sans interprétation)"""
        lect = {}
        for reg in r.get('regle_cpic', []):
            for g in reg['genes']:
                if len(reg['genes']) == 1: lect[g] = reg['phenotype']
        out = []
        for g, v in r.get('valeurs_requises', {}).items():
            out.append(dict(gene=g, valeur_codage=v, lecture=lect.get(g) or ('non déterminé' if v is None else 'valeur de codage %s (sans règle associée à ce cas)' % v)))
        return out

    @staticmethod
    def _regle(r):
        return [dict(genes=x['genes'], phenotype=x['phenotype'], action=x['action'], texte_guideline_en=x['texte'], source=x['source'], fichier=x['fichier'],
                     autres_sources_en_desaccord=bool(x['desaccord'])) for x in r.get('regle_cpic', [])]

    def _fiche(self, r, par_med, categorie, texte_patient, libelle):
        f = dict(medicament=r['medicament'], categorie=categorie, libelle=libelle, texte_patient=texte_patient, statut=r['statut'], avis=self._avis(r),
                 alertes=[dict(code=a, libelle=LIBELLE_ALERTE[a]) for a in r.get('alertes', [])], explication=self._explication(r), regle=self._regle(r),
                 confiance_regle=r.get('confiance_regle_cpic', ''), confiance_dl=r.get('confiance_dl'), proba_dl=r.get('proba_dl'))
        if r.get('genes_requis_hors_modele'): f['alerte_gene_hors_modele'] = r['genes_requis_hors_modele']
        if r.get('genes_regle_hors_profil'): f['alerte_gene_hors_profil'] = r['genes_regle_hors_profil']
        return f

    def classer(self, r, par_med):
        """catégorie d'un résultat du moteur : a_eviter / proposable / a_verifier / non_evalue / reference_seule"""
        st = r['statut']; avis = set(self._avis(r).values())
        if st == 'medicament_non_couvert': return 'non_evalue'
        if 'EVITER' in avis: return 'a_eviter'
        if st == 'dl_indisponible': return 'reference_seule'
        if st == 'ok': return 'proposable'
        if st == 'a_verifier': return 'a_verifier'
        return 'non_evalue'   # non_determine_gene, hors_domaine

    def recommander(self, resultats_moteur, specialite, max_proposes=4):
        if specialite not in self.classes: raise ValueError('Spécialité inconnue : %s' % specialite)
        par_med = {r['medicament']: r for r in resultats_moteur}
        meds_sp = self.medicaments_de_specialite(specialite)
        prop, evit, verif, nonev, refseule = [], [], [], [], []
        for m in meds_sp:
            r = par_med.get(m)
            if r is None: continue
            c = self.classer(r, par_med)
            if c == 'a_eviter':
                f = self._fiche(r, par_med, c, TEXTE_PATIENT['EVITER'], LIBELLE_PRO['EVITER']); f['alternatives'] = self._alternatives(m, par_med); evit.append(f)
            elif c == 'proposable':
                f = self._fiche(r, par_med, c, TEXTE_PATIENT[r['action_dl']], LIBELLE_PRO[r['action_dl']]); f['action'] = r['action_dl']; prop.append(f)
            elif c == 'a_verifier':
                verif.append(self._fiche(r, par_med, c, TEXTE_PATIENT['A_VERIFIER'], 'À vérifier par un professionnel'))
            elif c == 'reference_seule':
                refseule.append(self._fiche(r, par_med, c, TEXTE_PATIENT['NON_EVALUE'], 'Règle de guideline seule (pas de prédiction du modèle)'))
            else:
                f = self._fiche(r, par_med, c, TEXTE_PATIENT['NON_EVALUE'], 'Non évalué'); f['motif'] = r.get('message', r['statut']); nonev.append(f)
        prop.sort(key=lambda d: (ORDRE_PROPOSITION[d['action']], -(d['proba_dl'] or {}).get(d['action'], 0)))
        for i, d in enumerate(prop[:max_proposes], 1): d['rang'] = i
        evit.sort(key=lambda d: -((d['proba_dl'] or {}).get('EVITER') or 0))
        return dict(specialite=specialite, n_medicaments_specialite=len(meds_sp), proposes=prop[:max_proposes], autres_compatibles=len(prop[max_proposes:]),
                    a_eviter=evit, a_verifier=verif, non_evalues=nonev, reference_seule=refseule, avertissement=AVERTISSEMENT_GENERAL,
                    note_ordre="L'ordre reflète la confiance du modèle, pas une validation clinique.")

    def chercher_medicament(self, texte, resultats_moteur):
        """Recherche par nom international ou nom français courant connu ; les noms commerciaux ne sont PAS couverts (source à fournir)."""
        q = (texte or '').lower().strip(); m = self._noms.get(q)
        if m is None:
            return dict(trouve=False, requete=texte, message="Médicament non trouvé parmi les %d médicaments pris en charge. Les noms commerciaux ne sont pas encore reconnus : essayez le nom de la substance active." % len(self.meds))
        par_med = {r['medicament']: r for r in resultats_moteur}; r = par_med[m]; c = self.classer(r, par_med)
        if c == 'a_eviter':
            f = self._fiche(r, par_med, c, TEXTE_PATIENT['EVITER'], LIBELLE_PRO['EVITER']); f['alternatives'] = self._alternatives(m, par_med)
        elif c == 'proposable':
            f = self._fiche(r, par_med, c, TEXTE_PATIENT[r['action_dl']], LIBELLE_PRO[r['action_dl']]); f['action'] = r['action_dl']
        elif c == 'a_verifier':
            f = self._fiche(r, par_med, c, TEXTE_PATIENT['A_VERIFIER'], 'À vérifier par un professionnel')
        elif c == 'reference_seule':
            f = self._fiche(r, par_med, c, TEXTE_PATIENT['NON_EVALUE'], 'Règle de guideline seule (pas de prédiction du modèle)')
        else:
            f = self._fiche(r, par_med, c, TEXTE_PATIENT['NON_EVALUE'], 'Non évalué'); f['motif'] = r.get('message', r['statut'])
        f.update(trouve=True, avertissement=AVERTISSEMENT_GENERAL)
        return f
