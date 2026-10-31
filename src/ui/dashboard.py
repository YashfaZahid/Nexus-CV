"""Authenticated dashboard hub."""

from __future__ import annotations

import streamlit as st

from src.ui.session import set_page


def render_dashboard() -> None:
    st.markdown(
        """
        <div class="topbar">
          <div class="topbar-brand">NexusCV Studio</div>
        </div>
        <div class="glass-card">
          <div class="glass-card-title">Welcome back</div>
          <div class="glass-card-sub">
            Choose a workflow. Your OpenAI key stays in this session only — documents are never written to disk by the app.
          </div>
          <span class="stat-pill">Session secured</span>
          <span class="stat-pill">ATS-aware</span>
          <span class="stat-pill">PDF + DOCX export</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="glass-card">
              <div class="glass-card-title">Create CV from Scratch</div>
              <div class="glass-card-sub">
                Structured intake for experience, education, skills and more.
                Generate a job-tailored CV and cover letter you can edit and export.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Start create workflow", type="primary", width="stretch", key="go_create"):
            set_page("create")
            st.rerun()

    with c2:
        st.markdown(
            """
            <div class="glass-card">
              <div class="glass-card-title">Improve Existing CV</div>
              <div class="glass-card-sub">
                Upload PDF/DOCX, extract content, review issues side by side,
                then generate an improved CV and tailored cover letter — without inventing facts.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Start improve workflow", type="primary", width="stretch", key="go_improve"):
            set_page("improve")
            st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.session_state.get("generated_cv") is not None:
        st.markdown(
            """
            <div class="glass-card">
              <div class="glass-card-title">Continue with last generation</div>
              <div class="glass-card-sub">You have generated documents in this session.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open preview & export", width="stretch", key="go_export"):
            set_page("export")
            st.rerun()
