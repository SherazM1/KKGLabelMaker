"""PDF generator for Andersons labels."""

from __future__ import annotations

from io import BytesIO

from reportlab.graphics import renderPDF
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from app.models.andersons_label import AndersonsLabel
from app.services.barcode_service import generate_code128_barcode
from app.utils.formatting import sanitize_text


PAGE_WIDTH = 612.16
PAGE_HEIGHT = 792.07
LEFT_MARGIN = 48
RIGHT_MARGIN = 48
CENTER_X = PAGE_WIDTH / 2
PRINT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN


def _draw_line(c: canvas.Canvas, y: float, line_width: float = 1.0) -> None:
    c.setLineWidth(line_width)
    c.line(LEFT_MARGIN, y, PAGE_WIDTH - RIGHT_MARGIN, y)


def _draw_wrapped_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    *,
    font_name: str = "Helvetica",
    font_size: float = 15,
    line_height: float = 17,
    max_lines: int = 2,
) -> float:
    clean = sanitize_text(text)
    if not clean:
        return y

    words = clean.split()
    lines: list[str] = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if c.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
            if len(lines) >= max_lines:
                break

    if current and len(lines) < max_lines:
        lines.append(current)

    c.setFont(font_name, font_size)
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height

    return y


def _draw_fitted_string(
    c: canvas.Canvas,
    x: float,
    y: float,
    text: str,
    max_width: float,
    *,
    font_name: str = "Helvetica",
    font_size: float = 15,
    min_font_size: float = 8,
) -> None:
    clean = sanitize_text(text)
    current_size = font_size
    while current_size > min_font_size and c.stringWidth(clean, font_name, current_size) > max_width:
        current_size -= 0.5

    c.setFont(font_name, current_size)
    c.drawString(x, y, clean)


def _create_fitted_barcode(
    data: str,
    *,
    target_width: float,
    bar_height: float,
    max_bar_width: float,
    min_bar_width: float,
):
    bar_width = max_bar_width
    best = generate_code128_barcode(data, bar_height=bar_height, bar_width=bar_width)

    while bar_width >= min_bar_width:
        candidate = generate_code128_barcode(data, bar_height=bar_height, bar_width=bar_width)
        if candidate.width <= target_width:
            return candidate
        best = candidate
        bar_width -= 0.02

    return best


def _draw_label_value(
    c: canvas.Canvas,
    label_text: str,
    value: str,
    x: float,
    y: float,
    value_x: float,
    max_width: float,
) -> None:
    c.setFont("Helvetica-Bold", 17)
    c.drawString(x, y, label_text)
    _draw_fitted_string(c, value_x, y, value, max_width, font_size=16, min_font_size=8)


def _draw_label_page(
    c: canvas.Canvas,
    label: AndersonsLabel,
    ship_from: dict[str, str],
) -> None:
    c.setFillColorRGB(0, 0, 0)
    c.setStrokeColorRGB(0, 0, 0)

    top_y = PAGE_HEIGHT - 46
    c.setFont("Helvetica-Bold", 18)
    c.drawString(LEFT_MARGIN, top_y, "SHIP FROM: KENDAL KING")

    c.setFont("Helvetica-Bold", 17)
    c.drawString(LEFT_MARGIN, top_y - 34, "CLIENT")
    c.setFont("Helvetica", 16)
    c.drawString(LEFT_MARGIN + 82, top_y - 34, sanitize_text(label.client))

    c.setFont("Helvetica", 15)
    c.drawString(LEFT_MARGIN, top_y - 62, f"C/O: {sanitize_text(ship_from['care_of'])}")
    c.drawString(LEFT_MARGIN, top_y - 83, sanitize_text(ship_from["address"]))
    c.drawString(
        LEFT_MARGIN,
        top_y - 104,
        (
            f"{sanitize_text(ship_from['city'])}, "
            f"{sanitize_text(ship_from['state'])} "
            f"{sanitize_text(ship_from['zip_code'])}"
        ),
    )

    _draw_line(c, top_y - 126, 1.1)

    field_y = top_y - 162
    _draw_label_value(c, "BRAND", label.brand, LEFT_MARGIN, field_y, LEFT_MARGIN + 78, PRINT_WIDTH - 78)

    desc_y = field_y - 38
    c.setFont("Helvetica-Bold", 17)
    c.drawString(LEFT_MARGIN, desc_y, "DESC")
    _draw_wrapped_text(
        c,
        label.description,
        LEFT_MARGIN + 62,
        desc_y,
        PRINT_WIDTH - 62,
        font_size=15,
        line_height=17,
        max_lines=2,
    )

    qty_y = desc_y - 66
    _draw_label_value(
        c,
        "ORDER QTY",
        label.ordered_quantity,
        LEFT_MARGIN,
        qty_y,
        LEFT_MARGIN + 122,
        120,
    )
    _draw_label_value(
        c,
        "UOM",
        label.unit_of_measure,
        LEFT_MARGIN + 285,
        qty_y,
        LEFT_MARGIN + 338,
        140,
    )

    _draw_line(c, qty_y - 34, 1.1)

    po_y = qty_y - 72
    _draw_label_value(c, "PO NAME", label.po_name, LEFT_MARGIN, po_y, LEFT_MARGIN + 105, PRINT_WIDTH - 105)

    po_number_y = po_y - 42
    c.setFont("Helvetica-Bold", 17)
    c.drawString(LEFT_MARGIN, po_number_y, "PO NUMBER")
    c.setFont("Helvetica", 15)
    c.drawString(LEFT_MARGIN + 126, po_number_y, sanitize_text(label.po_number))

    po_barcode = _create_fitted_barcode(
        label.po_number,
        target_width=PRINT_WIDTH * 0.72,
        bar_height=0.55 * inch,
        max_bar_width=1.05,
        min_bar_width=0.52,
    )
    po_barcode_x = (PAGE_WIDTH - po_barcode.width) / 2
    po_barcode_y = po_number_y - 58
    renderPDF.draw(po_barcode, c, po_barcode_x, po_barcode_y)

    c.setFont("Helvetica", 12)
    po_text_width = c.stringWidth(label.po_number, "Helvetica", 12)
    c.drawString(CENTER_X - (po_text_width / 2), po_barcode_y - 17, sanitize_text(label.po_number))

    _draw_line(c, po_barcode_y - 42, 1.1)

    upc_label_y = po_barcode_y - 80
    c.setFont("Helvetica-Bold", 18)
    c.drawString(LEFT_MARGIN, upc_label_y, "UPC")

    upc_barcode = _create_fitted_barcode(
        label.upc,
        target_width=PRINT_WIDTH * 0.90,
        bar_height=1.05 * inch,
        max_bar_width=1.48,
        min_bar_width=0.72,
    )
    upc_barcode_x = (PAGE_WIDTH - upc_barcode.width) / 2
    upc_barcode_y = 80
    renderPDF.draw(upc_barcode, c, upc_barcode_x, upc_barcode_y)

    c.setFont("Helvetica", 14)
    upc_text_width = c.stringWidth(label.upc, "Helvetica", 14)
    c.drawString(CENTER_X - (upc_text_width / 2), upc_barcode_y - 22, sanitize_text(label.upc))


def generate_andersons_pdf(
    labels: list[AndersonsLabel],
    ship_from: dict[str, str],
) -> bytes:
    if not labels:
        raise ValueError("No labels provided for PDF generation.")

    required_ship_from = {"care_of", "address", "city", "state", "zip_code"}
    missing_ship_from = sorted(required_ship_from - set(ship_from))
    if missing_ship_from:
        raise ValueError("Ship From is missing: " + ", ".join(missing_ship_from))

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    for label in labels:
        _draw_label_page(c, label, ship_from)
        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.read()

