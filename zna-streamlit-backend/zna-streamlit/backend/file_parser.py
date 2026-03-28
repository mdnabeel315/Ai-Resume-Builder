"""
File Parser Service — Extract clean text from uploaded PDF/DOCX resumes.
Integrates with resume_service.parse_raw_data().
"""

import io
import logging
from typing import Union
import fitz  # PyMuPDF
from docx import Document

logger = logging.getLogger(__name__)

def extract_text(file_bytes: bytes, mime_type: str) -> str:
    """
    Extract clean text from uploaded resume file bytes.
    
    Args:
        file_bytes: Bytes from st.file_uploader.getvalue()
        mime_type: 'application/pdf' or 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    Returns:
        Concatenated clean text ready for LLM parsing.
    """
    if 'pdf' in mime_type:
        return _extract_pdf(file_bytes)
    elif 'document' in mime_type:
        return _extract_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {mime_type}")

def _extract_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        logger.info(f"Extracted {len(text)} chars from PDF")
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise

def _extract_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        logger.info(f"Extracted {len(text)} chars from DOCX")
        return text.strip()
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        raise

