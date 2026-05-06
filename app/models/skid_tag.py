"""SKID tag data model definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SkidTag:
    """Represents one generated pallet/skid tag."""

    dc: str
    po: str
    upc: str
    quantity: str
    pallet_number: int
    pallet_total: int
    source_row_number: int

    def __post_init__(self) -> None:
        self.dc = self.dc.strip()
        self.po = self.po.strip()
        self.upc = self.upc.strip()
        self.quantity = self.quantity.strip()

    @property
    def po_display(self) -> str:
        return f"{self.po}-{self.dc}" if self.dc and not self.po.endswith(f"-{self.dc}") else self.po

    @property
    def pallet_display(self) -> str:
        return f"Pallet {self.pallet_number} of {self.pallet_total}"
