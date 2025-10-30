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


class IndustryNewsItem(TypedDict):
    """Industry news impact item"""
    headline: str
    impact: str
    source: str
    date: str


class JourneyStageContent(TypedDict):
    """Content structure for each journey stage"""
    objective: str
    targetingStrategies: List[str]
    creativeConcepts: List[str]
    advertisingSolutions: List[str]
    contextInsight: str
    marketSignals: Optional[List[str]]
    industryNews: Optional[List[IndustryNewsItem]]


class JourneyStages(TypedDict):
    """All 5 journey stages"""
    AWARENESS: JourneyStageContent
    CONSIDERATION: JourneyStageContent
    INTENT: JourneyStageContent
    CONVERSION: JourneyStageContent
    LOYALTY: JourneyStageContent


class AudienceJourneyData(TypedDict):
    """Journey data for a specific audience segment"""
    name: str
    description: str
    stages: JourneyStages


class AudiencesData(TypedDict):
    """All four audience segments"""
    primary: AudienceJourneyData
    growth1: AudienceJourneyData
    growth2: AudienceJourneyData
    emerging: AudienceJourneyData


class AudienceOverlapItem(TypedDict):
    """Overlap analysis between two audience segments"""
    audiences: str
    audienceIds: List[str]
    overlap: int
    insight: str


class BriefJourneyData(TypedDict):
    """Complete brief journey analysis structure with multiple audiences"""
    industry: str
    audiences: AudiencesData
    audienceOverlaps: List[AudienceOverlapItem]
    strategicRecommendation: str


def generate_journey_from_brief(
    brief_content: str,
    industry: Optional[str] = None,
    audience_primary: Optional[str] = None,
    audience_growth1: Optional[str] = None,
    audience_growth2: Optional[str] = None,
    audience_emerging: Optional[str] = None
) -> BriefJourneyData:
    """
    Generate consumer journey maps for 4 different audience segments from a marketing brief.

    Args:
        brief_content: The full text content of the marketing brief
        industry: Optional industry context (will be detected from brief if not provided)
        audience_primary: Primary target audience name
        audience_growth1: Growth segment 1 audience name
        audience_growth2: Growth segment 2 audience name
        audience_emerging: Emerging audience name

    Returns:
        BriefJourneyData: Complete journey maps for 4 audiences (primary, growth1, growth2, emerging),
                          each with all 5 stages (AWARENESS, CONSIDERATION, INTENT, CONVERSION, LOYALTY)

    Raises:
        Exception: If OpenAI API call fails or response cannot be parsed
    """
    # Truncate brief content if too long (keep first 10,000 characters to avoid token limits)
    truncated_brief = (
        brief_content[:10000] + '...[truncated for processing]'
        if len(brief_content) > 10000
        else brief_content
    )

    # Build audience names string for prompt
    audience_names = {
        'primary': audience_primary or 'Primary Target Audience',
        'growth1': audience_growth1 or 'Growth Segment 1',
        'growth2': audience_growth2 or 'Growth Segment 2',
        'emerging': audience_emerging or 'Emerging Audience'
    }

    prompt = f"""You are a marketing strategist analyzing a client brief to create detailed consumer journey maps for FOUR specific audience segments.

BRIEF CONTENT:
{truncated_brief}

DETECTED INDUSTRY: {industry or 'General'}

TASK: Generate complete 5-stage consumer journeys for the following 4 SPECIFIC audience segments:

AUDIENCE SEGMENTS (USE THESE EXACT NAMES):
1. **Primary**: "{audience_names['primary']}"
2. **Growth1**: "{audience_names['growth1']}"
3. **Growth2**: "{audience_names['growth2']}"
4. **Emerging**: "{audience_names['emerging']}"

For EACH audience segment, provide:
- **name**: Use the EXACT audience name provided above
- **description**: Brief description of this specific segment (1 sentence)
- **stages**: All 5 journey stages with unique content tailored to this audience

For EACH of the 5 stages in EACH audience, provide:
1. **objective**: Marketing goal for this audience at this stage (1-2 sentences)
2. **targetingStrategies**: 4 specific programmatic targeting approaches tailored to this audience
3. **creativeConcepts**: 4 messaging themes that resonate with this specific audience
4. **advertisingSolutions**: 4 tactical media recommendations suited to this audience's behavior
5. **contextInsight**: 1 data-driven insight with realistic source citation (format: "Insight (Source - Month Year)")
6. **marketSignals**: 3 relevant market trends for this audience
7. **industryNews**: 2-3 recent industry news items relevant to this audience at this stage, each with:
   - **headline**: News headline (realistic and timely)
   - **impact**: How this news affects marketing strategy for THIS SPECIFIC AUDIENCE at this stage (1-2 sentences). CRITICAL: Each audience must have UNIQUE impact descriptions that reflect their distinct characteristics, behaviors, and motivations. Never reuse the same impact text across different audiences, even at the same stage.
   - **source**: News source (e.g., "TechCrunch", "Marketing Week", "AdAge")
   - **date**: Recent date (format: "Month Year", e.g., "October 2025")

ADDITIONALLY, provide cross-audience overlap analysis:
For ALL 6 audience pair combinations, analyze behavioral and strategic overlaps based on:
- Shared targeting strategies and channel preferences
- Similar creative concepts and messaging themes
- Overlapping media consumption patterns
- Common behavioral characteristics and motivations

Calculate UNIQUE overlap percentages (15-40% range) for each pair based on actual audience similarities:
- **Primary × Growth1**: Analyze overlap and provide consolidation opportunity
- **Primary × Growth2**: Analyze overlap and provide strategic insight
- **Primary × Emerging**: Analyze overlap and provide opportunity
- **Growth1 × Growth2**: Analyze overlap and provide efficiency potential
- **Growth1 × Emerging**: Analyze overlap and provide unified strategy
- **Growth2 × Emerging**: Analyze overlap and provide messaging consolidation

For EACH overlap, provide:
- **audiences**: Display name (e.g., "Urban Professionals × Tech Enthusiasts")
- **audienceIds**: Array of audience keys (e.g., ["primary", "growth1"])
- **overlap**: DYNAMICALLY CALCULATED integer percentage based on actual audience analysis (15-40 range, DO NOT use example values)
- **insight**: Specific tactical recommendation based on the calculated overlap percentage (1-2 sentences)

ADDITIONALLY, provide an OVERALL STRATEGIC RECOMMENDATION:
Analyze all 6 audience overlaps and synthesize an executive-level strategic recommendation that:
- Identifies how many audience pairs show significant overlap (30%+ threshold)
- Proposes specific budget consolidation opportunities (e.g., shared creative assets with audience-specific CTAs)
- Quantifies estimated media efficiency gains with realistic percentage ranges (e.g., "18-24% efficiency gain")
- Provides tactical implementation guidance (e.g., "Create single creative master template then deploy 4 CTA variants")
- Keeps recommendation concise (2-4 sentences) but highly actionable and specific to the analyzed audiences

IMPORTANT GUIDELINES:
- Make each audience segment DISTINCT with different behaviors, motivations, and channels
- Base audiences on the brief content and industry context
- Use programmatic advertising terminology (NO publisher names like YouTube, Meta, Google)
- Cite realistic sources like industry reports, research firms, trade publications
- Make it tactical and actionable, not generic
- Ensure content for each audience is unique and tailored to their specific characteristics
- CRITICAL: Each audience must have COMPLETELY UNIQUE content across ALL fields, especially industryNews impacts. Even if audiences are at the same stage, the strategic implications must differ based on each audience's unique characteristics, behaviors, and motivations. Never copy-paste impact descriptions between audiences.

Return a JSON object with this EXACT structure (use the EXACT audience names specified above):
{{
  "industry": "detected industry from brief",
  "audiences": {{
    "primary": {{
      "name": "{audience_names['primary']}",
      "description": "Brief description of this segment",
      "stages": {{
        "AWARENESS": {{
          "objective": "...",
          "targetingStrategies": ["...", "...", "...", "..."],
          "creativeConcepts": ["...", "...", "...", "..."],
          "advertisingSolutions": ["...", "...", "...", "..."],
          "contextInsight": "Insight (Source - Month Year)",
          "marketSignals": ["Signal 1", "Signal 2", "Signal 3"],
          "industryNews": [
            {{
              "headline": "Industry News Headline",
              "impact": "How this affects marketing strategy at this stage for this audience",
              "source": "News Source Name",
              "date": "Month Year"
            }},
            {{
              "headline": "Another Relevant News Item",
              "impact": "Impact on strategy",
              "source": "Source Name",
              "date": "Month Year"
            }}
          ]
        }},
        "CONSIDERATION": {{ ... same structure ... }},
        "INTENT": {{ ... same structure ... }},
        "CONVERSION": {{ ... same structure ... }},
        "LOYALTY": {{ ... same structure ... }}
      }}
    }},
    "growth1": {{
      "name": "{audience_names['growth1']}",
      "description": "Brief description",
      "stages": {{ ... all 5 stages with unique content ... }}
    }},
    "growth2": {{
      "name": "{audience_names['growth2']}",
      "description": "Brief description",
      "stages": {{ ... all 5 stages with unique content ... }}
    }},
    "emerging": {{
      "name": "{audience_names['emerging']}",
      "description": "Brief description",
      "stages": {{ ... all 5 stages with unique content ... }}
    }}
  }},
  "audienceOverlaps": [
    {{
      "audiences": "{audience_names['primary']} × {audience_names['growth1']}",
      "audienceIds": ["primary", "growth1"],
      "overlap": <calculate based on targeting/creative/channel similarities>,
      "insight": "Specific tactical recommendation based on overlap analysis"
    }},
    {{
      "audiences": "{audience_names['primary']} × {audience_names['growth2']}",
      "audienceIds": ["primary", "growth2"],
      "overlap": <calculate based on audience analysis>,
      "insight": "Specific tactical recommendation based on overlap analysis"
    }},
    {{
      "audiences": "{audience_names['primary']} × {audience_names['emerging']}",
      "audienceIds": ["primary", "emerging"],
      "overlap": <calculate unique percentage>,
      "insight": "Specific tactical recommendation based on overlap analysis"
    }},
    {{
      "audiences": "{audience_names['growth1']} × {audience_names['growth2']}",
      "audienceIds": ["growth1", "growth2"],
      "overlap": <analyze and calculate>,
      "insight": "Specific tactical recommendation based on overlap analysis"
    }},
    {{
      "audiences": "{audience_names['growth1']} × {audience_names['emerging']}",
      "audienceIds": ["growth1", "emerging"],
      "overlap": <calculate from audience characteristics>,
      "insight": "Specific tactical recommendation based on overlap analysis"
    }},
    {{
      "audiences": "{audience_names['growth2']} × {audience_names['emerging']}",
      "audienceIds": ["growth2", "emerging"],
      "overlap": <dynamically calculate percentage>,
      "insight": "Specific tactical recommendation based on overlap analysis"
    }}
  ],
  "strategicRecommendation": "Executive summary analyzing overlap patterns and recommending budget consolidation opportunities with specific tactics and estimated efficiency gains (2-4 sentences)"
}}"""

    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an expert marketing strategist specializing in consumer journey mapping and programmatic advertising strategy. You excel at identifying distinct audience segments and creating tailored journey strategies for each. Provide tactical, data-driven recommendations based on client briefs.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            response_format={'type': 'json_object'},
            temperature=0.4,
            max_tokens=16000,  # Increased for 4 audiences × 5 stages each
        )

        content = response.choices[0].message.content
        if not content:
            raise Exception('No response from OpenAI')

        parsed_response = json.loads(content)

        return parsed_response

    except Exception as error:
        print(f'Error generating journey from brief: {error}')
        raise error
