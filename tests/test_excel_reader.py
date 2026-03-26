"""Tests for the Excel reader service scaffold."""

from __future__ import annotations

import pytest

from app.services.excel_reader import read_excel


def test_read_excel_placeholder_raises_not_implemented() -> None:
    """Ensure scaffold implementation is explicitly unimplemented."""
    with pytest.raises(NotImplementedError):
        read_excel(file=None)

