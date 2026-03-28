"""
Page 4: Job Portal
AI-powered LinkedIn job search suggestions, alternate titles, and company targets.
Unlocks once the user has set a Target Job Title in the Resume Builder.
"""

import streamlit as st
from ui_utils import page_title, resume_mini_card, keyword_pills, section_header, warning_banner
from state_manager import (
    get_resume, get_target_title, has_resume,
    get_job_description, set_job_description,
)
from backend import run_ats_scan, extract_keywords, LLMError
from backend.llm_service import complete

# ── Page Setup ────────────────────────────────────────────────────────────────
page_title("🌐", "Job Portal", "AI-powered job search strategy tailored to your resume.")

target_title = get_target_title()
if not target_title:
    warning_banner(
        "Fill out the **Target Job Title** in the Resume Builder to unlock the Job Portal."
    )
    st.stop()

# ── Resume context ────────────────────────────────────────────────────────────
resume = get_resume()
if resume:
    st.markdown("#### 🗂️ Active Resume")
    resume_mini_card(resume)

st.divider()

# ── Search Strategy ───────────────────────────────────────────────────────────
section_header("🎯", "AI Search Strategy")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"**Target Role:** `{target_title}`")
    if resume:
        skills = resume.get("skills", {}).get("technical", [])
        if skills:
            st.markdown("**Your Top Skills:**")
            keyword_pills(skills[:10], colour="#1e3a5f")

with col2:
    generate_strategy = st.button("🤖 Generate Search Strategy", type="primary", use_container_width=True)

if generate_strategy:
    skills_list = []
    if resume:
        skills_list = resume.get("skills", {}).get("technical", [])

    with st.spinner("🔍 Generating LinkedIn search strategy..."):
        try:
            system = (
                "You are a job search strategist and recruiter. "
                "Return ONLY a valid JSON object — no markdown, no commentary."
            )
            user = f"""Generate a complete job search strategy for:
Role: {target_title}
Skills: {", ".join(skills_list[:15])}

Return JSON with this structure:
{{
  "linkedin_search_url": "https://www.linkedin.com/jobs/search/?keywords=...",
  "recommended_search_terms": [],
  "alternative_job_titles": [],
  "top_companies_to_target": [
    {{"name": "", "reason": ""}}
  ],
  "salary_range": {{
    "india_lpa": "",
    "us_usd": "",
    "uk_gbp": ""
  }},
  "search_tips": [],
  "resume_gaps_to_address": [],
  "certifications_to_boost_profile": []
}}"""
            data = complete(system, user, temperature=0.35, max_tokens=1500, json_mode=True)
            st.session_state["zna_job_strategy"] = data
        except LLMError as e:
            st.error(f"Strategy generation failed: {e}")

# ── Display Strategy ──────────────────────────────────────────────────────────
strategy = st.session_state.get("zna_job_strategy")
if strategy:
    st.divider()

    # LinkedIn CTA
    linkedin_url = strategy.get("linkedin_search_url", "")
    if linkedin_url:
        st.markdown("### 🔗 Your LinkedIn Job Search")
        st.markdown(
            f'<a href="{linkedin_url}" target="_blank" style="'
            f'background:#0077b5;color:white;padding:10px 20px;'
            f'border-radius:6px;text-decoration:none;font-weight:600;font-size:14px">'
            f'🔍 Open LinkedIn Jobs Search →</a>',
            unsafe_allow_html=True,
        )
        st.caption(f"`{linkedin_url}`")
        st.markdown("")

    col_left, col_right = st.columns(2)

    with col_left:
        # Alternative titles
        alt_titles = strategy.get("alternative_job_titles", [])
        if alt_titles:
            section_header("📋", "Alternative Job Titles")
            keyword_pills(alt_titles, colour="#1e3a5f")
            st.markdown("")

        # Search terms
        search_terms = strategy.get("recommended_search_terms", [])
        if search_terms:
            section_header("🔎", "Recommended Search Terms")
            keyword_pills(search_terms, colour="#1a3a2a")
            st.markdown("")

        # Salary ranges
        salary = strategy.get("salary_range", {})
        if any(salary.values()):
            section_header("💰", "Estimated Salary Range")
            scols = st.columns(3)
            with scols[0]:
                st.metric("India", salary.get("india_lpa", "N/A"))
            with scols[1]:
                st.metric("USA", salary.get("us_usd", "N/A"))
            with scols[2]:
                st.metric("UK", salary.get("uk_gbp", "N/A"))

    with col_right:
        # Top companies
        companies = strategy.get("top_companies_to_target", [])
        if companies:
            section_header("🏢", "Top Companies to Target")
            for co in companies:
                with st.expander(f"🏢 {co.get('name', '')}"):
                    st.write(co.get("reason", ""))

        # Search tips
        tips = strategy.get("search_tips", [])
        if tips:
            section_header("💡", "Search Tips")
            for tip in tips:
                st.markdown(f"- {tip}")

    # Resume gaps
    gaps = strategy.get("resume_gaps_to_address", [])
    certs = strategy.get("certifications_to_boost_profile", [])

    if gaps or certs:
        st.divider()
        gap_col, cert_col = st.columns(2)
        with gap_col:
            if gaps:
                section_header("⚠️", "Resume Gaps to Address")
                for g in gaps:
                    st.markdown(f"- {g}")
        with cert_col:
            if certs:
                section_header("🏅", "Certifications That Will Help")
                keyword_pills(certs, colour="#3b1f5e")

# ── Quick ATS Check against a live JD ────────────────────────────────────────
st.divider()
section_header("⚡", "Quick ATS Check")
st.caption("Paste any job posting here to instantly score your resume against it.")

jd_input = st.text_area(
    "Paste Job Description:",
    value=get_job_description(),
    placeholder="Paste a full job description here...",
    height=140,
    key="portal_jd_input",
)

if st.button("🚀 Quick Scan", use_container_width=False):
    if not resume:
        warning_banner("Build your resume first before running a quick scan.")
    elif not jd_input.strip():
        st.error("Paste a job description first.")
    else:
        set_job_description(jd_input)
        with st.spinner("Scanning..."):
            try:
                result = run_ats_scan(resume, jd_input)
                score = result.get("overall_score", 0)
                verdict = result.get("verdict", "")
                matched = result.get("matched_keywords", [])
                missing = result.get("missing_keywords", [])

                score_col, verdict_col = st.columns([1, 2])
                with score_col:
                    st.metric("ATS Score", f"{score}%")
                    st.progress(score / 100)
                with verdict_col:
                    st.markdown(f"### {verdict}")
                    if missing:
                        st.markdown("**Add these keywords:**")
                        keyword_pills(missing[:12], colour="#5a1e1e")

                if matched:
                    st.markdown("**Already matched:**")
                    keyword_pills(matched[:12], colour="#1a3a2a")

            except LLMError as e:
                st.error(f"Scan failed: {e}")
