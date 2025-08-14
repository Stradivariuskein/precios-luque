import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors


def generate_artics_pdf(artics_one_price: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=20
    )
    elements = []
    styles = getSampleStyleSheet()

    # --- Left block (WP and phone) ---
    wp_icon_path = "static/img/logo-wp.png"
    if os.path.exists(wp_icon_path):
        wp_icon = Image(wp_icon_path, width=1*cm, height=1*cm)
    else:
        wp_icon = Paragraph("WP", styles['Normal'])

    wp_text = Paragraph(
        "<b>Wp:</b> +54 9 11 3075-3001<br/><b>Tel:</b> 4460-2005",
        styles['Normal']
    )
    left_table = Table([[wp_icon, wp_text]], colWidths=[1.2*cm, 4.8*cm])
    left_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))

    # --- Center block (Logo) ---
    logo_path = "media/artics_imgs/luque.png"
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=7.5*cm, height=3.5*cm)
    else:
        logo = Paragraph("LOGO", styles['Title'])

    # --- Right block (Email) ---
    email_para = Paragraph("<b>Email:</b><br/>luquearti@gmail.com", styles['Normal'])

    # --- Combine into 1 row ---
    banner_table = Table(
        [[left_table, logo, email_para]],
        colWidths=[6*cm, 7.5*cm, 6*cm]  # 6 + 7.5 + 6 = 19.5 cm usable width
    )
    banner_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Center logo
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    elements.append(banner_table)
    elements.append(Spacer(1, 12))

    # Título principal
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=10,
        alignment=1  # Centro
    )
    elements.append(Paragraph("Lista de Precios", title_style))
    elements.append(Spacer(1, 18))

    # Títulos secundarios
    subtitle_style = styles['Heading3']

    for category_name, grouped_artics in artics_one_price.items():
        elements.append(Paragraph(category_name, subtitle_style))
        elements.append(Spacer(1, 12))

        for group in grouped_artics:
            group_name = group['name']
            articles = group['artics']

            elements.append(Paragraph(group_name, styles['Heading4']))
            elements.append(Spacer(1, 6))

            data = [["Código", "Descripción", "Precio"]]
            for artic, _images in articles:
                data.append([
                    str(artic.code),
                    artic.description,
                    f"${artic.price:.2f}" if artic.price is not None else "N/A"
                ])

            table = Table(data, colWidths=[80, 320, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff0000')),  # fondo rojo
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # texto blanco
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 20))

    doc.build(elements)
    buffer.seek(0)
    return buffer




# def generate_artics_pdf(artics_one_price: dict) -> io.BytesIO:
#     """
#     Genera un PDF con artículos agrupados por categoría y grupo (imagen_path).
    
#     :param artics_one_price: Diccionario con estructura:
#         {
#             "Categoria A": [
#                 {
#                     "name": "FIX NAC",
#                     "artics": [(ModelArticOnePrice, [imagenes]), ...]
#                 },
#                 ...
#             ],
#             ...
#         }
#     :return: Objeto BytesIO con el contenido del PDF
#     """
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()
#     title_style = styles['Heading1']
#     subtitle_style = styles['Heading3']
#     normal_style = styles['Normal']

#     for category_name, grouped_artics in artics_one_price.items():
#         elements.append(Paragraph(category_name, title_style))
#         elements.append(Spacer(1, 12))

#         for group in grouped_artics:
#             group_name = group['name']
#             articles = group['artics']

#             elements.append(Paragraph(group_name, subtitle_style))
#             elements.append(Spacer(1, 6))

#             data = [["Código", "Descripción", "Precio"]]
#             for artic, _images in articles:
#                 data.append([
#                     str(artic.code),
#                     artic.description,
#                     f"${artic.price:.2f}" if artic.price is not None else "N/A"
#                 ])

#             table = Table(data, colWidths=[80, 320, 80])
#             table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#                 ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
#                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ]))

#             elements.append(table)
#             elements.append(Spacer(1, 20))

#     doc.build(elements)
#     buffer.seek(0)
#     return buffer
