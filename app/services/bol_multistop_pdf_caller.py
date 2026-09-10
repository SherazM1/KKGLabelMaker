"""Explicit callers for Standard and No Recourse Multistop BOL PDFs.

Place this file in:
    app/services/bol_multistop_pdf_caller.py

Also place bol_pdf_template_stamper.py in:
    app/services/bol_pdf_template_stamper.py

Use generate_no_recourse_multistop_pdf(...) when the user selects
No Recourse Multistop. This guarantees multistop_no_recourse=True.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from app.models.bol_multistop_record import BolMultistopRecord
from app.services.bol_pdf_template_stamper import stamp_bol_pdf_set
from app.services.bol_standard_docx_generator import GeneratedDocxFile
from app.services.bol_standard_pdf_converter import StandardPdfConversionResult
from app.utils.bol_facilities import BolFacilityRecord


def generate_no_recourse_multistop_pdf(
    records: list[BolMultistopRecord],
    selected_facility: BolFacilityRecord | None,
    generated_docx_files: list[GeneratedDocxFile],
    *,
    bol_type: str | None = None,
    batch_comment: str | None = None,
    output_dir: Path | None = None,
    progress_callback: Callable[[int, int, GeneratedDocxFile], None] | None = None,
) -> StandardPdfConversionResult:
    """Generate a Multistop BOL with the No Recourse paragraph and footer."""

    return stamp_bol_pdf_set(
        records=records,
        selected_facility=selected_facility,
        generated_docx_files=generated_docx_files,
        mode="Multistop",
        bol_type=bol_type,
        multistop_no_recourse=True,
        batch_comment=batch_comment,
        output_dir=output_dir,
        progress_callback=progress_callback,
    )


def generate_standard_multistop_pdf(
    records: list[BolMultistopRecord],
    selected_facility: BolFacilityRecord | None,
    generated_docx_files: list[GeneratedDocxFile],
    *,
    bol_type: str | None = None,
    batch_comment: str | None = None,
    output_dir: Path | None = None,
    progress_callback: Callable[[int, int, GeneratedDocxFile], None] | None = None,
) -> StandardPdfConversionResult:
    """Generate a normal Standard Multistop BOL."""

    return stamp_bol_pdf_set(
        records=records,
        selected_facility=selected_facility,
        generated_docx_files=generated_docx_files,
        mode="Multistop",
        bol_type=bol_type,
        multistop_no_recourse=False,
        batch_comment=batch_comment,
        output_dir=output_dir,
        progress_callback=progress_callback,
    )
