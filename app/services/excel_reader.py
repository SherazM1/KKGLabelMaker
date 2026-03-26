"""Excel reader service for converting uploaded rows into label models."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.models.label import Label


REQUIRED_COLUMN_MAP = {
    "supplier": ["supplier"],
    "store": ["store", "store #"],
    "po": ["po", "po #"],
    "description": ["description"],
    "sap": ["sap", "sap #"],
}


def _normalize_header(header: str) -> str:
    return header.strip().lower()


def _resolve_columns(columns: list[str]) -> dict[str, str]:
    """
    Map actual Excel headers to required logical fields.
    Accepts minor header variations (case, spaces, optional #).
    """
    normalized = {_normalize_header(col): col for col in columns}

    resolved: dict[str, str] = {}

    for logical_name, variations in REQUIRED_COLUMN_MAP.items():
        for variant in variations:
            if variant in normalized:
                resolved[logical_name] = normalized[variant]
                break

        if logical_name not in resolved:
            raise ValueError(
                f"Missing required column for '{logical_name}'. "
                f"Accepted names: {variations}"
            )

    return resolved


def _coerce_to_string(value: Any) -> str:
    """
    Convert Excel cell value to string safely.

    Preserves leading zeros when Excel column is text.
    Converts numeric cells without scientific notation.
    """
    if pd.isna(value):
        return ""

    # If numeric (float/int), convert without decimal .0
    if isinstance(value, (int, float)):
        # Avoid scientific notation
        return str(int(value))

    return str(value)


def _validate_barcode_field(value: str, field_name: str) -> None:
    """
    Validate barcode field length.

    Must be exactly 10 characters.
    Allows alphanumeric for future safety.
    """
    if len(value) != 10:
        raise ValueError(
            f"{field_name} must be exactly 10 characters. Got '{value}' ({len(value)} chars)."
        )


def read_excel(file: Any) -> list[Label]:
    """
    Read an Excel file-like object and return label records.

    Args:
        file: Uploaded Excel file from Streamlit or file-like object.

    Returns:
        A list of parsed `Label` records.
    """
    df = pd.read_excel(file, dtype=str)

    column_map = _resolve_columns(df.columns.tolist())

    labels: list[Label] = []

    for _, row in df.iterrows():
        supplier = _coerce_to_string(row[column_map["supplier"]]).strip()
        store = _coerce_to_string(row[column_map["store"]]).strip()
        po = _coerce_to_string(row[column_map["po"]]).strip()
        description = _coerce_to_string(row[column_map["description"]]).strip()
        sap = _coerce_to_string(row[column_map["sap"]]).strip()

        if not po:
            raise ValueError("PO cannot be empty.")
        if not sap:
            raise ValueError("SAP cannot be empty.")

        _validate_barcode_field(po, "PO")
        _validate_barcode_field(sap, "SAP")

        labels.append(
            Label(
                supplier=supplier,
                store=store,
                po=po,
                description=description,
                sap=sap,
            )
        )

    if not labels:
        raise ValueError("Excel file contains no valid rows.")

    return labels
