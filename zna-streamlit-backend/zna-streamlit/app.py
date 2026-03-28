"""
ZNA AI Studio — Main entry point (Overview Dashboard)
Run with: streamlit run app.py
"""

import streamlit as st
import os

st.set_page_config(
    page_title="ZNA AI Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — tighten up sidebar nav ───────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebarNav"] { padding-top: 0.5rem; }
[data-testid="stSidebarNav"] li { margin-bottom: 2px; }
.stMetric label { font-size: 12px !important; }
.stMetric [data-testid="stMetricValue"] { font-size: 22px !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar status ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    from state_manager import get_target_title, has_resume, get_resume
    target = get_target_title()
    if target:
        st.success(f"🎯 **{target}**")
    else:
        st.info("💡 Fill out **Target Job Title** in Resume Builder to unlock the Job Portal.")

    if has_resume():
        r = get_resume()
        st.caption(f"📄 Resume loaded: **{r.get('name', 'User')}**")

# ── Dashboard ─────────────────────────────────────────────────────────────────
st.title("Welcome to your Career Workspace 🔗")
st.caption("Your central hub for AI-powered career growth and optimisation.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Dynamic Templates", "3 Styles", delta="Active ●")
with col2:
    st.metric("Input Modes", "Dual", delta="Enabled ⚡")
with col3:
    st.metric("Cover Letters", "Auto-Gen", delta="Ready 📋")
with col4:
    st.metric("ATS Scanner", "Semantic NLP", delta="Online 🚀")

st.divider()

# ── ATS Trends + Logs ─────────────────────────────────────────────────────────
from state_manager import get_ats_history
import pandas as pd

col_chart, col_logs = st.columns([1.5, 1])

with col_chart:
    st.subheader("📈 ATS Optimisation Trends")
    history = get_ats_history()
    chart_data = history if history else [65, 70, 68, 75, 82, 85, 92]
    df = pd.DataFrame({
        "Session": list(range(1, len(chart_data) + 1)),
        "ATS Match Score (%)": chart_data,
    })
    st.line_chart(df.set_index("Session"))
    if not history:
        st.caption("_Sample data shown — generate your first resume to start tracking._")

with col_logs:
    st.subheader("⚡ Live System Logs")

    gemini_key = ""
    try:
        gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        gemini_key = os.environ.get("GEMINI_API_KEY", "")

    if gemini_key:
        st.success("✅ **[System]** LLM Engine connected to Gemini 2.0 Flash.")
    else:
        st.error("❌ **[System]** GEMINI_API_KEY not set.")

    st.info("ℹ️ **[Module]** PDF Generation engine ready.")

    from state_manager import has_resume, get_resume
    if has_resume():
        resume = get_resume()
        st.warning(f"⏳ **[Memory]** Resume loaded for **{resume.get('name', 'user')}**.")
    else:
        st.warning("⏳ **[Memory]** Waiting for user to generate a resume...")

# ── Quick-start cards ─────────────────────────────────────────────────────────
st.divider()
st.subheader("🚀 Quick Start")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    **📄 Resume Builder**
    Parse LinkedIn/resume text and generate a polished, ATS-optimised resume.
    """)

with c2:
    st.markdown("""
    **✉️ Cover Letter**
    Auto-generate a tailored cover letter from your resume + job description.
    """)

with c3:
    st.markdown("""
    **🔍 ATS Engine**
    Deep scan: compare your resume to any job description with a keyword breakdown.
    """)

with c4:
    st.markdown("""
    **🌐 Job Portal**
    Get AI-powered LinkedIn search strategy, company targets, and salary ranges.
    """)
