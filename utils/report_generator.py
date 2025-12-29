from datetime import datetime
from io import BytesIO
import sys
import os
import base64


def generate_pdf_report(gap_analysis, tech_pct, soft_pct, overall_pct, recommendations, fig_tech=None, fig_soft=None, fig_radar=None):
    """Generate PDF from existing analysis data - matches website display with charts."""
    tech = gap_analysis['technical']
    soft = gap_analysis['soft']
    
    # Helper for color based on percentage
    def get_color_class(pct):
        if pct >= 70: return "#22c55e"
        elif pct >= 40: return "#eab308"
        return "#ef4444"
    
    # Convert plotly charts to base64 images
    def chart_to_base64(fig):
        if fig is None:
            return None
        try:
            # Update the figure directly for PDF (white background)
            fig_copy = fig.to_dict()
            
            # Update background colors
            if 'layout' in fig_copy:
                fig_copy['layout']['paper_bgcolor'] = 'white'
                fig_copy['layout']['plot_bgcolor'] = 'white'
                
                # Update annotation colors
                if 'annotations' in fig_copy['layout']:
                    for ann in fig_copy['layout']['annotations']:
                        if 'font' in ann and 'color' in ann['font']:
                            ann['font']['color'] = '#000000'
                
                # Update title color if exists
                if 'title' in fig_copy['layout']:
                    if isinstance(fig_copy['layout']['title'], dict):
                        if 'font' in fig_copy['layout']['title']:
                            fig_copy['layout']['title']['font']['color'] = '#000000'
                
                # Update polar axis colors for radar chart
                if 'polar' in fig_copy['layout']:
                    if 'angularaxis' in fig_copy['layout']['polar']:
                        if 'tickfont' in fig_copy['layout']['polar']['angularaxis']:
                            fig_copy['layout']['polar']['angularaxis']['tickfont']['color'] = '#000000'
                    if 'radialaxis' in fig_copy['layout']['polar']:
                        if 'tickfont' in fig_copy['layout']['polar']['radialaxis']:
                            fig_copy['layout']['polar']['radialaxis']['tickfont']['color'] = '#000000'
                        if 'gridcolor' in fig_copy['layout']['polar']['radialaxis']:
                            fig_copy['layout']['polar']['radialaxis']['gridcolor'] = '#cccccc'
                    if 'angularaxis' in fig_copy['layout']['polar']:
                        if 'gridcolor' in fig_copy['layout']['polar']['angularaxis']:
                            fig_copy['layout']['polar']['angularaxis']['gridcolor'] = '#cccccc'
                
                # Update legend colors
                if 'legend' in fig_copy['layout']:
                    if 'font' in fig_copy['layout']['legend']:
                        fig_copy['layout']['legend']['font']['color'] = '#000000'
            
            from plotly.graph_objects import Figure
            fig_white = Figure(fig_copy)
            
            # Try different methods to convert to image
            img_bytes = None
            try:
                # Try with kaleido engine
                img_bytes = fig_white.to_image(format="png", width=400, height=300, engine="kaleido")
            except:
                try:
                    # Try without engine (uses orca if available)
                    img_bytes = fig_white.to_image(format="png", width=400, height=300)
                except:
                    # Last resort: try original figure
                    img_bytes = fig.to_image(format="png", width=400, height=300)
            
            if img_bytes:
                return base64.b64encode(img_bytes).decode('utf-8')
            return None
        except Exception as e:
            # If all fails, return None
            return None
    
    # Convert charts to base64 - ensure figures are valid
    tech_chart_img = None
    soft_chart_img = None
    radar_chart_img = None
    
    if fig_tech is not None:
        tech_chart_img = chart_to_base64(fig_tech)
    if fig_soft is not None:
        soft_chart_img = chart_to_base64(fig_soft)
    if fig_radar is not None:
        radar_chart_img = chart_to_base64(fig_radar)
    
    html = f"""
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 25px; }}
            body {{ 
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                color: #000;
                line-height: 1.4;
                font-size: 11px;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #be123c;
                padding-bottom: 10px;
                margin-bottom: 15px;
            }}
            .header h1 {{
                color: #be123c;
                margin: 0;
                font-size: 24px;
                font-weight: 700;
            }}
            .header p {{
                color: #666;
                margin: 3px 0;
                font-size: 10px;
            }}
            .top-section {{
                display: flex;
                justify-content: space-around;
                align-items: center;
                margin: 15px 0;
                gap: 10px;
            }}
            .overall-score-box {{
                text-align: center;
                flex: 1;
                background: #f9f9f9;
                border-radius: 8px;
                padding: 15px;
            }}
            .overall-label {{
                font-size: 14px;
                color: #666;
                margin-bottom: 8px;
                font-weight: 600;
            }}
            .overall-value {{
                font-size: 48px;
                font-weight: 800;
            }}
            .chart-box {{
                text-align: center;
                flex: 1;
            }}
            .chart-box img {{
                max-width: 100%;
                height: auto;
            }}
            .chart-label {{
                font-size: 11px;
                font-weight: 600;
                margin-top: 5px;
                color: #333;
            }}
            .radar-chart {{
                text-align: center;
                margin: 15px 0;
            }}
            .radar-chart img {{
                max-width: 100%;
                height: auto;
            }}
            .radar-title {{
                font-size: 16px;
                font-weight: 700;
                color: #be123c;
                margin-bottom: 10px;
                text-align: center;
            }}
            .section {{
                margin: 15px 0;
            }}
            .section-title {{
                font-size: 16px;
                font-weight: 700;
                color: #be123c;
                border-bottom: 2px solid #be123c;
                padding-bottom: 5px;
                margin-bottom: 12px;
                text-align: center;
            }}
            .subsection-title {{
                font-size: 10px;
                font-weight: 600;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin: 10px 0 5px 0;
            }}
            .skill-tag {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 15px;
                font-size: 9px;
                margin: 2px;
                font-weight: 500;
            }}
            .tag-matched {{
                background: rgba(34, 197, 94, 0.15);
                color: #16a34a;
                border: 1px solid rgba(34, 197, 94, 0.3);
            }}
            .tag-partial {{
                background: rgba(234, 179, 8, 0.15);
                color: #ca8a04;
                border: 1px solid rgba(234, 179, 8, 0.3);
            }}
            .tag-missing {{
                background: rgba(239, 68, 68, 0.15);
                color: #dc2626;
                border: 1px solid rgba(239, 68, 68, 0.3);
            }}
            .skills-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin: 12px 0;
            }}
            .skill-card {{
                background: #f9f9f9;
                border-radius: 6px;
                padding: 10px;
                border: 1px solid #e5e5e5;
            }}
            .card-title {{
                font-size: 14px;
                font-weight: 700;
                color: #000;
                text-align: center;
                margin-bottom: 10px;
            }}
            .recommendations-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin: 12px 0;
            }}
            .recommendation {{
                background: #f9f9f9;
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0;
                border: 1px solid #e5e5e5;
            }}
            .rec-title {{
                font-weight: 600;
                font-size: 13px;
                color: #000;
                margin-bottom: 8px;
            }}
            .rec-detail {{
                margin: 4px 0;
                font-size: 10px;
                color: #333;
            }}
            .rec-label {{
                color: #64748b;
            }}
            .rec-value-impact {{
                color: #22c55e;
                font-weight: 600;
            }}
            .rec-value-ease {{
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
        
        <div class="top-section">
            <div class="overall-score-box">
                <div class="overall-label">Overall Match</div>
                <div class="overall-value" style="color: {get_color_class(overall_pct)};">{overall_pct}%</div>
            </div>
    """
    
    # Add pie charts alongside overall score (matching website layout)
    # Always show chart boxes, even if image conversion failed
    html += f"""
            <div class="chart-box">
    """
    if tech_chart_img:
        html += f'<img src="data:image/png;base64,{tech_chart_img}" alt="Technical Skills Chart" style="max-width: 100%; height: auto;">'
    else:
        html += f'<div style="padding: 20px; text-align: center; color: #999;">Technical Chart</div>'
    html += f"""
                <div class="chart-label">Technical: {tech_pct}%</div>
            </div>
            <div class="chart-box">
    """
    if soft_chart_img:
        html += f'<img src="data:image/png;base64,{soft_chart_img}" alt="Soft Skills Chart" style="max-width: 100%; height: auto;">'
    else:
        html += f'<div style="padding: 20px; text-align: center; color: #999;">Soft Skills Chart</div>'
    html += f"""
                <div class="chart-label">Soft Skills: {soft_pct}%</div>
            </div>
    """
    
    html += """
        </div>
    """
    
    # Add radar chart (always show, even if conversion failed)
    html += """
        <div class="radar-chart">
            <div class="radar-title">Skills Coverage Radar</div>
    """
    if radar_chart_img:
        html += f'<img src="data:image/png;base64,{radar_chart_img}" alt="Radar Chart" style="max-width: 100%; height: auto;">'
    else:
        html += '<div style="padding: 40px; text-align: center; color: #999;">Radar Chart</div>'
    html += """
        </div>
    """
    
    html += """
        <div class="section">
            <div class="section-title">Detailed Skill Breakdown</div>
            <div class="skills-grid">
                <div class="skill-card">
                    <div class="card-title">Technical Skills</div>
                    <div class="subsection-title">Matched ({len(tech['matched'])})</div>
                    <div>
    """
    
    if tech['matched']:
        for jd, res, score in tech['matched']:
            html += f'<span class="skill-tag tag-matched">{jd}</span>'
    else:
        html += '<span style="color: #64748b;">None</span>'
    
    html += f"""
                    </div>
                    <div class="subsection-title">Partial Match ({len(tech['partial'])})</div>
                    <div>
    """
    
    if tech['partial']:
        for jd, res, score in tech['partial']:
            html += f'<span class="skill-tag tag-partial">{jd}</span>'
    else:
        html += '<span style="color: #64748b;">None</span>'
    
    html += f"""
                    </div>
                    <div class="subsection-title">Missing ({len(tech['missing'])})</div>
                    <div>
    """
    
    if tech['missing']:
        for jd, score in tech['missing']:
            html += f'<span class="skill-tag tag-missing">{jd}</span>'
    else:
        html += '<span style="color: #64748b;">None</span>'
    
    html += """
                    </div>
                </div>
                <div class="skill-card">
                    <div class="card-title">Soft Skills</div>
                    <div class="subsection-title">Matched ("""
    html += str(len(soft['matched']))
    html += """)</div>
                    <div>
    """
    
    if soft['matched']:
        for jd, res, score in soft['matched']:
            html += f'<span class="skill-tag tag-matched">{jd}</span>'
    else:
        html += '<span style="color: #64748b;">None</span>'
    
    html += f"""
                    </div>
                    <div class="subsection-title">Partial Match ({len(soft['partial'])})</div>
                    <div>
    """
    
    if soft['partial']:
        for jd, res, score in soft['partial']:
            html += f'<span class="skill-tag tag-partial">{jd}</span>'
    else:
        html += '<span style="color: #64748b;">None</span>'
    
    html += f"""
                    </div>
                    <div class="subsection-title">Missing ({len(soft['missing'])})</div>
                    <div>
    """
    
    if soft['missing']:
        for jd, score in soft['missing']:
            html += f'<span class="skill-tag tag-missing">{jd}</span>'
    else:
        html += '<span style="color: #64748b;">None</span>'
    
    html += """
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Recommendations</div>
    """
    
    if recommendations:
        html += '<div class="recommendations-grid">'
        for i, rec in enumerate(recommendations, 1):
            html += f"""
            <div class="recommendation">
                <div class="rec-title">{i}. {rec['skill']}</div>
                <div class="rec-detail"><span class="rec-label">Learning Time:</span> {rec['learning_time']}</div>
                <div class="rec-detail"><span class="rec-label">Match Impact:</span> <span class="rec-value-impact">+{rec['match_impact']}%</span></div>
                <div class="rec-detail"><span class="rec-label">Learning Ease:</span> <span class="rec-value-ease">{int(rec['similarity_score']*100)}%</span></div>
            """
            if rec['closest_existing']:
                html += f'<div class="rec-detail"><span class="rec-label">Similar to:</span> {rec["closest_existing"]} ({int(rec["closest_similarity"]*100)}%)</div>'
            html += "</div>"
        html += "</div>"
    else:
        html += "<p style='color: #64748b;'>No skill recommendations - you have all required skills!</p>"
    
    html += """
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
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

