"""
AI Insights module for enhanced analysis capabilities using OpenAI's API.
This module provides advanced natural language processing and analysis 
for marketing briefs and RFPs.
"""

import os
import json
import re
from openai import OpenAI

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
        from analysis import extract_brand_info
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
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )
        
        # Debug the raw response
        print("================================")
        print("===== OPENAI API RESPONSE =====")
        print(response.choices[0].message.content)
        print("================================")
        
        # Parse the JSON response
        insights = json.loads(response.choices[0].message.content)
        
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
                    {"platform": "Mobile Video", "tactical_approach": "Create mobile-first vertical video assets in Spanish featuring landscape professionals succeeding on job sites, with specific product placements. Use VCR (Video Completion Rate) of 70-95% as the benchmark for performance."},
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
    from analysis import extract_brand_info
    brand_name, industry, product_type = extract_brand_info(brief_text)
    
    # Default segments structure with placeholder content
    segments = {
        "segments": [
            # Primary audience segment
            {
                "name": "Gen Z Hoops Fanatics",
                "description": "Young basketball enthusiasts who actively follow the sport and engage with basketball culture",
                "interest_categories": ["Basketball Enthusiasts", "Sports Apparel", "Sneakerheads", "Live Sports Events"],
                "targeting_params": {
                    "age_range": "18-24",
                    "gender_targeting": "All",
                    "income_targeting": "Below $50k"
                },
                "platform_targeting": [
                    {
                        "platform": "Programmatic Video Platforms",
                        "targeting_approach": "Interest-based targeting with sports content adjacency"
                    }
                ],
                "expected_performance": {
                    "CTR": "70-95%",  # For video platforms, this becomes VCR (video completion rate)
                    "engagement_rate": "6.2%"
                },
                "bidding_strategy": {
                    "bid_adjustments": "Higher bids on weekends",
                    "dayparting": "Evenings and weekends"
                }
            },
            # Secondary audience segment
            {
                "name": "Multi-Platform Sports Enthusiasts",
                "description": "Older Gen Z and young adults who consume sports content across multiple devices and platforms",
                "interest_categories": ["Athletic Lifestyle", "Premium Sports Content", "Cross-Device Media"],
                "targeting_params": {
                    "age_range": "21-34",
                    "gender_targeting": "All",
                    "income_targeting": "Above $50k"
                },
                "platform_targeting": [
                    {
                        "platform": "Audio Streaming Platforms",
                        "targeting_approach": "Sports podcast listeners and game streaming audiences"
                    }
                ],
                "expected_performance": {
                    "CTR": "80-95%",  # For audio platforms, this becomes LTR (listen-through rate)
                    "engagement_rate": "5.8%"
                },
                "bidding_strategy": {
                    "bid_adjustments": "Evening and weekend hours",
                    "dayparting": "5-11pm weekdays, all day weekends"
                }
            },
            # Growth opportunity segment
            {
                "name": "Fashion-Forward Urban Professionals",
                "description": "Style-conscious young professionals who blend athletic and casual wear",
                "interest_categories": ["Urban Fashion", "Premium Streetwear", "Casual Office Attire"],
                "targeting_params": {
                    "age_range": "25-34",
                    "gender_targeting": "All",
                    "income_targeting": "$75k+"
                },
                "platform_targeting": [
                    {
                        "platform": "Premium Display Networks",
                        "targeting_approach": "Fashion and lifestyle content adjacency"
                    }
                ],
                "expected_performance": {
                    "CTR": "0.2-0.5%",
                    "CPA": "$45-60",
                    "engagement_rate": "4.2%"
                },
                "bidding_strategy": {
                    "bid_adjustments": "Higher bids on payday periods",
                    "dayparting": "Lunch hours and evenings"
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

def generate_audience_segments(brief_text, ari_scores):
    """
    Generate audience segment recommendations based on the brief text and ARI scores.
    Including new potential audience segments with high growth potential that might not be 
    currently addressed in the brief.
    
    Args:
        brief_text (str): The marketing brief or RFP text
        ari_scores (dict): The Audience Resonance Index scores
        
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
        3. CTR estimates should reflect realistic omnichannel expectations (typically 0.05-0.7% for display, 0.3-1.5% for video)
        4. Make sure the LAST segment is a high-growth potential audience that might not be explicitly mentioned 
           in the brief but would be valuable to target based on adjacent interests, behaviors, or demographic extensions.
           This should be a growth opportunity audience that the campaign isn't currently addressing.
        
        Campaign Information:
        {brief_text[:3000]}  # Limiting to 3000 chars to avoid token limits
        
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
           - For video/OTT/CTV formats: Use VCR (Video Completion Rate) of 75-85% instead of CTR
           - For audio formats: Use LTR (Listen-Through Rate) of 80-90% instead of CTR
        6. Specific media buying tactics for this segment (bid adjustments, dayparting, etc.)
        
        Format the response as a valid JSON array with objects containing:
        - name: string (descriptive segment name)
        - targeting_params: object with age_range, gender_targeting, income_targeting, education_targeting, and location_targeting
        - interest_categories: array of strings (specific interests to target in ad platforms)
        - platform_targeting: array of objects with 'platform' and 'targeting_approach' 
        - expected_performance: object with CTR (click-through rate or video completion rate for video content), CPA (cost per acquisition), and engagement_rate
        - bidding_strategy: object with bid_adjustments, dayparting, and placement_priorities
        
        Remember, make the THIRD segment a high-potential growth audience that is not currently being addressed 
        in the campaign brief but shows strong potential based on trends, adjacent interests, and market opportunities.
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
        
        # Parse the JSON response
        segments = json.loads(response.choices[0].message.content)
        
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
                            "CTR": "0.3-0.7%",  # For display; would be 75-85% for video formats
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
                        "CTR": "75-85%",  # For video platforms, this becomes VCR (video completion rate)
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