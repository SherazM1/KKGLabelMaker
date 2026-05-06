"""PDF generator for SKID tags."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from app.models.skid_tag import SkidTag


PAGE_WIDTH, PAGE_HEIGHT = letter
TIMES_NEW_ROMAN = "SkidTagsTimesNewRoman"
APTOS_NARROW = "SkidTagsAptosNarrow"
TAG_FONT_SIZE = 72
PO_VALUE_FONT_SIZE = 60
LINE_GAP = 102
Y_START = 600


def _font_candidates(*names: str) -> list[Path]:
    roots = [
        Path(r"C:\Windows\Fonts"),
        Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts",
    ]
    return [root / name for root in roots for name in names]


def _register_font(font_name: str, candidates: list[Path], fallback_name: str) -> str:
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name

    for candidate in candidates:
        if candidate.exists():
            pdfmetrics.registerFont(TTFont(font_name, str(candidate)))
            return font_name

    return fallback_name


def _register_skid_tag_fonts() -> tuple[str, str]:
    times_font = _register_font(
        TIMES_NEW_ROMAN,
        _font_candidates("times.ttf"),
        "Times-Roman",
    )
    aptos_font = _register_font(
        APTOS_NARROW,
        _font_candidates(
            "AptosNarrow.ttf",
            "AptosNarrow-Regular.ttf",
            "aptosnarrow.ttf",
            "aptosnarrow-regular.ttf",
            "Aptos-Narrow.ttf",
            "Aptos-Narrow-Regular.ttf",
            "ARIALN.TTF",
        ),
        "Helvetica",
    )
    return times_font, aptos_font


def _draw_centered(
    pdf: canvas.Canvas,
    text: str,
    y: float,
    font_name: str,
    font_size: int,
) -> None:
    pdf.setFont(font_name, font_size)
    pdf.drawCentredString(PAGE_WIDTH / 2, y, text)


def _draw_centered_po_line(
    pdf: canvas.Canvas,
    po_value: str,
    y: float,
    times_font: str,
    aptos_font: str,
) -> None:
    label = "PO "
    label_width = pdfmetrics.stringWidth(label, times_font, TAG_FONT_SIZE)
    value_width = pdfmetrics.stringWidth(po_value, aptos_font, PO_VALUE_FONT_SIZE)
    x = (PAGE_WIDTH - label_width - value_width) / 2

    pdf.setFont(times_font, TAG_FONT_SIZE)
    pdf.drawString(x, y, label)
    pdf.setFont(aptos_font, PO_VALUE_FONT_SIZE)
    pdf.drawString(x + label_width, y + 6, po_value)


def _draw_tag_page(pdf: canvas.Canvas, tag: SkidTag) -> None:
    times_font, aptos_font = _register_skid_tag_fonts()

    y = Y_START
    _draw_centered(pdf, f"DC {tag.dc}", y, times_font, TAG_FONT_SIZE)

    y -= LINE_GAP
    _draw_centered_po_line(pdf, tag.po_display, y, times_font, aptos_font)

    y -= LINE_GAP
    _draw_centered(pdf, f"UPC {tag.upc}", y, times_font, TAG_FONT_SIZE)

    y -= LINE_GAP
    _draw_centered(pdf, tag.pallet_display, y, times_font, TAG_FONT_SIZE)

    y -= LINE_GAP
    _draw_centered(pdf, f"Qty: {tag.quantity}", y, times_font, TAG_FONT_SIZE)


def generate_skid_tags_pdf(tags: list[SkidTag]) -> bytes:
    if not tags:
        raise ValueError("No SKID tags provided for PDF generation.")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    for index, tag in enumerate(tags):
        _draw_tag_page(pdf, tag)
        if index < len(tags) - 1:
            pdf.showPage()

    pdf.save()
    buffer.seek(0)
    return buffer.read()
