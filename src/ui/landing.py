"""Premium landing page with OpenAI API key validation."""

from __future__ import annotations

import streamlit as st

from src.openai_client import validate_api_key
from src.ui.session import set_page


def render_landing() -> None:
    st.markdown(
        """
        <div class="hero-wrap">
          <div class="brand-mark">
            <div class="brand-orb"></div>
          </div>
          <h1 class="brand-title">NexusCV</h1>
          <p class="hero-sub">
            AI-powered CV &amp; cover letter studio. Tailor documents to any role,
            score ATS compatibility with transparent criteria, and export polished PDF/DOCX files.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="feature-grid">
          <div class="feature-item"><strong>Create from scratch</strong><span>Structured intake + job-tailored generation</span></div>
          <div class="feature-item"><strong>Improve existing CVs</strong><span>PDF/DOCX parsing with side-by-side fixes</span></div>
          <div class="feature-item"><strong>Deterministic ATS</strong><span>Explainable 90+ targeting — not LLM guesswork</span></div>
          <div class="feature-item"><strong>Export ready</strong><span>Multiple ATS-friendly templates, PDF &amp; DOCX</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2.2, 1])
    with col2:
        st.markdown(
            """
            <div class="glass-card">
              <div class="glass-card-title">Connect your OpenAI API key</div>
              <div class="glass-card-sub">
                Your key is stored only in this session on the server and is never logged or written to disk.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            label_visibility="collapsed",
            key="landing_api_key_input",
        )
        model = st.selectbox(
            "Model",
            options=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"],
            index=0,
            help="Used for all AI generation and analysis calls.",
        )

        validate = st.button("Validate & Enter Studio", width="stretch", type="primary")

        if validate:
            if not api_key.strip():
                st.error("Please enter your OpenAI API key.")
                return
            with st.spinner("Validating API key with OpenAI…"):
                ok, message = validate_api_key(api_key.strip())
            if ok:
                st.session_state.api_key = api_key.strip()
                st.session_state.authenticated = True
                st.session_state.openai_model = model
                set_page("dashboard")
                st.success(message)
                st.rerun()
            else:
                st.error(message)

        st.caption(
            "Get a key at platform.openai.com. Usage is billed to your OpenAI account. "
            "Documents stay in your session and are not persisted by this app."
        )
