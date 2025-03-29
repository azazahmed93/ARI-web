import base64
import io
import pandas as pd
import numpy as np
import math
import streamlit as st
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Wedge, Line, Circle, String, Rect, PolyLine
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.lib.colors import HexColor, Color
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

# Custom progress bar class for the PDF report
class ProgressBar(Flowable):
    """
    Custom flowable that draws a progress bar
    """
    def __init__(self, width=400, height=20, value=0.5, fillColor=HexColor('#5865f2'), backgroundColor=HexColor('#e0edff')):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.value = min(max(value, 0), 1)  # Ensure value is between 0 and 1
        self.fillColor = fillColor
        self.backgroundColor = backgroundColor
        
    def draw(self):
        # Draw background
        self.canv.setFillColor(self.backgroundColor)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        
        # Draw filled portion based on value
        self.canv.setFillColor(self.fillColor)
        fill_width = self.width * self.value
        self.canv.rect(0, 0, fill_width, self.height, fill=1, stroke=0)

# Radar chart for the PDF report
class ARIRadarChart(Flowable):
    """
    Radar chart for ARI metrics
    """
    def __init__(self, scores, width=400, height=400):
        Flowable.__init__(self)
        self.scores = scores
        self.width = width
        self.height = height
        
    def draw(self):
        # Create the drawing
        drawing = Drawing(self.width, self.height)
        
        # Create radar chart
        radar = SpiderChart()
        radar.x = self.width / 2
        radar.y = self.height / 2
        radar.width = self.width * 0.8
        radar.height = self.height * 0.8
        
        # Set data
        data = [list(self.scores.values())]
        radar.data = data
        
        # Set spoke labels (metric names)
        radar.labels = list(self.scores.keys())
        
        # Set style
        radar.fillColor = HexColor("#5865f230")  # Semi-transparent purple
        radar.strokeColor = HexColor("#5865f2")  # Purple
        radar.strokeWidth = 2
        radar.spokes.strokeDashArray = (2, 2)
        radar.spokes.strokeWidth = 0.5
        radar.spokes.strokeColor = HexColor("#a1a1aa")
        
        # Add background circles
        for i in range(1, 11, 2):
            circle = Circle(radar.x, radar.y, i * radar.width / 20)
            circle.fillColor = None
            circle.strokeColor = HexColor("#e5e7eb")
            circle.strokeWidth = 0.5
            drawing.add(circle)
        
        # Add the radar chart to the drawing
        drawing.add(radar)
        
        # Render the drawing
        drawing.drawOn(self.canv, 0, 0)

def create_pdf_download_link(scores, improvement_areas, percentile, brand_name="Unknown", industry="General", product_type="Product"):
    """
    Create a PDF report and return a download link.
    
    Args:
        scores (dict): Dictionary of ARI scores
        improvement_areas (list): List of improvement areas
        percentile (float): Benchmark percentile
        brand_name (str): Name of the brand
        industry (str): Industry of the brand
        product_type (str): Type of product being promoted
        
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
        spaceAfter=12,
        textColor=HexColor('#000000')
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
        textColor=HexColor('#707070')
    )
    
    # Build content
    content = []
    
    # Create a styled header for the PDF
    header_data = [[
        # Add logo visual element - creating a simple "DCG" logo with shapes
        (lambda: (draw := Drawing(30, 30, hAlign='LEFT'),
                 draw.add(Circle(15, 15, 15, fillColor=HexColor('#5865f2'), strokeColor=None)),
                 draw.add(String(15, 13, "DCG", fontSize=8, fillColor=HexColor('#FFFFFF'), textAnchor='middle')),
                 draw))(),
        # Add title text
        Paragraph(f"AUDIENCE RESONANCE INDEX™", 
                 ParagraphStyle('HeaderTitle', fontSize=14, textColor=HexColor('#5865f2'), fontName='Helvetica-Bold')),
        # Add date on the right
        Paragraph(f"REPORT DATE: MARCH 29, 2025", 
                 ParagraphStyle('HeaderDate', fontSize=8, alignment=TA_RIGHT))
    ]]
    
    # Create header table
    header_table = Table(header_data, colWidths=[50, 300, 150], rowHeights=[40])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8fafc')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, HexColor('#5865f2')),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    # Add the header
    content.append(header_table)
    content.append(Spacer(1, 20))
    
    # Add title with brand name if available
    if brand_name != "Unknown":
        content.append(Paragraph(f"{brand_name} Audience Resonance Index™ Scorecard", title_style))
    else:
        content.append(Paragraph("Audience Resonance Index™ Scorecard", title_style))
    content.append(Spacer(1, 12))
    
    # Add brand info if available
    if brand_name != "Unknown" and industry != "General":
        # Create styled brand info box
        brand_info_table = Table([[
            Paragraph(f"Industry: <b>{industry}</b> | Product Type: <b>{product_type}</b>", 
                    ParagraphStyle('BrandInfo', parent=normal_style, alignment=TA_CENTER))
        ]], colWidths=[500])
        brand_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#dbeafe')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(brand_info_table)
        content.append(Spacer(1, 12))
    
    # Metric Breakdown
    content.append(Paragraph("Metric Breakdown", heading1_style))
    
    # Add radar chart
    content.append(Paragraph("Audience Resonance Index™ Visualization", heading1_style))
    content.append(Spacer(1, 6))
    
    # Calculate radar chart size based on metrics count
    radar_chart = ARIRadarChart(scores, width=400, height=300)
    content.append(radar_chart)
    content.append(Spacer(1, 12))
    
    # Metric Breakdown with progress bars
    content.append(Paragraph("Metric Breakdown", heading1_style))
    content.append(Spacer(1, 6))
    
    # Create metrics with progress bars instead of table
    for metric, score in scores.items():
        # Metric name and score in a table
        metric_header = Table([[
            Paragraph(f"<b>{metric}</b>", metric_title_style),
            Paragraph(f"<b>{score}/10</b>", ParagraphStyle('Score', parent=metric_value_style, alignment=TA_RIGHT))
        ]], colWidths=[400, 100])
        metric_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#FFFFFF')),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ]))
        content.append(metric_header)
        
        # Progress bar
        level = "high" if score >= 7 else "medium" if score >= 4 else "low"
        
        # Select color based on score
        if score >= 7:
            color = HexColor('#4ade80')  # Green for high scores
        elif score >= 4:
            color = HexColor('#3b82f6')  # Blue for medium scores
        else:
            color = HexColor('#f43f5e')  # Red for low scores
            
        # Add progress bar
        progress_bar = ProgressBar(width=500, height=14, value=score/10, fillColor=color)
        content.append(progress_bar)
        
        # Description
        description = METRICS[metric][level]
        content.append(Paragraph(description, description_style))
        content.append(Spacer(1, 12))
    
    # Benchmark section with visualization
    content.append(Paragraph("Hyperdimensional Campaign Performance Matrix", heading1_style))
    
    # Create benchmark visualization
    benchmark_viz = Drawing(500, 70)
    
    # Background rectangle
    background = Rect(0, 0, 500, 60, fillColor=HexColor('#f8fafc'), strokeColor=None)
    benchmark_viz.add(background)
    
    # Percentile gauge colors
    colors = [
        HexColor('#ef4444'),  # Red for low
        HexColor('#f97316'),  # Orange for medium low
        HexColor('#facc15'),  # Yellow for medium
        HexColor('#84cc16'),  # Light green for medium high
        HexColor('#10b981')   # Green for high
    ]
    
    # Draw the gauge background
    gauge_width = 400
    gauge_height = 20
    gauge_x = 50
    gauge_y = 20
    
    # Draw colored gauge sections
    section_width = gauge_width / 5
    for i in range(5):
        x = gauge_x + (i * section_width)
        rect = Rect(x, gauge_y, section_width, gauge_height, 
                    fillColor=colors[i], strokeColor=None)
        benchmark_viz.add(rect)
    
    # Calculate position of percentile indicator
    percentile_pos = gauge_x + (gauge_width * percentile / 100)
    
    # Add indicator triangle
    indicator = PolyLine(
        points=[
            percentile_pos, gauge_y + gauge_height + 10,
            percentile_pos - 8, gauge_y + gauge_height,
            percentile_pos + 8, gauge_y + gauge_height
        ],
        fillColor=HexColor('#5865f2'),
        strokeColor=None
    )
    benchmark_viz.add(indicator)
    
    # Add percentile text
    percentile_text = String(
        percentile_pos, gauge_y - 15,
        f"{percentile}%",
        fontSize=12,
        fillColor=HexColor('#5865f2'),
        textAnchor='middle'
    )
    benchmark_viz.add(percentile_text)
    
    # Add the benchmark visualization
    content.append(benchmark_viz)
    content.append(Spacer(1, 6))
    
    # Create custom benchmark text based on brand information
    if brand_name != "Unknown" and industry != "General":
        benchmark_text = (f"This {brand_name} campaign ranks in the top {percentile}% of {industry} campaigns "
                        f"for Audience Resonance Index™ (ARI). That means it outperforms the majority of "
                        f"peer campaigns in relevance, authenticity, and emotional connection — based on "
                        f"Digital Culture Group's analysis of 300+ {industry.lower()} efforts.")
        
        improvement_text = (f"<b>Biggest opportunity areas for a {product_type} in the {industry} industry:</b> "
                         f"{', '.join(improvement_areas)}")
    else:
        benchmark_text = (f"This campaign ranks in the top {percentile}% of Gen Z-facing national campaigns "
                        f"for Audience Resonance Index™ (ARI). That means it outperforms the majority of "
                        f"peer campaigns in relevance, authenticity, and emotional connection — based on "
                        f"Digital Culture Group's analysis of 300+ national efforts.")
        
        improvement_text = f"<b>Biggest opportunity areas:</b> {', '.join(improvement_areas)}"
    
    content.append(Paragraph(benchmark_text, normal_style))
    content.append(Spacer(1, 6))
    
    # Improvement areas with styling
    content.append(Paragraph("Priority Enhancement Opportunities", 
                           ParagraphStyle('OpportunityHeading', parent=heading1_style, fontSize=12)))
    content.append(Spacer(1, 4))
    
    # Create a table for improvement areas
    improvement_data = []
    
    # Create a row for each improvement area with an arrow icon
    for area in improvement_areas:
        improvement_data.append([
            Paragraph(f"→ {area}", 
                    ParagraphStyle('Improvement', parent=normal_style, textColor=HexColor('#5865f2')))
        ])
    
    # Create table with improvement areas
    improvement_table = Table(improvement_data, colWidths=[500])
    improvement_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f5f7fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#FFFFFF')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(improvement_table)
    content.append(Spacer(1, 12))
    
    # Media Affinity section with styled header
    media_header = Table([[
        Paragraph("Media Affinities & Audience Insights", title_style)
    ]], colWidths=[500])
    media_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#5865f2')),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    content.append(media_header)
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
                row.append(Paragraph("", normal_style))
            media_site_data.append(row)
            row = []
    
    # Create media table
    col_width = 100
    media_table = Table(media_site_data, colWidths=[col_width] * 5)
    
    # Define styles for the table
    media_styles = [
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#FFFFFF')),
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
            if isinstance(cell, Paragraph):
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
                row.append(Paragraph("", normal_style))
            tv_network_data.append(row)
            row = []
    
    # Create TV network table
    tv_network_table = Table(tv_network_data, colWidths=[col_width] * 5)
    
    # Define styles for the table
    tv_styles = [
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#FFFFFF')),
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
            if isinstance(cell, Paragraph):
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
                row.append(Paragraph("", normal_style))
            streaming_data.append(row)
            row = []
    
    # Create streaming table
    streaming_table = Table(streaming_data, colWidths=[170] * 3)
    
    # Define styles for the table
    streaming_styles = [
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#FFFFFF')),
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
            if isinstance(cell, Paragraph):
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
    content.append(Paragraph('© 2025 Digital Culture Group, LLC. All rights reserved', 
                          ParagraphStyle('Footer', parent=normal_style, alignment=TA_CENTER, fontSize=8, textColor=HexColor('#808080'))))
    
    # Build the PDF
    doc.build(content)
    
    # Generate download link
    b64 = base64.b64encode(buf.getbuffer()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="ari_scorecard.pdf" style="display: inline-block; padding: 10px 15px; background-color: #5865f2; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">⬇ Download Report</a>'

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
