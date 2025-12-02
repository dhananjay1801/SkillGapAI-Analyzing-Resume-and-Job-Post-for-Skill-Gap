import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils.file_parser import parse_file
from utils.text_cleaner import process_text
from utils.skill_extractor import extract_skills

st.set_page_config(page_title = 'SkillGapAI - Dhananjay', layout = 'wide')

# auto refresh
# st_autorefresh(interval=1000, limit=None, key='my_autorefresh')

# Hide Streamlit's default header/menu
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        margin-top: -80px;
        padding-top: 0rem;
    }
    .stApp > header {
        position: fixed;
        top: 0;
    }
    .stApp > div {
        margin-top: 0px;
    }
    div[data-testid="stAppViewContainer"] {
        margin-top: 0px;
        padding-top: 0px;
    }
</style>
""", unsafe_allow_html=True)


st.title("SkillGapAI Analyzing Resume and Job Post for Skill Gap")

st.subheader("Upload files")

resume_file = None
resume_text = ""
job_file = None
job_text = ""

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Resume")
    col1_option = st.radio("Pick option for resume:", ['File', 'Text'])

    if col1_option == 'File':
        resume_file = st.file_uploader("Choose a resume file", type=['pdf', 'docx', 'txt'], key='resume')
        if resume_file:
            st.success(f"Resume uploaded: {resume_file.name}")
            resume_text = parse_file(resume_file)

    elif col1_option == 'Text':
        resume_text = st.text_area("Enter or paste resume text here:", height='content')
    
    cleaned_resume = process_text(resume_text)


    # preview cleaned text
    # st.text_area("preview resume", cleaned_resume, height='content')

with col2:
    st.markdown("#### Job Description")
    col2_option = st.radio("Pick option for job:", ['File', 'Text'])

    if col2_option == 'File':
        job_file = st.file_uploader("Choose a job description file", type=['pdf', 'docx', 'txt'], key='job')

        if job_file:
            st.success(f"Job Description uploaded: {job_file.name}")
            job_text = parse_file(job_file)

    elif col2_option == 'Text':
        job_text = st.text_area("Enter or paste job description here:", height='content')

    cleaned_jd = process_text(job_text)

    # preview cleaned text
    # st.text_area("preview jd", cleaned_jd, height='content')


# skill extraction
resume_skills = extract_skills(cleaned_resume) if cleaned_resume else {'technical': [], 'soft': []}
jd_skills = extract_skills(cleaned_jd) if cleaned_jd else {'technical': [], 'soft': []}

st.markdown('---')
st.subheader('Extracted Skills:')

col3, col4 = st.columns(2)

with col3:
    st.markdown("#### Resume Skills")
    st.markdown(f"**Technical ({len(resume_skills['technical'])})**")
    st.write(", ".join(resume_skills['technical']) if resume_skills['technical'] else "None found")
    st.markdown(f"**Soft ({len(resume_skills['soft'])})**")
    st.write(", ".join(resume_skills['soft']) if resume_skills['soft'] else "None found")

with col4:
    st.markdown("#### Job Description Skills")
    st.markdown(f"**Technical ({len(jd_skills['technical'])})**")
    st.write(", ".join(jd_skills['technical']) if jd_skills['technical'] else "None found")
    st.markdown(f"**Soft ({len(jd_skills['soft'])})**")
    st.write(", ".join(jd_skills['soft']) if jd_skills['soft'] else "None found")