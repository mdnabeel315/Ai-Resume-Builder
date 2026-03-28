"""
Page: ATS Match Engine
"""

import streamlit as st
from backend import run_ats_scan, extract_keywords, score_label, LLMError
from state_manager import get_resume, has_resume, get_job_description, set_job_description, set_ats_result, get_ats_result

st.title("🔍 ATS Match Engine")
st.caption("Compare your generated resume against a real Job Description to find missing keywords before you apply.")

# ── Guard ─────────────────────────────────────────────────────────────────────
if not has_resume():
    st.warning("⚠️ No resume loaded. Go to the **Smart Resume Builder** first.")
    st.stop()

resume = get_resume()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Your Active Resume")
    st.success(f"✅ Loaded: **{resume.get('name', 'Resume')}**")
    skills = resume.get("skills", {})
    if skills.get("technical"):
        st.caption("Technical Skills: " + ", ".join(skills["technical"][:8]))

with col2:
    st.subheader("Target Job Description")
    jd = st.text_area(
        "Paste the full Job Description here:",
        value=get_job_description(),
        placeholder="Paste the job requirements, skills, and responsibilities...",
        height=200,
    )
    if jd != get_job_description():
        set_job_description(jd)

# ── Scan ──────────────────────────────────────────────────────────────────────
if st.button("🚀 Run Deep ATS Scan", type="primary"):
    if not jd.strip():
        st.error("Please paste a Job Description.")
    else:
        with st.spinner("🔍 Running semantic ATS analysis..."):
            try:
                result = run_ats_scan(resume, jd)
                set_ats_result(result)
            except LLMError as e:
                st.error(f"ATS scan failed: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
result = get_ats_result()
if result:
    st.divider()
    overall = result.get("overall_score", 0)

    # Score hero
    col_score, col_verdict = st.columns([1, 2])
    with col_score:
        st.metric("Overall ATS Score", f"{overall}%")
    with col_verdict:
        st.markdown(f"### {score_label(overall)}")

    # Breakdown
    st.subheader("📊 Score Breakdown")
    breakdown = result.get("breakdown", {})
    b_cols = st.columns(4)
    labels = {
        "keyword_match": "Keyword Match",
        "skills_alignment": "Skills Alignment",
        "experience_relevance": "Experience",
        "title_match": "Title Match",
    }
    for col, (key, label) in zip(b_cols, labels.items()):
        with col:
            st.metric(label, f"{breakdown.get(key, 0)}%")

    # Keywords
    col_match, col_miss = st.columns(2)
    with col_match:
        st.subheader("✅ Matched Keywords")
        matched = result.get("matched_keywords", [])
        if matched:
            st.markdown(" ".join([f"`{k}`" for k in matched]))
        else:
            st.caption("None found.")

    with col_miss:
        st.subheader("❌ Missing Keywords")
        missing = result.get("missing_keywords", [])
        if missing:
            st.markdown(" ".join([f"`{k}`" for k in missing]))
        else:
            st.caption("None — great coverage!")

    # Missing skills
    missing_skills = result.get("missing_skills", [])
    if missing_skills:
        st.subheader("🛠️ Missing Skills")
        st.markdown(", ".join(f"**{s}**" for s in missing_skills))

    # Improvements
    improvements = result.get("improvements", [])
    if improvements:
        st.subheader("💡 Improvement Suggestions")
        for imp in improvements:
            with st.expander(f"📌 {imp.get('section', 'Section')}"):
                st.markdown(f"**Issue:** {imp.get('issue', '')}")
                st.markdown(f"**Suggestion:** {imp.get('suggestion', '')}")

    # Strengths
    strengths = result.get("strengths", [])
    if strengths:
        st.subheader("💪 Strengths")
        for s in strengths:
            st.markdown(f"- {s}")
