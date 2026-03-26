"""Formatting helpers for display normalization and data sanitation."""

from __future__ import annotations


def drop_leading_zeros(value: str) -> str:
    """
    Drop leading zeros for display while preserving semantic emptiness.

    Examples:
        "0040922455" -> "40922455"
        "0000000000" -> "0"
        "" -> ""
    """
    if value is None:
        return ""

    stripped_input = str(value).strip()
    if not stripped_input:
        return ""

    stripped_value = stripped_input.lstrip("0")
    return stripped_value or "0"


def sanitize_text(value: str) -> str:
    """
    Normalize whitespace and trim surrounding noise.

    - Collapses multiple spaces
    - Removes leading/trailing whitespace
    - Safe against None input
    """
    if value is None:
        return ""

    return " ".join(str(value).split()).strip()


def safe_upper(value: str) -> str:
    """
    Optional helper for fields that must be uppercase
    (future-proof if needed).
    """
    return sanitize_text(value).upper()


def safe_wrap_text(value: str, max_chars: int) -> list[str]:
    """
    Basic word-safe wrapping for PDF layout.

    Args:
        value: Text to wrap.
        max_chars: Maximum characters per line.

    Returns:
        List of wrapped lines.
    """
    text = sanitize_text(value)
    if not text:
        return [""]

    words = text.split()
    lines: list[str] = []
    current_line = ""

    for word in words:
        candidate = f"{current_line} {word}".strip()
        if len(candidate) <= max_chars:
            current_line = candidate
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines