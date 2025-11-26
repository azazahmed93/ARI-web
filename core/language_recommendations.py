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

Analyze the audience name and description above to infer contextual factors, then generate DYNAMIC language recommendations. Language usage varies significantly based on:

**Key Variation Factors:**
1. **Generation/Age**: Younger generations (Gen Z, Millennials) trend more English-dominant; older generations maintain heritage languages more strongly
2. **Geographic Region**: Border states (TX, CA, AZ, NM, FL) have higher heritage language retention; Midwest/Northeast varies by metro area
3. **Urbanicity**: Major metros have higher multilingual populations; rural areas vary by region
4. **Income/Education**: Higher education correlates with bilingualism; varies by community
5. **Acculturation Level**: Recent immigrants vs. 2nd/3rd generation Americans show different patterns

**US Census Reference Ranges (adjust based on context above):**
- Hispanic/Latino: Spanish 45-78% (higher in border states, older demos; lower in Midwest, younger demos)
- Asian: Heritage languages 55-85% (varies greatly by specific ethnicity and generation)
- Two or More Races: Multilingual 35-65% (depends on specific heritage mix)
- Black/African American: English 88-97%, heritage languages 3-12% (higher in immigrant communities)
- White: English 90-98%, heritage languages 2-10% (varies by European origin, region)

For EACH demographic group >5% of audience, provide:
1. The demographic name (exactly as shown in composition)
2. Their percentage of the total audience
3. Language breakdown with contextually-adjusted percentages based on the audience signals above
4. Brief description explaining WHY this percentage applies to THIS specific audience

Important:
- DO NOT use generic/default percentages - adjust based on audience context
- Percentages within each demographic's languages must sum to 100%
- Provide actionable insights specific to this audience
- Use distinct, accessible colors for visualization

Return ONLY valid JSON:
[
  {{
    "demographic": "Hispanic or Latino",
    "audiencePercentage": 21.1,
    "languages": [
      {{
        "language": "Spanish",
        "percentage": 58,
        "description": "This younger, urban audience in the Midwest shows moderate Spanish retention typical of 2nd-generation households",
        "color": "#10b981"
      }},
      {{
        "language": "English",
        "percentage": 42,
        "description": "Higher English-only rate reflects millennial/Gen-Z acculturation patterns in non-border states",
        "color": "#3b82f6"
      }}
    ]
  }}
]

Generate contextually-appropriate language recommendations for ALL demographics present."""

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
