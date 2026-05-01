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
ORDER_LABEL_FONT_SIZE = 20
ORDER_VALUE_FONT_SIZE = 18
ORDER_DESC_VALUE_FONT_SIZE = 16
ORDER_LABEL_X = LEFT_MARGIN
ORDER_PO_VALUE_X = LEFT_MARGIN + 205
ORDER_ITEM_VALUE_X = LEFT_MARGIN + 82
ORDER_DESC_VALUE_X = LEFT_MARGIN + 72
ORDER_ROW_GAP = 34
MIN_SHIP_TO_FONT_SIZE = 9


def _draw_divider(c: canvas.Canvas, y: float) -> None:
    c.setLineWidth(1)
    c.line(LEFT_MARGIN, y, PAGE_WIDTH - RIGHT_MARGIN, y)


def _draw_fitted_string(
    c: canvas.Canvas,
    x: float,
    y: float,
    text: str,
    max_width: float,
    font_name: str = "Helvetica",
    font_size: int = 13,
    min_font_size: int = MIN_SHIP_TO_FONT_SIZE,
) -> None:
    text = sanitize_text(text)
    current_size = font_size

    if hasattr(c, "stringWidth"):
        while (
            current_size > min_font_size
            and c.stringWidth(text, font_name, current_size) > max_width
        ):
            current_size -= 1

    c.setFont(font_name, current_size)
    c.drawString(x, y, text)


def _draw_label_page(
    c: canvas.Canvas,
    label: AlbertsonsLabel,
    manual_item_number: str = "",
    manual_qty: str = "",
    manual_po_type: str = "",
    qty_mode: str = "manual",
    identifier_mode: str = "item",
) -> None:
    identifier_label = "UPC#" if identifier_mode == "upc" else "ITEM#"
    identifier_value = (
        label.upc
        if identifier_mode == "upc"
        else manual_item_number.strip() or label.item_number
    )
    quantity = label.quantity if qty_mode == "auto" else manual_qty.strip()
    po_type = manual_po_type.strip() or label.carton_number

    c.setFillColorRGB(0, 0, 0)

    c.setFont("Helvetica-Bold", 30)
    header_y = PAGE_HEIGHT - 68
    c.drawCentredString(PAGE_WIDTH / 2, header_y, "CARTON LABEL")
    _draw_divider(c, header_y - 14)

    ship_section_top = PAGE_HEIGHT - 108
    _draw_divider(c, ship_section_top)

    ship_block_top = ship_section_top - 22
    left_x = LEFT_MARGIN
    right_x = PAGE_WIDTH / 2 + 20

    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_x, ship_block_top, "SHIP FROM")
    c.drawString(right_x, ship_block_top, "SHIP TO")

    c.setFont("Helvetica", 13)
    c.drawString(left_x, ship_block_top - 24, "KENDAL KING")
    c.drawString(left_x, ship_block_top - 42, "975 W OAKDALE RD")
    c.drawString(left_x, ship_block_top - 60, "GRAND PRAIRIE, TX 75050")

    ship_to_max_width = PAGE_WIDTH - RIGHT_MARGIN - right_x
    _draw_fitted_string(
        c,
        right_x,
        ship_block_top - 24,
        label.ship_to_name,
        ship_to_max_width,
    )
    _draw_fitted_string(
        c,
        right_x,
        ship_block_top - 42,
        label.ship_to_address,
        ship_to_max_width,
    )
    _draw_fitted_string(
        c,
        right_x,
        ship_block_top - 60,
        (
            f"{sanitize_text(label.ship_to_city)}, "
            f"{sanitize_text(label.ship_to_state)} "
            f"{sanitize_text(label.ship_to_zip)}"
        ),
        ship_to_max_width,
    )

    divider_one_y = ship_block_top - 76
    _draw_divider(c, divider_one_y)

    order_top_y = divider_one_y - 36
    c.setFont("Helvetica-Bold", ORDER_LABEL_FONT_SIZE)
    c.drawString(ORDER_LABEL_X, order_top_y, "PURCHASE ORDER#")
    c.setFont("Helvetica", ORDER_VALUE_FONT_SIZE)
    c.drawString(ORDER_PO_VALUE_X, order_top_y, sanitize_text(label.po_number))

    c.setFont("Helvetica-Bold", ORDER_LABEL_FONT_SIZE)
    c.drawString(ORDER_LABEL_X, order_top_y - ORDER_ROW_GAP, identifier_label)
    c.setFont("Helvetica", ORDER_VALUE_FONT_SIZE)
    c.drawString(
        ORDER_ITEM_VALUE_X,
        order_top_y - ORDER_ROW_GAP,
        sanitize_text(identifier_value),
    )

    c.setFont("Helvetica-Bold", ORDER_LABEL_FONT_SIZE)
    c.drawString(ORDER_LABEL_X, order_top_y - (ORDER_ROW_GAP * 2), "DESC")
    c.setFont("Helvetica", ORDER_DESC_VALUE_FONT_SIZE)
    c.drawString(
        ORDER_DESC_VALUE_X,
        order_top_y - (ORDER_ROW_GAP * 2),
        sanitize_text(label.description),
    )

    c.setFont("Helvetica-Bold", 18)
    c.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        order_top_y - ORDER_ROW_GAP,
        f"Qty {sanitize_text(quantity)}",
    )

    divider_two_y = order_top_y - 98
    _draw_divider(c, divider_two_y)

    center_y = divider_two_y - 56
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(PAGE_WIDTH / 2, center_y, sanitize_text(label.dc_label))
    c.setFont("Helvetica-Bold", 38)
    c.drawCentredString(PAGE_WIDTH / 2, center_y - 52, sanitize_text(label.dc_value))
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(PAGE_WIDTH / 2, center_y - 106, sanitize_text(po_type))

    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(PAGE_WIDTH / 2, 56, "DO NOT DESTROY")


def generate_albertsons_pdf(
    labels: list[AlbertsonsLabel],
    manual_item_number: str = "",
    manual_qty: str = "",
    manual_po_type: str = "",
    qty_mode: str = "manual",
    identifier_mode: str = "item",
) -> bytes:
    if not labels:
        raise ValueError("No labels provided for PDF generation.")

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    for label in labels:
        for _ in range(2):
            _draw_label_page(
                c,
                label,
                manual_item_number,
                manual_qty,
                manual_po_type,
                qty_mode,
                identifier_mode,
            )
            c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.read()
