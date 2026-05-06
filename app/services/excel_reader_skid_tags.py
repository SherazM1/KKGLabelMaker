"""Excel reader for SKID tag inputs."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re
from typing import Any

import pandas as pd

from app.models.skid_tag import SkidTag


COLUMN_MAP = {
    "dc": [
        "DC",
        "DC #",
        "DC#",
        "D.C.",
        "Distribution Center",
        "Destination DC",
        "Store",
        "Store #",
    ],
    "po": [
        "PO",
        "PO #",
        "PO#",
        "Purchase Order",
        "Purchase Order Number",
        "Customer PO",
    ],
    "upc": [
        "UPC",
        "UPC #",
        "UPC#",
        "GTIN",
        "Item UPC",
    ],
    "quantity": [
        "Qty",
        "QTY",
        "Quantity",
        "Case Qty",
        "Cases",
        "Qty Per Pallet",
        "Pallet Qty",
    ],
    "full_pallets": [
        "full pallets",
        "full pallet",
        "full",
    ],
    "partial_pallets": [
        "partial pallets",
        "partial pallet",
        "partial",
    ],
    "pallet_number": [
        "Pallet",
        "Pallet #",
        "Pallet#",
        "Pallet Number",
        "Pallet No",
        "Pallet No.",
        "Skid",
        "Skid #",
    ],
    "pallet_total": [
        "Total Pallets",
        "Pallet Total",
        "Pallets",
        "Number of Pallets",
        "Total Skids",
        "Skid Total",
    ],
}

REQUIRED_LOGICAL_COLUMNS = {"dc", "po", "upc"}


def _normalize_header(header: str) -> str:
    return "".join(char for char in str(header).strip().lower() if char.isalnum())


def _resolve_columns(columns: list[str]) -> dict[str, str]:
    normalized_to_actual = {_normalize_header(col): col for col in columns}
    resolved: dict[str, str] = {}
    missing: list[str] = []

    for logical_name, expected_headers in COLUMN_MAP.items():
        for expected_header in expected_headers:
            normalized_expected = _normalize_header(expected_header)
            if normalized_expected in normalized_to_actual:
                resolved[logical_name] = normalized_to_actual[normalized_expected]
                break
        else:
            if logical_name in REQUIRED_LOGICAL_COLUMNS:
                missing.append(expected_headers[0])

    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    return resolved


def _coerce_to_string(value: Any) -> str:
    if pd.isna(value):
        return ""

    text = str(value).strip()
    if not text:
        return ""

    try:
        decimal_value = Decimal(text)
    except InvalidOperation:
        return text

    normalized = format(decimal_value, "f")
    return normalized[:-2] if normalized.endswith(".0") else normalized


def _normalize_dc(value: Any) -> str:
    text = _coerce_to_string(value)
    return text.zfill(4) if text.isdigit() and len(text) < 4 else text


def _coerce_to_int(value: Any, row_number: int, field_name: str) -> int | None:
    text = _coerce_to_string(value)
    if not text:
        return None

    try:
        decimal_value = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"Row {row_number}: {field_name} must be numeric. Got '{text}'.") from exc

    if decimal_value != decimal_value.to_integral_value():
        raise ValueError(f"Row {row_number}: {field_name} must be a whole number. Got '{text}'.")

    number = int(decimal_value)
    if number < 1:
        raise ValueError(f"Row {row_number}: {field_name} must be at least 1. Got '{text}'.")

    return number


def _parse_pallet_spec(value: Any, row_number: int, field_name: str) -> list[str]:
    text = _coerce_to_string(value)
    if not text:
        return []

    match = re.fullmatch(r"(\d+)\s*@\s*(\d+(?:\.\d+)?)", text)
    if not match:
        raise ValueError(
            f"Row {row_number}: {field_name} must use the format '<count> @ <qty>'. "
            f"Got '{text}'."
        )

    count = int(match.group(1))
    quantity = _coerce_to_string(match.group(2))
    if count < 1:
        raise ValueError(f"Row {row_number}: {field_name} count must be at least 1.")

    return [quantity] * count


def _expand_row_quantities(
    row: Any,
    column_map: dict[str, str],
    row_number: int,
    fallback_quantity: str,
    fallback_total: int | None,
) -> list[str]:
    quantities: list[str] = []

    if "full_pallets" in column_map:
        quantities.extend(
            _parse_pallet_spec(row[column_map["full_pallets"]], row_number, "Full pallets")
        )

    if "partial_pallets" in column_map:
        quantities.extend(
            _parse_pallet_spec(row[column_map["partial_pallets"]], row_number, "Partial pallets")
        )

    if quantities:
        if fallback_total is not None and len(quantities) != fallback_total:
            raise ValueError(
                f"Row {row_number}: Expanded pallet count {len(quantities)} does not match "
                f"total pallets {fallback_total}."
            )
        return quantities

    if fallback_total is not None:
        return [fallback_quantity] * fallback_total

    return [fallback_quantity]


def read_excel_skid_tags(file: Any) -> list[SkidTag]:
    """Parse SKID tags from an Excel workbook, preserving row order."""

    df = pd.read_excel(file, dtype=str)

    if df.empty:
        raise ValueError("Excel file contains no rows.")

    column_map = _resolve_columns(df.columns.tolist())
    tags: list[SkidTag] = []

    for index, row in df.iterrows():
        row_number = index + 2

        dc = _normalize_dc(row[column_map["dc"]])
        po = _coerce_to_string(row[column_map["po"]])
        upc = _coerce_to_string(row[column_map["upc"]])
        quantity = (
            _coerce_to_string(row[column_map["quantity"]])
            if "quantity" in column_map
            else ""
        )
        pallet_number = (
            _coerce_to_int(row[column_map["pallet_number"]], row_number, "Pallet")
            if "pallet_number" in column_map
            else None
        )
        pallet_total = (
            _coerce_to_int(row[column_map["pallet_total"]], row_number, "Pallet total")
            if "pallet_total" in column_map
            else None
        )

        full_pallets = (
            _coerce_to_string(row[column_map["full_pallets"]])
            if "full_pallets" in column_map
            else ""
        )
        partial_pallets = (
            _coerce_to_string(row[column_map["partial_pallets"]])
            if "partial_pallets" in column_map
            else ""
        )

        if not any([dc, po, upc, full_pallets, partial_pallets, pallet_number, pallet_total]):
            continue

        missing = [
            field_name
            for field_name, value in (
                ("DC", dc),
                ("PO", po),
                ("UPC", upc),
            )
            if not value
        ]
        if missing:
            raise ValueError(f"Row {row_number}: Missing required values: {', '.join(missing)}.")

        if not any([quantity, full_pallets, partial_pallets]):
            raise ValueError(f"Row {row_number}: Missing required value: Quantity.")

        row_quantities = _expand_row_quantities(
            row,
            column_map,
            row_number,
            fallback_quantity=quantity,
            fallback_total=pallet_total,
        )

        row_total = pallet_total or len(row_quantities)
        start_number = pallet_number or 1
        for offset, row_quantity in enumerate(row_quantities):
            current_pallet_number = start_number + offset
            if current_pallet_number > row_total:
                raise ValueError(
                    f"Row {row_number}: Pallet number {current_pallet_number} is greater "
                    f"than pallet total {row_total}."
                )

            tags.append(
                SkidTag(
                    dc=dc,
                    po=po,
                    upc=upc,
                    quantity=row_quantity,
                    pallet_number=current_pallet_number,
                    pallet_total=row_total,
                    source_row_number=row_number,
                )
            )

    if not tags:
        raise ValueError("No valid SKID tag rows found in Excel file.")

    return tags
