"""
Resume Service
Handles:
  1. parse_raw_data  — extract structured JSON from any pasted text
  2. generate_resume — produce a polished, ATS-optimised resume dict
"""

from __future__ import annotations
from typing import Any
import structlog

from .llm_service import complete
from .validators import ResumeParseInput
from .error_handler import error_handler

logger = structlog.get_logger(__name__)

TEMPLATE_STYLES = ["Standard Corporate", "Modern Creative", "Minimal Clean"]

_TEMPLATE_DESCRIPTIONS = {
    "Standard Corporate": "formal, ATS-optimised, clean section hierarchy, conservative",
    "Modern Creative":    "modern, tech-forward, bold headers, suitable for design/engineering roles",
    "Minimal Clean":      "ultra-minimal, generous whitespace, executive tone, no clutter",
}

_PARSE_SCHEMA = '''{
  "name": "",
  "email": "",
  "phone": "",
  "github": "",
  "linkedin": "",
  "summary": "",
  "skills": [],
  "experience": [{"title":"","company":"","duration":"","bullets":[]}],
  "education": [{"degree":"","institution":"","year":""}],
  "projects": [{"name":"","description":"","tech":[]}],
  "certifications": []
}'''

_GENERATE_SCHEMA = '''{
  "name": "",
  "contact": {"email":"","phone":"","github":"","linkedin":""},
  "summary": "",
  "skills": {"technical":[],"soft":[]},
  "experience": [{"title":"","company":"","duration":"","bullets":[]}],
  "education": [{"degree":"","institution":"","year":""}],
  "projects": [{"name":"","description":"","tech":[]}],
  "certifications": [],
  "ats_score": 0,
  "template_style": ""
}'''


@error_handler.intercept
def parse_raw_data(raw_text: str) -> dict:
    \"\"\"
    Parse any pasted resume / LinkedIn text into a structured dict.
    Uses low temperature for maximum extraction accuracy.
    \"\"\"
    input_data = ResumeParseInput(raw_text=raw_text, target_job_title='', template_style='Standard Corporate')
    system = (
        "You are an expert resume parser. Extract every piece of information present. "
        "Return ONLY a valid JSON object matching the schema exactly — no commentary, no markdown."
    )
    user = f"Parse the following text into this JSON schema:\\n{_PARSE_SCHEMA}\\n\\nTEXT:\\n{raw_text}"
    return complete(system, user, temperature=0.1, max_tokens=2048, json_mode=True)


@error_handler.intercept
def generate_resume(
    parsed_data: dict,
    target_job_title: str,
    template_style: str = "Standard Corporate",
) -> dict:
    \"\"\"
    Generate a polished, ATS-optimised resume from parsed candidate data.
    \"\"\"
    style_desc = _TEMPLATE_DESCRIPTIONS.get(template_style, _TEMPLATE_DESCRIPTIONS["Standard Corporate"])

    system = (
        f"You are a world-class resume writer.\\n"
        f"Style: {style_desc}.\\n"
        "Rules:\\n"
        "- Every bullet point must start with a strong past-tense action verb\\n"
        "- Quantify achievements wherever data exists (%, $, X users, N months)\\n"
        "- Mirror language from the target job title naturally\\n"
        "- Set ats_score based on how well the resume matches the target role (0-100)\\n"
        "Return ONLY a valid JSON object — no markdown fences, no commentary."
    )
    user = (
        f"Target role: \\"{target_job_title}\\"\\n"
        f"Template style: \\"{template_style}\\"\\n\\n"
        f"Candidate data:\\n{parsed_data}\\n\\n"
        f"Return JSON matching this schema:\\n{_GENERATE_SCHEMA}"
    )
    return complete(system, user, temperature=0.4, max_tokens=3000, json_mode=True)


@error_handler.intercept
def parse_and_generate(
    raw_text: str,
    target_job_title: str,
    template_style: str = "Standard Corporate",
    overrides: dict | None = None,
) -> tuple[dict, dict]:
    \"\"\"
    Convenience pipeline: parse → optional field overrides → generate.
    Returns (parsed_data, generated_resume).
    \"\"\"
    input_data = ResumeParseInput(
        raw_text=raw_text,
        target_job_title=target_job_title, 
        template_style=template_style
    )
    parsed = parse_raw_data(raw_text)

    # Apply any explicit form-field overrides
    if overrides:
        for k, v in overrides.items():
            if v:
                parsed[k] = v

    resume = generate_resume(parsed, target_job_title, template_style)
    logger.info("Resume pipeline complete", ats_score=resume.get('ats_score', 0))
    return parsed, resume

