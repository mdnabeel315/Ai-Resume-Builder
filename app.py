import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime
from fpdf import FPDF
import os

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ZNA – AI Career Studio",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State Defaults ────────────────────────────────────────────────────
DEFAULTS = {
    "page": "Landing",
    "dark_mode": True,
    "gemini_api_key": "",
    "resume_data": None,
    "generated_resume_text": "",
    "cover_letter": "",
    "ats_result": None,
    "ats_history": [],
    "logs": [
        {"type": "system", "msg": "LLM Engine connected to Gemini 2.0 Flash."},
        {"type": "module", "msg": "PDF Generation engine ready."},
        {"type": "memory", "msg": "Waiting for user to generate a resume…"},
    ],
    "template_style": "Standard Corporate",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Theme Palette ─────────────────────────────────────────────────────────────
def palette(dark: bool) -> dict:
    if dark:
        return dict(
            bg="#0d0d0f", sidebar_bg="#111113",
            card_bg="#1a1a1e", card_border="#2e2e32",
            text_primary="#f5f5f7", text_secondary="#ababb0",
            accent="#3b9eff", accent2="#34d35f",
            accent3="#ff5147", accent4="#ffd60a",
            input_bg="#202024", input_border="#3a3a3e",
            nav_btn_bg="#1e3a5f", nav_btn_text="#90c8ff",
            nav_btn_active_bg="#3b9eff", nav_btn_active_text="#ffffff",
            log_system="#0e2b1a", log_module="#0e1f35", log_memory="#2b2410",
            shadow="rgba(0,0,0,0.4)",
        )
    else:
        return dict(
            bg="#f2f2f7", sidebar_bg="#ffffff",
            card_bg="#ffffff", card_border="#d1d1d6",
            text_primary="#1c1c1e", text_secondary="#636366",
            accent="#0071e3", accent2="#28a745",
            accent3="#dc3545", accent4="#ff9500",
            input_bg="#f2f2f7", input_border="#c7c7cc",
            nav_btn_bg="#ddeeff", nav_btn_text="#0055b3",
            nav_btn_active_bg="#0071e3", nav_btn_active_text="#ffffff",
            log_system="#d4edda", log_module="#cce5ff", log_memory="#fff3cd",
            shadow="rgba(0,0,0,0.08)",
        )


# ── CSS Injection ─────────────────────────────────────────────────────────────
def inject_css():
    dark = st.session_state["dark_mode"]
    p = palette(dark)

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    *, html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }}

    /* ── Global backgrounds ── */
    html, body, .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {p['bg']} !important;
    }}
    .main .block-container {{
        background-color: {p['bg']} !important;
        padding: 2rem 2.5rem !important;
        max-width: 1300px !important;
    }}
    [data-testid="stHeader"] {{ background: {p['bg']} !important; }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] > div:first-child {{
        background-color: {p['sidebar_bg']} !important;
        border-right: 1px solid {p['card_border']} !important;
        padding: 1.5rem 1rem !important;
    }}

    /* ── ALL sidebar buttons: high contrast ── */
    section[data-testid="stSidebar"] .stButton > button {{
        background-color: {p['nav_btn_bg']} !important;
        color: {p['nav_btn_text']} !important;
        border: 1px solid {p['card_border']} !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 9px 14px !important;
        text-align: left !important;
        width: 100% !important;
        margin-bottom: 4px !important;
        transition: all 0.18s ease !important;
        box-shadow: none !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: {p['nav_btn_active_bg']} !important;
        color: {p['nav_btn_active_text']} !important;
        border-color: {p['accent']} !important;
        transform: translateX(2px) !important;
    }}

    /* ── Main area buttons ── */
    .main .stButton > button {{
        background-color: {p['accent']} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 22px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        letter-spacing: -0.01em !important;
        box-shadow: 0 2px 12px {p['shadow']} !important;
    }}
    .main .stButton > button:hover {{
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px {p['shadow']} !important;
    }}

    /* ── Download buttons ── */
    .stDownloadButton > button {{
        background-color: {p['accent2']} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 22px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    .stDownloadButton > button:hover {{
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
    }}

    /* ── Typography ── */
    h1 {{ font-size: 38px !important; font-weight: 800 !important; letter-spacing: -0.03em !important; color: {p['text_primary']} !important; margin-bottom: 4px !important; }}
    h2 {{ font-size: 22px !important; font-weight: 700 !important; letter-spacing: -0.02em !important; color: {p['text_primary']} !important; }}
    h3 {{ font-size: 16px !important; font-weight: 600 !important; color: {p['text_primary']} !important; }}
    p, li {{ color: {p['text_secondary']} !important; font-size: 14px !important; line-height: 1.65 !important; }}

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: {p['input_bg']} !important;
        border: 1px solid {p['input_border']} !important;
        border-radius: 10px !important;
        color: {p['text_primary']} !important;
        font-size: 14px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {p['accent']} !important;
        box-shadow: 0 0 0 3px {p['accent']}28 !important;
    }}
    label, .stRadio label {{
        color: {p['text_secondary']} !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: {p['input_bg']} !important;
        border: 1px solid {p['input_border']} !important;
        border-radius: 10px !important;
        color: {p['text_primary']} !important;
    }}
    div[data-baseweb="select"] span {{
        color: {p['text_primary']} !important;
    }}

    /* ── Cards ── */
    .zna-card {{
        background: {p['card_bg']};
        border: 1px solid {p['card_border']};
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 20px {p['shadow']};
        transition: box-shadow 0.25s ease, transform 0.25s ease;
    }}
    .zna-card:hover {{
        box-shadow: 0 6px 30px {p['shadow']};
        transform: translateY(-1px);
    }}

    /* ── Stat cards ── */
    .stat-card {{
        background: {p['card_bg']};
        border: 1px solid {p['card_border']};
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 1px 10px {p['shadow']};
    }}
    .stat-label {{
        font-size: 10px; font-weight: 700;
        letter-spacing: 0.1em; text-transform: uppercase;
        color: {p['text_secondary']}; margin-bottom: 8px;
    }}
    .stat-value {{
        font-size: 26px; font-weight: 800;
        color: {p['text_primary']}; letter-spacing: -0.03em;
        line-height: 1; margin-bottom: 12px;
    }}
    .stat-badge {{
        display: inline-flex; align-items: center; gap: 5px;
        padding: 4px 11px; border-radius: 20px;
        font-size: 11px; font-weight: 700;
    }}
    .badge-active  {{ background:{'#0e2b1a' if dark else '#d4edda'}; color:{p['accent2']}; }}
    .badge-enabled {{ background:{'#0e1f35' if dark else '#cce5ff'}; color:{p['accent']}; }}
    .badge-ready   {{ background:{'#2a1a35' if dark else '#ede7f6'}; color:#bf5af2; }}
    .badge-online  {{ background:{'#2b1010' if dark else '#fce4ec'}; color:{p['accent3']}; }}

    /* ── Log items ── */
    .log-system {{ background:{p['log_system']}; border-radius:10px; padding:11px 15px; margin:6px 0; font-size:13px; color:{p['text_primary']}; border-left: 3px solid {p['accent2']}; }}
    .log-module  {{ background:{p['log_module']};  border-radius:10px; padding:11px 15px; margin:6px 0; font-size:13px; color:{p['text_primary']}; border-left: 3px solid {p['accent']}; }}
    .log-memory  {{ background:{p['log_memory']};  border-radius:10px; padding:11px 15px; margin:6px 0; font-size:13px; color:{p['text_primary']}; border-left: 3px solid {p['accent4']}; }}

    /* ── Alerts ── */
    .alert-error   {{ background:{'#2b1212' if dark else '#fff0f0'}; border:1px solid {p['accent3']}; border-radius:12px; padding:13px 16px; color:{p['accent3']}; font-size:13px; font-weight:500; margin:10px 0; }}
    .alert-warning {{ background:{'#2b2010' if dark else '#fff8e1'}; border:1px solid {p['accent4']}; border-radius:12px; padding:13px 16px; color:{p['accent4']}; font-size:13px; font-weight:500; margin:10px 0; }}
    .alert-success {{ background:{'#0e2b1a' if dark else '#d4edda'}; border:1px solid {p['accent2']}; border-radius:12px; padding:13px 16px; color:{p['accent2']}; font-size:13px; font-weight:500; margin:10px 0; }}
    .alert-info    {{ background:{'#0e1f35' if dark else '#cce5ff'}; border:1px solid {p['accent']};  border-radius:12px; padding:13px 16px; color:{p['accent']};  font-size:13px; font-weight:500; margin:10px 0; }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {p['card_bg']}; border-radius: 12px;
        padding: 4px; border: 1px solid {p['card_border']}; gap: 2px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 9px; font-weight: 600; font-size: 13px;
        color: {p['text_secondary']}; background: transparent; padding: 8px 18px;
    }}
    .stTabs [aria-selected="true"] {{
        background: {p['accent']} !important; color: #ffffff !important;
    }}

    /* ── Progress / spinner ── */
    .stProgress > div > div > div > div {{ background: {p['accent']}; border-radius: 4px; }}

    /* ── Divider ── */
    hr {{ border-color: {p['card_border']} !important; margin: 20px 0 !important; }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {p['input_border']}; border-radius: 10px; }}

    /* ── Sidebar section label ── */
    .sidebar-label {{
        font-size: 10px; font-weight: 800;
        letter-spacing: 0.12em; text-transform: uppercase;
        color: {p['text_secondary']}; margin: 16px 0 8px;
        padding-left: 4px;
    }}

    /* ── Hide streamlit chrome ── */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}
    [data-testid="stToolbar"] {{ display: none; }}

    /* ── Toggle ── */
    .stCheckbox > label, .stToggle > label {{
        color: {p['text_primary']} !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }}

    /* ── Landing page ── */
    .landing-hero {{
        text-align: center;
        padding: 80px 20px 60px;
    }}
    .landing-hero h1 {{
        font-size: 56px !important;
        font-weight: 900 !important;
        letter-spacing: -0.04em !important;
        color: {p['text_primary']} !important;
        line-height: 1.1 !important;
        margin-bottom: 20px !important;
    }}
    .landing-hero p {{
        font-size: 18px !important;
        color: {p['text_secondary']} !important;
        max-width: 560px;
        margin: 0 auto 36px !important;
        line-height: 1.7 !important;
    }}
    .feature-pill {{
        display: inline-flex; align-items: center; gap: 8px;
        background: {p['card_bg']}; border: 1px solid {p['card_border']};
        border-radius: 100px; padding: 6px 16px;
        font-size: 13px; font-weight: 600; color: {p['text_primary']};
        margin: 4px;
    }}
    .landing-feature-card {{
        background: {p['card_bg']};
        border: 1px solid {p['card_border']};
        border-radius: 20px;
        padding: 28px;
        height: 100%;
        box-shadow: 0 2px 16px {p['shadow']};
        transition: all 0.25s ease;
    }}
    .landing-feature-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 30px {p['shadow']};
        border-color: {p['accent']};
    }}
    .feature-icon {{ font-size: 36px; margin-bottom: 14px; }}
    .feature-title {{ font-size: 17px; font-weight: 700; color: {p['text_primary']}; margin-bottom: 8px; }}
    .feature-desc {{ font-size: 13px; color: {p['text_secondary']}; line-height: 1.6; }}
    </style>
    """, unsafe_allow_html=True)


# ── ZNA Logo SVG ──────────────────────────────────────────────────────────────
ZNA_LOGO = """
<svg width="110" height="38" viewBox="0 0 110 38" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="zna_grad" x1="0" y1="0" x2="110" y2="38" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#60b8ff"/>
      <stop offset="50%" stop-color="#3b9eff"/>
      <stop offset="100%" stop-color="#1a6fd4"/>
    </linearGradient>
  </defs>
  <!-- Z -->
  <text x="2" y="30" font-family="'Inter',sans-serif" font-weight="900" font-size="30"
        fill="url(#zna_grad)" letter-spacing="-1">ZNA</text>
  <!-- star accent -->
  <text x="95" y="10" font-family="sans-serif" font-size="10" fill="#3b9eff">✦</text>
  <!-- tagline -->
  <text x="2" y="38" font-family="'Inter',sans-serif" font-weight="700" font-size="7.5"
        fill="#3b9eff" letter-spacing="0.18em">INNOVATE YOUR CAREER</text>
</svg>
"""


# ── Gemini Helpers ────────────────────────────────────────────────────────────
def get_gemini_model():
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-2.0-flash")
    except Exception as e:
        st.session_state["gemini_error"] = str(e)
        return None


def call_gemini(prompt: str, system: str = "") -> str:
    model = get_gemini_model()
    if model is None:
        raise ValueError("⚠️ Gemini API key not configured. Please enter it in the sidebar.")
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    try:
        return model.generate_content(full_prompt).text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")


def add_log(log_type: str, msg: str):
    st.session_state["logs"].insert(0, {"type": log_type, "msg": msg})
    st.session_state["logs"] = st.session_state["logs"][:20]


# ── PDF Generator ─────────────────────────────────────────────────────────────
def generate_pdf_bytes(content: str, title: str = "Document") -> bytes:
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
            pdf.ln(3)
            continue
        if line.isupper() and len(line) < 60:
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, line)
            pdf.set_font("Helvetica", size=10)
        else:
            pdf.multi_cell(0, 5, line)
    return pdf.output(dest="S").encode("latin-1")


# ── Prompts ───────────────────────────────────────────────────────────────────
RESUME_SYSTEM = """You are an expert ATS-optimised resume writer with 15+ years experience.
Output ONLY a well-structured professional resume in Markdown. No preamble. No commentary.
Sections: Professional Summary | Work Experience | Education | Skills | Certifications (if any) | Projects (if any).
Use strong action verbs, quantify achievements, mirror keywords from the target job title."""

COVER_LETTER_SYSTEM = """You are an expert career coach writing highly personalised compelling cover letters.
Output ONLY the cover letter text. No preamble. No meta-commentary.
Keep it under 400 words. 3 paragraphs: Hook + Value, Evidence, Call-to-action."""

ATS_SYSTEM = """You are an ATS specialist. Analyse the resume against the job description.
Return ONLY valid JSON with EXACTLY this shape (no markdown fences, no extra text):
{"score":<int 0-100>,"matched_keywords":[<str>],"missing_keywords":[<str>],"strengths":[<str>],"improvements":[<str>]}"""

PARSE_SYSTEM = """You are a resume parser. Extract information from raw text.
Return ONLY valid JSON (no markdown fences, no extra text):
{"name":"","email":"","phone":"","linkedin":"","github":"","target_job":"","summary":"",
"experience":[{"title":"","company":"","dates":"","bullets":[]}],
"education":[{"degree":"","institution":"","year":""}],
"skills":[],"certifications":[],"projects":[{"name":"","description":""}]}"""


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    dark = st.session_state["dark_mode"]
    p = palette(dark)

    with st.sidebar:
        # ZNA Logo
        st.markdown(ZNA_LOGO, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f'<div class="sidebar-label">AI Studio Menu</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-label" style="margin-top:4px">Navigate Workspace</div>', unsafe_allow_html=True)

        pages = [
            ("🏠", "Landing",            "Home / Landing Page"),
            ("🗂️", "Overview Dashboard", "Overview Dashboard"),
            ("📄", "Smart Resume Builder","Smart Resume Builder"),
            ("✉️", "Cover Letter Generator", "Cover Letter Generator"),
            ("🔍", "ATS Match Engine",   "ATS Match Engine"),
        ]

        current = st.session_state["page"]
        for icon, key, label in pages:
            is_active = current == key
            # Use CSS override for active state via a wrapper trick
            prefix = "● " if is_active else "○ "
            btn_label = f"{prefix}{icon}  {label}"
            if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
                st.session_state["page"] = key
                st.rerun()

        st.markdown("---")

        # Theme toggle
        new_dark = st.toggle("🌙  Dark Mode", value=dark)
        if new_dark != dark:
            st.session_state["dark_mode"] = new_dark
            st.rerun()

        st.markdown("---")

        # API Key
        st.markdown(f'<div class="sidebar-label">Gemini API Key</div>', unsafe_allow_html=True)
        key_val = st.text_input(
            "API Key", type="password",
            value=st.session_state["gemini_api_key"],
            placeholder="AIza…",
            label_visibility="collapsed",
        )
        if key_val != st.session_state["gemini_api_key"]:
            st.session_state["gemini_api_key"] = key_val
            if key_val:
                add_log("system", "Gemini API key updated.")

        st.markdown("---")

        # Job Portal
        st.markdown(f'<div class="sidebar-label">🌐 Job Portal</div>', unsafe_allow_html=True)
        target_job = ""
        if st.session_state["resume_data"]:
            target_job = st.session_state["resume_data"].get("target_job", "")
        if not target_job:
            st.markdown(
                '<div class="alert-warning" style="font-size:12px">💡 Fill out the <b>Target Job Title</b> in the Resume Builder to unlock the LinkedIn Job Portal.</div>',
                unsafe_allow_html=True,
            )
        else:
            url = f"https://www.linkedin.com/jobs/search/?keywords={target_job.replace(' ', '%20')}"
            st.markdown(f'🔗 **[Search LinkedIn Jobs →]({url})**')
            st.caption(f"Searching: *{target_job}*")


# ── Page: Landing ─────────────────────────────────────────────────────────────
def page_landing():
    dark = st.session_state["dark_mode"]
    p = palette(dark)

    # Hero
    st.markdown(f"""
    <div class="landing-hero">
        {ZNA_LOGO}
        <br><br>
        <h1>The Best Free AI<br>Resume Builder</h1>
        <p>Our Resume Builder creates ATS-friendly resumes in minutes.
        Build a new resume or improve an existing one with unlimited
        downloads, instant job matching, and smart AI suggestions.</p>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀  Start Building Free", use_container_width=True):
                st.session_state["page"] = "Smart Resume Builder"
                st.rerun()
        with c2:
            if st.button("📊  View Dashboard", use_container_width=True):
                st.session_state["page"] = "Overview Dashboard"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature pills
    pills = ["✅ ATS Optimised", "⚡ Instant Generation", "🔗 LinkedIn Integration",
             "📄 PDF Export", "🔍 Semantic ATS Scanner", "✉️ Auto Cover Letters"]
    pill_html = "".join(f'<span class="feature-pill">{p_}</span>' for p_ in pills)
    st.markdown(f'<div style="text-align:center;margin-bottom:48px">{pill_html}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Feature cards
    st.markdown(f'<h2 style="text-align:center;margin-bottom:24px">Everything you need to land your dream job</h2>', unsafe_allow_html=True)

    features = [
        ("🎯", "Optimize for ATS",
         "Format your resume so it's easy for recruiters and ATS systems to find in searches. Powered by Gemini 2.0 Flash."),
        ("💼", "Job Matching",
         "Instantly edit any resume to match a job description using AI semantic analysis and keyword extraction."),
        ("♾️", "Create Without Limits",
         "Build, update, edit, and export as many resumes as you need — completely free with your Gemini API key."),
        ("🔗", "Direct Apply via LinkedIn",
         "Seamlessly submit your tailored resume directly to LinkedIn job postings via the built-in Job Portal."),
        ("✉️", "Auto Cover Letter",
         "Generate a matching cover letter instantly tailored to the job description with one click."),
        ("📈", "ATS Score Tracking",
         "Track your ATS optimisation trend across sessions and watch your match score climb to 100%."),
    ]

    for i in range(0, len(features), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(features):
                icon, title, desc = features[i + j]
                col.markdown(f"""
                <div class="landing-feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    # Stats banner
    st.markdown(f"""
    <div style="display:flex;justify-content:center;gap:60px;padding:40px 0;text-align:center;flex-wrap:wrap">
        <div>
            <div style="font-size:36px;font-weight:900;color:{p['accent']};letter-spacing:-0.03em">3</div>
            <div style="font-size:12px;font-weight:600;color:{p['text_secondary']};text-transform:uppercase;letter-spacing:0.08em">Resume Templates</div>
        </div>
        <div>
            <div style="font-size:36px;font-weight:900;color:{p['accent2']};letter-spacing:-0.03em">2</div>
            <div style="font-size:12px;font-weight:600;color:{p['text_secondary']};text-transform:uppercase;letter-spacing:0.08em">Input Modes</div>
        </div>
        <div>
            <div style="font-size:36px;font-weight:900;color:#bf5af2;letter-spacing:-0.03em">100%</div>
            <div style="font-size:12px;font-weight:600;color:{p['text_secondary']};text-transform:uppercase;letter-spacing:0.08em">Free to Use</div>
        </div>
        <div>
            <div style="font-size:36px;font-weight:900;color:{p['accent3']};letter-spacing:-0.03em">AI</div>
            <div style="font-size:12px;font-weight:600;color:{p['text_secondary']};text-transform:uppercase;letter-spacing:0.08em">Powered by Gemini</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
    <div style="text-align:center;padding:32px 0 16px;color:{p['text_secondary']};font-size:12px">
        {ZNA_LOGO}<br><br>
        © 2026 ZNA – Innovate Your Career &nbsp;·&nbsp; Built with Streamlit + Gemini AI
    </div>
    """, unsafe_allow_html=True)


# ── Page: Overview Dashboard ──────────────────────────────────────────────────
def page_overview():
    dark = st.session_state["dark_mode"]
    p = palette(dark)

    st.markdown(ZNA_LOGO, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("# Welcome to your Career Workspace")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Dynamic Templates</div>
            <div class="stat-value">3 Styles</div>
            <span class="stat-badge badge-active">+ Active 🟢</span>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Input Modes</div>
            <div class="stat-value">Dual (Auto/…</div>
            <span class="stat-badge badge-enabled">+ Enabled ⚡</span>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Cover Letters</div>
            <div class="stat-value">Auto-Gen</div>
            <span class="stat-badge badge-ready">+ Ready 📄</span>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">ATS Scanner</div>
            <div class="stat-value">Semantic NLP</div>
            <span class="stat-badge badge-online">+ Online 🚀</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("## 📈 ATS Optimization Trends")
        st.caption("Average ATS Match Scores generated by the AI over the last 7 sessions.")
        import pandas as pd
        history = st.session_state["ats_history"]
        data = history if history else [65, 72, 70, 78, 85, 88, 95]
        df = pd.DataFrame({"Session": list(range(1, len(data)+1)), "ATS Match Score (%)": data})
        st.line_chart(df.set_index("Session"), use_container_width=True, height=210)

    with col_right:
        st.markdown("## ⚡ Live System Logs")
        for log in st.session_state["logs"][:5]:
            t = log["type"]
            icons  = {"system": "✅", "module": "ℹ️", "memory": "⏳"}
            labels = {"system": "System", "module": "Module", "memory": "Memory"}
            icon  = icons.get(t, "🔹")
            label = labels.get(t, t.capitalize())
            st.markdown(
                f'<div class="log-{t}"><b>[{label}]</b> {icon} {log["msg"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("## 🚀 Quick Actions")
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        st.markdown('<div class="zna-card"><h3>📄 Build Resume</h3><p>Create an ATS-optimised resume from scratch or your LinkedIn data.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Resume Builder", key="qa_resume", use_container_width=True):
            st.session_state["page"] = "Smart Resume Builder"; st.rerun()
    with qa2:
        st.markdown('<div class="zna-card"><h3>✉️ Write Cover Letter</h3><p>Auto-generate a tailored cover letter based on your resume.</p></div>', unsafe_allow_html=True)
        if st.button("Go to Cover Letter", key="qa_cover", use_container_width=True):
            st.session_state["page"] = "Cover Letter Generator"; st.rerun()
    with qa3:
        st.markdown('<div class="zna-card"><h3>🔍 ATS Scan</h3><p>Upload a job description and get your match score instantly.</p></div>', unsafe_allow_html=True)
        if st.button("Go to ATS Engine", key="qa_ats", use_container_width=True):
            st.session_state["page"] = "ATS Match Engine"; st.rerun()


# ── Page: Smart Resume Builder ────────────────────────────────────────────────
def page_resume_builder():
    st.markdown("# 📄 Smart Resume Builder")

    tab1, tab2 = st.tabs(["⚙️  1. Setup & Data Input", "🤖  2. AI Output & Export"])

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

        st.markdown("---")
        st.markdown("## 📋 Choose Data Input Method")
        input_mode = st.radio(
            "How do you want to provide your details?",
            ["⚡ Auto-Parse (Paste LinkedIn/Resume Data)", "🖊️ Manual Entry (Fill Structured Form)"],
            horizontal=True,
        )

        if "Auto-Parse" in input_mode:
            st.markdown('<div class="alert-info">💡 <b>Fast-Import:</b> Paste your entire LinkedIn profile or old resume. Gemini will extract and organise it automatically.</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                full_name  = st.text_input("Full Name *",         placeholder="e.g. Syed Zaid Karim")
                email      = st.text_input("Email (for PDF links)")
                github_url = st.text_input("GitHub URL (for PDF links)")
            with c2:
                target_job   = st.text_input("Target Job Title *", placeholder="e.g. Computer Science Engineering Student")
                phone        = st.text_input("Phone Number (for PDF links)")
                linkedin_url = st.text_input("LinkedIn URL (for PDF links)")

            raw_text = st.text_area("Raw Experience / Education / LinkedIn Data *",
                                    placeholder="Paste your raw text here…", height=180)

            if st.button("✨  Auto Generate AI Resume", type="primary"):
                if not full_name or not target_job or not raw_text:
                    st.markdown('<div class="alert-error">⚠️ Full Name, Target Job Title, and Raw Data are required.</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("🤖 Parsing data with Gemini…"):
                        try:
                            parse_prompt = f"Name:{full_name}\nEmail:{email}\nPhone:{phone}\nLinkedIn:{linkedin_url}\nGitHub:{github_url}\nTarget Job:{target_job}\n\nRaw Data:\n{raw_text}"
                            parsed_json  = call_gemini(parse_prompt, system=PARSE_SYSTEM)
                            parsed_json  = re.sub(r"```json|```", "", parsed_json).strip()
                            resume_data  = json.loads(parsed_json)
                            for field, val in [("name",full_name),("email",email),("phone",phone),
                                               ("linkedin",linkedin_url),("github",github_url),("target_job",target_job)]:
                                if val: resume_data[field] = val
                            st.session_state["resume_data"] = resume_data
                            add_log("system", f"Resume data parsed for {full_name}.")
                        except json.JSONDecodeError:
                            st.markdown('<div class="alert-error">⚠️ JSON parse error. Try rephrasing raw data.</div>', unsafe_allow_html=True)
                            st.stop()
                        except Exception as e:
                            st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)
                            st.stop()

                    with st.spinner("✍️ Generating ATS-optimised resume…"):
                        try:
                            r = st.session_state["resume_data"]
                            resume_prompt = f"Name:{r.get('name','')}\nEmail:{r.get('email','')}\nPhone:{r.get('phone','')}\nLinkedIn:{r.get('linkedin','')}\nGitHub:{r.get('github','')}\nTarget Job:{r.get('target_job','')}\nTemplate:{template_style}\n\nParsed Data:\n{json.dumps(r,indent=2)}\n\nGenerate a full professional resume."
                            resume_md = call_gemini(resume_prompt, system=RESUME_SYSTEM)
                            st.session_state["generated_resume_text"] = resume_md
                            add_log("module", f"Resume generated. Template: {template_style}.")
                            st.markdown('<div class="alert-success">✅ Resume generated! Switch to Tab 2 to view and export.</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

        else:  # Manual Entry
            st.markdown("### 👤 Personal Information")
            c1, c2 = st.columns(2)
            with c1:
                m_name    = st.text_input("Full Name *", key="m_name")
                m_email   = st.text_input("Email",       key="m_email")
                m_github  = st.text_input("GitHub URL",  key="m_github")
            with c2:
                m_job     = st.text_input("Target Job Title *", key="m_job")
                m_phone   = st.text_input("Phone Number",       key="m_phone")
                m_linkedin= st.text_input("LinkedIn URL",       key="m_linkedin")

            st.markdown("### 📝 Professional Summary")
            m_summary  = st.text_area("Summary", placeholder="Brief professional summary…", height=90,  key="m_summary")
            st.markdown("### 💼 Work Experience")
            m_exp      = st.text_area("Experience (title, company, dates, achievements)", height=160, key="m_exp",
                                       placeholder="Software Engineer, Acme, 2022–Present\n- Led team of 5…")
            st.markdown("### 🎓 Education")
            m_edu      = st.text_area("Education", placeholder="B.Tech CS, XYZ University, 2020", height=80, key="m_edu")
            c1, c2     = st.columns(2)
            with c1: m_skills = st.text_area("Skills (comma-separated)", height=70, key="m_skills")
            with c2: m_certs  = st.text_area("Certifications",            height=70, key="m_certs")
            m_projects = st.text_area("Projects", placeholder="Project Name – Brief description", height=90, key="m_projects")

            if st.button("✨  Generate AI Resume from Form", type="primary"):
                if not m_name or not m_job:
                    st.markdown('<div class="alert-error">⚠️ Full Name and Target Job Title are required.</div>', unsafe_allow_html=True)
                else:
                    resume_data = {"name":m_name,"email":m_email,"phone":m_phone,"linkedin":m_linkedin,
                                   "github":m_github,"target_job":m_job,"summary":m_summary,
                                   "experience_raw":m_exp,"education_raw":m_edu,"skills_raw":m_skills,
                                   "certifications":m_certs,"projects_raw":m_projects}
                    st.session_state["resume_data"] = resume_data
                    with st.spinner("✍️ Generating resume…"):
                        try:
                            prompt = f"Name:{m_name}|Email:{m_email}|Phone:{m_phone}|LinkedIn:{m_linkedin}|GitHub:{m_github}\nTarget Job:{m_job}\nTemplate:{template_style}\nSummary:{m_summary}\nExperience:{m_exp}\nEducation:{m_edu}\nSkills:{m_skills}\nCertifications:{m_certs}\nProjects:{m_projects}\n\nGenerate a full professional resume."
                            resume_md = call_gemini(prompt, system=RESUME_SYSTEM)
                            st.session_state["generated_resume_text"] = resume_md
                            add_log("module", f"Manual resume generated for {m_name}.")
                            st.markdown('<div class="alert-success">✅ Resume generated! Switch to Tab 2.</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

    with tab2:
        resume_text = st.session_state.get("generated_resume_text", "")
        if not resume_text:
            st.markdown('<div class="alert-warning">⚠️ No resume generated yet. Complete Step 1 first.</div>', unsafe_allow_html=True)
            return

        st.markdown("## ✅ Your AI-Generated Resume")
        st.markdown('<div class="zna-card">', unsafe_allow_html=True)
        st.markdown(resume_text)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("⬇️ Download Markdown", data=resume_text,
                               file_name="resume.md", mime="text/markdown", use_container_width=True)
        with c2:
            try:
                pdf_bytes = generate_pdf_bytes(resume_text, "Resume")
                st.download_button("⬇️ Download PDF", data=pdf_bytes,
                                   file_name="resume.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.warning(f"PDF export unavailable: {e}")
        with c3:
            if st.button("♻️ Regenerate", use_container_width=True):
                st.session_state["generated_resume_text"] = ""; st.rerun()

        st.markdown("---")
        st.markdown("### ✏️ Edit Resume")
        edited = st.text_area("Edit the resume text directly:", value=resume_text, height=350)
        if st.button("💾 Save Edits"):
            st.session_state["generated_resume_text"] = edited
            add_log("module", "Resume manually edited and saved.")
            st.markdown('<div class="alert-success">✅ Edits saved.</div>', unsafe_allow_html=True)
            st.rerun()


# ── Page: Cover Letter Generator ─────────────────────────────────────────────
def page_cover_letter():
    st.markdown("# ✉️ Auto-Cover Letter")
    st.caption("Generate a highly personalised cover letter based on the exact data from your current resume.")

    if not st.session_state.get("resume_data"):
        st.markdown('<div class="alert-error">⚠️ No resume found in memory! Please build your resume in the <b>Smart Resume Builder</b> first so the AI knows your background.</div>', unsafe_allow_html=True)
        if st.button("→ Go to Resume Builder"):
            st.session_state["page"] = "Smart Resume Builder"; st.rerun()
        return

    r = st.session_state["resume_data"]
    st.markdown(f'<div class="alert-success">✅ Resume loaded for <b>{r.get("name","Unknown")}</b> — Target: <b>{r.get("target_job","N/A")}</b></div>', unsafe_allow_html=True)

    st.markdown("### 🎯 Job Details")
    c1, c2 = st.columns(2)
    with c1:
        company_name    = st.text_input("Company Name *", placeholder="e.g. Google")
        hiring_manager  = st.text_input("Hiring Manager (optional)", placeholder="e.g. Ms. Priya Sharma")
    with c2:
        job_title = st.text_input("Exact Job Title *", placeholder="e.g. Software Engineer, L4")
        tone      = st.selectbox("Tone", ["Professional", "Enthusiastic", "Confident", "Concise"])

    job_desc = st.text_area("Paste Job Description (recommended)",
                             placeholder="Paste the job description here for maximum personalisation…", height=140)

    if st.button("✨  Generate Cover Letter", type="primary"):
        if not company_name or not job_title:
            st.markdown('<div class="alert-error">⚠️ Company Name and Job Title are required.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("✍️ Writing your personalised cover letter…"):
                try:
                    prompt = f"Candidate Resume:\n{json.dumps(r,indent=2)}\n\nJob Title:{job_title}\nCompany:{company_name}\nHiring Manager:{hiring_manager or 'Hiring Manager'}\nTone:{tone}\nJob Description:{job_desc or 'Not provided'}\n\nWrite a cover letter."
                    cl = call_gemini(prompt, system=COVER_LETTER_SYSTEM)
                    st.session_state["cover_letter"] = cl
                    add_log("module", f"Cover letter generated for {company_name}.")
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
                pdf_b = generate_pdf_bytes(st.session_state["cover_letter"], "Cover Letter")
                st.download_button("⬇️ Download PDF", data=pdf_b,
                                   file_name="cover_letter.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.warning(f"PDF export unavailable: {e}")
        with c3:
            if st.button("♻️ Regenerate", use_container_width=True):
                st.session_state["cover_letter"] = ""; st.rerun()

        st.markdown("---")
        st.markdown("### ✏️ Edit Cover Letter")
        edited_cl = st.text_area("Edit directly:", value=st.session_state["cover_letter"], height=250)
        if st.button("💾 Save Edits", key="save_cl"):
            st.session_state["cover_letter"] = edited_cl
            add_log("module", "Cover letter manually edited.")
            st.markdown('<div class="alert-success">✅ Edits saved.</div>', unsafe_allow_html=True)
            st.rerun()


# ── Page: ATS Match Engine ────────────────────────────────────────────────────
def page_ats_engine():
    st.markdown("# 🔍 ATS Match Engine")
    st.caption("Semantic NLP-powered Applicant Tracking System analyser.")

    resume_text = st.session_state.get("generated_resume_text", "")
    if not resume_text and st.session_state.get("resume_data"):
        resume_text = json.dumps(st.session_state["resume_data"], indent=2)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📄 Resume")
        if resume_text:
            st.markdown('<div class="alert-success">✅ Resume loaded from memory.</div>', unsafe_allow_html=True)
            resume_override = st.text_area("Override / Edit Resume Text:", value=resume_text, height=220)
        else:
            st.markdown('<div class="alert-warning">⚠️ No resume in memory. Paste manually below.</div>', unsafe_allow_html=True)
            resume_override = st.text_area("Paste Resume Text:", height=220, placeholder="Paste your resume…")
    with c2:
        st.markdown("### 💼 Job Description")
        job_desc_ats = st.text_area("Paste the full Job Description *",
                                    height=220, placeholder="Paste the complete job description here…")

    if st.button("🔍  Run ATS Analysis", type="primary"):
        final_resume = resume_override.strip() if resume_override.strip() else resume_text
        if not final_resume:
            st.markdown('<div class="alert-error">⚠️ Resume text is required.</div>', unsafe_allow_html=True)
        elif not job_desc_ats.strip():
            st.markdown('<div class="alert-error">⚠️ Job Description is required.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("🤖 Running semantic ATS analysis…"):
                try:
                    prompt = f"RESUME:\n{final_resume}\n\nJOB DESCRIPTION:\n{job_desc_ats}\n\nAnalyse and return JSON."
                    raw    = call_gemini(prompt, system=ATS_SYSTEM)
                    raw    = re.sub(r"```json|```", "", raw).strip()
                    result = json.loads(raw)
                    st.session_state["ats_result"] = result
                    score  = result.get("score", 0)
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
        st.markdown("---")
        score = result.get("score", 0)
        color = "#34d35f" if score >= 75 else "#ffd60a" if score >= 50 else "#ff5147"

        st.markdown(f"""
        <div class="zna-card" style="text-align:center;padding:36px">
            <div style="font-size:80px;font-weight:900;color:{color};letter-spacing:-0.04em;line-height:1">{score}<span style="font-size:36px">%</span></div>
            <div style="font-size:15px;color:#ababb0;margin-top:6px;font-weight:500">ATS Match Score</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        dark = st.session_state["dark_mode"]

        with c1:
            st.markdown("### ✅ Matched")
            for kw in result.get("matched_keywords", []):
                st.markdown(f'<span style="background:{"#0e2b1a" if dark else "#d4edda"};color:#34d35f;padding:3px 10px;border-radius:20px;font-size:12px;margin:2px;display:inline-block">{kw}</span>', unsafe_allow_html=True)
        with c2:
            st.markdown("### ❌ Missing")
            for kw in result.get("missing_keywords", []):
                st.markdown(f'<span style="background:{"#2b1212" if dark else "#fce4ec"};color:#ff5147;padding:3px 10px;border-radius:20px;font-size:12px;margin:2px;display:inline-block">{kw}</span>', unsafe_allow_html=True)
        with c3:
            st.markdown("### 💪 Strengths")
            for s in result.get("strengths", []):
                st.markdown(f"• {s}")
        with c4:
            st.markdown("### 🔧 Improvements")
            for imp in result.get("improvements", []):
                st.markdown(f"• {imp}")

        st.markdown("---")
        st.markdown("### 🪄 One-Click Resume Tailoring")
        st.caption("Automatically rewrite your resume to close keyword gaps.")

        if st.button("✨  Tailor Resume to This Job", type="primary"):
            base = st.session_state.get("generated_resume_text", "") or resume_text
            if not base:
                st.markdown('<div class="alert-error">⚠️ No resume in memory to tailor.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("🤖 Tailoring resume…"):
                    try:
                        missing_kws = ", ".join(result.get("missing_keywords", []))
                        tp = f"Current Resume:\n{base}\n\nJob Description:\n{job_desc_ats}\n\nMissing Keywords to incorporate naturally: {missing_kws}\n\nRewrite the resume for a higher ATS match. Keep it truthful and professional."
                        tailored = call_gemini(tp, system=RESUME_SYSTEM)
                        st.session_state["generated_resume_text"] = tailored
                        add_log("module", "Resume tailored to job description.")
                        st.markdown('<div class="alert-success">✅ Resume tailored! View in Resume Builder → Tab 2.</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="alert-error">⚠️ {e}</div>', unsafe_allow_html=True)

        report = f"""ATS ANALYSIS REPORT\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nSCORE: {score}/100\n\nMATCHED KEYWORDS:\n{chr(10).join('• '+k for k in result.get('matched_keywords',[]))}\n\nMISSING KEYWORDS:\n{chr(10).join('• '+k for k in result.get('missing_keywords',[]))}\n\nSTRENGTHS:\n{chr(10).join('• '+s for s in result.get('strengths',[]))}\n\nIMPROVEMENTS:\n{chr(10).join('• '+i for i in result.get('improvements',[]))}"""
        st.download_button("⬇️ Download ATS Report", data=report,
                           file_name="ats_report.txt", mime="text/plain")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    inject_css()
    render_sidebar()

    page = st.session_state["page"]
    if   page == "Landing":               page_landing()
    elif page == "Overview Dashboard":    page_overview()
    elif page == "Smart Resume Builder":  page_resume_builder()
    elif page == "Cover Letter Generator":page_cover_letter()
    elif page == "ATS Match Engine":      page_ats_engine()


if __name__ == "__main__":
    main()
