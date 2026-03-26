"""PDF generator service for creating print-ready label documents."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF

from app.models.label import Label
from app.services.barcode_service import generate_code128_barcode
from app.utils.formatting import drop_leading_zeros, sanitize_text


PAGE_WIDTH, PAGE_HEIGHT = letter


def _draw_wrapped_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    line_height: float,
    max_lines: int = 2,
) -> float:
    """Draw wrapped text with controlled line count."""
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        test_line = f"{current} {word}".strip()
        if c.stringWidth(test_line, "Helvetica", 12) <= max_width:
            current = test_line
        else:
            lines.append(current)
            current = word

        if len(lines) >= max_lines:
            break

    if current and len(lines) < max_lines:
        lines.append(current)

    for line in lines:
        c.drawString(x, y, line)
        y -= line_height

    return y


def _draw_label_page(c: canvas.Canvas, label: Label) -> None:
    """Draw a single label page matching original layout structure."""

    left_margin = 1.0 * inch
    y = PAGE_HEIGHT - 1.0 * inch
    line_gap = 0.28 * inch

    c.setFont("Helvetica", 12)

    # 1️⃣ Shipper (Top)
    c.drawString(left_margin, y, f"Shipper: {sanitize_text(label.supplier)}")
    y -= line_gap

    # 2️⃣ Static ATTN + Dept
    c.drawString(left_margin, y, "ATTN: Dept. Mgr. Dept#: 5")
    y -= line_gap

    c.drawString(left_margin, y, "ELECTRONICS DEPARTMENT")
    y -= line_gap

    # 3️⃣ Store
    c.drawString(left_margin, y, f"STORE #: {sanitize_text(label.store)}")
    y -= line_gap

    # 4️⃣ Contents
    c.drawString(left_margin, y, "CONTENTS: SIGNAGE KITS")
    y -= line_gap

    # 5️⃣ PO
    po_display = drop_leading_zeros(label.po)
    c.drawString(left_margin, y, f"PO #: {po_display}")
    y -= 0.35 * inch

    # PO Barcode (tight placement)
    po_barcode = generate_code128_barcode(label.po)
    renderPDF.draw(po_barcode, c, left_margin, y)
    y -= 0.9 * inch

    # 6️⃣ Description
    c.drawString(left_margin, y, "Desc:")
    y -= 0.25 * inch

    y = _draw_wrapped_text(
        c,
        sanitize_text(label.description),
        left_margin,
        y,
        max_width=4.5 * inch,
        line_height=0.25 * inch,
        max_lines=2,
    )

    y -= 0.15 * inch

    # 7️⃣ SAP
    c.drawString(left_margin, y, f"SAP #: {sanitize_text(label.sap)}")
    y -= 0.35 * inch

    # SAP Barcode
    sap_barcode = generate_code128_barcode(label.sap)
    renderPDF.draw(sap_barcode, c, left_margin, y)
    y -= 0.9 * inch

    # 8️⃣ Category + Quantity
    c.drawString(left_margin, y, "CAT: ELECTRONICS DEPT.")
    y -= line_gap

    c.drawString(left_margin, y, "QTY: 1")
    y -= 0.5 * inch

    # 9️⃣ Footer
    c.setFont("Helvetica", 10)
    c.drawString(
        left_margin,
        y,
        "For questions or additional information, call",
    )
    y -= 0.22 * inch
    c.drawString(left_margin, y, "Tara Webb 501-454-6407")


def generate_label_pdf(labels: list[Label]) -> bytes:
    """Generate a letter-sized PDF with one label per page."""

    if not labels:
        raise ValueError("No labels provided for PDF generation.")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    for label in labels:
        _draw_label_page(c, label)
        c.showPage()

    c.save()
    buffer.seek(0)

    return buffer.read()