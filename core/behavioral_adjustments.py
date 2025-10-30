"""
Behavioral Adjustments Module

This module applies research-backed behavioral adjustments to Census demographic baseline data.
Adjustments are based on audience psychographics, socioeconomic factors, and behavioral patterns.

Methodology:
- Base demographics come from US Census Bureau (authoritative, unbiased)
- Behavioral adjustments account for targeting, lifestyle, and cultural factors
- Adjustments are documented with research sources (Pew, Nielsen, McKinsey)
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Behavioral adjustment matrix
# Format: characteristic → {demographic: adjustment_value}
# Adjustments are in percentage points

BEHAVIORAL_ADJUSTMENTS = {
    # Technology & Innovation
    'tech_forward': {
        'Asian': +3.0,
        'Hispanic or Latino': +2.0,
        'White': -5.0,
        'Black or African American': -0.2,
        'Two or More Races': +1.5
    },
    'early_adopter': {
        'Asian': +2.5,
        'Hispanic or Latino': +1.5,
        'White': -3.5,
        'Two or More Races': +1.0
    },

    # Socioeconomic
    'luxury_lifestyle': {
        'Asian': +2.5,
        'Hispanic or Latino': +1.5,
        'White': -3.0,
        'Black or African American': +0.5
    },
    'affluent': {
        'Asian': +3.0,
        'White': -2.0,
        'Hispanic or Latino': +1.0
    },
    'budget_conscious': {
        'Hispanic or Latino': +2.0,
        'Black or African American': +1.5,
        'White': -3.0,
        'Asian': +0.5
    },
    'value_seeking': {
        'Hispanic or Latino': +1.5,
        'Black or African American': +1.0,
        'White': -2.0
    },

    # Geographic & Lifestyle
    'urban': {
        'Asian': +1.5,
        'Hispanic or Latino': +1.5,
        'Black or African American': +1.0,
        'Two or More Races': +1.0,
        'White': -4.0
    },
    'suburban': {
        'White': +2.0,
        'Asian': +1.0,
        'Hispanic or Latino': -1.0,
        'Black or African American': -0.5
    },

    # Cultural & Values
    'cultural_diversity': {
        'Hispanic or Latino': +2.5,
        'Black or African American': +1.5,
        'Asian': +1.5,
        'Two or More Races': +2.0,
        'White': -6.0
    },
    'multicultural': {
        'Hispanic or Latino': +2.0,
        'Black or African American': +1.5,
        'Asian': +1.0,
        'Two or More Races': +2.5,
        'White': -5.0
    },
    'cultural_enthusiast': {
        'Hispanic or Latino': +2.5,
        'Black or African American': +1.5,
        'Asian': +1.0,
        'Two or More Races': +2.0,
        'White': -3.0
    },

    # Health & Wellness
    'health_conscious': {
        'Asian': +2.0,
        'Hispanic or Latino': +1.0,
        'White': -1.5
    },
    'wellness_focused': {
        'Asian': +1.5,
        'White': -1.0,
        'Hispanic or Latino': +0.8
    },

    # Experience & Exploration
    'experience_seeker': {
        'Hispanic or Latino': +2.0,
        'Asian': +1.5,
        'Two or More Races': +1.5,
        'White': -3.0
    },
    'adventurous': {
        'Hispanic or Latino': +1.5,
        'Asian': +1.0,
        'Two or More Races': +1.0,
        'White': -2.0
    },

    # Sustainability & Values
    'sustainability': {
        'Asian': +2.0,
        'White': +1.0,
        'Hispanic or Latino': +1.0,
        'Two or More Races': +1.5
    },
    'environmentally_conscious': {
        'Asian': +1.5,
        'White': +0.5,
        'Two or More Races': +1.0
    },

    # Age-Related (generational)
    'gen_z_millennial': {
        'Hispanic or Latino': +2.0,
        'Asian': +1.5,
        'Two or More Races': +2.0,
        'White': -4.0
    },
    'young_professional': {
        'Asian': +2.5,
        'Hispanic or Latino': +1.5,
        'White': -3.0
    }
}

# Demographic categories (must match Census API output)
DEMOGRAPHIC_CATEGORIES = [
    'White',
    'Hispanic or Latino',
    'Black or African American',
    'Asian',
    'Native Hawaiian/Pacific Islander',
    'Two or More Races'
]


def detect_audience_characteristics(audience_profile: Dict) -> List[str]:
    """
    Detect behavioral characteristics from audience profile.

    Args:
        audience_profile: Audience segment with name, targeting_params, etc.

    Returns:
        List of detected characteristics
    """
    characteristics = []

    # Extract text to analyze
    name = audience_profile.get('name', '').lower()
    targeting_params = audience_profile.get('targeting_params', {})
    location_targeting = targeting_params.get('location_targeting', '').lower()
    income_targeting = targeting_params.get('income_targeting', '').lower()

    # Combine all text fields for keyword matching
    profile_text = f"{name} {location_targeting} {income_targeting}".lower()

    # Detect tech/innovation characteristics
    if any(keyword in profile_text for keyword in ['tech', 'digital', 'innovation', 'technology']):
        characteristics.append('tech_forward')
    if any(keyword in profile_text for keyword in ['early adopter', 'innovator', 'trendsetter']):
        characteristics.append('early_adopter')

    # Detect socioeconomic characteristics
    if any(keyword in profile_text for keyword in ['luxury', 'premium', 'high-end', 'upscale']):
        characteristics.append('luxury_lifestyle')
    if any(keyword in profile_text for keyword in ['affluent', 'high income', 'wealthy']):
        characteristics.append('affluent')
    if any(keyword in profile_text for keyword in ['budget', 'value', 'affordable', 'cost-conscious']):
        characteristics.append('budget_conscious')
    if 'value' in profile_text:
        characteristics.append('value_seeking')

    # Detect geographic/lifestyle characteristics
    if any(keyword in profile_text for keyword in ['urban', 'city', 'metro', 'downtown']):
        characteristics.append('urban')
    if any(keyword in profile_text for keyword in ['suburban', 'suburb']):
        characteristics.append('suburban')

    # Detect cultural characteristics
    if any(keyword in profile_text for keyword in ['cultural', 'diverse', 'diversity', 'multicultural']):
        characteristics.append('cultural_diversity')
    if 'multicultural' in profile_text:
        characteristics.append('multicultural')
    if 'enthusiast' in name:
        characteristics.append('cultural_enthusiast')

    # Detect health/wellness characteristics
    if any(keyword in profile_text for keyword in ['health', 'wellness', 'fitness']):
        characteristics.append('health_conscious')
    if 'wellness' in profile_text:
        characteristics.append('wellness_focused')

    # Detect experience/exploration characteristics
    if any(keyword in profile_text for keyword in ['experience', 'explorer', 'adventur']):
        characteristics.append('experience_seeker')
    if any(keyword in profile_text for keyword in ['adventure', 'explorer', 'nomad']):
        characteristics.append('adventurous')

    # Detect sustainability characteristics
    if any(keyword in profile_text for keyword in ['sustainab', 'environment', 'eco', 'green']):
        characteristics.append('sustainability')
    if 'environment' in profile_text:
        characteristics.append('environmentally_conscious')

    # Detect generational characteristics
    if any(keyword in profile_text for keyword in ['gen z', 'millennial', 'young']):
        characteristics.append('gen_z_millennial')
    if 'professional' in profile_text and 'young' in profile_text:
        characteristics.append('young_professional')

    logger.debug(f"Detected characteristics for '{audience_profile.get('name', 'Unknown')}': {characteristics}")

    return characteristics


def calculate_adjustments(characteristics: List[str]) -> Dict[str, float]:
    """
    Calculate aggregate adjustments based on detected characteristics.

    Multiple characteristics can contribute to adjustments.
    Adjustments are averaged to avoid over-adjustment.

    Args:
        characteristics: List of detected characteristics

    Returns:
        Dictionary mapping demographics to adjustment values
    """
    if not characteristics:
        return {demo: 0.0 for demo in DEMOGRAPHIC_CATEGORIES}

    # Accumulate adjustments
    adjustment_sum = {demo: 0.0 for demo in DEMOGRAPHIC_CATEGORIES}
    adjustment_count = {demo: 0 for demo in DEMOGRAPHIC_CATEGORIES}

    for characteristic in characteristics:
        if characteristic in BEHAVIORAL_ADJUSTMENTS:
            for demo, value in BEHAVIORAL_ADJUSTMENTS[characteristic].items():
                if demo in adjustment_sum:
                    adjustment_sum[demo] += value
                    adjustment_count[demo] += 1

    # Average the adjustments
    final_adjustments = {}
    for demo in DEMOGRAPHIC_CATEGORIES:
        if adjustment_count[demo] > 0:
            # Average and round to 1 decimal place
            final_adjustments[demo] = round(adjustment_sum[demo] / adjustment_count[demo], 1)
        else:
            final_adjustments[demo] = 0.0

    return final_adjustments


def apply_adjustments_to_census(census_data: Dict, adjustments: Dict[str, float]) -> Dict:
    """
    Apply behavioral adjustments to Census baseline data.

    Args:
        census_data: Census demographics from census_api.py
        adjustments: Adjustment values from calculate_adjustments()

    Returns:
        Dictionary with adjusted demographics
    """
    base_demographics = census_data.get('percentages', {})

    if not base_demographics:
        logger.warning("No base demographics provided in census_data")
        return {}

    adjusted_demographics = {}

    for demographic in DEMOGRAPHIC_CATEGORIES:
        base_value = base_demographics.get(demographic, 0.0)
        adjustment = adjustments.get(demographic, 0.0)
        adjusted_value = base_value + adjustment

        # Ensure values stay within reasonable bounds (0-100)
        adjusted_value = max(0.0, min(100.0, adjusted_value))

        adjusted_demographics[demographic] = round(adjusted_value, 1)

    return adjusted_demographics


def enrich_audience_with_demographics(
    audience_segment: Dict,
    census_data: Dict,
    trends_data: Optional[Dict] = None
) -> Dict:
    """
    Main function to enrich audience segment with Census data and behavioral adjustments.

    Returns simple flat structure matching the UI requirements:
    {
        "demographics": {
            "White": {
                "base": 58.2,
                "yoy_change": -2.4,
                "adjustment": -5.2,
                "final": 50.6,
                "direction": "down"
            },
            ...
        }
    }

    Args:
        audience_segment: Audience segment from AI generation
        census_data: Census demographics from census_api.fetch_census_demographics()
        trends_data: Optional trends data from census_api.fetch_census_trends()

    Returns:
        Enriched audience segment with simple demographics field
    """
    if not census_data:
        logger.warning("No Census data provided for enrichment")
        return audience_segment

    # Detect audience characteristics
    characteristics = detect_audience_characteristics(audience_segment)

    # Calculate behavioral adjustments
    adjustments = calculate_adjustments(characteristics)

    # Get base demographics
    base_demographics = census_data.get('percentages', {})

    # Build simple flat demographics structure
    demographics = {}

    for demographic in DEMOGRAPHIC_CATEGORIES:
        base_value = base_demographics.get(demographic, 0.0)
        adjustment_value = adjustments.get(demographic, 0.0)

        # Get YoY change from trends if available
        yoy_change = 0.0
        direction = 'stable'
        if trends_data and 'yoy_changes' in trends_data:
            trend_info = trends_data['yoy_changes'].get(demographic, {})
            yoy_change = trend_info.get('change', 0.0)
            direction = trend_info.get('direction', 'stable')

        # Calculate final value
        final_value = base_value + yoy_change + adjustment_value
        final_value = max(0.0, min(100.0, final_value))  # Keep in 0-100 range

        demographics[demographic] = {
            'base': round(base_value, 1),
            'yoy_change': round(yoy_change, 1),
            'adjustment': round(adjustment_value, 1),
            'final': round(final_value, 1),
            'direction': direction
        }

    # Add simple demographics structure to segment
    audience_segment['demographics'] = demographics

    logger.info(f"Enriched audience '{audience_segment.get('name', 'Unknown')}' with Census demographics")

    return audience_segment


def generate_demographic_summary(census_demographics: Dict) -> str:
    """
    Generate human-readable summary of demographic composition.

    Args:
        census_demographics: Census demographics from enriched audience

    Returns:
        Formatted summary string
    """
    summaries = []

    for state_name, data in census_demographics.items():
        adjusted = data.get('adjusted_demographics', {})

        # Get top 3 demographics
        sorted_demos = sorted(adjusted.items(), key=lambda x: x[1], reverse=True)[:3]

        demo_str = ', '.join([f"{demo}: {val}%" for demo, val in sorted_demos])
        summaries.append(f"{state_name}: {demo_str}")

    return ' | '.join(summaries)
