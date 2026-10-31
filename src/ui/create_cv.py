"""Create CV from scratch workflow."""

from __future__ import annotations

import streamlit as st

from src.ats_analyzer import analyze_ats
from src.cv_generator import generate_cv_and_cover_letter, regenerate_section
from src.openai_client import safe_error_message
from src.schemas import (
    CertificationEntry,
    ContactInfo,
    CVProfile,
    EducationEntry,
    ExperienceEntry,
    JobTarget,
    LanguageEntry,
    ProjectEntry,
)
from src.ui.preview_export import render_preview_and_export
from src.ui.ats_view import render_ats_panel


def _ensure_list_state(key: str, default_n: int = 1) -> None:
    if key not in st.session_state:
        st.session_state[key] = default_n


def render_create_cv() -> None:
    st.markdown("### Create CV from Scratch")
    st.caption("Enter your details. AI will polish and tailor — never invent — your experience.")

    with st.expander("Personal & contact", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full name*", key="c_full_name")
            email = st.text_input("Email*", key="c_email")
            phone = st.text_input("Phone", key="c_phone")
            location = st.text_input("Location", key="c_location")
        with c2:
            linkedin = st.text_input("LinkedIn URL", key="c_linkedin")
            github = st.text_input("GitHub URL", key="c_github")
            portfolio = st.text_input("Portfolio URL", key="c_portfolio")
            website = st.text_input("Website", key="c_website")

    with st.expander("Professional summary", expanded=True):
        summary = st.text_area(
            "Summary / about you",
            height=120,
            placeholder="Brief overview of your background, strengths, and goals…",
            key="c_summary",
        )

    with st.expander("Target role (recommended)", expanded=True):
        t1, t2 = st.columns(2)
        with t1:
            job_title = st.text_input("Target job title", key="c_job_title")
        with t2:
            company = st.text_input("Target company", key="c_company")
        job_description = st.text_area(
            "Job description",
            height=140,
            placeholder="Paste the job posting for stronger keyword tailoring…",
            key="c_job_desc",
        )

    # Education
    _ensure_list_state("c_edu_n", 1)
    with st.expander("Education", expanded=True):
        education: list[EducationEntry] = []
        for i in range(st.session_state.c_edu_n):
            st.markdown(f"**Education #{i + 1}**")
            e1, e2 = st.columns(2)
            with e1:
                institution = st.text_input("Institution", key=f"c_edu_inst_{i}")
                degree = st.text_input("Degree", key=f"c_edu_deg_{i}")
                field = st.text_input("Field of study", key=f"c_edu_field_{i}")
            with e2:
                start = st.text_input("Start date", key=f"c_edu_start_{i}")
                end = st.text_input("End date", key=f"c_edu_end_{i}")
                gpa = st.text_input("GPA (optional)", key=f"c_edu_gpa_{i}")
            details = st.text_input("Details / coursework / honors", key=f"c_edu_det_{i}")
            if institution or degree:
                education.append(
                    EducationEntry(
                        institution=institution,
                        degree=degree,
                        field=field,
                        start_date=start,
                        end_date=end,
                        gpa=gpa,
                        details=details,
                    )
                )
        b1, b2, _ = st.columns([1, 1, 3])
        if b1.button("Add education", key="c_add_edu"):
            st.session_state.c_edu_n += 1
            st.rerun()
        if b2.button("Remove last", key="c_rm_edu") and st.session_state.c_edu_n > 1:
            st.session_state.c_edu_n -= 1
            st.rerun()

    # Experience
    _ensure_list_state("c_exp_n", 1)
    with st.expander("Work experience", expanded=True):
        experience: list[ExperienceEntry] = []
        for i in range(st.session_state.c_exp_n):
            st.markdown(f"**Role #{i + 1}**")
            e1, e2 = st.columns(2)
            with e1:
                company_e = st.text_input("Company", key=f"c_exp_co_{i}")
                title = st.text_input("Title", key=f"c_exp_title_{i}")
                loc = st.text_input("Location", key=f"c_exp_loc_{i}")
            with e2:
                start = st.text_input("Start date", key=f"c_exp_start_{i}")
                end = st.text_input("End date", key=f"c_exp_end_{i}")
            bullets_raw = st.text_area(
                "Achievements (one bullet per line)",
                height=100,
                key=f"c_exp_bullets_{i}",
            )
            bullets = [b.strip("•- ").strip() for b in bullets_raw.splitlines() if b.strip()]
            if company_e or title:
                experience.append(
                    ExperienceEntry(
                        company=company_e,
                        title=title,
                        location=loc,
                        start_date=start,
                        end_date=end,
                        bullets=bullets,
                    )
                )
        b1, b2, _ = st.columns([1, 1, 3])
        if b1.button("Add experience", key="c_add_exp"):
            st.session_state.c_exp_n += 1
            st.rerun()
        if b2.button("Remove last", key="c_rm_exp") and st.session_state.c_exp_n > 1:
            st.session_state.c_exp_n -= 1
            st.rerun()

    # Internships
    _ensure_list_state("c_int_n", 0)
    with st.expander("Internships", expanded=False):
        internships: list[ExperienceEntry] = []
        for i in range(st.session_state.c_int_n):
            st.markdown(f"**Internship #{i + 1}**")
            e1, e2 = st.columns(2)
            with e1:
                company_e = st.text_input("Company", key=f"c_int_co_{i}")
                title = st.text_input("Title", key=f"c_int_title_{i}")
            with e2:
                start = st.text_input("Start date", key=f"c_int_start_{i}")
                end = st.text_input("End date", key=f"c_int_end_{i}")
            bullets_raw = st.text_area("Bullets (one per line)", height=80, key=f"c_int_bullets_{i}")
            bullets = [b.strip("•- ").strip() for b in bullets_raw.splitlines() if b.strip()]
            if company_e or title:
                internships.append(
                    ExperienceEntry(
                        company=company_e, title=title, start_date=start, end_date=end, bullets=bullets
                    )
                )
        b1, b2, _ = st.columns([1, 1, 3])
        if b1.button("Add internship", key="c_add_int"):
            st.session_state.c_int_n += 1
            st.rerun()
        if b2.button("Remove last", key="c_rm_int") and st.session_state.c_int_n > 0:
            st.session_state.c_int_n -= 1
            st.rerun()

    # Projects
    _ensure_list_state("c_proj_n", 1)
    with st.expander("Projects", expanded=False):
        projects: list[ProjectEntry] = []
        for i in range(st.session_state.c_proj_n):
            st.markdown(f"**Project #{i + 1}**")
            name = st.text_input("Name", key=f"c_proj_name_{i}")
            tech = st.text_input("Technologies", key=f"c_proj_tech_{i}")
            url = st.text_input("URL", key=f"c_proj_url_{i}")
            bullets_raw = st.text_area("Highlights (one per line)", height=80, key=f"c_proj_bullets_{i}")
            bullets = [b.strip("•- ").strip() for b in bullets_raw.splitlines() if b.strip()]
            if name:
                projects.append(ProjectEntry(name=name, technologies=tech, url=url, bullets=bullets))
        b1, b2, _ = st.columns([1, 1, 3])
        if b1.button("Add project", key="c_add_proj"):
            st.session_state.c_proj_n += 1
            st.rerun()
        if b2.button("Remove last", key="c_rm_proj") and st.session_state.c_proj_n > 1:
            st.session_state.c_proj_n -= 1
            st.rerun()

    with st.expander("Skills, certifications, achievements, languages & links", expanded=True):
        skills_raw = st.text_area(
            "Skills (comma or newline separated)",
            height=80,
            key="c_skills",
        )
        skills = [s.strip() for s in skills_raw.replace("\n", ",").split(",") if s.strip()]

        _ensure_list_state("c_cert_n", 0)
        certifications: list[CertificationEntry] = []
        st.markdown("**Certifications**")
        for i in range(st.session_state.c_cert_n):
            c1, c2, c3 = st.columns(3)
            with c1:
                n = st.text_input("Name", key=f"c_cert_name_{i}")
            with c2:
                issuer = st.text_input("Issuer", key=f"c_cert_iss_{i}")
            with c3:
                date = st.text_input("Date", key=f"c_cert_date_{i}")
            if n:
                certifications.append(CertificationEntry(name=n, issuer=issuer, date=date))
        cb1, cb2, _ = st.columns([1, 1, 3])
        if cb1.button("Add certification", key="c_add_cert"):
            st.session_state.c_cert_n += 1
            st.rerun()
        if cb2.button("Remove last cert", key="c_rm_cert") and st.session_state.c_cert_n > 0:
            st.session_state.c_cert_n -= 1
            st.rerun()

        achievements_raw = st.text_area("Achievements (one per line)", height=80, key="c_achievements")
        achievements = [a.strip("•- ").strip() for a in achievements_raw.splitlines() if a.strip()]

        _ensure_list_state("c_lang_n", 0)
        languages: list[LanguageEntry] = []
        st.markdown("**Languages**")
        for i in range(st.session_state.c_lang_n):
            l1, l2 = st.columns(2)
            with l1:
                lang = st.text_input("Language", key=f"c_lang_{i}")
            with l2:
                prof = st.selectbox(
                    "Proficiency",
                    ["Native", "Fluent", "Professional", "Intermediate", "Basic"],
                    key=f"c_lang_prof_{i}",
                )
            if lang:
                languages.append(LanguageEntry(language=lang, proficiency=prof))
        lb1, lb2, _ = st.columns([1, 1, 3])
        if lb1.button("Add language", key="c_add_lang"):
            st.session_state.c_lang_n += 1
            st.rerun()
        if lb2.button("Remove last language", key="c_rm_lang") and st.session_state.c_lang_n > 0:
            st.session_state.c_lang_n -= 1
            st.rerun()

        links_raw = st.text_area("Portfolio / other links (one per line)", height=70, key="c_links")
        portfolio_links = [x.strip() for x in links_raw.splitlines() if x.strip()]

    template_id = st.selectbox(
        "Template",
        options=["classic", "modern", "minimal"],
        format_func=lambda x: {"classic": "Classic ATS", "modern": "Modern Violet", "minimal": "Minimal Clean"}[x],
        key="c_template",
    )

    generate = st.button("Generate CV & Cover Letter", type="primary", width="stretch")

    if generate:
        if not full_name.strip() or not email.strip():
            st.error("Full name and email are required.")
            return
        if not (experience or internships or education or projects or summary.strip()):
            st.error("Add at least a summary, education, experience, internship, or project.")
            return

        profile = CVProfile(
            contact=ContactInfo(
                full_name=full_name.strip(),
                email=email.strip(),
                phone=phone.strip(),
                location=location.strip(),
                linkedin=linkedin.strip(),
                github=github.strip(),
                portfolio=portfolio.strip(),
                website=website.strip(),
            ),
            professional_summary=summary.strip(),
            education=education,
            experience=experience,
            internships=internships,
            projects=projects,
            skills=skills,
            certifications=certifications,
            achievements=achievements,
            languages=languages,
            portfolio_links=portfolio_links,
            job_target=JobTarget(
                job_title=job_title.strip(),
                company=company.strip(),
                job_description=job_description.strip(),
            ),
        )
        st.session_state.create_profile = profile
        st.session_state.template_id = template_id

        with st.spinner("Generating tailored CV and cover letter with OpenAI…"):
            try:
                bundle = generate_cv_and_cover_letter(
                    st.session_state.api_key,
                    profile,
                    model=st.session_state.openai_model,
                    template_id=template_id,
                )
                st.session_state.generated_cv = bundle.cv
                st.session_state.generated_cover_letter = bundle.cover_letter
                st.session_state.ats_result = analyze_ats(
                    bundle.cv, profile.job_target.job_description
                )
                st.success("Generation complete. Review, edit, and export below.")
            except Exception as exc:  # noqa: BLE001
                st.error(safe_error_message(exc))
                return

    if st.session_state.generated_cv is not None:
        _render_edit_and_outputs()


def _render_edit_and_outputs() -> None:
    cv = st.session_state.generated_cv
    cl = st.session_state.generated_cover_letter
    profile = st.session_state.create_profile

    st.markdown("---")
    st.markdown("### Review & edit generated content")

    tab_cv, tab_cl, tab_ats, tab_export = st.tabs(
        ["CV content", "Cover letter", "ATS analysis", "Preview & export"]
    )

    with tab_cv:
        cv.professional_summary = st.text_area(
            "Professional summary", value=cv.professional_summary, height=120, key="edit_summary"
        )
        skills_text = st.text_area(
            "Skills (comma-separated)",
            value=", ".join(cv.skills),
            height=80,
            key="edit_skills",
        )
        cv.skills = [s.strip() for s in skills_text.split(",") if s.strip()]

        for i, exp in enumerate(cv.experience):
            with st.expander(f"Experience: {exp.title or 'Role'} @ {exp.company or 'Company'}", expanded=i == 0):
                exp.title = st.text_input("Title", value=exp.title, key=f"edit_exp_title_{i}")
                exp.company = st.text_input("Company", value=exp.company, key=f"edit_exp_co_{i}")
                bullets = st.text_area(
                    "Bullets",
                    value="\n".join(exp.bullets),
                    height=120,
                    key=f"edit_exp_bullets_{i}",
                )
                exp.bullets = [b.strip("•- ").strip() for b in bullets.splitlines() if b.strip()]

        if st.button("Regenerate summary only", key="regen_summary"):
            if profile is None:
                st.warning("Original profile missing; cannot regenerate.")
            else:
                with st.spinner("Regenerating summary…"):
                    try:
                        cv.professional_summary = regenerate_section(
                            st.session_state.api_key,
                            section_name="professional_summary",
                            current_content=cv.professional_summary,
                            profile=profile,
                            job_description=profile.job_target.job_description,
                            model=st.session_state.openai_model,
                        )
                        st.session_state.generated_cv = cv
                        st.rerun()
                    except Exception as exc:  # noqa: BLE001
                        st.error(safe_error_message(exc))

        if st.button("Re-run ATS analysis", key="rerun_ats_create"):
            jd = profile.job_target.job_description if profile else ""
            st.session_state.ats_result = analyze_ats(cv, jd)
            st.rerun()

        st.session_state.generated_cv = cv

    with tab_cl:
        if cl is None:
            st.info("No cover letter generated yet.")
        else:
            cl.greeting = st.text_input("Greeting", value=cl.greeting, key="edit_cl_greet")
            body = st.text_area(
                "Body paragraphs (separate with blank lines)",
                value="\n\n".join(cl.body_paragraphs),
                height=260,
                key="edit_cl_body",
            )
            cl.body_paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
            cl.closing = st.text_input("Closing", value=cl.closing, key="edit_cl_close")
            cl.signature_name = st.text_input(
                "Signature name", value=cl.signature_name, key="edit_cl_sig"
            )
            st.session_state.generated_cover_letter = cl

            if st.button("Regenerate cover letter body", key="regen_cl") and profile is not None:
                with st.spinner("Regenerating cover letter…"):
                    try:
                        new_body = regenerate_section(
                            st.session_state.api_key,
                            section_name="cover_letter_body",
                            current_content="\n\n".join(cl.body_paragraphs),
                            profile=profile,
                            job_description=profile.job_target.job_description,
                            model=st.session_state.openai_model,
                        )
                        cl.body_paragraphs = [p.strip() for p in new_body.split("\n\n") if p.strip()]
                        st.session_state.generated_cover_letter = cl
                        st.rerun()
                    except Exception as exc:  # noqa: BLE001
                        st.error(safe_error_message(exc))

    with tab_ats:
        if st.session_state.ats_result:
            render_ats_panel(st.session_state.ats_result)
        else:
            st.info("Generate a CV to see ATS analysis.")

    with tab_export:
        render_preview_and_export(
            st.session_state.generated_cv,
            st.session_state.generated_cover_letter,
            st.session_state.get("template_id", "classic"),
        )
