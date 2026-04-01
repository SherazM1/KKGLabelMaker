"""Data model for Albertsons carton labels."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AlbertsonsLabel:
    ship_to_name: str
    ship_to_address: str
    ship_to_city: str
    ship_to_state: str
    ship_to_zip: str
    po_number: str
    item_number: str
    description: str
    quantity: str
    dc_label: str
    dc_value: str
    carton_number: str
