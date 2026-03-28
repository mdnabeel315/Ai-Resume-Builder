"""
ATS Match Engine Service
Accurate, multi-dimensional keyword and semantic matching.

Fixes vs old approach:
  - Breaks scoring into 4 independent dimensions (not one vague score)
  - Uses low temperature (0.15) for consistent, reproducible scores
  - Returns structured improvement plan, not just a number
  - extract_keywords is a standalone utility for the UI keyword highlights
"""

from __future__ import annotations
import logging
from .llm_service import complete

logger = logging.getLogger(__name__)

_SCAN_SCHEMA = """{
  "overall_score": 0,
  "breakdown": {
    "keyword_match": 0,
    "skills_alignment": 0,
    "experience_relevance": 0,
    "title_match": 0
  },
  "matched_keywords": [],
  "missing_keywords": [],
  "missing_skills": [],
  "strengths": [],
  "improvements": [
    {"section": "", "issue": "", "suggestion": ""}
  ],
  "verdict": "Strong Match | Good Match | Partial Match | Weak Match"
}"""

_KEYWORDS_SCHEMA = """{
  "hard_skills": [],
  "soft_skills": [],
  "tools_and_technologies": [],
  "required_qualifications": [],
  "nice_to_have": [],
  "seniority_signals": []
}"""


def run_ats_scan(resume_data: dict, job_description: str) -> dict:
    """
    Deep ATS scan: semantic comparison of resume vs job description.
    Returns a rich scoring breakdown with actionable improvements.
    """
    system = (
        "You are a senior ATS analyst and technical recruiter.\n"
        "Scoring rules:\n"
        "  - keyword_match: exact + semantic keyword overlap (0–100)\n"
        "  - skills_alignment: how well candidate skills map to JD requirements (0–100)\n"
        "  - experience_relevance: relevance of past roles/projects to the JD (0–100)\n"
        "  - title_match: alignment of past job titles with target role (0–100)\n"
        "  - overall_score: weighted average (keywords 30%, skills 35%, experience 25%, title 10%)\n"
        "Be strict and accurate — do NOT inflate scores.\n"
        "Return ONLY a valid JSON object matching the schema. No markdown, no commentary."
    )
    user = (
        f"RESUME DATA:\n{resume_data}\n\n"
        f"JOB DESCRIPTION:\n{job_description}\n\n"
        f"Return JSON matching this schema:\n{_SCAN_SCHEMA}"
    )
    return complete(system, user, temperature=0.15, max_tokens=2000, json_mode=True)


def extract_keywords(job_description: str) -> dict:
    """
    Extract structured keywords from a job description.
    Useful for the UI keyword-highlight feature.
    """
    system = (
        "You are a technical recruiter extracting structured requirements from a job description.\n"
        "Return ONLY a valid JSON object. No markdown, no commentary."
    )
    user = (
        f"Extract all keywords from this job description:\n{job_description}\n\n"
        f"Return JSON matching this schema:\n{_KEYWORDS_SCHEMA}"
    )
    return complete(system, user, temperature=0.1, max_tokens=1024, json_mode=True)


def score_label(score: int) -> str:
    """Map a numeric ATS score to a human-readable label."""
    if score >= 85:
        return "🟢 Strong Match"
    elif score >= 70:
        return "🟡 Good Match"
    elif score >= 50:
        return "🟠 Partial Match"
    else:
        return "🔴 Weak Match"
