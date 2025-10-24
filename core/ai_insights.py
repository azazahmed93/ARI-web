"""
AI Insights module for enhanced analysis capabilities using OpenAI's API.
This module provides advanced natural language processing and analysis 
for marketing briefs and RFPs.
"""
from typing import  Any
import os
import json
import re
from openai import OpenAI
import base64
import json
from assets.content import PSYCHOGRAPHIC_HIGHLIGHTS
from core.utils import get_first_file_name
from core.ai_utils import make_openai_request

PATHS = {
    "JSON": "research/json",
    "PSYCHOGRAPHY": "research/psychography-uploads",
    "MEDIA_CONSUMPTION": "research/media-consumption-uploads",
    "SITES_AFFINITY": "research/sites-affinity-uploads"
}
demo = True

# Initialize the OpenAI client with the API key from environment variables
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def fix_grammar_and_duplicates(text):
    """
    Completely overhauled function to fix grammar issues, duplicates, and
    awkward phrasing typically found in AI-generated marketing text.
    
    Args:
        text (str): The text to clean up
        
    Returns:
        str: Professionally edited text with all issues fixed
    """
    if not text:
        return text
    
    # Step 1: Initial preprocessing and normalization
    # ---------------------------------------------
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Step 2: Fix common AI awkward phrasings
    # --------------------------------------
    
    # List of problematic phrases and their replacements
    awkward_phrases = [
        # Basic duplicates
        (r'\b(\w+)\s+\1\b', r'\1'),
        
        # Verb + through/by/with + same verb patterns
        (r'\b(implement|utilize|leverage|develop|create|establish|execute)\s+through\s+\1ing\b', r'\1'),
        (r'\b(implement|utilize|leverage|develop|create|establish|execute)\s+by\s+\1ing\b', r'\1'),
        (r'\b(implement|utilize|leverage|develop|create|establish|execute)\s+with\s+\1\b', r'\1'),
        
        # Preposition duplications
        (r'\b(through|by|as|among|for|to|with|in|on|of)\s+\1\b', r'\1'),
        
        # Marketing jargon redundancies
        (r'strategic strategy', 'strategy'),
        (r'optimized optimization', 'optimization'),
        (r'engaged engagement', 'engagement'),
        (r'targeted targeting', 'targeting'),
        (r'implemented implementation', 'implementation'),
        (r'leveraged leverage', 'leverage'),
        (r'utilized utilization', 'utilization'),
        (r'leveraging leverage', 'leveraging'),
        
        # Specific incorrect constructions
        (r'leverage through', 'leverage by implementing'),
        (r'implement through', 'implement by'),
        (r'utilize through', 'utilize by'),
        
        # Fix is using/utilizes redundancy
        (r'is using utilizes', 'utilizes'),
        (r'is utilizing utilizes', 'utilizes'),
        (r'utilizes utilizes', 'utilizes'),
        (r'using utilizes', 'utilizes'),
        (r'is using uses', 'uses'),
        
        # Fix verb-noun agreement issues
        (r'implements implements', 'implements'),
        (r'develops develops', 'develops'),
        (r'creates creates', 'creates'),
        (r'utilizes utilizes', 'utilizes'),
        (r'leverages leverages', 'leverages'),
        
        # Fix verb-preposition-verb patterns
        (r'leverage to leverage', 'leverage'),
        (r'utilize to utilize', 'utilize'),
        (r'implement to implement', 'implement')
    ]
    
    # Apply all replacements
    for pattern, replacement in awkward_phrases:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Step 3: Fix specific "is using [Verb]" patterns
    # ---------------------------------------------
    
    # Create a comprehensive list of verbs that commonly appear in these patterns
    marketing_verbs = [
        'utilizes', 'implements', 'leverages', 'employs', 'develops', 
        'creates', 'executes', 'deploys', 'establishes', 'incorporates'
    ]
    
    # Fix "[Subject] is using [MarketingVerb]" patterns
    for verb in marketing_verbs:
        # Handle capitalized and lowercase variants
        cap_verb = verb.capitalize()
        pattern = rf'is using {cap_verb}'
        text = re.sub(pattern, verb, text, flags=re.IGNORECASE)
        
        # Also fix "[Subject] is using and [MarketingVerb]" patterns
        pattern = rf'is using and {verb}'
        text = re.sub(pattern, verb, text, flags=re.IGNORECASE)
    
    # Step 4: Direct replacements for common problematic patterns
    # ---------------------------------------------------------
    direct_replacements = {
        # Specific problematic patterns
        "is using Utilizes": "utilizes",
        "is using utilizes": "utilizes",
        "Leverage through Leverage": "Leverage by implementing",
        "leverage through leverage": "leverage by implementing",
        "is using utilizes": "utilizes",
        "implements implements": "implements",
        "leverage leverage": "leverage",
        "develop develop": "develop",
        "implement implement": "implement",
        "create create": "create",
        "establish establish": "establish",
    }
    
    # Apply direct replacements
    for bad_phrase, good_phrase in direct_replacements.items():
        text = text.replace(bad_phrase, good_phrase)
    
    # Step 5: Fix capitalization issues
    # -------------------------------
    
    # Fix words with first letter capitalized followed by the same word lowercase
    pattern_capital = r'\b([A-Z][a-z]+)\s+([a-z]+)\b'
    matches = list(re.finditer(pattern_capital, text))
    for match in reversed(matches):  # Process in reverse to maintain correct indices
        if match.group(1).lower() == match.group(2).lower():
            start, end = match.span()
            text = text[:start] + match.group(1) + text[end:]
    
    # Fix "Company is using Utilizes" pattern
    text = re.sub(r'([A-Za-z\s]+) is using ([A-Z][a-z]+)', r'\1 utilizes', text)
    
    # Step 6: Fix punctuation and spacing issues
    # ----------------------------------------
    
    # Fix double punctuation
    text = re.sub(r'\.\.+', '.', text)
    text = re.sub(r',,+', ',', text)
    text = re.sub(r'!!+', '!', text)
    text = re.sub(r'\?\?+', '?', text)
    
    # Fix spaces before punctuation
    text = re.sub(r'\s+\.', '.', text)
    text = re.sub(r'\s+,', ',', text)
    text = re.sub(r'\s+!', '!', text)
    text = re.sub(r'\s+\?', '?', text)
    text = re.sub(r'\s+:', ':', text)
    text = re.sub(r'\s+;', ';', text)
    
    # Fix double periods after sentences
    text = re.sub(r'\.\s+\.', '.', text)
    
    # Fix incorrect capitalization after periods
    def capitalize_after_period(match):
        return match.group(1) + match.group(2).upper() + match.group(3)
    
    text = re.sub(r'(\.\s+)([a-z])(\w*)', capitalize_after_period, text)
    
    # Step 7: Final cleanup and normalization
    # -------------------------------------
    
    # Fix double spaces (again, after all the replacements)
    text = re.sub(r'\s+', ' ', text)
    
    # Fix spaces at beginning and end
    text = text.strip()
    
    # Ensure the text ends with proper punctuation
    if text and text[-1] not in '.!?':
        text += '.'
    
    return text


def ensure_valid_url_in_sites(site_data):
    """
    Ensures all site data has valid URLs or replaces missing URLs with empty strings.
    
    Args:
        site_data (list): List of site data dictionaries
        
    Returns:
        list: List of site data with validated URLs
    """
    if not site_data:
        return []
        
    result = []
    for site in site_data:
        site_copy = site.copy()
        if 'url' not in site_copy or not site_copy['url']:
            site_copy['url'] = ""
        result.append(site_copy)
    return result

def generate_deep_insights(brief_text, ari_scores):
    """
    Generate deeper AI-powered insights based on the brief text and ARI scores.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        ari_scores (dict): The Audience Resonance Index scores
        
    Returns:
        dict: A dictionary containing AI-generated insights
    """
    if not brief_text or len(brief_text) < 100:
        return {"error": "Brief text too short to analyze."}
    
    # Format the scores for inclusion in the prompt
    scores_str = "\n".join([f"- {metric}: {score}/10" for metric, score in ari_scores.items()])
    
    # Create a list of the weakest areas as improvement priorities
    improvement_areas = []
    for metric, score in ari_scores.items():
        if score < 6:  # Consider scores below 6 as needing improvement
            improvement_areas.append(metric)
    
    # Dynamically determine priority metrics based on the brief content
    priority_metrics = []
    
    # Check for diversity, inclusion, and equity themes
    equity_keywords = ["diverse", "diversity", "minority", "inclusive", "inclusion", "equity", "equality"]
    if any(keyword in brief_text.lower() for keyword in equity_keywords):
        priority_metrics.append("Media Ownership Equity")
    
    # Check for location and cultural references
    geo_keywords = ["local", "regional", "city", "area", "community", "geographic", "location", "region"]
    if any(keyword in brief_text.lower() for keyword in geo_keywords):
        priority_metrics.append("Geo-Cultural Fit")
    
    # Check for representation and demographic themes
    rep_keywords = ["represent", "authentic", "demographic", "audience", "identity", "depiction"]
    if any(keyword in brief_text.lower() for keyword in rep_keywords):
        priority_metrics.append("Representation")
    
    # Check for content engagement themes
    content_keywords = ["content", "creative", "story", "narrative", "messaging", "engagement"]
    if any(keyword in brief_text.lower() for keyword in content_keywords):
        priority_metrics.append("Content Engagement")
    
    # Check for multi-platform themes
    platform_keywords = ["platform", "channel", "multi-channel", "omnichannel", "device", "mobile", "digital"]
    if any(keyword in brief_text.lower() for keyword in platform_keywords):
        priority_metrics.append("Platform Diversity")
        
    # If we still need metrics to reach 3, add some fallbacks that are common improvement areas
    fallback_metrics = ["Media Ownership Equity", "Geo-Cultural Fit", "Representation", 
                        "Platform Diversity", "Content Engagement", "Community Connection"]
    
    # Ensure we don't duplicate metrics already in the improvement_areas
    remaining_fallbacks = [m for m in fallback_metrics if m not in improvement_areas and m not in priority_metrics]
    
    # Add prioritized metrics first
    for metric in priority_metrics:
        if metric not in improvement_areas and len(improvement_areas) < 3:
            improvement_areas.append(metric)
            
    # Then add fallbacks if needed
    for metric in remaining_fallbacks:
        if len(improvement_areas) < 3:
            improvement_areas.append(metric)
    
    # If we still don't have 3, add other metrics with the lowest scores
    if len(improvement_areas) < 3:
        remaining_metrics = [m for m in ari_scores.keys() if m not in improvement_areas]
        remaining_metrics.sort(key=lambda m: ari_scores[m])
        improvement_areas.extend(remaining_metrics[:3-len(improvement_areas)])
    
    # Limit to 3 improvement areas
    improvement_areas = improvement_areas[:3]
    improvement_areas_str = ", ".join(improvement_areas)
    
    # Check if this is the SiteOne Hispanic campaign
    is_siteone_hispanic = False
    audience_data_str = ""
    
    if "SiteOne" in brief_text and ("Hispanic" in brief_text or "Spanish" in brief_text):
        is_siteone_hispanic = True
        audience_data_str = """
Additional audience data for SiteOne Hispanic campaign:
- Demographics: 93% male, 39% ages 25-34, 33% income $25-50k, 42% high school degree
- Values: Maintaining traditions (161), Acquiring wealth (143), Being humble (142)
- Psychological Drivers: Exciting life (204), Social/professional status (166) 
- Hobbies: Soccer (419), Gambling on sports (265), Basketball (249)
- Media: Univision (1357), NFL Network (295), Comedy Central (282)
- Streaming: Disney+ without ads (184), Netflix without ads (164)
- Devices: Mobile phone (313), Smart TV (211)
- Social Media: Twitch (208), Discord (178), TikTok (146), Reddit (140)
- Magazines: Men's Health (562), Sports Illustrated (455)
"""
    
    try:
        # Extract brand name, industry, and product for context-specific insights
        from core.analysis import extract_brand_info
        brand_name, industry, product_type = extract_brand_info(brief_text)
        
        # Craft an enhanced prompt for the OpenAI API with stronger brief-specific guidance
        prompt = f"""
        You are an expert marketing strategist and cultural analyst specializing in audience resonance.
        
        Analyze the following marketing brief or RFP and the corresponding Audience Resonance Index (ARI) scores.
        Provide deep insights that could help improve the campaign's effectiveness.
        
        Brief/RFP:
        {brief_text[:4000]}  # Limiting to 4000 chars to avoid token limits
        
        ARI Scores:
        {scores_str}
        
        {audience_data_str if is_siteone_hispanic else ""}
        
        Brand: {brand_name}
        Industry: {industry}
        Product/Service: {product_type}
        
        Focus specifically on these priority improvement areas: {improvement_areas_str}
        
        Please provide the following insights in JSON format with a light, approachable tone:
        1. Three specific areas of strength and why they are strong in digital advertising context
        2. Three specific areas for improvement with TACTICAL digital advertising recommendations (MUST focus on the priority areas listed above)
        3. Three cultural trends this campaign could leverage through digital ad targeting and platforms
        4. One key audience insight for digital media buying that might be overlooked
        5. One prediction about campaign performance metrics
        6. Detailed analysis for EVERY ARI metric that specifically references ACTUAL CONTENT from the brief
        
        For the metric details section, you MUST:
        - Directly reference specific phrases, statistics, audience details, or tactics mentioned in the brief
        - Explain how specific elements in the brief affected each metric score
        - Include brief quotes or paraphrases from the actual brief for each metric
        - Connect the metric scores to specific targeting approaches mentioned in the brief
        - Refer to specific audience segments, channels, or creative approaches mentioned in the brief
        - DO NOT use generic descriptions - ONLY use content that appears in this specific brief
        
        For the improvement recommendations, focus specifically on digital advertising tactics including:
        - Media mix allocation percentages
        - Platform-specific targeting parameters
        - Bidding strategies and KPI targets
        - Programmatic optimization techniques
        - Audience segmentation for ad platforms
        - Clear measurement metrics and benchmarks
        
        Use accessible language that any marketing professional would understand. Avoid overly technical jargon while still being specific and actionable.
        
        Format the response as a valid JSON object with these keys:
        - strengths: array of objects with 'area' and 'explanation'
        - improvements: array of objects with 'area', 'explanation', and 'recommendation'
        - trends: array of objects with 'trend' and 'application'
        - hidden_insight: string
        - performance_prediction: string
        - metric_details: object with each ARI metric as a key and a specific analysis as value
        """
        
        # Call the OpenAI API with enhanced system prompt
        system_prompt = """
        You are a digital advertising tactician with expertise in programmatic media buying, platform-specific optimization, 
        and culturally-relevant campaign execution. Focus on actionable tactics, not general strategy.
        
        EXTREMELY IMPORTANT: When analyzing metrics, you MUST reference SPECIFIC content from the brief.
        Do not use generic descriptions. Each metric analysis should directly quote or mention specific elements 
        from the brief text. This is not optional - your response will be rejected if it contains generic 
        descriptions that don't reference actual content from the brief.
        """
        
        # Use the improved API call with retry logic
        result = make_openai_request(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o",
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000,
            max_retries=3
        )
        
        # Check if the request failed
        if result is None:
            print("Failed to get response from OpenAI after all retries")
            return {"error": "Unable to generate insights after multiple attempts"}
        
        # Debug the response
        print("================================")
        print("===== OPENAI API RESPONSE =====")
        print(json.dumps(result, indent=2))
        print("================================")
        
        # The result is already parsed JSON
        insights = result
        
        # Clean up grammar and duplicate words in the insights
        if 'strengths' in insights:
            for strength in insights['strengths']:
                if 'explanation' in strength:
                    strength['explanation'] = fix_grammar_and_duplicates(strength['explanation'])
        
        if 'improvements' in insights:
            for improvement in insights['improvements']:
                if 'explanation' in improvement:
                    improvement['explanation'] = fix_grammar_and_duplicates(improvement['explanation'])
                if 'recommendation' in improvement:
                    improvement['recommendation'] = fix_grammar_and_duplicates(improvement['recommendation'])
        
        if 'trends' in insights:
            for trend in insights['trends']:
                if 'application' in trend:
                    trend['application'] = fix_grammar_and_duplicates(trend['application'])
        
        if 'hidden_insight' in insights:
            insights['hidden_insight'] = fix_grammar_and_duplicates(insights['hidden_insight'])
            
        if 'performance_prediction' in insights:
            insights['performance_prediction'] = fix_grammar_and_duplicates(insights['performance_prediction'])
            
        # Ensure we have metric_details for all metrics
        if 'metric_details' not in insights:
            insights['metric_details'] = {}
            
        # Ensure all metrics have details and clean them
        for metric in ari_scores.keys():
            if metric in insights.get('metric_details', {}):
                insights['metric_details'][metric] = fix_grammar_and_duplicates(insights['metric_details'][metric])
            else:
                # If a metric is missing details, add a placeholder that prompts for a brief upload
                insights['metric_details'][metric] = f"Upload a brief to get specific {metric} analysis for your campaign."
                
        # Debug the parsed insights
        print("================================")
        print("===== PARSED INSIGHTS =====")
        print(f"Got {len(insights.get('strengths', []))} strengths")
        print(f"Got {len(insights.get('improvements', []))} improvements")
        print(f"Has hidden insight: {bool(insights.get('hidden_insight'))}")
        print(f"Has performance prediction: {bool(insights.get('performance_prediction'))}")
        print("============================")
        
        return insights
        
    except Exception as e:
        print(f"Error generating AI insights: {str(e)}")
        # Return a minimal error response
        return {"error": f"Unable to generate insights: {str(e)}"}

def generate_competitor_analysis(brief_text, industry=None):
    """
    Generate a competitive analysis based on the brief text and industry.
    
    This function also sanitizes and formats the output to ensure no grammatical errors,
    duplicate phrases like "Implement Implement" or "Leverage Leverage", and ensures
    text flows naturally without repetition.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        industry (str, optional): The industry classification
        
    Returns:
        dict: A dictionary containing competitor analysis with sanitized text
    """
    try:
        # Check if this is the SiteOne Hispanic campaign
        is_siteone_hispanic = False
        audience_data_str = ""
        
        if "SiteOne" in brief_text and ("Hispanic" in brief_text or "Spanish" in brief_text):
            is_siteone_hispanic = True
            audience_data_str = """
Additional audience data for SiteOne Hispanic campaign:
- Demographics: 93% male, 39% ages 25-34, 33% income $25-50k, 42% high school degree
- Values: Maintaining traditions (161), Acquiring wealth (143), Being humble (142)
- Psychological Drivers: Exciting life (204), Social/professional status (166) 
- Hobbies: Soccer (419), Gambling on sports (265), Basketball (249)
- Media: Univision (1357), NFL Network (295), Comedy Central (282)
- Streaming: Disney+ without ads (184), Netflix without ads (164)
- Devices: Mobile phone (313), Smart TV (211)
- Social Media: Twitch (208), Discord (178), TikTok (146), Reddit (140)
- Magazines: Men's Health (562), Sports Illustrated (455)
"""
            
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
        
        {audience_data_str if is_siteone_hispanic else ""}
        
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
        
        # Use the improved API call with retry logic
        result = make_openai_request(
            messages=[
                {"role": "system", "content": "You are a digital media competitive intelligence expert specialized in advertising platform strategies, audience targeting, and media buying optimization."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o",
            response_format={"type": "json_object"},
            max_tokens=1200,
            max_retries=3
        )
        
        # Check if the request failed
        if result is None:
            raise Exception("Failed to get response from OpenAI after all retries")
        
        # The result is already parsed JSON
        analysis = result
        
        # Clean up grammar and duplicate words in the analysis
        if 'competitors' in analysis:
            for comp in analysis['competitors']:
                if 'digital_tactics' in comp:
                    comp['digital_tactics'] = fix_grammar_and_duplicates(comp['digital_tactics'])
        
        if 'advantages' in analysis:
            for adv in analysis['advantages']:
                if 'tactical_application' in adv:
                    adv['tactical_application'] = fix_grammar_and_duplicates(adv['tactical_application'])
        
        if 'threats' in analysis:
            for threat in analysis['threats']:
                if 'tactical_response' in threat:
                    threat['tactical_response'] = fix_grammar_and_duplicates(threat['tactical_response'])
        
        if 'differentiation' in analysis:
            for diff in analysis['differentiation']:
                if 'tactical_approach' in diff:
                    diff['tactical_approach'] = fix_grammar_and_duplicates(diff['tactical_approach'])
        
        return analysis
        
    except Exception as e:
        # If there's an error, check if it's a SiteOne Hispanic campaign and return tailored fallback data
        is_siteone_targeting_hispanic = "SiteOne" in brief_text and ("Hispanic" in brief_text or "Spanish" in brief_text)
        
        if is_siteone_targeting_hispanic:
            return {
                "error": str(e),
                "competitors": [
                    {"name": "Lowe's Garden Center", "threat_level": "high", "digital_tactics": "Heavy investment in Spanish-language search campaigns and aggressive geo-targeted mobile ads targeting Hispanic neighborhoods with landscape service promotions."},
                    {"name": "Home Depot Pro", "threat_level": "medium", "digital_tactics": "Sports-focused Spanish language video content strategy with strong presence on streaming platforms popular with Hispanic audiences."},
                    {"name": "Regional Landscape Suppliers", "threat_level": "medium", "digital_tactics": "Community-based marketing and local Spanish radio integrations with digital companion campaigns."}
                ],
                "advantages": [
                    {"advantage": "Hispanic Audience Data Insights", "tactical_application": "Apply custom audience targeting focused on 25-34 year old Hispanic males with interest in soccer and sports betting, with 25% higher bid adjustments on Spanish-language mobile inventory."},
                    {"advantage": "Value-Based Messaging Alignment", "tactical_application": "Implement sequential messaging that emphasizes tradition maintenance and professional status growth with Spanish-language creative variations."}
                ],
                "threats": [
                    {"threat": "Spanish-Language Content Competition", "tactical_response": "Develop high-quality Spanish language assets featuring authentic cultural elements, and allocate 35% of budget to these placements with performance-based optimization."},
                    {"threat": "Mobile App Competition for Hispanic Users", "tactical_response": "Focus on high-performance mobile placements with sports content adjacencies using Spanish language interfaces."}
                ],
                "differentiation": [
                    {"platform": "Mobile Video", "tactical_approach": "Create mobile-first vertical video assets in Spanish featuring landscape professionals succeeding on job sites, with specific product placements. Use VCR (Video Completion Rate) of 70-90% as the benchmark for performance."},
                    {"platform": "Audio Streaming", "tactical_approach": "Develop Spanish-language audio ads targeting listeners of sports content and traditional music genres with mobile companion banners."}
                ]
            }
        else:
            # Default fallback
            return {
                "error": str(e),
                "competitors": [
                    {"name": "Major Industry Player", "threat_level": "high", "digital_tactics": "Heavy investment in programmatic display with high-frequency retargeting and aggressive conquest campaigns targeting competitor brand terms."},
                    {"name": "Emerging Disruptor", "threat_level": "medium", "digital_tactics": "Video content strategy with creator partnerships and high organic content amplification through paid boosting."},
                    {"name": "Legacy Brand", "threat_level": "low", "digital_tactics": "Traditional search and display mix with limited digital presence, primarily focused on brand protection keywords."}
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

def get_default_audience_segments(brief_text, ari_scores):
    """
    Generate default audience segments when AI generation is unavailable.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        ari_scores (dict): The Audience Resonance Index scores
        
    Returns:
        dict: A dictionary containing default audience segments
    """
    # Extract brand/industry information for more relevant defaults
    from core.analysis import extract_brand_info
    brand_name, industry, product_type = extract_brand_info(brief_text)
    
    # Check if this is an Apple TV+ campaign first
    if "Apple TV+" in brief_text or "Apple TV Plus" in brief_text:
        # Use Apple TV+ specific audience data
        import streamlit as st
        
        # If we have Apple audience data in session state, use it directly
        if 'audience_data' in st.session_state and st.session_state.audience_data is not None:
            apple_data = st.session_state.audience_data
            all_segments = []
            
            # Add primary segments
            if 'primary' in apple_data:
                all_segments.extend(apple_data['primary'])
                
            # Add secondary segments
            if 'secondary' in apple_data:
                all_segments.extend(apple_data['secondary'])
                
            # Add growth segments
            if 'growth' in apple_data:
                all_segments.extend(apple_data['growth'])
            
            # If we have segments, return them in the expected format
            if all_segments:
                return {"segments": all_segments}
            
        # If we don't have the audience_data in session_state, try to load it directly
        try:
            from core.audience.apple_audience_data import get_apple_audience_data
            apple_data = get_apple_audience_data()
            all_segments = []
            
            # Add primary segments
            if 'primary' in apple_data:
                all_segments.extend(apple_data['primary'])
                
            # Add secondary segments
            if 'secondary' in apple_data:
                all_segments.extend(apple_data['secondary'])
                
            # Add growth segments
            if 'growth' in apple_data:
                all_segments.extend(apple_data['growth'])
            
            # Save the original apple_data to session_state if not already there
            # This is important so we can access the emerging audience separately
            import streamlit as st
            if 'audience_data' not in st.session_state or st.session_state.audience_data is None:
                st.session_state.audience_data = apple_data
                
            # Add emerging audience as a separate segment if available
            # This will make it distinct from the growth segments
            if 'emerging' in apple_data:
                # Add emerging audience to the segment list
                all_segments.append(apple_data['emerging'])
            
            # If we have segments, return them in the expected format
            if all_segments:
                return {"segments": all_segments}
        except:
            # Fall back to the default segments if Apple data loading fails
            pass
    
    # Default segments structure matching the required image format
    segments = {
        "segments": [
            # Primary audience segment
            {
                "name": "Tech-Savvy Streamers",
                "description": "Age: 25-45 | Gender: All | Income: Mid to High",
                "interest_categories": ["Technology Enthusiasts", "Early Adopters", "Streaming Services", "Digital Entertainment"],
                "targeting_params": {
                    "age_range": "25-45",
                    "gender_targeting": "All",
                    "income_targeting": "Mid to High"
                },
                "platform_targeting": [
                    {
                        "platform": "OTT/CTV",
                        "targeting_approach": "Technology focused content and premium streaming environments"
                    }
                ],
                "expected_performance": {
                    "CTR": "90-100%",  # For OTT/CTV platforms, this becomes VCR (video completion rate)
                    "engagement_rate": "5.2%"
                },
                "bidding_strategy": {
                    "bid_adjustments": "Higher bids for premium content",
                    "dayparting": "Evenings and weekends"
                }
            },
            # Secondary audience segment - Lifestyle & Culture Enthusiasts
            {
                "name": "Lifestyle & Culture Enthusiasts",
                "description": "Age: 30-50 | Gender: All | Income: Mid to High",
                "interest_categories": ["Culture & Arts", "Lifestyle", "TV Shows & Movies", "Digital Subscriptions"],
                "targeting_params": {
                    "age_range": "30-50",
                    "gender_targeting": "All",
                    "income_targeting": "Mid to High"
                },
                "platform_targeting": [
                    {
                        "platform": "Desktop and Tablet Display",
                        "targeting_approach": "Premium lifestyle content and entertainment environments"
                    }
                ],
                "expected_performance": {
                    "CTR": "80-90%",  # For audio platforms, this becomes LTR (listen-through rate)
                    "engagement_rate": "4.8%"
                },
                "bidding_strategy": {
                    "bid_adjustments": "Content category optimization",
                    "dayparting": "Peak entertainment hours"
                }
            }
        ]
    }
    
    # Don't customize based on industry - use the consistent Gen Z Hoops Fanatics and Multi-Platform Sports Enthusiasts 
    # to match our audience card titles across the application
    
    # Modify interests based on brief content keywords
    brief_lower = brief_text.lower()
    if "luxury" in brief_lower or "premium" in brief_lower:
        segments["segments"][0]["interest_categories"].append("Luxury Lifestyle")
        segments["segments"][1]["interest_categories"].append("Premium Brands")
    if "sustainable" in brief_lower or "eco" in brief_lower:
        segments["segments"][0]["interest_categories"].append("Sustainability")
        segments["segments"][1]["interest_categories"].append("Eco-Friendly Products")
    
    return segments

def generate_audience_segments(brief_text, ari_scores, demographics_info=None):
    """
    Generate audience segment recommendations based on the brief text and ARI scores.
    Including new potential audience segments with high growth potential that might not be 
    currently addressed in the brief.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        ari_scores (dict): The Audience Resonance Index scores
        demographics_info (str, optional): Demographic configuration from psychographic input
        
    Returns:
        dict: A dictionary containing audience segments with descriptions and affinities
    """
    try:
        # Check if this is the SiteOne Hispanic campaign
        is_siteone_hispanic = False
        audience_data_str = ""
        
        if "SiteOne" in brief_text and ("Hispanic" in brief_text or "Spanish" in brief_text):
            is_siteone_hispanic = True
            audience_data_str = """
Additional audience data for SiteOne Hispanic campaign:
- Demographics: 93% male, 39% ages 25-34, 33% income $25-50k, 42% high school degree
- Values: Maintaining traditions (161), Acquiring wealth (143), Being humble (142)
- Psychological Drivers: Exciting life (204), Social/professional status (166) 
- Hobbies: Soccer (419), Gambling on sports (265), Basketball (249)
- Media: Univision (1357), NFL Network (295), Comedy Central (282)
- Streaming: Disney+ without ads (184), Netflix without ads (164)
- Devices: Mobile phone (313), Smart TV (211)
- Social Media: Twitch (208), Discord (178), TikTok (146), Reddit (140)
- Magazines: Men's Health (562), Sports Illustrated (455)
"""
            
        # Format the scores for inclusion in the prompt
        scores_str = "\n".join([f"- {metric}: {score}/10" for metric, score in ari_scores.items()])
        
        # Craft a prompt for the OpenAI API
        prompt = f"""
        You are a digital media buying and audience segmentation expert specializing in omnichannel advertising platforms.
        
        Based on the following marketing campaign information and Audience Resonance Index scores,
        identify 3 key audience segments for targeted omnichannel digital advertising with specific platform targeting parameters.
        
        IMPORTANT GUIDELINES:
        1. Focus on OMNICHANNEL digital advertising solutions - including display, video, CTV/OTT, audio, rich media, high impact, 
           interactive, programmatic digital out-of-home (DOOH), etc.
        2. DO NOT focus on search or social media campaigns, which typically have higher CTRs than other digital channels
        3. CTR estimates should reflect realistic omnichannel expectations
        4. Make sure the LAST segment is a high-growth potential audience that might not be explicitly mentioned 
           in the brief but would be valuable to target based on adjacent interests, behaviors, or demographic extensions.
           This should be a growth opportunity audience that the campaign isn't currently addressing.
        
        Campaign Information:
        {brief_text[:3000]}  # Limiting to 3000 chars to avoid token limits
        
        {f"Target Demographics: {demographics_info}" if demographics_info else ""}
        
        ARI Scores:
        {scores_str}
        
        {audience_data_str if is_siteone_hispanic else ""}
        
        For each segment, provide detailed targeting specifications for digital advertising platforms:
        1. A descriptive segment name for use in ad platforms
        2. Precise demographic targeting parameters (age ranges, gender, income brackets, etc.)
        3. Digital platform interest categories and behavior targeting options
        4. Platform-specific targeting recommendations (use generic platform types, not brand names)
        5. Key performance indicators and benchmark rates to expect for omnichannel campaigns
           - For display formats: Use CTR of 0.05-0.7%
           - For video formats: Use VCR (Video Completion Rate) of 70-90% instead of CTR
           - For CTV/OTT formats: Use VCR (Video Completion Rate) of 90-100% instead of CTR
           - For audio formats: Use LTR (Listen-Through Rate) of 80-90% instead of CTR
        6. Specific media buying tactics for this segment (bid adjustments, dayparting, etc.)
        7. For the following platform_targeting.platform set CTR accordingly:
            - If the platform is Video, set CTR to 70-90%.
            - If the platform is CTV/OTT, set CTR to 90-100%.
        
        Format the response as a valid JSON array with objects containing:
        - name: string (descriptive segment name)
        - targeting_params: object with age_range, gender_targeting, income_targeting, education_targeting, and location_targeting
        - interest_categories: array of strings (specific interests to target in ad platforms)
        - platform_targeting: array of objects with 'platform' and 'targeting_approach' 
        - expected_performance: object with CTR (click-through rate or video completion rate for video content), CPA (cost per acquisition), and engagement_rate
        - bidding_strategy: object with bid_adjustments, dayparting, and placement_priorities
        - rationale: string with a brief rationale for why it recommends the specific emerging audience, only populate it for emerging audience, max 400 letters. Don't mention that it's not being explicitly targeted.
        
        Remember, make the THIRD segment a high-potential growth audience that is not currently being addressed 
        in the campaign brief but shows strong potential based on trends, adjacent interests, and market opportunities. It should not be the same as the FIRST or SECOND segment.
        """
        
        # Use the improved API call with retry logic
        result = make_openai_request(
            messages=[
                {"role": "system", "content": "You are a digital advertising audience specialist with expertise in platform-specific targeting parameters, lookalike modeling, and programmatic audience segmentation."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o",
            response_format={"type": "json_object"},
            max_tokens=1500,
            max_retries=3
        )
        
        # Check if the request failed
        if result is None:
            raise Exception("Failed to get response from OpenAI after all retries")
        
        # The result is already parsed JSON
        segments = result
        
        # Clean up grammar and duplicate words in the segments
        if 'segments' in segments:
            for segment in segments['segments']:
                # Clean platform targeting approaches
                if 'platform_targeting' in segment:
                    for platform in segment['platform_targeting']:
                        if 'targeting_approach' in platform:
                            platform['targeting_approach'] = fix_grammar_and_duplicates(platform['targeting_approach'])
                
                # Clean bidding strategy
                if 'bidding_strategy' in segment:
                    for key in segment['bidding_strategy']:
                        if isinstance(segment['bidding_strategy'][key], str):
                            segment['bidding_strategy'][key] = fix_grammar_and_duplicates(segment['bidding_strategy'][key])
        
        return segments
        
    except Exception as e:
        print(f"Error generating audience segments: {str(e)}")
        # If there's an error, check if it's a SiteOne Hispanic campaign and return tailored fallback data
        is_siteone_targeting_hispanic = "SiteOne" in brief_text and ("Hispanic" in brief_text or "Spanish" in brief_text)
        
        if is_siteone_targeting_hispanic:
            return {
                "error": str(e),
                "segments": [
                    {
                        "name": "Hispanic Landscape Professionals",
                        "targeting_params": {
                            "age_range": "25-34",
                            "gender_targeting": "Male dominant (93%)",
                            "income_targeting": "$25K-50K annually",
                            "education_targeting": "High school degree (42%)",
                            "location_targeting": "High-density Hispanic neighborhoods with suburban landscape markets"
                        },
                        "interest_categories": [
                            "Soccer enthusiasts", 
                            "Sports betting", 
                            "Basketball fans",
                            "Family-oriented activities"
                        ],
                        "platform_targeting": [
                            {"platform": "Spanish Media Networks", "targeting_approach": "Target viewers of sports programming on Spanish-language networks with companion display ads"},
                            {"platform": "Mobile Gaming", "targeting_approach": "Reach users on mobile devices through sports apps and games with Spanish language options"}
                        ],
                        "expected_performance": {
                            "CTR": "0.3-0.7%",  # For display; would be 70-90% for video formats
                            "CPA": "20-25% below account average for Spanish creative", 
                            "engagement_rate": "3.5-4.2%"
                        },
                        "bidding_strategy": {
                            "bid_adjustments": "+25% for mobile devices, +15% for Spanish language content",
                            "dayparting": "Increase bids 20% during 6-9pm local time when sports viewing peaks",
                            "placement_priorities": "In-stream video prioritized over display, 60/40 budget split"
                        }
                    }
                ]
            }
        else:
            # Default fallback
            return {
                "error": str(e),
                "segments": [
                    {
                        "name": "Gen Z Hoops Fanatics",
                        "targeting_params": {
                            "age_range": "18-24",
                            "gender_targeting": "All",
                            "income_targeting": "Below $50k",
                            "education_targeting": "High school or some college",
                            "location_targeting": "Urban centers and college towns"
                        },
                    "interest_categories": [
                        "Basketball Enthusiasts", 
                        "Sports Apparel", 
                        "Sneakerheads",
                        "Live Sports Events"
                    ],
                    "platform_targeting": [
                        {"platform": "Programmatic Video Platforms", "targeting_approach": "Target basketball content viewers across premium video platforms with sports content adjacency and interactive video formats"},
                        {"platform": "Sports Streaming Services", "targeting_approach": "Focus on live game audiences and pre/post-game content with high-impact ad placements"}
                    ],
                    "expected_performance": {
                        "CTR": "70-90%",  # For video platforms, this becomes VCR (video completion rate)
                        "CPA": "15-20% below account average", 
                        "engagement_rate": "4.5-5.2%"
                    },
                    "bidding_strategy": {
                        "bid_adjustments": "+25% during game days, +15% for mobile devices",
                        "dayparting": "Increase bids 30% during prime-time game hours (7-11pm)",
                        "placement_priorities": "Pre-roll video prioritized over mid-roll, 60/40 budget split"
                    }
                }
            ]
        }


def generate_audience_summary(brief_text, ari_scores, primary_segment, secondary_segment, psychographic_highglights):
    """
    Generate a summary of audience segments based on the brief text and ARI scores.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        ari_scores (dict): The Audience Resonance Index scores
        primary_segment (dict): The primary audience segment
        secondary_segment (dict): The secondary audience segment
        psychographic_highglights (string): Psychographic highlights text
        
    Returns:
        dict: A dictionary containing the audience summary
    """
    try:
        # Format the scores for inclusion in the prompt
        scores_str = "\n".join([f"- {metric}: {score}/10" for metric, score in ari_scores.items()])
        
        # Craft a prompt for the OpenAI API
        prompt = f"""
        You are a digital media buying and audience segmentation expert specializing in omnichannel advertising platforms.
        
        Based on the following marketing campaign information and Audience Resonance Index scores,
        summarize the key audience segments for targeted omnichannel digital advertising.
        
        Campaign Information:
        {brief_text[:3000]}  # Limiting to 3000 chars to avoid token limits
        
        ARI Scores:
        {scores_str}
        
        Primary Segment:
        {primary_segment}
        
        Secondary Segment:
        {secondary_segment}
        
        Psychographic Highlights:
        {psychographic_highglights}
        
        Please provide a summary of the audience segments, including:
        1. Key characteristics of each segment
        2. Targeting recommendations for digital advertising platforms
        3. Expected performance metrics and benchmarks
        4. Psychographic insights that can be leveraged in messaging and creative development
        
        Format the response as a valid JSON object with keys:
        - summary: string (summary of audience segments)
        """
        
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
        
        # Parse the 
        summary = json.loads(response.choices[0].message.content)
        # Clean up grammar and duplicate words in the summary
        if 'summary' in summary:
            summary['summary'] = fix_grammar_and_duplicates(summary['summary'])
        return summary
    except Exception as e:
        # If there's an error, return a default summary
        return {
            "error": str(e),
            "summary": {
                "key_characteristics": "Unable to generate summary due to error.",
                "targeting_recommendations": "Unable to generate targeting recommendations due to error.",
                "expected_performance_metrics": "Unable to generate performance metrics due to error.",
                "psychographic_insights": "Unable to generate psychographic insights due to error."
            }
        }


def generate_competitor_strategy(brief_text, competitor_brand, campaign_goal):
    """
    Generate a custom strategy to counter a specific competitor brand based on campaign goals.
    
    Args:
        brief_text (str): The marketing brief or RFP text for context
        competitor_brand (str): The name of the competitor brand
        campaign_goal (str): The description of the campaign goals
        
    Returns:
        list: A list of strategic recommendations to counter the competitor
    """
    try:
        import os
        from openai import OpenAI
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        
        # If there's no API key, return a default response
        if not os.environ.get("OPENAI_API_KEY"):
            # Return a default list of strategies
            return [
                f"Capitalize on Cultural Moments: Unlike {competitor_brand}'s mass approach, build engagement through culturally relevant events, holidays, and seasonal activations using tailored creative.",
                f"Highlight Specialization: Position the campaign around specific expertise or product benefits that contrast {competitor_brand}'s broad and general messaging.",
                f"Leverage Authentic Storytelling: Use community voices, user-generated content, or influencer partnerships to add credibility—areas where {competitor_brand} may rely on traditional ads.",
                f"Enhance Local Relevance: Create geo-targeted or bilingual messaging that speaks directly to underserved or high-potential regions where {competitor_brand} underdelivers.",
                f"Activate Emerging Platforms: Extend the campaign to newer or underutilized platforms where {competitor_brand} has little presence."
            ]
        
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Prepare a prompt that includes context from the brief, competitor, and campaign goal
        prompt = f"""
        I need to create a digital advertising strategy that will effectively counter our competitor, {competitor_brand}.
        
        Campaign Goal: {campaign_goal}
        
        Additional context from our marketing brief:
        {brief_text[:2000]}  # Limit brief text to reasonable length
        
        Please provide 5 specific strategic recommendations that will help us differentiate and outperform {competitor_brand}.
        Each recommendation should:
        1. Start with a clear tactical approach (2-4 words)
        2. Explain how it contrasts with {competitor_brand}'s approach
        3. Be specific to digital advertising tactics
        4. Be actionable and measurable
        5. IMPORTANT: Do not mention specific publisher names, social platforms, or network names. 
           Instead use generic terms like "audio platforms", "rich media formats", "high impact placements", "interactive video", etc.
        
        Format each recommendation as a single paragraph. Begin each recommendation with a bold header.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )
        
        # Extract the recommendations from the response
        raw_text = response.choices[0].message.content
        
        # Preprocess the text to identify recommendation paragraphs
        lines = raw_text.split('\n')
        recommendations = []
        current_rec = ""
        
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '**', '- ')):
                if current_rec:  # If we have a recommendation in progress
                    recommendations.append(fix_grammar_and_duplicates(current_rec))
                    current_rec = ""
                current_rec = line.strip().lstrip('123456789.- *').strip()
            elif line.strip() and current_rec:  # If this is content for the current recommendation
                current_rec += " " + line.strip()
        
        # Add the last recommendation
        if current_rec:
            recommendations.append(fix_grammar_and_duplicates(current_rec))
        
        # If no recommendations were found, format the entire response
        if not recommendations:
            paragraphs = [p for p in raw_text.split('\n\n') if p.strip()]
            recommendations = [fix_grammar_and_duplicates(p) for p in paragraphs[:5]]
        
        # Ensure we return at most 5 recommendations
        recommendations = recommendations[:5]
        
        # Ensure we have at least 5 recommendations
        if len(recommendations) < 5:
            default_recs = [
                f"Capitalize on Cultural Moments: Unlike {competitor_brand}'s mass approach, build engagement through culturally relevant events, holidays, and seasonal activations using tailored creative.",
                f"Highlight Specialization: Position the campaign around specific expertise or product benefits that contrast {competitor_brand}'s broad and general messaging.",
                f"Leverage Authentic Storytelling: Use community voices, user-generated content, or influencer partnerships to add credibility—areas where {competitor_brand} may rely on traditional ads.",
                f"Enhance Local Relevance: Create geo-targeted or bilingual messaging that speaks directly to underserved or high-potential regions where {competitor_brand} underdelivers.",
                f"Activate Emerging Platforms: Extend the campaign to newer or underutilized platforms where {competitor_brand} has little presence."
            ]
            recommendations.extend(default_recs[len(recommendations):])
        
        return recommendations
    
    except Exception as e:
        print(f"Error generating competitor strategy: {str(e)}")
        # Return a default list of strategies
        return [
            f"Capitalize on Cultural Moments: Unlike {competitor_brand}'s mass approach, build engagement through culturally relevant events, holidays, and seasonal activations using tailored creative.",
            f"Highlight Specialization: Position the campaign around specific expertise or product benefits that contrast {competitor_brand}'s broad and general messaging.",
            f"Leverage Authentic Storytelling: Use community voices, user-generated content, or influencer partnerships to add credibility—areas where {competitor_brand} may rely on traditional ads.",
            f"Enhance Local Relevance: Create geo-targeted or bilingual messaging that speaks directly to underserved or high-potential regions where {competitor_brand} underdelivers.",
            f"Activate Emerging Platforms: Extend the campaign to newer or underutilized platforms where {competitor_brand} has little presence."
        ]

# Helper to convert image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function to send image to GPT-4 Vision and extract structured JSON or generate with AI
def generate_audience_insights(source_type='legacy', uploaded_file=None, brief_text=None, demographics_info=None):
    """
    Generate psychographic insights from either uploaded image or AI generation.
    
    Args:
        source_type: 'upload' for user upload, 'generate' for AI generation, 'legacy' for old admin flow
        uploaded_file: Streamlit uploaded file object (for upload)
        brief_text: Brief text for AI generation (for generate)
        demographics_info: Optional demographic context for AI generation
    
    Returns:
        dict: Psychographic data in standard JSON format
    """
    
    # Legacy mode - for backward compatibility with admin uploads
    if source_type == 'legacy':
        image_file_name = get_first_file_name(PATHS.get('PSYCHOGRAPHY'))
        if not image_file_name:
            return {}
        base_file_name = os.path.splitext(image_file_name)[0]
        json_file_name = f"{PATHS.get('JSON')}/{base_file_name}.json"
        image_path = f"{PATHS.get('PSYCHOGRAPHY')}/{image_file_name}"
        
        if os.path.exists(json_file_name):
            with open(json_file_name, "r") as f:
                return json.load(f)
        
        base64_image = encode_image_to_base64(image_path)
        
    # User upload mode - process uploaded file directly
    elif source_type == 'upload' and uploaded_file:
        # Convert uploaded file to base64
        uploaded_file.seek(0)  # Reset file pointer
        base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")
        
    # AI generation mode - generate from brief
    elif source_type == 'generate' and brief_text:
        # Load and prepare the prompt template
        with open("docs/prompt.txt", "r") as f:
            prompt_template = f.read()
        
        # Prepare the context
        industry = demographics_info if demographics_info else "General Consumer Market"
        
        # Replace placeholders in prompt
        prompt = prompt_template.replace("Savannah's Urban Lifestyle Enthusiasts", industry)
        prompt = prompt.replace("{brief_text[:1000]}", brief_text[:1000])
        
        # If demographics info provided, update the demographics line
        if demographics_info:
            prompt = prompt.replace("Age: 25-40 | Gender: All | Income: Middle to Upper Middle Income", demographics_info)
        
        # Generate with GPT-4 using retry logic
        result = make_openai_request(
            messages=[
                {"role": "system", "content": "You are a consumer psychologist and market research expert specializing in psychographic profiling and behavioral analysis."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o",
            response_format={"type": "json_object"},
            max_tokens=1500,
            max_retries=3
        )

        # make_openai_request returns parsed JSON or None
        return result if result else {}
    
    else:
        raise ValueError("Invalid source_type or missing required parameters")
    
    # Process image with GPT-4 Vision (for both legacy and upload modes)
    if source_type in ['legacy', 'upload']:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts marketing insights from visuals."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Please extract the psychographic and demographic data from this image "
                                "and format it into the following JSON structure:\n\n"
                                "{\n"
                                "    \"demographics\": [\"string\", \"string\", ...],\n"
                                "    \"values\": [{\"trait\": \"string\", \"qvi\": integer}, ...],\n"
                                "    \"psychological_drivers\": [{\"trait\": \"string\", \"qvi\": integer}, ...],\n"
                                "    \"activities\": [{\"trait\": \"string\", \"qvi\": integer}, ...],\n"
                                "    \"daily_routines\": [{\"trait\": \"string\", \"qvi\": integer}, ...]\n"
                                "}"
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Only save to file in legacy mode
        if source_type == 'legacy':
            os.makedirs(os.path.dirname(json_file_name), exist_ok=True)
            with open(json_file_name, "w") as f:
                json.dump(response.choices[0].message.content, f, indent=4)
        
        return result

def generate_media_consumption():
    image_file_name = get_first_file_name(PATHS.get('MEDIA_CONSUMPTION'))
    base_file_name = os.path.splitext(image_file_name)[0]
    json_file_name =  f"{PATHS.get('JSON')}/{base_file_name}.json"
    image_path = f"{PATHS.get('MEDIA_CONSUMPTION')}/{image_file_name}"

    if os.path.exists(json_file_name):
        with open(json_file_name, "r") as f:
            return json.load(f)


    base64_image = encode_image_to_base64(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a data extraction assistant that processes visual charts of audience media consumption into structured JSON for marketing purposes."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract media consumption insights from the attached image and return them in the following JSON format:\n\n"
                            "{\n"
                        "    \"streaming_platforms\": [\n"
                        "      {\"name\": \"string\", \"category\": \"string\", \"qvi\": integer} // Infer primary categories like 'Video Sharing Platform' 'Entertainment', 'Sports' etc \n"
                        "    ],\n"
                        "    \"devices\": [\n"
                        "      {\"name\": \"string\", \"qvi\": integer}\n"
                        "    ],\n"
                        "    \"newspapers\": [\n"
                        "      {\"name\": \"string\", \"qvi\": integer}\n"
                        "    ],\n"
                        "    \"tv_networks\": [\n"
                        "      {\"name\": \"string\", \"category\": \"string\", \"qvi\": integer} // Infer primary categories like 'Video Sharing Platform' 'Entertainment', 'Sports' etc \n"
                        "    ],\n"
                        "    \"streaming_devices\": [\n"
                        "      {\"name\": \"string\", \"qvi\": integer}\n"
                        "    ],\n"
                        "    \"social_media_networks\": [\n"
                        "      {\"name\": \"string\", \"qvi\": integer}\n"
                        "    ],\n"
                        "    \"magazine_reads\": [\n"
                        "      {\"name\": \"string\", \"qvi\": integer}\n"
                        "    ],\n"
                        "    \"apps_by_category\": [\n"
                        "      {\"name\": \"string\", \"qvi\": integer}\n"
                        "    ],\n"
                        "    \"hours_online_per_week\": [\n"
                        "      {\"range\": \"string\", \"composition\": integer}  // Skip the one where composition is not found\n"
                        "    ]\n"
                            "}"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=2000
    )

    os.makedirs(os.path.dirname(json_file_name), exist_ok=True)
    with open(json_file_name, "w") as f:
        json.dump(response.choices[0].message.content, f, indent=4)

    return json.loads(response.choices[0].message.content)


def generate_media_affinity():
    import pandas as pd
    base_file_name = get_first_file_name(PATHS.get('SITES_AFFINITY'))
    if not base_file_name:
        return
    df = pd.read_csv(f"{PATHS.get('SITES_AFFINITY')}/{base_file_name}")
    df['QVI Audience'] = pd.to_numeric(df['QVI Audience'], errors='coerce')
    top_5 = df.sort_values(by='QVI Audience', ascending=False).head(5)
    top_5['name'] = top_5['Domain Name']
    top_5['url'] = 'https://' + top_5['Domain Name'].str.strip()
    top_5 = top_5.rename(columns={
        'Category': 'category',
        'QVI Audience': 'qvi'
    })
    return top_5[['name', 'url', 'category', 'qvi']].to_json(orient='records')


def generate_pychographic_highlights(audience_insights):
    prompt = f"""
You are an AI trained in behavioral and psychographic marketing analysis.

Given the following psychographic payload:
{audience_insights}

Generate a paragraph called a "psychographic highlight" in the following tone and format:

"{PSYCHOGRAPHIC_HIGHLIGHTS}"

Use the top 3 highest-indexed items in each category from the payload. Format the text with HTML <strong> tags around the traits and indexes. Match the tone, length, and structure shown in the sample.

IMPORTANT: Return ONLY the psychographic highlight paragraph. Do not include any introductory phrases like "Certainly!", "Here is", "Based on", etc. Start directly with "This audience..." 
"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a data analyst. Return only the requested content without any conversational elements or acknowledgments."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content.strip()
    
    # Clean up any potential AI acknowledgments at the beginning
    # Remove common AI response patterns
    unwanted_starts = [
        "Certainly!", "Certainly,", "Certainly.", 
        "Sure!", "Sure,", "Sure.",
        "Here is", "Here's", "Based on",
        "Of course!", "Of course,", "Of course.",
        "I'll generate", "Let me generate",
        "Here is a psychographic highlight:",
        "Here's the psychographic highlight:",
        "The psychographic highlight is:",
        "Psychographic highlight:",
    ]
    
    for start in unwanted_starts:
        if content.lower().startswith(start.lower()):
            # Find where the actual content starts (usually after a colon, newline, or quote)
            for delimiter in [':', '\n', '"', 'This audience']:
                if delimiter in content:
                    parts = content.split(delimiter, 1)
                    if len(parts) > 1 and parts[1].strip():
                        content = (delimiter + parts[1]) if delimiter != 'This audience' else ('This audience' + parts[1])
                        break
    
    # Ensure content starts with "This audience" if it doesn't already
    if not content.strip().startswith("This audience"):
        # Try to find "This audience" anywhere in the text
        if "This audience" in content:
            # Extract from "This audience" onwards
            content = content[content.find("This audience"):]
    
    # Final cleanup - remove any quotes around the entire content
    content = content.strip().strip('"').strip("'").strip()
    
    return content

def generate_core_audience_summary(audience_insights, media_consumption, brief_text):
    prompt = f"""
You are an AI trained in behavioral and psychographic marketing analysis.

Given the following payload:

Psychographic Payload:
{audience_insights}

Media Consumption Payload:
{media_consumption}

Generate a paragraph called a "core audience" in the following tone and format:

"This audience skews <strong>female (57%)</strong> with a <strong>mean age of 44</strong> and <strong>19% in the $100-150k income bracket</strong> (mean income: $107,914). They have a strong affinity for Apple TV+ (index 189), health & fitness apps (32%), and premium streaming content. <strong>57% are married</strong> and <strong>59% do not have children under age 18</strong>."

Use the top 3 highest-indexed items in each category from the payload. Format the text with HTML <strong> tags around the traits and indexes. Match the tone, length, and structure shown in the sample.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating AI insights: {str(e)}")

def generate_primary_audience_signal(audience_insights, media_consumption, segment_name, brief_text):
    prompt = f"""
You are an AI trained in behavioral and psychographic marketing analysis.

Given the following payload:

Psychographic Payload:
{audience_insights}

Media Consumption Payload:
{media_consumption}

Segment Name:
{segment_name}

Generate a paragraph called "primary audience" in the following tone and format:

"Our AI analysis identifies <strong id='segment_name'>Tech-Savvy Streamers</strong> who value life full of excitement, novelties, and challenges (index 138). They have high engagement with international travel (index 152) and group travel (index 140). This audience shows strong affinities for connected TV (index 132) and premium digital video, with 2.8x higher completion rates when targeted with high-quality storytelling that emphasizes exciting experiences and creative content."

Use the top 3 highest-indexed items in each category from the payload. Format the text with HTML <strong> tags around the traits and indexes. Strictly match the tone, length, and structure shown in the sample. Use "index" instead of "qvi" as shown in the sample. Always utilise the provided segment_name: {segment_name}
"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def generate_secondary_audience_signal(audience_insights, media_consumption, segment_name, brief_text):
    prompt = f"""
You are an AI trained in behavioral and psychographic marketing analysis.

Given the following payload:

Psychographic Payload:
{audience_insights}

Media Consumption Payload:
{media_consumption}

Segment Name:
{segment_name}

Generate a paragraph called "secondary audience" in the following tone and format:

"Additional opportunity exists with <strong id='segment_name'>Lifestyle & Culture Enthusiasts</strong> who value arts and entertainment (index 124), premium lifestyle content (index 114), and cultural experiences (index 113). This segment indexes high for digital subscriptions (index 150) and demonstrates strong engagement with TV shows & movies content (index 137)."

Use the top 3 highest-indexed items in each category from the payload. Format the text with HTML <strong> tags around the traits and indexes. Strictly match the tone, length, and structure shown in the sample. Use "index" instead of "qvi" as shown in the sample. Always utilise the provided segment_name: {segment_name}
"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def generate_recommended_dmas(brief_text, audience_segments):
    """
    Generate recommended DMAs (Designated Market Areas) based on the RFP brief and audience segments.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        audience_segments (dict): The identified audience segments
        
    Returns:
        list: A list of recommended DMA IDs
    """
    try:
        # Prepare the prompt with audience segments data
        audience_segments_json = json.dumps(audience_segments, indent=2)
        
        prompt = f"""
        Given the following RFP brief and identified audience segments:
        
        RFP Content: {brief_text[:3000]}
        
        Identified Audience Segments:
        {audience_segments_json}
        
        Task: Select 4-6 Nielsen Designated Market Areas (DMAs) where this campaign should focus.
        
        Consider:
        - Geographic locations explicitly mentioned in the RFP
        - Where the identified audience segments have highest concentration
        - Market efficiency (cost vs. reach potential)
        - Competitive saturation levels
        - Budget constraints if mentioned
        
        Return a JSON array of DMA IDs only. Do not include names or other data.
        
        Common DMA Reference:
        - New York: 501
        - Los Angeles: 803
        - Chicago: 602
        - Philadelphia: 504
        - Dallas-Fort Worth: 623
        - San Francisco-Oakland-San Jose: 807
        - Boston: 506
        - Atlanta: 524
        - Washington DC: 511
        - Houston: 618
        - Phoenix: 753
        - Seattle-Tacoma: 819
        - Miami-Fort Lauderdale: 528
        - Denver: 751
        - Detroit: 505
        - Tampa-St. Petersburg: 539
        - Minneapolis-St. Paul: 613
        - Orlando-Daytona Beach: 534
        - Sacramento-Stockton: 862
        - Charlotte: 517
        
        Example output:
        [501, 803, 602, 807]
        
        Return ONLY a JSON array of numbers. Nothing else.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a media planning expert specializing in DMA selection and geographic targeting for advertising campaigns."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=200
        )
        
        # Parse the response
        result = json.loads(response.choices[0].message.content)
        print('recommended_dmas AI GENERATOR')
        print(result)
        
        # Extract the DMA IDs from various possible response formats
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            # Handle cases where the model returns {"dmas": [501, 803, ...]}
            if "dmas" in result:
                return result["dmas"]
            if "DMAs" in result:
                return result["DMAs"]
            elif "dma_ids" in result:
                return result["dma_ids"]
            elif "ids" in result:
                return result["ids"]
            # Handle case where the model returns {"result": [501, 803, ...]}
            elif "result" in result:
                return result["result"]
        
        # Fallback to default DMAs if parsing fails
        return [501, 803, 602, 807]
        
    except Exception as e:
        print(f"Error generating recommended DMAs: {str(e)}")
        # Return default major market DMAs
        return [501, 803, 602, 807]  # New York, LA, Chicago, San Francisco

def generate_audience_reach(dma_ids, audience_segments, industry):
    """
    Calculate the addressable audience reach for each DMA based on campaign targeting criteria.
    
    Args:
        dma_ids (list): List of DMA IDs
        audience_segments (dict): The target audience segments
        industry (str): The industry vertical
        
    Returns:
        list: List of dictionaries containing DMA name and audience reach
    """
    try:
        # DMA ID to name mapping (major markets)
        dma_mapping = {
            501: "New York, NY",
            803: "Los Angeles, CA",
            602: "Chicago, IL",
            504: "Philadelphia, PA",
            623: "Dallas-Fort Worth, TX",
            807: "San Francisco-Oakland-San Jose, CA",
            506: "Boston, MA",
            524: "Atlanta, GA",
            511: "Washington DC",
            618: "Houston, TX",
            753: "Phoenix, AZ",
            819: "Seattle-Tacoma, WA",
            528: "Miami-Fort Lauderdale, FL",
            751: "Denver, CO",
            505: "Detroit, MI",
            539: "Tampa-St. Petersburg, FL",
            613: "Minneapolis-St. Paul, MN",
            534: "Orlando-Daytona Beach, FL",
            862: "Sacramento-Stockton, CA",
            517: "Charlotte, NC"
        }
        
        # Convert DMA IDs to names for the prompt
        selected_dmas = []
        for dma_id in dma_ids:
            if dma_id in dma_mapping:
                selected_dmas.append({"id": dma_id, "name": dma_mapping[dma_id]})
        
        prompt = f"""
        Given the selected DMAs and campaign targeting criteria:
        
        Selected DMAs: {json.dumps(selected_dmas)}
        Target Audience Segments: {json.dumps(audience_segments, indent=2)}
        Industry: {industry}
        
        Task: Calculate the addressable audience reach (in millions) for each DMA based on the campaign's target criteria.
        
        For each DMA:
        1. Start with the DMA's total population
        2. Apply demographic filters (age, income, education)
        3. Apply psychographic/behavioral filters based on audience segments
        4. Consider industry-specific penetration rates
        
        Return data in this exact format:
        [
          {{
            "name": "DMA Name, State",
            "audienceReach": X.X
          }}
        ]
        
        Include a "National Campaign" entry that represents the total addressable audience if running nationally (not just sum of selected DMAs).
        
        Reference populations (in millions) and typical addressable percentages:
        - New York: 7.5M total → likely 2.5-3.0M addressable (33-40%)
        - Los Angeles: 5.7M total → likely 1.8-2.2M addressable (32-39%)
        - San Francisco: 2.5M total → likely 0.8-1.2M addressable (32-48%)
        - Chicago: 3.5M total → likely 1.1-1.4M addressable (31-40%)
        - Dallas-Fort Worth: 2.8M total → likely 0.9-1.1M addressable (32-39%)
        - Boston: 2.4M total → likely 0.8-1.0M addressable (33-42%)
        - Atlanta: 2.3M total → likely 0.7-0.9M addressable (30-39%)
        - Houston: 2.5M total → likely 0.8-1.0M addressable (32-40%)
        - National: 85-95M addressable audience across all 210 DMAs
        
        The audienceReach should be a realistic number based on the targeting criteria.
        
        Example output:
        [
          {{
            "name": "New York, NY",
            "audienceReach": 2.8
          }},
          {{
            "name": "Los Angeles, CA",
            "audienceReach": 2.1
          }},
          {{
            "name": "National Campaign",
            "audienceReach": 28.5
          }}
        ]

        Return ONLY a JSON array of objects as shown in the example output. Nothing else.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a media planning analyst expert in calculating addressable audience reach across DMAs based on demographic and psychographic targeting criteria."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=800
        )
        
        # Parse the response
        result = json.loads(response.choices[0].message.content)
        print('result from audience reach AI GENERATOR')
        print(result)
        
        # Extract the audience reach data from various possible formats
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            if "audienceReach" in result:
                return result["audienceReach"]
            elif "reach" in result:
                return result["reach"]
            elif "data" in result:
                return result["data"]
            elif "result" in result:
                return result["result"]
        
        # Fallback data if parsing fails
        fallback_data = []
        for dma_id in dma_ids:
            if dma_id in dma_mapping:
                # Estimate based on DMA size
                reach_estimates = {
                    501: 2.8,  # New York
                    803: 2.1,  # Los Angeles
                    602: 1.3,  # Chicago
                    807: 1.0,  # San Francisco
                    623: 1.0,  # Dallas
                    506: 0.9,  # Boston
                    524: 0.8,  # Atlanta
                    618: 0.9,  # Houston
                }
                fallback_data.append({
                    "name": dma_mapping[dma_id],
                    "audienceReach": reach_estimates.get(dma_id, 0.7)
                })
        
        # Add national campaign estimate
        fallback_data.append({
            "name": "National Campaign",
            "audienceReach": 28.5
        })
        
        return fallback_data
        
    except Exception as e:
        print(f"Error generating audience reach: {str(e)}")
        # Return fallback data
        fallback_data = []
        for dma_id in dma_ids[:4]:  # Use first 4 DMAs
            if dma_id == 501:
                fallback_data.append({"name": "New York, NY", "audienceReach": 2.8})
            elif dma_id == 803:
                fallback_data.append({"name": "Los Angeles, CA", "audienceReach": 2.1})
            elif dma_id == 602:
                fallback_data.append({"name": "Chicago, IL", "audienceReach": 1.3})
            elif dma_id == 807:
                fallback_data.append({"name": "San Francisco-Oakland-San Jose, CA", "audienceReach": 1.0})
        
        fallback_data.append({"name": "National Campaign", "audienceReach": 28.5})
        return fallback_data

def generate_market_insights(recommended_dmas, primary_audience, all_audiences, audience_reach):
    """
    Generate market insights summary based on recommended DMAs and audience data.
    
    Args:
        recommended_dmas (list): List of recommended DMA IDs with names
        primary_audience (dict): The primary audience segment
        all_audiences (dict): All audience segments
        audience_reach (list): Audience reach data by DMA
        
    Returns:
        dict: Market insights containing primary market name, audience, and total addressable audience
    """
    try:
        # Prepare data for the prompt
        dmas_with_names = []
        for dma in audience_reach:
            if dma["name"] != "National Campaign":
                dmas_with_names.append(dma)
        
        prompt = f"""
        Based on the campaign analysis and recommended DMAs:
        
        Recommended DMAs: {json.dumps(dmas_with_names)}
        Primary Audience Segment: {json.dumps(primary_audience)}
        All Audience Segments: {json.dumps(all_audiences)}
        Total Audience Reach by DMA: {json.dumps(audience_reach)}
        
        Task: Generate market insights summary with these three specific fields:
        
        1. primaryMarketName: The name of the #1 recommended DMA (just city name, no state)
        2. primaryMarketAudience: The name/label of the dominant audience segment in that market
        3. totalAddressableAudience: Sum of all audienceReach values from selected DMAs (not including National)
        
        Consider:
        - Which DMA has the highest concentration of the primary audience
        - Which audience segment has the strongest presence in the top market
        - Calculate total by adding all individual DMA reach numbers
        
        Return ONLY a JSON object in this exact format:
        {{
          "primaryMarketName": "San Francisco",
          "primaryMarketAudience": "Tech Enthusiasts",
          "totalAddressableAudience": 8.5
        }}
        
        IMPORTANT:
        - primaryMarketName should be JUST the city name without state (e.g., "New York" not "New York, NY")
        - primaryMarketAudience should be the exact name of the audience segment
        - totalAddressableAudience should be the sum of all DMA reach values (excluding National Campaign)
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a market insights analyst specializing in geographic and audience analysis for advertising campaigns."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=300
        )
        
        # Parse the response
        insights = json.loads(response.choices[0].message.content)

        print('insights from market insights AI GENERATOR')
        print(insights)
        
        # Validate the response has required fields
        if all(key in insights for key in ["primaryMarketName", "primaryMarketAudience", "totalAddressableAudience"]):
            return insights
        
        # Fallback calculation if response is incomplete
        total_reach = sum(dma["audienceReach"] for dma in audience_reach if dma["name"] != "National Campaign")
        primary_dma = dmas_with_names[0] if dmas_with_names else {"name": "New York, NY"}
        primary_market_name = primary_dma["name"].split(",")[0].strip()
        
        return {
            "primaryMarketName": primary_market_name,
            "primaryMarketAudience": primary_audience.get("name", "Primary Audience"),
            "totalAddressableAudience": round(total_reach, 1)
        }
        
    except Exception as e:
        print(f"Error generating market insights: {str(e)}")
        # Return fallback insights
        total_reach = sum(dma["audienceReach"] for dma in audience_reach if dma.get("name", "") != "National Campaign")
        
        return {
            "primaryMarketName": "New York",
            "primaryMarketAudience": "Urban Professionals",
            "totalAddressableAudience": round(total_reach, 1) if total_reach > 0 else 7.5
        }
