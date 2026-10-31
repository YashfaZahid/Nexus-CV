"""Premium dark SaaS styling for Streamlit."""

from __future__ import annotations

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
}

.stApp {
  background:
    radial-gradient(1200px 600px at 10% -10%, rgba(124, 58, 237, 0.28), transparent 55%),
    radial-gradient(900px 500px at 90% 0%, rgba(14, 165, 233, 0.18), transparent 50%),
    radial-gradient(800px 500px at 50% 100%, rgba(99, 102, 241, 0.12), transparent 55%),
    linear-gradient(165deg, #070A12 0%, #0B0F19 40%, #10182A 100%);
  color: #E8ECF4;
}

/* Hide default chrome noise */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
  padding-top: 2rem !important;
  padding-bottom: 3rem !important;
  max-width: 1200px;
}

h1, h2, h3, .brand-title {
  font-family: 'Space Grotesk', sans-serif !important;
  letter-spacing: -0.02em;
}

.hero-wrap {
  text-align: center;
  padding: 3.5rem 1.5rem 1.5rem;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 1.25rem;
}

.brand-orb {
  width: 42px; height: 42px; border-radius: 12px;
  background: linear-gradient(135deg, #8B5CF6, #06B6D4);
  box-shadow: 0 0 40px rgba(139, 92, 246, 0.45);
}

.brand-title {
  font-size: clamp(2.4rem, 5vw, 3.4rem);
  font-weight: 700;
  margin: 0;
  background: linear-gradient(120deg, #F8FAFC 10%, #C4B5FD 45%, #67E8F9 90%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-sub {
  color: #94A3B8;
  font-size: 1.1rem;
  max-width: 560px;
  margin: 0.85rem auto 0;
  line-height: 1.55;
}

.glass-card {
  background: rgba(20, 27, 45, 0.72);
  border: 1px solid rgba(139, 92, 246, 0.22);
  border-radius: 18px;
  padding: 1.5rem 1.6rem;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.03) inset,
    0 20px 50px rgba(0,0,0,0.35);
  margin-bottom: 1rem;
}

.glass-card-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.15rem;
  font-weight: 600;
  margin: 0 0 0.35rem 0;
  color: #F1F5F9;
}

.glass-card-sub {
  color: #94A3B8;
  font-size: 0.92rem;
  margin-bottom: 1rem;
}

.stat-pill {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: rgba(139, 92, 246, 0.15);
  border: 1px solid rgba(139, 92, 246, 0.35);
  color: #C4B5FD;
  font-size: 0.8rem;
  font-weight: 600;
  margin-right: 0.4rem;
}

.score-hero {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 3.2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #A78BFA, #22D3EE);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.disclaimer {
  font-size: 0.8rem;
  color: #64748B;
  border-left: 3px solid rgba(139, 92, 246, 0.5);
  padding-left: 0.75rem;
  margin-top: 0.75rem;
}

.preview-box {
  background: #F8FAFC;
  color: #0F172A;
  border-radius: 12px;
  padding: 1.25rem 1.4rem;
  font-family: 'DM Sans', Georgia, serif;
  font-size: 0.92rem;
  line-height: 1.5;
  white-space: pre-wrap;
  max-height: 640px;
  overflow-y: auto;
  border: 1px solid #E2E8F0;
}

.side-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94A3B8;
  margin-bottom: 0.35rem;
  font-weight: 600;
}

.diff-original {
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 10px;
  padding: 0.85rem;
  color: #FCA5A5;
  font-size: 0.9rem;
}

.diff-recommended {
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 10px;
  padding: 0.85rem;
  color: #6EE7B7;
  font-size: 0.9rem;
}

.nav-chip {
  display: inline-block;
  padding: 0.4rem 0.9rem;
  border-radius: 10px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  color: #CBD5E1;
  font-size: 0.85rem;
  margin-right: 0.4rem;
}

div[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0B1020 0%, #121A2E 100%);
  border-right: 1px solid rgba(139, 92, 246, 0.15);
}

div[data-testid="stSidebar"] .stMarkdown {
  color: #CBD5E1;
}

.stButton > button {
  background: linear-gradient(135deg, #7C3AED, #4F46E5) !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  padding: 0.55rem 1.1rem !important;
  box-shadow: 0 8px 24px rgba(124, 58, 237, 0.35) !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}

.stButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(124, 58, 237, 0.45) !important;
}

.stButton > button[kind="secondary"] {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  box-shadow: none !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] > div,
div[data-baseweb="select"] > div {
  background-color: rgba(15, 23, 42, 0.75) !important;
  border-radius: 10px !important;
  border-color: rgba(148, 163, 184, 0.25) !important;
  color: #E2E8F0 !important;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.9rem;
  margin: 1.5rem 0 0.5rem;
}

.feature-item {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 1rem;
}

.feature-item strong {
  display: block;
  color: #E2E8F0;
  margin-bottom: 0.25rem;
  font-family: 'Space Grotesk', sans-serif;
}

.feature-item span {
  color: #94A3B8;
  font-size: 0.86rem;
  line-height: 1.4;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.topbar-brand {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
  background: linear-gradient(120deg, #E2E8F0, #A78BFA);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
"""


def inject_styles() -> None:
    import streamlit as st

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
