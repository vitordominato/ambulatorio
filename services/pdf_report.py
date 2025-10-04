from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path

def export_recommendations(filename: str, header: str, lines: list[str]):
    p = Path(filename)
    c = canvas.Canvas(str(p), pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, header)
    y -= 30
    c.setFont("Helvetica", 11)
    for line in lines:
        c.drawString(50, y, f"- {line}")
        y -= 18
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 11)
    c.save()
    return str(p)

