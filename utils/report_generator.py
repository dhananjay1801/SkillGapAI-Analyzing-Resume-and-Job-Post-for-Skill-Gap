from datetime import datetime
from io import BytesIO
import sys
import os
import base64


def generate_pdf_report(gap_analysis, tech_pct, soft_pct, overall_pct, recommendations, fig_tech=None, fig_soft=None, fig_radar=None):
    tech = gap_analysis['technical']
    soft = gap_analysis['soft']
    
    def get_color(pct):
        if pct >= 70: return "#22c55e"
        elif pct >= 40: return "#eab308"
        return "#ef4444"
    
    def chart_to_base64(fig, width=400, height=300):
        if fig is None:
            return None
        try:
            fig_copy = fig.to_dict()
            if 'layout' in fig_copy:
                fig_copy['layout']['paper_bgcolor'] = 'white'
                fig_copy['layout']['plot_bgcolor'] = 'white'
                if 'annotations' in fig_copy['layout']:
                    for ann in fig_copy['layout']['annotations']:
                        if 'font' in ann and 'color' in ann['font']:
                            ann['font']['color'] = '#000000'
                if 'title' in fig_copy['layout'] and isinstance(fig_copy['layout']['title'], dict):
                    if 'font' in fig_copy['layout']['title']:
                        fig_copy['layout']['title']['font']['color'] = '#000000'
                if 'polar' in fig_copy['layout']:
                    polar = fig_copy['layout']['polar']
                    if 'angularaxis' in polar and 'tickfont' in polar['angularaxis']:
                        polar['angularaxis']['tickfont']['color'] = '#000000'
                    if 'radialaxis' in polar:
                        if 'tickfont' in polar['radialaxis']:
                            polar['radialaxis']['tickfont']['color'] = '#000000'
                        if 'gridcolor' in polar['radialaxis']:
                            polar['radialaxis']['gridcolor'] = '#cccccc'
                    if 'angularaxis' in polar and 'gridcolor' in polar['angularaxis']:
                        polar['angularaxis']['gridcolor'] = '#cccccc'
                if 'legend' in fig_copy['layout'] and 'font' in fig_copy['layout']['legend']:
                    fig_copy['layout']['legend']['font']['color'] = '#000000'
            
            from plotly.graph_objects import Figure
            fig_white = Figure(fig_copy)
            img_bytes = None
            try:
                img_bytes = fig_white.to_image(format="png", width=width, height=height, engine="kaleido")
            except:
                try:
                    img_bytes = fig_white.to_image(format="png", width=width, height=height)
                except:
                    img_bytes = fig.to_image(format="png", width=width, height=height)
            if img_bytes:
                return base64.b64encode(img_bytes).decode('utf-8')
            return None
        except:
            return None
    
    tech_chart_img = chart_to_base64(fig_tech, 350, 280) if fig_tech else None
    soft_chart_img = chart_to_base64(fig_soft, 350, 280) if fig_soft else None
    radar_chart_img = chart_to_base64(fig_radar, 700, 450) if fig_radar else None
    
    def render_skill_tag(skill_name, score, tag_class):
        pct = int(score * 100)
        colors = {
            'tag-matched': '#22c55e',
            'tag-partial': '#eab308', 
            'tag-missing': '#ef4444'
        }
        fill_color = colors.get(tag_class, '#999')
        return f'''<span class="skill-tag {tag_class}">{skill_name}<span class="skill-progress"><span class="skill-progress-bar"><span class="skill-progress-fill" style="width:{pct}%"></span></span><span class="skill-pct">{pct}%</span></span></span>'''
    
    def render_skills_grid(skills_list, tag_class, is_missing=False):
        if not skills_list:
            return '<div style="color:#64748b;padding:5px;">None</div>'
        html = '<table class="skills-grid-table"><tr>'
        for i, skill_data in enumerate(skills_list):
            if is_missing:
                jd, score = skill_data
            else:
                jd, res, score = skill_data
            if i > 0 and i % 2 == 0:
                html += '</tr><tr>'
            html += f'<td>{render_skill_tag(jd, score, tag_class)}</td>'
        if len(skills_list) % 2 == 1:
            html += '<td></td>'
        html += '</tr></table>'
        return html
    
    html = f"""
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 20px; }}
            body {{ 
                font-family: "Liberation Sans", "DejaVu Sans", "Noto Sans", "Segoe UI", Tahoma, sans-serif;
                color: #1e293b;
                line-height: 1.4;
                font-size: 10px;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #be123c;
                padding-bottom: 8px;
                margin-bottom: 12px;
            }}
            .header h1 {{
                color: #be123c;
                margin: 0;
                font-size: 22px;
                font-weight: 700;
            }}
            .header p {{
                color: #64748b;
                margin: 3px 0 0 0;
                font-size: 9px;
            }}
            .top-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15px;
            }}
            .top-table td {{
                vertical-align: middle;
                text-align: center;
                padding: 8px;
            }}
            .score-box {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px 10px;
            }}
            .score-label {{
                font-size: 12px;
                color: #64748b;
                font-weight: 600;
                margin-bottom: 5px;
            }}
            .score-value {{
                font-size: 42px;
                font-weight: 800;
            }}
            .chart-box img {{
                max-width: 180px;
                height: auto;
            }}
            .chart-label {{
                font-size: 10px;
                font-weight: 600;
                color: #334155;
                margin-top: 3px;
            }}
            .radar-section {{
                text-align: center;
                margin: 12px 0;
            }}
            .radar-title {{
                font-size: 14px;
                font-weight: 700;
                color: #be123c;
                margin-bottom: 8px;
            }}
            .radar-section img {{
                max-width: 100%;
                max-height: 280px;
            }}
            .section-title {{
                font-size: 14px;
                font-weight: 700;
                color: #be123c;
                border-bottom: 2px solid #be123c;
                padding-bottom: 4px;
                margin: 15px 0 10px 0;
                text-align: center;
            }}
            .main-table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 10px;
            }}
            .main-table > tbody > tr > td {{
                width: 50%;
                vertical-align: top;
            }}
            .skill-card {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
            }}
            .card-title {{
                font-size: 13px;
                font-weight: 700;
                color: #1e293b;
                text-align: center;
                margin-bottom: 8px;
                padding-bottom: 5px;
                border-bottom: 1px solid #e2e8f0;
            }}
            .subsection-title {{
                font-size: 9px;
                font-weight: 600;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin: 8px 0 4px 0;
                page-break-after: avoid;
                break-after: avoid;
            }}
            .skills-grid-table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 4px;
            }}
            .skills-grid-table td {{
                width: 50%;
                vertical-align: top;
                padding: 0;
            }}
            .skill-tag {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
                padding: 8px 12px;
                border-radius: 20px;
                font-size: 9px;
                font-weight: 500;
                box-sizing: border-box;
                margin-bottom: 4px;
                page-break-inside: avoid;
                break-inside: avoid;
            }}
            .skill-progress {{
                display: flex;
                align-items: center;
                gap: 5px;
                flex-shrink: 0;
            }}
            .skill-progress-bar {{
                display: inline-block;
                width: 45px;
                height: 5px;
                background: rgba(0,0,0,0.15);
                border-radius: 3px;
                overflow: hidden;
            }}
            .skill-progress-fill {{
                display: block;
                height: 100%;
                border-radius: 3px;
            }}
            .skill-pct {{
                font-size: 8px;
                font-weight: 700;
            }}
            .tag-matched {{
                background: rgba(34, 197, 94, 0.2);
                color: #16a34a;
                border: 1px solid rgba(34, 197, 94, 0.4);
            }}
            .tag-matched .skill-progress-bar {{
                background: rgba(34, 197, 94, 0.25);
            }}
            .tag-matched .skill-progress-fill {{
                background: #22c55e;
            }}
            .tag-partial {{
                background: rgba(234, 179, 8, 0.2);
                color: #a16207;
                border: 1px solid rgba(234, 179, 8, 0.4);
            }}
            .tag-partial .skill-progress-bar {{
                background: rgba(234, 179, 8, 0.25);
            }}
            .tag-partial .skill-progress-fill {{
                background: #eab308;
            }}
            .tag-missing {{
                background: rgba(239, 68, 68, 0.2);
                color: #dc2626;
                border: 1px solid rgba(239, 68, 68, 0.4);
            }}
            .tag-missing .skill-progress-bar {{
                background: rgba(239, 68, 68, 0.25);
            }}
            .tag-missing .skill-progress-fill {{
                background: #ef4444;
            }}
            .rec-table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 8px;
            }}
            .rec-table td {{
                width: 50%;
                vertical-align: top;
            }}
            .recommendation {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
            }}
            .rec-title {{
                font-weight: 600;
                font-size: 11px;
                color: #1e293b;
                margin-bottom: 6px;
            }}
            .rec-detail {{
                margin: 3px 0;
                font-size: 9px;
                color: #475569;
            }}
            .rec-label {{
                color: #64748b;
            }}
            .rec-impact {{
                color: #22c55e;
                font-weight: 600;
            }}
            .rec-ease {{
                color: #eab308;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Skill Gap Analysis Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <table class="top-table">
            <tr>
                <td style="width:33%">
                    <div class="score-box">
                        <div class="score-label">Overall Match</div>
                        <div class="score-value" style="color:{get_color(overall_pct)}">{overall_pct}%</div>
                    </div>
                </td>
                <td style="width:33%">
                    <div class="chart-box">
                        {f'<img src="data:image/png;base64,{tech_chart_img}">' if tech_chart_img else '<div style="padding:30px;color:#999">Chart</div>'}
                        <div class="chart-label">Technical: {tech_pct}%</div>
                    </div>
                </td>
                <td style="width:33%">
                    <div class="chart-box">
                        {f'<img src="data:image/png;base64,{soft_chart_img}">' if soft_chart_img else '<div style="padding:30px;color:#999">Chart</div>'}
                        <div class="chart-label">Soft Skills: {soft_pct}%</div>
                    </div>
                </td>
            </tr>
        </table>
        
        <div class="radar-section">
            <div class="radar-title">Skills Coverage Radar</div>
            {f'<img src="data:image/png;base64,{radar_chart_img}">' if radar_chart_img else '<div style="padding:40px;color:#999">Radar Chart</div>'}
        </div>
        
        <div class="section-title">Detailed Skill Breakdown</div>
        <table class="main-table">
            <tr>
                <td>
                    <div class="skill-card">
                        <div class="card-title">Technical Skills</div>
                        <div class="subsection-title">Matched ({len(tech['matched'])})</div>
                        {render_skills_grid(tech['matched'], 'tag-matched', False)}
                        <div class="subsection-title">Partial Match ({len(tech['partial'])})</div>
                        {render_skills_grid(tech['partial'], 'tag-partial', False)}
                        <div class="subsection-title">Missing ({len(tech['missing'])})</div>
                        {render_skills_grid(tech['missing'], 'tag-missing', True)}
                    </div>
                </td>
                <td>
                    <div class="skill-card">
                        <div class="card-title">Soft Skills</div>
                        <div class="subsection-title">Matched ({len(soft['matched'])})</div>
                        {render_skills_grid(soft['matched'], 'tag-matched', False)}
                        <div class="subsection-title">Partial Match ({len(soft['partial'])})</div>
                        {render_skills_grid(soft['partial'], 'tag-partial', False)}
                        <div class="subsection-title">Missing ({len(soft['missing'])})</div>
                        {render_skills_grid(soft['missing'], 'tag-missing', True)}
                    </div>
                </td>
            </tr>
        </table>
        
        <div class="section-title">Recommendations</div>
    """
    
    if recommendations:
        html += '<table class="rec-table"><tr>'
        for i, rec in enumerate(recommendations, 1):
            if i > 1 and (i - 1) % 2 == 0:
                html += '</tr><tr>'
            similar = f'<div class="rec-detail"><span class="rec-label">Similar to:</span> {rec["closest_existing"]} ({int(rec["closest_similarity"]*100)}%)</div>' if rec['closest_existing'] else ''
            html += f'''<td>
                <div class="recommendation">
                    <div class="rec-title">{i}. {rec['skill']}</div>
                    <div class="rec-detail"><span class="rec-label">Learning Time:</span> {rec['learning_time']}</div>
                    <div class="rec-detail"><span class="rec-label">Match Impact:</span> <span class="rec-impact">+{rec['match_impact']}%</span></div>
                    <div class="rec-detail"><span class="rec-label">Learning Ease:</span> <span class="rec-ease">{int(rec['similarity_score']*100)}%</span></div>
                    {similar}
                </div>
            </td>'''
        if len(recommendations) % 2 == 1:
            html += '<td></td>'
        html += '</tr></table>'
    else:
        html += '<p style="color:#64748b;text-align:center;">No recommendations - you have all required skills!</p>'
    
    html += """
    </body>
    </html>
    """
    
    if sys.platform == "win32":
        gtk_bin = r"D:\Program Files\GTK3-Runtime Win64\bin"
        if os.path.exists(gtk_bin) and hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(gtk_bin)
            except:
                pass
    
    from weasyprint import HTML
    buffer = BytesIO()
    HTML(string=html).write_pdf(buffer)
    buffer.seek(0)
    return buffer

