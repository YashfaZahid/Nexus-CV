"""Pydantic schemas for structured AI responses and form data."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class ContactInfo(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    website: str = ""


class EducationEntry(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""
    details: str = ""


class ExperienceEntry(BaseModel):
    company: str = ""
    title: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    bullets: list[str] = Field(default_factory=list)
    description: str = ""


class ProjectEntry(BaseModel):
    name: str = ""
    technologies: str = ""
    url: str = ""
    bullets: list[str] = Field(default_factory=list)
    description: str = ""


class CertificationEntry(BaseModel):
    name: str = ""
    issuer: str = ""
    date: str = ""
    credential_id: str = ""


class LanguageEntry(BaseModel):
    language: str = ""
    proficiency: str = ""


class JobTarget(BaseModel):
    job_title: str = ""
    company: str = ""
    job_description: str = ""


class CVProfile(BaseModel):
    contact: ContactInfo = Field(default_factory=ContactInfo)
    professional_summary: str = ""
    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    internships: list[ExperienceEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[CertificationEntry] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    languages: list[LanguageEntry] = Field(default_factory=list)
    portfolio_links: list[str] = Field(default_factory=list)
    job_target: JobTarget = Field(default_factory=JobTarget)


class GeneratedSection(BaseModel):
    heading: str
    content: str


class GeneratedCV(BaseModel):
    contact: ContactInfo = Field(default_factory=ContactInfo)
    professional_summary: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    internships: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    certifications: list[CertificationEntry] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    languages: list[LanguageEntry] = Field(default_factory=list)
    portfolio_links: list[str] = Field(default_factory=list)


class GeneratedCoverLetter(BaseModel):
    greeting: str = "Dear Hiring Manager,"
    body_paragraphs: list[str] = Field(default_factory=list)
    closing: str = "Sincerely,"
    signature_name: str = ""


class ImprovementItem(BaseModel):
    category: str
    severity: str = "medium"
    original: str = ""
    recommended: str = ""
    explanation: str = ""


class CVAnalysisResult(BaseModel):
    extracted_profile: CVProfile = Field(default_factory=CVProfile)
    grammar_issues: list[ImprovementItem] = Field(default_factory=list)
    weak_descriptions: list[ImprovementItem] = Field(default_factory=list)
    formatting_issues: list[ImprovementItem] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    irrelevant_content: list[ImprovementItem] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    overall_notes: str = ""


class SectionScore(BaseModel):
    name: str
    score: float
    max_score: float
    details: str
    recommendations: list[str] = Field(default_factory=list)


class ATSResult(BaseModel):
    overall_score: float
    keyword_score: float
    formatting_score: float
    skills_score: float
    experience_score: float
    completeness_score: float
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    section_scores: list[SectionScore] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "ATS scores are deterministic estimates based on transparent criteria "
        "(keyword overlap, section completeness, formatting signals, and relevance). "
        "They are not guaranteed results from any employer's ATS."
    )

    @field_validator(
        "overall_score",
        "keyword_score",
        "formatting_score",
        "skills_score",
        "experience_score",
        "completeness_score",
        mode="before",
    )
    @classmethod
    def clamp_score(cls, v: Any) -> float:
        try:
            return max(0.0, min(100.0, float(v)))
        except (TypeError, ValueError):
            return 0.0


class GenerationBundle(BaseModel):
    cv: GeneratedCV
    cover_letter: GeneratedCoverLetter
    template_id: str = "classic"
    notes: Optional[str] = None
