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
    if include_sections.get('tv_networks', True):
        content.append(Paragraph("Top TV Network Affinities", heading1_style))
        
        # Create TV networks table with 5 columns
        tv_network_data = []
        row = []
        tv_col_width = 100  # Define column width for TV networks
        
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
    if include_sections.get('psychographic', True):
        content.append(Paragraph("Psychographic Highlights", heading1_style))
        psycho_text = strip_html(PSYCHOGRAPHIC_HIGHLIGHTS)
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
        if hasattr(st, 'session_state') and 'competitor_tactics' in st.session_state and st.session_state.competitor_tactics:
            competitor_tactics = st.session_state.competitor_tactics
            has_competitor_tactics = len(competitor_tactics) > 0
        
        # If we have tactics, format them nicely for the PDF
        if has_competitor_tactics:
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
        from marketing_trends import generate_simplified_trend_data
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
        content.append(Paragraph("High-Performance Markets:", 
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

def display_metric_bar(metric, score):
    """
    Display a metric with a colored progress bar and contextual learning tip.
    
    Args:
        metric (str): Name of the metric
        score (float): Score value (0-10)
    """
    # Import the learning tips module
    from assets.learning_tips import metric_with_tip
    
    # Create a container for the metric
    metric_container = st.container()
    
    with metric_container:
        # Display metric label and score
        col1, col2 = st.columns([4, 1])
        
        # Add the metric name with learning tip bubble
        col1.markdown(metric_with_tip(metric), unsafe_allow_html=True)
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
