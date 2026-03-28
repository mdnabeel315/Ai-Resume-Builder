"""
Cover Letter Service
Generates highly personalised, tone-aware cover letters.
"""

from __future__ import annotations
from datetime import date
import logging
from .llm_service import complete

logger = logging.getLogger(__name__)

TONES = ["Professional", "Enthusiastic", "Concise"]

_TONE_GUIDES = {
    "Professional":   "Formal, confident, achievement-driven. No fluff or filler phrases.",
    "Enthusiastic":   "Warm, energetic, genuinely excited about the role. Show personality.",
    "Concise":        "3 tight paragraphs maximum. Every sentence must earn its place.",
}


def generate_cover_letter(
    resume_data: dict,
    job_description: str,
    tone: str = "Professional",
) -> dict:
    """
    Generate a tailored cover letter.

    Returns:
        {
            "text": str,         # full letter text
            "word_count": int,
            "tone": str,
            "date": str,
        }
    """
    tone_guide = _TONE_GUIDES.get(tone, _TONE_GUIDES["Professional"])

    system = (
        f"You are an elite cover letter writer.\n"
        f"Tone: {tone_guide}\n"
        "Hard rules:\n"
        "  - NEVER open with 'I am writing to apply for...'\n"
        "  - Lead with a specific, compelling hook about the role or company\n"
        "  - Reference at least 2 concrete, quantified achievements from the resume\n"
        "  - Close with a confident, non-desperate call to action\n"
        "  - Maximum 350 words\n"
        "  - Return ONLY the letter body — no subject line, no metadata."
    )

    name = resume_data.get("name", "the applicant")
    exp_preview = resume_data.get("experience", [])[:2]
    skills_preview = resume_data.get("skills", {})

    user = (
        f"Write a cover letter for:\n"
        f"Applicant: {name}\n"
        f"Recent Experience: {exp_preview}\n"
        f"Skills: {skills_preview}\n\n"
        f"JOB DESCRIPTION:\n{job_description}"
    )

    text = complete(system, user, temperature=0.75, max_tokens=600, json_mode=False, use_cache=False)

    return {
        "text": text,
        "word_count": len(text.split()),
        "tone": tone,
        "date": date.today().strftime("%B %d, %Y"),
    }
