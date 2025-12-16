import streamlit as st
from streamlit_local_storage import LocalStorage
from io import BytesIO
import json

# Initialize local storage
local_storage = LocalStorage()

# Page config
st.set_page_config(
    page_title="SkillGapAI - Resume Generator",
    layout="wide"
)

# Apply styling similar to SkillGap AI page
st.markdown("""
<style>
    .card-title {
        color: #f8fafc;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #334155;
    }
    .card-title-resume {
        border-bottom-color: #be123c;
    }
    .card-title-job {
        border-bottom-color: #ea580c;
    }
    /* Colorful section separators */
    h3 {
        border-bottom: 2px solid;
        padding-bottom: 0.5rem !important;
        margin-bottom: 1.2rem !important;
        margin-top: 1rem !important;
    }
    /* Add spacing after h3 before expanders */
    h3 + div[data-testid="stExpander"] {
        margin-top: 0.5rem !important;
    }
    h3.section-personal {
        border-bottom-color: #be123c !important;
    }
    h3.section-summary {
        border-bottom-color: #f43f5e !important;
    }
    h3.section-education {
        border-bottom-color: #ea580c !important;
    }
    h3.section-skills {
        border-bottom-color: #eab308 !important;
    }
    h3.section-experience {
        border-bottom-color: #22c55e !important;
    }
    h3.section-projects {
        border-bottom-color: #3b82f6 !important;
    }
    h3.section-certifications {
        border-bottom-color: #8b5cf6 !important;
    }
    h3.section-achievements {
        border-bottom-color: #ec4899 !important;
    }
    h3.section-preview {
        border-bottom-color: #ea580c !important;
    }
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #0f172a;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #1e293b;
    }
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #334155;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #be123c 0%, #f43f5e 100%);
        color: #fafafa;
        font-size: 1rem;
        font-weight: 700;
        padding: 0.6rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(190, 18, 60, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(190, 18, 60, 0.5);
    }
    /* Ensure download buttons match regular buttons */
    div[data-testid="stDownloadButton"] > button[kind="primary"],
    div.stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #be123c 0%, #f43f5e 100%) !important;
        color: #fafafa !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        padding: 0.6rem 2rem !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(190, 18, 60, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stDownloadButton"] > button[kind="primary"]:hover,
    div.stDownloadButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(190, 18, 60, 0.5) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: #1e293b;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: #334155;
        border-color: #475569;
    }
    .stExpander {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
    }
    .stExpander > div > div {
        background: #0f172a;
    }
    h1, h2, h3 {
        color: #f8fafc;
    }
    .preview-container {
        background: #0f172a;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with default values
def get_default_resume_data():
    return {
        "full_name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "portfolio": "",
        "github": "",
        "summary": "",
        "experiences": [],
        "education": [],
        "projects": [],
        "skills": [],
        "certifications": [],
        "achievements": []
    }

def load_from_local_storage():
    """Load resume data from localStorage"""
    try:
        stored_data = local_storage.getItem("resume_data")
        if stored_data:
            return json.loads(stored_data)
    except:
        pass
    return None

def save_to_local_storage(data):
    """Save resume data to localStorage"""
    try:
        local_storage.setItem("resume_data", json.dumps(data))
    except:
        pass

def initialize_session_state():
    """Initialize session state from localStorage or defaults"""
    if "initialized" not in st.session_state:
        stored_data = load_from_local_storage()
        if stored_data:
            for key, value in stored_data.items():
                st.session_state[key] = value
        else:
            defaults = get_default_resume_data()
            for key, value in defaults.items():
                st.session_state[key] = value
        # Backwards compatibility for old certifications format (string -> list)
        certs = st.session_state.get("certifications", [])
        if isinstance(certs, str):
            if certs.strip():
                st.session_state.certifications = [{
                    "name": certs.strip(),
                    "authority": "",
                    "link": ""
                }]
            else:
                st.session_state.certifications = []
        # Backwards compatibility: migrate languages -> achievements if present
        if "achievements" not in st.session_state or not st.session_state.achievements:
            langs = st.session_state.get("languages", "")
            if isinstance(langs, str) and langs.strip():
                st.session_state.achievements = [line.strip() for line in langs.splitlines() if line.strip()]
            elif isinstance(st.session_state.get("achievements"), str):
                ach = st.session_state.get("achievements", "").strip()
                st.session_state.achievements = [line.strip() for line in ach.splitlines() if line.strip()] if ach else []
        # Ensure projects have technologies field
        projects = st.session_state.get("projects", [])
        if isinstance(projects, list):
            for proj in projects:
                if isinstance(proj, dict) and "technologies" not in proj:
                    proj["technologies"] = ""
        # Ensure experiences have location field
        experiences = st.session_state.get("experiences", [])
        if isinstance(experiences, list):
            for exp in experiences:
                if isinstance(exp, dict) and "location" not in exp:
                    exp["location"] = ""
        # Backwards compatibility for old skills format (string -> list)
        skills_state = st.session_state.get("skills", [])
        if isinstance(skills_state, str):
            skills_text = skills_state or ""
            skill_items = []
            for line in skills_text.splitlines():
                for part in line.split(","):
                    part = part.strip()
                    if part:
                        skill_items.append(part)
            st.session_state.skills = skill_items
        st.session_state.initialized = True

def save_current_state():
    """Save current session state to localStorage"""
    data = {
        "full_name": st.session_state.get("full_name", ""),
        "email": st.session_state.get("email", ""),
        "phone": st.session_state.get("phone", ""),
        "location": st.session_state.get("location", ""),
        "linkedin": st.session_state.get("linkedin", ""),
        "portfolio": st.session_state.get("portfolio", ""),
        "github": st.session_state.get("github", ""),
        "summary": st.session_state.get("summary", ""),
        "experiences": st.session_state.get("experiences", []),
        "education": st.session_state.get("education", []),
        "projects": st.session_state.get("projects", []),
        "skills": st.session_state.get("skills", []),
        "certifications": st.session_state.get("certifications", []),
        "achievements": st.session_state.get("achievements", [])
    }
    save_to_local_storage(data)

def build_resume_html() -> str:
    css = """
    <style>
        @page {
            size: A4;
            margin: 40px 0 40px 0;
        }
        @page :first {
            margin-top: 0;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        html, body {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
        }
        .preview-window {
            background-color: #ffffff;
            border: none;
            border-radius: 0;
            padding: 40px 40px 60px 40px;
            width: 100%;
            height: 100%;
            margin: 0;
            overflow: hidden;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        }
        .resume-name {
            font-size: 34px;
            font-weight: bold;
            color: #000000;
            margin-bottom: 4px;
            text-align: center;
            letter-spacing: 3px;
        }
        .resume-contact {
            font-size: 14px;
            color: #000000;
            text-align: center;
            margin-bottom: 14px;
        }
        .resume-section-title {
            font-size: 14px;
            font-weight: bold;
            color: #000000;
            text-transform: uppercase;
            letter-spacing: 2px;
            border-bottom: 1px solid #000000;
            padding-bottom: 3px;
            margin-top: 18px;
            margin-bottom: 6px;
        }
        .resume-section-title.projects-section {
            margin-top: 28px;
        }
        .resume-content {
            font-size: 14px;
            color: #000000;
            line-height: 1.5;
        }
        .experience-title {
            font-weight: bold;
            color: #000000;
        }
        .experience-company {
            color: #000000;
            font-style: italic;
        }
        .experience-date {
            color: #000000;
            font-size: 13px;
            float: right;
        }
        .experience-location {
            color: #000000;
            font-size: 13px;
            float: right;
        }
        .experience-entry {
            margin-top: 12px;
        }
        .project-entry {
            margin-top: 12px;
        }
    </style>
    """

    html_parts = ["<html><head>", css, "</head><body>", '<div class="preview-window">']

    # Header - Name
    name = st.session_state.get("full_name", "") or "[Your Name]"
    html_parts.append(f'<div class="resume-name">{name}</div>')

    # Single-line contact info + links
    contact_parts = []
    if st.session_state.get("email"):
        contact_parts.append(st.session_state.email)
    if st.session_state.get("phone"):
        contact_parts.append(st.session_state.phone)
    if st.session_state.get("location"):
        contact_parts.append(st.session_state.location)
    if st.session_state.get("linkedin"):
        contact_parts.append(f'<a href="{st.session_state.linkedin}" target="_blank">LinkedIn</a>')
    if st.session_state.get("portfolio"):
        contact_parts.append(f'<a href="{st.session_state.portfolio}" target="_blank">Portfolio</a>')
    if st.session_state.get("github"):
        contact_parts.append(f'<a href="{st.session_state.github}" target="_blank">GitHub</a>')

    if contact_parts:
        html_parts.append(f'<div class="resume-contact">{" | ".join(contact_parts)}</div>')

    # Summary
    if st.session_state.get("summary"):
        html_parts.append('<div class="resume-section-title">Professional Summary</div>')
        summary_html = st.session_state.summary.replace("\n", "<br>")
        html_parts.append(f'<div class="resume-content">{summary_html}</div>')

    # Education
    if st.session_state.get("education"):
        html_parts.append('<div class="resume-section-title">Education</div>')
        for edu in st.session_state.education:
            period = f"{edu['start_year']} - {edu['end_year']}"
            html_parts.append(
                f'''
                <div class="resume-content">
                    <span class="experience-title">{edu['degree']}</span>
                    <span class="experience-date">{period}</span><br>
                    <span class="experience-company">{edu['institution']}</span>
                </div>
                '''
            )
            if edu.get("gpa"):
                html_parts.append(f'<div class="resume-content">GPA: {edu["gpa"]}</div>')

    # Skills
    skills_state = st.session_state.get("skills")
    if skills_state:
        html_parts.append('<div class="resume-section-title">Skills</div>')
        if isinstance(skills_state, str):
            skills_text = skills_state or ""
            skill_items = []
            for line in skills_text.splitlines():
                for part in line.split(","):
                    part = part.strip()
                    if part:
                        skill_items.append(part)
            if not skill_items and skills_text.strip():
                skill_items = [skills_text.strip()]
        else:
            skill_items = list(skills_state)
        for sk in skill_items:
            html_parts.append(f'<div class="resume-content">• {sk}</div>')

    # Experience
    if st.session_state.get("experiences"):
        html_parts.append('<div class="resume-section-title">Work Experience</div>')
        for idx, exp in enumerate(st.session_state.experiences):
            desc_html = (exp.get("description") or "").replace("\n", "<br>")
            period = f"{exp['start_date']} - {exp['end_date']}"
            entry_class = "experience-entry" if idx > 0 else ""
            html_parts.append(f'<div class="{entry_class}">')
            location_html = f'<span class="experience-location">{exp.get("location", "")}</span>' if exp.get("location") else ""
            html_parts.append(
                f'''
                <div class="resume-content">
                    <span class="experience-title">{exp['job_title']}</span>
                    <span class="experience-date">{period}</span><br>
                    <span class="experience-company">{exp['company']}</span>
                    {location_html}
                </div>
                '''
            )
            if desc_html:
                html_parts.append(f'<div class="resume-content">{desc_html}</div>')
            html_parts.append('</div>')

    # Projects / Open-Source
    if st.session_state.get("projects"):
        html_parts.append('<div class="resume-section-title projects-section">Projects / Open-Source</div>')
        for idx, proj in enumerate(st.session_state.projects):
            desc_html = (proj.get("description") or "").replace("\n", "<br>")
            links_line_parts = []
            if proj.get("live_link"):
                links_line_parts.append(f'<a href="{proj["live_link"]}" target="_blank">Live</a>')
            if proj.get("source_code"):
                links_line_parts.append(f'<a href="{proj["source_code"]}" target="_blank">Source</a>')
            links_line = " | ".join(links_line_parts)
            entry_class = "project-entry" if idx > 0 else ""
            html_parts.append(f'<div class="{entry_class}">')
            html_parts.append('<div class="resume-content">')
            html_parts.append(f'<span class="experience-title">{proj.get("name", "")}</span>')
            if links_line:
                html_parts.append(f' &nbsp; <span class="experience-company">{links_line}</span>')
            if proj.get("technologies"):
                html_parts.append(f'<br><span class="experience-company">Technologies: {proj["technologies"]}</span>')
            if desc_html:
                html_parts.append(f'<br><div>{desc_html}</div>')
            html_parts.append('</div>')
            html_parts.append('</div>')

    # Certifications
    certs_state = st.session_state.get("certifications")
    if certs_state:
        html_parts.append('<div class="resume-section-title">Certifications</div>')
        if isinstance(certs_state, str):
            certs = certs_state.replace("\n", "<br>")
            html_parts.append(f'<div class="resume-content">{certs}</div>')
        else:
            for cert in certs_state:
                line = cert.get("name", "")
                if cert.get("authority"):
                    line += f' - <span class="experience-company">{cert["authority"]}</span>'
                if cert.get("link"):
                    line += f' | <a href="{cert["link"]}" target="_blank">Verify</a>'
                html_parts.append(f'<div class="resume-content">• {line}</div>')

    # Achievements
    ach_state = st.session_state.get("achievements")
    if ach_state:
        html_parts.append('<div class="resume-section-title">Achievements</div>')
        if isinstance(ach_state, str):
            ach_html = ach_state.replace("\n", "<br>")
            html_parts.append(f'<div class="resume-content">{ach_html}</div>')
        else:
            for ach in ach_state:
                html_parts.append(f'<div class="resume-content">• {ach}</div>')

    html_parts.append("</div></body></html>")
    return "".join(html_parts)


def generate_pdf_from_html(html: str) -> BytesIO:
    """Generate PDF from HTML using WeasyPrint"""
    import sys
    import os
    
    # Add GTK+ bin directory to DLL search path on Windows
    if sys.platform == "win32":
        gtk_bin = r"D:\Program Files\GTK3-Runtime Win64\bin"
        if os.path.exists(gtk_bin) and hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(gtk_bin)
            except Exception:
                pass
    
    try:
        from weasyprint import HTML
    except OSError as e:
        st.error(f"Failed to load WeasyPrint: {e}. Please ensure GTK+ runtime is properly installed and in your system PATH.")
        raise
    buffer = BytesIO()
    HTML(string=html).write_pdf(buffer)
    buffer.seek(0)
    return buffer

# Initialize
initialize_session_state()

# Title
st.markdown('<h1 style="text-align: center;">Resume Generator</h1>', unsafe_allow_html=True)
st.markdown('---')

# Create two columns: Form and Preview
col_form, col_preview = st.columns([1, 1])

# ==================== FORM SECTION ====================
with col_form:
    with st.container(border=True):
        # Personal Information Section
        st.markdown('<h3 class="section-personal">Personal Information</h3>', unsafe_allow_html=True)
        
        # Personal info inputs (use standard text_input, auto-save on change)
        st.text_input(
            "Full Name",
            key="full_name",
            on_change=save_current_state
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "Email",
                key="email",
                on_change=save_current_state
            )
        with col2:
            st.text_input(
                "Phone",
                key="phone",
                on_change=save_current_state
            )
        
        col3, col4 = st.columns(2)
        with col3:
            st.text_input(
                "Location",
                key="location",
                on_change=save_current_state
            )
        with col4:
            st.text_input(
                "LinkedIn URL",
                key="linkedin",
                on_change=save_current_state
            )

        col5, col6 = st.columns(2)
        with col5:
            st.text_input(
                "Portfolio/Website",
                key="portfolio",
                on_change=save_current_state
            )
        with col6:
            st.text_input(
                "GitHub URL",
                key="github",
                on_change=save_current_state
            )
        
        # Professional Summary
        st.markdown('<h3 class="section-summary">Professional Summary</h3>', unsafe_allow_html=True)
        st.text_area(
            "Summary",
            height=100,
            key="summary",
            placeholder="Write a brief professional summary...",
            on_change=save_current_state
        )
        
        # Education Section
        st.markdown('<h3 class="section-education">Education</h3>', unsafe_allow_html=True)
        
        if "education" not in st.session_state:
            st.session_state.education = []
        
        with st.expander("Add Education", expanded=len(st.session_state.education) == 0):
            new_degree = st.text_input("Degree", key="new_degree")
            new_institution = st.text_input("Institution", key="new_institution")
            edu_col1, edu_col2, edu_col3 = st.columns(3)
            with edu_col1:
                new_edu_start = st.text_input("Start", placeholder="MM/YYYY or Year", key="new_edu_start")
            with edu_col2:
                new_edu_end = st.text_input("End", placeholder="MM/YYYY, Year or Present", key="new_edu_end")
            with edu_col3:
                new_gpa = st.text_input("GPA (optional)", key="new_gpa")
            
            if st.button("Add Education", type="primary", key="add_edu_btn"):
                if new_degree and new_institution:
                    st.session_state.education.append({
                        "degree": new_degree,
                        "institution": new_institution,
                        "start_year": new_edu_start,
                        "end_year": new_edu_end,
                        "gpa": new_gpa
                    })
                    save_current_state()
                    st.rerun()
        
        # Display existing education
        for idx, edu in enumerate(st.session_state.education):
            with st.expander(f"{edu['degree']} - {edu['institution']}", expanded=False):
                period = f"{edu['start_year']} - {edu['end_year']}"
                line = f"{edu['degree']} at {edu['institution']} ({period})"
                st.write(line)
                if edu.get('gpa'):
                    st.write(f"GPA: {edu['gpa']}")
                if st.button(f"Remove", key=f"remove_edu_{idx}"):
                    st.session_state.education.pop(idx)
                    save_current_state()
                    st.rerun()

        # Skills Section
        st.markdown('<h3 class="section-skills">Skills</h3>', unsafe_allow_html=True)

        if "skills" not in st.session_state or isinstance(st.session_state.skills, str):
            skills_state = st.session_state.get("skills", [])
            if isinstance(skills_state, str) and skills_state.strip():
                skill_items = []
                for line in skills_state.splitlines():
                    for part in line.split(","):
                        part = part.strip()
                        if part:
                            skill_items.append(part)
                st.session_state.skills = skill_items
            elif not isinstance(skills_state, list):
                st.session_state.skills = []

        # Add new skill section
        with st.expander("Add New Skill Section", expanded=len(st.session_state.skills) == 0):
            new_skill = st.text_input("Skill", key="new_skill")

            if st.button("Add Skill", type="primary"):
                if new_skill.strip():
                    st.session_state.skills.append(new_skill.strip())
                    save_current_state()
                    st.rerun()

        # Display existing skills
        for idx, sk in enumerate(st.session_state.skills):
            with st.expander(sk or f"Skill {idx + 1}", expanded=False):
                st.write(sk)
                if st.button("Remove", key=f"remove_skill_{idx}"):
                    st.session_state.skills.pop(idx)
                    save_current_state()
                    st.rerun()
        # Work Experience Section
        st.markdown('<h3 class="section-experience">Work Experience</h3>', unsafe_allow_html=True)
        
        # Experience management
        if "experiences" not in st.session_state:
            st.session_state.experiences = []
        
        # Add new experience
        with st.expander("Add New Experience", expanded=len(st.session_state.experiences) == 0):
            new_job_title = st.text_input("Job Title", key="new_job_title")
            new_company = st.text_input("Company", key="new_company")
            new_location = st.text_input("Location (optional)", key="new_location")
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                new_start_date = st.text_input("Start Date", placeholder="MM/YYYY", key="new_start_date")
            with exp_col2:
                new_end_date = st.text_input("End Date", placeholder="MM/YYYY or Present", key="new_end_date")
            new_exp_description = st.text_area(
                "Description",
                placeholder="Describe your responsibilities and achievements...",
                key="new_exp_description"
            )
            
            if st.button("Add Experience", type="primary"):
                if new_job_title and new_company:
                    st.session_state.experiences.append({
                        "job_title": new_job_title,
                        "company": new_company,
                        "location": new_location,
                        "start_date": new_start_date,
                        "end_date": new_end_date,
                        "description": new_exp_description
                    })
                    save_current_state()
                    st.rerun()
        
        # Display existing experiences
        for idx, exp in enumerate(st.session_state.experiences):
            with st.expander(f"{exp['job_title']} at {exp['company']}", expanded=False):
                st.write(f"Period: {exp['start_date']} - {exp['end_date']}")
                if exp.get('location'):
                    st.write(f"Location: {exp['location']}")
                st.write(f"Description: {exp['description']}")
                if st.button(f"Remove", key=f"remove_exp_{idx}"):
                    st.session_state.experiences.pop(idx)
                    save_current_state()
                    st.rerun()
        
        # Projects / Open-Source Section
        st.markdown('<h3 class="section-projects">Projects / Open-Source</h3>', unsafe_allow_html=True)

        if "projects" not in st.session_state:
            st.session_state.projects = []

        # Add new project
        with st.expander("Add New Project", expanded=len(st.session_state.projects) == 0):
            new_project_name = st.text_input("Project Name", key="new_project_name")
            new_project_tech = st.text_input("Technologies Used", key="new_project_technologies")
            new_project_live = st.text_input("Live Link (optional)", key="new_project_live")
            new_project_source = st.text_input("Source Code URL (optional)", key="new_project_source")
            new_project_description = st.text_area(
                "Description",
                placeholder="Describe what the project does and your contributions...",
                key="new_project_description"
            )

            if st.button("Add Project", type="primary"):
                if new_project_name:
                    st.session_state.projects.append({
                        "name": new_project_name,
                        "description": new_project_description,
                        "technologies": new_project_tech,
                        "live_link": new_project_live,
                        "source_code": new_project_source,
                    })
                    save_current_state()
                    st.rerun()

        # Display existing projects
        for idx, proj in enumerate(st.session_state.projects):
            with st.expander(proj.get("name") or f"Project {idx + 1}", expanded=False):
                if proj.get("technologies"):
                    st.write(f"Technologies: {proj['technologies']}")
                if proj.get("live_link"):
                    st.write(f"Live: {proj['live_link']}")
                if proj.get("source_code"):
                    st.write(f"Source: {proj['source_code']}")
                if proj.get("description"):
                    st.write(f"Description: {proj['description']}")
                if st.button("Remove", key=f"remove_project_{idx}"):
                    st.session_state.projects.pop(idx)
                    save_current_state()
                    st.rerun()

        # Certifications Section
        st.markdown('<h3 class="section-certifications">Certifications</h3>', unsafe_allow_html=True)

        if "certifications" not in st.session_state or isinstance(st.session_state.certifications, str):
            # Normalize to list format
            existing_certs = st.session_state.get("certifications", [])
            if isinstance(existing_certs, str) and existing_certs.strip():
                st.session_state.certifications = [{
                    "name": existing_certs.strip(),
                    "authority": "",
                    "link": ""
                }]
            else:
                st.session_state.certifications = []

        # Add new certification
        with st.expander("Add New Certification", expanded=len(st.session_state.certifications) == 0):
            new_cert_name = st.text_input("Certification Name", key="new_cert_name")
            new_cert_authority = st.text_input("Issuing Authority", key="new_cert_authority")
            new_cert_link = st.text_input("Verification Link (optional)", key="new_cert_link")

            if st.button("Add Certification", type="primary"):
                if new_cert_name:
                    st.session_state.certifications.append({
                        "name": new_cert_name,
                        "authority": new_cert_authority,
                        "link": new_cert_link,
                    })
                    save_current_state()
                    st.rerun()

        # Display existing certifications
        for idx, cert in enumerate(st.session_state.certifications):
            title = cert["name"] or f"Certification {idx + 1}"
            with st.expander(title, expanded=False):
                if cert.get("authority"):
                    st.write(f"Issued by: {cert['authority']}")
                if cert.get("link"):
                    st.write(f"Link: {cert['link']}")
                if st.button("Remove", key=f"remove_cert_{idx}"):
                    st.session_state.certifications.pop(idx)
                    save_current_state()
                    st.rerun()
        
        # Achievements Section
        st.markdown('<h3 class="section-achievements">Achievements</h3>', unsafe_allow_html=True)

        if "achievements" not in st.session_state or isinstance(st.session_state.achievements, str):
            ach = st.session_state.get("achievements", "")
            if isinstance(ach, str) and ach.strip():
                st.session_state.achievements = [line.strip() for line in ach.splitlines() if line.strip()]
            else:
                st.session_state.achievements = []

        # Add new achievement
        with st.expander("Add New Achievement", expanded=len(st.session_state.achievements) == 0):
            new_achievement = st.text_input("Achievement", key="new_achievement")

            if st.button("Add Achievement", type="primary"):
                if new_achievement.strip():
                    st.session_state.achievements.append(new_achievement.strip())
                    save_current_state()
                    st.rerun()

        # Display existing achievements
        for idx, ach in enumerate(st.session_state.achievements):
            with st.expander(ach or f"Achievement {idx + 1}", expanded=False):
                st.write(ach)
                if st.button("Remove", key=f"remove_achievement_{idx}"):
                    st.session_state.achievements.pop(idx)
                    save_current_state()
                    st.rerun()

# ==================== PREVIEW SECTION ====================
with col_preview:
    with st.container(border=True):
        st.markdown('<h3 class="section-preview">Live Preview</h3>', unsafe_allow_html=True)

        resume_html = build_resume_html()

        pdf_buffer = generate_pdf_from_html(resume_html)
        filename = st.session_state.get("full_name", "").replace(" ", "_") or "my_resume"
        st.download_button(
            label="Download as PDF",
            data=pdf_buffer,
            file_name=f"resume_{filename}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            key="download_pdf_btn",
        )

        st.markdown("---")

        st.markdown(resume_html, unsafe_allow_html=True)
