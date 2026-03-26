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
    if pd.isna(value):
        return ""
    return str(value).strip()


def _normalize_sap(value: str, row_number: int) -> str:
    """
    Normalize SAP to a 10-digit string.
    Accepts 9 or 10 digit numeric values.
    Pads 9-digit values with leading zero.
    """

    cleaned = value.strip()

    if not cleaned:
        raise ValueError(f"Row {row_number}: SAP is blank.")

    if not cleaned.isdigit():
        raise ValueError(
            f"Row {row_number}: SAP must be numeric. Got '{value}'."
        )

    length = len(cleaned)

    if length == 10:
        return cleaned

    if length == 9:
        return cleaned.zfill(10)

    raise ValueError(
        f"Row {row_number}: SAP must be 9 or 10 digits. "
        f"Got '{value}' ({length} digits)."
    )


def read_excel(file: Any) -> list[Label]:
    """
    Read an Excel file-like object and return label records.
    """

    df = pd.read_excel(file, dtype=str)

    if df.empty:
        raise ValueError("Excel file contains no rows.")

    column_map = _resolve_columns(df.columns.tolist())

    labels: list[Label] = []

    for index, row in df.iterrows():
        row_number = index + 2  # +2 because Excel rows start at 1 and row 1 is header

        supplier = _coerce_to_string(row[column_map["supplier"]])
        store = _coerce_to_string(row[column_map["store"]])
        po = _coerce_to_string(row[column_map["po"]])
        description = _coerce_to_string(row[column_map["description"]])
        sap_raw = _coerce_to_string(row[column_map["sap"]])

        print(
            f"[DEBUG] Row {row_number} -> "
            f"Supplier='{supplier}', Store='{store}', "
            f"PO='{po}', SAP='{sap_raw}'"
        )

        if not supplier:
            raise ValueError(f"Row {row_number}: Supplier is blank.")

        if not store:
            raise ValueError(f"Row {row_number}: Store is blank.")

        if not po:
            raise ValueError(f"Row {row_number}: PO is blank.")

        sap = _normalize_sap(sap_raw, row_number)

        labels.append(
            Label(
                supplier=supplier,
                store=store,
                po=po,
                description=description,
                sap=sap,
            )
        )

    return labels