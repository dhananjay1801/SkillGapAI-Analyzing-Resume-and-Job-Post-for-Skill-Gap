import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from utils.file_parser import parse_file
from utils.text_cleaner import process_text
from utils.skill_extractor import extract_skills
from utils.skill_gap_analyzer import analyze_complete_skill_gap, calculate_match_percentage
from utils.skill_recommendation import get_smart_recommendations
from utils.report_generator import generate_pdf_report

st.set_page_config(
    page_title = 'SkillGapAI - AI Analyzer',
    layout = 'wide'
)

# auto refresh
# st_autorefresh(interval=1000, limit=None, key='my_autorefresh')

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
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #0f172a;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #1e293b;
    }
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #334155;
    }
    .analyze-btn-container {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #be123c 0%, #f43f5e 100%);
        color: #fafafa;
        font-size: 1.2rem;
        font-weight: 700;
        padding: 0.8rem 3rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(190, 18, 60, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(190, 18, 60, 0.5);
    }
    .analysis-card {
        background: #0f172a;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #1e293b;
        margin: 0;
        display: flex;
        flex-direction: column;
    }
    .skills-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        align-items: stretch;
    }
    .skills-grid .analysis-card {
        height: 100%;
    }
    .analysis-title {
        color: #f8fafc;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }
    .score-big {
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        margin: 1rem 0;
    }
    .score-green { color: #22c55e; }
    .score-yellow { color: #eab308; }
    .score-red { color: #ef4444; }
    .skill-tag {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
        margin: 4px;
        font-weight: 500;
    }
    .tag-matched {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .tag-partial {
        background: rgba(234, 179, 8, 0.15);
        color: #facc15;
        border: 1px solid rgba(234, 179, 8, 0.3);
    }
    .tag-missing {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .skill-section-title {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyze_clicked' not in st.session_state:
    st.session_state.analyze_clicked = False

st.markdown('<h1 style="text-align: center;">SkillGapAI Analyzer</h1>', unsafe_allow_html=True)
st.markdown('---')

resume_file = None
resume_text = ""
job_file = None
job_text = ""

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown('<div class="card-title card-title-resume">Resume</div>', unsafe_allow_html=True)
        
        col1_option = st.radio("Pick option for resume:", ['File', 'Text'], horizontal=True)

        if col1_option == 'File':
            resume_file = st.file_uploader("Choose a resume file", type=['pdf', 'docx', 'txt'], key='resume')
            if resume_file:
                st.success(f"Resume uploaded: {resume_file.name}")
                resume_text = parse_file(resume_file)

        elif col1_option == 'Text':
            resume_text = st.text_area("Enter or paste resume text here:", height=200, key='resume_text')
    
    cleaned_resume = process_text(resume_text)

with col2:
    with st.container(border=True):
        st.markdown('<div class="card-title card-title-job">Job Description</div>', unsafe_allow_html=True)
        
        col2_option = st.radio("Pick option for job:", ['File', 'Text'], horizontal=True)

        if col2_option == 'File':
            job_file = st.file_uploader("Choose a job description file", type=['pdf', 'docx', 'txt'], key='job')

            if job_file:
                st.success(f"Job Description uploaded: {job_file.name}")
                job_text = parse_file(job_file)

        elif col2_option == 'Text':
            job_text = st.text_area("Enter or paste job description here:", height=200, key='job_text')

    cleaned_jd = process_text(job_text)



# button
st.markdown("")
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
with btn_col2:
    if st.button("Analyze Skill Gap", type="primary", width='stretch'):
        if cleaned_resume and cleaned_jd:
            st.session_state.analyze_clicked = True
        else:
            st.warning("Please upload both resume and job description first.")

# Analysis Section
if st.session_state.analyze_clicked and cleaned_resume and cleaned_jd:
    # skill extraction
    resume_skills = extract_skills(cleaned_resume)
    jd_skills = extract_skills(cleaned_jd)
    
    st.markdown('---')
    st.markdown('<h2 style="text-align: center; margin-bottom: 2rem;">Skill Gap Analysis</h2>', unsafe_allow_html=True)

    if (resume_skills['technical'] or resume_skills['soft']) and (jd_skills['technical'] or jd_skills['soft']):
        gap_analysis = analyze_complete_skill_gap(jd_skills, resume_skills)

        tech_pct = calculate_match_percentage(gap_analysis['technical'])
        soft_pct = calculate_match_percentage(gap_analysis['soft'])
        overall_pct = (tech_pct + soft_pct) // 2
        
        tech = gap_analysis['technical']
        soft = gap_analysis['soft']
        
        # Helper function for color
        def get_color(pct):
            if pct >= 70: return "#22c55e"
            elif pct >= 40: return "#eab308"
            return "#ef4444"
        
        def get_color_class(pct):
            if pct >= 70: return "score-green"
            elif pct >= 40: return "score-yellow"
            return "score-red"

        # Row 1: Overall Score + Pie Charts
        score_col1, score_col2, score_col3 = st.columns([1, 1, 1])
        
        with score_col1:
            st.markdown(f"""
            <div class="analysis-card">
                <div class="analysis-title">Overall Match</div>
                <div class="score-big {get_color_class(overall_pct)}">{overall_pct}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with score_col2:
            # Technical Skills Pie Chart
            fig_tech = go.Figure(data=[go.Pie(
                values=[len(tech['matched']), len(tech['partial']), len(tech['missing'])],
                labels=['Matched', 'Partial', 'Missing'],
                hole=0.6,
                marker_colors=['#22c55e', '#eab308', '#ef4444'],
                textinfo='none',
                hovertemplate='%{label}: %{value}<extra></extra>',
                sort=False,
                direction='clockwise',
                rotation=0
            )])
            fig_tech.update_layout(
                title=dict(text=f"Technical: {tech_pct}%", x=0.5, xanchor='center', font=dict(size=16, color='#f8fafc')),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=250,
                margin=dict(t=50, b=20, l=20, r=20),
                annotations=[dict(text=f'{tech_pct}%', x=0.5, y=0.5, font_size=24, font_color=get_color(tech_pct), showarrow=False)]
            )
            st.plotly_chart(fig_tech, width='stretch')
        
        with score_col3:
            # Soft Skills Pie Chart
            fig_soft = go.Figure(data=[go.Pie(
                values=[len(soft['matched']), len(soft['partial']), len(soft['missing'])],
                labels=['Matched', 'Partial', 'Missing'],
                hole=0.6,
                marker_colors=['#22c55e', '#eab308', '#ef4444'],
                textinfo='none',
                hovertemplate='%{label}: %{value}<extra></extra>',
                sort=False,
                direction='clockwise',
                rotation=0
            )])
            fig_soft.update_layout(
                title=dict(text=f"Soft Skills: {soft_pct}%", x=0.5, xanchor='center', font=dict(size=16, color='#f8fafc')),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=250,
                margin=dict(t=50, b=20, l=20, r=20),
                annotations=[dict(text=f'{soft_pct}%', x=0.5, y=0.5, font_size=24, font_color=get_color(soft_pct), showarrow=False)]
            )
            st.plotly_chart(fig_soft, width='stretch')
        
        # Radar Chart - Skills Coverage (moved above detailed cards)
        st.markdown('<h3 style="text-align: center; margin: 2rem 0 1rem 0;">Skills Coverage Radar</h3>', unsafe_allow_html=True)
        
        # Calculate coverage percentages for radar
        tech_total = len(tech['matched']) + len(tech['partial']) + len(tech['missing'])
        soft_total = len(soft['matched']) + len(soft['partial']) + len(soft['missing'])
        
        tech_matched_pct = (len(tech['matched']) / tech_total * 100) if tech_total > 0 else 0
        tech_partial_pct = (len(tech['partial']) / tech_total * 100) if tech_total > 0 else 0
        soft_matched_pct = (len(soft['matched']) / soft_total * 100) if soft_total > 0 else 0
        soft_partial_pct = (len(soft['partial']) / soft_total * 100) if soft_total > 0 else 0
        
        # Combined scores
        tech_coverage = tech_matched_pct + (tech_partial_pct * 0.5)
        soft_coverage = soft_matched_pct + (soft_partial_pct * 0.5)
        
        # Radar Chart
        categories = ['Technical Skills', 'Soft Skills', 'Full Match Rate', 'Partial Match Rate', 'Overall Fit']
        
        # Resume values (what candidate has)
        resume_values = [
            tech_coverage,
            soft_coverage,
            (len(tech['matched']) + len(soft['matched'])) / (tech_total + soft_total) * 100 if (tech_total + soft_total) > 0 else 0,
            (len(tech['partial']) + len(soft['partial'])) / (tech_total + soft_total) * 100 if (tech_total + soft_total) > 0 else 0,
            overall_pct
        ]
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=resume_values + [resume_values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(190, 18, 60, 0.3)',
            line=dict(color='#be123c', width=2),
            name='Your Profile'
        ))
        
        # Job requirement baseline (100% for all)
        fig_radar.add_trace(go.Scatterpolar(
            r=[100, 100, 100, 0, 100, 100],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(34, 197, 94, 0.1)',
            line=dict(color='#22c55e', width=1, dash='dash'),
            name='Ideal Match'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color='#64748b'),
                    gridcolor='#1e293b'
                ),
                angularaxis=dict(
                    tickfont=dict(color='#f8fafc', size=11),
                    gridcolor='#1e293b'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=True,
            legend=dict(
                font=dict(color='#f8fafc'),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            margin=dict(t=30, b=30, l=60, r=60)
        )
        st.plotly_chart(fig_radar, width='stretch')
        
        # Detailed Skills Cards - Equal Height
        st.markdown('<h3 style="text-align: center; margin: 2rem 0 1rem 0;">Detailed Skill Breakdown</h3>', unsafe_allow_html=True)
        
        matched_tags_tech = "".join([f'<span class="skill-tag tag-matched">{jd}</span>' for jd, res, score in tech['matched']]) if tech['matched'] else '<span style="color: #64748b;">None</span>'
        partial_tags_tech = "".join([f'<span class="skill-tag tag-partial">{jd}</span>' for jd, res, score in tech['partial']]) if tech['partial'] else '<span style="color: #64748b;">None</span>'
        missing_tags_tech = "".join([f'<span class="skill-tag tag-missing">{jd}</span>' for jd, score in tech['missing']]) if tech['missing'] else '<span style="color: #64748b;">None</span>'
        
        matched_tags_soft = "".join([f'<span class="skill-tag tag-matched">{jd}</span>' for jd, res, score in soft['matched']]) if soft['matched'] else '<span style="color: #64748b;">None</span>'
        partial_tags_soft = "".join([f'<span class="skill-tag tag-partial">{jd}</span>' for jd, res, score in soft['partial']]) if soft['partial'] else '<span style="color: #64748b;">None</span>'
        missing_tags_soft = "".join([f'<span class="skill-tag tag-missing">{jd}</span>' for jd, score in soft['missing']]) if soft['missing'] else '<span style="color: #64748b;">None</span>'
        
        st.markdown(f"""
        <div class="skills-grid">
            <div class="analysis-card">
                <div class="analysis-title">Technical Skills</div>
                <div class="skill-section-title">Matched ({len(tech['matched'])})</div>
                <div>{matched_tags_tech}</div>
                <div class="skill-section-title">Partial Match ({len(tech['partial'])})</div>
                <div>{partial_tags_tech}</div>
                <div class="skill-section-title">Missing ({len(tech['missing'])})</div>
                <div>{missing_tags_tech}</div>
            </div>
            <div class="analysis-card">
                <div class="analysis-title">Soft Skills</div>
                <div class="skill-section-title">Matched ({len(soft['matched'])})</div>
                <div>{matched_tags_soft}</div>
                <div class="skill-section-title">Partial Match ({len(soft['partial'])})</div>
                <div>{partial_tags_soft}</div>
                <div class="skill-section-title">Missing ({len(soft['missing'])})</div>
                <div>{missing_tags_soft}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('---')
        st.markdown('<h3 style="text-align: center; margin: 1.5rem 0 1rem 0;">Recommendations</h3>', unsafe_allow_html=True)

        recommendations = get_smart_recommendations(gap_analysis, resume_skills)

        if recommendations:
            # Create 2 columns
            cols = st.columns(2)
            
            for i, rec in enumerate(recommendations):
                col_idx = i % 2
                with cols[col_idx]:
                    st.markdown(f"""
                    <div style="background: #0f172a; border-radius: 8px; padding: 1rem; margin: 0.75rem 0;">
                        <div style="color: #f8fafc; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">{i+1}. {rec['skill']}</div>
                        <div style="color: #cbd5e1; font-size: 0.85rem;">
                            <div style="margin-bottom: 0.3rem;"><span style="color: #94a3b8;">Learning Time:</span> {rec['learning_time']}</div>
                            <div style="margin-bottom: 0.3rem;"><span style="color: #94a3b8;">Match Impact:</span> <span style="color: #22c55e;">+{rec['match_impact']}%</span></div>
                            <div style="margin-bottom: 0.3rem;"><span style="color: #94a3b8;">Learning Ease:</span> <span style="color: #eab308;">{int(rec['similarity_score']*100)}%</span></div>
                            {f'<div><span style="color: #94a3b8;">Similar to:</span> {rec["closest_existing"]} ({int(rec["closest_similarity"]*100)}%)</div>' if rec['closest_existing'] else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No skill recommendations - you have all required skills!")

        # Download Report
        st.markdown('---')
        pdf_buffer = generate_pdf_report(gap_analysis, tech_pct, soft_pct, overall_pct, recommendations, fig_tech, fig_soft, fig_radar)
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name=f"skill_gap_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            type="primary"
        )

    else:
        st.info("No skills found. Please check your inputs.")