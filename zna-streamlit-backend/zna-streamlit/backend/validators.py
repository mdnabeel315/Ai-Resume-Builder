"""
Pydantic validators for robust backend input handling.
Prevents malformed data from reaching LLM/PDF services.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any
import re

class ResumeParseInput(BaseModel):
    """Validated input for parse_raw_data / parse_and_generate."""
    raw_text: str = Field(..., min_length=50, max_length=10000)
    target_job_title: str = Field(..., min_length=2, max_length=100, regex=r"^[a-zA-Z0-9\\s-]+$")
    template_style: str = Field(..., regex=r"^(Standard Corporate|Modern Creative|Minimal Clean)$")
    overrides: Dict[str, str] = {}

    @validator('raw_text')
    def check_resume_content(cls, v):
        if not re.search(r'(experience|education|skill|project|python|engineer|data)', v.lower()):
            raise ValueError('Text appears empty of resume content')
        return v

    @validator('target_job_title')
    def normalize_title(cls, v):
        return ' '.join(v.strip().split()).title()

class ATSScanInput(BaseModel):
    """Validated input for ATS scan."""
    resume_data: Dict[str, Any]
    job_description: str = Field(..., min_length=100, max_length=5000)

class CoverLetterInput(BaseModel):
    """Validated input for cover letter generation."""
    resume_data: Dict[str, Any]
    job_description: str = Field(..., min_length=100, max_length=5000)
    tone: str = Field(default="Professional", regex=r"^(Professional|Enthusiastic|Formal)$")


# Global usage example:
# from backend.validators import ResumeParseInput
# validated = ResumeParseInput(raw_text=text, target_job_title=title)
"""

