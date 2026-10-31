"""Live preview and PDF/DOCX download controls."""

from __future__ import annotations

import streamlit as st

from src.document_export import (
    build_cover_letter_docx,
    build_cover_letter_pdf,
    build_cv_docx,
    build_cv_pdf,
    cover_letter_to_plain_text,
    cv_to_plain_text,
)
from src.schemas import GeneratedCoverLetter, GeneratedCV


def render_preview_and_export(
    cv: GeneratedCV | None,
    cover_letter: GeneratedCoverLetter | None,
    template_id: str = "classic",
) -> None:
    if cv is None:
        st.info("Generate or improve a CV to preview and export.")
        return

    template_id = st.selectbox(
        "Export template",
        options=["classic", "modern", "minimal"],
        index=["classic", "modern", "minimal"].index(template_id)
        if template_id in ("classic", "modern", "minimal")
        else 0,
        format_func=lambda x: {
            "classic": "Classic ATS",
            "modern": "Modern Violet",
            "minimal": "Minimal Clean",
        }[x],
        key="export_template_select",
    )
    st.session_state.template_id = template_id

    p1, p2 = st.columns(2)
    with p1:
        st.markdown('<div class="side-label">CV preview</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="preview-box">{_html_escape(cv_to_plain_text(cv))}</div>',
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown('<div class="side-label">Cover letter preview</div>', unsafe_allow_html=True)
        if cover_letter:
            st.markdown(
                f'<div class="preview-box">{_html_escape(cover_letter_to_plain_text(cover_letter))}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("No cover letter available.")

    st.markdown("#### Downloads")
    d1, d2, d3, d4 = st.columns(4)

    try:
        cv_pdf = build_cv_pdf(cv, template_id)  # type: ignore[arg-type]
        cv_docx = build_cv_docx(cv, template_id)  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to build CV files: {exc}")
        return

    safe_name = (cv.contact.full_name or "Candidate").replace(" ", "_")

    d1.download_button(
        "CV · PDF",
        data=cv_pdf,
        file_name=f"{safe_name}_CV.pdf",
        mime="application/pdf",
        width="stretch",
        key="dl_cv_pdf",
    )
    d2.download_button(
        "CV · DOCX",
        data=cv_docx,
        file_name=f"{safe_name}_CV.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        width="stretch",
        key="dl_cv_docx",
    )

    if cover_letter:
        try:
            cl_pdf = build_cover_letter_pdf(cover_letter, template_id)  # type: ignore[arg-type]
            cl_docx = build_cover_letter_docx(cover_letter, template_id)  # type: ignore[arg-type]
        except Exception as exc:  # noqa: BLE001
            st.error(f"Failed to build cover letter files: {exc}")
            return
        d3.download_button(
            "Cover letter · PDF",
            data=cl_pdf,
            file_name=f"{safe_name}_Cover_Letter.pdf",
            mime="application/pdf",
            width="stretch",
            key="dl_cl_pdf",
        )
        d4.download_button(
            "Cover letter · DOCX",
            data=cl_docx,
            file_name=f"{safe_name}_Cover_Letter.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            width="stretch",
            key="dl_cl_docx",
        )
    else:
        d3.button("Cover letter · PDF", disabled=True, width="stretch")
        d4.button("Cover letter · DOCX", disabled=True, width="stretch")


def _html_escape(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
