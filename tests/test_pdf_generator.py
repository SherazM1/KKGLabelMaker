"""Tests for document generator scaffolds."""

from __future__ import annotations

import pytest

from app.services.docx_generator import generate_label_docx
from app.services.pdf_generator import generate_label_pdf


def test_generate_label_pdf_placeholder_raises_not_implemented() -> None:
    """Ensure PDF generator remains a scaffold stub."""
    with pytest.raises(NotImplementedError):
        generate_label_pdf(labels=[])


def test_generate_label_docx_placeholder_raises_not_implemented() -> None:
    """Ensure DOCX generator remains a scaffold stub."""
    with pytest.raises(NotImplementedError):
        generate_label_docx(labels=[])

