"""File-related helpers for Streamlit download interactions."""

from __future__ import annotations

from typing import Any


def create_download_button(streamlit: Any, data: bytes, filename: str) -> None:
    """Render a Streamlit download button for generated artifacts.

    Args:
        streamlit: Streamlit module or container-like object.
        data: Binary payload to download.
        filename: Suggested name for the downloaded file.
    """
    streamlit.download_button(
        label=f"Download {filename}",
        data=data,
        file_name=filename,
        disabled=not data,
    )

