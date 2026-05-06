from __future__ import annotations

from io import BytesIO

from docx import Document

from app.services.bol_doc_upload_parser import parse_bol_doc_upload


def _build_docx_upload(rows: list[tuple[str, str]], filename: str = "Shipment Request Form.docx"):
    doc = Document()
    table = doc.add_table(rows=0, cols=2)
    for label, value in rows:
        cells = table.add_row().cells
        cells[0].text = label
        cells[1].text = value

    payload = BytesIO()
    doc.save(payload)
    payload.seek(0)
    payload.name = filename
    return payload


def test_parse_bol_doc_upload_extracts_shipment_request_fields():
    upload = _build_docx_upload(
        [
            ("Origin Facility", "Kendal King C/O Shorr Packaging"),
            ("Origin Street Address", "975 W Oakdale Road"),
            ("Origin City/State/Zip", "Grand Prairie, TX 75050"),
            ("Delivery Facility", "Kendal King"),
            ("Delivery Street Address", "901 SW A Street"),
            ("Delivery City/State/Zip", "Bentonville, AR 72712"),
            ("Pallet Qty", "3"),
            ("Pallet DIMS", "40x48x36"),
            ("Pallet Weight", "300 lbs."),
            ("Delivery # (If Applicable)", "123456"),
            ("Project", "26-INCM-02456"),
            ("Comments", "Mixed Freight"),
            ("KKG PO#", "4569"),
            ("Carrier Pro", "101564"),
            ("Carrier SCAC", "TRYI"),
        ]
    )

    result = parse_bol_doc_upload(upload)
    record = result.records[0]

    assert record.bol_number == "123456"
    assert record.ship_from.company == "Kendal King C/O Shorr Packaging"
    assert record.ship_from.street == "975 W Oakdale Road"
    assert record.ship_from.city_state_zip == "Grand Prairie, TX 75050"
    assert record.consignee_company == "Kendal King"
    assert record.consignee_street == "901 SW A Street"
    assert record.consignee_city_state_zip == "Bentonville, AR 72712"
    assert record.kk_po_number == "4569"
    assert record.po_number == "4569"
    assert record.kk_load_number == "1"
    assert record.carrier_pro_number == "101564"
    assert record.carrier == "TRYI"
    assert record.comments == "Mixed Freight"
    assert record.item_lines[0].pallet_qty == "3"
    assert record.item_lines[0].skids == "3"
    assert record.item_lines[0].weight_each == "300"
    assert record.item_lines[0].item_description == "Mixed Freight"
    assert "40x48x36" not in record.item_lines[0].item_description
    assert "26-INCM-02456" not in record.item_lines[0].item_description
    assert record.item_lines[0].item_number == ""
    assert record.item_lines[0].upc == ""


def test_parse_bol_doc_upload_allows_optional_item_number_and_upc():
    upload = _build_docx_upload(
        [
            ("Delivery Facility", "Kendal King"),
            ("Delivery Street Address", "901 SW A Street"),
            ("Delivery City/State/Zip", "Bentonville, AR 72712"),
            ("Pallet Qty", "3"),
            ("Delivery #", "123456"),
            ("Item #", "ITEM-1"),
            ("UPC", "000123456789"),
        ],
        filename="Shipment Request Form EX.docx",
    )

    result = parse_bol_doc_upload(upload)
    record = result.records[0]

    assert record.kk_load_number == "1"
    assert record.item_lines[0].item_number == "ITEM-1"
    assert record.item_lines[0].upc == "000123456789"
