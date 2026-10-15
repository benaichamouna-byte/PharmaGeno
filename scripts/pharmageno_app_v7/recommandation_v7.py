#!/usr/bin/env python3
"""
recommandation_v7.py : couche de recommandation de l'application PharmaGeno (logique pure, sans interface).
Entrée : la sortie de moteur_v7.MoteurPGx.predire(profil) + une spécialité. Sortie : un dictionnaire prêt pour la page de résultats et le PDF.

Ce que la couche fait (et ne fait pas)
  - Elle ne recalcule rien : toute prédiction vient du moteur DL (XGBoost en second avis). Elle trie, filtre par spécialité et met en forme.
  - « Médicaments proposés » = compatibilité PHARMACOGÉNÉTIQUE uniquement (≤ 4, classés par classe d'action puis par confiance du modèle). Ce n'est pas
    une prescription : l'indication clinique, les interactions et les contre-indications ne sont pas évaluées. L'ordre est une confiance du modèle,
    non validée cliniquement.
  - « À éviter » = tout médicament de la spécialité pour lequel le DL OU XGBoost prédit EVITER (par prudence : un seul avis suffit à le signaler).
  - « Non évalués » = gène non déterminé, combinaison jamais vue par le modèle, médicament hors des 76 : jamais proposés, jamais classés comme normaux.
  - Alternatives d'un médicament à éviter : mêmes sous-groupe pharmacologique ATC (4e niveau) ET statut ok / STANDARD pour ce patient. L'équivalence
    clinique n'est pas affirmée (alternatives_atc4_v1.csv : statut « à valider »).
  - La spécialité est rattachée à des classes ATC (specialite_atc_v1.csv : choix de conception, à valider par un clinicien). L'ATC range un médicament
    selon son usage principal : des corrections d'usage clinique restent à établir (ex. codéine).
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
}
LIBELLE_VALEUR = {0.0: 'activité très réduite ou absente', 0.5: 'activité réduite', 1.0: 'activité normale', 1.5: 'activité augmentée', 2.0: 'activité très augmentée'}
AVERTISSEMENT_GENERAL = ("Cet outil analyse un nombre limité de gènes et de médicaments ; il ne remplace ni l'avis d'un médecin ou d'un pharmacien, "
                         "ni une prescription. Il ne tient pas compte des autres médicaments, des maladies ni de l'âge. Résultat à discuter avec un professionnel de santé.")
FRANCAIS_VERS_INN = {'warfarine': 'warfarin', 'aspirine': 'aspirin', 'fluorouracile': 'fluorouracil', 'tamoxifene': 'tamoxifen', 'tamoxifène': 'tamoxifen',
                     'codeine': 'codeine', 'codéine': 'codeine', 'omeprazole': 'omeprazole', 'oméprazole': 'omeprazole'}   # extraits de l'ancien app.py ; liste à compléter


def _codes(s):
    return [c for c in str(s).split(';') if c and c != 'nan']


class Recommandeur:
    def __init__(self, atc_csv, specialites_csv, alternatives_csv, medicaments_moteur):
        self.meds = list(medicaments_moteur)
        a = pd.read_csv(atc_csv); self.atc = a[a.medicament.isin(self.meds)].set_index('medicament')
        s = pd.read_csv(specialites_csv); s = s[s.code_atc != 'TOTAL'].dropna(subset=['code_atc'])
        self.classes = {sp: sorted(set(g.code_atc)) for sp, g in s.groupby('specialite')}
        alt = pd.read_csv(alternatives_csv)
        self.alt_classe = {}   # classe ATC4 -> principes actifs
        for c, g in alt.groupby('classe_atc4'): self.alt_classe[c] = sorted(set(g.principe_actif))
        self._noms = {}
        for m, r in self.atc.iterrows():
            for n in {m, str(r.principe_actif), str(r.nom_utilise_pour_la_recherche)}: self._noms[n.lower().strip()] = m
        self._noms.update({k: v for k, v in FRANCAIS_VERS_INN.items() if v in self.meds})

    def specialites(self):
        return sorted(self.classes)

    def medicaments_de_specialite(self, specialite):
        pref = tuple(self.classes[specialite])
        return [m for m in self.meds if any(c.startswith(pref) for c in _codes(self.atc.loc[m, 'atc_codes']))]

    def _alternatives(self, med, par_med):
        """Mêmes sous-groupe ATC (4e niveau), statut ok et STANDARD pour ce patient. Équivalence clinique NON affirmée."""
        out = []
        classes4 = {c[:5] for c in _codes(self.atc.loc[med, 'atc_codes'])}
        for m2, r in self.atc.iterrows():
            if m2 == med or m2 not in par_med: continue
            if classes4 & {c[:5] for c in _codes(r.atc_codes)}:
                x = par_med[m2]
                if x['statut'] == 'ok' and x['action'] == 'STANDARD': out.append(dict(medicament=m2, confiance=x['proba_dl']['STANDARD']))
        return sorted(out, key=lambda d: -d['confiance'])

    def _explication(self, med, profil, detail_profil, domaine):
        genes = domaine[med]['genes']; lignes = []
        for g in genes:
            v = profil.get(g)
            ph = (detail_profil or {}).get(g, {}).get('phenotype')
            lignes.append(dict(gene=g, valeur=v, phenotype_pypgx=ph, lecture=LIBELLE_VALEUR.get(v, 'non déterminé')))
        return lignes

    def recommander(self, resultats_moteur, specialite, profil, domaine, detail_profil=None, max_proposes=4):
        if specialite not in self.classes:
            raise ValueError('Spécialité inconnue : %s' % specialite)
        par_med = {}
        for r in resultats_moteur:
            x = dict(r); x['proba_dl'] = r.get('proba_dl', {}); par_med[r['medicament']] = x
        meds_sp = self.medicaments_de_specialite(specialite)
        proposables, a_eviter, non_evalues = [], [], []
        for m in meds_sp:
            r = par_med.get(m)
            if r is None: continue
            if r['statut'] in ('ok', 'desaccord'):
                avis = {r['action'], r.get('action_xgboost')}
                if 'EVITER' in avis:
                    a_eviter.append(dict(medicament=m, action_dl=r['action'], action_xgboost=r.get('action_xgboost'),
                                         avis_divergent=r['statut'] == 'desaccord', confiance_dl=r['proba_dl'].get('EVITER'),
                                         libelle=LIBELLE_PRO['EVITER'], texte_patient=TEXTE_PATIENT['EVITER'],
                                         explication=self._explication(m, profil, detail_profil, domaine), alternatives=self._alternatives(m, par_med)))
                elif r['statut'] == 'ok':
                    proposables.append(dict(medicament=m, action=r['action'], confiance=r['proba_dl'][r['action']], libelle=LIBELLE_PRO[r['action']],
                                            texte_patient=TEXTE_PATIENT[r['action']], explication=self._explication(m, profil, detail_profil, domaine),
                                            alerte_gene_hors_modele=domaine[m]['genes_regle_hors_modele'] or None))
                else:
                    non_evalues.append(dict(medicament=m, motif='Les deux modèles ne sont pas d\'accord (DL : %s, XGBoost : %s) : à vérifier par un professionnel.' % (r['action'], r.get('action_xgboost'))))
            else:
                non_evalues.append(dict(medicament=m, motif=r.get('message', r['statut']), statut=r['statut'],
                                        regles_non_apprises=r.get('regles_non_apprises')))
        proposables.sort(key=lambda d: (ORDRE_PROPOSITION[d['action']], -d['confiance']))
        for i, d in enumerate(proposables[:max_proposes], 1): d['rang'] = i
        return dict(specialite=specialite, n_medicaments_specialite=len(meds_sp), proposes=proposables[:max_proposes], autres_compatibles=len(proposables[max_proposes:]),
                    a_eviter=sorted(a_eviter, key=lambda d: -(d['confiance_dl'] or 0)), non_evalues=non_evalues,
                    avertissement=AVERTISSEMENT_GENERAL,
                    note_ordre="L'ordre reflète la confiance du modèle, pas une validation clinique.")

    def chercher_medicament(self, texte, resultats_moteur, profil=None, domaine=None, detail_profil=None):
        """Recherche par nom international (INN) ou nom français courant déjà connu. Les noms commerciaux ne sont PAS encore couverts (source à fournir).
        Retourne une fiche complète (statut, texte patient, explication par gène, alternatives si à éviter)."""
        q = (texte or '').lower().strip()
        m = self._noms.get(q)
        if m is None:
            return dict(trouve=False, requete=texte, message="Médicament non trouvé parmi les %d médicaments pris en charge. Les noms commerciaux ne sont pas encore reconnus : essayez le nom de la substance active." % len(self.meds))
        par_med = {r['medicament']: r for r in resultats_moteur}
        r = par_med[m]; fiche = dict(trouve=True, medicament=m, statut=r['statut'], avertissement=AVERTISSEMENT_GENERAL, resultat=r)
        if domaine is not None and profil is not None: fiche['explication'] = self._explication(m, profil, detail_profil, domaine)
        if r['statut'] in ('ok', 'desaccord'):
            avis = {r['action'], r.get('action_xgboost')}
            act = 'EVITER' if 'EVITER' in avis else r['action']
            if r['statut'] == 'desaccord' and act != 'EVITER':
                fiche.update(libelle='Avis divergents entre les deux modèles : à vérifier par un professionnel', texte_patient="Les deux modèles ne donnent pas la même réponse pour ce médicament : demandez l'avis de votre médecin ou de votre pharmacien.")
            else:
                fiche.update(action=act, libelle=LIBELLE_PRO[act], texte_patient=TEXTE_PATIENT[act])
            if act == 'EVITER': fiche['alternatives'] = self._alternatives(m, par_med)
        else:
            fiche.update(libelle='Non évalué', texte_patient="Ce médicament n'a pas pu être évalué pour ce profil : " + r.get('message', r['statut']))
        return fiche
