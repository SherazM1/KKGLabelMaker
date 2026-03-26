"""Barcode service for generating Code128 encoded assets."""

from __future__ import annotations

from reportlab.graphics.barcode import createBarcodeDrawing


def generate_code128_barcode(
    data: str,
    *,
    bar_height: float = 28,
    bar_width: float = 0.72,
):
    """
    Generate a Code128 barcode drawing object for rendering into PDF.
    Size must be defined at creation time.
    """

    if not data:
        raise ValueError("Barcode data cannot be empty.")

    return createBarcodeDrawing(
        "Code128",
        value=data,
        barHeight=bar_height,
        barWidth=bar_width,
        humanReadable=False,
    )