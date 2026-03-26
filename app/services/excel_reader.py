"""Excel reader service for converting uploaded rows into label models."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.models.label import Label


REQUIRED_COLUMNS = {"Supplier", "Store", "PO", "Description", "SAP"}


def _normalize_column_names(columns: list[str]) -> list[str]:
    """Strip whitespace from Excel headers."""
    return [col.strip() for col in columns]


def _validate_headers(columns: list[str]) -> None:
    """Ensure required columns exist exactly."""
    missing = REQUIRED_COLUMNS - set(columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")


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

    df.columns = _normalize_column_names(df.columns.tolist())
    _validate_headers(df.columns.tolist())

    labels: list[Label] = []

    for _, row in df.iterrows():
        supplier = _coerce_to_string(row["Supplier"]).strip()
        store = _coerce_to_string(row["Store"]).strip()
        po = _coerce_to_string(row["PO"]).strip()
        description = _coerce_to_string(row["Description"]).strip()
        sap = _coerce_to_string(row["SAP"]).strip()

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