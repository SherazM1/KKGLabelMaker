"""Label data model definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Label:
    """
    Represents one shipping label input row.

    All fields are stored exactly as received from Excel.
    Formatting rules (e.g., dropping leading zeros for display)
    are handled via computed properties.
    """

    supplier: str
    store: str
    po: str
    description: str
    sap: str

    def __post_init__(self) -> None:
        # Normalize whitespace but preserve leading zeros and casing.
        self.supplier = self.supplier.strip()
        self.store = self.store.strip()
        self.po = self.po.strip()
        self.description = self.description.strip()
        self.sap = self.sap.strip()

    @property
    def po_display(self) -> str:
        """
        PO value for human-readable display (leading zeros removed).
        """
        return self.po.lstrip("0") or "0"

    @property
    def po_barcode(self) -> str:
        """
        PO value encoded into barcode (exact original string).
        """
        return self.po

    @property
    def sap_barcode(self) -> str:
        """
        SAP value encoded into barcode (exact original string).
        """
        return self.sap