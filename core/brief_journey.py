"""
Brief Journey Generation module for creating consumer journey maps from marketing briefs.
This module provides AI-powered analysis to generate tactical journey strategies.
"""
import os
import json
from typing import Dict, List, Optional, TypedDict
from openai import OpenAI

# Initialize the OpenAI client with the API key from environment variables
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class JourneyStageContent(TypedDict):
    """Content structure for each journey stage"""
    objective: str
    targetingStrategies: List[str]
    creativeConcepts: List[str]
    advertisingSolutions: List[str]
    contextInsight: str
    marketSignals: Optional[List[str]]


class BriefJourneyData(TypedDict):
    """Complete brief journey analysis structure"""
    industry: str
    audience: str
    stages: Dict[str, JourneyStageContent]
    generatedAt: str


def generate_journey_from_brief(
    brief_content: str,
    industry: Optional[str] = None,
    target_audience: Optional[str] = None
) -> BriefJourneyData:
    """
    Generate a complete 5-stage consumer journey map from a marketing brief.

    Args:
        brief_content: The full text content of the marketing brief
        industry: Optional industry context (will be detected from brief if not provided)
        target_audience: Optional target audience (will be extracted from brief if not provided)

    Returns:
        BriefJourneyData: Complete journey map with all 5 stages (AWARENESS, CONSIDERATION,
                          INTENT, CONVERSION, LOYALTY) and tactical recommendations

    Raises:
        Exception: If OpenAI API call fails or response cannot be parsed
    """
    # Truncate brief content if too long (keep first 10,000 characters to avoid token limits)
    truncated_brief = (
        brief_content[:10000] + '...[truncated for processing]'
        if len(brief_content) > 10000
        else brief_content
    )

    prompt = f"""You are a marketing strategist analyzing a client brief to create a detailed consumer journey map.

BRIEF CONTENT:
{truncated_brief}

DETECTED INDUSTRY: {industry or 'General'}
TARGET AUDIENCE: {target_audience or 'Not specified'}

TASK: Generate a complete 5-stage consumer journey (Awareness → Consideration → Intent → Conversion → Loyalty) with specific tactical recommendations for each stage.

For EACH of the 5 stages, provide:
1. **Objective**: What the marketing goal is at this stage (1-2 sentences)
2. **Targeting Strategies**: 4 specific programmatic targeting approaches (use in-market audiences, affinity audiences, behavioral targeting, contextual targeting, CRM segmentation, geographic targeting, custom intent audiences, lookalike audiences - NO specific publisher names)
3. **Creative Concepts**: 4 specific messaging themes or creative approaches
4. **Advertising Solutions**: 4 specific tactical media recommendations (reference platform types like "streaming video platforms", "social media", "programmatic display", "search advertising" - NO specific publisher names like YouTube, Meta, Google)
5. **Context Insight**: 1 data-driven insight about this stage with a realistic source citation (format: "Key insight here (Source - Date)")
6. **Market Signals**: 3 relevant market trends or data points that influence this stage

IMPORTANT GUIDELINES:
- Base everything on the actual brief content provided
- Use programmatic advertising terminology (NO publisher names)
- Be industry-specific based on the brief
- Cite realistic sources like industry reports, research firms, trade publications
- Make it tactical and actionable, not generic

Return a JSON object with this structure:
{{
  "industry": "detected industry from brief",
  "audience": "target audience from brief",
  "stages": {{
    "AWARENESS": {{
      "objective": "...",
      "targetingStrategies": ["...", "...", "...", "..."],
      "creativeConcepts": ["...", "...", "...", "..."],
      "advertisingSolutions": ["...", "...", "...", "..."],
      "contextInsight": "Insight with source (Source Name - Month Year)",
      "marketSignals": ["Signal 1", "Signal 2", "Signal 3"]
    }},
    "CONSIDERATION": {{ ... }},
    "INTENT": {{ ... }},
    "CONVERSION": {{ ... }},
    "LOYALTY": {{ ... }}
  }}
}}"""

    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an expert marketing strategist specializing in consumer journey mapping and programmatic advertising strategy. Provide tactical, data-driven recommendations based on client briefs.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            response_format={'type': 'json_object'},
            temperature=0.4,
            max_tokens=4000,
        )

        content = response.choices[0].message.content
        if not content:
            raise Exception('No response from OpenAI')

        parsed_response = json.loads(content)

        # Add timestamp
        from datetime import datetime
        parsed_response['generatedAt'] = datetime.now().isoformat()

        return parsed_response

    except Exception as error:
        print(f'Error generating journey from brief: {error}')
        raise error
