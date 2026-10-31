"""Improve existing CV workflow with upload, analysis, and side-by-side review."""

from __future__ import annotations

import html

import streamlit as st

from src.ats_analyzer import analyze_ats
from src.cv_improver import analyze_cv, improve_cv_and_cover_letter
from src.document_parser import DocumentParseError, extract_text
from src.openai_client import safe_error_message
from src.schemas import ImprovementItem
from src.ui.ats_view import render_ats_panel
from src.ui.preview_export import render_preview_and_export


def _render_issue_pair(item: ImprovementItem, idx: int, prefix: str) -> None:
    st.markdown(f"**{item.category.replace('_', ' ').title()}** · severity: `{item.severity}`")
    if item.explanation:
        st.caption(item.explanation)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="side-label">Original</div>', unsafe_allow_html=True)
        original = html.escape(item.original or "(not specified)")
        st.markdown(
            f'<div class="diff-original">{original}</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown('<div class="side-label">Recommended</div>', unsafe_allow_html=True)
        recommended = html.escape(item.recommended or "(see explanation)")
        st.markdown(
            f'<div class="diff-recommended">{recommended}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("")


def render_improve_cv() -> None:
    st.markdown("### Improve Existing CV")
    st.caption(
        "Upload a PDF or DOCX. We extract real content, analyze it with OpenAI, "
        "and improve wording without inventing qualifications."
    )

    uploaded = st.file_uploader(
        "Upload CV (PDF or DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=False,
        key="improve_upload",
    )

    j1, j2 = st.columns(2)
    with j1:
        job_title = st.text_input("Target job title (optional)", key="imp_job_title")
    with j2:
        company = st.text_input("Target company (optional)", key="imp_company")
    job_description = st.text_area(
        "Job description (optional but recommended)",
        height=120,
        key="imp_job_desc",
        placeholder="Paste the job posting to surface missing keywords and tailor the rewrite…",
    )
    template_id = st.selectbox(
        "Template",
        options=["classic", "modern", "minimal"],
        format_func=lambda x: {
            "classic": "Classic ATS",
            "modern": "Modern Violet",
            "minimal": "Minimal Clean",
        }[x],
        key="imp_template",
    )

    col_a, col_b = st.columns(2)
    analyze_btn = col_a.button("Analyze CV", width="stretch")
    improve_btn = col_b.button("Improve CV & Cover Letter", type="primary", width="stretch")

    if uploaded is None:
        st.info("Upload a PDF or DOCX to begin.")
        if st.session_state.get("generated_cv") is not None and st.session_state.get("cv_text_raw"):
            _render_results()
        return

    try:
        data = uploaded.getvalue()
        cv_text = extract_text(uploaded.name, data)
        st.session_state.cv_text_raw = cv_text
    except DocumentParseError as exc:
        st.error(str(exc))
        return
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to read file: {exc}")
        return

    with st.expander("Extracted document text", expanded=False):
        st.text_area("Extracted content", value=cv_text, height=220, disabled=True, key="imp_extracted")

    if analyze_btn:
        with st.spinner("Analyzing CV with OpenAI…"):
            try:
                analysis = analyze_cv(
                    st.session_state.api_key,
                    cv_text=cv_text,
                    job_description=job_description,
                    model=st.session_state.openai_model,
                )
                st.session_state.analysis_result = analysis
                # Preliminary ATS on extracted structured profile
                from src.cv_improver import merge_profile_into_cv

                prelim = merge_profile_into_cv(analysis.extracted_profile)
                st.session_state.ats_result = analyze_ats(prelim, job_description)
                st.success("Analysis complete.")
            except Exception as exc:  # noqa: BLE001
                st.error(safe_error_message(exc))

    if improve_btn:
        with st.spinner("Generating improved CV and cover letter…"):
            try:
                analysis = st.session_state.get("analysis_result")
                if analysis is None:
                    analysis = analyze_cv(
                        st.session_state.api_key,
                        cv_text=cv_text,
                        job_description=job_description,
                        model=st.session_state.openai_model,
                    )
                    st.session_state.analysis_result = analysis

                bundle = improve_cv_and_cover_letter(
                    st.session_state.api_key,
                    cv_text=cv_text,
                    analysis=analysis,
                    job_title=job_title,
                    company=company,
                    job_description=job_description,
                    model=st.session_state.openai_model,
                    template_id=template_id,
                )
                st.session_state.generated_cv = bundle.cv
                st.session_state.generated_cover_letter = bundle.cover_letter
                st.session_state.template_id = template_id
                st.session_state.ats_result = analyze_ats(bundle.cv, job_description)
                st.success("Improved documents ready. Review side-by-side findings and export below.")
            except Exception as exc:  # noqa: BLE001
                st.error(safe_error_message(exc))

    _render_results()


def _render_results() -> None:
    analysis = st.session_state.get("analysis_result")
    if analysis is not None:
        st.markdown("---")
        st.markdown("### Side-by-side recommendations")
        if analysis.overall_notes:
            st.info(analysis.overall_notes)

        if analysis.missing_sections:
            st.markdown("**Missing sections**")
            st.write(", ".join(analysis.missing_sections))

        if analysis.missing_keywords:
            st.markdown("**Missing job-specific keywords**")
            st.write(", ".join(analysis.missing_keywords))

        groups = [
            ("Grammar", analysis.grammar_issues),
            ("Weak descriptions", analysis.weak_descriptions),
            ("Formatting", analysis.formatting_issues),
            ("Irrelevant content", analysis.irrelevant_content),
        ]
        for label, items in groups:
            if not items:
                continue
            with st.expander(f"{label} ({len(items)})", expanded=label == "Weak descriptions"):
                for i, item in enumerate(items):
                    _render_issue_pair(item, i, label)

    if st.session_state.get("generated_cv") is not None:
        st.markdown("---")
        st.markdown("### Improved documents")
        tabs = st.tabs(["Edit CV", "Edit cover letter", "ATS analysis", "Preview & export"])
        cv = st.session_state.generated_cv
        cl = st.session_state.generated_cover_letter

        with tabs[0]:
            cv.professional_summary = st.text_area(
                "Summary", value=cv.professional_summary, height=120, key="imp_edit_summary"
            )
            skills = st.text_area(
                "Skills", value=", ".join(cv.skills), height=80, key="imp_edit_skills"
            )
            cv.skills = [s.strip() for s in skills.split(",") if s.strip()]
            for i, exp in enumerate(cv.experience):
                with st.expander(f"{exp.title} @ {exp.company}", expanded=False):
                    bullets = st.text_area(
                        "Bullets",
                        value="\n".join(exp.bullets),
                        height=100,
                        key=f"imp_edit_exp_{i}",
                    )
                    exp.bullets = [b.strip("•- ").strip() for b in bullets.splitlines() if b.strip()]
            st.session_state.generated_cv = cv

        with tabs[1]:
            if cl:
                cl.greeting = st.text_input("Greeting", value=cl.greeting, key="imp_cl_greet")
                body = st.text_area(
                    "Body",
                    value="\n\n".join(cl.body_paragraphs),
                    height=240,
                    key="imp_cl_body",
                )
                cl.body_paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
                cl.closing = st.text_input("Closing", value=cl.closing, key="imp_cl_close")
                cl.signature_name = st.text_input(
                    "Signature", value=cl.signature_name, key="imp_cl_sig"
                )
                st.session_state.generated_cover_letter = cl
            else:
                st.info("No cover letter yet.")

        with tabs[2]:
            if st.session_state.ats_result:
                render_ats_panel(st.session_state.ats_result)
            else:
                st.info("Run improvement to see ATS scores.")

        with tabs[3]:
            render_preview_and_export(
                st.session_state.generated_cv,
                st.session_state.generated_cover_letter,
                st.session_state.get("template_id", "classic"),
            )
