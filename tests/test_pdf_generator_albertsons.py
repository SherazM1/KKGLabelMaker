"""Tests for Albertsons PDF generation."""

from __future__ import annotations

from app.models.albertsons_label import AlbertsonsLabel
from app.services.pdf_generator_albertsons import _draw_label_page


class RecordingCanvas:
    def __init__(self) -> None:
        self.strings: list[str] = []

    def setFillColorRGB(self, *_args: object) -> None:
        pass

    def setFont(self, *_args: object) -> None:
        pass

    def drawCentredString(self, _x: float, _y: float, text: str) -> None:
        self.strings.append(text)

    def drawRightString(self, _x: float, _y: float, text: str) -> None:
        self.strings.append(text)

    def drawString(self, _x: float, _y: float, text: str) -> None:
        self.strings.append(text)

    def setLineWidth(self, *_args: object) -> None:
        pass

    def line(self, *_args: object) -> None:
        pass


def _label() -> AlbertsonsLabel:
    return AlbertsonsLabel(
        ship_to_name="Store",
        ship_to_address="123 Main St",
        ship_to_city="Dallas",
        ship_to_state="TX",
        ship_to_zip="75001",
        po_number="PO-1",
        item_number="EXCEL-ITEM",
        description="Display",
        quantity="12",
        dc_label="DC#",
        dc_value="WNCA",
        carton_number="1",
    )


def test_albertsons_manual_values_override_label_values() -> None:
    canvas = RecordingCanvas()

    _draw_label_page(
        canvas,
        _label(),
        manual_item_number="MANUAL-ITEM",
        manual_qty="24",
        manual_po_type="PO-TYPE",
    )

    assert "MANUAL-ITEM" in canvas.strings
    assert "Qty 24" in canvas.strings
    assert "PO-TYPE" in canvas.strings
    assert "EXCEL-ITEM" not in canvas.strings
    assert "Qty 12" not in canvas.strings


def test_albertsons_blank_manual_values_preserve_existing_values() -> None:
    canvas = RecordingCanvas()

    _draw_label_page(canvas, _label())

    assert "EXCEL-ITEM" in canvas.strings
    assert "Qty 12" in canvas.strings
    assert "1" in canvas.strings
