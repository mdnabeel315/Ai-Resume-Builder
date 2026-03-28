"""
Page: Smart Resume Builder
"""

import streamlit as st
from backend import parse_and_generate, generate_resume_pdf, extract_text, TEMPLATE_STYLES, LLMError
from state_manager import set_resume, set_parsed_data, set_target_title, get_target_title

st.title("📄 Smart Resume Builder")

# ── Template Selection ────────────────────────────────────────────────────────
st.subheader("⚙️ Template Settings")
template_style = st.selectbox("Select Professional Template Style:", TEMPLATE_STYLES)

st.divider()

# ── File Upload ───────────────────────────────────────────────────────────────
st.subheader("📎 Upload Resume File (Optional)")
uploaded_file = st.file_uploader(
    "Choose PDF or DOCX resume file",
    type=['pdf', 'docx'],
    help="Upload your existing resume to auto-extract and enhance it."
)

if uploaded_file is not None:
    try:
        with st.spinner("Extracting text from file..."):
            raw_text_extracted = extract_text(uploaded_file.getvalue(), uploaded_file.type)
        st.success(f"✅ Extracted {len(raw_text_extracted)} chars from {uploaded_file.name}")
        st.info("📄 Extracted text loaded below. Review/edit as needed.")
    except Exception as e:
        st.error(f"File parsing failed: {e}")
        raw_text_extracted = None
else:
    raw_text_extracted = None

st.divider()

# ── Input Mode ────────────────────────────────────────────────────────────────
st.subheader("📋 Choose Data Input Method")
mode = st.radio(
    "How do you want to provide your details?",
    ["⚡ Auto-Parse (Paste LinkedIn/Resume Data)", "✍️ Manual Entry (Fill Structured Form)"],
    horizontal=True,
)

auto_parse = mode.startswith("⚡")

# ── Form ──────────────────────────────────────────────────────────────────────
if auto_parse:
    st.info("💡 **Fast-Import:** Copy your entire LinkedIn profile or old resume text and paste it below. The AI will extract and organise it automatically.")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name *", placeholder="e.g. Syed Zaid Karim")
with col2:
    target_job_title = st.text_input("Target Job Title *", placeholder="e.g. Software Engineer", value=get_target_title())

col3, col4 = st.columns(2)
with col3:
    email = st.text_input("Email (for PDF links)")
with col4:
    phone = st.text_input("Phone Number (for PDF links)")

col5, col6 = st.columns(2)
with col5:
    github = st.text_input("GitHub URL (for PDF links)")
with col6:
    linkedin_url = st.text_input("LinkedIn URL (for PDF links)")

if auto_parse:
    # Prefill with extracted text if available
    initial_text = raw_text_extracted or ""
    raw_text = st.text_area(
        "Raw Experience / Education / LinkedIn Data *",
        value=initial_text,
        placeholder="Paste your raw text here... (or upload above)",
        height=160,
    )
else:
    # Manual structured entry
    st.subheader("Work Experience")
    raw_text = st.text_area(
        "Describe your experience, education, skills, and projects",
        placeholder="E.g.\n\nSoftware Engineer at Acme Corp (2022–2024)\n- Built REST APIs serving 100k users\n- Led migration to microservices\n\nB.Tech Computer Science, XYZ University, 2022\n\nSkills: Python, React, AWS, Docker",
        height=200,
    )

# ── Generate ──────────────────────────────────────────────────────────────────
if st.button("✨ Auto Generate AI Resume", type="primary"):
    if not raw_text.strip():
        st.error("Please provide your experience/background text.")
    elif not target_job_title.strip():
        st.error("Please enter a Target Job Title.")
    else:
        # Auto-infer job title from extracted text if possible
        if raw_text_extracted and not target_job_title.strip():
            import re
            common_titles = ['data analyst', 'software engineer', 'data scientist', 'data science', 'analyst']
            for title in common_titles:
                if re.search(title, raw_text_extracted.lower()):
                    target_job_title = title.title().replace(' ', ' ')
                    st.info(f"💡 Auto-detected Target Job: **{target_job_title}**")
                    break
        set_target_title(target_job_title.strip())

        with st.spinner("🤖 Parsing and generating your resume..."):
            try:
                overrides = {
                    k: v for k, v in {
                        "name": name, "email": email, "phone": phone,
                        "github": github, "linkedin": linkedin_url,
                    }.items() if v.strip()
                }

                parsed, resume = parse_and_generate(
                    raw_text,
                    target_job_title,
                    template_style,
                    overrides=overrides,
                )

                set_parsed_data(parsed)
                set_resume(resume)
                st.success(f"✅ Resume generated! ATS Score: **{resume.get('ats_score', 'N/A')}%**")

            except LLMError as e:
                st.error(f"AI generation failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

# ── Output & Download ─────────────────────────────────────────────────────────
from state_manager import get_resume

resume = get_resume()
if resume:
    st.divider()
    st.subheader("2. AI Output & Export")

    tab1, tab2 = st.tabs(["📋 Resume Preview", "📥 Download PDF"])

    with tab1:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.markdown(f"### {resume.get('name', '')}")
            contact = resume.get("contact", {})
            contact_str = "  ·  ".join(filter(None, [
                contact.get("email"), contact.get("phone"),
                contact.get("github"), contact.get("linkedin"),
            ]))
            if contact_str:
                st.caption(contact_str)

            if resume.get("summary"):
                st.markdown("**Summary**")
                st.write(resume["summary"])

            skills = resume.get("skills", {})
            if skills.get("technical"):
                st.markdown(f"**Technical Skills:** {', '.join(skills['technical'])}")
            if skills.get("soft"):
                st.markdown(f"**Soft Skills:** {', '.join(skills['soft'])}")

            for exp in resume.get("experience", []):
                st.markdown(f"**{exp.get('title')}** — {exp.get('company')} _{exp.get('duration')}_")
                for b in exp.get("bullets", []):
                    st.markdown(f"- {b}")

            for edu in resume.get("education", []):
                st.markdown(f"**{edu.get('degree')}** — {edu.get('institution')} _{edu.get('year')}_")

        with col_b:
            score = resume.get("ats_score", 0)
            st.metric("ATS Score", f"{score}%")
            st.metric("Template", resume.get("template_style", template_style))

    with tab2:
        with st.spinner("Generating PDF..."):
            try:
                pdf_bytes = generate_resume_pdf(resume, template_style)
                fname = f"{(resume.get('name') or 'resume').replace(' ', '_')}_resume.pdf"
                st.download_button(
                    label="⬇️ Download Resume PDF",
                    data=pdf_bytes,
                    file_name=fname,
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
