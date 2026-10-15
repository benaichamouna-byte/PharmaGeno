#!/usr/bin/env python3
"""
rapport_pdf_v7.py : rapport PDF de l'application PharmaGeno (reportlab). Aucune prédiction n'est calculée ici : le module met en forme ce que
moteur_v7 / recommandation_v7 ont produit. Le statut est toujours écrit en toutes lettres (jamais la couleur seule).
"""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, KeepTogether

BLEU = colors.HexColor('#1f4e79')
COULEUR_ACTION = {'EVITER': '#b71c1c', 'ADAPTER_DOSE': '#c75b00', 'SURVEILLER': '#8a6d00', 'STANDARD': '#1b5e20'}


def _e(t):
    """Échappe le texte pour reportlab Paragraph."""
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def construire_pdf(job, reco, genes_table, fiche, resume, avertissement):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.8 * cm, bottomMargin=1.8 * cm, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            title='PharmaGeno - rapport', author='PharmaGeno')
    st = getSampleStyleSheet()
    h1 = ParagraphStyle('h1', parent=st['Title'], textColor=BLEU, fontSize=18)
    h2 = ParagraphStyle('h2', parent=st['Heading2'], textColor=BLEU, fontSize=12.5, spaceBefore=10, keepWithNext=1)
    n = ParagraphStyle('n', parent=st['Normal'], fontSize=9, leading=12)
    petit = ParagraphStyle('p', parent=n, fontSize=7.5, leading=10, textColor=colors.HexColor('#444444'))
    cell = ParagraphStyle('c', parent=n, fontSize=8, leading=10)
    cellb = ParagraphStyle('cb', parent=cell, fontName='Helvetica-Bold', textColor=colors.white)
    S = []

    def tableau(entetes, lignes, largeurs):
        data = [[Paragraph(_e(x), cellb) for x in entetes]] + [[c if hasattr(c, 'wrap') else Paragraph(_e(c), cell) for c in l] for l in lignes]
        t = Table(data, colWidths=largeurs, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), BLEU), ('GRID', (0, 0), (-1, -1), 0.4, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                               ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f7fb')])]))
        return t

    def etiquette(action, texte):
        return Paragraph('<font color="%s"><b>%s</b></font>' % (COULEUR_ACTION.get(action, '#333333'), _e(texte)), cell)

    S.append(Paragraph("PharmaGeno - Rapport d'analyse pharmacogénétique", h1))
    origine = ('Profil de démonstration (issu du corpus d\'entraînement : ne concerne aucun patient réel)' if job['mode'] == 'demo'
               else 'Fichier VCF : %s (assemblage %s)' % (job.get('nom_fichier', ''), job.get('assemblage', '?')))
    S.append(Paragraph('%s<br/>Spécialité choisie : <b>%s</b><br/>Date du rapport : %s' % (_e(origine), _e(reco['specialite']), datetime.now().strftime('%d/%m/%Y %H:%M')), n))
    S.append(Spacer(1, 6))
    S.append(Paragraph('<b>Important.</b> ' + _e(avertissement), n))

    S.append(Paragraph('1. Résumé', h2))
    S.append(Paragraph(_e(resume), n))

    S.append(Paragraph('2. Gènes analysés', h2))
    S.append(tableau(['Gène', 'Lecture', 'Phénotype PyPGx', 'Remarque'],
                     [[g['gene'], g['lecture'], g.get('phenotype') or '-', g.get('motif') or ''] for g in genes_table],
                     [2.2 * cm, 4.2 * cm, 4.4 * cm, 6.4 * cm]))

    S.append(Paragraph('3. Médicaments proposés pour la spécialité (compatibilité génétique uniquement)', h2))
    if reco['proposes']:
        S.append(tableau(['Rang', 'Médicament', 'Conclusion', 'Confiance du modèle', 'Gènes pris en compte'],
                         [[str(p['rang']), p['medicament'], etiquette(p['action'], p['libelle']), '%.1f %%' % (100 * p['confiance']),
                           ', '.join('%s (%s)' % (x['gene'], x['lecture']) for x in p['explication'])] for p in reco['proposes']],
                         [1.4 * cm, 2.6 * cm, 4.2 * cm, 2.4 * cm, 6.6 * cm]))
        S.append(Spacer(1, 3)); S.append(Paragraph(_e(reco['note_ordre']) + ' Plusieurs médicaments ont une confiance quasi identique : l\'écart entre eux n\'est pas significatif.', petit))
        if reco['autres_compatibles']:
            S.append(Paragraph('%d autre(s) médicament(s) de la spécialité sont également compatibles et ne sont pas détaillés ici.' % reco['autres_compatibles'], petit))
    else:
        S.append(Paragraph('Aucun médicament de cette spécialité n\'a pu être proposé pour ce profil.', n))

    S.append(Paragraph('4. Médicaments à éviter', h2))
    if reco['a_eviter']:
        lignes = []
        for a in reco['a_eviter']:
            alt = ', '.join(x['medicament'] for x in a['alternatives'][:4]) or 'aucune alternative de la même classe parmi les médicaments pris en charge'
            avis = 'DL : %s ; XGBoost : %s' % (a['action_dl'], a['action_xgboost'])
            lignes.append([a['medicament'], etiquette('EVITER', 'À éviter'), avis + (' (avis divergents : à vérifier)' if a['avis_divergent'] else ''), alt])
        S.append(tableau(['Médicament', 'Conclusion', 'Avis des modèles', 'Alternatives possibles (même classe ATC, sans adaptation génétique)'], lignes,
                         [2.6 * cm, 2.4 * cm, 5.2 * cm, 7.0 * cm]))
        S.append(Spacer(1, 3)); S.append(Paragraph("Les alternatives sont de la même classe pharmacologique ; leur équivalence clinique n'est pas affirmée et reste à confirmer par un professionnel.", petit))
    else:
        S.append(Paragraph('Aucun médicament de la spécialité n\'est signalé « à éviter » pour ce profil.', n))

    S.append(Paragraph('5. Médicaments non évalués', h2))
    if reco['non_evalues']:
        S.append(tableau(['Médicament', 'Motif'], [[x['medicament'], x['motif']] for x in reco['non_evalues']], [3.5 * cm, 13.7 * cm]))
    else:
        S.append(Paragraph('Tous les médicaments de la spécialité ont pu être évalués.', n))

    if fiche and fiche.get('trouve'):
        S.append(Paragraph('6. Médicament recherché : %s' % _e(fiche['medicament']), h2))
        S.append(Paragraph('<b>%s</b>' % _e(fiche['libelle']), n))
        S.append(Paragraph(_e(fiche['texte_patient']), n))
    elif fiche:
        S.append(Paragraph('6. Médicament recherché', h2)); S.append(Paragraph(_e(fiche['message']), n))

    S.append(Paragraph('Explication en langage simple (pour le patient)', h2))
    simples = list(reco['proposes']) + list(reco['a_eviter'])
    for p in simples:
        S.append(KeepTogether([Paragraph('<b>%s</b> - %s' % (_e(p['medicament']), _e(p['libelle'])), n), Paragraph(_e(p['texte_patient']), n), Spacer(1, 4)]))
    if not simples: S.append(Paragraph('Aucun médicament à commenter.', n))

    S.append(Spacer(1, 10))
    S.append(Paragraph("Méthode : réseau de neurones (couche FiLM conditionnée par le médicament) avec XGBoost comme second avis, entraînés sur le corpus v3 (76 médicaments, 12 gènes). "
                       "Les génotypes sont convertis en phénotypes par PyPGx 0.27.0. Les recommandations CPIC / DPWG ont servi à construire les étiquettes d'entraînement et à évaluer le modèle ; "
                       "elles ne sont pas appliquées directement à ce patient. Outil de recherche (mémoire de master), non validé cliniquement.", petit))
    doc.build(S)
    buf.seek(0)
    return buf
