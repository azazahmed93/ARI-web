"""
Audience Simulation module for generating AI-powered audience responses to marketing scenarios.
This module simulates different audience segments and their reactions to marketing messages.
"""
import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
import random

# Initialize OpenAI client (with graceful handling of missing API key)
def _get_openai_client():
    """Get OpenAI client, initializing if needed."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def classify_input_intent(user_input: str) -> Dict:
    """
    Classify user input as 'message_testing' or 'analytical_inquiry' using AI.

    Args:
        user_input: The user's scenario/question text

    Returns:
        Dict with:
            - intent: 'message_testing' | 'analytical_inquiry'
            - confidence: float (0.0-1.0)
            - reasoning: str (why this classification was chosen)
    """

    # Handle empty or very short input
    if len(user_input.strip()) < 10:
        return {
            'intent': 'message_testing',
            'confidence': 0.5,
            'reasoning': 'Input too short to classify reliably'
        }

    classification_prompt = f"""Classify the following user input into one of two categories:

1. MESSAGE_TESTING: User wants to test how audiences react to a specific marketing message, positioning, or campaign.
   Examples:
   - "Try this premium car message with luxury features"
   - "How would you respond to eco-friendly packaging?"
   - "Test this tagline: 'Innovation meets tradition'"

2. ANALYTICAL_INQUIRY: User wants analytical insights about audience psychology, behavior, or motivations.
   Examples:
   - "What motivates brand loyalists vs occasional buyers?"
   - "Why do audiences prefer premium over budget options?"
   - "What psychological factors drive conversion?"

User Input: "{user_input}"

Respond with ONLY a JSON object in this exact format:
{{
    "intent": "message_testing" or "analytical_inquiry",
    "confidence": 0.95,
    "reasoning": "Brief explanation of classification"
}}"""

    try:
        client = _get_openai_client()
        if not client:
            # No API key available, use fallback
            raise Exception("OpenAI API key not available")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert classifier that determines user intent. Always respond with valid JSON only."},
                {"role": "user", "content": classification_prompt}
            ],
            temperature=0.3,  # Low temperature for consistent classification
            max_tokens=150
        )

        result_text = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]

        result = json.loads(result_text)
        return result

    except Exception as e:
        # Fallback to heuristic classification
        analytical_keywords = [
            'what', 'why', 'how', 'motivate', 'factor', 'drive',
            'psychology', 'behavior', 'insight', 'understand',
            'explain', 'reason', 'cause', 'influence', 'compare',
            'separate', 'difference', 'versus', 'vs', 'between'
        ]

        user_input_lower = user_input.lower()
        analytical_count = sum(1 for keyword in analytical_keywords if keyword in user_input_lower)

        # Check for message testing indicators
        message_indicators = ['what if we', 'how would you respond', 'try this', 'test this']
        has_message_indicator = any(indicator in user_input_lower for indicator in message_indicators)

        if has_message_indicator:
            return {
                'intent': 'message_testing',
                'confidence': 0.7,
                'reasoning': 'Heuristic classification: message testing indicator detected'
            }
        elif analytical_count >= 2:
            return {
                'intent': 'analytical_inquiry',
                'confidence': 0.7,
                'reasoning': 'Heuristic classification: multiple analytical keywords detected'
            }
        else:
            return {
                'intent': 'message_testing',
                'confidence': 0.6,
                'reasoning': 'Default classification (AI classification unavailable)'
            }

def generate_analytical_prompt(
    audience_profile: Dict,
    user_scenario: str,
    rfp_context: str,
    trend_context: str
) -> str:
    """
    Generate prompt for analytical inquiry mode.
    Answers user questions FROM the perspective of each audience segment.

    Args:
        audience_profile: Audience segment information
        user_scenario: The analytical question to answer
        rfp_context: RFP analysis context
        trend_context: Market trends context

    Returns:
        str: Formatted analytical prompt
    """

    # Extract audience characteristics
    if audience_profile.get('is_core', False):
        characteristics = ', '.join(audience_profile.get('traits', []))
        audience_desc = f"{audience_profile.get('description', 'Primary target audience')} with characteristics: {characteristics}"
    elif 'segment_data' in audience_profile:
        segment = audience_profile['segment_data']
        targeting_params = segment.get('targeting_params', {})

        char_parts = []
        if 'age_range' in targeting_params:
            char_parts.append(f"Age: {targeting_params['age_range']}")
        if 'income_targeting' in targeting_params:
            char_parts.append(f"Income: {targeting_params['income_targeting']}")
        interests = segment.get('interest_categories', [])
        if interests:
            char_parts.append(f"Interests: {', '.join(interests[:3])}")

        audience_desc = f"{audience_profile['name']} - {'; '.join(char_parts)}" if char_parts else audience_profile['name']
    else:
        audience_desc = f"{audience_profile['name']}: {audience_profile.get('description', 'Target audience')}"

    return f"""Answer the following analytical question about the {audience_profile['name']} audience segment.

Audience Profile: {audience_desc}
{rfp_context}
{trend_context}

Analytical Question: "{user_scenario}"

Provide a concise, insight-driven answer from a third-person analytical perspective. Focus on:
1. Key psychological drivers and motivations specific to this audience segment
2. Behavioral patterns and decision-making factors that distinguish this group
3. Actionable insights relevant to marketing strategy for this specific segment

Your response should explain how THIS PARTICULAR AUDIENCE SEGMENT relates to the question, highlighting what makes them unique.
Maximum response: 200 characters."""

def generate_message_testing_prompt(
    audience_profile: Dict,
    user_scenario: str,
    rfp_context: str,
    trend_context: str,
    analysis_data: Optional[Dict] = None
) -> str:
    """
    Generate prompt for message testing mode (existing behavior).
    Predicts how audiences will react to marketing messages.

    Args:
        audience_profile: Audience segment information
        user_scenario: The marketing message/scenario to test
        rfp_context: RFP analysis context
        trend_context: Market trends context
        analysis_data: Optional RFP analysis data

    Returns:
        str: Formatted message testing prompt
    """

    # Check if this is the core audience
    if audience_profile.get('is_core', False):
        characteristics = ', '.join(audience_profile.get('traits', []))

        return f"""Analyze the Core Target Audience from the RFP analysis and predict their behavioral response.
        Description: {audience_profile.get('description', 'Primary target audience')}
        Key Characteristics: {characteristics}
        {rfp_context}
        {trend_context}
        Marketing Scenario: "{user_scenario}"

        Based on this core audience's primary business objectives, decision-making criteria, and expected outcomes, analyze how they would likely respond to this marketing scenario.

        Provide a 1-2 sentence behavioral prediction that describes their expected reaction (positive, neutral, or negative).
        Your analysis should predict whether this audience would likely be excited, interested, skeptical, or concerned, using third-person perspective to describe their probable response.
        Maximum response: 200 characters."""

    # Check if we have segment data in the profile
    elif 'segment_data' in audience_profile:
        segment = audience_profile['segment_data']

        # Build characteristics from segment data
        characteristics = []
        targeting_params = segment.get('targeting_params', {})

        if targeting_params:
            if 'age_range' in targeting_params:
                characteristics.append(f"Age: {targeting_params['age_range']}")
            if 'gender_targeting' in targeting_params:
                characteristics.append(f"Gender: {targeting_params['gender_targeting']}")
            if 'income_targeting' in targeting_params:
                characteristics.append(f"Income: {targeting_params['income_targeting']}")
            if 'education_targeting' in targeting_params:
                characteristics.append(f"Education: {targeting_params['education_targeting']}")

        # Add interests
        interests = segment.get('interest_categories', [])
        if interests:
            characteristics.append(f"Interests: {', '.join(interests)}")

        characteristics_str = '; '.join(characteristics) if characteristics else 'General audience characteristics'

        # Build motivations from segment data
        motivations = []
        if 'bidding_strategy' in segment:
            bidding = segment['bidding_strategy']
            if 'strategy_type' in bidding:
                motivations.append(f"{bidding['strategy_type']} focused")

        # Add platform preferences
        if 'platform_targeting' in segment:
            platforms = [p.get('platform', '') for p in segment['platform_targeting'] if 'platform' in p]
            if platforms:
                motivations.append(f"Active on {', '.join(platforms)}")

        motivations_str = ', '.join(motivations) if motivations else 'General consumer motivations'

        # Generate dynamic prompt
        return f"""Analyze {audience_profile['name']}: {audience_profile.get('description', 'a target audience segment')} and predict their behavioral response.
        Characteristics: {characteristics_str}
        {rfp_context}
        {trend_context}
        Marketing Scenario: "{user_scenario}"

        Based on this audience segment's characteristics and their {motivations_str}, analyze how they would likely respond to this marketing scenario.

        Provide a 1-2 sentence behavioral prediction that describes their expected reaction (positive, neutral, or negative).
        Your analysis should predict whether this audience would likely be excited, interested, skeptical, or concerned, using third-person perspective to describe their probable response.
        Maximum response: 200 characters."""

    # Fallback to hardcoded prompts if no segment data
    prompts = {
        'rfp-core-audience': f"""Analyze the RFP Core Audience: the primary target audience identified in the RFP analysis.
        {f"Characteristics: {analysis_data.get('keyAudience', 'Professional decision makers')} in {analysis_data.get('industry', 'the industry')}, focused on {analysis_data.get('summary', 'business results and strategic outcomes')}." if analysis_data else 'Characteristics: Strategic decision makers, performance-focused professionals, results-oriented buyers with quality-conscious mindset.'}
        {rfp_context}
        {trend_context}
        Marketing Scenario: "{user_scenario}"

        Based on this RFP Core Audience's primary motivations around business results, strategic decision-making, and performance optimization, analyze how they would likely respond to this marketing scenario.

        Provide a 1-2 sentence behavioral prediction that describes their expected reaction (positive, neutral, or negative).
        Your analysis should predict whether this audience would likely be excited, interested, skeptical, or concerned, using third-person perspective to describe their probable response.
        Maximum response: 200 characters.""",

        'growth-audience-1': f"""Analyze Growth Audience 1 - Urban Explorers: a tech-forward, sustainability-focused marketing audience from the RFP analysis.
        Characteristics: Innovation-driven, environmental consciousness, digital natives, urban lifestyle preferences.
        {rfp_context}
        {trend_context}
        Marketing Scenario: "{user_scenario}"

        Based on Growth Audience 1 (Urban Explorers) motivations around technology adoption, sustainability values, and innovative solutions, analyze how they would likely respond to this marketing scenario.

        Provide a 1-2 sentence behavioral prediction that describes their expected reaction (positive, neutral, or negative).
        Your analysis should predict whether this audience would likely be excited, interested, skeptical, or concerned, using third-person perspective to describe their probable response.
        Maximum response: 200 characters.""",

        'growth-audience-2': f"""Analyze Growth Audience 2 - Global Nomads: a luxury-lifestyle driven, health-conscious marketing audience from the RFP analysis.
        Characteristics: Premium experiences, wellness-focused, location independence, quality over quantity mindset.
        {rfp_context}
        {trend_context}
        Marketing Scenario: "{user_scenario}"

        Based on Growth Audience 2 (Global Nomads) motivations around luxury consumption, wellness priorities, and lifestyle flexibility, analyze how they would likely respond to this marketing scenario.

        Provide a 1-2 sentence behavioral prediction that describes their expected reaction (positive, neutral, or negative).
        Your analysis should predict whether this audience would likely be excited, interested, skeptical, or concerned, using third-person perspective to describe their probable response.
        Maximum response: 200 characters.""",

        'emerging-audience': f"""Analyze Emerging Audience 3 - Cultural Enthusiasts: a budget-conscious, experience-seeking marketing audience from the RFP analysis.
        Characteristics: Cultural immersion, value-oriented, authentic experiences, social connection priorities.
        {rfp_context}
        {trend_context}
        Marketing Scenario: "{user_scenario}"

        Based on Emerging Audience 3 (Cultural Enthusiasts) motivations around cultural authenticity, value consciousness, and meaningful experiences, analyze how they would likely respond to this marketing scenario.

        Provide a 1-2 sentence behavioral prediction that describes their expected reaction (positive, neutral, or negative).
        Your analysis should predict whether this audience would likely be excited, interested, skeptical, or concerned, using third-person perspective to describe their probable response.
        Maximum response: 200 characters."""
    }

    return prompts.get(audience_profile['id'], prompts['rfp-core-audience'])

def generate_audience_prompt(
    audience_profile: Dict,
    user_scenario: str,
    analysis_data: Optional[Dict] = None,
    intent_classification: Optional[Dict] = None
) -> str:
    """
    Generate a prompt for the AI to simulate audience response or answer analytical questions.
    Now supports both message testing and analytical inquiry modes.

    Args:
        audience_profile: Dictionary containing audience profile information
        user_scenario: The marketing scenario to test OR analytical question
        analysis_data: Optional RFP analysis data from the main analysis
        intent_classification: Classification result from classify_input_intent()

    Returns:
        str: Formatted prompt for AI response generation
    """

    # Determine mode
    mode = 'message_testing'  # Default
    if intent_classification:
        mode = intent_classification.get('intent', 'message_testing')

    # Get RFP context if available
    rfp_context = ""
    if analysis_data:
        rfp_context = f"""
        Based on RFP Analysis:
        - Industry: {analysis_data.get('industry', 'General')}
        - Key Audience: {analysis_data.get('keyAudience', 'Professional')}
        - Campaign Focus: {analysis_data.get('summary', 'Marketing campaign')}
        """

    # Include emerging market trends context
    trend_context = """
    Market Intelligence Context:
    - Current trending topics in consumer behavior and digital marketing
    - Emerging opportunities in sustainable business practices and wellness
    - Rising interest in authentic brand experiences and premium lifestyle
    """

    # Route to appropriate prompt generator based on intent
    if mode == 'analytical_inquiry':
        return generate_analytical_prompt(
            audience_profile,
            user_scenario,
            rfp_context,
            trend_context
        )
    else:
        return generate_message_testing_prompt(
            audience_profile,
            user_scenario,
            rfp_context,
            trend_context,
            analysis_data
        )

def simulate_audience_response(audience_profile: Dict, user_scenario: str, analysis_data: Optional[Dict] = None) -> Dict:
    """
    Simulate an audience response to a marketing scenario OR answer analytical questions.
    Now intelligently detects input intent and routes to appropriate AI prompt.

    Args:
        audience_profile: Dictionary containing audience profile information
        user_scenario: The marketing scenario to test OR analytical question to answer
        analysis_data: Optional RFP analysis data

    Returns:
        Dict: Audience response with metrics and insights
    """

    # Check if OpenAI API is available
    if not os.environ.get("OPENAI_API_KEY"):
        # Generate a default response without AI
        return generate_default_response(audience_profile, user_scenario)

    try:
        # NEW: Classify input intent to determine mode (message testing vs analytical)
        intent_classification = classify_input_intent(user_scenario)

        # Generate appropriate prompt based on intent classification
        prompt = generate_audience_prompt(
            audience_profile,
            user_scenario,
            analysis_data,
            intent_classification  # NEW: Pass classification to prompt generator
        )
        
        # Call OpenAI API
        client = _get_openai_client()
        if not client:
            # No API key available, use fallback
            raise Exception("OpenAI API key not available")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert audience behavior prediction system that analyzes how different audience segments would likely respond to marketing scenarios. Always describe audience reactions from a third-person analytical perspective, not as if you are the audience."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Analyze sentiment and generate metrics
        sentiment = analyze_sentiment(response_text)
        metrics = generate_response_metrics(sentiment, audience_profile)
        
        # Extract key insights
        key_insights = extract_key_insights(response_text, sentiment, metrics)
        
        # Use the full response as the quote since it's now short and focused
        quote = response_text
        
        return {
            'audienceType': audience_profile['name'],
            'response': response_text,
            'quote': quote,
            'sentiment': sentiment,
            'resonanceScore': metrics['resonanceScore'],
            'engagementLevel': metrics['engagementLevel'],
            'conversionPotential': metrics['conversionPotential'],
            'keyInsights': key_insights
        }
        
    except Exception as e:
        # Fallback to default response on error
        return generate_default_response(audience_profile, user_scenario)

def analyze_sentiment(response_text: str) -> str:
    """
    Analyze the sentiment of the response text.
    
    Args:
        response_text: The AI-generated response
    
    Returns:
        str: 'positive', 'neutral', or 'negative'
    """
    positive_words = ['excited', 'love', 'great', 'amazing', 'excellent', 'fantastic', 'interested', 'valuable', 'impressive']
    negative_words = ['concerned', 'worried', 'skeptical', 'disappointed', 'confused', 'uncertain', 'expensive', 'difficult']
    
    response_lower = response_text.lower()
    
    positive_count = sum(1 for word in positive_words if word in response_lower)
    negative_count = sum(1 for word in negative_words if word in response_lower)
    
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'

def generate_response_metrics(sentiment: str, audience_profile: Dict) -> Dict:
    """
    Generate realistic metrics based on sentiment and audience profile.
    
    Args:
        sentiment: The sentiment analysis result
        audience_profile: The audience profile dictionary
    
    Returns:
        Dict: Metrics including resonance score, engagement level, and conversion potential
    """
    # Base metrics by sentiment
    base_metrics = {
        'positive': {'resonance': (8, 10), 'engagement': (7, 10), 'conversion': (6, 9)},
        'neutral': {'resonance': (5, 7), 'engagement': (5, 7), 'conversion': (4, 6)},
        'negative': {'resonance': (2, 4), 'engagement': (3, 5), 'conversion': (2, 4)}
    }
    
    metrics = base_metrics.get(sentiment, base_metrics['neutral'])
    
    # Adjust based on audience profile
    if 'tech-forward' in ' '.join(audience_profile.get('traits', [])).lower():
        # Tech-forward audiences may have higher engagement
        adjustment = 1
    elif 'budget-conscious' in ' '.join(audience_profile.get('traits', [])).lower():
        # Budget-conscious audiences may have lower conversion
        adjustment = -1
    else:
        adjustment = 0
    
    return {
        'resonanceScore': random.randint(*metrics['resonance']) + adjustment,
        'engagementLevel': random.randint(*metrics['engagement']) + adjustment,
        'conversionPotential': random.randint(*metrics['conversion']) + adjustment
    }

def extract_key_insights(response_text: str, sentiment: str, metrics: Dict) -> List[str]:
    """
    Extract key insights from the response.
    
    Args:
        response_text: The AI-generated response
        sentiment: The sentiment analysis result
        metrics: The generated metrics
    
    Returns:
        List[str]: List of key insights
    """
    interest_level = 'High' if sentiment == 'positive' else 'Low' if sentiment == 'negative' else 'Moderate'
    
    insights = [
        f"{interest_level} initial interest",
        f"{metrics['conversionPotential']}/10 conversion potential"
    ]
    
    # Add specific insight based on response content
    if 'sustainable' in response_text.lower() or 'eco' in response_text.lower():
        insights.append("Sustainability focus resonates")
    elif 'premium' in response_text.lower() or 'luxury' in response_text.lower():
        insights.append("Premium positioning aligns")
    elif 'value' in response_text.lower() or 'affordable' in response_text.lower():
        insights.append("Value proposition important")
    else:
        insights.append("Brand alignment potential")
    
    return insights

def generate_default_response(audience_profile: Dict, user_scenario: str) -> Dict:
    """
    Generate a default response when AI is not available.
    
    Args:
        audience_profile: Dictionary containing audience profile information
        user_scenario: The marketing scenario to test
    
    Returns:
        Dict: Default audience response
    """
    # Generate dynamic response based on audience profile
    traits = audience_profile.get('traits', [])
    name = audience_profile.get('name', 'Target Audience')
    description = audience_profile.get('description', '')
    
    # Determine sentiment based on traits
    positive_indicators = ['premium', 'innovative', 'tech', 'quality', 'enthusiast']
    negative_indicators = ['budget', 'value', 'cost-conscious']
    
    sentiment = 'neutral'
    traits_lower = ' '.join(traits).lower()
    if any(indicator in traits_lower for indicator in positive_indicators):
        sentiment = 'positive'
    elif any(indicator in traits_lower for indicator in negative_indicators) and 'premium' in user_scenario.lower():
        sentiment = 'negative'
    
    # Generate response based on profile
    if 'segment_data' in audience_profile:
        # Use segment data to craft response
        segment = audience_profile['segment_data']
        interests = segment.get('interest_categories', [])
        
        # Generate a short, sentiment-aligned response from system perspective
        if sentiment == 'positive':
            response = f"This audience would likely show strong interest due to alignment with their {interests[0] if interests else 'values'} - they would be excited about how this matches their {traits[0].lower() if traits else 'interests'}."
        elif sentiment == 'negative':
            response = f"This audience would likely be skeptical as the scenario doesn't align with their {interests[0] if interests else 'values'} and might not meet their {traits[0].lower() if traits else 'needs'}."
        else:
            response = f"This audience would show moderate interest but would need to see how it specifically addresses their {interests[0] if interests else 'priorities'} before fully engaging."
    else:
        # Fallback response from system perspective
        if sentiment == 'positive':
            response = f"This audience would be impressed by this approach - it clearly addresses their {traits[0].lower() if traits else 'values'} and they would see real potential for engagement."
        elif sentiment == 'negative':
            response = f"This audience would likely reject this approach as it doesn't align with their {traits[0].lower() if traits else 'priorities'}, making them skeptical about the value proposition."
        else:
            response = f"The {name} would see some potential here but would require more specifics on how this addresses their {traits[0].lower() if traits else 'needs'} before committing."
    
    # Set metrics based on sentiment
    metrics_map = {
        'positive': {'resonance': 7, 'engagement': 8, 'conversion': 6},
        'neutral': {'resonance': 6, 'engagement': 5, 'conversion': 5},
        'negative': {'resonance': 3, 'engagement': 4, 'conversion': 2}
    }
    
    metrics = metrics_map.get(sentiment, metrics_map['neutral'])
    
    return {
        'audienceType': name,
        'response': response,
        'quote': response,  # Use full response as quote since it's now short
        'sentiment': sentiment,
        'resonanceScore': metrics['resonance'],
        'engagementLevel': metrics['engagement'],
        'conversionPotential': metrics['conversion'],
        'keyInsights': [
            f"{sentiment.capitalize()} initial response",
            f"{traits[0] if traits else 'General'} alignment",
            f"{metrics['conversion']}/10 conversion potential"
        ]
    }

def get_audience_profiles(analysis_data: Optional[Dict] = None) -> List[Dict]:
    """
    Get the audience profiles for simulation from session state.
    
    Args:
        analysis_data: Optional RFP analysis data
    
    Returns:
        List[Dict]: List of audience profiles
    """
    import streamlit as st
    
    profiles = []
    
    # First, add the core audience if available
    if 'audience_summary' in st.session_state and st.session_state.audience_summary:
        core_audience = st.session_state.audience_summary.get('core_audience', '')
        primary_audience = st.session_state.audience_summary.get('primary_audience', '')
        
        if core_audience:
            # Extract key characteristics from the core audience description
            traits = []
            
            # Try to extract some traits from the description
            if 'professional' in core_audience.lower():
                traits.append('Professional focus')
            if 'decision' in core_audience.lower():
                traits.append('Decision makers')
            if 'strategic' in core_audience.lower():
                traits.append('Strategic mindset')
            if 'quality' in core_audience.lower():
                traits.append('Quality conscious')
            
            # Add industry/brand context if available
            if 'brand_name' in st.session_state:
                traits.append(f"{st.session_state.brand_name} aligned")
            
            # Ensure we have at least 4 traits
            default_core_traits = ['Results oriented', 'Performance driven', 'ROI focused', 'Value seeking']
            while len(traits) < 4 and default_core_traits:
                traits.append(default_core_traits.pop(0))
            
            # Create core audience profile with correct ID
            core_profile = {
                'id': 'rfp-core-audience',
                'name': 'RFP Core Audience',
                'description': core_audience[:100] if len(core_audience) > 100 else core_audience,
                'traits': traits[:4],
                'icon': '🎯',
                'color': 'red',
                'is_core': True
            }
            profiles.append(core_profile)
    
    # Check if we have audience segments in session state
    if 'audience_segments' in st.session_state and st.session_state.audience_segments:
        segments_data = st.session_state.audience_segments
        
        if 'segments' in segments_data and isinstance(segments_data['segments'], list):
            segment_list = segments_data['segments']
            
            # Define icons for each audience type (skip first one since core uses it)
            icons = ['📱', '✈️', '☕', '🌟', '🎨', '🏆']
            colors = ['green', 'purple', 'orange', 'blue', 'yellow', 'gray']
            
            # Process each segment (limit based on how many slots we have left)
            max_segments = 4 - len(profiles)  # Account for core audience if added
            for idx, segment in enumerate(segment_list[:max_segments]):
                # Extract traits from targeting parameters and interests
                traits = []
                
                # Add interests as traits
                if 'interest_categories' in segment:
                    # Take up to 2 interests
                    interests = segment['interest_categories'][:2]
                    traits.extend(interests)
                
                # Add demographic traits
                targeting_params = segment.get('targeting_params', {})
                if 'age_range' in targeting_params:
                    traits.append(f"Age {targeting_params['age_range']}")
                if 'income_targeting' in targeting_params:
                    income = targeting_params['income_targeting']
                    # Shorten income description if too long
                    if len(income) > 20:
                        income = income.split(',')[0]  # Take first part
                    traits.append(income)
                if 'education_targeting' in targeting_params and len(traits) < 4:
                    traits.append(targeting_params['education_targeting'])
                
                # Add platform preferences if we still need traits
                if len(traits) < 4 and 'platform_targeting' in segment:
                    platforms = segment['platform_targeting']
                    if platforms and isinstance(platforms, list):
                        for platform in platforms[:2]:  # Take up to 2 platforms
                            if 'platform' in platform and len(traits) < 4:
                                traits.append(f"{platform['platform']} user")
                
                # Ensure we have at least 4 traits
                default_traits = ['Strategic focus', 'Quality conscious', 'Results oriented', 'Value driven']
                while len(traits) < 4:
                    if default_traits:
                        traits.append(default_traits.pop(0))
                
                # Create profile with proper description
                description = segment.get('description', '')
                if not description and 'targeting_params' in segment:
                    # Build description from targeting params
                    params = segment['targeting_params']
                    desc_parts = []
                    if 'age_range' in params:
                        desc_parts.append(params['age_range'])
                    if 'gender_targeting' in params and params['gender_targeting'] != 'All':
                        desc_parts.append(params['gender_targeting'])
                    description = ', '.join(desc_parts) if desc_parts else 'Target audience segment'
                
                # Map index to correct IDs
                id_mapping = {
                    0: 'growth-audience-1',
                    1: 'growth-audience-2',
                    2: 'emerging-audience'
                }
                
                # Create profile
                profile = {
                    'id': id_mapping.get(idx, f'audience-{idx}'),
                    'name': segment.get('name', f'Audience Segment {idx + 1}'),
                    'description': description[:100],  # Limit description length
                    'traits': traits[:4],  # Limit to 4 traits
                    'icon': icons[idx % len(icons)],
                    'color': colors[idx % len(colors)],
                    'segment_data': segment  # Store original segment data for reference
                }
                profiles.append(profile)
            
            # If we have profiles from session state, return them
            if profiles:
                return profiles
    
    # Fallback to default profiles if no segments in session state
    return [
        {
            'id': 'rfp-core-audience',
            'name': 'RFP Core Audience',
            'description': f"{analysis_data.get('keyAudience', 'Primary Target')} - {analysis_data.get('industry', 'Professional')}" if analysis_data else 'Primary RFP Target Audience',
            'traits': [
                f"{analysis_data.get('industry', 'Industry')} focused" if analysis_data else 'Strategic decision makers',
                'Decision makers',
                'Strategic buyers',
                'Performance driven'
            ],
            'icon': '🎯',
            'color': 'gray'
        },
        {
            'id': 'growth-audience-1',
            'name': 'Growth Audience 1 – Urban Explorers',
            'description': 'Tech-Forward, Values Sustainability',
            'traits': ['Innovation-driven', 'Environmental consciousness', 'Digital natives', 'Urban lifestyle'],
            'icon': '📱',
            'color': 'green'
        },
        {
            'id': 'growth-audience-2',
            'name': 'Growth Audience 2 – Global Nomads',
            'description': 'Luxury-Lifestyle Driven, Health-Conscious',
            'traits': ['Premium experiences', 'Wellness-focused', 'Location independence', 'Quality over quantity'],
            'icon': '✈️',
            'color': 'purple'
        },
        {
            'id': 'emerging-audience',
            'name': 'Emerging Audience 3 – Cultural Enthusiasts',
            'description': 'Budget-Conscious, Experience Seekers',
            'traits': ['Cultural immersion', 'Value-oriented', 'Authentic experiences', 'Social connection'],
            'icon': '☕',
            'color': 'orange'
        }
    ]
