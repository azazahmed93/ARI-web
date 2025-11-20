"""
Language Recommendations Module

This module generates advertising language recommendations based on
demographic composition of audience segments, using AI-powered analysis
of US Census language data and research-backed insights.
"""

import logging
import json
from typing import Dict, List, Optional
from core.ai_utils import make_openai_request

logger = logging.getLogger(__name__)


def generate_language_recommendations(audience_segment: Dict) -> List[Dict]:
    """
    Generate AI-powered language recommendations based on segment demographics.

    Analyzes the demographic composition and uses OpenAI to generate
    research-backed language usage recommendations for advertising campaigns.

    Args:
        audience_segment: Enriched audience segment with demographics field

    Returns:
        List of language recommendation profiles for relevant demographics
    """
    demographics = audience_segment.get('demographics', {})

    if not demographics:
        logger.warning(f"No demographics found for segment '{audience_segment.get('name')}'")
        return []

    try:
        # Build context for AI
        audience_name = audience_segment.get('name', 'Unknown Audience')
        audience_description = audience_segment.get('description', '')

        # Extract significant demographics (>5% of audience)
        significant_demographics = {
            demo: data for demo, data in demographics.items()
            if data.get('final', 0.0) > 5.0
        }

        if not significant_demographics:
            logger.info(f"No significant demographics (>5%) found for '{audience_name}'")
            return []

        # Create prompt for OpenAI
        prompt = f"""You are a linguistic and demographic research analyst specializing in multilingual advertising strategies.

Audience Profile:
- Name: {audience_name}
- Description: {audience_description}

Demographics Composition (% of audience):
{json.dumps(significant_demographics, indent=2)}

Based on US Census Bureau language data and research patterns, generate language recommendations for advertising to this audience.

For EACH demographic group that represents >5% of the audience, provide:
1. The demographic name (exactly as shown above)
2. Their percentage of the total audience
3. Language breakdown with:
   - Language name
   - Percentage of that demographic speaking this language
   - Research-backed description citing US Census data
   - A hex color code for visualization

Use these research patterns:
- Hispanic or Latino: ~68% Spanish-speaking households, ~32% English-only (US Census Bureau)
- Asian: ~75% heritage languages (Chinese, Tagalog, Vietnamese, Korean, Hindi, etc.), ~25% English-only
- Two or More Races: ~55% bilingual/multilingual households, ~45% English-only
- Black or African American: ~95% English, ~5% African/Caribbean heritage languages
- White: ~95% English, ~5% European heritage languages

Important guidelines:
- Only include demographics that are present in the audience composition
- Percentages within each demographic's languages should sum to 100%
- Use realistic US Census-based data
- Provide clear, actionable descriptions for marketers
- Use distinct, accessible colors for visualization

Return ONLY valid JSON in this exact format:
[
  {{
    "demographic": "Hispanic or Latino",
    "audiencePercentage": 21.1,
    "languages": [
      {{
        "language": "Spanish",
        "percentage": 68,
        "description": "US Census data shows ~68% of Hispanic/Latino households speak Spanish at home",
        "color": "#10b981"
      }},
      {{
        "language": "English",
        "percentage": 32,
        "description": "Remaining ~32% are English-only or bilingual households",
        "color": "#3b82f6"
      }}
    ]
  }}
]

Generate language recommendations for ALL demographics present in the composition."""

        # Use make_openai_request utility function
        response = make_openai_request(
            messages=[
                {
                    "role": "system",
                    "content": "You are a linguistic demographics analyst. Return only valid JSON with language recommendations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=1500
        )

        if not response:
            logger.error("Failed to get response from OpenAI for language recommendations")
            return []

        # Parse response
        recommendations_json = response.get('content', '').strip()

        # Remove markdown code blocks if present
        if recommendations_json.startswith('```'):
            recommendations_json = recommendations_json.split('```')[1]
            if recommendations_json.startswith('json'):
                recommendations_json = recommendations_json[4:]
            recommendations_json = recommendations_json.strip()

        language_recommendations = json.loads(recommendations_json)

        # Validate and sort by audience percentage
        valid_recommendations = []
        for rec in language_recommendations:
            if rec.get('demographic') and rec.get('languages'):
                valid_recommendations.append(rec)

        valid_recommendations.sort(key=lambda x: x.get('audiencePercentage', 0), reverse=True)

        logger.info(
            f"Generated {len(valid_recommendations)} language recommendations "
            f"for segment '{audience_name}'"
        )

        return valid_recommendations

    except Exception as e:
        logger.error(f"Error generating language recommendations: {e}")
        return []


def enrich_segment_with_language_recommendations(audience_segment: Dict) -> Dict:
    """
    Add AI-generated language recommendations to an audience segment.

    This should be called after demographic enrichment has been applied.

    Args:
        audience_segment: Audience segment with demographics field

    Returns:
        Segment with languageRecommendations field added
    """
    if 'demographics' not in audience_segment:
        logger.warning(
            f"Segment '{audience_segment.get('name')}' missing demographics field. "
            "Skipping language recommendations."
        )
        return audience_segment

    language_recommendations = generate_language_recommendations(audience_segment)

    if language_recommendations:
        audience_segment['languageRecommendations'] = language_recommendations
        logger.info(
            f"Enriched segment '{audience_segment.get('name')}' with "
            f"{len(language_recommendations)} language recommendations"
        )
    else:
        logger.debug(
            f"No language recommendations generated for segment '{audience_segment.get('name')}'"
        )

    return audience_segment
