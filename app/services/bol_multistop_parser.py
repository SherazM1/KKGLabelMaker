"""Parser service for Multistop-mode BOL Excel uploads."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from app.models.bol_multistop_row import BolMultistopRow


MULTISTOP_SHEET_NAME = "MAIN LOAD SHEET"
MULTISTOP_SHEET_NAME_VARIANTS: tuple[str, ...] = (
    "MAIN LOAD SHEET",
    "Load sheet",
    "LOAD SHEET",
    "Main Load Sheet",
)

REQUIRED_COLUMN_SPECS: dict[str, str] = {
    "kk_load": "KK Load",
    "stop": "Stop",
    "trackers": "TRACKERS",
    "carrier": "Carrier",
    "load_number": "load#",
    "kk_po_number": "KK PO#",
    "bol_number": "BOL #",
    "ship_date": "ship date",
    "dc_name": "DC Name",
    "dc_address": "DC ADDRESS",
    "dc_city_state_zip": "DC City, State, Zip",
    "dc_city": "DC CITY",
    "dc_state": "DCST",
    "dc_zip": "DCZIP",
    "dc_number": "DC #",
    "target_po_number": "TGT PO #",
    "upc": "UPC",
    "pallet_description": "PalletDescription",
    "cases": "Cases",
    "total_pallets": "Total PLT",
    "kit_value_each": "Kit Value (EACH)",
    "shipment_value": "Shipment Value",
    "chargeback_3_percent": "3% Chargeback",
    "weight_each": "weight each",
    "weight": "Weight",
}


def _normalize_header(header: str) -> str:
    cleaned = str(header).strip()
    cleaned = re.sub(r"\s*#\s*", "#", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.upper()


def _resolve_multistop_sheet_name(file: Any) -> str:
    file.seek(0)
    workbook = pd.ExcelFile(file)
    available_sheet_names = [str(name) for name in workbook.sheet_names]

    exact_lookup = {name: name for name in available_sheet_names}
    for candidate in MULTISTOP_SHEET_NAME_VARIANTS:
        if candidate in exact_lookup:
            return exact_lookup[candidate]

    normalized_lookup = {_normalize_header(name): name for name in available_sheet_names}
    for candidate in MULTISTOP_SHEET_NAME_VARIANTS:
        normalized_candidate = _normalize_header(candidate)
        if normalized_candidate in normalized_lookup:
            return normalized_lookup[normalized_candidate]

    raise ValueError(
        "Required worksheet was not found for Multistop parsing. "
        f"Expected one of: {', '.join(MULTISTOP_SHEET_NAME_VARIANTS)}."
    )


def _resolve_columns(columns: list[str]) -> dict[str, str]:
    resolved_columns = [str(col) for col in columns]
    exact_columns = {col: col for col in resolved_columns}
    normalized_columns = {_normalize_header(col): col for col in resolved_columns}

    resolved: dict[str, str] = {}
    missing: list[str] = []

    for logical_name, source_name in REQUIRED_COLUMN_SPECS.items():
        resolved_name = None

        if source_name in exact_columns:
            resolved_name = exact_columns[source_name]
        else:
            normalized_name = _normalize_header(source_name)
            if normalized_name in normalized_columns:
                resolved_name = normalized_columns[normalized_name]

        if resolved_name is None:
            missing.append(f"{logical_name} (expected '{source_name}')")
        else:
            resolved[logical_name] = resolved_name

    if missing:
        raise ValueError(
            "Missing required columns in 'MAIN LOAD SHEET' for Multistop mode: "
            + "; ".join(missing)
        )

    return resolved


def _coerce_to_string(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _parse_stop_number(value: str) -> int | None:
    cleaned = (value or "").strip()
    if not cleaned:
        return None

    cleaned = cleaned.replace(",", "")
    try:
        parsed = float(cleaned)
    except ValueError:
        return None

    if not parsed.is_integer():
        return None

    return int(parsed)


def parse_multistop_bol_excel(file: Any) -> list[BolMultistopRow]:
    if file is None:
        raise ValueError("No file uploaded. Upload an Excel file to parse.")

    try:
        resolved_sheet_name = _resolve_multistop_sheet_name(file)
        file.seek(0)
        df = pd.read_excel(file, sheet_name=resolved_sheet_name, dtype=object)
    except ValueError as exc:
        raise

    if df.empty:
        raise ValueError("Worksheet 'MAIN LOAD SHEET' contains no rows.")

    column_map = _resolve_columns(df.columns.tolist())

    parsed_rows: list[BolMultistopRow] = []
    for index, row in df.iterrows():
        row_number = index + 2
        row_values = {
            key: _coerce_to_string(row[source_column])
            for key, source_column in column_map.items()
        }

        if not any(row_values.values()):
            continue

        parsed_rows.append(
            BolMultistopRow(
                source_row_number=row_number,
                kk_load=row_values["kk_load"],
                stop=row_values["stop"],
                stop_number=_parse_stop_number(row_values["stop"]),
                trackers=row_values["trackers"],
                carrier=row_values["carrier"],
                load_number=row_values["load_number"],
                kk_po_number=row_values["kk_po_number"],
                bol_number=row_values["bol_number"],
                ship_date=row_values["ship_date"],
                dc_name=row_values["dc_name"],
                dc_address=row_values["dc_address"],
                dc_city_state_zip=row_values["dc_city_state_zip"],
                dc_city=row_values["dc_city"],
                dc_state=row_values["dc_state"],
                dc_zip=row_values["dc_zip"],
                dc_number=row_values["dc_number"],
                target_po_number=row_values["target_po_number"],
                upc=row_values["upc"],
                pallet_description=row_values["pallet_description"],
                cases=row_values["cases"],
                total_pallets=row_values["total_pallets"],
                kit_value_each=row_values["kit_value_each"],
                shipment_value=row_values["shipment_value"],
                chargeback_3_percent=row_values["chargeback_3_percent"],
                weight_each=row_values["weight_each"],
                weight=row_values["weight"],
            )
        )

    if not parsed_rows:
        raise ValueError("No non-empty data rows found in 'MAIN LOAD SHEET'.")

    return parsed_rows
