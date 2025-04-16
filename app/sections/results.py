import streamlit as st

# Import the grammar fix function from ai_insights module
# This helps clean up grammatical errors and duplicate words
from core.ai_insights import (
    fix_grammar_and_duplicates,
)

from core.utils import (
    create_pdf_download_link,
    create_infographic_download_link,
)
from core.utils import is_siteone_hispanic_campaign
from .detailed_metrics import detailed_metrics
from .audience_insights import audience_insights
from .media_affinities import media_affinities
from .trend_analysis import trend_analysis
from .next_steps import next_steps
from .summary import summary
from .premium_cta import premium_cta

def display_results(scores, percentile, improvement_areas, brand_name="Unknown", industry="General", product_type="Product", brief_text=""):
    """Display the ARI analysis results."""
    # Import the marketing trend heatmap functionality
    from app.components.marketing_trends import display_trend_heatmap
    st.markdown("---")
    
    # Initialize values that will be set based on scores or AI insights
    summary_text = ""
    # These will be dynamically set based on actual metric scores, ensuring no static data
    top_strength = None
    key_opportunity = None
    roi_potential = ""
    
    # Extract top strength and key opportunity
    # Initialize variables to avoid "possibly unbound" errors
    # Calculate dynamic metrics based on actual scores
    metric_scores = list(scores.items())
    metric_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Calculate weighted ROI metrics based on key performance indicators
    weighted_metrics = {
        "Cultural Authority": 1.5,
        "Buzz & Conversation": 1.3,
        "Cultural Vernacular": 1.2,
        "Commerce Bridge": 1.2,
        "Platform Relevance": 1.1
    }
    
    # Calculate weighted ROI score
    roi_sum = 0
    roi_weight_total = 0
    
    for metric, score in scores.items():
        weight = weighted_metrics.get(metric, 0.8)  # Default weight for other metrics
        roi_sum += score * weight
        roi_weight_total += weight
    
    # Calculate weighted average ROI and convert to percentage
    if roi_weight_total > 0:
        roi_score = roi_sum / roi_weight_total
        roi_percent = int(5 + (roi_score / 10) * 20)
        roi_potential = f"+{roi_percent}%"
    else:
        # Fallback if weights are missing
        avg_score = sum(scores.values()) / len(scores) if scores else 7.0
        roi_percent = int(5 + (avg_score / 10) * 20)
        roi_potential = f"+{roi_percent}%"
    
    # Use AI-generated insights if available, otherwise use calculated metrics
    if 'ai_insights' in st.session_state and st.session_state.ai_insights:
        ai_insights = st.session_state.ai_insights
        strengths = ai_insights.get('strengths', [])
        improvements = ai_insights.get('improvements', [])
        
        # Extract the first strength and improvement for the executive summary
        if strengths:
            top_strength = strengths[0].get('area', 'Cultural Relevance')
        else:
            # Fall back to calculated top strength - fully dynamic
            top_strength = metric_scores[0][0] if metric_scores and len(metric_scores) > 0 else None
            
        if improvements:
            key_opportunity = improvements[0].get('area', 'Audience Engagement')
        else:
            # Fall back to calculated bottom metric - fully dynamic
            key_opportunity = metric_scores[-1][0] if metric_scores and len(metric_scores) > 0 else None
        
        # Track values internally
        internal_tracking = {
            "source": "ai_insights",
            "top_strength": top_strength,
            "key_opportunity": key_opportunity,
            "calculated_top": metric_scores[0][0] if metric_scores else "None",
            "calculated_bottom": metric_scores[-1][0] if metric_scores else "None"
        }
        
        # Extract potential ROI from performance prediction if available
        prediction = ai_insights.get('performance_prediction', '')
        if prediction and '%' in prediction:
            import re
            roi_match = re.search(r'(\+\d+%|\d+%)', prediction)
            if roi_match:
                roi_potential = roi_match.group(0)
                if not roi_potential.startswith('+'):
                    roi_potential = f"+{roi_potential}"
    else:
        # Calculate based on the scores if AI insights aren't available
        
        # Use the highest scoring metric as the top strength - fully dynamic
        top_strength = metric_scores[0][0] if metric_scores and len(metric_scores) > 0 else None
        
        # Use the lowest scoring metric as the key opportunity - fully dynamic
        key_opportunity = metric_scores[-1][0] if metric_scores and len(metric_scores) > 0 else None
        
        # Track values internally
        internal_tracking = {
            "source": "calculated_scores",
            "top_strength": top_strength,
            "key_opportunity": key_opportunity,
            "metric_scores": {name: score for name, score in metric_scores},
            "roi_formula": {
                "roi_percent": roi_percent
            }
        }
    
    # Generate summary text from the insights - make it more dynamic and specific to the brief
    if 'ai_insights' in st.session_state and st.session_state.ai_insights:
        ai_insights = st.session_state.ai_insights
        
        # Get the top strength explanation if available
        top_strength_explanation = ""
        for strength in ai_insights.get('strengths', []):
            if strength.get('area') == top_strength and 'explanation' in strength:
                top_strength_explanation = strength['explanation']
                break
        
        # Get the key opportunity explanation if available
        key_opportunity_explanation = ""
        for improvement in ai_insights.get('improvements', []):
            if improvement.get('area') == key_opportunity and 'explanation' in improvement:
                key_opportunity_explanation = improvement['explanation']
                break
        
        # If we have detailed explanations, use them in a more detailed summary
        if top_strength_explanation and key_opportunity_explanation:
            summary_text = f"This campaign excels in <strong>{top_strength}</strong>: {top_strength_explanation[0].lower() + top_strength_explanation[1:]} However, there's an opportunity to enhance <strong>{key_opportunity}</strong>: {key_opportunity_explanation[0].lower() + key_opportunity_explanation[1:]} Our AI-powered analysis suggests implementing targeted tactical adjustments that could increase overall effectiveness by <strong>{roi_potential}</strong>."
        else:
            # Fall back to the simpler summary if we don't have detailed explanations
            summary_text = f"This campaign demonstrates strong performance in <strong>{top_strength}</strong>, with opportunities to improve <strong>{key_opportunity}</strong>. Our AI-powered analysis suggests tactical adjustments that could increase overall effectiveness by <strong>{roi_potential}</strong>."
    else:
        # Default summary when no AI insights are available
        summary_text = f"This campaign demonstrates strong performance in <strong>{top_strength}</strong>, with opportunities to improve <strong>{key_opportunity}</strong>. Our AI-powered analysis suggests tactical adjustments that could increase overall effectiveness by <strong>{roi_potential}</strong>."
    
    # Check if this is a SiteOne Hispanic campaign
    is_siteone_hispanic = is_siteone_hispanic_campaign(brand_name, brief_text)
    
    # Create tabs for better organization of content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Detailed Metrics", 
        "Audience Insights", 
        "Media Affinities", 
        "Trend Analysis",
        "Next Steps"
    ])
    
    # TAB 1: DETAILED METRICS
    with tab1:
        detailed_metrics(is_siteone_hispanic, scores, improvement_areas, brief_text, summary_text, top_strength, key_opportunity, roi_potential)
        summary(percentile, scores, improvement_areas, brand_name, brief_text, industry, product_type)
    
    # Premium styled CSS for Advanced Metric Analysis with simplified bar styling (no animations that might conflict with Streamlit)
    st.markdown("""
    <style>
    .metric-analysis {
        margin-top: 2rem;
        padding: 2rem;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-top: 4px solid #5865f2;
    }
    .metric-box {
        display: flex;
        gap: 1.2rem;
        margin: 1.5rem 0;
    }
    .strength-box {
        flex: 1;
        background: #f0fdf4;
        padding: 1.5rem;
        border-radius: 8px;
        border-top: 4px solid #10b981;
        box-shadow: 0 2px 6px rgba(16, 185, 129, 0.1);
    }
    .opportunity-box {
        flex: 1;
        background: #fff7ed;
        padding: 1.5rem;
        border-radius: 8px;
        border-top: 4px solid #f59e0b;
        box-shadow: 0 2px 6px rgba(245, 158, 11, 0.1);
    }
    .roi-box {
        flex: 1;
        background: #fef2f2;
        padding: 1.5rem;
        border-radius: 8px;
        border-top: 4px solid #ef4444;
        box-shadow: 0 2px 6px rgba(239, 68, 68, 0.1);
    }
    .metrics-container {
        margin-top: 1.5rem;
    }
    .metric-item {
        margin-bottom: 1.8rem;
        background: #f8fafc;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
    }
    .metric-score {
        font-weight: 600;
        border-radius: 100px;
        padding: 0.3rem 0.8rem;
        font-size: 0.9rem;
    }
    .metric-score.excellent {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
    }
    .metric-score.good {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
    }
    .metric-score.needs-improvement {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
    }
    .metric-progress-container {
        height: 8px;
        width: 100%;
        background: #e2e8f0;
        border-radius: 100px;
        margin-bottom: 1rem;
        overflow: hidden;
        position: relative;
    }
    .metric-progress-bar.excellent {
        background: linear-gradient(90deg, #10b981, #34d399);
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        border-radius: 100px;
    }
    .metric-progress-bar.good {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        border-radius: 100px;
    }
    .metric-progress-bar.needs-improvement {
        background: linear-gradient(90deg, #ef4444, #f87171);
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        border-radius: 100px;
    }
    .metric-description {
        color: #475569;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .metric-analysis h3 {
        color: #1e293b;
        font-weight: 600;
        margin-bottom: 1.2rem;
        font-size: 1.4rem;
        letter-spacing: -0.01em;
    }
    .metric-analysis strong {
        color: #0f172a;
        font-weight: 600;
    }
    /* Tooltip Styles */
    .tooltip {
        position: relative;
        display: inline-block;
        margin-left: 5px;
        vertical-align: middle;
    }
    .info-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        background-color: #e2e8f0;
        color: #64748b;
        border-radius: 50%;
        font-size: 11px;
        font-weight: bold;
        font-style: normal;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 280px;
        background-color: #1e293b;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 8px 12px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -140px;
        opacity: 0;
        transition: opacity 0.2s;
        font-size: 0.8rem;
        line-height: 1.5;
        font-weight: normal;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #1e293b transparent transparent transparent;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    # TAB 3: MEDIA AFFINITIES
    with tab3:
        media_affinities(is_siteone_hispanic)
    
    # TAB 4: TREND ANALYSIS
    with tab4:
        trend_analysis(brief_text)
    
    # TAB 2: AUDIENCE INSIGHTS
    with tab2:
        audience_insights(is_siteone_hispanic)
    # TAB 5: NEXT STEPS
    with tab5:
        next_steps()


    
    
    # Premium investor-focused call-to-action section
    st.markdown("---")
    
    premium_cta(scores, improvement_areas, percentile, brand_name, industry, product_type, brief_text)
    # Priority improvement recommendations have been moved to the tabs above in the Campaign Intelligence section
    
    # Add the demo section
    demo_container = st.container()
    with demo_container:
        st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.85rem; color: #777;'>Want to see how we can help your business?</p>", unsafe_allow_html=True)
        # Create a custom HTML link that looks like a button but opens an email client
        st.markdown("""
        <a href="mailto:crystal@digitalculture.group?subject=Schedule a Demo for ARI Analyzer&body=I would like to schedule a demo for the Audience Resonance Index Analyzer." 
           style="display: inline-block; padding: 0.5rem 1rem; font-weight: 600; text-align: center; 
                  background-color: #5865f2; color: white; text-decoration: none; 
                  border-radius: 0.25rem; cursor: pointer; margin: 0.5rem 0;">
            Schedule a Demo
        </a>
        """, unsafe_allow_html=True)

