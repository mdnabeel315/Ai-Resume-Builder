import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime
from fpdf import FPDF
import os

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ZNA – AI Career Studio",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
DEFAULTS = {
    "page":                  "Overview Dashboard",
    "dark_mode":             True,
    "gemini_api_key":        "",
    "resume_data":           None,
    "generated_resume_text": "",
    "cover_letter":          "",
    "ats_result":            None,
    "ats_history":           [],
    "template_style":        "Standard Corporate",
    "logs": [
        {"type": "system", "msg": "LLM Engine connected to Gemini 2.0 Flash."},
        {"type": "module", "msg": "PDF Generation engine ready."},
        {"type": "memory", "msg": "Waiting for user to generate a resume…"},
    ],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR PALETTES
# ─────────────────────────────────────────────────────────────────────────────
def P():
    """Return the active palette dict."""
    d = st.session_state["dark_mode"]
    if d:
        return dict(
            bg="#08090d",          bg2="#0f1117",
            card="#13151c",        border="rgba(255,255,255,0.08)",
            text="#eef0f7",        muted="#7c8096",
            accent="#3b8bff",      accent2="#00d68f",
            accent3="#ff6b6b",     accent4="#f5c842",
            input_bg="#1a1d27",    input_border="rgba(255,255,255,0.12)",
            nav_bg="#112244",      nav_text="#90c0ff",
            nav_active_bg="#3b8bff", nav_active_text="#ffffff",
            log_sys="#0a2015",     log_mod="#0a1830",   log_mem="#25200a",
            shadow="rgba(0,0,0,0.5)",
        )
    return dict(
        bg="#f0f2f8",          bg2="#e8eaf4",
        card="#ffffff",        border="rgba(0,0,0,0.08)",
        text="#0d0f1a",        muted="#555a72",
        accent="#1a6fff",      accent2="#00a870",
        accent3="#e03a3a",     accent4="#d4a800",
        input_bg="#ffffff",    input_border="rgba(0,0,0,0.15)",
        nav_bg="#ddeeff",      nav_text="#0044bb",
        nav_active_bg="#1a6fff", nav_active_text="#ffffff",
        log_sys="#d4edda",     log_mod="#cce5ff",   log_mem="#fff3cd",
        shadow="rgba(0,0,0,0.08)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# CSS  (injected fresh every render so theme switch works instantly)
# ─────────────────────────────────────────────────────────────────────────────
def inject_css():
    p = P()
    dark = st.session_state["dark_mode"]
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500;600&display=swap');

/* ── Global ── */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"] {{
    background-color: {p['bg']} !important;
    color: {p['text']} !important;
}}
.main .block-container {{
    background-color: {p['bg']} !important;
    padding: 2rem 2.5rem !important;
    max-width: 1300px !important;
    font-family: 'DM Sans', sans-serif !important;
}}
* {{ font-family: 'DM Sans', sans-serif !important; }}
h1,h2,h3,h4 {{ font-family: 'Syne', sans-serif !important; }}

/* ── Sidebar shell ── */
section[data-testid="stSidebar"] > div:first-child {{
    background-color: {p['bg2']} !important;
    border-right: 1px solid {p['border']} !important;
    padding: 1.2rem 0.9rem !important;
}}

/* ── Sidebar nav buttons ── */
section[data-testid="stSidebar"] .stButton > button {{
    background-color: {p['nav_bg']} !important;
    color: {p['nav_text']} !important;
    border: 1px solid {p['input_border']} !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 12px !important;
    text-align: left !important;
    width: 100% !important;
    margin-bottom: 5px !important;
    transition: all 0.18s !important;
    box-shadow: none !important;
    letter-spacing: 0 !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background-color: {p['nav_active_bg']} !important;
    color: {p['nav_active_text']} !important;
    border-color: {p['accent']} !important;
    transform: translateX(3px) !important;
    box-shadow: 0 0 0 0 transparent !important;
}}
section[data-testid="stSidebar"] .stButton > button:focus:not(:active) {{
    background-color: {p['nav_active_bg']} !important;
    color: {p['nav_active_text']} !important;
}}

/* ── Main buttons ── */
.main .stButton > button {{
    background-color: {p['accent']} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 11px 24px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
    box-shadow: 0 3px 14px {p['shadow']} !important;
    letter-spacing: -0.01em !important;
}}
.main .stButton > button:hover {{
    opacity: 0.87 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px {p['shadow']} !important;
}}

/* ── Download buttons ── */
.stDownloadButton > button {{
    background-color: {p['accent2']} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 11px 24px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
}}
.stDownloadButton > button:hover {{
    opacity: 0.87 !important;
    transform: translateY(-2px) !important;
}}

/* ── Typography ── */
h1 {{ font-size: 36px !important; font-weight: 800 !important;
      letter-spacing: -0.03em !important; color: {p['text']} !important;
      margin-bottom: 4px !important; line-height: 1.1 !important; }}
h2 {{ font-size: 22px !important; font-weight: 700 !important;
      letter-spacing: -0.02em !important; color: {p['text']} !important; }}
h3 {{ font-size: 16px !important; font-weight: 700 !important;
      color: {p['text']} !important; }}
p, li {{ color: {p['muted']} !important; font-size: 14px !important;
         line-height: 1.65 !important; }}
label, .stRadio label {{
    color: {p['muted']} !important; font-size: 13px !important;
    font-weight: 500 !important;
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea {{
    background-color: {p['input_bg']} !important;
    border: 1px solid {p['input_border']} !important;
    border-radius: 10px !important;
    color: {p['text']} !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {{
    border-color: {p['accent']} !important;
    box-shadow: 0 0 0 3px {p['accent']}28 !important;
    outline: none !important;
}}
div[data-baseweb="select"] > div {{
    background-color: {p['input_bg']} !important;
    border: 1px solid {p['input_border']} !important;
    border-radius: 10px !important;
}}
div[data-baseweb="select"] span {{ color: {p['text']} !important; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {p['card']}; border-radius: 12px;
    padding: 4px; border: 1px solid {p['border']}; gap: 3px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 9px; font-weight: 600; font-size: 13px;
    color: {p['muted']}; background: transparent; padding: 8px 18px;
}}
.stTabs [aria-selected="true"] {{
    background: {p['accent']} !important; color: #ffffff !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 20px; }}

/* ── Toggle / Checkbox ── */
.stCheckbox > label, .stToggle > label {{
    color: {p['text']} !important;
    font-size: 13px !important; font-weight: 600 !important;
}}

/* ── Cards ── */
.zna-card {{
    background: {p['card']};
    border: 1px solid {p['border']};
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 20px {p['shadow']};
    transition: box-shadow .25s, transform .25s;
}}
.zna-card:hover {{
    box-shadow: 0 6px 32px {p['shadow']};
    transform: translateY(-2px);
}}

/* ── Stat cards ── */
.stat-card {{
    background: {p['card']}; border: 1px solid {p['border']};
    border-radius: 16px; padding: 22px;
    box-shadow: 0 1px 10px {p['shadow']};
}}
.stat-label {{
    font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: {p['muted']}; margin-bottom: 8px;
}}
.stat-value {{
    font-size: 26px; font-weight: 800; color: {p['text']};
    letter-spacing: -0.03em; line-height: 1; margin-bottom: 12px;
    font-family: 'Syne', sans-serif;
}}
.stat-badge {{
    display: inline-flex; align-items: center;
    padding: 4px 11px; border-radius: 20px;
    font-size: 11px; font-weight: 700;
}}
.badge-active  {{ background:{'#0a2015' if dark else '#d4edda'}; color:{p['accent2']}; }}
.badge-enabled {{ background:{'#0a1830' if dark else '#cce5ff'}; color:{p['accent']};  }}
.badge-ready   {{ background:{'#1e1030' if dark else '#ede7f6'}; color:#bf5af2; }}
.badge-online  {{ background:{'#2a1010' if dark else '#fce4ec'}; color:{p['accent3']}; }}

/* ── Log items ── */
.log-system {{
    background:{p['log_sys']}; border-left:3px solid {p['accent2']};
    border-radius:10px; padding:11px 15px; margin:6px 0;
    font-size:13px; color:{p['text']};
}}
.log-module {{
    background:{p['log_mod']}; border-left:3px solid {p['accent']};
    border-radius:10px; padding:11px 15px; margin:6px 0;
    font-size:13px; color:{p['text']};
}}
.log-memory {{
    background:{p['log_mem']}; border-left:3px solid {p['accent4']};
    border-radius:10px; padding:11px 15px; margin:6px 0;
    font-size:13px; color:{p['text']};
}}

/* ── Alert boxes ── */
.alert-error {{
    background:{'#2a1010' if dark else '#fff0f0'};
    border:1px solid {p['accent3']};
    border-radius:12px; padding:13px 16px;
    color:{p['accent3']}; font-size:13px; font-weight:500; margin:10px 0;
}}
.alert-warning {{
    background:{'#25200a' if dark else '#fff8e1'};
    border:1px solid {p['accent4']};
    border-radius:12px; padding:13px 16px;
    color:{p['accent4']}; font-size:13px; font-weight:500; margin:10px 0;
}}
.alert-success {{
    background:{'#0a2015' if dark else '#d4edda'};
    border:1px solid {p['accent2']};
    border-radius:12px; padding:13px 16px;
    color:{p['accent2']}; font-size:13px; font-weight:500; margin:10px 0;
}}
.alert-info {{
    background:{'#0a1830' if dark else '#cce5ff'};
    border:1px solid {p['accent']};
    border-radius:12px; padding:13px 16px;
    color:{p['accent']}; font-size:13px; font-weight:500; margin:10px 0;
}}

/* ── Keyword chips ── */
.chip-green {{
    background:{'#0a2015' if dark else '#d4edda'};
    color:{p['accent2']};
    padding:3px 10px; border-radius:20px;
    font-size:12px; margin:2px; display:inline-block;
}}
.chip-red {{
    background:{'#2a1010' if dark else '#fce4ec'};
    color:{p['accent3']};
    padding:3px 10px; border-radius:20px;
    font-size:12px; margin:2px; display:inline-block;
}}

/* ── Sidebar labels ── */
.sidebar-label {{
    font-size:10px; font-weight:800; letter-spacing:0.14em;
    text-transform:uppercase; color:{p['muted']};
    margin:16px 0 8px; padding-left:4px;
}}

/* ── Divider ── */
hr {{ border-color:{p['border']} !important; margin:22px 0 !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:{p['input_border']}; border-radius:10px; }}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {{ display:none !important; visibility:hidden !important; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ZNA LOGO  (pure SVG – always renders correctly)
# ─────────────────────────────────────────────────────────────────────────────
ZNA_LOGO_HTML = """
<svg width="120" height="42" viewBox="0 0 120 42" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="zg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="#60b8ff"/>
      <stop offset="50%"  stop-color="#3b8bff"/>
      <stop offset="100%" stop-color="#1a5fd4"/>
    </linearGradient>
  </defs>
  <text x="2" y="32" font-family="Arial Black,Arial" font-weight="900"
        font-size="33" fill="url(#zg)" letter-spacing="-1">ZNA</text>
  <text x="100" y="14" font-family="Arial" font-size="11" fill="#3b8bff">✦</text>
  <text x="2" y="41" font-family="Arial" font-weight="700" font-size="7.5"
        fill="#3b8bff" letter-spacing="2.2">INNOVATE YOUR CAREER</text>
</svg>
"""


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI
# ─────────────────────────────────────────────────────────────────────────────
def get_gemini_model():
    api_key = st.session_state.get("gemini_api_key", "").strip() \
              or os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-2.0-flash")
    except Exception as e:
        st.session_state["_gemini_err"] = str(e)
        return None


def call_gemini(prompt: str, system: str = "") -> str:
    model = get_gemini_model()
    if not model:
        raise ValueError("Gemini API key not configured. Enter it in the sidebar.")
    full = f"{system}\n\n{prompt}" if system else prompt
    try:
        return model.generate_content(full).text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")


def add_log(kind: str, msg: str):
    st.session_state["logs"].insert(0, {"type": kind, "msg": msg})
    st.session_state["logs"] = st.session_state["logs"][:20]


# ─────────────────────────────────────────────────────────────────────────────
# PDF EXPORT
# ─────────────────────────────────────────────────────────────────────────────
def make_pdf(content: str, title: str = "Document") -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, title, ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Helvetica", size=10)
    clean = re.sub(r"#{1,6}\s*", "", content)
    clean = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", clean)
    clean = re.sub(r"`(.+?)`", r"\1", clean)
    for line in clean.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(3); continue
        if line.isupper() and len(line) < 70:
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, line)
            pdf.set_font("Helvetica", size=10)
        else:
            pdf.multi_cell(0, 5, line)
    return pdf.output(dest="S").encode("latin-1")


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────────────────────────────────────
RESUME_SYS = """You are an expert ATS-optimised resume writer with 15+ years experience.
Output ONLY a well-structured professional resume in Markdown. No preamble. No commentary.
Sections: Professional Summary | Work Experience | Education | Skills | Certifications | Projects.
Use strong action verbs, quantify achievements, mirror keywords from the target job title."""

COVER_SYS = """You are an expert career coach writing highly personalised cover letters.
Output ONLY the cover letter. No preamble. No meta-commentary.
Under 400 words. 3 paragraphs: Hook+Value, Evidence, Call-to-action."""

ATS_SYS = """You are an ATS specialist. Analyse the resume against the job description.
Return ONLY valid JSON, no markdown fences, no extra text:
{"score":<int 0-100>,"matched_keywords":[<str>],"missing_keywords":[<str>],"strengths":[<str>],"improvements":[<str>]}"""

PARSE_SYS = """You are a resume parser. Extract info from raw text.
Return ONLY valid JSON, no markdown fences, no extra text:
{"name":"","email":"","phone":"","linkedin":"","github":"","target_job":"","summary":"",
"experience":[{"title":"","company":"","dates":"","bullets":[]}],
"education":[{"degree":"","institution":"","year":""}],
"skills":[],"certifications":[],"projects":[{"name":"","description":""}]}"""


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def sidebar():
    p = P()
    with st.sidebar:
        # Logo
        st.markdown(ZNA_LOGO_HTML, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">AI Studio Menu</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-label" style="margin-top:2px">Navigate Workspace</div>', unsafe_allow_html=True)

        pages = [
            ("🗂️", "Overview Dashboard"),
            ("📄", "Smart Resume Builder"),
            ("✉️", "Cover Letter Generator"),
            ("🔍", "ATS Match Engine"),
        ]
        cur = st.session_state["page"]
        for icon, name in pages:
            prefix = "●" if cur == name else "○"
            if st.button(f"{prefix}  {icon}  {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state["page"] = name
                st.rerun()

        st.markdown("---")

        # Theme toggle
        new_dark = st.toggle("🌙  Dark Mode", value=st.session_state["dark_mode"])
        if new_dark != st.session_state["dark_mode"]:
            st.session_state["dark_mode"] = new_dark
            st.rerun()

        st.markdown("---")

        # API Key
        st.markdown('<div class="sidebar-label">Gemini API Key</div>', unsafe_allow_html=True)
        key = st.text_input("key", type="password",
                            value=st.session_state["gemini_api_key"],
                            placeholder="AIza…", label_visibility="collapsed")
        if key != st.session_state["gemini_api_key"]:
            st.session_state["gemini_api_key"] = key
            if key:
                add_log("system", "Gemini API key updated and configured.")

        st.markdown("---")

        # Job Portal
        st.markdown('<div class="sidebar-label">🌐 Job Portal</div>', unsafe_allow_html=True)
        job = (st.session_state["resume_data"] or {}).get("target_job", "")
        if not job:
            st.markdown(
                '<div class="alert-warning" style="font-size:12px">💡 Fill out the <b>Target Job Title</b> in the Resume Builder to unlock LinkedIn Job Portal.</div>',
                unsafe_allow_html=True)
        else:
            url = f"https://www.linkedin.com/jobs/search/?keywords={job.replace(' ','%20')}"
            st.markdown(f"🔗 **[Search LinkedIn Jobs →]({url})**")
            st.caption(f"Searching: *{job}*")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: OVERVIEW DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def page_overview():
    p = P()
    st.markdown(ZNA_LOGO_HTML, unsafe_allow_html=True)
    st.markdown("# Welcome to your Career Workspace")

    # Stat cards
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("Dynamic Templates", "3 Styles",     "badge-active",  "+ Active 🟢"),
        ("Input Modes",       "Dual (Auto/…", "badge-enabled", "+ Enabled ⚡"),
        ("Cover Letters",     "Auto-Gen",      "badge-ready",   "+ Ready 📄"),
        ("ATS Scanner",       "Semantic NLP",  "badge-online",  "+ Online 🚀"),
    ]
    for col, (label, val, badge_cls, badge_txt) in zip([c1,c2,c3,c4], cards):
        col.markdown(f"""
<div class="stat-card">
  <div class="stat-label">{label}</div>
  <div class="stat-value">{val}</div>
  <span class="stat-badge {badge_cls}">{badge_txt}</span>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown("## 📈 ATS Optimization Trends")
        st.caption("Average ATS Match Scores from the AI over the last 7 sessions.")
        import pandas as pd
        hist = st.session_state["ats_history"] or [65,72,70,78,85,88,95]
        df = pd.DataFrame({"Session": range(1, len(hist)+1), "ATS Match Score (%)": hist})
        st.line_chart(df.set_index("Session"), use_container_width=True, height=200)

    with col_r:
        st.markdown("## ⚡ Live System Logs")
        icons  = {"system":"✅","module":"ℹ️","memory":"⏳"}
        labels = {"system":"System","module":"Module","memory":"Memory"}
        for log in st.session_state["logs"][:5]:
            t = log["type"]
            st.markdown(
                f'<div class="log-{t}"><b>[{labels.get(t,t)}]</b> {icons.get(t,"🔹")} {log["msg"]}</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🚀 Quick Actions")
    qa1, qa2, qa3 = st.columns(3)
    actions = [
        (qa1, "📄 Build Resume",        "Create an ATS-optimised resume from scratch or your LinkedIn data.",  "Smart Resume Builder"),
        (qa2, "✉️ Write Cover Letter", "Auto-generate a personalised cover letter based on your resume.",       "Cover Letter Generator"),
        (qa3, "🔍 ATS Scan",           "Paste a job description and get your match score instantly.",            "ATS Match Engine"),
    ]
    for col, title, desc, dest in actions:
        col.markdown(f'<div class="zna-card"><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
        if col.button(f"Go to {title.split(' ',1)[1]}", key=f"qa_{dest}", use_container_width=True):
            st.session_state["page"] = dest; st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SMART RESUME BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def page_resume():
    st.markdown("# 📄 Smart Resume Builder")
    tab1, tab2 = st.tabs(["⚙️  1. Setup & Data Input", "🤖  2. AI Output & Export"])

    # ── TAB 1 ──────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("## ⚙️ Template Settings")
        styles = ["Standard Corporate","Creative Modern","Minimalist Clean"]
        style = st.selectbox("Select Professional Template Style", styles,
                             index=styles.index(st.session_state["template_style"]))
        st.session_state["template_style"] = style

        st.markdown("---")
        st.markdown("## 📋 Choose Data Input Method")
        mode = st.radio("How do you want to provide your details?",
                        ["⚡  Auto-Parse (Paste LinkedIn / Resume Data)",
                         "🖊️  Manual Entry (Fill Structured Form)"],
                        horizontal=True)

        # ── AUTO-PARSE ──────────────────────────────────────────────────
        if "Auto-Parse" in mode:
            st.markdown(
                '<div class="alert-info">💡 <b>Fast-Import:</b> Paste your entire LinkedIn profile or old resume. Gemini extracts and organises everything automatically.</div>',
                unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                name      = st.text_input("Full Name *",          placeholder="e.g. Syed Zaid Karim")
                email     = st.text_input("Email (for PDF)")
                github    = st.text_input("GitHub URL (for PDF)")
            with c2:
                job_title = st.text_input("Target Job Title *",   placeholder="e.g. Software Engineer")
                phone     = st.text_input("Phone (for PDF)")
                linkedin  = st.text_input("LinkedIn URL (for PDF)")

            raw = st.text_area("Raw Experience / Education / LinkedIn Data *",
                               placeholder="Paste your raw text here…", height=180)

            if st.button("✨  Auto Generate AI Resume", type="primary"):
                if not name or not job_title or not raw:
                    st.markdown('<div class="alert-error">⚠️ Full Name, Target Job Title, and Raw Data are required.</div>',
                                unsafe_allow_html=True)
                else:
                    with st.spinner("🤖 Parsing data with Gemini…"):
                        try:
                            blob = (f"Name:{name}\nEmail:{email}\nPhone:{phone}\n"
                                    f"LinkedIn:{linkedin}\nGitHub:{github}\nTarget Job:{job_title}\n\nRaw:\n{raw}")
                            raw_json = call_gemini(blob, system=PARSE_SYS)
                            raw_json = re.sub(r"```json|```", "", raw_json).strip()
                            rdata = json.loads(raw_json)
                            for fld, val in [("name",name),("email",email),("phone",phone),
                                             ("linkedin",linkedin),("github",github),("target_job",job_title)]:
                                if val: rdata[fld] = val
                            st.session_state["resume_data"] = rdata
                            add_log("system", f"Resume parsed for {name}.")
                        except json.JSONDecodeError:
                            st.markdown('<div class="alert-error">⚠️ JSON parse error — try rephrasing raw data.</div>',
                                        unsafe_allow_html=True); st.stop()
                        except Exception as e:
                            st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True); st.stop()

                    with st.spinner("✍️ Generating ATS-optimised resume…"):
                        try:
                            r = st.session_state["resume_data"]
                            prompt = (f"Name:{r.get('name','')}\nEmail:{r.get('email','')}\n"
                                      f"Phone:{r.get('phone','')}\nLinkedIn:{r.get('linkedin','')}\n"
                                      f"GitHub:{r.get('github','')}\nTarget Job:{r.get('target_job','')}\n"
                                      f"Template:{style}\n\nParsed Data:\n{json.dumps(r,indent=2)}\n\nGenerate full resume.")
                            md = call_gemini(prompt, system=RESUME_SYS)
                            st.session_state["generated_resume_text"] = md
                            add_log("module", f"Resume generated. Template: {style}.")
                            st.markdown('<div class="alert-success">✅ Resume generated! Switch to Tab 2 to view and export.</div>',
                                        unsafe_allow_html=True)
                        except Exception as e:
                            st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

        # ── MANUAL FORM ─────────────────────────────────────────────────
        else:
            st.markdown("### 👤 Personal Information")
            c1, c2 = st.columns(2)
            with c1:
                mn = st.text_input("Full Name *",          key="mn")
                me = st.text_input("Email",                key="me")
                mg = st.text_input("GitHub URL",           key="mg")
            with c2:
                mj = st.text_input("Target Job Title *",   key="mj")
                mp = st.text_input("Phone Number",         key="mp")
                ml = st.text_input("LinkedIn URL",         key="ml")
            st.markdown("### 📝 Professional Summary")
            ms = st.text_area("Summary", placeholder="Brief professional summary…", height=90, key="ms")
            st.markdown("### 💼 Work Experience")
            mx = st.text_area("Experience (title, company, dates, key achievements)",
                              placeholder="Software Engineer, Acme, 2022–Present\n• Led team of 5…",
                              height=150, key="mx")
            st.markdown("### 🎓 Education")
            med = st.text_area("Education", placeholder="B.Tech CS, XYZ University, 2020", height=75, key="med")
            c1, c2 = st.columns(2)
            with c1: msk = st.text_area("Skills (comma-separated)", height=70, key="msk")
            with c2: mce = st.text_area("Certifications",           height=70, key="mce")
            mpr = st.text_area("Projects", placeholder="Project Name – Brief description", height=90, key="mpr")

            if st.button("✨  Generate AI Resume from Form", type="primary"):
                if not mn or not mj:
                    st.markdown('<div class="alert-error">⚠️ Full Name and Target Job Title are required.</div>',
                                unsafe_allow_html=True)
                else:
                    st.session_state["resume_data"] = {
                        "name":mn,"email":me,"phone":mp,"linkedin":ml,"github":mg,
                        "target_job":mj,"summary":ms,"experience_raw":mx,
                        "education_raw":med,"skills_raw":msk,"certifications":mce,"projects_raw":mpr}
                    with st.spinner("✍️ Generating resume…"):
                        try:
                            prompt = (f"Name:{mn}|Email:{me}|Phone:{mp}|LinkedIn:{ml}|GitHub:{mg}\n"
                                      f"Target Job:{mj}\nTemplate:{style}\nSummary:{ms}\n"
                                      f"Experience:{mx}\nEducation:{med}\nSkills:{msk}\n"
                                      f"Certifications:{mce}\nProjects:{mpr}\n\nGenerate full resume.")
                            md = call_gemini(prompt, system=RESUME_SYS)
                            st.session_state["generated_resume_text"] = md
                            add_log("module", f"Manual resume generated for {mn}.")
                            st.markdown('<div class="alert-success">✅ Resume generated! Switch to Tab 2.</div>',
                                        unsafe_allow_html=True)
                        except Exception as e:
                            st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

    # ── TAB 2 ──────────────────────────────────────────────────────────────
    with tab2:
        txt = st.session_state.get("generated_resume_text","")
        if not txt:
            st.markdown('<div class="alert-warning">⚠️ No resume generated yet. Complete Step 1 first.</div>',
                        unsafe_allow_html=True)
            return

        st.markdown("## ✅ Your AI-Generated Resume")
        st.markdown('<div class="zna-card">', unsafe_allow_html=True)
        st.markdown(txt)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("⬇️ Download Markdown", data=txt,
                               file_name="resume.md", mime="text/markdown", use_container_width=True)
        with c2:
            try:
                st.download_button("⬇️ Download PDF", data=make_pdf(txt,"Resume"),
                                   file_name="resume.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.warning(f"PDF unavailable: {e}")
        with c3:
            if st.button("♻️ Regenerate", use_container_width=True):
                st.session_state["generated_resume_text"] = ""; st.rerun()

        st.markdown("---")
        st.markdown("### ✏️ Edit Resume")
        edited = st.text_area("Edit directly:", value=txt, height=350)
        if st.button("💾 Save Edits"):
            st.session_state["generated_resume_text"] = edited
            add_log("module", "Resume manually edited.")
            st.markdown('<div class="alert-success">✅ Saved.</div>', unsafe_allow_html=True)
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: COVER LETTER
# ─────────────────────────────────────────────────────────────────────────────
def page_cover():
    st.markdown("# ✉️ Auto-Cover Letter")
    st.caption("Generate a highly personalised cover letter from your current resume.")

    if not st.session_state.get("resume_data"):
        st.markdown(
            '<div class="alert-error">⚠️ No resume found in memory! Build your resume in '
            '<b>Smart Resume Builder</b> first.</div>', unsafe_allow_html=True)
        if st.button("→ Go to Resume Builder"):
            st.session_state["page"] = "Smart Resume Builder"; st.rerun()
        return

    r = st.session_state["resume_data"]
    st.markdown(
        f'<div class="alert-success">✅ Resume loaded — <b>{r.get("name","Unknown")}</b> · '
        f'Target: <b>{r.get("target_job","N/A")}</b></div>', unsafe_allow_html=True)

    st.markdown("### 🎯 Job Details")
    c1, c2 = st.columns(2)
    with c1:
        company = st.text_input("Company Name *", placeholder="e.g. Google")
        manager = st.text_input("Hiring Manager (optional)", placeholder="e.g. Ms. Priya Sharma")
    with c2:
        job_ttl = st.text_input("Exact Job Title *", placeholder="e.g. Software Engineer L4")
        tone    = st.selectbox("Tone", ["Professional","Enthusiastic","Confident","Concise"])

    jd = st.text_area("Paste Job Description (recommended for best results)",
                      placeholder="Paste the full job description…", height=140)

    if st.button("✨  Generate Cover Letter", type="primary"):
        if not company or not job_ttl:
            st.markdown('<div class="alert-error">⚠️ Company Name and Job Title are required.</div>',
                        unsafe_allow_html=True)
        else:
            with st.spinner("✍️ Writing personalised cover letter…"):
                try:
                    prompt = (f"Resume:\n{json.dumps(r,indent=2)}\n\n"
                              f"Job Title:{job_ttl}\nCompany:{company}\n"
                              f"Hiring Manager:{manager or 'Hiring Manager'}\n"
                              f"Tone:{tone}\nJob Description:{jd or 'Not provided'}\n\nWrite cover letter.")
                    cl = call_gemini(prompt, system=COVER_SYS)
                    st.session_state["cover_letter"] = cl
                    add_log("module", f"Cover letter generated for {company}.")
                except Exception as e:
                    st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

    if st.session_state.get("cover_letter"):
        st.markdown("---")
        st.markdown("## ✅ Your Cover Letter")
        st.markdown('<div class="zna-card">', unsafe_allow_html=True)
        st.markdown(st.session_state["cover_letter"])
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("⬇️ Download Text", data=st.session_state["cover_letter"],
                               file_name="cover_letter.txt", mime="text/plain", use_container_width=True)
        with c2:
            try:
                st.download_button("⬇️ Download PDF", data=make_pdf(st.session_state["cover_letter"],"Cover Letter"),
                                   file_name="cover_letter.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.warning(f"PDF unavailable: {e}")
        with c3:
            if st.button("♻️ Regenerate", use_container_width=True):
                st.session_state["cover_letter"] = ""; st.rerun()

        st.markdown("---")
        st.markdown("### ✏️ Edit Cover Letter")
        ecl = st.text_area("Edit directly:", value=st.session_state["cover_letter"], height=250)
        if st.button("💾 Save Edits", key="save_cl"):
            st.session_state["cover_letter"] = ecl
            add_log("module", "Cover letter manually edited.")
            st.markdown('<div class="alert-success">✅ Saved.</div>', unsafe_allow_html=True)
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ATS MATCH ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def page_ats():
    p = P()
    dark = st.session_state["dark_mode"]
    st.markdown("# 🔍 ATS Match Engine")
    st.caption("Semantic NLP-powered Applicant Tracking System analyser.")

    resume_txt = st.session_state.get("generated_resume_text","")
    if not resume_txt and st.session_state.get("resume_data"):
        resume_txt = json.dumps(st.session_state["resume_data"], indent=2)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📄 Resume")
        if resume_txt:
            st.markdown('<div class="alert-success">✅ Resume loaded from memory.</div>', unsafe_allow_html=True)
            r_override = st.text_area("Override / Edit Resume Text:", value=resume_txt, height=220)
        else:
            st.markdown('<div class="alert-warning">⚠️ No resume in memory. Paste manually.</div>', unsafe_allow_html=True)
            r_override = st.text_area("Paste Resume Text:", height=220, placeholder="Paste your resume…")
    with c2:
        st.markdown("### 💼 Job Description")
        jd_ats = st.text_area("Paste the full Job Description *",
                              height=220, placeholder="Paste the complete job description…")

    if st.button("🔍  Run ATS Analysis", type="primary"):
        final_r = r_override.strip() or resume_txt
        if not final_r:
            st.markdown('<div class="alert-error">⚠️ Resume text required.</div>', unsafe_allow_html=True)
        elif not jd_ats.strip():
            st.markdown('<div class="alert-error">⚠️ Job Description required.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("🤖 Running semantic ATS analysis…"):
                try:
                    raw = call_gemini(f"RESUME:\n{final_r}\n\nJOB DESCRIPTION:\n{jd_ats}\n\nAnalyse.", system=ATS_SYS)
                    raw = re.sub(r"```json|```", "", raw).strip()
                    result = json.loads(raw)
                    st.session_state["ats_result"] = result
                    score = result.get("score", 0)
                    hist  = st.session_state["ats_history"]
                    hist.append(score)
                    st.session_state["ats_history"] = hist[-7:]
                    add_log("system", f"ATS analysis complete. Score: {score}/100.")
                except json.JSONDecodeError:
                    st.markdown('<div class="alert-error">⚠️ Could not parse ATS JSON. Try again.</div>',
                                unsafe_allow_html=True)
                    add_log("memory", "ATS JSON parse error.")
                except Exception as e:
                    st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

    result = st.session_state.get("ats_result")
    if not result:
        return

    st.markdown("---")
    score = result.get("score", 0)
    color = "#00d68f" if score >= 75 else "#f5c842" if score >= 50 else "#ff6b6b"

    st.markdown(f"""
<div class="zna-card" style="text-align:center;padding:36px">
  <div style="font-size:80px;font-weight:900;color:{color};letter-spacing:-0.04em;
              font-family:'Syne',sans-serif;line-height:1">{score}<span style="font-size:36px">%</span></div>
  <div style="font-size:15px;color:{p['muted']};margin-top:6px;font-weight:500">ATS Match Score</div>
</div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("### ✅ Matched")
        for kw in result.get("matched_keywords",[]):
            st.markdown(f'<span class="chip-green">{kw}</span>', unsafe_allow_html=True)
    with c2:
        st.markdown("### ❌ Missing")
        for kw in result.get("missing_keywords",[]):
            st.markdown(f'<span class="chip-red">{kw}</span>', unsafe_allow_html=True)
    with c3:
        st.markdown("### 💪 Strengths")
        for s in result.get("strengths",[]): st.markdown(f"• {s}")
    with c4:
        st.markdown("### 🔧 Improvements")
        for i in result.get("improvements",[]): st.markdown(f"• {i}")

    st.markdown("---")
    st.markdown("### 🪄 One-Click Resume Tailoring")
    st.caption("Rewrite your resume to close keyword gaps automatically.")
    if st.button("✨  Tailor Resume to This Job", type="primary"):
        base = st.session_state.get("generated_resume_text","") or resume_txt
        if not base:
            st.markdown('<div class="alert-error">⚠️ No resume in memory to tailor.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("🤖 Tailoring resume…"):
                try:
                    missing = ", ".join(result.get("missing_keywords",[]))
                    tp = (f"Resume:\n{base}\n\nJob Description:\n{jd_ats}\n\n"
                          f"Missing keywords to add naturally: {missing}\n\n"
                          f"Rewrite for higher ATS match. Keep it truthful.")
                    tailored = call_gemini(tp, system=RESUME_SYS)
                    st.session_state["generated_resume_text"] = tailored
                    add_log("module", "Resume tailored to job description.")
                    st.markdown('<div class="alert-success">✅ Resume tailored! View in Resume Builder → Tab 2.</div>',
                                unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

    report = (f"ATS ANALYSIS REPORT\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
              f"SCORE: {score}/100\n\nMATCHED KEYWORDS:\n"
              + "\n".join(f"• {k}" for k in result.get("matched_keywords",[]))
              + "\n\nMISSING KEYWORDS:\n"
              + "\n".join(f"• {k}" for k in result.get("missing_keywords",[]))
              + "\n\nSTRENGTHS:\n"
              + "\n".join(f"• {s}" for s in result.get("strengths",[]))
              + "\n\nIMPROVEMENTS:\n"
              + "\n".join(f"• {i}" for i in result.get("improvements",[])))
    st.download_button("⬇️ Download ATS Report", data=report,
                       file_name="ats_report.txt", mime="text/plain")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main():
    inject_css()
    sidebar()
    page = st.session_state["page"]
    if   page == "Overview Dashboard":     page_overview()
    elif page == "Smart Resume Builder":   page_resume()
    elif page == "Cover Letter Generator": page_cover()
    elif page == "ATS Match Engine":       page_ats()

if __name__ == "__main__":
    main()
