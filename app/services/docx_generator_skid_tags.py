"""DOCX generator for SKID tags."""

from __future__ import annotations

from io import BytesIO

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from app.models.skid_tag import SkidTag


def _add_paragraph(document: Document, text: str = "", *, centered: bool = False) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if centered else WD_ALIGN_PARAGRAPH.LEFT
    run = paragraph.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(16)


def _add_tag_page(document: Document, tag: SkidTag) -> None:
    _add_paragraph(document, f"DC {tag.dc}")
    _add_paragraph(document, f"PO {tag.po_display}")
    _add_paragraph(document)
    _add_paragraph(document, f"   UPC  {tag.upc}")
    _add_paragraph(document)
    _add_paragraph(document, f"     {tag.pallet_display}")
    _add_paragraph(document, f"Qty: {tag.quantity}", centered=True)


def generate_skid_tags_docx(tags: list[SkidTag]) -> bytes:
    if not tags:
        raise ValueError("No SKID tags provided for DOCX generation.")

    document = Document()
    section = document.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Inches(11)
    section.page_height = Inches(8.5)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    for index, tag in enumerate(tags):
        if index:
            document.add_page_break()
        _add_tag_page(document, tag)

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.read()
