"""Generate job-tailored CV and cover letter from user profile via OpenAI."""

from __future__ import annotations

import json

from src.openai_client import chat_json, chat_text
from src.schemas import (
    CVProfile,
    GeneratedCoverLetter,
    GeneratedCV,
    GenerationBundle,
)

SYSTEM_GENERATE = """You are an expert CV and cover letter writer specializing in ATS-optimized documents.
Rules:
1. NEVER invent qualifications, jobs, degrees, skills, certifications, achievements, or dates.
2. Only use information present in the candidate profile. You may polish wording and emphasize relevance.
3. Tailor language to the target role when a job description is provided.
4. Prefer quantified, action-led bullets when the source data supports it.
5. Keep content professional, concise, and ATS-friendly (no tables, columns, or icons).
6. Return STRICT JSON matching the requested schema.
"""


def _profile_payload(profile: CVProfile) -> str:
    return json.dumps(profile.model_dump(), indent=2)


def generate_cv_and_cover_letter(
    api_key: str,
    profile: CVProfile,
    *,
    model: str = "gpt-4o-mini",
    template_id: str = "classic",
) -> GenerationBundle:
    user = f"""Create a polished, job-tailored CV and cover letter from this candidate profile.

CANDIDATE PROFILE (JSON):
{_profile_payload(profile)}

Return JSON with this exact shape:
{{
  "cv": {{
    "contact": {{"full_name":"", "email":"", "phone":"", "location":"", "linkedin":"", "github":"", "portfolio":"", "website":""}},
    "professional_summary": "",
    "skills": ["..."],
    "experience": [{{"company":"", "title":"", "location":"", "start_date":"", "end_date":"", "bullets":["..."], "description":""}}],
    "internships": [{{"company":"", "title":"", "location":"", "start_date":"", "end_date":"", "bullets":["..."], "description":""}}],
    "education": [{{"institution":"", "degree":"", "field":"", "start_date":"", "end_date":"", "gpa":"", "details":""}}],
    "projects": [{{"name":"", "technologies":"", "url":"", "bullets":["..."], "description":""}}],
    "certifications": [{{"name":"", "issuer":"", "date":"", "credential_id":""}}],
    "achievements": ["..."],
    "languages": [{{"language":"", "proficiency":""}}],
    "portfolio_links": ["..."]
  }},
  "cover_letter": {{
    "greeting": "Dear Hiring Manager,",
    "body_paragraphs": ["para1", "para2", "para3"],
    "closing": "Sincerely,",
    "signature_name": ""
  }},
  "template_id": "{template_id}",
  "notes": "optional short note"
}}

If a field has no source data, use an empty string or empty array. Do not fabricate.
"""
    bundle = chat_json(
        api_key,
        system=SYSTEM_GENERATE,
        user=user,
        schema=GenerationBundle,
        model=model,
        temperature=0.35,
    )
    # Preserve contact facts if model dropped them
    if not bundle.cv.contact.full_name and profile.contact.full_name:
        bundle.cv.contact = profile.contact
    if not bundle.cover_letter.signature_name:
        bundle.cover_letter.signature_name = (
            bundle.cv.contact.full_name or profile.contact.full_name
        )
    bundle.template_id = template_id
    return bundle


def regenerate_section(
    api_key: str,
    *,
    section_name: str,
    current_content: str,
    profile: CVProfile,
    job_description: str = "",
    model: str = "gpt-4o-mini",
) -> str:
    system = (
        "You improve a single CV/cover-letter section. "
        "Never invent facts. Return ONLY the improved section text, no markdown fences."
    )
    user = f"""Improve the '{section_name}' section.

Current content:
{current_content}

Candidate context (JSON):
{_profile_payload(profile)}

Job description (optional):
{job_description or '(none)'}
"""
    return chat_text(api_key, system=system, user=user, model=model, temperature=0.4)


def profile_from_form_dict(data: dict) -> CVProfile:
    return CVProfile.model_validate(data)
