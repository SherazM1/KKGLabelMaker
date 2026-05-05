"""Data model for Andersons labels."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AndersonsLabel:
    client: str
    upc: str
    brand: str
    description: str
    unit_of_measure: str
    ordered_quantity: str
    po_name: str
    po_number: str

