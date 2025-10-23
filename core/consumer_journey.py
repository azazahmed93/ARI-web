"""
Consumer Journey Generation module for creating comprehensive 9-stage consumer journey maps.
This module provides AI-powered analysis to generate tactical journey strategies across all phases.
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


class ConsumerJourneyStages(TypedDict):
    """All 9 consumer journey stages"""
    DREAM: JourneyStageContent
    FAMILIARIZE: JourneyStageContent
    CONSIDER: JourneyStageContent
    EXPLORE: JourneyStageContent
    NARROW: JourneyStageContent
    PURCHASE: JourneyStageContent
    ONBOARD: JourneyStageContent
    REVEL: JourneyStageContent
    COAST: JourneyStageContent


class AudienceJourneyData(TypedDict):
    """Journey data for a specific audience segment"""
    name: str
    description: str
    stages: ConsumerJourneyStages


class AudiencesData(TypedDict):
    """All four audience segments"""
    core: AudienceJourneyData
    growth1: AudienceJourneyData
    growth2: AudienceJourneyData
    emerging: AudienceJourneyData


class AudienceOverlapItem(TypedDict):
    """Overlap analysis between two audience segments"""
    audiences: str
    audienceIds: List[str]
    overlap: int
    insight: str


class ConsumerJourneyData(TypedDict):
    """Complete consumer journey analysis structure with 9 stages and multiple audiences"""
    industry: str
    audiences: AudiencesData
    audienceOverlaps: List[AudienceOverlapItem]
    strategicRecommendation: str


def generate_consumer_journey_from_brief(
    brief_content: str,
    industry: Optional[str] = None,
    audience_core: Optional[str] = None,
    audience_growth1: Optional[str] = None,
    audience_growth2: Optional[str] = None,
    audience_emerging: Optional[str] = None
) -> ConsumerJourneyData:
    """
    Generate comprehensive 9-stage consumer journey maps for 4 different audience segments from a marketing brief.

    Args:
        brief_content: The full text content of the marketing brief
        industry: Optional industry context (will be detected from brief if not provided)
        audience_core: Core target audience name
        audience_growth1: Growth segment 1 audience name
        audience_growth2: Growth segment 2 audience name
        audience_emerging: Emerging audience name

    Returns:
        ConsumerJourneyData: Complete journey maps for 4 audiences (core, growth1, growth2, emerging),
                            each with all 9 stages (DREAM through COAST)

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
        'core': audience_core or 'Core Target Audience',
        'growth1': audience_growth1 or 'Primary Growth Segment',
        'growth2': audience_growth2 or 'Secondary Growth Segment',
        'emerging': audience_emerging or 'Emerging Opportunity Segment'
    }

    prompt = f"""You are a marketing strategist analyzing a client brief to create detailed 9-stage consumer journey maps for FOUR specific audience segments.

BRIEF CONTENT:
{truncated_brief}

DETECTED INDUSTRY: {industry or 'General'}

TASK: Generate complete 9-stage consumer journeys for the following 4 SPECIFIC audience segments:

AUDIENCE SEGMENTS (USE THESE EXACT NAMES):
1. **Core**: "{audience_names['core']}"
2. **Growth1**: "{audience_names['growth1']}"
3. **Growth2**: "{audience_names['growth2']}"
4. **Emerging**: "{audience_names['emerging']}"

JOURNEY FRAMEWORK - 9 STAGES ACROSS 3 PHASES:

**PHASE 1: GET IN CONSIDERATION SET**
- DREAM: Initial aspiration and awareness
- FAMILIARIZE: Learning and exploration
- CONSIDER: Active evaluation and comparison

**PHASE 2: WIN THE SHOPPING JOURNEY**
- EXPLORE: Deep research and engagement
- NARROW: Shortlist and decision-making
- PURCHASE: Transaction and conversion

**PHASE 3: MAXIMIZE OWNER VALUE**
- ONBOARD: Initial ownership experience
- REVEL: Satisfaction and enjoyment
- COAST: Long-term retention and loyalty

For EACH audience segment, provide:
- **name**: Use the EXACT audience name provided above
- **description**: Brief description of this specific segment (1 sentence)
- **stages**: All 9 journey stages with unique content tailored to this audience

For EACH of the 9 stages in EACH audience, provide:
1. **objective**: Marketing goal for this audience at this stage (1-2 sentences)
2. **targetingStrategies**: 4 specific programmatic targeting approaches tailored to this audience and stage
3. **creativeConcepts**: 4 messaging themes that resonate with this specific audience at this stage
4. **advertisingSolutions**: 4 tactical media recommendations suited to this audience's behavior at this stage
5. **contextInsight**: 1 data-driven insight with realistic source citation (format: "Insight (Source - Month Year)")
6. **marketSignals**: 3 relevant market trends for this audience at this stage
7. **industryNews**: 2-3 recent industry news items relevant to this audience at this stage, each with:
   - **headline**: News headline (realistic and timely)
   - **impact**: How this news affects marketing strategy for this audience at this stage (1-2 sentences)
   - **source**: News source (e.g., "TechCrunch", "Marketing Week", "AdAge", "Automotive News")
   - **date**: Recent date (format: "Month Year", e.g., "October 2025")

ADDITIONALLY, provide cross-audience overlap analysis:
For ALL 6 audience pair combinations, analyze behavioral and strategic overlaps based on:
- Shared targeting strategies and channel preferences
- Similar creative concepts and messaging themes
- Overlapping media consumption patterns
- Common behavioral characteristics and motivations

Calculate UNIQUE overlap percentages (15-40% range) for each pair based on actual audience similarities:
- **Core × Growth1**: Analyze overlap and provide consolidation opportunity
- **Core × Growth2**: Analyze overlap and provide strategic insight
- **Core × Emerging**: Analyze overlap and provide opportunity
- **Growth1 × Growth2**: Analyze overlap and provide efficiency potential
- **Growth1 × Emerging**: Analyze overlap and provide unified strategy
- **Growth2 × Emerging**: Analyze overlap and provide messaging consolidation

For EACH overlap, provide:
- **audiences**: Display name (e.g., "Tech Enthusiasts × Early Adopters")
- **audienceIds**: Array of audience keys (e.g., ["core", "growth1"])
- **overlap**: DYNAMICALLY CALCULATED integer percentage based on actual audience analysis (15-40 range)
- **insight**: Specific tactical recommendation based on the calculated overlap percentage (1-2 sentences with actionable consolidation strategy)

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
- Stage content should evolve logically across the 9-stage journey
- DREAM stage focuses on aspiration, COAST stage focuses on loyalty and retention

Return a JSON object with this EXACT structure (use the EXACT audience names specified above):
{{
  "industry": "detected industry from brief",
  "audiences": {{
    "core": {{
      "name": "{audience_names['core']}",
      "description": "Brief description of this segment",
      "stages": {{
        "DREAM": {{
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
        "FAMILIARIZE": {{ ... same structure ... }},
        "CONSIDER": {{ ... same structure ... }},
        "EXPLORE": {{ ... same structure ... }},
        "NARROW": {{ ... same structure ... }},
        "PURCHASE": {{ ... same structure ... }},
        "ONBOARD": {{ ... same structure ... }},
        "REVEL": {{ ... same structure ... }},
        "COAST": {{ ... same structure ... }}
      }}
    }},
    "growth1": {{
      "name": "{audience_names['growth1']}",
      "description": "Brief description",
      "stages": {{ ... all 9 stages with unique content ... }}
    }},
    "growth2": {{
      "name": "{audience_names['growth2']}",
      "description": "Brief description",
      "stages": {{ ... all 9 stages with unique content ... }}
    }},
    "emerging": {{
      "name": "{audience_names['emerging']}",
      "description": "Brief description",
      "stages": {{ ... all 9 stages with unique content ... }}
    }}
  }},
  "audienceOverlaps": [
    {{
      "audiences": "{audience_names['core']} × {audience_names['growth1']}",
      "audienceIds": ["core", "growth1"],
      "overlap": <calculate based on targeting/creative/channel similarities>,
      "insight": "Specific tactical recommendation based on overlap analysis"
    }},
    {{
      "audiences": "{audience_names['core']} × {audience_names['growth2']}",
      "audienceIds": ["core", "growth2"],
      "overlap": <calculate based on audience analysis>,
      "insight": "Specific tactical recommendation based on overlap analysis"
    }},
    {{
      "audiences": "{audience_names['core']} × {audience_names['emerging']}",
      "audienceIds": ["core", "emerging"],
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
                    'content': 'You are an expert marketing strategist specializing in comprehensive consumer journey mapping and programmatic advertising strategy. You excel at identifying distinct audience segments and creating tailored 9-stage journey strategies for each. Provide tactical, data-driven recommendations based on client briefs.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            response_format={'type': 'json_object'},
            temperature=0.4,
            max_tokens=16384,  # Increased for 4 audiences × 9 stages each
        )

        content = response.choices[0].message.content
        if not content:
            raise Exception('No response from OpenAI')

        parsed_response = json.loads(content)

        return parsed_response

    except Exception as error:
        print(f'Error generating consumer journey from brief: {error}')
        raise error
