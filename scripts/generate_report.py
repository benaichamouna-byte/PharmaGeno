from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime
import io

def generate_pdf_report(filename, variants, predictions, results, drug_search=None, drug_result=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                             topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'],
                                   textColor=colors.HexColor('#2E5F8A'))
    story.append(Paragraph("PharmaGeno — Rapport d'analyse pharmacogénomique", title_style))
    story.append(Spacer(1, 12))

    info = (f"Fichier analysé : {filename}<br/>"
            f"Date du rapport : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    story.append(Paragraph(info, styles['Normal']))
    story.append(Spacer(1, 18))

    # Variants
    story.append(Paragraph("Variants détectés", styles['Heading2']))
    var_data = [['Gène', 'rsID', 'Génotype', 'Chromosome', 'Position']]
    for v in variants:
        var_data.append([v['gene'], v['rsid'], v['genotype'],
                          str(v['chromosome']), str(v['position'])])
    var_table = Table(var_data, hAlign='LEFT')
    var_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E5F8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f9ff')]),
    ]))
    story.append(var_table)
    story.append(Spacer(1, 18))

    # Prédictions ML
    story.append(Paragraph("Prédictions du modèle — Vote majoritaire DL v5 + RF v3", styles['Heading2']))
    pred_data = [['Gène', 'rsID', 'Phénotype prédit', 'Confiance', 'Niveau']]
    for p in predictions:
        pred_data.append([p['gene'], p['rsid'], p['phenotype'],
                           f"{p['confidence']}%", p['level']])
    pred_table = Table(pred_data, hAlign='LEFT')

    style_cmds = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E5F8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]
    color_map = {'green': colors.HexColor('#1e8449'),
                 'orange': colors.HexColor('#b7950b'),
                 'red': colors.HexColor('#c0392b')}
    for i, p in enumerate(predictions, start=1):
        style_cmds.append(('TEXTCOLOR', (3,i), (4,i), color_map.get(p['color'], colors.black)))
        style_cmds.append(('FONTNAME', (3,i), (4,i), 'Helvetica-Bold'))
    pred_table.setStyle(TableStyle(style_cmds))
    story.append(pred_table)
    story.append(Spacer(1, 18))

    # Recherche médicament si présente
    if drug_search and drug_result:
        story.append(Paragraph(f"Vérification du médicament : {drug_search}", styles['Heading2']))
        story.append(Paragraph(drug_result['message'], styles['Normal']))
        story.append(Spacer(1, 12))

    # Recommandations (limité aux 30 premières pour ne pas surcharger le PDF)
    story.append(Paragraph("Recommandations PharmGKB + CPIC + DPWG (extrait)", styles['Heading2']))
    rec_data = [['Gène', 'rsID', 'Médicament', 'Phénotype', 'Source']]
    for r in results[:30]:
        rec_data.append([r['gene'], r['rsid'], str(r['drug'])[:30],
                          r['phenotype'], r['source']])
    rec_table = Table(rec_data, hAlign='LEFT')
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E5F8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f9ff')]),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 18))

    footer = ("Rapport généré automatiquement par PharmaGeno — "
              "Projet de mémoire Master Bioinformatique. "
              "Ce document est un outil d'aide à la décision et ne remplace pas "
              "l'avis clinique d'un professionnel de santé.")
    story.append(Paragraph(footer, ParagraphStyle('Footer', parent=styles['Normal'],
                                                    fontSize=7, textColor=colors.grey)))

    doc.build(story)
    buffer.seek(0)
    return buffer
