"""Tests for the barcode service scaffold."""

from __future__ import annotations

import pytest

from app.services.barcode_service import generate_code128_barcode


def test_generate_code128_barcode_placeholder_raises_not_implemented() -> None:
    """Ensure scaffold implementation is explicitly unimplemented."""
    with pytest.raises(NotImplementedError):
        generate_code128_barcode("00012345")

