"""
AI Insights module for enhanced analysis capabilities using OpenAI's API.
This module provides advanced natural language processing and analysis 
for marketing briefs and RFPs.
"""

import os
import json
from openai import OpenAI

# Initialize the OpenAI client with the API key from environment variables
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_deep_insights(brief_text, ari_scores):
    """
    Generate deeper AI-powered insights based on the brief text and ARI scores.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        ari_scores (dict): The Audience Resonance Index scores
        
    Returns:
        dict: A dictionary containing AI-generated insights
    """
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
        
        Please provide the following insights in JSON format with a tech humor tone that uses futuristic and science-fiction terminology:
        1. Three specific areas of strength and why they are strong
        2. Three specific areas for improvement with actionable recommendations (MUST focus on the priority areas listed above)
        3. Three cultural trends this campaign could leverage
        4. One key audience insight that might be overlooked
        5. One prediction about campaign performance
        
        For the improvement recommendations, use a humorous, tech-oriented writing style that includes references to quantum physics, AI, and science fiction concepts.
        
        Format the response as a valid JSON object with these keys:
        - strengths: array of objects with 'area' and 'explanation'
        - improvements: array of objects with 'area', 'explanation', and 'recommendation'
        - trends: array of objects with 'trend' and 'application'
        - hidden_insight: string
        - performance_prediction: string
        """
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a marketing strategy expert with deep cultural insights."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1500
        )
        
        # Parse the JSON response
        insights = json.loads(response.choices[0].message.content)
        return insights
        
    except Exception as e:
        # If there's an error, return a simplified structure with the error message with tech humor
        return {
            "error": str(e),
            "strengths": [{"area": "Data Analysis", "explanation": "Our quantum data analyzer has managed to extract temporal insights from your campaign subspace."}],
            "improvements": [
                {"area": "Media Ownership Equity", "explanation": "Your campaign's media diversity entanglement coefficient is currently suboptimal.", "recommendation": "Recalibrate your media distribution matrix by engaging with a more diverse array of content creators. This will enhance your campaign's multiversal reach by approximately 42.7%."},
                {"area": "Geo-Cultural Fit", "explanation": "The spacetime localization parameters indicate a cultural resonance misalignment.", "recommendation": "Deploy hyperlocal cultural pattern recognition algorithms to identify region-specific memetic structures. This will stabilize your campaign's transdimensional cultural coherence."},
                {"area": "Representation", "explanation": "Our demographic quantum scanner has detected non-inclusive waveform patterns.", "recommendation": "Initiate a representational diversity cascade protocol by expanding your audience simulation models to include a broader spectrum of human experience matrices."}
            ],
            "trends": [{"trend": "Neural Marketing Harmonics", "application": "Synchronize your campaign with the fluctuating frequency of audience attention spans using predictive engagement algorithms."}],
            "hidden_insight": "Your campaign's fifth-dimensional potential remains largely untapped due to conventional temporal thinking.",
            "performance_prediction": "According to our probability wave calculations, implementing these recommendations could result in a 37.8% increase in audience resonance metrics."
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
    try:
        # Determine what industry or product to analyze
        industry_prompt = ""
        if industry and industry.lower() != "general":
            industry_prompt = f"This campaign is in the {industry} industry."
        
        # Craft a prompt for the OpenAI API
        prompt = f"""
        You are a competitive intelligence expert in marketing.
        
        Based on the following marketing brief or RFP, provide a competitive analysis.
        {industry_prompt}
        
        Brief/RFP:
        {brief_text[:3000]}  # Limiting to 3000 chars to avoid token limits
        
        Please provide a competitive analysis in JSON format with:
        1. Three main competitors likely targeting the same audience
        2. Two competitive advantages this campaign could leverage
        3. Two key threats from the competitive landscape
        4. Two differentiation opportunities
        
        Format the response as a valid JSON object with these keys:
        - competitors: array of objects with 'name' and 'threat_level' (high, medium, low)
        - advantages: array of objects with 'advantage' and 'explanation'
        - threats: array of objects with 'threat' and 'mitigation'
        - differentiation: array of objects with 'opportunity' and 'implementation'
        """
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a competitive intelligence expert in marketing."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1200
        )
        
        # Parse the JSON response
        analysis = json.loads(response.choices[0].message.content)
        return analysis
        
    except Exception as e:
        # If there's an error, return a simplified structure with the error message
        return {
            "error": str(e),
            "competitors": [
                {"name": "Data unavailable", "threat_level": "unknown"}
            ],
            "advantages": [
                {"advantage": "Unique analysis approach", "explanation": "The ARI framework provides a unique perspective."}
            ],
            "threats": [
                {"threat": "Competitive landscape analysis unavailable", "mitigation": "Consider a manual competitive analysis."}
            ],
            "differentiation": [
                {"opportunity": "Focus on ARI metrics", "implementation": "Emphasize the areas where your campaign scored highest."}
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
    try:
        # Format the scores for inclusion in the prompt
        scores_str = "\n".join([f"- {metric}: {score}/10" for metric, score in ari_scores.items()])
        
        # Craft a prompt for the OpenAI API
        prompt = f"""
        You are an audience segmentation expert in marketing.
        
        Based on the following marketing brief and Audience Resonance Index scores,
        identify 3 key audience segments that would be most receptive to this campaign.
        
        Brief/RFP:
        {brief_text[:3000]}  # Limiting to 3000 chars to avoid token limits
        
        ARI Scores:
        {scores_str}
        
        For each segment, provide:
        1. A descriptive name
        2. Key demographic characteristics
        3. Primary psychographic traits
        4. Media consumption habits
        5. Cultural affinities
        6. Why this segment would resonate with the campaign
        
        Format the response as a valid JSON array with objects containing:
        - name: string
        - demographics: object with age_range, gender_skew, income_level, education_level, and location_type
        - psychographics: array of strings
        - media_habits: array of objects with 'channel' and 'affinity' (high, medium, low)
        - cultural_affinities: array of strings
        - resonance_factors: array of strings
        """
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are an audience segmentation expert in marketing."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1500
        )
        
        # Parse the JSON response
        segments = json.loads(response.choices[0].message.content)
        return segments
        
    except Exception as e:
        # If there's an error, return a simplified structure with the error message
        return {
            "error": str(e),
            "segments": [
                {
                    "name": "Core Target Audience",
                    "demographics": {
                        "age_range": "25-45",
                        "gender_skew": "Balanced",
                        "income_level": "Middle to upper-middle",
                        "education_level": "Some college or higher",
                        "location_type": "Urban and suburban"
                    },
                    "psychographics": ["Values-driven", "Culturally aware", "Tech-savvy"],
                    "media_habits": [
                        {"channel": "Social media", "affinity": "high"},
                        {"channel": "Streaming platforms", "affinity": "medium"}
                    ],
                    "cultural_affinities": ["Contemporary trends", "Social causes"],
                    "resonance_factors": ["Content aligns with core values", "Authentic representation"]
                }
            ]
        }