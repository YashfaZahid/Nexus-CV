"""NexusCV — AI-powered CV & Cover Letter Generator (Streamlit)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path when launched via `streamlit run app.py`
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv

from src.ui.ats_view import render_ats_panel
from src.ui.create_cv import render_create_cv
from src.ui.dashboard import render_dashboard
from src.ui.improve_cv import render_improve_cv
from src.ui.landing import render_landing
from src.ui.preview_export import render_preview_and_export
from src.ui.session import init_session, logout, require_auth, set_page
from src.ui.styles import inject_styles

load_dotenv()

st.set_page_config(
    page_title="NexusCV | AI CV & Cover Letter Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:0.5rem 0 1rem;">
              <div class="topbar-brand">NexusCV</div>
              <div style="color:#64748B;font-size:0.85rem;margin-top:0.25rem;">
                Premium CV studio
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not require_auth():
            st.caption("Enter your OpenAI API key on the landing page to unlock the studio.")
            return

        st.markdown(f"**Model:** `{st.session_state.openai_model}`")
        st.divider()

        nav = {
            "dashboard": "Dashboard",
            "create": "Create from Scratch",
            "improve": "Improve Existing CV",
            "ats": "ATS Analysis",
            "export": "Preview & Export",
        }
        for key, label in nav.items():
            disabled = key in ("ats", "export") and st.session_state.get("generated_cv") is None
            if st.button(
                label,
                key=f"nav_{key}",
                width="stretch",
                type="primary" if st.session_state.page == key else "secondary",
                disabled=disabled,
            ):
                set_page(key)
                st.rerun()

        st.divider()
        if st.button("Sign out / clear key", width="stretch", key="logout_btn"):
            logout()
            st.rerun()

        st.caption(
            "API keys are kept in Streamlit session state only. "
            "They are never written to logs or .env by this app."
        )


def main() -> None:
    init_session()
    if os.getenv("OPENAI_MODEL") and not st.session_state.get("_model_from_env"):
        # Soft default from env without overriding an authenticated choice mid-session
        if not st.session_state.authenticated:
            st.session_state.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        st.session_state._model_from_env = True

    inject_styles()
    _sidebar()

    if not require_auth():
        st.session_state.page = "landing"
        render_landing()
        return

    page = st.session_state.page
    if page == "landing":
        set_page("dashboard")
        page = "dashboard"

    if page == "dashboard":
        render_dashboard()
    elif page == "create":
        render_create_cv()
    elif page == "improve":
        render_improve_cv()
    elif page == "ats":
        st.markdown("### ATS Analysis")
        if st.session_state.ats_result:
            render_ats_panel(st.session_state.ats_result)
        else:
            st.info("Generate or improve a CV first to see ATS analysis.")
    elif page == "export":
        st.markdown("### Preview & Export")
        render_preview_and_export(
            st.session_state.generated_cv,
            st.session_state.generated_cover_letter,
            st.session_state.get("template_id", "classic"),
        )
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
