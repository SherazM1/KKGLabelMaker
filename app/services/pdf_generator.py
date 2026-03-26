"""PDF generator service for creating print-ready label documents."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF

from app.models.label import Label
from app.services.barcode_service import generate_code128_barcode
from app.utils.formatting import drop_leading_zeros, sanitize_text, safe_wrap_text


PAGE_WIDTH, PAGE_HEIGHT = letter


def _draw_static_text(c: canvas.Canvas) -> None:
    """Render static content that does not change per label."""
    c.setFont("Helvetica", 12)

    c.drawString(1 * inch, PAGE_HEIGHT - 1 * inch, "ATTN: Dept. Mgr. Dept#: 5")
    c.drawString(1 * inch, PAGE_HEIGHT - 1.25 * inch, "ELECTRONICS DEPARTMENT")
    c.drawString(1 * inch, PAGE_HEIGHT - 1.75 * inch, "CONTENTS: SIGNAGE KITS")
    c.drawString(1 * inch, PAGE_HEIGHT - 6.75 * inch, "CAT: ELECTRONICS DEPT.")
    c.drawString(1 * inch, PAGE_HEIGHT - 7.0 * inch, "QTY: 1")

    footer_text = "For questions or additional information, call\nTara Webb 501-454-6407"
    text_obj = c.beginText(1 * inch, 1.25 * inch)
    text_obj.setFont("Helvetica", 10)
    for line in footer_text.split("\n"):
        text_obj.textLine(line)
    c.drawText(text_obj)


def _draw_label_fields(c: canvas.Canvas, label: Label) -> None:
    """Render dynamic label fields."""
    c.setFont("Helvetica", 12)

    y_cursor = PAGE_HEIGHT - 2.25 * inch

    # Shipper
    c.drawString(1 * inch, y_cursor, f"Shipper: {sanitize_text(label.supplier)}")
    y_cursor -= 0.5 * inch

    # Store
    c.drawString(1 * inch, y_cursor, f"STORE #: {sanitize_text(label.store)}")
    y_cursor -= 0.5 * inch

    # PO (display without leading zeros)
    po_display = drop_leading_zeros(label.po)
    c.drawString(1 * inch, y_cursor, f"PO #: {po_display}")
    y_cursor -= 0.75 * inch

    # PO Barcode
    po_barcode = generate_code128_barcode(label.po)
    renderPDF.draw(po_barcode, c, 1 * inch, y_cursor)
    y_cursor -= 1.25 * inch

    # Description
    c.drawString(1 * inch, y_cursor, "Desc:")
    y_cursor -= 0.3 * inch

    wrapped_lines = safe_wrap_text(label.description, max_chars=45)
    for line in wrapped_lines[:4]:  # prevent runaway overflow
        c.drawString(1 * inch, y_cursor, line)
        y_cursor -= 0.3 * inch

    y_cursor -= 0.25 * inch

    # SAP
    c.drawString(1 * inch, y_cursor, f"SAP #: {sanitize_text(label.sap)}")
    y_cursor -= 0.75 * inch

    # SAP Barcode
    sap_barcode = generate_code128_barcode(label.sap)
    renderPDF.draw(sap_barcode, c, 1 * inch, y_cursor)


def generate_label_pdf(labels: list[Label]) -> bytes:
    """
    Generate a letter-sized PDF with one label per page.

    Args:
        labels: Label models to render.

    Returns:
        PDF bytes.
    """
    if not labels:
        raise ValueError("No labels provided for PDF generation.")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    for label in labels:
        _draw_static_text(c)
        _draw_label_fields(c, label)
        c.showPage()

    c.save()
    buffer.seek(0)

    return buffer.read()