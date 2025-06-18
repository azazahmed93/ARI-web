import streamlit as st
import json

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
from core.analysis import industry_keywords
import os
import streamlit.components.v1 as components

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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Detailed Metrics", 
        "Audience Insights", 
        "Media Affinities", 
        "Trend Analysis",
        "Transaction Data",
        "DMA Insights",
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
    # TAB 5: Transaction Data
    with tab5:
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        PARENT_DIR = os.path.dirname(CURRENT_DIR)
        HTML_FILE_PATH = os.path.join(PARENT_DIR, "static", "index.html") 

        try:
            with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
                html_code = f.read()

            # Embed the HTML content
            # You can adjust height and scrolling as needed.
            # For a full-page-like experience, you might need a large height.
            # `scrolling=True` allows the component to have its own scrollbar if content overflows.
            # st.components.v1.html(html_code, height=800)
            html_code = html_code.replace("{{INDUSTRY}}", industry)
            html_code = html_code.replace("{{KEYWORDS}}", ", ".join(f"'{word}'" for word in industry_keywords[industry]))
            components.html(html_code, height=1000, scrolling=True)

        except FileNotFoundError:
            st.error(f"ERROR: The HTML file was not found at '{HTML_FILE_PATH}'.")
            st.info("Please make sure 'index.html' is in the correct location.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    with tab6:
        # Create CompleteBriefAnalysis mapping
        def create_complete_brief_analysis():
            """
            Maps all AI-generated data to the CompleteBriefAnalysis shape for external system integration.
            """
            # Extract key audiences from segments
            key_audiences = []
            if 'audience_segments' in st.session_state and 'segments' in st.session_state.audience_segments:
                for segment in st.session_state.audience_segments['segments'][:3]:  # Top 3 segments
                    key_audiences.append(segment.get('name', ''))
            
            # Extract competitive insights
            competitive_insights = {
                "competitorCount": len(st.session_state.get('competitor_analysis', {}).get('competitors', [])) if 'competitor_analysis' in st.session_state else 3,
                "marketShare": 27,  # Default as we don't calculate total market share
                "strengthAreas": []
            }
            
            if 'ai_insights' in st.session_state and st.session_state.ai_insights:
                strengths = st.session_state.ai_insights.get('strengths', [])
                competitive_insights["strengthAreas"] = [s.get('area', '') for s in strengths[:3]]
            
            # Extract growth opportunities from AI insights
            growth_opportunities = []
            if 'ai_insights' in st.session_state and st.session_state.ai_insights:
                improvements = st.session_state.ai_insights.get('improvements', [])
                # Calculate potential scores based on ARI scores and improvement priorities
                base_potential = 90
                for idx, improvement in enumerate(improvements[:3]):
                    # Calculate potential based on the gap between current score and perfect score
                    area_name = improvement.get('area', '')
                    current_score = scores.get(area_name, 5) if 'scores' in locals() else 5
                    improvement_potential = int(base_potential - (current_score * 2) - (idx * 5))
                    
                    growth_opportunities.append({
                        "id": idx + 1,
                        "title": improvement.get('area', ''),
                        "description": improvement.get('recommendation', ''),
                        "potential": max(60, min(95, improvement_potential))  # Keep between 60-95
                    })
            
            # Map geoData from DMA information with actual audience reach data
            geo_data = {"topMarkets": []}
            if 'recommended_dmas' in st.session_state and 'audience_reach' in st.session_state:
                dma_mapping = {
                    501: {"name": "New York", "state": "NY", "population": 7452000},
                    803: {"name": "Los Angeles", "state": "CA", "population": 5735000},
                    602: {"name": "Chicago", "state": "IL", "population": 3462000},
                    807: {"name": "San Francisco-Oakland-San Jose", "state": "CA", "population": 2452000},
                    623: {"name": "Dallas-Fort Worth", "state": "TX", "population": 2963000},
                    506: {"name": "Boston", "state": "MA", "population": 2395000},
                    524: {"name": "Atlanta", "state": "GA", "population": 2329000},
                    618: {"name": "Houston", "state": "TX", "population": 2484000},
                    753: {"name": "Phoenix", "state": "AZ", "population": 1995000},
                    819: {"name": "Seattle-Tacoma", "state": "WA", "population": 1915000},
                    528: {"name": "Miami-Fort Lauderdale", "state": "FL", "population": 1744000},
                    751: {"name": "Denver", "state": "CO", "population": 1760000},
                    505: {"name": "Detroit", "state": "MI", "population": 1985000},
                    539: {"name": "Tampa-St. Petersburg", "state": "FL", "population": 1867000},
                    613: {"name": "Minneapolis-St. Paul", "state": "MN", "population": 1752000},
                    534: {"name": "Orlando-Daytona Beach", "state": "FL", "population": 1509000},
                    862: {"name": "Sacramento-Stockton", "state": "CA", "population": 1340000},
                    517: {"name": "Charlotte", "state": "NC", "population": 1265000},
                    504: {"name": "Philadelphia", "state": "PA", "population": 2953000},
                    511: {"name": "Washington DC", "state": "DC", "population": 2536000}
                }
                
                # Get audience reach data to calculate index scores
                audience_reach_by_dma = {}
                for reach_data in st.session_state.audience_reach:
                    if reach_data.get('name') != 'National Campaign':
                        # Extract DMA name without state
                        dma_name = reach_data['name'].split(',')[0].strip()
                        audience_reach_by_dma[dma_name] = reach_data.get('audienceReach', 0)
                
                # Calculate index scores based on audience reach relative to population
                for idx, dma_id in enumerate(st.session_state.recommended_dmas[:4]):  # Top 4 markets
                    if dma_id in dma_mapping:
                        dma_info = dma_mapping[dma_id]
                        dma_name_short = dma_info["name"].split('-')[0].strip()  # Handle multi-city names
                        
                        # Get audience reach for this DMA
                        audience_reach = audience_reach_by_dma.get(dma_name_short, 0)
                        if audience_reach == 0:
                            # Try full name match
                            for reach_name, reach_val in audience_reach_by_dma.items():
                                if dma_name_short in reach_name:
                                    audience_reach = reach_val
                                    break
                        
                        # Calculate index score based on audience reach vs population
                        population_millions = dma_info["population"] / 1000000
                        if population_millions > 0:
                            reach_percentage = (audience_reach / population_millions) * 100
                            # Index where 100 = average, higher is better
                            index_score = int(100 + (reach_percentage - 35) * 2)  # Assuming 35% is average
                        else:
                            index_score = 100
                        
                        geo_data["topMarkets"].append({
                            "dmaId": dma_id,
                            "name": dma_info["name"],
                            "state": dma_info["state"],
                            "population": dma_info["population"],
                            "indexScore": max(80, min(180, index_score))  # Keep between 80-180
                        })
            
            # Extract competitor analysis with actual threat levels
            competitors_list = []
            if 'competitor_analysis' in st.session_state and st.session_state.competitor_analysis:
                competitors = st.session_state.competitor_analysis.get('competitors', [])
                for comp in competitors[:3]:
                    # Extract strengths from digital tactics
                    digital_tactics = comp.get('digital_tactics', '')
                    strengths = []
                    
                    # Parse key strength areas from digital tactics description
                    if 'programmatic' in digital_tactics.lower():
                        strengths.append("Programmatic excellence")
                    if 'video' in digital_tactics.lower() or 'content' in digital_tactics.lower():
                        strengths.append("Content strategy")
                    if 'mobile' in digital_tactics.lower() or 'app' in digital_tactics.lower():
                        strengths.append("Mobile dominance")
                    if 'search' in digital_tactics.lower() or 'seo' in digital_tactics.lower():
                        strengths.append("Search optimization")
                    if 'social' in digital_tactics.lower() or 'influencer' in digital_tactics.lower():
                        strengths.append("Social engagement")
                    
                    # If no specific strengths found, use generic based on threat level
                    if not strengths:
                        threat_level = comp.get('threat_level', 'medium')
                        if threat_level == 'high':
                            strengths = ["Market leadership", "Brand recognition", "Resource advantage"]
                        elif threat_level == 'medium':
                            strengths = ["Growing presence", "Innovation", "Agility"]
                        else:
                            strengths = ["Niche expertise", "Cost efficiency", "Targeted approach"]
                    
                    # Estimate market share based on threat level
                    threat_to_share = {'high': 20 + idx * 2, 'medium': 10 + idx * 2, 'low': 5 + idx}
                    market_share = threat_to_share.get(comp.get('threat_level', 'medium'), 10)
                    
                    competitors_list.append({
                        "name": comp.get('name', ''),
                        "marketShare": market_share,
                        "strengths": strengths[:3],  # Limit to 3 strengths
                        "weaknesses": []  # We don't generate weaknesses in current implementation
                    })
            
            # Create media recommendations based on audience segments and platforms
            media_recommendations = {
                "channels": [],
                "tvNetworks": [],
                "streaming": [],
                "digital": [],
                "social": []
            }
            
            # Extract channel recommendations from audience segments
            channels_set = set()
            if 'audience_segments' in st.session_state and 'segments' in st.session_state.audience_segments:
                for segment in st.session_state.audience_segments['segments']:
                    if 'platform_targeting' in segment:
                        for platform in segment['platform_targeting']:
                            platform_name = platform.get('platform', '')
                            if 'video' in platform_name.lower() or 'ctv' in platform_name.lower() or 'ott' in platform_name.lower():
                                channels_set.add("Streaming")
                            if 'display' in platform_name.lower() or 'programmatic' in platform_name.lower():
                                channels_set.add("Digital")
                            if 'mobile' in platform_name.lower():
                                channels_set.add("Mobile")
                            if 'audio' in platform_name.lower():
                                channels_set.add("Audio")
                            if 'dooh' in platform_name.lower():
                                channels_set.add("Out-of-Home")
            
            # Ensure we have key channels
            channels_set.update(["Digital", "Streaming"])
            media_recommendations["channels"] = list(channels_set)[:4]  # Limit to 4 channels
            
            # Generate TV network recommendations based on industry and audience
            if st.session_state.get('industry', '').lower() in ['sports', 'entertainment', 'media']:
                media_recommendations["tvNetworks"] = [
                    {"name": "ESPN", "reach": "94% sports audience", "targetAudience": "Sports enthusiasts 18-49"},
                    {"name": "FOX Sports", "reach": "92% coverage", "targetAudience": "Live sports viewers"},
                    {"name": "NBC Sports", "reach": "90% coverage", "targetAudience": "Premium sports content"}
                ]
            else:
                media_recommendations["tvNetworks"] = [
                    {"name": "NBC", "reach": "98% market coverage", "targetAudience": "Adults 25-54"},
                    {"name": "CBS", "reach": "97% market coverage", "targetAudience": "Adults 35-64"},
                    {"name": "ABC", "reach": "96% market coverage", "targetAudience": "Family households"}
                ]
            
            # Generate streaming recommendations based on audience segments
            streaming_platforms = []
            for segment in st.session_state.get('audience_segments', {}).get('segments', []):
                age_range = segment.get('targeting_params', {}).get('age_range', '')
                if '18-' in age_range or '25-' in age_range:
                    streaming_platforms.append(
                        {"name": "YouTube TV", "monthlyActiveUsers": "5M+", "engagement": "High - 95 min/day avg"}
                    )
                if '25-' in age_range or '30-' in age_range or '35-' in age_range:
                    streaming_platforms.append(
                        {"name": "Hulu", "monthlyActiveUsers": "48M", "engagement": "High - 87 min/day avg"}
                    )
                if 'premium' in str(segment).lower() or 'high' in segment.get('targeting_params', {}).get('income_targeting', '').lower():
                    streaming_platforms.append(
                        {"name": "Premium Streaming", "monthlyActiveUsers": "Combined 75M+", "engagement": "Premium content viewers"}
                    )
            
            # Ensure we have at least some streaming platforms
            if not streaming_platforms:
                streaming_platforms = [
                    {"name": "Hulu", "monthlyActiveUsers": "48M", "engagement": "High - 87 min/day avg"},
                    {"name": "YouTube TV", "monthlyActiveUsers": "5M+", "engagement": "Growing - 65 min/day avg"},
                    {"name": "Connected TV", "monthlyActiveUsers": "100M+ households", "engagement": "Premium viewing experience"}
                ]
            
            media_recommendations["streaming"] = streaming_platforms[:3]
            
            # Generate digital platform recommendations
            media_recommendations["digital"] = [
                {"name": "Programmatic Display", "impressions": "Billions available", "costEfficiency": "Optimized CPM with advanced targeting"},
                {"name": "Video Advertising", "impressions": "High viewability", "costEfficiency": "Premium CPV with completion rates"},
                {"name": "Native Advertising", "impressions": "Contextual placement", "costEfficiency": "Higher engagement rates"}
            ]
            
            # Generate social recommendations based on audience age demographics
            social_platforms = []
            for segment in st.session_state.get('audience_segments', {}).get('segments', []):
                age_range = segment.get('targeting_params', {}).get('age_range', '')
                if '18-24' in age_range or '16-' in age_range:
                    social_platforms.append(
                        {"name": "TikTok", "demographics": "16-24 primary", "engagementRate": "5.96%"}
                    )
                if '25-' in age_range or '30-' in age_range:
                    social_platforms.append(
                        {"name": "Instagram", "demographics": "25-34 primary", "engagementRate": "3.22%"}
                    )
                if '35-' in age_range or '45-' in age_range or 'professional' in str(segment).lower():
                    social_platforms.append(
                        {"name": "LinkedIn", "demographics": "25-49 professionals", "engagementRate": "2.0%"}
                    )
            
            # Remove duplicates and limit
            seen = set()
            unique_social = []
            for platform in social_platforms:
                if platform['name'] not in seen:
                    seen.add(platform['name'])
                    unique_social.append(platform)
            
            media_recommendations["social"] = unique_social[:3]
            
            # Create the complete analysis object
            complete_analysis = {
                "briefAnalysis": {
                    "industry": st.session_state.get('industry', 'General'),
                    "keyAudiences": key_audiences,
                    "recommendedDMAs": st.session_state.get('recommended_dmas', []),
                    "competitiveInsights": competitive_insights,
                    "growthOpportunities": growth_opportunities,
                    "audienceReach": st.session_state.get('audience_reach', []),
                    "marketInsights": st.session_state.get('market_insights', {})
                },
                "mediaRecommendations": media_recommendations,
                "competitorAnalysis": {
                    "competitors": competitors_list
                },
                "geoData": geo_data
            }
            
            return complete_analysis
        
        # Generate the complete brief analysis
        complete_brief_analysis = create_complete_brief_analysis()
        
        # Store in session state for access by other systems
        st.session_state.complete_brief_analysis = complete_brief_analysis
        # Original DMA visualization code
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        PARENT_DIR = os.path.dirname(CURRENT_DIR)
        HTML_FILE_PATH = os.path.join(PARENT_DIR, "static", "DMA/index.html") 
        
        try:
            with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
                html_code = f.read()

                # Replace placeholders with the complete brief analysis data
                html_code = html_code.replace("{{KEY_AUDIENCES}}", json.dumps(complete_brief_analysis['briefAnalysis'].get('keyAudiences', [])))
                html_code = html_code.replace("{{MEDIA_RECOMMENDATIONS}}", json.dumps(complete_brief_analysis['briefAnalysis'].get('mediaRecommendations', {})))
                html_code = html_code.replace("{{RECOMMENDED_DMAS}}", json.dumps(st.session_state.dma_analysis.get('recommendedDMAs')))
                html_code = html_code.replace("{{AUDIENCE_REACH}}", json.dumps(st.session_state.dma_analysis.get('audienceReach')))
                html_code = html_code.replace("{{MARKET_INSIGHTS}}", json.dumps(st.session_state.dma_analysis.get('marketInsights')))
                # Also pass the complete analysis for potential use
                html_code = html_code.replace("{{COMPLETE_BRIEF_ANALYSIS}}", json.dumps(complete_brief_analysis))
                
                components.html(html_code, height=2000, scrolling=True)

        except FileNotFoundError:
            st.error(f"ERROR: The HTML file was not found at '{HTML_FILE_PATH}'.")
            st.info("Please make sure 'index.html' is in the correct location.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    with tab7:
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

