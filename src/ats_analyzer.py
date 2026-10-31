"""Deterministic, explainable ATS compatibility scoring.

Scores are computed from transparent criteria — never invented by an LLM.
"""

from __future__ import annotations

import re
from collections import Counter

from src.schemas import ATSResult, GeneratedCV, SectionScore

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "for", "on", "with", "at",
    "by", "from", "as", "is", "are", "be", "this", "that", "it", "we", "you",
    "our", "your", "will", "can", "may", "not", "have", "has", "had", "been",
    "their", "they", "them", "who", "which", "what", "when", "where", "how",
    "all", "any", "each", "other", "more", "most", "such", "than", "then",
    "into", "over", "after", "before", "about", "also", "using", "use", "used",
    "role", "job", "position", "team", "work", "working", "experience", "years",
    "looking", "require", "requires", "required", "requiring", "including", "include",
    "strong", "ability", "abilities", "preferred", "plus", "must", "should",
    "candidate", "candidates", "company", "opportunity", "join", "help",
    "build", "building", "across", "within", "well", "good", "great", "new",
    "etc", "via", "per", "based", "related", "responsible", "responsibilities",
    "qualification", "qualifications", "requirement", "requirements",
    "description", "summary", "about", "us", "day", "requests",
}

SECTION_WEIGHTS = {
    "keyword": 0.30,
    "formatting": 0.15,
    "skills": 0.20,
    "experience": 0.20,
    "completeness": 0.15,
}


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\+\#\.\-]{1,}", (text or "").lower())
    cleaned: list[str] = []
    for t in tokens:
        t = t.strip(".-")
        if t and t not in STOPWORDS and len(t) > 1:
            cleaned.append(t)
    return cleaned


def _extract_phrases(text: str) -> set[str]:
    """Extract unigrams and skill-like bigrams as candidate keywords."""
    tokens = _tokenize(text)
    unigrams = set(tokens)
    bigrams = {
        f"{tokens[i]} {tokens[i + 1]}"
        for i in range(len(tokens) - 1)
        if _is_skillish(tokens[i]) and _is_skillish(tokens[i + 1])
    }
    return unigrams | bigrams


def _cv_to_text(cv: GeneratedCV) -> str:
    parts: list[str] = []
    c = cv.contact
    parts.extend([c.full_name, c.email, c.phone, c.location, c.linkedin, c.github, c.portfolio])
    parts.append(cv.professional_summary)
    parts.extend(cv.skills)
    parts.extend(cv.achievements)
    parts.extend(cv.portfolio_links)
    for e in cv.experience + cv.internships:
        parts.extend([e.company, e.title, e.location, e.description, *e.bullets])
    for ed in cv.education:
        parts.extend([ed.institution, ed.degree, ed.field, ed.details])
    for p in cv.projects:
        parts.extend([p.name, p.technologies, p.description, *p.bullets])
    for cert in cv.certifications:
        parts.extend([cert.name, cert.issuer])
    for lang in cv.languages:
        parts.extend([lang.language, lang.proficiency])
    return "\n".join(p for p in parts if p)


def _is_skillish(token: str) -> bool:
    """Heuristic: keep technical / proper-skill tokens; drop soft filler."""
    if len(token) <= 2 and token not in {"ai", "ml", "ui", "ux", "qa", "go", "c", "r"}:
        return False
    if re.search(r"\d", token):
        return True
    if re.search(r"[+#.]|sql|aws|azure|gcp|api|cloud|data|dev|ops|python|java|react|node|docker|kuber|linux|git", token):
        return True
    # Capitalized-origin terms often survive lowercasing as multi-char skills
    return len(token) >= 4


def _keyword_score(cv_text: str, job_description: str) -> tuple[float, list[str], list[str], str]:
    if not (job_description or "").strip():
        # Without a JD, score based on lexical richness of CV
        tokens = _tokenize(cv_text)
        unique = len(set(tokens))
        score = min(100.0, 60.0 + unique * 0.4)
        return score, [], [], "No job description provided — scored lexical density only."

    jd_tokens = [t for t in _tokenize(job_description) if _is_skillish(t)]
    counts = Counter(jd_tokens)
    # Prefer distinctive JD skills over repeated boilerplate
    priority = [w for w, _ in counts.most_common(20)]
    bigrams = [p for p in _extract_phrases(job_description) if " " in p][:10]
    keywords = list(dict.fromkeys(priority + bigrams))[:25]
    if not keywords:
        keywords = list(dict.fromkeys(_tokenize(job_description)))[:20]

    cv_lower = cv_text.lower()
    matched = [k for k in keywords if k in cv_lower]
    missing = [k for k in keywords if k not in cv_lower]
    ratio = len(matched) / max(len(keywords), 1)
    # Soft curve: strong coverage maps into the high band (90+ achievable)
    score = round(min(100.0, 45.0 + ratio * 55.0), 1)
    detail = f"Matched {len(matched)} of {len(keywords)} priority job keywords."
    return score, matched[:40], missing[:25], detail


def _formatting_score(cv: GeneratedCV, cv_text: str) -> tuple[float, str, list[str]]:
    score = 100.0
    recs: list[str] = []
    # Contact completeness
    if not cv.contact.email:
        score -= 15
        recs.append("Add a professional email address.")
    if not cv.contact.phone:
        score -= 8
        recs.append("Add a phone number.")
    if not cv.contact.full_name:
        score -= 20
        recs.append("Include your full name in the header.")
    # Avoid tables/columns signals (we generate linear docs — reward clean structure)
    if re.search(r"\|{2,}|\t{2,}", cv_text):
        score -= 10
        recs.append("Avoid complex table/column layouts that confuse ATS parsers.")
    # Bullet quality
    bullets = [b for e in cv.experience for b in e.bullets] + [
        b for e in cv.internships for b in e.bullets
    ]
    if bullets:
        avg_len = sum(len(b.split()) for b in bullets) / len(bullets)
        if avg_len < 5:
            score -= 8
            recs.append("Expand short bullet points with concrete outcomes.")
        if avg_len > 40:
            score -= 5
            recs.append("Shorten overly long bullets for ATS readability.")
    else:
        if cv.experience:
            score -= 12
            recs.append("Use bullet points for work experience achievements.")
    # Special characters overload
    weird = len(re.findall(r"[★◆●■✓✔→←]|[^\x00-\x7F]", cv_text))
    if weird > 15:
        score -= 10
        recs.append("Reduce decorative symbols/emojis that break ATS parsing.")
    score = max(0.0, min(100.0, score))
    detail = "Evaluated contact fields, linear structure, bullet quality, and symbol usage."
    return score, detail, recs


def _skills_score(cv: GeneratedCV, job_description: str) -> tuple[float, str, list[str]]:
    skills = [s.strip().lower() for s in cv.skills if s.strip()]
    recs: list[str] = []
    if not skills:
        return 25.0, "No skills section detected.", ["Add a dedicated skills section with relevant keywords."]

    base = min(100.0, 40.0 + len(skills) * 4.0)
    if job_description.strip():
        jd_tokens = set(_tokenize(job_description))
        hits = sum(1 for s in skills if any(tok in s or s in tok for tok in jd_tokens) or s in job_description.lower())
        ratio = hits / max(len(skills), 1)
        score = round(min(100.0, base * 0.4 + ratio * 100 * 0.6), 1)
        if ratio < 0.4:
            recs.append("Align listed skills more closely with the job description keywords.")
        detail = f"{hits}/{len(skills)} listed skills overlap with the job description."
    else:
        score = round(base, 1)
        detail = f"{len(skills)} skills listed; provide a job description for relevance scoring."
    if len(skills) < 5:
        recs.append("List at least 5–12 relevant hard skills.")
    return score, detail, recs


def _experience_score(cv: GeneratedCV, job_description: str) -> tuple[float, str, list[str]]:
    roles = cv.experience + cv.internships
    recs: list[str] = []
    if not roles:
        return 20.0, "No work experience or internships found.", [
            "Add relevant work experience or internships with measurable achievements."
        ]

    score = min(75.0, 35.0 + len(roles) * 14.0)
    quantified = 0
    action = 0
    action_verbs = {
        "led", "built", "designed", "developed", "implemented", "managed", "created",
        "improved", "increased", "reduced", "optimized", "delivered", "launched",
        "owned", "architected", "automated", "analyzed", "collaborated", "achieved",
    }
    for role in roles:
        texts = role.bullets or ([role.description] if role.description else [])
        for t in texts:
            if re.search(r"\d|%|\$", t):
                quantified += 1
            first = (t.strip().split() or [""])[0].lower().rstrip(",.")
            if first in action_verbs:
                action += 1
    total_bullets = max(sum(len(r.bullets) or (1 if r.description else 0) for r in roles), 1)
    score += min(15.0, (quantified / total_bullets) * 15)
    score += min(10.0, (action / total_bullets) * 10)

    if job_description.strip():
        jd = job_description.lower()
        title_hits = sum(1 for r in roles if r.title and r.title.lower() in jd)
        if title_hits:
            score = min(100.0, score + 8)
        exp_text = " ".join(
            " ".join([r.title, r.company, r.description, *r.bullets]) for r in roles
        ).lower()
        jd_toks = set(_tokenize(job_description))
        overlap = len(jd_toks & set(_tokenize(exp_text))) / max(len(jd_toks), 1)
        score = min(100.0, score + overlap * 18)
        if overlap < 0.15 and not title_hits:
            recs.append("Tailor experience bullets to mirror language from the job posting.")

    if quantified / total_bullets < 0.3:
        recs.append("Add metrics (%, $, time saved) to more achievement bullets.")
    if action / total_bullets < 0.4:
        recs.append("Start bullets with strong action verbs.")

    score = round(max(0.0, min(100.0, score)), 1)
    detail = (
        f"{len(roles)} roles; {quantified}/{total_bullets} quantified bullets; "
        f"{action}/{total_bullets} action-led bullets."
    )
    return score, detail, recs


def _completeness_score(cv: GeneratedCV) -> tuple[float, str, list[str]]:
    checks = {
        "Contact name": bool(cv.contact.full_name),
        "Email": bool(cv.contact.email),
        "Professional summary": bool(cv.professional_summary.strip()),
        "Skills": bool(cv.skills),
        "Experience or internships": bool(cv.experience or cv.internships),
        "Education": bool(cv.education),
        "Projects or certifications": bool(cv.projects or cv.certifications),
    }
    present = sum(1 for v in checks.values() if v)
    score = round(100.0 * present / len(checks), 1)
    missing = [k for k, v in checks.items() if not v]
    recs = [f"Add a {m.lower()} section." for m in missing]
    detail = f"{present}/{len(checks)} core sections present."
    return score, detail, recs


def analyze_ats(cv: GeneratedCV, job_description: str = "") -> ATSResult:
    cv_text = _cv_to_text(cv)

    kw_score, matched, missing, kw_detail = _keyword_score(cv_text, job_description)
    fmt_score, fmt_detail, fmt_recs = _formatting_score(cv, cv_text)
    sk_score, sk_detail, sk_recs = _skills_score(cv, job_description)
    exp_score, exp_detail, exp_recs = _experience_score(cv, job_description)
    comp_score, comp_detail, comp_recs = _completeness_score(cv)

    overall = round(
        kw_score * SECTION_WEIGHTS["keyword"]
        + fmt_score * SECTION_WEIGHTS["formatting"]
        + sk_score * SECTION_WEIGHTS["skills"]
        + exp_score * SECTION_WEIGHTS["experience"]
        + comp_score * SECTION_WEIGHTS["completeness"],
        1,
    )

    sections = [
        SectionScore(
            name="Keyword Matching",
            score=kw_score,
            max_score=100,
            details=kw_detail,
            recommendations=[f"Consider adding missing keyword: {m}" for m in missing[:8]],
        ),
        SectionScore(
            name="Formatting & Parsing",
            score=fmt_score,
            max_score=100,
            details=fmt_detail,
            recommendations=fmt_recs,
        ),
        SectionScore(
            name="Skills Relevance",
            score=sk_score,
            max_score=100,
            details=sk_detail,
            recommendations=sk_recs,
        ),
        SectionScore(
            name="Experience Relevance",
            score=exp_score,
            max_score=100,
            details=exp_detail,
            recommendations=exp_recs,
        ),
        SectionScore(
            name="Section Completeness",
            score=comp_score,
            max_score=100,
            details=comp_detail,
            recommendations=comp_recs,
        ),
    ]

    recommendations: list[str] = []
    for s in sections:
        recommendations.extend(s.recommendations)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_recs: list[str] = []
    for r in recommendations:
        if r not in seen:
            seen.add(r)
            unique_recs.append(r)

    if overall < 90:
        unique_recs.insert(
            0,
            "Target 90+: tighten keyword coverage, quantify achievements, and complete all core sections.",
        )

    return ATSResult(
        overall_score=overall,
        keyword_score=kw_score,
        formatting_score=fmt_score,
        skills_score=sk_score,
        experience_score=exp_score,
        completeness_score=comp_score,
        matched_keywords=matched,
        missing_keywords=missing,
        section_scores=sections,
        recommendations=unique_recs[:12],
    )


def analyze_raw_text_as_cv(raw_text: str, job_description: str = "") -> ATSResult:
    """Lightweight ATS on raw uploaded text before structured parsing completes."""
    pseudo = GeneratedCV(
        professional_summary=raw_text[:800],
        skills=_tokenize(raw_text)[:20],
    )
    # Heuristic contact
    email = re.search(r"[\w.\-+]+@[\w.\-]+\.\w+", raw_text or "")
    phone = re.search(r"(\+?\d[\d\-\s().]{7,}\d)", raw_text or "")
    if email:
        pseudo.contact.email = email.group(0)
    if phone:
        pseudo.contact.phone = phone.group(0)
    lines = [ln.strip() for ln in (raw_text or "").splitlines() if ln.strip()]
    if lines:
        pseudo.contact.full_name = lines[0][:80]
    return analyze_ats(pseudo, job_description)
