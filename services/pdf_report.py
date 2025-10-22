# -*- coding: utf-8 -*-
# services/pdf_report.py

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import textwrap

def export_plan_pdf(filename: str, cards: list[dict], title: str = "Assistente de Rastreamento e Vacinação – Resumo"):
    """
    Gera um PDF limpo e compatível com acentuação contendo os cards de recomendações.
    Cada card deve ser um dicionário com as chaves: title, rationale, action, notes, references.
    """
    # Fonte compatível com português
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

    c = canvas.Canvas(filename, pagesize=A4)
    W, H = A4

    # Margens
    left_margin = 2 * cm
    right_margin = W - 2 * cm
    top_margin = H - 3 * cm
    bottom_margin = 2 * cm

    # Cabeçalho
    c.setFont("HeiseiMin-W3", 14)
    c.drawString(left_margin, top_margin + 1.2*cm, "Hospital / Centro Médico CHN")
    c.setFont("HeiseiMin-W3", 12)
    c.drawString(left_margin, top_margin, title)
    c.setFont("HeiseiMin-W3", 9)
    c.drawRightString(right_margin, top_margin, datetime.now().strftime("%d/%m/%Y %H:%M"))
    c.line(left_margin, top_margin - 4, right_margin, top_margin - 4)

    y = top_margin - 30
    page_num = 1
    c.setFont("HeiseiMin-W3", 10)

    def add_page_footer():
        nonlocal page_num
        c.setFont("HeiseiMin-W3", 8)
        c.drawRightString(right_margin, bottom_margin - 10, f"Página {page_num}")
        c.showPage()
        page_num += 1
        c.setFont("HeiseiMin-W3", 10)

    # Percorre cada card
    for card in cards:
        # Título do bloco
        c.setFont("HeiseiMin-W3", 12)
        c.drawString(left_margin, y, f"• {card.get('title','Sem título')}")
        y -= 18
        c.setFont("HeiseiMin-W3", 10)

        for label in ["rationale", "action", "notes", "references"]:
            content = card.get(label)
            if not content:
                continue

            # título da seção
            section_label = label.capitalize()
            c.setFont("HeiseiMin-W3", 9)
            c.drawString(left_margin + 5, y, f"{section_label}:")
            y -= 14
            c.setFont("HeiseiMin-W3", 10)

            # transforma listas em texto único
            if isinstance(content, list):
                content = "\n".join(content)

            lines = []
            for ln in str(content).split("\n"):
                lines += textwrap.wrap(ln, width=95)

            for ln in lines:
                if y < bottom_margin + 40:
                    add_page_footer()
                    y = top_margin
                c.drawString(left_margin + 10, y, ln)
                y -= 12
            y -= 10  # espaço entre seções

        y -= 8
        if y < bottom_margin + 60:
            add_page_footer()
            y = top_margin

    # rodapé final
    add_page_footer()
    c.save()
