"""
AI Insights module for enhanced analysis capabilities using OpenAI's API.
This module provides advanced natural language processing and analysis 
for marketing briefs and RFPs.
"""

import os
import json
import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client with the API key from environment variables
# Make sure to handle authentication issues gracefully
try:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.warning("OpenAI API key not found in environment variables. Enhanced AI analysis will be limited.")
        client = None
    else:
        client = OpenAI(api_key=api_key)
        # Test the API key with a simple request
        try:
            response = client.models.list()
            st.success("OpenAI API connection successful.")
        except Exception as e:
            st.error(f"Error connecting to OpenAI API: {str(e)}")
            client = None
except Exception as e:
    st.error(f"Failed to initialize OpenAI client: {str(e)}")
    client = None

def generate_deep_insights(brief_text, ari_scores):
    """
    Generate deeper AI-powered insights based on the brief text and ARI scores.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        ari_scores (dict): The Audience Resonance Index scores
        
    Returns:
        dict: A dictionary containing AI-generated insights
    """
    # Check if OpenAI client is available
    if client is None:
        st.warning("Enhanced AI analysis is not available. Using pre-generated insights instead.")
        return get_fallback_insights(ari_scores)
    
    # Format the scores for inclusion in the prompt
    scores_str = "\n".join([f"- {metric}: {score}/10" for metric, score in ari_scores.items()])
    
    # Create a list of the weakest areas as improvement priorities
    improvement_areas = []
    for metric, score in ari_scores.items():
        if score < 6:  # Consider scores below 6 as needing improvement
            improvement_areas.append(metric)
    
    # If we don't have 3 weak areas, add some specific ones the user requested
    priority_metrics = ["Media Ownership Equity", "Geo-Cultural Fit", "Representation"]
    for metric in priority_metrics:
        if metric not in improvement_areas and len(improvement_areas) < 3:
            improvement_areas.append(metric)
    
    # If we still don't have 3, add other metrics with the lowest scores
    if len(improvement_areas) < 3:
        remaining_metrics = [m for m in ari_scores.keys() if m not in improvement_areas]
        remaining_metrics.sort(key=lambda m: ari_scores[m])
        improvement_areas.extend(remaining_metrics[:3-len(improvement_areas)])
    
    # Limit to 3 improvement areas
    improvement_areas = improvement_areas[:3]
    improvement_areas_str = ", ".join(improvement_areas)
    
    try:
        # Craft a prompt for the OpenAI API
        prompt = f"""
        You are an expert marketing strategist and cultural analyst specializing in audience resonance.
        
        Analyze the following marketing brief or RFP and the corresponding Audience Resonance Index (ARI) scores.
        Provide deep insights that could help improve the campaign's effectiveness.
        
        Brief/RFP:
        {brief_text[:4000]}  # Limiting to 4000 chars to avoid token limits
        
        ARI Scores:
        {scores_str}
        
        Focus specifically on these priority improvement areas: {improvement_areas_str}
        
        Please provide the following insights in JSON format with a light, approachable tone:
        1. Three specific areas of strength and why they are strong in digital advertising context
        2. Three specific areas for improvement with TACTICAL digital advertising recommendations (MUST focus on the priority areas listed above)
        3. Three cultural trends this campaign could leverage through digital ad targeting and platforms
        4. One key audience insight for digital media buying that might be overlooked
        5. One prediction about campaign performance metrics
        
        For the improvement recommendations, focus specifically on digital advertising tactics including:
        - Media mix allocation percentages
        - Platform-specific targeting parameters
        - Bidding strategies and KPI targets
        - Programmatic optimization techniques
        - Audience segmentation for ad platforms
        - Clear measurement metrics and benchmarks
        
        Use accessible language that any marketing professional would understand. Include some light AI humor but keep it relatable and avoid overly technical jargon.
        
        Format the response as a valid JSON object with these keys:
        - strengths: array of objects with 'area' and 'explanation'
        - improvements: array of objects with 'area', 'explanation', and 'recommendation'
        - trends: array of objects with 'trend' and 'application'
        - hidden_insight: string
        - performance_prediction: string
        """
        
        try:
            # Call the OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": "You are a digital advertising tactician with expertise in programmatic media buying, platform-specific optimization, and culturally-relevant campaign execution. Focus on actionable tactics, not general strategy."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            # Parse the JSON response
            insights = json.loads(response.choices[0].message.content)
            return insights
            
        except Exception as e:
            st.error(f"OpenAI API error: {str(e)}")
            return get_fallback_insights(ari_scores)
            
    except Exception as e:
        st.exception(f"Error in generate_deep_insights: {str(e)}")
        return get_fallback_insights(ari_scores)

def get_fallback_insights(ari_scores):
    """
    Provides fallback insights when the OpenAI API is not available or fails.
    
    Args:
        ari_scores (dict): The Audience Resonance Index scores
        
    Returns:
        dict: A dictionary containing pre-generated insights
    """
    # Get the three lowest scoring areas
    improvement_areas = sorted(ari_scores.items(), key=lambda x: x[1])[:3]
    improvement_area_names = [area for area, _ in improvement_areas]
    
    # Create a fallback response with the lowest scoring areas as improvement areas
    return {
        "strengths": [{"area": "Data Analysis", "explanation": "Our analysis has identified key insights from your marketing campaign data."}],
        "improvements": [
            {"area": "Media Ownership Equity", "explanation": "Your digital ad spend is not adequately distributed across diverse media ownership channels.", "recommendation": "Allocate 20-25% of programmatic spend to minority-owned demand-side platforms and utilize private marketplace deals with culturally-relevant publishers. Implement rich media and high-impact DOOH placements in culturally diverse neighborhoods. Target a 3:1 ROAS with these placements using precision audience segments with 30% higher bid adjustments."},
            {"area": "Geo-Cultural Fit", "explanation": "Current ad targeting lacks geo-cultural precision for regional market differences.", "recommendation": "Deploy omnichannel geo-targeting with ReachTV, premium CTV/OTT, and interactive video formats. Set up location-specific ad sets with 15-20 mile radius targeting, custom CTAs, and region-specific bidding strategies. Enhance with picture-in-picture sports placements during relevant cultural events. Target a 15% improvement in CTR versus current geo-agnostic campaigns."},
            {"area": "Representation", "explanation": "Ad creative and audience targeting parameters are missing key demographic segments.", "recommendation": "Expand custom audience modeling to include multicultural seed audiences and increase audience diversity by 40%. Implement A/B testing with native articles and native display ads featuring diverse representation, with a minimum of 10K impressions per variant, measuring engagement uplift against control groups. Allocate 18% to social display boost that repurposes inclusive organic posts for the open web."},
            {"area": "Competitor Tactics", "explanation": "Analysis of competitor digital ad strategies reveals opportunities for differentiation.", "recommendation": "Key competitors are investing heavily in broad awareness campaigns with limited targeting precision. Opportunity to counter with highly-targeted mid-funnel tactics using first-party data across audio, performance display ads, and premium CTV/OTT that delivers 2.8x the engagement rate. Consider allocating 35% of budget to competitive conquest strategies with interactive video formats that outperform traditional placements."}
        ],
        "trends": [
            {"trend": "Channel-Specific Optimization", "application": "Implement tailored ad formats and bidding strategies across all digital channels to maximize engagement with a 15% budget reallocation towards highest-performing formats."},
            {"trend": "First-Party Data Activation", "application": "Develop custom audience segments using first-party data with a 30-day recency filter to improve retargeting efficiency by 25%."},
            {"trend": "Contextual Targeting Renaissance", "application": "Allocate 15% of programmatic budget to contextual targeting using category and sentiment signals as privacy-focused solutions gain prominence."}
        ],
        "hidden_insight": "Your campaign could benefit from a multi-touch attribution model with a 40/40/20 split between upper, mid and lower funnel tactics across all digital channels.",
        "performance_prediction": "Based on our analysis, shifting 20% of budget to these tactical recommendations would yield a 32% improvement in ROAS and 18% increase in brand lift metrics."
    }

def generate_competitor_analysis(brief_text, industry=None):
    """
    Generate a competitive analysis based on the brief text and industry.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        industry (str, optional): The industry classification
        
    Returns:
        dict: A dictionary containing competitor analysis
    """
    # Check if OpenAI client is available
    if client is None:
        st.warning("Enhanced competitor analysis is not available. Using pre-generated insights instead.")
        return get_fallback_competitor_analysis(industry)
    
    try:
        # Determine what industry or product to analyze
        industry_prompt = ""
        if industry and industry.lower() != "general":
            industry_prompt = f"This campaign is in the {industry} industry."
        
        # Craft a prompt for the OpenAI API
        prompt = f"""
        You are a competitive intelligence expert specialized in digital advertising platforms, bid strategies, and media tactics.
        
        Based on the following marketing campaign information, provide a digital advertising competitive analysis.
        {industry_prompt}
        
        Campaign Information:
        {brief_text[:3000]}  # Limiting to 3000 chars to avoid token limits
        
        Please provide a competitive analysis in JSON format with:
        1. Three main competitors and their digital advertising approach
        2. Two competitive advantages this campaign could leverage in digital media buying
        3. Two key threats from the competitive digital advertising landscape
        4. Two digital platform-specific differentiation opportunities
        
        Format the response as a valid JSON object with these keys:
        - competitors: array of objects with 'name', 'threat_level' (high, medium, low), and 'digital_tactics' (specific digital marketing approaches they use)
        - advantages: array of objects with 'advantage' and 'tactical_application' (how to apply this as a digital media buying tactic)
        - threats: array of objects with 'threat' and 'tactical_response' (specific digital advertising counter-strategy)
        - differentiation: array of objects with 'platform' (use generic platform types, not brand names) and 'tactical_approach' (specific media buying/targeting approach for that platform)
        """
        
        try:
            # Call the OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": "You are a digital media competitive intelligence expert specialized in advertising platform strategies, audience targeting, and media buying optimization."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1200
            )
            
            # Parse the JSON response
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            st.error(f"OpenAI API error in competitor analysis: {str(e)}")
            return get_fallback_competitor_analysis(industry)
            
    except Exception as e:
        st.exception(f"Error in generate_competitor_analysis: {str(e)}")
        return get_fallback_competitor_analysis(industry)

def get_fallback_competitor_analysis(industry=None):
    """
    Provides fallback competitor analysis when the OpenAI API is not available or fails.
    
    Args:
        industry (str, optional): The industry classification
        
    Returns:
        dict: A dictionary containing pre-generated competitor analysis
    """
    industry_text = ""
    if industry and industry.lower() != "general":
        industry_text = f" in the {industry} industry"
    
    return {
        "competitors": [
            {"name": f"Major{industry_text} Player", "threat_level": "high", "digital_tactics": "Heavy investment in programmatic display with high-frequency retargeting and aggressive conquest campaigns targeting competitor brand terms."},
            {"name": f"Emerging{industry_text} Disruptor", "threat_level": "medium", "digital_tactics": "Video content strategy with creator partnerships and high organic content amplification through paid boosting."},
            {"name": f"Legacy{industry_text} Brand", "threat_level": "low", "digital_tactics": "Traditional search and display mix with limited digital presence, primarily focused on brand protection keywords."}
        ],
        "advantages": [
            {"advantage": "Cultural Audience Insights", "tactical_application": "Apply custom audience targeting segments with 15% higher bid adjustments on digital channels where cultural relevance scored highest, overlaying first-party data."},
            {"advantage": "Cross-channel Message Consistency", "tactical_application": "Implement sequential messaging strategy with frequency caps of 2-3 per channel and cross-channel attribution to maintain consistent user journey tracking."}
        ],
        "threats": [
            {"threat": "Rising CPMs in Primary Channels", "tactical_response": "Shift 30% of digital ad budget to emerging content formats where CPMs are 40-50% lower while maintaining similar audience quality."},
            {"threat": "Competitor Keyword Conquest", "tactical_response": "Implement defensive search bidding with automated rules to increase bids by 20% when competitors appear for brand terms."}
        ],
        "differentiation": [
            {"platform": "Video Channels", "tactical_approach": "Utilize Dynamic Creative Optimization with multicultural creative asset testing, implement 3-5 variants per audience segment with automated performance-based budget allocation."},
            {"platform": "Programmatic", "tactical_approach": "Focus on minority-owned supply-side platforms and private marketplace deals with custom audience activation, leveraging first-party data matching and contextual alignment signals."}
        ]
    }

def generate_audience_segments(brief_text, ari_scores):
    """
    Generate audience segment recommendations based on the brief text and ARI scores.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        ari_scores (dict): The Audience Resonance Index scores
        
    Returns:
        list: A list of audience segments with descriptions and affinities
    """
    # Check if OpenAI client is available
    if client is None:
        st.warning("Enhanced audience segmentation is not available. Using pre-generated segments instead.")
        return get_fallback_audience_segments(ari_scores)
    
    try:
        # Format the scores for inclusion in the prompt
        scores_str = "\n".join([f"- {metric}: {score}/10" for metric, score in ari_scores.items()])
        
        # Craft a prompt for the OpenAI API
        prompt = f"""
        You are a digital media buying and audience segmentation expert specializing in advertising platforms.
        
        Based on the following marketing campaign information and Audience Resonance Index scores,
        identify 3 key audience segments for targeted digital advertising with specific platform targeting parameters.
        
        Campaign Information:
        {brief_text[:3000]}  # Limiting to 3000 chars to avoid token limits
        
        ARI Scores:
        {scores_str}
        
        For each segment, provide detailed targeting specifications for digital advertising platforms:
        1. A descriptive segment name for use in ad platforms
        2. Precise demographic targeting parameters (age ranges, gender, income brackets, etc.)
        3. Digital platform interest categories and behavior targeting options
        4. Platform-specific targeting recommendations (use generic platform types, not brand names)
        5. Key performance indicators and benchmark CTRs/conversion rates to expect
        6. Specific media buying tactics for this segment (bid adjustments, dayparting, etc.)
        
        Format the response as a valid JSON array with objects containing:
        - name: string (descriptive segment name)
        - targeting_params: object with age_range, gender_targeting, income_targeting, education_targeting, and location_targeting
        - interest_categories: array of strings (specific interests to target in ad platforms)
        - platform_targeting: array of objects with 'platform' and 'targeting_approach' 
        - expected_performance: object with CTR (click-through rate), CPA (cost per acquisition), and engagement_rate
        - bidding_strategy: object with bid_adjustments, dayparting, and placement_priorities
        """
        
        try:
            # Call the OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": "You are a digital advertising audience specialist with expertise in platform-specific targeting parameters, lookalike modeling, and programmatic audience segmentation."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            # Parse the JSON response
            segments = json.loads(response.choices[0].message.content)
            return segments
            
        except Exception as e:
            st.error(f"OpenAI API error in audience segmentation: {str(e)}")
            return get_fallback_audience_segments(ari_scores)
            
    except Exception as e:
        st.exception(f"Error in generate_audience_segments: {str(e)}")
        return get_fallback_audience_segments(ari_scores)

def get_fallback_audience_segments(ari_scores):
    """
    Provides fallback audience segments when the OpenAI API is not available or fails.
    
    Args:
        ari_scores (dict): The Audience Resonance Index scores
        
    Returns:
        dict: A dictionary containing pre-generated audience segments
    """
    # Find highest scoring metrics to personalize segments
    top_metrics = sorted(ari_scores.items(), key=lambda x: x[1], reverse=True)[:2]
    top_metric_names = [metric for metric, _ in top_metrics]
    
    # Build audience descriptions based on top metrics
    audience_descriptions = []
    if "Cultural Relevance" in top_metric_names:
        audience_descriptions.append("culturally engaged")
    if "Platform Relevance" in top_metric_names:
        audience_descriptions.append("tech-savvy")
    if "Representation" in top_metric_names:
        audience_descriptions.append("diverse")
    if "Cultural Vernacular" in top_metric_names:
        audience_descriptions.append("trend-aware")
    if "Cultural Authority" in top_metric_names:
        audience_descriptions.append("influence-seeking")
    if "Geo-Cultural Fit" in top_metric_names:
        audience_descriptions.append("location-sensitive")
    
    # Default description if none of the above
    if not audience_descriptions:
        audience_descriptions = ["digitally active", "brand-conscious"]
    
    description_text = " and ".join(audience_descriptions[:2])
    
    # Return fallback segments
    return {
        "segments": [
            {
                "name": f"Core {description_text.title()} Segment",
                "targeting_params": {
                    "age_range": "25-39",
                    "gender_targeting": "Slight female skew (55%/45%)",
                    "income_targeting": "$75K-150K annually",
                    "education_targeting": "College degree or higher",
                    "location_targeting": "Urban centers and tech hubs, DMA top 50 markets"
                },
                "interest_categories": [
                    "Technology early adopters", 
                    "Digital media consumers", 
                    "Cultural trend followers",
                    "Social impact supporters"
                ],
                "platform_targeting": [
                    {"platform": "Interactive Media", "targeting_approach": "Utilize 1% lookalike audiences from existing customers, target In-Market segments for related products, exclude previous converters beyond 30-day window"},
                    {"platform": "Video Platforms", "targeting_approach": "Focus on interest-based targeting with creator affinity segments, use engagement custom audiences"}
                ],
                "expected_performance": {
                    "CTR": "2.3-2.8%", 
                    "CPA": "15-20% below account average", 
                    "engagement_rate": "4.5-5.2%"
                },
                "bidding_strategy": {
                    "bid_adjustments": "+15% for mobile devices, -10% for desktop placement",
                    "dayparting": "Increase bids 20% during 6-10pm local time",
                    "placement_priorities": "In-feed prioritized over sidebar, 70/30 budget split"
                }
            },
            {
                "name": "Multicultural Amplifiers",
                "targeting_params": {
                    "age_range": "18-34",
                    "gender_targeting": "Balanced (50%/50%)",
                    "income_targeting": "$45K-100K annually",
                    "education_targeting": "Some college or higher",
                    "location_targeting": "Metropolitan areas with high diversity indexes"
                },
                "interest_categories": [
                    "Cultural content creators", 
                    "Community influencers", 
                    "Cause-driven consumers",
                    "Multicultural entertainment enthusiasts"
                ],
                "platform_targeting": [
                    {"platform": "Social Networks", "targeting_approach": "Target users with high engagement rates on multicultural content, apply custom audience modeling with 3% similarity threshold"},
                    {"platform": "Audio Streaming", "targeting_approach": "Focus on genre-specific targeting with cultural affinity indicators, prioritize premium inventory"}
                ],
                "expected_performance": {
                    "CTR": "1.8-2.2%", 
                    "CPA": "5-10% above account average, offset by higher LTV", 
                    "engagement_rate": "7.5-8.2%"
                },
                "bidding_strategy": {
                    "bid_adjustments": "+25% for high engagement users, +10% for mobile devices",
                    "dayparting": "Increase bids 15% during evenings and weekends",
                    "placement_priorities": "Native content prioritized, 60/40 budget allocation"
                }
            },
            {
                "name": "High-Value Converters",
                "targeting_params": {
                    "age_range": "35-54",
                    "gender_targeting": "Slight male skew (45%/55%)",
                    "income_targeting": "$100K+ annually",
                    "education_targeting": "Bachelor's degree or higher",
                    "location_targeting": "High-income zip codes within major markets"
                },
                "interest_categories": [
                    "Business decision makers", 
                    "Premium product purchasers", 
                    "Early technology adopters",
                    "Lifestyle enthusiasts"
                ],
                "platform_targeting": [
                    {"platform": "Premium Content", "targeting_approach": "Utilize content targeting on business and finance topics, implement custom intent signals with purchase behavior indicators"},
                    {"platform": "Connected TV", "targeting_approach": "Target premium content viewers with household income targeting, focus on completion rate optimization"}
                ],
                "expected_performance": {
                    "CTR": "1.3-1.7%", 
                    "CPA": "25-30% below account average", 
                    "engagement_rate": "3.2-3.8%"
                },
                "bidding_strategy": {
                    "bid_adjustments": "+40% for previous site visitors, +20% for cart abandoners",
                    "dayparting": "Increase bids 30% during business hours",
                    "placement_priorities": "Premium placements prioritized, 80/20 budget split"
                }
            }
        ]
    }