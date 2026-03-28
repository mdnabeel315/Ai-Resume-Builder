import streamlit as st
import google.generativeai as genai
import json
import re
import time
from datetime import datetime
from fpdf import FPDF
import io
import os

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme / CSS ───────────────────────────────────────────────────────────────
def inject_css(dark_mode: bool):
    if dark_mode:
        bg          = "#0d0d0f"
        sidebar_bg  = "#111113"
        card_bg     = "#1a1a1e"
        card_border = "#2a2a2e"
        text_primary   = "#f5f5f7"
        text_secondary = "#a1a1a6"
        accent      = "#2997ff"
        accent2     = "#30d158"
        accent3     = "#ff453a"
        accent4     = "#ffd60a"
        input_bg    = "#1c1c1e"
        input_border= "#3a3a3c"
        log_system  = "#1a3a1a"
        log_module  = "#1a2a3a"
        log_memory  = "#2a2a1a"
        tag_active  = "#1a3a1a"
        tag_enabled = "#1a2a3a"
        tag_ready   = "#2a1a2a"
        tag_online  = "#2a1a1a"
    else:
        bg          = "#f5f5f7"
        sidebar_bg  = "#ffffff"
        card_bg     = "#ffffff"
        card_border = "#d2d2d7"
        text_primary   = "#1d1d1f"
        text_secondary = "#6e6e73"
        accent      = "#0071e3"
        accent2     = "#34c759"
        accent3     = "#ff3b30"
        accent4     = "#ff9f0a"
        input_bg    = "#f5f5f7"
        input_border= "#c7c7cc"
        log_system  = "#e8f5e9"
        log_module  = "#e3f2fd"
        log_memory  = "#fffde7"
        tag_active  = "#e8f5e9"
        tag_enabled = "#e3f2fd"
        tag_ready   = "#f3e5f5"
        tag_online  = "#fce4ec"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
        background-color: {bg};
        color: {text_primary};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid {card_border};
    }}
    section[data-testid="stSidebar"] .stRadio label {{
        color: {text_primary} !important;
        font-size: 13px;
        font-weight: 400;
    }}

    /* Main area */
    .main .block-container {{
        background-color: {bg};
        padding: 2rem 2.5rem;
        max-width: 1200px;
    }}

    /* Cards */
    .apple-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 20px rgba(0,0,0,{'0.15' if dark_mode else '0.06'});
        transition: box-shadow 0.3s ease;
    }}
    .apple-card:hover {{
        box-shadow: 0 4px 30px rgba(0,0,0,{'0.25' if dark_mode else '0.1'});
    }}

    /* Stat cards */
    .stat-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 14px;
        padding: 20px 24px;
        text-align: left;
        box-shadow: 0 1px 8px rgba(0,0,0,{'0.12' if dark_mode else '0.05'});
    }}
    .stat-label {{
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {text_secondary};
        margin-bottom: 6px;
    }}
    .stat-value {{
        font-size: 28px;
        font-weight: 700;
        color: {text_primary};
        letter-spacing: -0.02em;
        line-height: 1;
        margin-bottom: 10px;
    }}
    .stat-badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }}
    .badge-active  {{ background:{tag_active};  color:{accent2}; }}
    .badge-enabled {{ background:{tag_enabled}; color:{accent}; }}
    .badge-ready   {{ background:{tag_ready};   color:#bf5af2; }}
    .badge-online  {{ background:{tag_online};  color:{accent3}; }}

    /* Log items */
    .log-system {{ background:{log_system}; border-radius:10px; padding:12px 16px; margin:8px 0; font-size:13px; color:{text_primary}; }}
    .log-module {{ background:{log_module}; border-radius:10px; padding:12px 16px; margin:8px 0; font-size:13px; color:{text_primary}; }}
    .log-memory {{ background:{log_memory}; border-radius:10px; padding:12px 16px; margin:8px 0; font-size:13px; color:{text_primary}; }}

    /* Headings */
    h1 {{ font-size: 40px !important; font-weight: 700 !important; letter-spacing: -0.03em !important; color: {text_primary} !important; }}
    h2 {{ font-size: 22px !important; font-weight: 600 !important; letter-spacing: -0.01em !important; color: {text_primary} !important; }}
    h3 {{ font-size: 17px !important; font-weight: 600 !important; color: {text_primary} !important; }}
    p, li {{ color: {text_secondary}; font-size: 14px; line-height: 1.6; }}

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {{
        background-color: {input_bg} !important;
        border: 1px solid {input_border} !important;
        border-radius: 10px !important;
        color: {text_primary} !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 3px rgba(41,151,255,0.15) !important;
        outline: none !important;
    }}
    label {{ color: {text_secondary} !important; font-size: 13px !important; font-weight: 500 !important; }}

    /* Buttons */
    .stButton > button {{
        background: {accent};
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 10px 22px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        letter-spacing: -0.01em;
    }}
    .stButton > button:hover {{
        background: {'#1a7ae8' if dark_mode else '#005ec3'};
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(41,151,255,0.35);
    }}
    .stButton > button:active {{ transform: translateY(0); }}

    /* Download button */
    .stDownloadButton > button {{
        background: {accent2};
        color: #fff;
        border: none;
        border-radius: 10px;
        padding: 10px 22px;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: -0.01em;
        transition: all 0.2s ease;
    }}
    .stDownloadButton > button:hover {{
        background: {'#28b84b' if dark_mode else '#2fb350'};
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(48,209,88,0.35);
    }}

    /* Alerts */
    .alert-error {{
        background: {'#2a1515' if dark_mode else '#fff0f0'};
        border: 1px solid {accent3};
        border-radius: 12px;
        padding: 14px 18px;
        color: {accent3};
        font-size: 13px;
        font-weight: 500;
        margin: 12px 0;
    }}
    .alert-warning {{
        background: {'#2a2210' if dark_mode else '#fffbf0'};
        border: 1px solid {accent4};
        border-radius: 12px;
        padding: 14px 18px;
        color: {accent4};
        font-size: 13px;
        font-weight: 500;
        margin: 12px 0;
    }}
    .alert-success {{
        background: {'#102010' if dark_mode else '#f0fff4'};
        border: 1px solid {accent2};
        border-radius: 12px;
        padding: 14px 18px;
        color: {accent2};
        font-size: 13px;
        font-weight: 500;
        margin: 12px 0;
    }}
    .alert-info {{
        background: {'#101f30' if dark_mode else '#f0f7ff'};
        border: 1px solid {accent};
        border-radius: 12px;
        padding: 14px 18px;
        color: {accent};
        font-size: 13px;
        font-weight: 500;
        margin: 12px 0;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: {card_bg};
        border-radius: 12px;
        padding: 4px;
        border: 1px solid {card_border};
        gap: 2px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 9px;
        font-weight: 500;
        font-size: 13px;
        color: {text_secondary};
        background: transparent;
        padding: 8px 18px;
    }}
    .stTabs [aria-selected="true"] {{
        background: {accent} !important;
        color: #ffffff !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        padding: 20px 0 0;
    }}

    /* Divider */
    hr {{ border-color: {card_border}; margin: 20px 0; }}

    /* Section header */
    .section-header {{
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 16px;
    }}
    .section-icon {{
        font-size: 20px;
    }}

    /* Sidebar label */
    .sidebar-section {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: {text_secondary};
        margin: 18px 0 8px;
    }}
    .nav-item {{
        display: flex; align-items: center; gap: 8px;
        padding: 7px 10px;
        border-radius: 9px;
        font-size: 13px;
        font-weight: 500;
        color: {text_primary};
        cursor: pointer;
        transition: background 0.15s;
    }}
    .nav-item:hover {{ background: {card_bg}; }}

    /* Progress bar */
    .stProgress > div > div > div > div {{
        background: {accent};
        border-radius: 4px;
    }}

    /* Spinner */
    .stSpinner > div {{ color: {accent}; }}

    /* Metric */
    [data-testid="metric-container"] {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 14px;
        padding: 16px;
    }}
    [data-testid="stMetricValue"] {{ color: {text_primary}; font-size: 26px; font-weight: 700; }}
    [data-testid="stMetricLabel"] {{ color: {text_secondary}; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }}

    /* Radio */
    .stRadio > div {{ gap: 6px; }}
    .stRadio > div label {{ font-size: 13px; font-weight: 500; color: {text_primary} !important; }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {input_border}; border-radius: 10px; }}

    /* Code block */
    code {{ background: {input_bg}; border-radius: 6px; padding: 2px 8px; font-size: 13px; color: {accent}; }}
    pre {{ background: {input_bg} !important; border-radius: 12px !important; border: 1px solid {card_border} !important; }}

    /* Hide streamlit branding */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}

    /* Selectbox dropdown */
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        border: 1px solid {input_border} !important;
        border-radius: 10px !important;
    }}

    /* ATS Score display */
    .ats-score-ring {{
        width: 80px; height: 80px;
        border-radius: 50%;
        background: conic-gradient({accent2} var(--pct), {input_border} 0);
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; font-weight: 700; color: {text_primary};
    }}
    </style>
    """, unsafe_allow_html=True)


# ── Gemini Setup ──────────────────────────────────────────────────────────────
def get_gemini_model():
    """Configure and return Gemini model. Returns None if key missing."""
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        return model
    except Exception as e:
        st.session_state["gemini_error"] = str(e)
        return None


def call_gemini(prompt: str, system: str = "") -> str:
    """Call Gemini and return text. Raises on failure."""
    model = get_gemini_model()
    if model is None:
        raise ValueError("Gemini API key not configured. Please enter it in the sidebar.")
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")


# ── Session State Defaults ────────────────────────────────────────────────────
DEFAULTS = {
    "page": "Overview Dashboard",
    "dark_mode": True,
    "gemini_api_key": "",
    "resume_data": None,          # parsed structured resume dict
    "generated_resume_text": "",  # formatted resume markdown
    "cover_letter": "",
    "ats_result": None,           # dict: score, keywords, gaps, suggestions
    "ats_history": [],            # list of scores for trend chart
    "logs": [
        {"type": "system", "msg": "LLM Engine connected to Gemini 2.0 Flash."},
        {"type": "module", "msg": "PDF Generation engine ready."},
        {"type": "memory", "msg": "Waiting for user to generate a resume…"},
    ],
    "template_style": "Standard Corporate",
    "resume_tab": "1. Setup & Data Input",
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def add_log(log_type: str, msg: str):
    st.session_state["logs"].insert(0, {"type": log_type, "msg": msg})
    if len(st.session_state["logs"]) > 20:
        st.session_state["logs"] = st.session_state["logs"][:20]


# ── PDF Generator ─────────────────────────────────────────────────────────────
def generate_pdf_bytes(content: str, title: str = "Document") -> bytes:
    """Convert markdown-ish text to PDF bytes using FPDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 12, title, ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", size=10)
    clean = re.sub(r"#{1,6}\s*", "", content)          # remove # headings
    clean = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", clean)  # remove bold/italic
    clean = re.sub(r"`(.+?)`", r"\1", clean)            # remove code ticks
    clean = re.sub(r"---+", "─" * 60, clean)           # horizontal rule

    for line in clean.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
        # Bold-ish headings
        if line.startswith("##") or line.isupper():
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, line.lstrip("#").strip())
            pdf.set_font("Helvetica", size=10)
            pdf.set_text_color(0, 0, 0)
        elif line.startswith("•") or line.startswith("-"):
            pdf.multi_cell(0, 5, "  " + line)
        else:
            pdf.multi_cell(0, 5, line)

    return pdf.output(dest="S").encode("latin-1")


# ── Prompts ───────────────────────────────────────────────────────────────────
RESUME_SYSTEM = """You are an expert ATS-optimised resume writer with 15+ years of experience.
Output ONLY a well-structured professional resume in Markdown. No preamble. No commentary.
Sections: Professional Summary | Work Experience | Education | Skills | Certifications (if any) | Projects (if any).
Use strong action verbs, quantify achievements, mirror keywords from the target job title."""

COVER_LETTER_SYSTEM = """You are an expert career coach writing highly personalised, compelling cover letters.
Output ONLY the cover letter text. No preamble. No meta-commentary.
Keep it under 400 words. Use 3 paragraphs: Hook + Value, Evidence, Call-to-action."""

ATS_SYSTEM = """You are an ATS (Applicant Tracking System) specialist.
Analyse the resume against the job description and return ONLY valid JSON with this exact shape:
{
  "score": <integer 0-100>,
  "matched_keywords": [<string>, ...],
  "missing_keywords": [<string>, ...],
  "strengths": [<string>, ...],
  "improvements": [<string>, ...]
}
No markdown fences. No extra text. Pure JSON only."""

PARSE_SYSTEM = """You are a resume parser. Extract information from the raw text and return ONLY valid JSON:
{
  "name": "",
  "email": "",
  "phone": "",
  "linkedin": "",
  "github": "",
  "target_job": "",
  "summary": "",
  "experience": [{"title":"","company":"","dates":"","bullets":[]}],
  "education": [{"degree":"","institution":"","year":""}],
  "skills": [],
  "certifications": [],
  "projects": [{"name":"","description":""}]
}
No markdown fences. Pure JSON only."""


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ AI Studio Menu")
        st.markdown('<div class="sidebar-section">Navigate Workspace</div>', unsafe_allow_html=True)

        pages = [
            ("🗂️", "Overview Dashboard"),
            ("📄", "Smart Resume Builder"),
            ("✉️", "Cover Letter Generator"),
            ("🔍", "ATS Match Engine"),
        ]
        for icon, name in pages:
            selected = st.session_state["page"] == name
            label = f"{'● ' if selected else '○ '}{icon} {name}"
            if st.button(label, key=f"nav_{name}", use_container_width=True):
                st.session_state["page"] = name
                st.rerun()

        st.divider()

        # Theme toggle
        st.session_state["dark_mode"] = st.toggle("🌙 Dark Mode", value=st.session_state["dark_mode"])

        st.divider()

        # API Key
        st.markdown('<div class="sidebar-section">Gemini API Key</div>', unsafe_allow_html=True)
        key_input = st.text_input(
            "API Key", type="password",
            value=st.session_state["gemini_api_key"],
            placeholder="AIza...",
            label_visibility="collapsed",
        )
        if key_input != st.session_state["gemini_api_key"]:
            st.session_state["gemini_api_key"] = key_input
            if key_input:
                add_log("system", "API key updated. LLM Engine re-configured.")

        st.divider()

        # Job Portal hint
        target_job = ""
        if st.session_state["resume_data"]:
            target_job = st.session_state["resume_data"].get("target_job", "")

        st.markdown("### 🌐 Job Portal")
        if not target_job:
            st.markdown(
                '<div class="alert-warning">💡 Fill out the <b>Target Job Title</b> in the Resume Builder to unlock the LinkedIn Job Portal.</div>',
                unsafe_allow_html=True,
            )
        else:
            url = f"https://www.linkedin.com/jobs/search/?keywords={target_job.replace(' ', '%20')}"
            st.markdown(f'🔗 **[Search LinkedIn Jobs →]({url})**')
            st.caption(f"Searching for: *{target_job}*")


# ── Page: Overview Dashboard ──────────────────────────────────────────────────
def page_overview():
    st.markdown("# Welcome to your Career Workspace")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""<div class="stat-card">
            <div class="stat-label">Dynamic Templates</div>
            <div class="stat-value">3 Styles</div>
            <span class="stat-badge badge-active">↑ Active 🟢</span>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="stat-card">
            <div class="stat-label">Input Modes</div>
            <div class="stat-value">Dual (Auto/…</div>
            <span class="stat-badge badge-enabled">↑ Enabled ⚡</span>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="stat-card">
            <div class="stat-label">Cover Letters</div>
            <div class="stat-value">Auto-Gen</div>
            <span class="stat-badge badge-ready">↑ Ready 📄</span>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""<div class="stat-card">
            <div class="stat-label">ATS Scanner</div>
            <div class="stat-value">Semantic NLP</div>
            <span class="stat-badge badge-online">↑ Online 🚀</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("## 📈 ATS Optimization Trends")
        st.caption("Average ATS Match Scores generated by the AI over the last 7 sessions.")
        history = st.session_state["ats_history"]
        if history:
            import pandas as pd
            df = pd.DataFrame({"Session": list(range(1, len(history)+1)), "ATS Match Score (%)": history})
            st.line_chart(df.set_index("Session"), use_container_width=True, height=220)
        else:
            # Placeholder chart
            import pandas as pd
            placeholder = [65, 72, 70, 78, 85, 88, 95]
            df = pd.DataFrame({"Session": list(range(1, 8)), "ATS Match Score (%)": placeholder})
            st.line_chart(df.set_index("Session"), use_container_width=True, height=220)

    with col_right:
        st.markdown("## ⚡ Live System Logs")
        logs = st.session_state["logs"]
        for log in logs[:6]:
            t = log["type"]
            css = f"log-{t}"
            icons = {"system": "✅", "module": "ℹ️", "memory": "⏳"}
            labels = {"system": "System", "module": "Module", "memory": "Memory"}
            icon = icons.get(t, "🔹")
            label = labels.get(t, t.capitalize())
            st.markdown(
                f'<div class="{css}"><b>[{label}]</b> {icon} {log["msg"]}</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # Quick action cards
    st.markdown("## 🚀 Quick Actions")
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        st.markdown('<div class="apple-card"><h3>📄 Build Resume</h3><p>Create an ATS-optimised resume from scratch or your LinkedIn data.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Resume Builder", key="qa_resume"):
            st.session_state["page"] = "Smart Resume Builder"
            st.rerun()
    with qa2:
        st.markdown('<div class="apple-card"><h3>✉️ Write Cover Letter</h3><p>Auto-generate a tailored cover letter based on your resume.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Cover Letter", key="qa_cover"):
            st.session_state["page"] = "Cover Letter Generator"
            st.rerun()
    with qa3:
        st.markdown('<div class="apple-card"><h3>🔍 ATS Scan</h3><p>Upload a job description and get your match score instantly.</p></div>', unsafe_allow_html=True)
        if st.button("Go to ATS Engine", key="qa_ats"):
            st.session_state["page"] = "ATS Match Engine"
            st.rerun()


# ── Page: Smart Resume Builder ────────────────────────────────────────────────
def page_resume_builder():
    st.markdown("# 📄 Smart Resume Builder")

    tab1, tab2 = st.tabs(["⚙️ 1. Setup & Data Input", "🤖 2. AI Output & Export"])

    # ── TAB 1: Input ──
    with tab1:
        st.markdown("## ⚙️ Template Settings")
        template_style = st.selectbox(
            "Select Professional Template Style",
            ["Standard Corporate", "Creative Modern", "Minimalist Clean"],
            index=["Standard Corporate", "Creative Modern", "Minimalist Clean"].index(
                st.session_state["template_style"]
            ),
        )
        st.session_state["template_style"] = template_style

        st.divider()
        st.markdown("## 📋 Choose Data Input Method")
        input_mode = st.radio(
            "How do you want to provide your details?",
            ["⚡ Auto-Parse (Paste LinkedIn/Resume Data)", "🖊️ Manual Entry (Fill Structured Form)"],
            horizontal=True,
        )

        if "Auto-Parse" in input_mode:
            st.markdown(
                '<div class="alert-info">💡 <b>Fast-Import:</b> Skip the typing! Copy your entire LinkedIn profile or old resume text and paste it below. The AI will extract and organise it automatically.</div>',
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            with col1:
                full_name  = st.text_input("Full Name *", placeholder="e.g. Syed Zaid Karim")
                email      = st.text_input("Email (for PDF links)")
                github_url = st.text_input("GitHub URL (for PDF links)")
            with col2:
                target_job  = st.text_input("Target Job Title *", placeholder="e.g. Computer Science Engineering Student")
                phone       = st.text_input("Phone Number (for PDF links)")
                linkedin_url= st.text_input("LinkedIn URL (for PDF links)")

            raw_text = st.text_area(
                "Raw Experience / Education / LinkedIn Data *",
                placeholder="Paste your raw text here…",
                height=180,
            )

            if st.button("✨ Auto Generate AI Resume", type="primary"):
                if not full_name or not target_job or not raw_text:
                    st.markdown('<div class="alert-error">⚠️ Full Name, Target Job Title, and Raw Data are required.</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("🤖 Parsing your data with Gemini…"):
                        try:
                            parse_prompt = f"""
Name: {full_name}
Email: {email}
Phone: {phone}
LinkedIn: {linkedin_url}
GitHub: {github_url}
Target Job: {target_job}

Raw Data:
{raw_text}
"""
                            parsed_json = call_gemini(parse_prompt, system=PARSE_SYSTEM)
                            parsed_json = re.sub(r"```json|```", "", parsed_json).strip()
                            resume_data = json.loads(parsed_json)
                            # Override with explicit fields if provided
                            if full_name:  resume_data["name"]       = full_name
                            if email:      resume_data["email"]      = email
                            if phone:      resume_data["phone"]      = phone
                            if linkedin_url: resume_data["linkedin"] = linkedin_url
                            if github_url: resume_data["github"]     = github_url
                            if target_job: resume_data["target_job"] = target_job
                            st.session_state["resume_data"] = resume_data

                            add_log("system", f"Resume data parsed for {full_name}.")
                        except json.JSONDecodeError:
                            st.markdown('<div class="alert-error">⚠️ Could not parse JSON from Gemini. Try rephrasing your raw data.</div>', unsafe_allow_html=True)
                            add_log("memory", "Parse failed — JSON decode error.")
                            st.stop()
                        except Exception as e:
                            st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)
                            add_log("memory", f"Error: {e}")
                            st.stop()

                    with st.spinner("✍️ Generating ATS-optimised resume…"):
                        try:
                            r = st.session_state["resume_data"]
                            resume_prompt = f"""
Name: {r.get('name','')}
Email: {r.get('email','')} | Phone: {r.get('phone','')}
LinkedIn: {r.get('linkedin','')} | GitHub: {r.get('github','')}
Target Job Title: {r.get('target_job','')}
Template Style: {template_style}

Parsed Data:
{json.dumps(r, indent=2)}

Generate a full professional resume."""
                            resume_md = call_gemini(resume_prompt, system=RESUME_SYSTEM)
                            st.session_state["generated_resume_text"] = resume_md
                            add_log("module", f"Resume generated. Template: {template_style}.")
                            st.success("✅ Resume generated! Go to Tab 2 to view and export.")
                            st.session_state["resume_tab"] = "2. AI Output & Export"
                        except Exception as e:
                            st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

        else:  # Manual Entry
            st.markdown("### 👤 Personal Information")
            col1, col2 = st.columns(2)
            with col1:
                m_name    = st.text_input("Full Name *", key="m_name")
                m_email   = st.text_input("Email", key="m_email")
                m_github  = st.text_input("GitHub URL", key="m_github")
            with col2:
                m_job     = st.text_input("Target Job Title *", key="m_job")
                m_phone   = st.text_input("Phone Number", key="m_phone")
                m_linkedin= st.text_input("LinkedIn URL", key="m_linkedin")

            st.markdown("### 📝 Professional Summary")
            m_summary = st.text_area("Summary", placeholder="Brief professional summary…", height=90, key="m_summary")

            st.markdown("### 💼 Work Experience")
            m_exp = st.text_area(
                "Experience (paste each role — title, company, dates, key achievements)",
                placeholder="Software Engineer, Acme Corp, 2022–Present\n- Led team of 5…\n- Reduced latency by 40%…",
                height=160, key="m_exp",
            )

            st.markdown("### 🎓 Education")
            m_edu = st.text_area(
                "Education",
                placeholder="B.Tech Computer Science, XYZ University, 2020",
                height=80, key="m_edu",
            )

            st.markdown("### 🛠️ Skills & Certifications")
            col1, col2 = st.columns(2)
            with col1:
                m_skills = st.text_area("Skills (comma-separated)", height=70, key="m_skills")
            with col2:
                m_certs  = st.text_area("Certifications", height=70, key="m_certs")

            st.markdown("### 🚀 Projects")
            m_projects = st.text_area("Projects", placeholder="Project Name – Brief description", height=90, key="m_projects")

            if st.button("✨ Generate AI Resume from Form", type="primary"):
                if not m_name or not m_job:
                    st.markdown('<div class="alert-error">⚠️ Full Name and Target Job Title are required.</div>', unsafe_allow_html=True)
                else:
                    resume_data = {
                        "name": m_name, "email": m_email, "phone": m_phone,
                        "linkedin": m_linkedin, "github": m_github,
                        "target_job": m_job, "summary": m_summary,
                        "experience_raw": m_exp, "education_raw": m_edu,
                        "skills_raw": m_skills, "certifications": m_certs,
                        "projects_raw": m_projects,
                    }
                    st.session_state["resume_data"] = resume_data
                    with st.spinner("✍️ Generating resume…"):
                        try:
                            prompt = f"""
Name: {m_name} | Email: {m_email} | Phone: {m_phone}
LinkedIn: {m_linkedin} | GitHub: {m_github}
Target Job: {m_job}
Template Style: {template_style}

Summary: {m_summary}
Experience: {m_exp}
Education: {m_edu}
Skills: {m_skills}
Certifications: {m_certs}
Projects: {m_projects}

Generate a full professional resume."""
                            resume_md = call_gemini(prompt, system=RESUME_SYSTEM)
                            st.session_state["generated_resume_text"] = resume_md
                            add_log("module", f"Manual resume generated for {m_name}.")
                            st.success("✅ Resume generated! Go to Tab 2 to view and export.")
                        except Exception as e:
                            st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

    # ── TAB 2: Output ──
    with tab2:
        resume_text = st.session_state.get("generated_resume_text", "")
        if not resume_text:
            st.markdown('<div class="alert-warning">⚠️ No resume generated yet. Complete Step 1 first.</div>', unsafe_allow_html=True)
            return

        st.markdown("## ✅ Your AI-Generated Resume")
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        st.markdown(resume_text)
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                "⬇️ Download as Markdown (.md)",
                data=resume_text,
                file_name="resume.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col2:
            try:
                pdf_bytes = generate_pdf_bytes(resume_text, "Resume")
                st.download_button(
                    "⬇️ Download as PDF",
                    data=pdf_bytes,
                    file_name="resume.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"PDF export unavailable: {e}")
        with col3:
            if st.button("♻️ Regenerate Resume", use_container_width=True):
                st.session_state["generated_resume_text"] = ""
                st.rerun()

        st.divider()
        st.markdown("### ✏️ Edit Resume")
        edited = st.text_area("Edit the resume text directly:", value=resume_text, height=350)
        if st.button("💾 Save Edits"):
            st.session_state["generated_resume_text"] = edited
            add_log("module", "Resume manually edited and saved.")
            st.success("✅ Edits saved.")
            st.rerun()


# ── Page: Cover Letter Generator ─────────────────────────────────────────────
def page_cover_letter():
    st.markdown("# ✉️ Auto-Cover Letter")
    st.caption("Generate a highly personalised cover letter based on the exact data from your current resume.")

    if not st.session_state.get("resume_data"):
        st.markdown(
            '<div class="alert-error">⚠️ No resume found in memory! Please build your resume in the <b>Smart Resume Builder</b> first so the AI knows your background.</div>',
            unsafe_allow_html=True,
        )
        return

    r = st.session_state["resume_data"]
    st.markdown(f'<div class="alert-success">✅ Resume loaded for <b>{r.get("name","Unknown")}</b> — Target: <b>{r.get("target_job","N/A")}</b></div>', unsafe_allow_html=True)

    st.markdown("### 🎯 Job Details")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name *", placeholder="e.g. Google")
        hiring_manager = st.text_input("Hiring Manager Name (optional)", placeholder="e.g. Ms. Priya Sharma")
    with col2:
        job_title = st.text_input("Exact Job Title *", placeholder="e.g. Software Engineer, L4")
        tone = st.selectbox("Tone", ["Professional", "Enthusiastic", "Confident", "Concise"])

    job_desc = st.text_area(
        "Paste Job Description (optional but recommended)",
        placeholder="Paste the job description here for maximum personalisation…",
        height=150,
    )

    if st.button("✨ Generate Cover Letter", type="primary"):
        if not company_name or not job_title:
            st.markdown('<div class="alert-error">⚠️ Company Name and Job Title are required.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("✍️ Writing your personalised cover letter…"):
                try:
                    prompt = f"""
Candidate Resume Data:
{json.dumps(r, indent=2)}

Job Title: {job_title}
Company: {company_name}
Hiring Manager: {hiring_manager or 'Hiring Manager'}
Tone: {tone}
Job Description: {job_desc or 'Not provided'}

Write a cover letter."""
                    cl = call_gemini(prompt, system=COVER_LETTER_SYSTEM)
                    st.session_state["cover_letter"] = cl
                    add_log("module", f"Cover letter generated for {company_name}.")
                except Exception as e:
                    st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

    if st.session_state.get("cover_letter"):
        st.divider()
        st.markdown("## ✅ Your Cover Letter")
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        st.markdown(st.session_state["cover_letter"])
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                "⬇️ Download as Text (.txt)",
                data=st.session_state["cover_letter"],
                file_name="cover_letter.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col2:
            try:
                pdf_bytes = generate_pdf_bytes(st.session_state["cover_letter"], "Cover Letter")
                st.download_button(
                    "⬇️ Download as PDF",
                    data=pdf_bytes,
                    file_name="cover_letter.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"PDF export unavailable: {e}")
        with col3:
            if st.button("♻️ Regenerate", use_container_width=True):
                st.session_state["cover_letter"] = ""
                st.rerun()

        st.divider()
        st.markdown("### ✏️ Edit Cover Letter")
        edited_cl = st.text_area("Edit directly:", value=st.session_state["cover_letter"], height=250)
        if st.button("💾 Save Edits", key="save_cl"):
            st.session_state["cover_letter"] = edited_cl
            add_log("module", "Cover letter manually edited.")
            st.success("✅ Edits saved.")
            st.rerun()


# ── Page: ATS Match Engine ────────────────────────────────────────────────────
def page_ats_engine():
    st.markdown("# 🔍 ATS Match Engine")
    st.caption("Semantic NLP-powered Applicant Tracking System analyser.")

    resume_text = st.session_state.get("generated_resume_text", "")
    if not resume_text and st.session_state.get("resume_data"):
        resume_text = json.dumps(st.session_state["resume_data"], indent=2)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 Resume")
        if resume_text:
            st.markdown('<div class="alert-success">✅ Resume loaded from memory.</div>', unsafe_allow_html=True)
            resume_override = st.text_area("Override / Edit Resume Text:", value=resume_text, height=220)
        else:
            st.markdown('<div class="alert-warning">⚠️ No resume in memory. Paste manually below.</div>', unsafe_allow_html=True)
            resume_override = st.text_area("Paste Resume Text:", height=220, placeholder="Paste your resume…")

    with col2:
        st.markdown("### 💼 Job Description")
        job_desc_ats = st.text_area(
            "Paste the full Job Description *",
            height=220,
            placeholder="Paste the complete job description here…",
        )

    if st.button("🔍 Run ATS Analysis", type="primary"):
        final_resume = resume_override if resume_override.strip() else resume_text
        if not final_resume:
            st.markdown('<div class="alert-error">⚠️ Resume text is required.</div>', unsafe_allow_html=True)
        elif not job_desc_ats.strip():
            st.markdown('<div class="alert-error">⚠️ Job Description is required.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("🤖 Running semantic ATS analysis…"):
                try:
                    prompt = f"""
RESUME:
{final_resume}

JOB DESCRIPTION:
{job_desc_ats}

Analyse and return JSON."""
                    raw = call_gemini(prompt, system=ATS_SYSTEM)
                    raw = re.sub(r"```json|```", "", raw).strip()
                    result = json.loads(raw)
                    st.session_state["ats_result"] = result

                    score = result.get("score", 0)
                    st.session_state["ats_history"].append(score)
                    if len(st.session_state["ats_history"]) > 7:
                        st.session_state["ats_history"] = st.session_state["ats_history"][-7:]
                    add_log("system", f"ATS analysis complete. Score: {score}/100.")
                except json.JSONDecodeError:
                    st.markdown('<div class="alert-error">⚠️ Could not parse ATS JSON. Try again.</div>', unsafe_allow_html=True)
                    add_log("memory", "ATS JSON parse error.")
                except Exception as e:
                    st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

    result = st.session_state.get("ats_result")
    if result:
        st.divider()
        score = result.get("score", 0)
        color = "#30d158" if score >= 75 else "#ffd60a" if score >= 50 else "#ff453a"

        st.markdown(f"""
        <div class="apple-card" style="text-align:center; padding: 30px;">
            <div style="font-size:72px; font-weight:800; color:{color}; letter-spacing:-0.04em;">{score}<span style="font-size:32px">%</span></div>
            <div style="font-size:14px; color:var(--text-secondary); margin-top:4px;">ATS Match Score</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("### ✅ Matched Keywords")
            matched = result.get("matched_keywords", [])
            if matched:
                for kw in matched:
                    st.markdown(f'<span style="background:#1a3a1a;color:#30d158;padding:3px 10px;border-radius:20px;font-size:12px;margin:2px;display:inline-block">{kw}</span>', unsafe_allow_html=True)
            else:
                st.caption("None detected.")

        with col2:
            st.markdown("### ❌ Missing Keywords")
            missing = result.get("missing_keywords", [])
            if missing:
                for kw in missing:
                    st.markdown(f'<span style="background:#2a1515;color:#ff453a;padding:3px 10px;border-radius:20px;font-size:12px;margin:2px;display:inline-block">{kw}</span>', unsafe_allow_html=True)
            else:
                st.caption("None — excellent match!")

        with col3:
            st.markdown("### 💪 Strengths")
            strengths = result.get("strengths", [])
            for s in strengths:
                st.markdown(f"• {s}")

        with col4:
            st.markdown("### 🔧 Improvements")
            improvements = result.get("improvements", [])
            for imp in improvements:
                st.markdown(f"• {imp}")

        st.divider()

        # One-click tailoring
        st.markdown("### 🪄 One-Click Resume Tailoring")
        st.caption("Automatically rewrite your resume to target missing keywords.")
        if st.button("✨ Tailor Resume to This Job", type="primary"):
            if not resume_text:
                st.markdown('<div class="alert-error">⚠️ No resume in memory to tailor.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("🤖 Tailoring resume…"):
                    try:
                        missing_kws = ", ".join(result.get("missing_keywords", []))
                        tailor_prompt = f"""
Current Resume:
{resume_text}

Job Description:
{job_desc_ats}

Missing Keywords to incorporate naturally: {missing_kws}

Rewrite the resume to achieve a higher ATS match. Keep it truthful and professional."""
                        tailored = call_gemini(tailor_prompt, system=RESUME_SYSTEM)
                        st.session_state["generated_resume_text"] = tailored
                        add_log("module", "Resume tailored to job description.")
                        st.success("✅ Resume tailored! View it in the Resume Builder → Tab 2.")
                    except Exception as e:
                        st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

        # Export report
        report = f"""ATS ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

SCORE: {score}/100

MATCHED KEYWORDS:
{chr(10).join('• ' + k for k in result.get('matched_keywords', []))}

MISSING KEYWORDS:
{chr(10).join('• ' + k for k in result.get('missing_keywords', []))}

STRENGTHS:
{chr(10).join('• ' + s for s in result.get('strengths', []))}

IMPROVEMENTS:
{chr(10).join('• ' + i for i in result.get('improvements', []))}
"""
        st.download_button("⬇️ Download ATS Report (.txt)", data=report, file_name="ats_report.txt", mime="text/plain")


# ── Main Router ───────────────────────────────────────────────────────────────
def main():
    dark_mode = st.session_state.get("dark_mode", True)
    inject_css(dark_mode)
    render_sidebar()

    page = st.session_state["page"]
    if page == "Overview Dashboard":
        page_overview()
    elif page == "Smart Resume Builder":
        page_resume_builder()
    elif page == "Cover Letter Generator":
        page_cover_letter()
    elif page == "ATS Match Engine":
        page_ats_engine()


if __name__ == "__main__":
    main()
