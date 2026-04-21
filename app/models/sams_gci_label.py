"""Data models for Sam's GCI label workflow."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SamsGciBottomRow:
    program_name: str
    item_number: str
    quantity: str
    barcode_value: str
    description: str


@dataclass(slots=True)
class SamsGciTopLabelRow:
    shipper_name: str
    shipper_address: str
    shipper_city: str
    shipper_state: str
    shipper_zip: str
    ship_to_name: str
    ship_to_address: str
    ship_to_city: str
    ship_to_state: str
    ship_to_zip: str
    po_number: str
    club_number: str
    whse: str
    item_number: str
    description: str
    quantity: str

    @property
    def club_display(self) -> str:
        """Display CLUB# when present, otherwise fallback to WHSE."""
        return self.club_number or self.whse

    @property
    def top_barcode_value(self) -> str:
        """Top barcode value for the GCI layout is Item #."""
        return self.item_number


@dataclass(slots=True)
class SamsGciPayload:
    mdg_labels: list[SamsGciTopLabelRow]
    bottom_rows: list[SamsGciBottomRow]

    @property
    def page_count(self) -> int:
        """Each MDG row renders two pages."""
        return len(self.mdg_labels) * 2
