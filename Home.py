import streamlit as st
from streamlit_autorefresh import st_autorefresh

# auto refresh
# st_autorefresh(interval=1000, limit=None, key='my_autorefresh')

st.set_page_config(
    page_title="SkillGapAI - Home",
    layout="wide"
)

st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 4rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradient-shift 3s ease infinite;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
        position: relative;
        padding: 1rem 0;
    }
    
    @keyframes gradient-shift {
        0%, 100% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
    }
    
    .title-container {
        position: relative;
        padding: 2rem 0;
        margin-bottom: 1rem;
    }
    
    .title-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: linear-gradient(90deg, transparent, #667eea, #764ba2, transparent);
        border-radius: 2px;
    }
    
    .title-container::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: linear-gradient(90deg, transparent, #f093fb, #f5576c, transparent);
        border-radius: 2px;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.3rem;
        color: #4a5568;
        margin-bottom: 3rem;
        font-weight: 400;
        letter-spacing: 0.5px;
        font-style: italic;
    }
    
    .feature-card {
        background: #0f172a;
        border-radius: 16px;
        overflow: hidden;
        height: 100%;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    
    
    .feature-title {
        background: linear-gradient(135deg, #be123c 0%, #e11d48 50%, #fb7185 100%);
        color: #fafafa;
        font-size: 1.8rem;
        font-weight: bold;
        padding: 1.5rem 2rem;
        margin: 0;
        text-align: center;
    }
    
    .feature-description {
        color: #cbd5e1;
        font-size: 1rem;
        line-height: 1.7;
        padding: 2rem;
        background: #0f172a;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #be123c 0%, #e11d48 100%);
        color: #fafafa;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(225, 29, 72, 0.5);
    }
    
    [data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(2) .stButton > button {
        background: linear-gradient(90deg, #ea580c 0%, #f97316 100%);
        color: #fafafa;
    }
    
    [data-testid="stHorizontalBlock"]:nth-of-type(1) > div:nth-child(2) .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.5);
    }
    
    .info-section {
        background: #0f172a;
        border-radius: 12px;
        padding: 2.5rem;
        margin-top: 3rem;
    }
    
    .info-title {
        font-size: 2rem;
        font-weight: bold;
        color: #fafafa;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .info-text {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #cbd5e1;
        text-align: justify;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        color: #6b7280;
        font-size: 0.95rem;
        border-top: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-container">
    <div class="main-title">SkillGapAI</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your AI-Powered SkillGap Assistant and Resume Generator</div>', unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">SkillGap AI Analyzer</div>
        <div class="feature-description">
            Analyze your resume against job descriptions to identify skill gaps and improve your match percentage. 
            Get detailed insights on missing, matched, and partially matched skills.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open SkillGap AI Analyzer", key="skillgap_btn", use_container_width=True):
        st.switch_page("pages/SkillGap_AI.py")

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title" style="background: linear-gradient(135deg, #ea580c 0%, #f97316 50%, #fb923c 100%); color: #fff7ed;">Resume Generator</div>
        <div class="feature-description">
            Create professional resumes tailored to your skills and experience. 
            Generate ATS-friendly resumes that stand out to recruiters.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Resume Generator", key="resume_btn", use_container_width=True):
        st.switch_page("pages/Resume_Generator.py")

st.markdown("""
<div class="info-section">
    <div class="info-title">About SkillGapAI</div>
    <div class="info-text">
        <p>
            SkillGapAI is an innovative platform designed to bridge the gap between job seekers and their dream careers. 
            Our advanced AI-powered tools help you understand exactly what skills employers are looking for and how your 
            current skill set measures up.
        </p>
        <p>
            Whether you're actively job hunting or looking to advance in your current role, SkillGapAI provides actionable 
            insights to help you identify areas for improvement, enhance your resume, and increase your chances of landing 
            your ideal position. Our comprehensive analysis covers both technical and soft skills, giving you a complete 
            picture of your professional profile.
        </p>
        <p>
            Start your journey today by selecting one of our powerful tools above. Upload your resume and job descriptions 
            to get instant feedback, or use our resume generator to create a polished, professional document that highlights 
            your strengths and addresses potential skill gaps.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="footer">
    Developed by Dhananjay Tailor
</div>
""", unsafe_allow_html=True)
