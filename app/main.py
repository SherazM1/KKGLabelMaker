"""Streamlit entry point for the EOTF label maker application."""

from __future__ import annotations

import streamlit as st

from app.services.excel_reader import read_excel
from app.services.excel_reader_sams import read_excel_sams
from app.services.pdf_generator import generate_label_pdf
from app.services.pdf_generator_sams import generate_sams_pdf


def render_mode_selector() -> str | None:
    st.title("Kendal King Label Maker")
    st.markdown("---")

    if "label_mode" not in st.session_state:
        st.session_state["label_mode"] = None

    left_col, right_col = st.columns(2)

    with left_col:
        if st.button("Walmart Labels", use_container_width=True):
            st.session_state["label_mode"] = "walmart"

    with right_col:
        if st.button("Sam's Warehouse Labels", use_container_width=True):
            st.session_state["label_mode"] = "sams"

    return st.session_state["label_mode"]


def render_walmart_mode() -> None:
    try:
        st.write("Upload Excel workbook to generate letter-sized Walmart labels.")

        uploaded_file = st.file_uploader(
            "Upload Excel input",
            type=["xlsx", "xlsm", "xls"],
            help="Required columns: Supplier, Store, PO, Description, SAP",
            key="walmart_file_uploader",
        )

        if uploaded_file is None:
            st.info("Upload an Excel file to begin.")
            return

        labels = read_excel(uploaded_file)
        page_count = len(labels)
        st.success(f"Parsed {len(labels)} rows. This will generate {page_count} pages.")

        if st.button("Generate Walmart PDF", type="primary", key="generate_walmart_pdf"):
            pdf_bytes = generate_label_pdf(labels)
            st.download_button(
                label="Download Walmart Labels PDF",
                data=pdf_bytes,
                file_name="walmart_labels.pdf",
                mime="application/pdf",
                key="download_walmart_pdf",
            )

    except ValueError as exc:
        st.error(f"Validation error: {exc}")
    except Exception as exc:
        st.error(f"Unexpected error: {exc}")


def render_sams_mode() -> None:
    try:
        st.write("Upload Excel workbook to generate 4x6 thermal warehouse labels.")
        st.write("Each row produces 2 labels.")
        st.write("ZIP must be 5+4 format.")
        st.write("UPC must be numeric.")

        uploaded_file = st.file_uploader(
            "Upload Excel input",
            type=["xlsx", "xlsm", "xls"],
            key="sams_file_uploader",
        )

        if uploaded_file is None:
            st.info("Upload an Excel file to begin.")
            return

        labels = read_excel_sams(uploaded_file)
        page_count = len(labels) * 2
        st.success(f"Parsed {len(labels)} rows. This will generate {page_count} pages.")

        if st.button("Generate Sam's PDF", type="primary", key="generate_sams_pdf"):
            pdf_bytes = generate_sams_pdf(labels)
            st.download_button(
                label="Download Sam's Labels PDF",
                data=pdf_bytes,
                file_name="sams_labels.pdf",
                mime="application/pdf",
                key="download_sams_pdf",
            )

    except ValueError as exc:
        st.error(f"Validation error: {exc}")
    except Exception as exc:
        st.error(f"Unexpected error: {exc}")


def main() -> None:
    """Run the Streamlit user interface."""
    st.set_page_config(page_title="Kendal King Label Maker", layout="centered")

    mode = render_mode_selector()

    if mode == "walmart":
        render_walmart_mode()
    elif mode == "sams":
        render_sams_mode()
    else:
        st.info("Select a label mode to begin.")


if __name__ == "__main__":
    main()
