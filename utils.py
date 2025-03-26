import base64
import io
import pandas as pd
import streamlit as st
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Wedge, Line, Circle, String
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.colors import HexColor
from assets.content import (
    MEDIA_AFFINITY_SITES, 
    TV_NETWORKS, 
    STREAMING_PLATFORMS, 
    PSYCHOGRAPHIC_HIGHLIGHTS,
    AUDIENCE_SUMMARY,
    NEXT_STEPS,
    METRICS
)

# Remove HTML tags from a string
def strip_html(text):
    """Remove HTML tags from a string."""
    return re.sub('<[^<]+?>', '', text).strip()

def create_pdf_download_link(scores, improvement_areas, percentile):
    """
    Create a PDF report and return a download link.
    
    Args:
        scores (dict): Dictionary of ARI scores
        improvement_areas (list): List of improvement areas
        percentile (float): Benchmark percentile
        
    Returns:
        str: HTML link for downloading the PDF
    """
    # Create a PDF buffer
    buf = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buf, 
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    heading1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=6,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=9
    )
    
    metric_title_style = ParagraphStyle(
        'MetricTitle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold'
    )
    
    metric_value_style = ParagraphStyle(
        'MetricValue',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    description_style = ParagraphStyle(
        'Description',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.darkgray
    )
    
    # Build content
    content = []
    
    # Add title
    content.append(Paragraph("Audience Resonance Index™ Scorecard", title_style))
    content.append(Spacer(1, 12))
    
    # Metric Breakdown
    content.append(Paragraph("Metric Breakdown", heading1_style))
    
    # Create tables for metrics
    metrics_data = []
    
    # Add headers
    headers = ["Metric", "Score", "Description"]
    
    # Row style for alternating colors
    row_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    
    # Add alternating row colors
    for i, (metric, score) in enumerate(scores.items()):
        level = "high" if score >= 7 else "medium" if score >= 4 else "low"
        description = METRICS[metric][level]
        
        metrics_data.append([
            Paragraph(f"<b>{metric}</b>", normal_style),
            Paragraph(f"<b>{score}/10</b>", normal_style),
            Paragraph(description, description_style)
        ])
        
        # Add row color
        if i % 2 == 0:
            row_styles.append(('BACKGROUND', (0, i+1), (-1, i+1), HexColor('#e0edff')))
        else:
            row_styles.append(('BACKGROUND', (0, i+1), (-1, i+1), HexColor('#f0f9ff')))
    
    # Create table
    metrics_table = Table(metrics_data, colWidths=[120, 50, 330], repeatRows=1)
    metrics_table.setStyle(TableStyle(row_styles))
    
    content.append(metrics_table)
    content.append(Spacer(1, 12))
    
    # Benchmark section
    content.append(Paragraph("Benchmark Comparison", heading1_style))
    
    benchmark_text = (f"This campaign ranks in the top {percentile}% of Gen Z-facing national campaigns "
                    f"for Audience Resonance Index™ (ARI). That means it outperforms the majority of "
                    f"peer campaigns in relevance, authenticity, and emotional connection — based on "
                    f"Digital Culture Group's analysis of 300+ national efforts.")
    
    improvement_text = f"<b>Biggest opportunity areas:</b> {', '.join(improvement_areas)}"
    
    content.append(Paragraph(benchmark_text, normal_style))
    content.append(Spacer(1, 6))
    content.append(Paragraph(improvement_text, normal_style))
    content.append(Spacer(1, 12))
    
    # Media Affinity section
    content.append(Paragraph("Media Affinities & Audience Insights", title_style))
    content.append(Spacer(1, 12))
    
    # Top Media Affinity Sites
    content.append(Paragraph("Top Media Affinity Sites", heading1_style))
    content.append(Paragraph("QVI = Quality Visit Index, a score indicating audience engagement strength", description_style))
    
    # Create media sites table with 5 columns
    media_site_data = []
    row = []
    
    for i, site in enumerate(MEDIA_AFFINITY_SITES):
        site_cell = f"""<b>{site['name']}</b><br/>
        {site['category']}<br/>
        <font color="#3b82f6"><b>QVI: {site['qvi']}</b></font><br/>
        <font color="#3b82f6">Visit Site</font>"""
        
        row.append(Paragraph(site_cell, normal_style))
        
        # After 5 sites, start a new row
        if (i + 1) % 5 == 0 or i == len(MEDIA_AFFINITY_SITES) - 1:
            # Pad the row if needed
            while len(row) < 5:
                row.append("")
            media_site_data.append(row)
            row = []
    
    # Create media table
    col_width = 100
    media_table = Table(media_site_data, colWidths=[col_width] * 5)
    
    # Define styles for the table
    media_styles = [
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    
    # Apply background colors to each cell with content
    for row_idx, row in enumerate(media_site_data):
        for col_idx, cell in enumerate(row):
            if cell:
                media_styles.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), HexColor('#e0edff')))
    
    media_table.setStyle(TableStyle(media_styles))
    
    content.append(media_table)
    content.append(Spacer(1, 12))
    
    # TV Network Affinities
    content.append(Paragraph("Top TV Network Affinities", heading1_style))
    
    # Create TV networks table with 5 columns
    tv_network_data = []
    row = []
    
    for i, network in enumerate(TV_NETWORKS):
        network_cell = f"""<b>{network['name']}</b><br/>
        {network['category']}<br/>
        <font color="#1e88e5"><b>QVI: {network['qvi']}</b></font>"""
        
        row.append(Paragraph(network_cell, normal_style))
        
        # After 5 networks, start a new row
        if (i + 1) % 5 == 0 or i == len(TV_NETWORKS) - 1:
            # Pad the row if needed
            while len(row) < 5:
                row.append("")
            tv_network_data.append(row)
            row = []
    
    # Create TV network table
    tv_network_table = Table(tv_network_data, colWidths=[col_width] * 5)
    
    # Define styles for the table
    tv_styles = [
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    
    # Apply background colors to each cell with content
    for row_idx, row in enumerate(tv_network_data):
        for col_idx, cell in enumerate(row):
            if cell:
                tv_styles.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), HexColor('#dbeafe')))
    
    tv_network_table.setStyle(TableStyle(tv_styles))
    
    content.append(tv_network_table)
    content.append(Spacer(1, 12))
    
    # Streaming Platforms
    content.append(Paragraph("Top Streaming Platforms", heading1_style))
    
    # Create streaming platforms table with 3 columns
    streaming_data = []
    row = []
    
    for i, platform in enumerate(STREAMING_PLATFORMS):
        platform_cell = f"""<b>{platform['name']}</b><br/>
        {platform['category']}<br/>
        <font color="#059669"><b>QVI: {platform['qvi']}</b></font>"""
        
        row.append(Paragraph(platform_cell, normal_style))
        
        # After 3 platforms, start a new row
        if (i + 1) % 3 == 0 or i == len(STREAMING_PLATFORMS) - 1:
            # Pad the row if needed
            while len(row) < 3:
                row.append("")
            streaming_data.append(row)
            row = []
    
    # Create streaming table
    streaming_table = Table(streaming_data, colWidths=[170] * 3)
    
    # Define styles for the table
    streaming_styles = [
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    
    # Apply background colors to each cell with content
    for row_idx, row in enumerate(streaming_data):
        for col_idx, cell in enumerate(row):
            if cell:
                streaming_styles.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), HexColor('#d1fae5')))
    
    streaming_table.setStyle(TableStyle(streaming_styles))
    
    content.append(streaming_table)
    content.append(Spacer(1, 12))
    
    # Psychographic Highlights
    content.append(Paragraph("Psychographic Highlights", heading1_style))
    psycho_text = strip_html(PSYCHOGRAPHIC_HIGHLIGHTS)
    content.append(Paragraph(psycho_text, normal_style))
    content.append(Spacer(1, 12))
    
    # Audience Summary
    content.append(Paragraph("Audience Summary", heading1_style))
    audience_text = strip_html(AUDIENCE_SUMMARY)
    content.append(Paragraph(audience_text, normal_style))
    content.append(Spacer(1, 12))
    
    # What's Next?
    content.append(Paragraph("What's Next?", heading1_style))
    next_text = strip_html(NEXT_STEPS)
    content.append(Paragraph(next_text, normal_style))
    
    content.append(Paragraph('Let\'s build a breakthrough growth strategy — Digital Culture Group has proven tactics that boost underperforming areas.', 
                           ParagraphStyle('Blue', parent=normal_style, textColor=HexColor('#5865f2'))))
    content.append(Spacer(1, 12))
    
    # Footer
    content.append(Paragraph('Powered by Digital Culture Group © 2023', 
                          ParagraphStyle('Footer', parent=normal_style, alignment=TA_CENTER, fontSize=8, textColor=colors.gray)))
    
    # Build the PDF
    doc.build(content)
    
    # Generate download link
    b64 = base64.b64encode(buf.getbuffer()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="ari_scorecard.pdf" style="display: inline-block; padding: 10px 15px; background-color: #5865f2; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">⬇ Download Scorecard as PDF</a>'

def display_metric_bar(metric, score):
    """
    Display a metric with a colored progress bar.
    
    Args:
        metric (str): Name of the metric
        score (float): Score value (0-10)
    """
    # Create a container for the metric
    metric_container = st.container()
    
    with metric_container:
        # Display metric label and score
        col1, col2 = st.columns([4, 1])
        col1.markdown(f"**{metric}**")
        col2.markdown(f"**{score}/10**")
        
        # Show the progress bar
        st.progress(score/10, "rgb(88, 101, 242)")

def get_tone_of_brief(brief_text):
    """
    Analyze the tone of a campaign brief. This is a simulated function that
    would be replaced with actual NLP analysis in a real implementation.
    
    Args:
        brief_text (str): The campaign brief text
        
    Returns:
        str: Tone description
    """
    tones = [
        "professional and strategic",
        "creative and innovative",
        "data-driven and analytical",
        "adventurous and bold",
        "modern and tech-savvy",
        "community-focused and authentic"
    ]
    
    if not brief_text or brief_text.strip() == "":
        return tones[0]
    
    # Choose tone based on text length as a simple heuristic
    # This would be replaced with actual tone analysis in a real implementation
    index = len(brief_text.strip()) % len(tones)
    return tones[index]
