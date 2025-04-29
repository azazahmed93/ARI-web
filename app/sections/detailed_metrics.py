import streamlit as st
from core.analysis import (

    get_score_level,
)
from assets.content import (
    METRICS, 
)
from .metrics_summary import display_metrics_summary

def detailed_metrics(is_siteone_hispanic, scores, improvement_areas, brief_text, summary_text, top_strength, key_opportunity, roi_potential):
    # Display standard scorecard title with no brand reference
    st.markdown("<h2 style='text-align: center;'>Audience Resonance Index Scorecard</h2>", unsafe_allow_html=True)
    
    # If this is a SiteOne Hispanic campaign, display a specialized audience tag
    if is_siteone_hispanic:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 15px;">
            <span style="background-color: #5865f2; color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 500;">
                SiteOne Hispanic Audience Analysis
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    # Add some spacing after the title
    st.markdown("---")
    
    # Display metrics summary (replaced radar chart)
    display_metrics_summary(scores, improvement_areas, brief_text)
    
    # Generate and display Executive Summary
    analysis = '<div class="metric-analysis">'
    analysis += f'<h3>Executive Summary</h3>'
    analysis += f'<p>{summary_text}</p>'
    # Add debug info for tracking
    st.session_state['final_values'] = {
        "top_strength": top_strength,
        "key_opportunity": key_opportunity,
        "roi_potential": roi_potential
    }
    
    analysis += '<div class="metric-box">'
    analysis += f'<div class="strength-box"><strong>Top Strength:</strong><br/>{top_strength}</div>'
    analysis += f'<div class="opportunity-box"><strong>Key Opportunity:</strong><br/>{key_opportunity}</div>'
    analysis += f'<div class="roi-box"><strong>ROI Potential:</strong><br/>{roi_potential}</div>'
    analysis += '</div>'
    analysis += '<h3>Detailed Metrics</h3>'
    analysis += '<div class="metrics-container">'
    
    # Replace static metrics_html with colored progress bars for each metric
    for metric, score in scores.items():
        formatted_score = f"{score:.1f}"
        # Get description text - prioritize AI-generated descriptions if available
        if 'ai_insights' in st.session_state and st.session_state.ai_insights and 'metric_details' in st.session_state.ai_insights:
            # Use the AI-generated description specific to this brief if available
            metric_details = st.session_state.ai_insights.get('metric_details', {})
            if metric in metric_details:
                description = metric_details[metric]
            else:
                # Fall back to generic descriptions
                description = METRICS[metric][get_score_level(score)]
        else:
            # Use generic descriptions from METRICS
            description = METRICS[metric][get_score_level(score)]
            
        # Calculate percent for bar width (use full percentage for proper display)
        percent = int(score * 10)
        
        # Set the color based on score - use direct CSS colors instead of classes for reliability
        if score >= 8:
            bar_bg = "linear-gradient(90deg, #10b981, #34d399)"
            score_bg = "rgba(16, 185, 129, 0.15)"
            score_color = "#10b981"
            bar_class = "excellent"
        elif score >= 6:
            bar_bg = "linear-gradient(90deg, #f59e0b, #fbbf24)"
            score_bg = "rgba(245, 158, 11, 0.15)"
            score_color = "#f59e0b"
            bar_class = "good"
        else:
            bar_bg = "linear-gradient(90deg, #ef4444, #f87171)"
            score_bg = "rgba(239, 68, 68, 0.15)"
            score_color = "#ef4444"
            bar_class = "needs-improvement"
            
        # Add tooltip descriptions for complex metrics
        tooltip_content = ""
        if metric == "Cultural Authority":
            tooltip_content = "A measure of how effectively the campaign leverages culturally significant elements or voices with credibility in the target audience space."
        elif metric == "Cultural Vernacular":
            tooltip_content = "Evaluates how well the campaign uses language patterns, expressions, and communication styles authentic to the target audience."
        elif metric == "Media Ownership Equity":
            tooltip_content = "Analyzes the diversity of media partnerships and distribution channels, with higher scores for more inclusive and equitable media representation."
        elif metric == "Commerce Bridge":
            tooltip_content = "Measures how effectively the campaign connects brand storytelling to purchase opportunities across the customer journey."
        elif metric == "Geo-Cultural Fit":
            tooltip_content = "Evaluates how well the campaign accounts for geographical and cultural variations within the target audience."
        elif metric == "Platform Relevance":
            tooltip_content = "Assesses how effectively the campaign utilizes media platforms aligned with the target audience's consumption behaviors."
        elif metric == "Buzz & Conversation":
            tooltip_content = "Evaluates the campaign's potential to generate organic discussion and sharing among the target audience."
        elif metric == "Representation":
            tooltip_content = "Measures how authentically the campaign represents the diversity of perspectives, experiences, and identities within the target audience."
        elif metric == "Cultural Relevance":
            tooltip_content = "Evaluates how well the campaign connects with currently relevant cultural themes important to the target audience."
            
        # Add tooltip HTML if available
        tooltip_html = f'<div class="tooltip"><i class="info-icon">i</i><span class="tooltiptext">{tooltip_content}</span></div>' if tooltip_content else ""
        
        # Add metric with custom-styled progress bar (using inline styles for reliability)
        analysis += f'<div class="metric-item">'
        analysis += f'<div class="metric-header"><strong>{metric}</strong> {tooltip_html} <span style="font-weight: 600; border-radius: 100px; padding: 0.3rem 0.8rem; font-size: 0.9rem; background: {score_bg}; color: {score_color};">{formatted_score}</span></div>'
        analysis += f'<div style="height: 8px; width: 100%; background: #e2e8f0; border-radius: 100px; margin-bottom: 1rem; overflow: hidden; position: relative;">'
        analysis += f'<div style="position: absolute; top: 0; left: 0; height: 100%; width: {percent}%; background: {bar_bg}; border-radius: 100px;"></div>'
        analysis += f'</div>'
        analysis += f'<div class="metric-description">{description}</div>'
        analysis += f'</div>'
    
    analysis += '</div>'  # Close metrics-container
    analysis += '</div>'  # Close metric-analysis
    
    st.markdown(analysis, unsafe_allow_html=True)
    
    # Create an advanced metric analysis section using the new HTML template
    st.markdown('<h3 style="margin-top: 30px;">Advanced Metric Analysis</h3>', unsafe_allow_html=True)
    
    # Read the HTML template file
    with open("attached_assets/ARI_AdvancedMetricAnalyzer.html", "r") as file:
        template_html = file.read()
    
    # Add the advanced metric analysis section using the new HTML template
    metrics_html = ""
    for metric, score in scores.items():
        # Format the score to a single decimal place
        formatted_score = f"{score:.1f}"
        
        # Determine score level for styling
        if score >= 8:
            bg_color = "#e0f7ec"
            border_color = "#10b981"
            strength_level = "STRONG"
        elif score >= 6:
            bg_color = "#fff4e5"
            border_color = "#f59e0b"
            strength_level = "GOOD"
        else:
            bg_color = "#fef2f2"
            border_color = "#ef4444"
            strength_level = "NEEDS IMPROVEMENT"
            
        # Get description text - prioritize AI-generated descriptions if available
        if 'ai_insights' in st.session_state and st.session_state.ai_insights and 'metric_details' in st.session_state.ai_insights:
            # Use the AI-generated description specific to this brief if available
            metric_details = st.session_state.ai_insights.get('metric_details', {})
            if metric in metric_details:
                description = metric_details[metric]
            else:
                # Fall back to generic descriptions
                description = METRICS[metric][get_score_level(score)]
        else:
            # Use generic descriptions from METRICS
            description = METRICS[metric][get_score_level(score)]
        
        # Add this metric to the HTML - use string concatenation instead of f-strings with triple quotes
        metrics_html += f'<div style="margin-bottom: 1rem;"><strong>{metric} – {formatted_score}:</strong> {description}</div>'
