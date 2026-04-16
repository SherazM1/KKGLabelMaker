"""UI-only BOL generator page."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def _initialize_bol_state() -> None:
    if "bol_mode" not in st.session_state:
        st.session_state["bol_mode"] = "Standard"
    if "bol_uploaded_filename" not in st.session_state:
        st.session_state["bol_uploaded_filename"] = None
    if "bol_parse_requested" not in st.session_state:
        st.session_state["bol_parse_requested"] = False
    if "bol_generation_status" not in st.session_state:
        st.session_state["bol_generation_status"] = "Waiting for generation action."


def _placeholder_review_records(mode: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "BOL number": "BOL-10001",
                "Load number": "LD-2231",
                "PO number": "PO-88412",
                "Ship date": "2026-04-16",
                "Carrier": "Carrier A",
                "Ship from": "Dallas, TX",
                "Ship to": "Kansas City, MO",
                "Total quantity": 128,
                "Total weight": "4,120 lb",
                "Item line count": 7,
                "Mode": mode,
                "Status": "Ready",
            },
            {
                "BOL number": "BOL-10002",
                "Load number": "LD-2232",
                "PO number": "PO-88433",
                "Ship date": "2026-04-17",
                "Carrier": "Carrier B",
                "Ship from": "Fort Worth, TX",
                "Ship to": "Omaha, NE",
                "Total quantity": 96,
                "Total weight": "3,010 lb",
                "Item line count": 5,
                "Mode": mode,
                "Status": "Issue",
            },
            {
                "BOL number": "BOL-10003",
                "Load number": "LD-2233",
                "PO number": "PO-88444",
                "Ship date": "2026-04-18",
                "Carrier": "Carrier C",
                "Ship from": "Houston, TX",
                "Ship to": "Tulsa, OK",
                "Total quantity": 112,
                "Total weight": "3,700 lb",
                "Item line count": 6,
                "Mode": mode,
                "Status": "Ready",
            },
        ]
    )


def render_bol_generator_view() -> None:
    _initialize_bol_state()

    if st.button("Back to Home"):
        st.session_state["page"] = "home"
        st.stop()

    st.markdown("---")

    st.title("BOL Generator")
    st.caption("Batch workflow for reviewing records and preparing BOL output sets.")

    st.subheader("Mode Selection")
    st.session_state["bol_mode"] = st.radio(
        "Select BOL mode",
        options=["Standard", "No Recourse", "Multistop"],
        horizontal=True,
        key="bol_mode_radio",
        index=["Standard", "No Recourse", "Multistop"].index(st.session_state["bol_mode"]),
    )

    st.markdown("---")

    st.subheader("Upload Excel")
    st.caption("Accepted file types: .xlsx, .xlsm, .xls")
    uploaded_file = st.file_uploader(
        "Upload Excel input",
        type=["xlsx", "xlsm", "xls"],
        key="bol_excel_uploader",
    )
    if uploaded_file is None:
        st.info("No Excel file uploaded yet.")
        st.session_state["bol_uploaded_filename"] = None
    else:
        st.session_state["bol_uploaded_filename"] = uploaded_file.name
        st.success(f"Uploaded file: {uploaded_file.name}")

    st.markdown("---")

    st.subheader("Parse")
    parse_disabled = st.session_state["bol_uploaded_filename"] is None
    if st.button("Parse Excel", type="primary", disabled=parse_disabled):
        st.session_state["bol_parse_requested"] = True

    if parse_disabled:
        st.info("Upload an Excel file to enable parsing.")
    elif st.session_state["bol_parse_requested"]:
        st.success("Parse complete (placeholder).")
        st.write(
            {
                "source_file": st.session_state["bol_uploaded_filename"],
                "mode": st.session_state["bol_mode"],
                "summary": "Placeholder parse output for UI wiring.",
            }
        )
    else:
        st.info("Parse summary will appear here after clicking Parse Excel.")

    st.markdown("---")

    st.subheader("Review Records")
    total_records = 3
    ready_records = 2
    issue_records = 1
    selected_records = 2

    metric_cols = st.columns(4)
    metric_cols[0].metric("Total records found", total_records)
    metric_cols[1].metric("Ready records", ready_records)
    metric_cols[2].metric("Records with issues", issue_records)
    metric_cols[3].metric("Records selected for generation", selected_records)

    st.dataframe(
        _placeholder_review_records(st.session_state["bol_mode"]),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    st.subheader("Generate")
    st.button("Generate DOCX Set", disabled=True, use_container_width=True)
    st.button("Generate PDF Set", disabled=True, use_container_width=True)
    st.button("Generate All", disabled=True, use_container_width=True)
    st.caption("Generation actions are placeholders and will be enabled when backend logic is connected.")

    st.markdown("---")

    st.subheader("Download")
    st.button("Download DOCX Bundle", disabled=True, use_container_width=True)
    st.button("Download PDF Bundle", disabled=True, use_container_width=True)
    st.button("Download All Files", disabled=True, use_container_width=True)

    st.markdown("---")

    st.subheader("Status & Results")
    st.info("Generation status: Not started (placeholder).")
    st.info("Bundle readiness: No bundles available yet (placeholder).")

