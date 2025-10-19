# services/pdf_export.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from textwrap import wrap

def export_plan_pdf(filename: str, cards: list[dict]):
    c = canvas.Canvas(filename, pagesize=A4)
    W, H = A4
    x, y = 40, H - 60
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Assistente de Rastreio e Vacinação — Resumo")
    y -= 30
    c.setFont("Helvetica", 10)

    for card in cards:
        for label in ["title", "rationale", "action", "notes", "references"]:
            text = f"{label.capitalize()}: {card.get(label, '')}".strip()
            if not text: 
                continue
            lines = []
            for ln in text.split("\n"):
                lines += wrap(ln, width=95)
            for ln in lines:
                if y < 60:
                    c.showPage(); y = H - 40; c.setFont("Helvetica", 10)
                c.drawString(x, y, ln); y -= 14
            y -= 10
        y -= 10
    c.showPage(); c.save()
