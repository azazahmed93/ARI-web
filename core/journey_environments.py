"""
Journey Environments Resonance Scoring Module
Generates AI-powered resonance scores for ad formats and programming shows
based on RFP audience profile and campaign objectives.
"""
import os
from typing import Dict, Any, List, Optional
from core.ai_utils import make_openai_request


def generate_retargeting_channels(
    audience_profile: Optional[Dict[str, Any]] = None,
    campaign_objectives: Optional[List[str]] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Generate AI-powered retargeting channel recommendations with reasons.

    Args:
        audience_profile: Demographics and psychographics from RFP
        campaign_objectives: Campaign goals and requirements

    Returns:
        List of retargeting channel objects with scores and reasons
    """
    if not os.environ.get("OPENAI_API_KEY"):
        return None

    # Build context from RFP data
    context = ""
    if audience_profile:
        demographics = audience_profile.get('demographics', {})
        context += f"""
Audience Profile:
- Age Range: {demographics.get('ageRange', 'N/A')}
- Profession: {demographics.get('profession', 'N/A')}
- Income Level: {demographics.get('incomeLevel', 'N/A')}
- Affluence: {demographics.get('affluence', 'N/A')}
"""

    if campaign_objectives:
        context += f"\n\nCampaign Objectives: {', '.join(campaign_objectives)}"

    prompt = f"""Based on the following audience profile, generate retargeting channel recommendations for extending airport advertising reach.

{context if context else "Use general business traveler audience assumptions."}

Analyze these 3 retargeting channels and rank them by how well they match the audience profile:
1. Connected TV (streaming platforms)
2. Online Video (pre-roll/mid-roll)
3. Display Ads (web/mobile banners)

For each channel, provide:
1. resonanceScore: Score 0-100 based on actual audience alignment with the channel
2. matchLevel: "best", "strong", or "good" - assign based on resonance score and audience fit
   - Use "best" for the highest-scoring channel that best matches the audience
   - Use "strong" for channels with good alignment but not the top choice
   - Use "good" for channels with moderate alignment
3. reasons: Array of 3 specific reasons why this channel matches (or doesn't match) the audience profile
   - Each reason should reference specific demographics or behaviors from the profile
   - Make reasons data-driven and specific to the audience profile
   - Include percentages or statistics when relevant to the specific audience
   - Reasons should justify the resonance score and match level

IMPORTANT: Determine match levels based on the actual audience profile provided, not assumptions.

Return ONLY valid JSON object with 'channels' key containing an array with this exact structure:
{{
  "channels": [
    {{
      "id": "connected-tv",
      "name": "Connected TV",
      "description": "Premium streaming platforms with high engagement",
      "icon": "Tv",
      "resonanceScore": 94,
      "matchLevel": "best",
      "reasons": [
        "Specific reason 1 with data",
        "Specific reason 2 with data",
        "Specific reason 3 with data"
      ]
    }},
    {{
      "id": "online-video",
      "name": "Online Video",
      "description": "Pre-Roll and Mid-Roll in premium video players and inventory",
      "icon": "Youtube",
      "resonanceScore": 88,
      "matchLevel": "strong",
      "reasons": [
        "Specific reason 1 with data",
        "Specific reason 2 with data",
        "Specific reason 3 with data"
      ]
    }},
    {{
      "id": "display-ads",
      "name": "Display Ads",
      "description": "Banner and native ads across web and mobile",
      "icon": "Monitor",
      "resonanceScore": 82,
      "matchLevel": "good",
      "reasons": [
        "Specific reason 1 with data",
        "Specific reason 2 with data",
        "Specific reason 3 with data"
      ]
    }}
  ]
}}"""

    messages = [
        {
            "role": "system",
            "content": "You are an expert digital media strategist specializing in retargeting and audience extension. Generate data-driven channel recommendations in JSON format."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response = make_openai_request(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000
        )

        if response and 'channels' in response:
            return response['channels']
        elif response:
            # Try to extract array from response
            for key in response.keys():
                if isinstance(response[key], list):
                    return response[key]

        return None

    except Exception as e:
        print(f"Error generating retargeting channels: {e}")
        return None


def generate_resonance_scores(
    audience_profile: Optional[Dict[str, Any]] = None,
    campaign_objectives: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Generate resonance scores for existing ad formats and programming shows.

    Args:
        audience_profile: Demographics and psychographics from RFP
        campaign_objectives: Campaign goals and requirements

    Returns:
        Dictionary with ad_format_scores, programming_show_scores, and retargeting_channels
    """
    if not os.environ.get("OPENAI_API_KEY"):
        return None

    # Build context from RFP data
    context = ""
    if audience_profile:
        demographics = audience_profile.get('demographics', {})
        context += f"""
Audience Profile:
- Age Range: {demographics.get('ageRange', 'N/A')}
- Profession: {demographics.get('profession', 'N/A')}
- Income Level: {demographics.get('incomeLevel', 'N/A')}
- Affluence: {demographics.get('affluence', 'N/A')}
"""
        if audience_profile.get('psychographics'):
            context += f"\nPsychographics: {str(audience_profile.get('psychographics'))[:200]}"

    if campaign_objectives:
        context += f"\n\nCampaign Objectives: {', '.join(campaign_objectives)}"

    prompt = f"""Based on the following audience profile and campaign objectives, generate resonance scores (0-100) for ReachTV ad formats and programming shows.

{context if context else "Use general business traveler audience assumptions."}

Calculate resonance scores based on:
- Audience alignment (demographics, psychographics, profession)
- Campaign objective fit
- Environment appropriateness (airport/travel context)
- Engagement potential

**AD FORMATS TO SCORE:**
1. instream-video: In-Stream Video Ads - Full screen video ads within premium programming
2. lbar-ads: L-Bar/Squeeze Back Ads - Branded skin wraps around content
3. pip-ads: Picture-in-Picture Ads - Ad plays alongside live sports content
4. sponsorship-billboards: Sponsorship Billboards - Intro/outro segment sponsorships
5. custom-branded-content: Custom Branded Content - Bespoke programming content
6. inshow-integration: Brand/Product In-Show Integration - Brand integration in series
7. tower-ads: Tower Ads - Vertical banner ads alongside content
8. hotel-welcome-screen: Hotel Welcome Screen - Personalized room TV greeting
9. hotel-video-ads: Hotel Video Ads - Video ads in hotel TV systems
10. hotel-guide-banner: Hotel Guide Banner - Banner ads in hotel entertainment guides
11. inflight-wifi: Inflight WiFi Portal Ads - Ads on inflight WiFi login/portal screens

**PROGRAMMING SHOWS TO SCORE:**
1. bloomberg-news: Bloomberg News - Financial news and market updates
2. business-traveler-show: The Business Traveler Show - Travel insights for professionals
3. market-movers: Market Movers: Opening Bell - Morning market analysis
4. travel-takeover: Travel Takeover / Variety - Travel destinations and lifestyle
5. trivia-airport: Trivia at the Airport with Maria Menounos - Interactive trivia
6. nfl-films: NFL Films Presents - Behind-the-scenes NFL content
7. in-depth-bensinger: In Depth with Graham Bensinger - Sports/entertainment interviews
8. global-child-tv: Global Child TV - Family-friendly content
9. mr-lynns-taste-trip: Mr. Lynn's Taste Trip - Culinary adventures and food exploration
10. nfl-top-10: NFL Top 10 - Top NFL moments and highlights
11. business-of-sports: Business of Sports - Sports industry and business analysis
12. cultural-eats: Cultural Eats with Chef Eric Adjepong - Culinary travel show
13. discover-more-maria: Discover More with Maria Menounos - Lifestyle and discovery
14. life-of-kai: Life of Kai - Lifestyle and adventure content
15. nascar-reality: NASCAR Reality - Behind-the-scenes NASCAR content
16. ncaa-virginia-tech: NCAA Virginia Tech - College sports programming
17. nfl-vikings-packers: NFL Vikings vs Packers - NFL game content

Return ONLY valid JSON object with this exact structure (use these EXACT keys):
{{
  "ad_format_scores": {{
    "instream-video": 92,
    "lbar-ads": 88,
    "pip-ads": 85,
    "sponsorship-billboards": 90,
    "custom-branded-content": 95,
    "inshow-integration": 93,
    "tower-ads": 87,
    "hotel-welcome-screen": 84,
    "hotel-video-ads": 86,
    "hotel-guide-banner": 89,
    "inflight-wifi": 82
  }},
  "programming_show_scores": {{
    "bloomberg-news": 88,
    "business-traveler-show": 92,
    "market-movers": 86,
    "travel-takeover": 84,
    "trivia-airport": 78,
    "nfl-films": 95,
    "in-depth-bensinger": 82,
    "global-child-tv": 75,
    "mr-lynns-taste-trip": 80,
    "nfl-top-10": 85,
    "business-of-sports": 81,
    "cultural-eats": 80,
    "discover-more-maria": 81,
    "life-of-kai": 77,
    "nascar-reality": 88,
    "ncaa-virginia-tech": 76,
    "nfl-vikings-packers": 87
  }}
}}"""

    messages = [
        {
            "role": "system",
            "content": "You are an expert media analyst specializing in audience alignment and resonance scoring. Generate accurate resonance scores (0-100) in JSON format."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response = make_openai_request(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1500
        )

        result = {}

        if response and 'ad_format_scores' in response and 'programming_show_scores' in response:
            result['ad_format_scores'] = response['ad_format_scores']
            result['programming_show_scores'] = response['programming_show_scores']
        else:
            return None

        # Generate retargeting channels
        print("Generating retargeting channel recommendations...")
        retargeting_channels = generate_retargeting_channels(
            audience_profile=audience_profile,
            campaign_objectives=campaign_objectives
        )

        if retargeting_channels:
            result['retargeting_channels'] = retargeting_channels
            print(f"Generated {len(retargeting_channels)} retargeting channel recommendations")

        return result

    except Exception as e:
        print(f"Error generating resonance scores: {e}")
        return None
