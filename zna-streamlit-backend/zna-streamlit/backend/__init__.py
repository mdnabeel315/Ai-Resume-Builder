"""
ZNA Backend — public API surface.

Import from here in your Streamlit pages:

    from backend import parse_and_generate, run_ats_scan, generate_cover_letter
    from backend import generate_resume_pdf, generate_cover_letter_pdf
    from backend import extract_keywords, score_label
    from backend import TEMPLATE_STYLES, TONES
"""

from .resume_service import (
    parse_raw_data,
    generate_resume,
    parse_and_generate,
    TEMPLATE_STYLES,
)

from .ats_service import (
    run_ats_scan,
    extract_keywords,
    score_label,
)

from .cover_letter_service import (
    generate_cover_letter,
    TONES,
)

from .pdf_service import (
    generate_resume_pdf,
    generate_cover_letter_pdf,
)

from .file_parser import (
    extract_text,
)

from .validators import (
    ResumeParseInput,
    ATSScanInput,
    CoverLetterInput,
)

from .error_handler import (
    error_handler,
)

from .llm_service import LLMError, LLMParseError

__all__ = [
    # Resume
    "parse_raw_data",
    "generate_resume",
    "parse_and_generate",
    "TEMPLATE_STYLES",
    # ATS
    "run_ats_scan",
    "extract_keywords",
    "score_label",
    # Cover Letter
    "generate_cover_letter",
    "TONES",
    # PDF
    "generate_resume_pdf",
    "generate_cover_letter_pdf",
# File Parser
    "extract_text",
    # Errors
    "LLMError",
    "LLMParseError",
]
