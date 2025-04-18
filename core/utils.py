import base64
import io
import pandas as pd
import streamlit as st
import re
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Wedge, Line, Circle, String, Rect
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor, toColor
from assets.content import (
    PSYCHOGRAPHIC_HIGHLIGHTS,
    AUDIENCE_SUMMARY,
    NEXT_STEPS,
    METRICS
)
from core.database import benchmark_db, BLOCKED_KEYWORDS
import docx
import PyPDF2

# Remove HTML tags from a string
def strip_html(text):
    """Remove HTML tags from a string."""
    return re.sub('<[^<]+?>', '', text).strip()

def create_pdf_download_link(scores, improvement_areas, percentile, brand_name="Unknown", industry="General", product_type="Product", 
                       include_sections=None, brief_text=""):
    """
    Create a PDF report and return a download link.
    
    Args:
        scores (dict): Dictionary of ARI scores
        improvement_areas (list): List of improvement areas
        percentile (float): Benchmark percentile
        brand_name (str): Name of the brand
        industry (str): Industry of the brand
        product_type (str): Type of product being promoted
        include_sections (dict, optional): Dictionary of section flags to include/exclude
            keys: 'metrics', 'benchmark', 'media_affinities', 'tv_networks', 
                 'streaming', 'psychographic', 'audience', 'next_steps', 'trends'
            values: boolean (True to include, False to exclude)
        brief_text (str, optional): The full text of the brief for context-specific insights
    
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
    
    # Default sections to include if not specified
    if include_sections is None:
        include_sections = {
            'metrics': True,
            'benchmark': True,
            'media_affinities': True,
            'tv_networks': True,
            'streaming': True,
            'psychographic': True,
            'audience': True,
            'competitor_tactics': True,
            'trends': True
        }
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.black
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
    
    # Add title with brand name if available
    if brand_name != "Unknown":
        content.append(Paragraph(f"{brand_name} Audience Resonance Index™ Scorecard", title_style))
    else:
        content.append(Paragraph("Audience Resonance Index™ Scorecard", title_style))
    content.append(Spacer(1, 12))
    
    # Remove industry info as requested
    if brand_name != "Unknown":
        content.append(Paragraph(f"Brand: {brand_name}", 
                               ParagraphStyle('BrandInfo', parent=normal_style, alignment=TA_CENTER)))
        content.append(Spacer(1, 12))
    
    # Metric Breakdown
    if include_sections.get('metrics', True):
        content.append(Paragraph("Metric Breakdown", heading1_style))
        
        # Create tables for metrics
        metrics_data = []
        
        # Add headers
        headers = ["Metric", "Score", "Description"]
        
        # Create a header for the table
        metrics_data.append([
            Paragraph("<b>Metric</b>", normal_style),
            Paragraph("<b>Score</b>", normal_style),
            Paragraph("<b>Description</b>", normal_style)
        ])
        
        # Row styles
        row_styles = [
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#dbeafe')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        
        # Add metrics data with alternating row colors
        for i, (metric, score) in enumerate(scores.items()):
            level = "high" if score >= 7 else "medium" if score >= 4 else "low"
            description = METRICS[metric][level]
            
            # All text should be normal black with consistent styling
            metrics_data.append([
                Paragraph(f"<b>{metric}</b>", normal_style),
                Paragraph(f"<b>{score}/10</b>", normal_style),
                Paragraph(description, description_style)
            ])
            
            # Add alternating row colors
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
    if include_sections.get('benchmark', True):
        content.append(Paragraph("Benchmark Comparison", heading1_style))
        
        # Simplified benchmark text without industry references
        benchmark_text = (f"This campaign ranks in the top {percentile}% of all campaigns "
                        f"for Audience Resonance Index™ (ARI). That means it outperforms the majority of "
                        f"campaigns in relevance, authenticity, and emotional connection — based on "
                        f"Digital Culture Group's analysis of 300+ marketing efforts.")
        
        improvement_text = f"<b>Biggest opportunity areas:</b> {', '.join(improvement_areas)}"
        
        content.append(Paragraph(benchmark_text, normal_style))
        content.append(Spacer(1, 6))
        content.append(Paragraph(improvement_text, normal_style))
        content.append(Spacer(1, 12))
    
    # Media Affinity section - use the same title_style for consistent centering
    if any([include_sections.get('media_affinities', True), 
            include_sections.get('tv_networks', True),
            include_sections.get('streaming', True)]):
        content.append(Paragraph("Media Affinities & Audience Insights", title_style))
        content.append(Spacer(1, 12))
    
    # Top Media Affinity Sites
    if include_sections.get('media_affinities', True):
        content.append(Paragraph("Top Media Affinity Sites", heading1_style))
        content.append(Paragraph("QVI = Quality Visit Index, a score indicating audience engagement strength", description_style))
        
        # Create media sites table with 5 columns
        media_site_data = []
        row = []
        
        for i, site in enumerate(st.session_state.media_affinity['media_affinity_sites']):
            site_cell = f"""<b>{site['name']}</b><br/>
            {site['category']}<br/>
            <font color="#3b82f6"><b>QVI: {site['qvi']}</b></font><br/>
            <font color="#3b82f6">Visit Site</font>"""
            
            row.append(Paragraph(site_cell, normal_style))
            
            # After 5 sites, start a new row
            if (i + 1) % 5 == 0 or i == len(st.session_state.media_affinity['media_affinity_sites']) - 1:
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
    if include_sections.get('tv_networks', True):
        content.append(Paragraph("Top TV Network Affinities", heading1_style))
        
        # Create TV networks table with 5 columns
        tv_network_data = []
        row = []
        tv_col_width = 100  # Define column width for TV networks
        
        for i, network in enumerate(st.session_state.audience_media_consumption['tv_networks']):
            network_cell = f"""<b>{network['name']}</b><br/>
            {network['category']}<br/>
            <font color="#1e88e5"><b>QVI: {network['qvi']}</b></font>"""
            
            row.append(Paragraph(network_cell, normal_style))
            
            # After 5 networks, start a new row
            if (i + 1) % 5 == 0 or i == len(st.session_state.audience_media_consumption['tv_networks']) - 1:
                # Pad the row if needed
                while len(row) < 5:
                    row.append("")
                tv_network_data.append(row)
                row = []
        
        # Create TV network table
        tv_network_table = Table(tv_network_data, colWidths=[tv_col_width] * 5)
        
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
    if include_sections.get('streaming', True):
        content.append(Paragraph("Top Streaming Platforms", heading1_style))
        
        # Create streaming platforms table with 3 columns
        streaming_data = []
        row = []
        
        for i, platform in enumerate(st.session_state.audience_media_consumption['streaming_platforms']):
            platform_cell = f"""<b>{platform['name']}</b><br/>
            {platform['category']}<br/>
            <font color="#059669"><b>QVI: {platform['qvi']}</b></font>"""
            
            row.append(Paragraph(platform_cell, normal_style))
            
            # After 3 platforms, start a new row
            if (i + 1) % 3 == 0 or i == len(st.session_state.audience_media_consumption['streaming_platforms']) - 1:
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
    if include_sections.get('psychographic', True):
        content.append(Paragraph("Psychographic Highlights", heading1_style))
        psycho_text = strip_html(st.session_state.pychographic_highlights)
        content.append(Paragraph(psycho_text, normal_style))
        content.append(Spacer(1, 12))
    
    # Audience Summary
    if include_sections.get('audience', True):
        content.append(Paragraph("Audience Summary", heading1_style))
        
        # Check if we have dynamic audience segments in session state
        has_dynamic_segments = False
        if hasattr(st, 'session_state') and 'audience_segments' in st.session_state and st.session_state.audience_segments:
            segments = st.session_state.audience_segments.get('segments', [])
            has_dynamic_segments = len(segments) > 0
        
        # If we have dynamic segments, format them nicely for the PDF
        if has_dynamic_segments:
            segments = st.session_state.audience_segments.get('segments', [])
            
            # Add Core Audience (Primary)
            if len(segments) > 0:
                primary = segments[0]
                content.append(Paragraph("Core Audience:", 
                                ParagraphStyle('SubHeading', parent=normal_style, fontSize=11, fontName='Helvetica-Bold')))
                
                # Format the primary audience description
                primary_text = f"{primary.get('name', 'Primary Audience')}: {primary.get('description', 'Core target audience')}"
                content.append(Paragraph(primary_text, normal_style))
                
                # Add demographics if available
                targeting_params = primary.get('targeting_params', {})
                if targeting_params:
                    demo_parts = []
                    if 'age_range' in targeting_params:
                        demo_parts.append(f"Age: {targeting_params['age_range']}")
                    if 'gender_targeting' in targeting_params:
                        demo_parts.append(f"Gender: {targeting_params['gender_targeting']}")
                    if 'income_targeting' in targeting_params:
                        demo_parts.append(f"Income: {targeting_params['income_targeting']}")
                    
                    if demo_parts:
                        demo_text = "Demographics: " + " | ".join(demo_parts)
                        content.append(Paragraph(demo_text, normal_style))
                
                # Add platform information with appropriate metrics
                platform_targeting = primary.get('platform_targeting', [])
                if platform_targeting and len(platform_targeting) > 0:
                    platform = platform_targeting[0].get('platform', '')
                    
                    # Determine appropriate metric based on platform type
                    performance = primary.get('expected_performance', {})
                    metric_value = performance.get('CTR', 'N/A')
                    metric_name = "Expected CTR"
                    
                    # Check for video platforms
                    if platform and ('video' in platform.lower() or 'ott' in platform.lower() 
                                    or 'ctv' in platform.lower() or 'streaming' in platform.lower()):
                        metric_name = "Expected VCR"
                        metric_value = "70-95%"  # Dynamic range for video completion
                    
                    # Check for audio platforms
                    elif platform and ('audio' in platform.lower() or 'podcast' in platform.lower() 
                                      or 'music' in platform.lower()):
                        metric_name = "Expected LTR"
                        metric_value = "80-95%"  # Dynamic range for audio listen-through
                    
                    platform_text = f"Recommended Platform: {platform} ({metric_name}: {metric_value})"
                    content.append(Paragraph(platform_text, normal_style))
                
                content.append(Spacer(1, 8))
            
            # Add Secondary Growth Audience
            if len(segments) > 1:
                secondary = segments[1]
                content.append(Paragraph("Secondary Growth Audience:", 
                                ParagraphStyle('SubHeading', parent=normal_style, fontSize=11, fontName='Helvetica-Bold')))
                
                # Format the secondary audience description
                secondary_text = f"{secondary.get('name', 'Secondary Growth Audience')}: {secondary.get('description', 'Additional target audience')}"
                content.append(Paragraph(secondary_text, normal_style))
                
                # Add platform information with appropriate metrics
                platform_targeting = secondary.get('platform_targeting', [])
                if platform_targeting and len(platform_targeting) > 0:
                    platform = platform_targeting[0].get('platform', '')
                    
                    # Determine appropriate metric based on platform type
                    performance = secondary.get('expected_performance', {})
                    metric_value = performance.get('CTR', 'N/A')
                    metric_name = "Expected CTR"
                    
                    # Check for video platforms
                    if platform and ('video' in platform.lower() or 'ott' in platform.lower() 
                                    or 'ctv' in platform.lower() or 'streaming' in platform.lower()):
                        metric_name = "Expected VCR"
                        metric_value = "70-95%"  # Dynamic range for video completion
                    
                    # Check for audio platforms
                    elif platform and ('audio' in platform.lower() or 'podcast' in platform.lower() 
                                      or 'music' in platform.lower()):
                        metric_name = "Expected LTR"
                        metric_value = "80-95%"  # Dynamic range for audio listen-through
                    
                    platform_text = f"Recommended Platform: {platform} ({metric_name}: {metric_value})"
                    content.append(Paragraph(platform_text, normal_style))
                
                content.append(Spacer(1, 8))
            
            # Add Emerging Audience Opportunity
            if len(segments) > 2:
                growth = segments[-1]  # Use the last segment as growth opportunity
                content.append(Paragraph("Emerging Audience Opportunity:", 
                                ParagraphStyle('SubHeading', parent=normal_style, fontSize=11, fontName='Helvetica-Bold')))
                
                # Format the growth audience description
                growth_text = f"{growth.get('name', 'Emerging Audience')}: {growth.get('description', 'Growth potential audience')}"
                content.append(Paragraph(growth_text, normal_style))
                
                # Add interests if available
                interests = growth.get('interest_categories', [])
                if interests:
                    interests_text = "Key Interests: " + ", ".join(interests)
                    content.append(Paragraph(interests_text, normal_style))
                
                # Add platform information with appropriate metrics
                platform_targeting = growth.get('platform_targeting', [])
                if platform_targeting and len(platform_targeting) > 0:
                    platform = platform_targeting[0].get('platform', '')
                    
                    # Determine appropriate metric based on platform type
                    performance = growth.get('expected_performance', {})
                    metric_value = performance.get('CTR', 'N/A')
                    metric_name = "Expected CTR"
                    
                    # Check for video platforms
                    if platform and ('video' in platform.lower() or 'ott' in platform.lower() 
                                    or 'ctv' in platform.lower() or 'streaming' in platform.lower()):
                        metric_name = "Expected VCR"
                        metric_value = "70-95%"  # Dynamic range for video completion
                    
                    # Check for audio platforms
                    elif platform and ('audio' in platform.lower() or 'podcast' in platform.lower() 
                                      or 'music' in platform.lower()):
                        metric_name = "Expected LTR"
                        metric_value = "80-95%"  # Dynamic range for audio listen-through
                    
                    platform_text = f"Recommended Platform: {platform} ({metric_name}: {metric_value})"
                    content.append(Paragraph(platform_text, normal_style))
            
        else:
            # Determine if this is a SiteOne Hispanic campaign by checking the brief text
            is_siteone_hispanic = False
            if brief_text and "SiteOne" in brief_text and ("Hispanic" in brief_text or "Spanish" in brief_text):
                is_siteone_hispanic = True
                
            # Use the static audience summary, selecting the appropriate one based on campaign type
            if is_siteone_hispanic:
                # Import here to avoid circular import issues
                from assets.content import SITEONE_HISPANIC_SUMMARY
                audience_text = strip_html(SITEONE_HISPANIC_SUMMARY)
            else:
                audience_text = strip_html(AUDIENCE_SUMMARY)
                
            content.append(Paragraph(audience_text, normal_style))
            
        content.append(Spacer(1, 12))
    
    # Competitor Tactics
    if include_sections.get('competitor_tactics', True):
        content.append(Paragraph("Competitor Tactics", heading1_style))
        
        # Check if we have competitor tactics in session state
        has_competitor_tactics = False
        competitor_tactics = []
        if hasattr(st, 'session_state') and 'competitor_tactics' in st.session_state and st.session_state.competitor_tactics:
            if isinstance(st.session_state.competitor_tactics, list):
                competitor_tactics = st.session_state.competitor_tactics
                has_competitor_tactics = len(competitor_tactics) > 0
            else:
                has_competitor_tactics = bool(st.session_state.competitor_tactics)
        
        # If we have tactics, format them nicely for the PDF
        if has_competitor_tactics and isinstance(competitor_tactics, list) and len(competitor_tactics) > 0:
            for i, tactic in enumerate(competitor_tactics):
                content.append(Paragraph(f"{i+1}. {tactic}", normal_style))
                content.append(Spacer(1, 6))
        else:
            # Default competitor tactics text
            content.append(Paragraph("Competitor tactics analysis not available. Visit the Competitor Tactics tab to generate custom competitive strategy recommendations.", normal_style))
        
        content.append(Spacer(1, 12))
    
    # Marketing Trend Analysis
    if include_sections.get('trends', True):
        content.append(Paragraph("Marketing Trend Analysis", heading1_style))
        
        # Add trend insights
        content.append(Paragraph("Top Marketing Trends Relevant to Your Campaign", 
                              ParagraphStyle('SubHeading', parent=normal_style, fontSize=12, fontName='Helvetica-Bold')))
        
        # Import marketing trends data
        from app.components.marketing_trends import generate_simplified_trend_data
        top_trends, top_markets, top_combinations = generate_simplified_trend_data(brief_text=brief_text)
        
        # Add top trends
        content.append(Paragraph("Emerging Trends:", 
                              ParagraphStyle('BulletHeader', parent=normal_style, fontSize=11, fontName='Helvetica-Bold')))
        
        for trend in top_trends[:3]:  # Show top 3 trends
            if isinstance(trend, dict):
                trend_text = f"• {trend.get('trend', 'Unknown')}: {trend.get('growth', 0)}% growth"
            else:
                # Handle case where trend might be a float or other type
                trend_text = f"• Generic Trend: {trend}% growth"
            content.append(Paragraph(trend_text, normal_style))
        
        content.append(Spacer(1, 6))
        
        # Add top markets
        content.append(Paragraph("High-Performance Targets:", 
                              ParagraphStyle('BulletHeader', parent=normal_style, fontSize=11, fontName='Helvetica-Bold')))
        
        for market in top_markets[:3]:  # Show top 3 markets
            if isinstance(market, dict):
                market_text = f"• {market.get('market', 'Unknown')}: {market.get('index', 0)} engagement index"
            else:
                # Handle case where market might be a float or other type
                market_text = f"• Generic Market: {market} engagement index"
            content.append(Paragraph(market_text, normal_style))
        
        content.append(Spacer(1, 6))
        
        # Add trend applications
        content.append(Paragraph("Strategic Applications:", 
                              ParagraphStyle('BulletHeader', parent=normal_style, fontSize=11, fontName='Helvetica-Bold')))
        
        # Get trend applications from AI insights if available in session state
        trend_applications = []
        if hasattr(st, 'session_state') and 'ai_insights' in st.session_state:
            trend_applications = st.session_state.ai_insights.get('trends', [])
        
        # If AI insights not available, use default applications
        if not trend_applications:
            trend_applications = [
                {"trend": "Interactive Video", "application": "Implement interactive video ads that allow viewers to engage with product features"},
                {"trend": "Audio Advertising", "application": "Develop targeted audio ads for streaming platforms to reach on-the-go audiences"},
                {"trend": "Immersive Experiences", "application": "Create virtual try-on experiences to boost engagement and purchase intent"}
            ]
        
        # Add trend applications to the report
        for app in trend_applications[:3]:  # Show top 3 applications
            if isinstance(app, dict):
                app_text = f"• {app.get('trend', 'Unknown')}: {app.get('application', 'Implementation details')}"
            else:
                # Handle case where app might be a float or other type
                app_text = f"• Generic Application: {app}"
            content.append(Paragraph(app_text, normal_style))
            
        content.append(Spacer(1, 12))
    
    # What's Next?
    if include_sections.get('next_steps', True):
        content.append(Paragraph("What's Next?", heading1_style))
        next_text = strip_html(NEXT_STEPS)
        content.append(Paragraph(next_text, normal_style))
        
        content.append(Paragraph('Let\'s build a breakthrough growth strategy — Digital Culture Group has proven tactics that boost underperforming areas.', 
                            ParagraphStyle('Blue', parent=normal_style, textColor=HexColor('#5865f2'))))
    content.append(Spacer(1, 12))
    
    # Footer
    content.append(Paragraph('© 2025 Digital Culture Group, LLC. All rights reserved.', 
                          ParagraphStyle('Footer', parent=normal_style, alignment=TA_CENTER, fontSize=8, textColor=colors.gray)))
    
    # Build the PDF
    doc.build(content)
    
    # Generate download link
    b64 = base64.b64encode(buf.getbuffer()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="ari_scorecard.pdf" style="display: inline-block; padding: 10px 15px; background-color: #5865f2; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">⬇ Download Report</a>'

def create_infographic_download_link(scores, improvement_areas, percentile, brand_name="Unknown", top_audience=None):
    """
    Create a shareable infographic that can be sent via email.
    
    Args:
        scores (dict): Dictionary of ARI scores
        improvement_areas (list): List of improvement areas 
        percentile (float): Benchmark percentile
        brand_name (str): Name of the brand
        top_audience (dict, optional): Top audience segment details
        
    Returns:
        str: HTML link for downloading the infographic
    """
    # Create a PDF buffer
    buf = io.BytesIO()
    
    # Create PDF document in landscape orientation
    doc = SimpleDocTemplate(
        buf, 
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=colors.black
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=colors.darkgray
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=6,
        spaceBefore=6,
        textColor=HexColor('#4338ca')
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10
    )
    
    # Custom styles for the infographic
    metric_title_style = ParagraphStyle(
        'MetricTitle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=HexColor('#4338ca')
    )
    
    # Create content for the infographic
    content = []
    
    # Add title with brand name
    if brand_name != "Unknown":
        content.append(Paragraph(f"{brand_name} Campaign Performance Snapshot", title_style))
    else:
        content.append(Paragraph("Campaign Performance Snapshot", title_style))
    
    # Add subtitle
    content.append(Paragraph("Powered by the Audience Resonance Index™", subtitle_style))
    content.append(Spacer(1, 10))
    
    # Create a 3-column layout for the main content
    data = [[None, None, None]]
    
    # Column 1: ARI Score and Percentile
    # Create a donut chart showing the percentile
    def create_percentile_chart():
        drawing = Drawing(200, 200)
        
        # Create a manual donut chart using a combination of wedges
        # Parameters for the wedges
        centerx, centery = 100, 100
        outer_radius = 50
        inner_radius = 20
        
        # Calculate the angles for the percentage wedge
        percent_angle = percentile * 3.6  # Convert percentage to degrees (out of 360)
        
        # Create wedge for the colored portion (if not 0%)
        if percentile > 0:
            # Colored wedge (main percentage)
            w1 = Wedge(centerx, centery, outer_radius, 0, percent_angle, 
                      fillColor=HexColor('#4338ca'), strokeColor=None)
            drawing.add(w1)
            
            # Inner circle cutout for colored portion
            if percentile < 100:
                w3 = Wedge(centerx, centery, inner_radius, 0, percent_angle, 
                          fillColor='white', strokeColor=None)
                drawing.add(w3)
        
        # Create wedge for the remaining portion (if not 100%)
        if percentile < 100:
            # Gray wedge (remaining percentage)
            w2 = Wedge(centerx, centery, outer_radius, percent_angle, 360, 
                      fillColor=HexColor('#e0e0e0'), strokeColor=None)
            drawing.add(w2)
            
            # Inner circle cutout for gray portion
            w4 = Wedge(centerx, centery, inner_radius, percent_angle, 360, 
                      fillColor='white', strokeColor=None)
            drawing.add(w4)
        
        # Add the percentile text in the center
        percentile_text = String(centerx, centery + 5, f"{percentile}%", textAnchor='middle')
        percentile_text.fontName = 'Helvetica-Bold'
        percentile_text.fontSize = 20
        percentile_text.fillColor = HexColor('#4338ca')
        
        # Add "Percentile" text under the number
        label_text = String(centerx, centery - 15, "Percentile", textAnchor='middle')
        label_text.fontName = 'Helvetica'
        label_text.fontSize = 10
        label_text.fillColor = colors.darkgray
        
        drawing.add(percentile_text)
        drawing.add(label_text)
        
        return drawing
    
    # Create the first column content with benchmark percentile
    col1_content = []
    col1_content.append(Paragraph("Campaign Performance", heading_style))
    col1_content.append(create_percentile_chart())
    col1_content.append(Paragraph(f"This campaign outperforms {percentile}% of all campaigns analyzed by Digital Culture Group.", normal_style))
    
    # Column 2: Top Metrics and Areas for Improvement
    col2_content = []
    col2_content.append(Paragraph("Key Metrics", heading_style))
    
    # Create a mini bar chart for the top metrics
    def create_metrics_chart():
        drawing = Drawing(200, 150)
        
        # Sort metrics by score
        sorted_metrics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 5 metrics
        top_metrics = sorted_metrics[:5]
        
        # Instead of using the VerticalBarChart, we'll create a custom bar chart with rectangles
        # Define dimensions
        chart_height = 100
        chart_width = 180
        max_value = 10
        bar_width = chart_width / len(top_metrics) * 0.8
        spacing = chart_width / len(top_metrics) * 0.2
        
        # Draw axes
        x_axis = Line(10, 10, 10 + chart_width, 10, strokeColor=colors.black)
        y_axis = Line(10, 10, 10, 10 + chart_height, strokeColor=colors.black)
        drawing.add(x_axis)
        drawing.add(y_axis)
        
        # Add bars
        for i, (metric, score) in enumerate(top_metrics):
            # Calculate bar height proportional to score
            bar_height = (score / max_value) * chart_height
            
            # Calculate bar position
            x = 10 + i * (bar_width + spacing) + spacing/2
            y = 10
            
            # Create bar
            bar = Rect(x, y, bar_width, bar_height, fillColor=HexColor('#4338ca'), strokeColor=None)
            drawing.add(bar)
            
            # Add value on top of bar
            value_text = String(x + bar_width/2, y + bar_height + 5, str(score), 
                              textAnchor='middle', fontSize=8)
            drawing.add(value_text)
            
            # Add metric name under the bar
            # Shorten metric name if needed
            metric_display = metric
            if len(metric) > 12:
                metric_display = metric[:10] + '..'
                
            metric_text = String(x + bar_width/2, y - 10, metric_display, 
                               textAnchor='middle', fontSize=7, fillColor=colors.darkblue)
            drawing.add(metric_text)
        
        # Add a title
        title = String(10 + chart_width/2, 10 + chart_height + 20, "Top Metrics", 
                     textAnchor='middle', fontSize=10, fillColor=colors.black)
        drawing.add(title)
        
        return drawing
    
    # Add the metrics chart
    col2_content.append(create_metrics_chart())
    
    # Add improvement areas
    col2_content.append(Paragraph("Areas for Improvement:", metric_title_style))
    for area in improvement_areas[:3]:  # Limit to top 3
        col2_content.append(Paragraph(f"• {area}", normal_style))
    
    # Column 3: Audience Snapshot
    col3_content = []
    col3_content.append(Paragraph("Primary Audience Snapshot", heading_style))
    
    # Add audience information if available
    if top_audience:
        audience_name = top_audience.get('name', 'Primary Audience')
        audience_desc = top_audience.get('description', 'No description available')
        
        col3_content.append(Paragraph(f"<b>{audience_name}</b>", normal_style))
        col3_content.append(Paragraph(audience_desc, normal_style))
        
        # Add interests if available
        interests = top_audience.get('interest_categories', [])
        if interests:
            col3_content.append(Paragraph("<b>Key Interests:</b>", normal_style))
            interest_text = ", ".join(interests[:5])  # Limit to 5 interests
            col3_content.append(Paragraph(interest_text, normal_style))
        
        # Add platform targeting if available
        platforms = top_audience.get('platform_targeting', [])
        if platforms:
            col3_content.append(Paragraph("<b>Recommended Platforms:</b>", normal_style))
            platform_list = []
            for platform in platforms[:3]:  # Limit to 3 platforms
                platform_name = platform.get('platform', '')
                if platform_name:
                    platform_list.append(platform_name)
            platform_text = ", ".join(platform_list)
            col3_content.append(Paragraph(platform_text, normal_style))
            
        # Add performance metrics if available
        performance = top_audience.get('expected_performance', {})
        if performance:
            col3_content.append(Paragraph("<b>Expected Performance:</b>", normal_style))
            perf_list = []
            for metric, value in performance.items():
                if metric in ['CTR', 'engagement_rate', 'CPA']:
                    perf_list.append(f"{metric}: {value}")
            perf_text = " | ".join(perf_list)
            col3_content.append(Paragraph(perf_text, normal_style))
    else:
        col3_content.append(Paragraph("Audience data not available", normal_style))
    
    # Create tables to hold column content
    col1_table = Table([[col] for col in col1_content], colWidths=[250])
    col2_table = Table([[col] for col in col2_content], colWidths=[250])
    col3_table = Table([[col] for col in col3_content], colWidths=[250])
    
    # Style the column tables
    col_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ])
    
    col1_table.setStyle(col_style)
    col2_table.setStyle(col_style)
    col3_table.setStyle(col_style)
    
    # Create a table to organize the three columns
    data = [[col1_table, col2_table, col3_table]]
    table = Table(data, colWidths=[250, 250, 250])
    
    # Style the main table
    table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ])
    table.setStyle(table_style)
    
    content.append(table)
    
    # Add footer
    content.append(Spacer(1, 20))
    footer_text = "© 2025 Digital Culture Group, LLC. All rights reserved. This data is directional only."
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.darkgray
    )
    content.append(Paragraph(footer_text, footer_style))
    
    # Build the document
    doc.build(content)
    
    # Get PDF as base64 string
    pdf_data = buf.getvalue()
    b64 = base64.b64encode(pdf_data).decode()
    
    # Create download link
    filename = f"{brand_name.replace(' ', '_')}_Snapshot.pdf" if brand_name != "Unknown" else "Campaign_Snapshot.pdf"
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" style="text-decoration: none; display: inline-block; padding: 10px 20px; background-color: #4338ca; color: white; border-radius: 5px; font-weight: 500;">Download Infographic for Email</a>'
    
    return href

# Define function to extract text from various file types
def extract_text_from_file(uploaded_file):
    """
    Extract text from various file types including docx, pdf and txt.
    
    Args:
        uploaded_file: The file uploaded through Streamlit's file_uploader
        
    Returns:
        str: The extracted text from the file
    """
    try:
        # Get the file extension from the name
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        # Convert the uploaded file to bytes for processing
        file_bytes = io.BytesIO(uploaded_file.getvalue())
        
        if file_type == 'txt':
            # For text files
            text = uploaded_file.getvalue().decode('utf-8')
        
        elif file_type == 'docx':
            try:
                # For Word documents
                doc = docx.Document(file_bytes)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            except Exception as e:
                st.error(f"Error processing DOCX file: {str(e)}")
                return None
        
        elif file_type == 'pdf':
            try:
                # For PDF files
                pdf_reader = PyPDF2.PdfReader(file_bytes)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
            except Exception as e:
                st.error(f"Error processing PDF file: {str(e)}")
                return None
        
        else:
            # Unsupported file type
            st.error(f"Unsupported file type: {file_type}. Please use txt, pdf, or docx files.")
            return None
        
        # Check for blocked keywords and remove them
        for keyword in BLOCKED_KEYWORDS:
            text = text.replace(keyword, "[FILTERED]")
        
        return text
    
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
        return None

def hash(text):
    """Simple hash function for generating a deterministic number from text."""
    if not text:
        return 0
    h = 0
    for c in text:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return h % 100  # Return a number between 0-99




def is_siteone_hispanic_campaign(brand_name, brief_text):
    """
    Detect if this is a SiteOne Hispanic-targeted campaign based on brand name and brief text.
    
    Args:
        brand_name (str): Brand name extracted from the brief
        brief_text (str): The full text of the brief
        
    Returns:
        bool: True if this is a SiteOne Hispanic campaign, False otherwise
    """
    if not brief_text:
        return False
        
    # Add brand name to brief text for more robust detection
    combined_text = f"{brand_name} {brief_text}" if brand_name else brief_text
    
    # Use the centralized detection function from ai_insights module
    return is_siteone_hispanic_content(combined_text)




def is_siteone_hispanic_content(text):
    """
    Detect if the content is related to SiteOne Hispanic audience targeting.
    
    Args:
        text (str): The text content to analyze
        
    Returns:
        bool: True if the content is SiteOne Hispanic related, False otherwise
    """
    if not text:
        return False
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Check for SiteOne brand mentions
    siteone_terms = ['siteone', 'site one', 'site-one']
    has_siteone = any(term in text_lower for term in siteone_terms)
    
    # Check for Hispanic audience targeting keywords
    hispanic_terms = [
        'hispanic', 'latino', 'latina', 'latinx', 
        'español', 'espanol', 'spanish-language', 'spanish language'
    ]
    has_hispanic = any(term in text_lower for term in hispanic_terms)
    
    # Return True if both SiteOne and Hispanic indicators are found
    return has_siteone and has_hispanic
