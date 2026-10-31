"""ATS analysis visualizations."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src.schemas import ATSResult


def _gauge(score: float, title: str) -> go.Figure:
    color = "#22D3EE" if score >= 90 else "#A78BFA" if score >= 75 else "#F59E0B" if score >= 60 else "#F87171"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "", "font": {"size": 36, "color": "#E2E8F0"}},
            title={"text": title, "font": {"size": 14, "color": "#94A3B8"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#64748B"},
                "bar": {"color": color},
                "bgcolor": "rgba(15,23,42,0.4)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 60], "color": "rgba(248,113,113,0.15)"},
                    {"range": [60, 75], "color": "rgba(245,158,11,0.12)"},
                    {"range": [75, 90], "color": "rgba(167,139,250,0.12)"},
                    {"range": [90, 100], "color": "rgba(34,211,238,0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#22D3EE", "width": 2},
                    "thickness": 0.75,
                    "value": 90,
                },
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E2E8F0"},
        height=240,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig


def _radar(result: ATSResult) -> go.Figure:
    cats = ["Keywords", "Formatting", "Skills", "Experience", "Completeness"]
    vals = [
        result.keyword_score,
        result.formatting_score,
        result.skills_score,
        result.experience_score,
        result.completeness_score,
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=vals + [vals[0]],
            theta=cats + [cats[0]],
            fill="toself",
            fillcolor="rgba(139, 92, 246, 0.25)",
            line=dict(color="#A78BFA", width=2),
            name="Score",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=[90] * 6,
            theta=cats + [cats[0]],
            line=dict(color="#22D3EE", width=1, dash="dash"),
            name="90+ target",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(15,23,42,0.35)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(148,163,184,0.2)"),
            angularaxis=dict(gridcolor="rgba(148,163,184,0.2)"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(color="#94A3B8")),
        height=340,
        margin=dict(l=40, r=40, t=20, b=20),
    )
    return fig


def render_ats_panel(result: ATSResult) -> None:
    st.markdown(
        f"""
        <div class="glass-card">
          <div class="glass-card-title">ATS compatibility estimate</div>
          <div class="score-hero">{result.overall_score:.0f}</div>
          <div class="glass-card-sub" style="margin-top:0.5rem;">
            Weighted overall score targeting <span class="stat-pill">90+</span>
          </div>
          <div class="disclaimer">{result.disclaimer}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    g1, g2 = st.columns([1.1, 1])
    with g1:
        st.plotly_chart(_gauge(result.overall_score, "Overall"), width="stretch")
    with g2:
        st.plotly_chart(_radar(result), width="stretch")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Keywords", f"{result.keyword_score:.0f}")
    m2.metric("Formatting", f"{result.formatting_score:.0f}")
    m3.metric("Skills", f"{result.skills_score:.0f}")
    m4.metric("Experience", f"{result.experience_score:.0f}")
    m5.metric("Completeness", f"{result.completeness_score:.0f}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Matched keywords**")
        if result.matched_keywords:
            st.success(", ".join(result.matched_keywords[:30]))
        else:
            st.caption("None matched yet — add a job description for keyword scoring.")
    with c2:
        st.markdown("**Missing keywords**")
        if result.missing_keywords:
            st.warning(", ".join(result.missing_keywords[:25]))
        else:
            st.caption("No missing priority keywords detected.")

    st.markdown("**Section breakdown**")
    for section in result.section_scores:
        with st.expander(f"{section.name}: {section.score:.0f}/100", expanded=False):
            st.write(section.details)
            if section.recommendations:
                for r in section.recommendations:
                    st.markdown(f"- {r}")

    if result.recommendations:
        st.markdown("**Priority recommendations**")
        for r in result.recommendations:
            st.markdown(f"- {r}")
