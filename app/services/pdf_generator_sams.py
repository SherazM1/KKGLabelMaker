"""PDF generator for Sam's warehouse 4x6 labels."""

from __future__ import annotations

from io import BytesIO

from reportlab.graphics import renderPDF
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from app.models.sams_label import SamsLabel
from app.services.barcode_service import generate_code128_barcode
from app.utils.formatting import sanitize_text


PAGE_WIDTH = 4 * inch
PAGE_HEIGHT = 6 * inch
LEFT_MARGIN = 0.28 * inch


def _draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font_name: str = "Helvetica",
    font_size: float = 9,
    line_height: float = 11,
    max_lines: int = 3,
) -> float:
    clean = sanitize_text(text)
    if not clean:
        return y

    c.setFont(font_name, font_size)
    words = clean.split()
    line = ""
    lines: list[str] = []

    for word in words:
        candidate = f"{line} {word}".strip()
        if c.stringWidth(candidate, font_name, font_size) <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
            if len(lines) >= max_lines:
                break

    if line and len(lines) < max_lines:
        lines.append(line)

    for value in lines:
        c.drawString(x, y, value)
        y -= line_height

    return y


def _draw_label_page(c: canvas.Canvas, label: SamsLabel) -> None:
    c.setFont("Helvetica-Bold", 12)
    c.drawString(LEFT_MARGIN, PAGE_HEIGHT - 0.45 * inch, "SAM'S WAREHOUSE LABEL")

    c.setFont("Helvetica", 9)
    y = PAGE_HEIGHT - 0.75 * inch
    c.drawString(LEFT_MARGIN, y, f"FROM: {sanitize_text(label.shipper_name)}")
    y -= 11
    y = _draw_wrapped(c, label.shipper_address, LEFT_MARGIN + 34, y, PAGE_WIDTH - 0.7 * inch)
    c.drawString(LEFT_MARGIN, y, f"{sanitize_text(label.shipper_city)}, {sanitize_text(label.shipper_state)} {label.shipper_zip}")

    y -= 18
    c.drawString(LEFT_MARGIN, y, f"TO: {sanitize_text(label.ship_to_name)}")
    y -= 11
    y = _draw_wrapped(c, label.ship_to_address, LEFT_MARGIN + 18, y, PAGE_WIDTH - 0.7 * inch)
    c.drawString(LEFT_MARGIN, y, f"{sanitize_text(label.ship_to_city)}, {sanitize_text(label.ship_to_state)} {label.ship_to_zip}")

    postal_barcode_value = "420" + label.ship_to_zip.replace("-", "")
    postal_barcode = generate_code128_barcode(
        postal_barcode_value,
        bar_height=42,
        bar_width=0.95,
    )

    postal_y = PAGE_HEIGHT - 3.15 * inch
    renderPDF.draw(postal_barcode, c, LEFT_MARGIN, postal_y)
    c.setFont("Helvetica", 10)
    c.drawString(LEFT_MARGIN, postal_y - 12, f"(420){label.ship_to_zip}")

    c.setFont("Helvetica", 9)
    meta_y = postal_y - 30
    c.drawString(LEFT_MARGIN, meta_y, f"PO #: {label.po_number}")
    c.drawString(PAGE_WIDTH / 2, meta_y, f"QTY: {label.quantity}")
    meta_y -= 11
    c.drawString(LEFT_MARGIN, meta_y, f"WHSE: {label.whse}")
    c.drawString(PAGE_WIDTH / 2, meta_y, f"TYPE: {label.type_code}")
    meta_y -= 11
    c.drawString(LEFT_MARGIN, meta_y, f"DEPT: {label.dept}")
    c.drawString(PAGE_WIDTH / 2, meta_y, f"ITEM #: {label.item_number}")
    meta_y -= 11
    _draw_wrapped(c, f"DESC: {label.description}", LEFT_MARGIN, meta_y, PAGE_WIDTH - 0.55 * inch, max_lines=2)

    bottom_barcode = generate_code128_barcode(
        label.upc,
        bar_height=52,
        bar_width=1.0,
    )
    bottom_y = 0.82 * inch
    renderPDF.draw(bottom_barcode, c, LEFT_MARGIN, bottom_y)
    c.setFont("Helvetica", 10)
    c.drawString(LEFT_MARGIN, bottom_y - 12, label.upc)


def generate_sams_pdf(labels: list[SamsLabel]) -> bytes:
    if not labels:
        raise ValueError("No labels provided for PDF generation.")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    for label in labels:
        for _ in range(2):
            _draw_label_page(c, label)
            c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.read()
