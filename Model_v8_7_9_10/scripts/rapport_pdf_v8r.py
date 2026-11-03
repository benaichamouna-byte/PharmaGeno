#!/usr/bin/env python3
"""
rapport_pdf_v8r.py (3 nov. 2026) : copie de rapport_pdf_v8.py (INTACT) : quatre avis (DL, directive officielle, XGBoost, Random Forest) avec score 0-1, plus de « confiance x % », section des directives et références.
Aucune prédiction n'est calculée ici : le module met en forme ce que moteur_v8 / recommandation_v8 ont produit.
Règles de présentation : le statut est toujours écrit en toutes lettres (jamais la couleur seule) ; les trois avis (modèle DL, règle CPIC/DPWG,
XGBoost) sont affichés côte à côte ; les médicaments non évalués ne sont jamais présentés comme sans risque ; le texte des guidelines n'est pas traduit.
"""
import io, re
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
import math
from references_v8r import REFERENCES, REF_SOURCE, LEGENDE_SCORES
from reportlab.platypus import CondPageBreak, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BLEU = colors.HexColor('#1f4e79')
COULEUR_ACTION = {'EVITER': '#b71c1c', 'ADAPTER_DOSE': '#c75b00', 'SURVEILLER': '#8a6d00', 'STANDARD': '#1b5e20'}
COURT = {'EVITER': 'À éviter', 'ADAPTER_DOSE': 'Adapter la dose', 'SURVEILLER': 'Surveiller', 'STANDARD': 'Standard'}


def _p3(x):
    """score 0-1, 3 décimales arrondi vers le bas ; ≥ 0,999 au-delà (même règle que l'écran)"""
    if x is None: return '-'
    v = math.floor(float(x) * 1000) / 1000
    return '≥ 0,999' if v >= 0.999 else ('%.3f' % v).replace('.', ',')


def _e(t):
    """Échappe le texte pour reportlab Paragraph."""
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def construire_pdf(job, reco, genes_table, fiche, resume, avertissement, globaux, bloquants, limites, methode):
    """job : dict de la tâche ; reco : sortie de Recommandeur.recommander ; genes_table : lignes du tableau des gènes ;
    fiche : sortie de chercher_medicament ou None ; resume : texte ; globaux : liste de fiches « à éviter » (toutes spécialités) ;
    bloquants : liste de textes sur les gènes non déterminés ; limites : liste de textes ; methode : texte."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.6 * cm, bottomMargin=1.6 * cm, leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                            title='PharmaGeno - rapport', author='PharmaGeno')
    st = getSampleStyleSheet()
    h1 = ParagraphStyle('h1', parent=st['Title'], textColor=BLEU, fontSize=18)
    h2 = ParagraphStyle('h2', parent=st['Heading2'], textColor=BLEU, fontSize=12.5, spaceBefore=10)
    n = ParagraphStyle('n', parent=st['Normal'], fontSize=9, leading=12)
    petit = ParagraphStyle('p', parent=n, fontSize=7.5, leading=10, textColor=colors.HexColor('#444444'))
    cell = ParagraphStyle('c', parent=n, fontSize=7.8, leading=10)
    cellb = ParagraphStyle('cb', parent=cell, fontName='Helvetica-Bold', textColor=colors.white)
    S = []

    def tableau(entetes, lignes, largeurs):
        data = [[Paragraph(_e(x), cellb) for x in entetes]] + [[c if hasattr(c, 'wrap') else Paragraph(_e(c), cell) for c in l] for l in lignes]
        t = Table(data, colWidths=largeurs, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), BLEU), ('GRID', (0, 0), (-1, -1), 0.4, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                               ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f7fb')])]))
        return t

    def etiquette(action, extra=''):
        if not action: return Paragraph('-', cell)
        return Paragraph('<font color="%s"><b>%s</b></font>%s' % (COULEUR_ACTION.get(action, '#333333'), _e(COURT.get(action, action)), extra), cell)

    def avis_score(a, p):
        return etiquette(a, ('<br/>score %s' % _p3(p)) if (a and p is not None) else '')

    def quatre_avis(f):
        a = f.get('avis', {})
        return [avis_score(a.get('DL'), f.get('p_dl')), etiquette(a.get('règle CPIC/DPWG')), avis_score(a.get('XGBoost'), f.get('p_xgb')), avis_score(f.get('avis_rf'), f.get('p_rf'))]

    ENT = ['Médicament', 'DL (programme d\'IA) et score', 'Directive officielle (CPIC/DPWG)', 'XGBoost (contrôle) et score', 'Random Forest (contrôle) et score']
    LARG = [3.1 * cm, 3.4 * cm, 3.4 * cm, 3.4 * cm, 3.4 * cm]

    def table_fiches(fs):
        return tableau(ENT + ['Alertes'], [[('#%d ' % f['rang'] if f.get('rang') else '') + f['medicament']] + quatre_avis(f) + [Paragraph(_e(' ; '.join(x['libelle'] for x in f.get('alertes', [])) or 'aucune'), cell)] for f in fs],
                       [2.7 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm, 3.5 * cm])

    # --- en-tête
    S.append(Paragraph("PharmaGeno - Rapport d'analyse pharmacogénétique (v8r)", h1))
    origine = ("Profil de démonstration (profil réel du corpus d'entraînement : ne concerne aucun patient)" if job['mode'] == 'demo'
               else 'Fichier VCF : %s (assemblage %s)' % (job.get('nom_fichier', ''), job.get('assemblage', '?')))
    S.append(Paragraph('%s<br/>Spécialité choisie : <b>%s</b><br/>Date du rapport : %s' % (_e(origine), _e(reco['specialite']), datetime.now().strftime('%d/%m/%Y %H:%M')), n))
    S.append(Spacer(1, 6))
    S.append(Paragraph('<b>Important.</b> ' + _e(avertissement), n))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('1. Résumé', h2))
    S.append(Paragraph(_e(resume), n))
    for b in bloquants:
        S.append(Spacer(1, 3)); S.append(Paragraph('<b>Attention.</b> ' + _e(b), n))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('2. Gènes analysés', h2))
    S.append(tableau(['Gène', 'Valeur de codage', 'Phénotype / génotype lu', 'Origine', 'Remarque'],
                     [[g['gene'], g['valeur_txt'], g['lecture'] + ((' (' + g['genotype'] + ')') if g.get('genotype') else ''), g['origine'], g['motif'] or ''] for g in genes_table],
                     [2.4 * cm, 2.0 * cm, 4.2 * cm, 3.4 * cm, 5.4 * cm]))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('3. Médicaments à éviter pour ce profil (toutes spécialités)', h2))
    if globaux:
        lignes = []
        for f in globaux:
            alt = ', '.join(x['medicament'] for x in f.get('alternatives', [])[:4]) or 'aucune alternative de la même classe parmi les médicaments pris en charge'
            lignes.append([f['medicament']] + quatre_avis(f) + [Paragraph(_e(alt), cell)])
        S.append(tableau(ENT + ['Alternatives possibles (même classe ATC, sans adaptation génétique)'], lignes, [2.6 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 4.4 * cm]))
        S.append(Spacer(1, 3))
        S.append(Paragraph("Un seul avis « à éviter » (DL, XGBoost, Random Forest ou directive officielle) suffit à signaler le médicament, par prudence. Les alternatives sont de la même "
                           "classe pharmacologique ; leur équivalence clinique n'est pas affirmée et reste à confirmer par un professionnel.", petit))
    else:
        S.append(Paragraph("Aucun des médicaments évalués n'est signalé « à éviter ». Cette conclusion ne couvre pas les médicaments non évalués (voir ci-dessous).", n))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('4. Spécialité « %s » : médicaments proposés (compatibilité génétique uniquement)' % _e(reco['specialite']), h2))
    if reco['proposes']:
        S.append(table_fiches(reco['proposes']))
        S.append(Spacer(1, 3))
        S.append(Paragraph("L'ordre suit le score du DL ; il ne constitue pas une validation clinique. Plusieurs médicaments ont des scores quasi identiques : l'écart entre eux n'est pas significatif. "
                           "Ce n'est pas une prescription : l'indication, les interactions et les contre-indications ne sont pas évaluées.", petit))
        if reco['autres_compatibles']:
            S.append(Paragraph('%d autre(s) médicament(s) de la spécialité sont également compatibles et ne sont pas détaillés ici.' % reco['autres_compatibles'], petit))
    else:
        S.append(Paragraph("Aucun médicament de cette spécialité n'a pu être proposé pour ce profil.", n))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('5. À vérifier par un professionnel', h2))
    if reco['a_verifier']:
        S.append(table_fiches(reco['a_verifier']))
    else:
        S.append(Paragraph('Aucun médicament de la spécialité dans cette catégorie.', n))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('6. Médicaments non évalués', h2))
    S.append(Paragraph("« Non évalué » ne veut pas dire « sans risque » : le modèle ne peut pas répondre de façon fiable pour ces médicaments.", petit))
    if reco['non_evalues']:
        S.append(tableau(['Médicament', 'Motif', 'Règle CPIC/DPWG (référence)'],
                         [[f['medicament'], f.get('motif') or '', etiquette(f.get('avis', {}).get('règle CPIC/DPWG'))] for f in reco['non_evalues']],
                         [3.2 * cm, 10.0 * cm, 4.2 * cm]))
    else:
        S.append(Paragraph('Tous les médicaments de la spécialité ont pu être évalués.', n))

    if reco['reference_seule']:
        S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('7. Règle de guideline seule (pas de prédiction du modèle)', h2))
        S.append(tableau(['Médicament', 'Règle CPIC/DPWG'], [[f['medicament'], etiquette(f.get('avis', {}).get('règle CPIC/DPWG'))] for f in reco['reference_seule']],
                         [6.0 * cm, 11.4 * cm]))

    if fiche:
        S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('8. Médicament recherché%s' % ((' : ' + _e(fiche['medicament'])) if fiche.get('trouve') else ''), h2))
        if fiche.get('trouve'):
            S.append(table_fiches([fiche]))
            S.append(Spacer(1, 3)); S.append(Paragraph(_e(fiche['texte_patient']), n))
            for r in fiche.get('regle', []):
                S.append(Paragraph('Règle %s : %s (%s). %s' % (_e('+'.join(r['genes'])), _e(r['phenotype']), _e(r['source']), _e(r['texte_guideline_en'])), petit))
        else:
            S.append(Paragraph(_e(fiche['message']), n))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('9. Explication en langage simple (pour le patient)', h2))
    simples = list(globaux) + [f for f in reco['proposes'] if f['medicament'] not in {g['medicament'] for g in globaux}]
    for p in simples:
        S.append(KeepTogether([Paragraph('<b>%s</b> - %s' % (_e(p['medicament']), _e(p['libelle'])), n), Paragraph(_e(p['texte_patient']), n), Spacer(1, 4)]))
    if not simples: S.append(Paragraph('Aucun médicament à commenter.', n))
    if reco['non_evalues']:
        S.append(Paragraph("Les médicaments « non évalués » n'ont pas pu être analysés pour votre profil : cela ne veut pas dire qu'ils vous conviennent. "
                           "Demandez l'avis de votre médecin ou de votre pharmacien.", n))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('10. Lire les scores 0-1', h2))
    S.append(Paragraph(_e(LEGENDE_SCORES), petit))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('11. Directives utilisées pour les médicaments de ce rapport', h2))
    vus, lignes_dir = set(), []
    for f in list(reco['proposes']) + list(reco['a_verifier']) + list(globaux) + list(reco['non_evalues']) + list(reco['reference_seule']) + ([fiche] if fiche and fiche.get('trouve') else []):
        for r_ in f.get('regle', []):
            ids = re.findall(r'PA\d{6,}', str(r_.get('fichier') or ''))
            cle = (f['medicament'], r_['source'], tuple(ids))
            if cle in vus: continue
            vus.add(cle)
            ref, lien = REF_SOURCE.get(str(r_['source']).split('-')[0].strip(), (None, None)) if ('etiquette' not in str(r_['source']) and str(r_['source']) != 'FDA') else (None, None)
            texte = '<b>%s</b> : %s' % (_e(f['medicament']), _e(r_['source']))
            if ref: texte += ' (référence générale de la source : %s, <link href="%s" color="blue">%s</link>)' % (_e(ref), lien, _e(lien))
            for i in ids: texte += ' ; fiche de la directive : <link href="https://www.clinpgx.org/guidelineAnnotation/%s" color="blue">%s</link>' % (i, i)
            lignes_dir.append(Paragraph(texte, petit))
    if lignes_dir: S.extend(lignes_dir)
    else: S.append(Paragraph("Aucune règle de directive à citer pour ces médicaments.", petit))
    S.append(Paragraph("La publication précise de chaque directive par médicament n'est pas encore associée ; la référence générale de la source et la fiche ClinPGx sont indiquées.", petit))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('12. Références scientifiques', h2))
    for g in REFERENCES:
        S.append(Paragraph('<b>%s</b>' % _e(g['groupe']), petit))
        for it in g['items']:
            S.append(Paragraph('- %s <link href="%s" color="blue">%s</link>' % (_e(it['texte']), it['lien'], _e(it['etiquette'])), petit))

    S.append(CondPageBreak(3.5 * cm)); S.append(Paragraph('13. Méthode et limites', h2))
    S.append(Paragraph(_e(methode), petit))
    for l in limites:
        S.append(Paragraph('- ' + _e(l), petit))
    doc.build(S)
    buf.seek(0)
    return buf
