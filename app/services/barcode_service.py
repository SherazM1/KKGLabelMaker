"""Barcode service for generating Code128-A encoded assets."""

from __future__ import annotations

from reportlab.graphics.barcode import createBarcodeDrawing


def generate_code128_barcode(data: str):
    """
    Generate a Code128 barcode drawing object for rendering into PDF.
    """

    if not data:
        raise ValueError("Barcode data cannot be empty.")

    barcode = createBarcodeDrawing(
        "Code128",
        value=data,
        barHeight=40,
        barWidth=1.0,
        humanReadable=False,
    )

    return barcode