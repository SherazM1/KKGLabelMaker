"""PDF generator for SKID tags."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from app.models.skid_tag import SkidTag


PAGE_WIDTH, PAGE_HEIGHT = landscape(letter)
FONT_NAME = "Helvetica"
FONT_SIZE = 16
LEFT_MARGIN = 72


def _draw_tag_page(pdf: canvas.Canvas, tag: SkidTag) -> None:
    pdf.setFont(FONT_NAME, FONT_SIZE)

    y = PAGE_HEIGHT - 92
    pdf.drawCentredString(PAGE_WIDTH / 2, y, f"DC {tag.dc}")

    y -= 24
    pdf.drawCentredString(PAGE_WIDTH / 2, y, f"PO {tag.po_display}")

    y -= 48
    pdf.drawString(LEFT_MARGIN + 220, y, f"UPC  {tag.upc}")

    y -= 48
    pdf.drawString(LEFT_MARGIN + 240, y, tag.pallet_display)

    y -= 24
    pdf.drawCentredString(PAGE_WIDTH / 2, y, f"Qty: {tag.quantity}")


def generate_skid_tags_pdf(tags: list[SkidTag]) -> bytes:
    if not tags:
        raise ValueError("No SKID tags provided for PDF generation.")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    for tag in tags:
        _draw_tag_page(pdf, tag)
        pdf.showPage()

    pdf.save()
    buffer.seek(0)
    return buffer.read()
