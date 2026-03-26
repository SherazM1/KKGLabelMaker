"""Barcode service for generating Code128 encoded assets."""

from __future__ import annotations

from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing


def generate_code128_barcode(data: str) -> Drawing:
    """
    Generate a Code128 barcode drawing object.

    This barcode:
    - Preserves leading zeros
    - Supports alphanumeric input
    - Uses automatic subset switching (safer than forcing subset A)

    Args:
        data: Raw barcode input text (exact value from Excel).

    Returns:
        A ReportLab Drawing object representing the barcode.

    Raises:
        ValueError: If data is empty.
    """
    if not data:
        raise ValueError("Barcode data cannot be empty.")

    barcode = code128.Code128(
        data,
        barHeight=40,     # Tunable later
        barWidth=1.0,     # Tunable density
        humanReadable=False,
    )

    drawing = Drawing(barcode.width, barcode.height)
    drawing.add(barcode)

    return drawing