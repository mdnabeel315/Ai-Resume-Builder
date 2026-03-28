"""
PDF Service — Professional resume & cover letter PDFs using ReportLab Platypus.

Fixes vs old approach:
  - Uses Platypus (flowable layout engine) instead of low-level canvas
  - 3 distinct visual themes matching the UI template styles
  - Proper font registration, colour palette, spacing constants
  - Returns bytes — caller decides whether to write to disk or stream
"""

from __future__ import annotations
import io
from datetime import date
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Colour Palettes ────────────────────────────────────────────────────────────
THEMES: dict[str, dict] = {
    "Standard Corporate": {
        "accent":      colors.HexColor("#1a365d"),
        "subtext":     colors.HexColor("#4a5568"),
        "rule":        colors.HexColor("#2b6cb0"),
        "name_size":   22,
        "heading_size": 9,
        "body_size":    9,
        "font_name":   "Times-Roman",
        "font_bold":   "Times-Bold",
    },
    "Modern Creative": {
        "accent":      colors.HexColor("#6b21a8"),
        "subtext":     colors.HexColor("#553c9a"),
        "rule":        colors.HexColor("#7c3aed"),
        "name_size":   24,
        "heading_size": 9,
        "body_size":    9,
        "font_name":   "Helvetica",
        "font_bold":   "Helvetica-Bold",
    },
    "Minimal Clean": {
        "accent":      colors.HexColor("#111827"),
        "subtext":     colors.HexColor("#6b7280"),
        "rule":        colors.HexColor("#9ca3af"),
        "name_size":   22,
        "heading_size": 8,
        "body_size":    9,
        "font_name":   "Helvetica",
        "font_bold":   "Helvetica-Bold",
    },
}

PAGE_W, PAGE_H = A4
MARGIN_H = 1.8 * cm
MARGIN_V = 1.5 * cm
CONTENT_W = PAGE_W - 2 * MARGIN_H


def _build_styles(theme: dict) -> dict[str, ParagraphStyle]:
    """Build a complete ParagraphStyle map for the given theme."""
    fn = theme["font_name"]
    fb = theme["font_bold"]
    acc = theme["accent"]
    sub = theme["subtext"]

    return {
        "name": ParagraphStyle(
            "ZNA_Name",
            fontName=fb, fontSize=theme["name_size"],
            textColor=acc, spaceAfter=1 * mm, leading=theme["name_size"] + 2,
        ),
        "contact": ParagraphStyle(
            "ZNA_Contact",
            fontName=fn, fontSize=7.5,
            textColor=sub, spaceAfter=3 * mm, leading=11,
        ),
        "section_heading": ParagraphStyle(
            "ZNA_SectionHeading",
            fontName=fb, fontSize=theme["heading_size"],
            textColor=acc, spaceBefore=4 * mm, spaceAfter=1 * mm,
            leading=12, wordWrap="LTR",
            textTransform="uppercase", tracking=80,
        ),
        "entry_header": ParagraphStyle(
            "ZNA_EntryHeader",
            fontName=fb, fontSize=theme["body_size"],
            textColor=colors.HexColor("#1a1a1a"), leading=13,
        ),
        "entry_meta": ParagraphStyle(
            "ZNA_EntryMeta",
            fontName=fn, fontSize=8,
            textColor=sub, leading=11,
        ),
        "bullet": ParagraphStyle(
            "ZNA_Bullet",
            fontName=fn, fontSize=theme["body_size"],
            textColor=colors.HexColor("#2d2d2d"),
            leftIndent=10, firstLineIndent=-10,
            leading=12, spaceAfter=1 * mm,
        ),
        "body": ParagraphStyle(
            "ZNA_Body",
            fontName=fn, fontSize=theme["body_size"],
            textColor=colors.HexColor("#2d2d2d"),
            leading=13, spaceAfter=2 * mm,
        ),
        "skills_label": ParagraphStyle(
            "ZNA_SkillsLabel",
            fontName=fb, fontSize=theme["body_size"],
            textColor=acc, leading=13,
        ),
    }


def _rule(theme: dict) -> HRFlowable:
    return HRFlowable(
        width="100%", thickness=0.8,
        color=theme["rule"], spaceAfter=2 * mm,
    )


def _section(title: str, styles: dict, theme: dict) -> list:
    return [
        Paragraph(title, styles["section_heading"]),
        _rule(theme),
    ]


def _safe(val: Any) -> str:
    """Escape XML special chars for ReportLab Paragraph."""
    if not val:
        return ""
    return str(val).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── Resume PDF ─────────────────────────────────────────────────────────────────
def generate_resume_pdf(resume: dict, template_style: str = "Standard Corporate") -> bytes:
    """
    Render a resume dict to a professional PDF.
    Returns raw bytes.
    """
    theme = THEMES.get(template_style, THEMES["Standard Corporate"])
    styles = _build_styles(theme)

    buffer = io.BytesIO()

    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN_H,
        rightMargin=MARGIN_H,
        topMargin=MARGIN_V,
        bottomMargin=MARGIN_V,
    )
    frame = Frame(
        MARGIN_H, MARGIN_V,
        CONTENT_W, PAGE_H - 2 * MARGIN_V,
        id="main",
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=frame)])

    story: list = []

    # ── Header ────────────────────────────────────────────────────────────────
    contact = resume.get("contact") or {}
    story.append(Paragraph(_safe(resume.get("name", "Your Name")), styles["name"]))

    contact_parts = [
        contact.get("email", ""),
        contact.get("phone", ""),
        contact.get("linkedin", ""),
        contact.get("github", ""),
    ]
    contact_line = "  ·  ".join(_safe(p) for p in contact_parts if p)
    if contact_line:
        story.append(Paragraph(contact_line, styles["contact"]))

    story.append(_rule(theme))
    story.append(Spacer(1, 1 * mm))

    # ── Summary ───────────────────────────────────────────────────────────────
    summary = resume.get("summary", "")
    if summary:
        story += _section("Summary", styles, theme)
        story.append(Paragraph(_safe(summary), styles["body"]))

    # ── Skills ────────────────────────────────────────────────────────────────
    skills = resume.get("skills") or {}
    tech = skills.get("technical") or []
    soft = skills.get("soft") or []
    if tech or soft:
        story += _section("Skills", styles, theme)
        if tech:
            story.append(Paragraph(
                f'<b>Technical:</b>  {_safe(", ".join(tech))}',
                styles["body"]
            ))
        if soft:
            story.append(Paragraph(
                f'<b>Soft Skills:</b>  {_safe(", ".join(soft))}',
                styles["body"]
            ))

    # ── Experience ────────────────────────────────────────────────────────────
    experience = resume.get("experience") or []
    if experience:
        story += _section("Experience", styles, theme)
        for exp in experience:
            block = [
                Paragraph(
                    f'<b>{_safe(exp.get("title",""))}</b>  —  {_safe(exp.get("company",""))}',
                    styles["entry_header"]
                ),
                Paragraph(_safe(exp.get("duration", "")), styles["entry_meta"]),
            ]
            for bullet in exp.get("bullets") or []:
                block.append(Paragraph(f"• {_safe(bullet)}", styles["bullet"]))
            block.append(Spacer(1, 2 * mm))
            story.append(KeepTogether(block))

    # ── Education ─────────────────────────────────────────────────────────────
    education = resume.get("education") or []
    if education:
        story += _section("Education", styles, theme)
        for edu in education:
            story.append(Paragraph(
                f'<b>{_safe(edu.get("degree",""))}</b>  —  {_safe(edu.get("institution",""))}',
                styles["entry_header"]
            ))
            story.append(Paragraph(_safe(edu.get("year", "")), styles["entry_meta"]))
            story.append(Spacer(1, 2 * mm))

    # ── Projects ──────────────────────────────────────────────────────────────
    projects = resume.get("projects") or []
    if projects:
        story += _section("Projects", styles, theme)
        for proj in projects:
            tech_str = " · ".join(proj.get("tech") or [])
            block = [
                Paragraph(f'<b>{_safe(proj.get("name",""))}</b>', styles["entry_header"]),
                Paragraph(_safe(proj.get("description", "")), styles["body"]),
            ]
            if tech_str:
                block.append(Paragraph(f'<i>{_safe(tech_str)}</i>', styles["entry_meta"]))
            block.append(Spacer(1, 2 * mm))
            story.append(KeepTogether(block))

    # ── Certifications ────────────────────────────────────────────────────────
    certs = resume.get("certifications") or []
    if certs:
        story += _section("Certifications", styles, theme)
        for cert in certs:
            story.append(Paragraph(f"• {_safe(cert)}", styles["bullet"]))

    doc.build(story)
    return buffer.getvalue()


# ── Cover Letter PDF ───────────────────────────────────────────────────────────
def generate_cover_letter_pdf(cover_letter: dict) -> bytes:
    """
    Render a cover letter dict to a clean PDF.
    Returns raw bytes.
    """
    theme = THEMES["Standard Corporate"]
    styles = _build_styles(theme)

    buffer = io.BytesIO()
    doc = BaseDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=3 * cm, bottomMargin=3 * cm,
    )
    frame = Frame(
        2.5 * cm, 3 * cm,
        PAGE_W - 5 * cm, PAGE_H - 6 * cm,
        id="main",
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=frame)])

    story: list = []

    # Sender name + date
    name = cover_letter.get("name") or cover_letter.get("applicant_name", "")
    letter_date = cover_letter.get("date", date.today().strftime("%B %d, %Y"))

    if name:
        story.append(Paragraph(_safe(name), styles["name"]))
    story.append(Paragraph(_safe(letter_date), styles["entry_meta"]))
    story.append(Spacer(1, 8 * mm))

    # Letter body — split into paragraphs on double newlines
    body_text = cover_letter.get("text", "")
    for para in body_text.split("\n\n"):
        para = para.strip()
        if para:
            story.append(Paragraph(_safe(para), styles["body"]))
            story.append(Spacer(1, 3 * mm))

    doc.build(story)
    return buffer.getvalue()
