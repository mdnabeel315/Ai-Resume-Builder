"""
UI Utilities — shared Streamlit components used across all pages.

Import:
    from ui_utils import error_banner, success_banner, score_gauge, keyword_pills
    from ui_utils import section_header, resume_not_loaded_guard
"""

import streamlit as st


# ── Banners ───────────────────────────────────────────────────────────────────

def error_banner(message: str) -> None:
    st.error(f"❌ {message}")


def success_banner(message: str) -> None:
    st.success(f"✅ {message}")


def warning_banner(message: str) -> None:
    st.warning(f"⚠️ {message}")


def info_banner(message: str) -> None:
    st.info(f"💡 {message}")


# ── Guards ────────────────────────────────────────────────────────────────────

def resume_not_loaded_guard() -> None:
    """
    Call at the top of any page that requires a resume.
    Stops page execution with a clear, friendly message if none is loaded.
    """
    from state_manager import has_resume
    if not has_resume():
        st.warning(
            "⚠️ No resume loaded yet.\n\n"
            "👉 Go to **Smart Resume Builder** first to generate your resume, "
            "then come back here."
        )
        st.stop()


# ── Score Gauge ───────────────────────────────────────────────────────────────

def score_gauge(score: int, label: str = "Score") -> None:
    """
    Render a coloured metric + progress bar for any 0-100 score.
    """
    if score >= 85:
        colour = "🟢"
    elif score >= 70:
        colour = "🟡"
    elif score >= 50:
        colour = "🟠"
    else:
        colour = "🔴"

    st.metric(label, f"{colour} {score}%")
    st.progress(score / 100)


# ── Keyword Pills ─────────────────────────────────────────────────────────────

def keyword_pills(keywords: list[str], colour: str = "#1e3a5f") -> None:
    """
    Render a list of keywords as inline styled chips.
    """
    if not keywords:
        st.caption("None found.")
        return

    pills_html = " ".join(
        f'<span style="'
        f'background:{colour};color:#e8eaf0;padding:2px 10px;'
        f'border-radius:12px;font-size:12px;margin:2px;display:inline-block">'
        f'{kw}</span>'
        for kw in keywords
    )
    st.markdown(pills_html, unsafe_allow_html=True)


# ── Section Header ────────────────────────────────────────────────────────────

def section_header(icon: str, title: str) -> None:
    st.markdown(f"### {icon} {title}")
    st.markdown('<hr style="margin:4px 0 12px;border-color:#2d3147">', unsafe_allow_html=True)


# ── Loading Spinner Context ───────────────────────────────────────────────────

def ai_spinner(message: str = "🤖 AI is thinking..."):
    """Convenience wrapper for st.spinner with a consistent message style."""
    return st.spinner(message)


# ── Resume Mini-Card ──────────────────────────────────────────────────────────

def resume_mini_card(resume: dict) -> None:
    """
    Display a compact summary card of the loaded resume.
    """
    name = resume.get("name", "Unknown")
    score = resume.get("ats_score", 0)
    template = resume.get("template_style", "Standard Corporate")
    skills = resume.get("skills", {})
    tech = skills.get("technical", [])[:5]

    with st.container():
        st.markdown(
            f"""
            <div style="
                background:#1a1d27;border:1px solid #2d3147;
                border-radius:10px;padding:14px 18px;margin-bottom:12px">
                <div style="font-size:16px;font-weight:700;color:#e8eaf0">{name}</div>
                <div style="font-size:11px;color:#8892b0;margin-top:4px">
                    Template: {template} &nbsp;·&nbsp; ATS Score: {score}%
                </div>
                <div style="font-size:11px;color:#64748b;margin-top:6px">
                    {" · ".join(tech)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Page Title with Icon ──────────────────────────────────────────────────────

def page_title(icon: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div style="margin-bottom:8px">
            <span style="font-size:28px;font-weight:800;color:#e8eaf0">{icon} {title}</span>
            {'<div style="font-size:13px;color:#8892b0;margin-top:4px">' + subtitle + '</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<hr style="margin:0 0 20px;border-color:#2d3147">', unsafe_allow_html=True)
