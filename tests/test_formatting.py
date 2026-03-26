"""Tests for formatting utilities."""

from __future__ import annotations

from app.utils.formatting import drop_leading_zeros, sanitize_text


def test_drop_leading_zeros_removes_padding() -> None:
    """Verify leading zero trimming for normal numeric text."""
    assert drop_leading_zeros("000123") == "123"


def test_drop_leading_zeros_returns_zero_for_all_zero_input() -> None:
    """Verify all-zero values normalize to a single zero."""
    assert drop_leading_zeros("0000") == "0"


def test_sanitize_text_collapses_whitespace() -> None:
    """Verify internal and surrounding whitespace normalization."""
    assert sanitize_text("  SIGNAGE    KITS  ") == "SIGNAGE KITS"

