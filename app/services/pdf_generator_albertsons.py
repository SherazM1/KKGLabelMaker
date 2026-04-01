"""PDF generator for Albertsons carton labels."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.models.albertsons_label import AlbertsonsLabel
from app.utils.formatting import sanitize_text


PAGE_WIDTH, PAGE_HEIGHT = letter
LEFT_MARGIN = 48
RIGHT_MARGIN = 48


def _draw_divider(c: canvas.Canvas, y: float) -> None:
    c.setLineWidth(1)
    c.line(LEFT_MARGIN, y, PAGE_WIDTH - RIGHT_MARGIN, y)


def _draw_label_page(c: canvas.Canvas, label: AlbertsonsLabel) -> None:
    c.setFillColorRGB(0, 0, 0)

    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 68, "CARTON LABEL")

    ship_block_top = PAGE_HEIGHT - 128
    left_x = LEFT_MARGIN
    right_x = PAGE_WIDTH / 2 + 20

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_x, ship_block_top, "SHIP FROM")
    c.drawString(right_x, ship_block_top, "SHIP TO")

    c.setFont("Helvetica", 11)
    c.drawString(left_x, ship_block_top - 20, "KENDAL KING")
    c.drawString(left_x, ship_block_top - 36, "975 W OAKDALE RD")
    c.drawString(left_x, ship_block_top - 52, "GRAND PRAIRIE, TX 75050")

    c.drawString(right_x, ship_block_top - 20, sanitize_text(label.ship_to_name))
    c.drawString(right_x, ship_block_top - 36, sanitize_text(label.ship_to_address))
    c.drawString(
        right_x,
        ship_block_top - 52,
        (
            f"{sanitize_text(label.ship_to_city)}, "
            f"{sanitize_text(label.ship_to_state)} "
            f"{sanitize_text(label.ship_to_zip)}"
        ),
    )

    divider_one_y = PAGE_HEIGHT - 202
    _draw_divider(c, divider_one_y)

    order_top_y = divider_one_y - 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_x, order_top_y, "PURCHASE ORDER#")
    c.drawString(left_x + 150, order_top_y, sanitize_text(label.po_number))

    c.drawString(left_x, order_top_y - 22, "ITEM#")
    c.drawString(left_x + 150, order_top_y - 22, sanitize_text(label.item_number))

    c.drawString(left_x, order_top_y - 44, "DESC")
    c.setFont("Helvetica", 11)
    c.drawString(left_x + 150, order_top_y - 44, sanitize_text(label.description))

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, order_top_y - 22, f"Qty {sanitize_text(label.quantity)}")

    divider_two_y = order_top_y - 68
    _draw_divider(c, divider_two_y)

    center_y = divider_two_y - 64
    c.setFont("Helvetica-Bold", 44)
    c.drawCentredString(PAGE_WIDTH / 2, center_y, sanitize_text(label.dc_label))
    c.drawCentredString(PAGE_WIDTH / 2, center_y - 56, sanitize_text(label.dc_value))
    c.drawCentredString(PAGE_WIDTH / 2, center_y - 112, sanitize_text(label.carton_number))

    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(PAGE_WIDTH / 2, 56, "DO NOT DESTROY")


def generate_albertsons_pdf(labels: list[AlbertsonsLabel]) -> bytes:
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
