"""
Page: Auto-Cover Letter Generator
"""

import streamlit as st
from backend import generate_cover_letter, generate_cover_letter_pdf, TONES, LLMError
from state_manager import get_resume, has_resume, get_job_description, set_cover_letter, get_cover_letter

st.title("✉️ Auto-Cover Letter")
st.caption("Generate a highly personalised cover letter based on the exact data from your current resume.")

# ── Guard ─────────────────────────────────────────────────────────────────────
if not has_resume():
    st.warning("⚠️ No resume found in memory! Please build your resume in the **Smart Resume Builder** first so the AI knows your background.")
    st.stop()

resume = get_resume()

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    jd = st.text_area(
        "Target Job Description",
        value=get_job_description(),
        placeholder="Paste the job description here for a fully tailored letter...",
        height=180,
    )

with col2:
    tone = st.selectbox("Letter Tone", TONES)
    st.caption({
        "Professional": "Formal, confident, achievement-driven.",
        "Enthusiastic": "Warm, energetic, shows personality.",
        "Concise":      "3 tight paragraphs, no filler.",
    }.get(tone, ""))

# ── Generate ──────────────────────────────────────────────────────────────────
if st.button("✨ Generate Cover Letter", type="primary"):
    if not jd.strip():
        st.error("Please paste a Job Description to tailor the letter.")
    else:
        with st.spinner("✍️ Crafting your cover letter..."):
            try:
                result = generate_cover_letter(resume, jd, tone)
                result["name"] = resume.get("name", "")
                set_cover_letter(result)
                st.success(f"✅ Cover letter generated! ({result['word_count']} words)")
            except LLMError as e:
                st.error(f"Generation failed: {e}")

# ── Output ────────────────────────────────────────────────────────────────────
cl = get_cover_letter()
if cl:
    st.divider()

    col_preview, col_actions = st.columns([3, 1])

    with col_preview:
        st.subheader("📝 Your Cover Letter")
        st.text_area(
            "Edit if needed:",
            value=cl.get("text", ""),
            height=380,
            key="cl_edit_box",
        )

    with col_actions:
        st.subheader("Export")
        st.metric("Words", cl.get("word_count", 0))
        st.metric("Tone", cl.get("tone", ""))

        # Update text from editable box before export
        edited_text = st.session_state.get("cl_edit_box", cl["text"])

        # PDF download
        try:
            pdf_bytes = generate_cover_letter_pdf({
                "text": edited_text,
                "name": cl.get("name", ""),
                "date": cl.get("date", ""),
            })
            st.download_button(
                "⬇️ Download PDF",
                data=pdf_bytes,
                file_name="cover_letter.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"PDF failed: {e}")

        # Plain text download
        st.download_button(
            "⬇️ Download .txt",
            data=edited_text,
            file_name="cover_letter.txt",
            mime="text/plain",
        )
