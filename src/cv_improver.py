"""Analyze and improve uploaded CVs without inventing qualifications."""

from __future__ import annotations

import json

from src.openai_client import chat_json
from src.schemas import (
    CVAnalysisResult,
    CVProfile,
    GeneratedCoverLetter,
    GeneratedCV,
    GenerationBundle,
)

SYSTEM_ANALYZE = """You are an expert CV reviewer and career coach.
Analyze the uploaded CV text carefully.
Rules:
1. NEVER invent qualifications, experience, skills, or achievements that are not in the source.
2. Identify grammar errors, weak descriptions, formatting problems, missing sections,
   irrelevant information, and missing job-specific keywords (when a job description is provided).
3. For each issue, provide original text (when available), recommended rewrite, severity, and explanation.
4. Extract a structured profile using ONLY facts present in the CV.
5. Return STRICT JSON matching the schema.
"""

SYSTEM_IMPROVE = """You improve CVs and write tailored cover letters.
Rules:
1. NEVER invent qualifications, jobs, degrees, skills, certifications, achievements, or dates.
2. Only rewrite, reorganize, and emphasize content that exists in the source CV / extracted profile.
3. If the job description is provided, tailor wording and keyword emphasis without fabricating experience.
4. Prefer ATS-friendly formatting: clear sections, strong bullets, no tables/icons.
5. Return STRICT JSON matching the schema.
"""


def analyze_cv(
    api_key: str,
    *,
    cv_text: str,
    job_description: str = "",
    model: str = "gpt-4o-mini",
) -> CVAnalysisResult:
    user = f"""Analyze this CV.

CV TEXT:
\"\"\"
{cv_text[:20000]}
\"\"\"

TARGET JOB DESCRIPTION (optional):
\"\"\"
{job_description[:8000] if job_description else '(none provided)'}
\"\"\"

Return JSON:
{{
  "extracted_profile": {{ ... CVProfile fields ... }},
  "grammar_issues": [{{"category":"grammar","severity":"low|medium|high","original":"","recommended":"","explanation":""}}],
  "weak_descriptions": [{{"category":"weak_description","severity":"medium","original":"","recommended":"","explanation":""}}],
  "formatting_issues": [{{"category":"formatting","severity":"medium","original":"","recommended":"","explanation":""}}],
  "missing_sections": ["..."],
  "irrelevant_content": [{{"category":"irrelevant","severity":"low","original":"","recommended":"","explanation":""}}],
  "missing_keywords": ["..."],
  "overall_notes": ""
}}
"""
    return chat_json(
        api_key,
        system=SYSTEM_ANALYZE,
        user=user,
        schema=CVAnalysisResult,
        model=model,
        temperature=0.2,
    )


def improve_cv_and_cover_letter(
    api_key: str,
    *,
    cv_text: str,
    analysis: CVAnalysisResult | None = None,
    job_title: str = "",
    company: str = "",
    job_description: str = "",
    model: str = "gpt-4o-mini",
    template_id: str = "classic",
) -> GenerationBundle:
    analysis_blob = (
        json.dumps(analysis.model_dump(), indent=2) if analysis else "{}"
    )
    user = f"""Produce an improved CV and a tailored cover letter.

ORIGINAL CV TEXT:
\"\"\"
{cv_text[:20000]}
\"\"\"

ANALYSIS JSON (may help guide improvements):
{analysis_blob[:12000]}

TARGET ROLE:
job_title={job_title}
company={company}
job_description:
\"\"\"
{job_description[:8000] if job_description else '(none)'}
\"\"\"

Return JSON GenerationBundle:
{{
  "cv": {{ ... GeneratedCV ... }},
  "cover_letter": {{
    "greeting": "Dear Hiring Manager,",
    "body_paragraphs": ["..."],
    "closing": "Sincerely,",
    "signature_name": ""
  }},
  "template_id": "{template_id}",
  "notes": "Brief note on what was improved — do not claim invented experience."
}}
"""
    bundle = chat_json(
        api_key,
        system=SYSTEM_IMPROVE,
        user=user,
        schema=GenerationBundle,
        model=model,
        temperature=0.3,
    )
    bundle.template_id = template_id
    if not bundle.cover_letter.signature_name and bundle.cv.contact.full_name:
        bundle.cover_letter.signature_name = bundle.cv.contact.full_name
    return bundle


def merge_profile_into_cv(profile: CVProfile) -> GeneratedCV:
    """Fallback mapping when generation fails partially."""
    return GeneratedCV(
        contact=profile.contact,
        professional_summary=profile.professional_summary,
        skills=profile.skills,
        experience=profile.experience,
        internships=profile.internships,
        education=profile.education,
        projects=profile.projects,
        certifications=profile.certifications,
        achievements=profile.achievements,
        languages=profile.languages,
        portfolio_links=profile.portfolio_links,
    )
