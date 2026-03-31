"""Data model for Sam's warehouse 4x6 labels."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SamsLabel:
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
    quantity: str
    upc: str
    whse: str
    type_code: str
    dept: str
    item_number: str
    description: str
