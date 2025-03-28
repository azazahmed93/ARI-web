import os
import json
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def analyze_brief_with_ai(brief_text, brand_name="Apple"):
    """
    Use GPT-4o to analyze a marketing brief with Apple-specific insights
    
    Args:
        brief_text (str): The marketing brief text
        brand_name (str): The brand name (default: Apple)
        
    Returns:
        dict: Dictionary with AI-powered insights and recommendations
    """
    try:
        prompt = f"""
        Analyze this {brand_name} marketing brief from a cultural intelligence perspective.
        
        Brief: {brief_text}
        
        Provide a detailed analysis of how well this marketing brief aligns with {brand_name}'s brand 
        positioning and target audiences. Focus on:
        
        1. Cultural Relevance: How well does it connect with cultural touchpoints relevant to {brand_name}'s audience?
        2. Audience Alignment: How well does it address {brand_name}'s target demographics and psychographics?
        3. Platform Strategy: Are the proposed channels and platforms optimal for reaching {brand_name}'s audience?
        4. Creative Approach: Is the creative direction aligned with {brand_name}'s premium positioning?
        5. Key Improvement Areas: What are 3 specific ways this brief could better align with {brand_name}'s audience?
        
        Format your response as JSON with the following structure:
        {{
            "cultural_relevance_score": 1-10 score,
            "cultural_relevance_analysis": "detailed analysis",
            "audience_alignment_score": 1-10 score,
            "audience_alignment_analysis": "detailed analysis",
            "platform_strategy_score": 1-10 score,
            "platform_strategy_analysis": "detailed analysis",
            "creative_alignment_score": 1-10 score,
            "creative_alignment_analysis": "detailed analysis",
            "improvement_areas": ["area 1", "area 2", "area 3"],
            "executive_summary": "brief executive summary of overall analysis"
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        # Parse the JSON response
        result = json.loads(response.choices[0].message.content)
        return result
    
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        # Return a default response if there's an error
        return {
            "cultural_relevance_score": 5,
            "cultural_relevance_analysis": "Analysis not available. Please try again.",
            "audience_alignment_score": 5,
            "audience_alignment_analysis": "Analysis not available. Please try again.",
            "platform_strategy_score": 5,
            "platform_strategy_analysis": "Analysis not available. Please try again.",
            "creative_alignment_score": 5,
            "creative_alignment_analysis": "Analysis not available. Please try again.",
            "improvement_areas": ["Error in AI analysis", "Please try again", "Check API key"],
            "executive_summary": "An error occurred during AI analysis. Please try again."
        }

def generate_ai_recommendations(scores, brand_name="Apple"):
    """
    Generate AI-powered, brand-specific recommendations based on the ARI scores
    
    Args:
        scores (dict): Dictionary of ARI metric scores
        brand_name (str): The brand name (default: Apple)
        
    Returns:
        dict: Dictionary with recommendations for each low-scoring area
    """
    try:
        # Identify the lowest scoring areas (below 7)
        low_scores = {k: v for k, v in scores.items() if v < 7}
        if not low_scores:
            # If no low scores, get the lowest 2
            sorted_scores = sorted(scores.items(), key=lambda x: x[1])
            low_scores = dict(sorted_scores[:2])
        
        # Create prompt for generating recommendations
        metrics_list = ", ".join([f"{k} ({v}/10)" for k, v in low_scores.items()])
        prompt = f"""
        Generate specific, actionable recommendations for improving the following metrics in an {brand_name} marketing campaign:
        
        {metrics_list}
        
        For each metric, provide:
        1. A brief explanation of why this area is important for {brand_name}'s audience
        2. Three specific, tactical recommendations that would improve this score
        3. Examples of how other premium brands have successfully addressed this area
        
        Format your response as JSON with the following structure for each metric:
        {{
            "metric_name": {{
                "importance": "explanation of importance",
                "recommendations": ["rec 1", "rec 2", "rec 3"],
                "examples": ["example 1", "example 2"]
            }},
            ...
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        # Parse the JSON response
        recommendations = json.loads(response.choices[0].message.content)
        return recommendations
    
    except Exception as e:
        print(f"Error generating AI recommendations: {e}")
        # Return a default response if there's an error
        default_response = {}
        for metric in scores:
            if scores[metric] < 7:
                default_response[metric] = {
                    "importance": f"This is an important area for {brand_name}'s marketing strategy.",
                    "recommendations": [
                        "Consider revising your approach based on audience insights.",
                        "Analyze successful campaigns in this area.",
                        "Consult with cultural specialists for this target audience."
                    ],
                    "examples": [
                        "Other premium brands have addressed this through focused research.",
                        "Successful campaigns often integrate this element more deeply."
                    ]
                }
        
        if not default_response:
            default_response["General Improvements"] = {
                "importance": "Continuous improvement is essential for marketing excellence.",
                "recommendations": [
                    "Review your highest scoring areas for opportunities to excel further.",
                    "Consider A/B testing variations of your strongest elements.",
                    "Benchmark against industry leaders in each category."
                ],
                "examples": [
                    "Leading brands constantly refine even their strongest areas.",
                    "Premium positioning requires excellence across all metrics."
                ]
            }
        
        return default_response