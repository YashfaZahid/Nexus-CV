"""Generate professionally formatted PDF and DOCX CVs and cover letters."""

from __future__ import annotations

import io
from typing import Literal

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from src.schemas import GeneratedCoverLetter, GeneratedCV

TemplateId = Literal["classic", "modern", "minimal"]

TEMPLATES = {
    "classic": {
        "label": "Classic ATS",
        "accent": colors.HexColor("#1e293b"),
        "name_size": 16,
        "heading_size": 11,
    },
    "modern": {
        "label": "Modern Violet",
        "accent": colors.HexColor("#7C3AED"),
        "name_size": 17,
        "heading_size": 11,
    },
    "minimal": {
        "label": "Minimal Clean",
        "accent": colors.HexColor("#0EA5E9"),
        "name_size": 15,
        "heading_size": 10,
    },
}


def _contact_line(cv: GeneratedCV) -> str:
    c = cv.contact
    bits = [x for x in [c.email, c.phone, c.location] if x]
    links = [x for x in [c.linkedin, c.github, c.portfolio, c.website] if x]
    line = " | ".join(bits)
    if links:
        line = f"{line} | {' | '.join(links)}" if line else " | ".join(links)
    return line


def _escape(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def cv_to_plain_text(cv: GeneratedCV) -> str:
    lines: list[str] = []
    name = cv.contact.full_name or "Curriculum Vitae"
    lines.append(name)
    lines.append(_contact_line(cv))
    lines.append("")
    if cv.professional_summary:
        lines.append("PROFESSIONAL SUMMARY")
        lines.append(cv.professional_summary)
        lines.append("")
    if cv.skills:
        lines.append("SKILLS")
        lines.append(", ".join(cv.skills))
        lines.append("")
    if cv.experience:
        lines.append("EXPERIENCE")
        for e in cv.experience:
            header = f"{e.title} — {e.company}".strip(" —")
            dates = " – ".join(x for x in [e.start_date, e.end_date] if x)
            lines.append(f"{header}{f' ({dates})' if dates else ''}")
            for b in e.bullets:
                lines.append(f"• {b}")
            if e.description and not e.bullets:
                lines.append(e.description)
            lines.append("")
    if cv.internships:
        lines.append("INTERNSHIPS")
        for e in cv.internships:
            header = f"{e.title} — {e.company}".strip(" —")
            dates = " – ".join(x for x in [e.start_date, e.end_date] if x)
            lines.append(f"{header}{f' ({dates})' if dates else ''}")
            for b in e.bullets:
                lines.append(f"• {b}")
            lines.append("")
    if cv.education:
        lines.append("EDUCATION")
        for ed in cv.education:
            lines.append(f"{ed.degree} {ed.field} — {ed.institution}".strip())
            dates = " – ".join(x for x in [ed.start_date, ed.end_date] if x)
            if dates:
                lines.append(dates)
            if ed.details:
                lines.append(ed.details)
            lines.append("")
    if cv.projects:
        lines.append("PROJECTS")
        for p in cv.projects:
            lines.append(f"{p.name}{' | ' + p.technologies if p.technologies else ''}")
            for b in p.bullets:
                lines.append(f"• {b}")
            if p.description and not p.bullets:
                lines.append(p.description)
            lines.append("")
    if cv.certifications:
        lines.append("CERTIFICATIONS")
        for cert in cv.certifications:
            lines.append(f"{cert.name} — {cert.issuer} ({cert.date})".strip(" —()"))
        lines.append("")
    if cv.achievements:
        lines.append("ACHIEVEMENTS")
        for a in cv.achievements:
            lines.append(f"• {a}")
        lines.append("")
    if cv.languages:
        lines.append("LANGUAGES")
        lines.append(", ".join(f"{l.language} ({l.proficiency})" if l.proficiency else l.language for l in cv.languages))
        lines.append("")
    if cv.portfolio_links:
        lines.append("PORTFOLIO")
        for link in cv.portfolio_links:
            lines.append(f"• {link}")
    return "\n".join(lines).strip()


def cover_letter_to_plain_text(cl: GeneratedCoverLetter) -> str:
    parts = [cl.greeting, ""]
    for p in cl.body_paragraphs:
        parts.append(p)
        parts.append("")
    parts.append(cl.closing)
    parts.append(cl.signature_name)
    return "\n".join(parts).strip()


def build_cv_pdf(cv: GeneratedCV, template_id: TemplateId = "classic") -> bytes:
    tmpl = TEMPLATES.get(template_id, TEMPLATES["classic"])
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()
    name_style = ParagraphStyle(
        "Name",
        parent=styles["Heading1"],
        fontSize=tmpl["name_size"],
        textColor=tmpl["accent"],
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=20,
    )
    contact_style = ParagraphStyle(
        "Contact",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10,
    )
    heading_style = ParagraphStyle(
        "SectionHead",
        parent=styles["Heading2"],
        fontSize=tmpl["heading_size"],
        textColor=tmpl["accent"],
        spaceBefore=10,
        spaceAfter=4,
        leading=14,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceAfter=4,
    )
    role_style = ParagraphStyle(
        "Role",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        spaceBefore=4,
        spaceAfter=2,
        textColor=colors.HexColor("#0f172a"),
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        leftIndent=12,
        spaceAfter=1,
    )

    story: list = []
    story.append(Paragraph(_escape(cv.contact.full_name or "Curriculum Vitae"), name_style))
    story.append(Paragraph(_escape(_contact_line(cv)), contact_style))
    story.append(HRFlowable(width="100%", thickness=1, color=tmpl["accent"], spaceAfter=8))

    def add_heading(title: str) -> None:
        story.append(Paragraph(title, heading_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=4))

    if cv.professional_summary:
        add_heading("PROFESSIONAL SUMMARY")
        story.append(Paragraph(_escape(cv.professional_summary), body))

    if cv.skills:
        add_heading("SKILLS")
        story.append(Paragraph(_escape(", ".join(cv.skills)), body))

    def add_roles(title: str, roles: list) -> None:
        if not roles:
            return
        add_heading(title)
        for e in roles:
            header = f"<b>{_escape(e.title)}</b>"
            if e.company:
                header += f" — {_escape(e.company)}"
            dates = " – ".join(x for x in [e.start_date, e.end_date] if x)
            if dates:
                header += f" &nbsp;&nbsp;<font color='#64748B'>{_escape(dates)}</font>"
            story.append(Paragraph(header, role_style))
            for b in e.bullets:
                story.append(Paragraph(f"• {_escape(b)}", bullet_style))
            if e.description and not e.bullets:
                story.append(Paragraph(_escape(e.description), body))

    add_roles("EXPERIENCE", cv.experience)
    add_roles("INTERNSHIPS", cv.internships)

    if cv.education:
        add_heading("EDUCATION")
        for ed in cv.education:
            line = f"<b>{_escape(ed.degree)}</b>"
            if ed.field:
                line += f" in {_escape(ed.field)}"
            if ed.institution:
                line += f" — {_escape(ed.institution)}"
            story.append(Paragraph(line, role_style))
            meta = " – ".join(x for x in [ed.start_date, ed.end_date] if x)
            if ed.gpa:
                meta = f"{meta} | GPA: {ed.gpa}" if meta else f"GPA: {ed.gpa}"
            if meta:
                story.append(Paragraph(_escape(meta), bullet_style))
            if ed.details:
                story.append(Paragraph(_escape(ed.details), bullet_style))

    if cv.projects:
        add_heading("PROJECTS")
        for p in cv.projects:
            line = f"<b>{_escape(p.name)}</b>"
            if p.technologies:
                line += f" — {_escape(p.technologies)}"
            story.append(Paragraph(line, role_style))
            for b in p.bullets:
                story.append(Paragraph(f"• {_escape(b)}", bullet_style))
            if p.description and not p.bullets:
                story.append(Paragraph(_escape(p.description), body))

    if cv.certifications:
        add_heading("CERTIFICATIONS")
        for cert in cv.certifications:
            line = f"• <b>{_escape(cert.name)}</b>"
            if cert.issuer:
                line += f" — {_escape(cert.issuer)}"
            if cert.date:
                line += f" ({_escape(cert.date)})"
            story.append(Paragraph(line, bullet_style))

    if cv.achievements:
        add_heading("ACHIEVEMENTS")
        for a in cv.achievements:
            story.append(Paragraph(f"• {_escape(a)}", bullet_style))

    if cv.languages:
        add_heading("LANGUAGES")
        langs = ", ".join(
            f"{l.language} ({l.proficiency})" if l.proficiency else l.language for l in cv.languages
        )
        story.append(Paragraph(_escape(langs), body))

    if cv.portfolio_links:
        add_heading("PORTFOLIO")
        for link in cv.portfolio_links:
            story.append(Paragraph(f"• {_escape(link)}", bullet_style))

    doc.build(story)
    return buffer.getvalue()


def build_cover_letter_pdf(cl: GeneratedCoverLetter, template_id: TemplateId = "classic") -> bytes:
    tmpl = TEMPLATES.get(template_id, TEMPLATES["classic"])
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "CLBody",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
    )
    story = [
        Paragraph(_escape(cl.greeting), body),
    ]
    for p in cl.body_paragraphs:
        story.append(Paragraph(_escape(p), body))
    story.append(Spacer(1, 8))
    story.append(Paragraph(_escape(cl.closing), body))
    story.append(Paragraph(_escape(cl.signature_name), body))
    # subtle accent rule at top
    story.insert(0, HRFlowable(width="100%", thickness=2, color=tmpl["accent"], spaceAfter=18))
    doc.build(story)
    return buffer.getvalue()


def build_cv_docx(cv: GeneratedCV, template_id: TemplateId = "classic") -> bytes:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    accent_map = {
        "classic": RGBColor(0x1E, 0x29, 0x3B),
        "modern": RGBColor(0x7C, 0x3A, 0xED),
        "minimal": RGBColor(0x0E, 0xA5, 0xE9),
    }
    accent = accent_map.get(template_id, accent_map["classic"])

    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = name.add_run(cv.contact.full_name or "Curriculum Vitae")
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = accent

    contact = doc.add_paragraph(_contact_line(cv))
    contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in contact.runs:
        r.font.size = Pt(9)

    def heading(text: str) -> None:
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = accent

    if cv.professional_summary:
        heading("PROFESSIONAL SUMMARY")
        doc.add_paragraph(cv.professional_summary)

    if cv.skills:
        heading("SKILLS")
        doc.add_paragraph(", ".join(cv.skills))

    def add_roles(title: str, roles: list) -> None:
        if not roles:
            return
        heading(title)
        for e in roles:
            header = f"{e.title} — {e.company}".strip(" —")
            dates = " – ".join(x for x in [e.start_date, e.end_date] if x)
            p = doc.add_paragraph()
            r = p.add_run(header)
            r.bold = True
            if dates:
                p.add_run(f"  ({dates})")
            for b in e.bullets:
                doc.add_paragraph(b, style="List Bullet")
            if e.description and not e.bullets:
                doc.add_paragraph(e.description)

    add_roles("EXPERIENCE", cv.experience)
    add_roles("INTERNSHIPS", cv.internships)

    if cv.education:
        heading("EDUCATION")
        for ed in cv.education:
            line = f"{ed.degree} {ed.field} — {ed.institution}".strip()
            p = doc.add_paragraph()
            r = p.add_run(line)
            r.bold = True
            dates = " – ".join(x for x in [ed.start_date, ed.end_date] if x)
            if dates or ed.gpa:
                meta = dates
                if ed.gpa:
                    meta = f"{meta} | GPA: {ed.gpa}" if meta else f"GPA: {ed.gpa}"
                doc.add_paragraph(meta)
            if ed.details:
                doc.add_paragraph(ed.details)

    if cv.projects:
        heading("PROJECTS")
        for pjt in cv.projects:
            p = doc.add_paragraph()
            r = p.add_run(pjt.name)
            r.bold = True
            if pjt.technologies:
                p.add_run(f" — {pjt.technologies}")
            for b in pjt.bullets:
                doc.add_paragraph(b, style="List Bullet")
            if pjt.description and not pjt.bullets:
                doc.add_paragraph(pjt.description)

    if cv.certifications:
        heading("CERTIFICATIONS")
        for cert in cv.certifications:
            line = cert.name
            if cert.issuer:
                line += f" — {cert.issuer}"
            if cert.date:
                line += f" ({cert.date})"
            doc.add_paragraph(line, style="List Bullet")

    if cv.achievements:
        heading("ACHIEVEMENTS")
        for a in cv.achievements:
            doc.add_paragraph(a, style="List Bullet")

    if cv.languages:
        heading("LANGUAGES")
        doc.add_paragraph(
            ", ".join(
                f"{l.language} ({l.proficiency})" if l.proficiency else l.language
                for l in cv.languages
            )
        )

    if cv.portfolio_links:
        heading("PORTFOLIO")
        for link in cv.portfolio_links:
            doc.add_paragraph(link, style="List Bullet")

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def build_cover_letter_docx(cl: GeneratedCoverLetter, template_id: TemplateId = "classic") -> bytes:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    doc.add_paragraph(cl.greeting)
    doc.add_paragraph("")
    for p in cl.body_paragraphs:
        doc.add_paragraph(p)
    doc.add_paragraph("")
    doc.add_paragraph(cl.closing)
    doc.add_paragraph(cl.signature_name)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
