"""PDF generator for Sam's GCI 4x6 labels."""

from __future__ import annotations

from io import BytesIO

from reportlab.graphics import renderPDF
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from app.models.sams_gci_label import SamsGciPayload, SamsGciTopLabelRow
from app.services.barcode_service import generate_code128_barcode
from app.utils.formatting import sanitize_text


PAGE_WIDTH = 4 * inch
PAGE_HEIGHT = 6 * inch

LEFT_MARGIN = 0.16 * inch
RIGHT_MARGIN = 0.16 * inch
TOP_MARGIN = 0.15 * inch
BOTTOM_MARGIN = 0.15 * inch
PRINT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN


def _draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    *,
    font_name: str = "Helvetica",
    font_size: float = 8.0,
    line_height: float = 9.0,
    max_lines: int = 2,
) -> float:
    clean = sanitize_text(text)
    if not clean:
        return y

    words = clean.split()
    lines: list[str] = []
    line = ""

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

    c.setFont(font_name, font_size)
    for value in lines:
        c.drawString(x, y, value)
        y -= line_height

    return y


def _create_fitted_barcode(
    data: str,
    *,
    target_width: float,
    bar_height: float,
    max_bar_width: float,
    min_bar_width: float,
    step: float = 0.02,
):
    bar_width = max_bar_width
    best = generate_code128_barcode(data, bar_height=bar_height, bar_width=bar_width)

    while bar_width >= min_bar_width:
        candidate = generate_code128_barcode(
            data,
            bar_height=bar_height,
            bar_width=bar_width,
        )
        if candidate.width <= target_width:
            return candidate
        best = candidate
        bar_width -= step

    return best


def _draw_top_section(c: canvas.Canvas, top_label: SamsGciTopLabelRow) -> float:
    top_y = PAGE_HEIGHT - TOP_MARGIN - 6

    col_gap = 0.12 * inch
    col_width = (PRINT_WIDTH - col_gap) / 2
    left_x = LEFT_MARGIN
    right_x = LEFT_MARGIN + col_width + col_gap
    divider_x = LEFT_MARGIN + col_width + (col_gap / 2)

    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    c.setFont("Helvetica-Bold", 8.8)
    c.drawString(left_x, top_y, "SHIP FROM")
    c.drawString(right_x, top_y, "SHIP TO")

    row_y = top_y - 11
    c.setFont("Helvetica", 8.2)
    c.drawString(left_x, row_y, sanitize_text(top_label.shipper_name))
    c.drawString(right_x, row_y, sanitize_text(top_label.ship_to_name))

    row_y -= 10
    left_end_y = _draw_wrapped(
        c,
        top_label.shipper_address,
        left_x,
        row_y,
        col_width,
        font_name="Helvetica",
        font_size=8.0,
        line_height=8.8,
        max_lines=2,
    )
    right_end_y = _draw_wrapped(
        c,
        top_label.ship_to_address,
        right_x,
        row_y,
        col_width,
        font_name="Helvetica",
        font_size=8.0,
        line_height=8.8,
        max_lines=2,
    )

    c.setFont("Helvetica", 8.2)
    c.drawString(
        left_x,
        left_end_y,
        f"{sanitize_text(top_label.shipper_city)}, "
        f"{sanitize_text(top_label.shipper_state)} {sanitize_text(top_label.shipper_zip)}",
    )
    c.drawString(
        right_x,
        right_end_y,
        f"{sanitize_text(top_label.ship_to_city)}, "
        f"{sanitize_text(top_label.ship_to_state)} {sanitize_text(top_label.ship_to_zip)}",
    )

    top_block_bottom_y = min(left_end_y, right_end_y) - 7
    c.setLineWidth(0.9)
    c.line(divider_x, top_y + 2, divider_x, top_block_bottom_y + 3)
    c.line(LEFT_MARGIN, top_block_bottom_y, PAGE_WIDTH - RIGHT_MARGIN, top_block_bottom_y)

    title_y = top_block_bottom_y - 11
    c.setFont("Helvetica-Bold", 8.8)
    c.drawCentredString(PAGE_WIDTH / 2, title_y, "SAM'S GCI PALLET LABEL")

    info_y = title_y - 11
    c.setFont("Helvetica-Bold", 8.4)
    c.drawString(LEFT_MARGIN, info_y, f"PO#: {sanitize_text(top_label.po_number)}")
    c.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        info_y,
        f"CLUB#: {sanitize_text(top_label.club_display)}",
    )

    info_y -= 10
    c.setFont("Helvetica-Bold", 8.4)
    c.drawString(LEFT_MARGIN, info_y, "ITEM#:")
    c.setFont("Helvetica", 8.4)
    c.drawString(LEFT_MARGIN + 30, info_y, sanitize_text(top_label.item_number))
    c.setFont("Helvetica-Bold", 8.4)
    c.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        info_y,
        f"QTY: {sanitize_text(top_label.quantity)}",
    )

    info_y -= 10
    c.setFont("Helvetica", 7.8)
    desc_label = f"DESC: {sanitize_text(top_label.description)}"
    _draw_wrapped(
        c,
        desc_label,
        LEFT_MARGIN,
        info_y,
        PRINT_WIDTH,
        font_name="Helvetica",
        font_size=7.8,
        line_height=8.6,
        max_lines=2,
    )

    barcode_value = sanitize_text(top_label.top_barcode_value)
    if barcode_value:
        top_barcode = _create_fitted_barcode(
            barcode_value,
            target_width=PRINT_WIDTH * 0.94,
            bar_height=0.46 * inch,
            max_bar_width=1.24,
            min_bar_width=0.64,
        )
        top_barcode_x = (PAGE_WIDTH - top_barcode.width) / 2
        top_barcode_bottom = info_y - 47
        renderPDF.draw(top_barcode, c, top_barcode_x, top_barcode_bottom)
        c.setFont("Helvetica", 8.8)
        c.drawCentredString(PAGE_WIDTH / 2, top_barcode_bottom - 11, barcode_value)
        return top_barcode_bottom - 18

    return info_y - 8


def _draw_bottom_rows(c: canvas.Canvas, payload: SamsGciPayload, start_y: float) -> None:
    c.setLineWidth(0.8)
    c.line(LEFT_MARGIN, start_y, PAGE_WIDTH - RIGHT_MARGIN, start_y)

    row_count = len(payload.bottom_rows)
    if row_count <= 0:
        return

    available_height = max(18.0, start_y - BOTTOM_MARGIN - 4)
    row_block_height = available_height / row_count
    # Keep rows within page bounds when many bottom rows are present.
    row_block_height = max(11.0, min(row_block_height, 58.0))

    barcode_region_width = PRINT_WIDTH * 0.35
    text_x = LEFT_MARGIN + barcode_region_width + 6
    text_width = PAGE_WIDTH - RIGHT_MARGIN - text_x

    y = start_y - 5
    for row in payload.bottom_rows:
        barcode_value = sanitize_text(row.barcode_value)
        quantity_value = sanitize_text(row.quantity)
        item_value = sanitize_text(row.item_number)
        desc_value = sanitize_text(row.description)
        program_value = sanitize_text(row.program_name)

        barcode_height = max(0.15 * inch, min(0.26 * inch, row_block_height * 0.42))
        barcode_target_width = barcode_region_width - 4

        if barcode_value:
            row_barcode = _create_fitted_barcode(
                barcode_value,
                target_width=barcode_target_width,
                bar_height=barcode_height,
                max_bar_width=1.00,
                min_bar_width=0.36,
            )
            row_barcode_x = LEFT_MARGIN + 1
            row_barcode_bottom = y - barcode_height + 1
            renderPDF.draw(row_barcode, c, row_barcode_x, row_barcode_bottom)
            c.setFont("Helvetica", 6.3)
            c.drawCentredString(
                LEFT_MARGIN + (barcode_region_width / 2),
                row_barcode_bottom - 7.0,
                barcode_value,
            )

        top_text_y = y - 0.5
        c.setFont("Helvetica-Bold", 7.0)
        c.drawString(text_x, top_text_y, f"ITEM#: {item_value}")
        c.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, top_text_y, f"QTY: {quantity_value}")

        mid_text_y = top_text_y - 8.5
        c.setFont("Helvetica", 6.9)
        _draw_wrapped(
            c,
            desc_value,
            text_x,
            mid_text_y,
            text_width,
            font_name="Helvetica",
            font_size=6.9,
            line_height=7.4,
            max_lines=2,
        )

        if program_value:
            c.setFont("Helvetica-Oblique", 6.5)
            c.drawString(text_x, y - row_block_height + 7.5, program_value)

        row_bottom = y - row_block_height
        c.setLineWidth(0.55)
        c.line(LEFT_MARGIN, row_bottom, PAGE_WIDTH - RIGHT_MARGIN, row_bottom)
        y = row_bottom


def _draw_gci_label_page(c: canvas.Canvas, payload: SamsGciPayload, top_label: SamsGciTopLabelRow) -> None:
    bottom_start_y = _draw_top_section(c, top_label)
    _draw_bottom_rows(c, payload, bottom_start_y)


def generate_sams_gci_pdf(payload: SamsGciPayload) -> bytes:
    """Generate Sam's GCI label PDF bytes with 2 pages per MDG row."""
    if not payload.mdg_labels:
        raise ValueError("No MDG labels provided for GCI PDF generation.")
    if not payload.bottom_rows:
        raise ValueError("No GCI bottom rows provided for GCI PDF generation.")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    for top_label in payload.mdg_labels:
        for _ in range(2):
            _draw_gci_label_page(c, payload, top_label)
            c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.read()
