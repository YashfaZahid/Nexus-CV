"""Session-state initialization and helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st

DEFAULTS: dict[str, Any] = {
    "authenticated": False,
    "api_key": "",
    "openai_model": "gpt-4o-mini",
    "page": "dashboard",
    "generated_cv": None,
    "generated_cover_letter": None,
    "ats_result": None,
    "template_id": "classic",
    "cv_text_raw": "",
    "analysis_result": None,
    "create_profile": None,
    "last_error": "",
}


def init_session() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def require_auth() -> bool:
    return bool(st.session_state.get("authenticated") and st.session_state.get("api_key"))


def logout() -> None:
    st.session_state.authenticated = False
    st.session_state.api_key = ""
    st.session_state.page = "landing"
    st.session_state.generated_cv = None
    st.session_state.generated_cover_letter = None
    st.session_state.ats_result = None
    st.session_state.analysis_result = None
    st.session_state.cv_text_raw = ""


def set_page(page: str) -> None:
    st.session_state.page = page
