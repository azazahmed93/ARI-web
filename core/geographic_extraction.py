"""
Geographic Extraction Module

This module extracts geographic targeting information from campaign briefs and RFPs.
It uses pattern matching, city/region mapping, and industry defaults to identify target states.
"""

import re
import logging
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# US States (full names and abbreviations)
US_STATES = {
    'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut',
    'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa',
    'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan',
    'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada',
    'new hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina',
    'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island',
    'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont',
    'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming',
    'district of columbia', 'dc'
}

# Major cities to state mapping
CITY_TO_STATE = {
    # California
    'san francisco': 'California', 'los angeles': 'California', 'san diego': 'California',
    'oakland': 'California', 'sacramento': 'California', 'san jose': 'California',
    # New York
    'new york city': 'New York', 'nyc': 'New York', 'brooklyn': 'New York',
    'manhattan': 'New York', 'albany': 'New York', 'buffalo': 'New York',
    # Texas
    'houston': 'Texas', 'dallas': 'Texas', 'austin': 'Texas', 'san antonio': 'Texas',
    'fort worth': 'Texas', 'el paso': 'Texas',
    # Florida
    'miami': 'Florida', 'tampa': 'Florida', 'orlando': 'Florida', 'jacksonville': 'Florida',
    # Illinois
    'chicago': 'Illinois',
    # Pennsylvania
    'philadelphia': 'Pennsylvania', 'pittsburgh': 'Pennsylvania',
    # Arizona
    'phoenix': 'Arizona', 'tucson': 'Arizona',
    # Washington
    'seattle': 'Washington', 'spokane': 'Washington',
    # Massachusetts
    'boston': 'Massachusetts',
    # Nevada
    'las vegas': 'Nevada', 'reno': 'Nevada',
    # Michigan
    'detroit': 'Michigan',
    # Georgia
    'atlanta': 'Georgia',
    # Colorado
    'denver': 'Colorado',
    # Tennessee
    'nashville': 'Tennessee', 'memphis': 'Tennessee',
    # Oregon
    'portland': 'Oregon',
    # Minnesota
    'minneapolis': 'Minnesota',
    # Missouri
    'st louis': 'Missouri', 'kansas city': 'Missouri',
    # Wisconsin
    'milwaukee': 'Wisconsin',
    # North Carolina
    'charlotte': 'North Carolina', 'raleigh': 'North Carolina',
    # Louisiana
    'new orleans': 'Louisiana',
    # Ohio
    'cleveland': 'Ohio', 'columbus': 'Ohio', 'cincinnati': 'Ohio',
}

# US Regions to states mapping
REGION_TO_STATES = {
    'northeast': ['New York', 'Pennsylvania', 'Massachusetts', 'New Jersey', 'Connecticut',
                  'Rhode Island', 'Vermont', 'New Hampshire', 'Maine'],
    'south': ['Texas', 'Florida', 'Georgia', 'North Carolina', 'Virginia', 'Tennessee',
              'Louisiana', 'South Carolina', 'Alabama', 'Kentucky', 'Oklahoma', 'Arkansas',
              'Mississippi', 'West Virginia', 'Maryland', 'Delaware'],
    'midwest': ['Illinois', 'Ohio', 'Michigan', 'Indiana', 'Wisconsin', 'Minnesota',
                'Missouri', 'Iowa', 'Kansas', 'Nebraska', 'South Dakota', 'North Dakota'],
    'west': ['California', 'Washington', 'Oregon', 'Nevada', 'Arizona', 'Colorado',
             'Utah', 'Idaho', 'Montana', 'Wyoming', 'New Mexico', 'Alaska', 'Hawaii'],
    'southeast': ['Florida', 'Georgia', 'North Carolina', 'South Carolina', 'Tennessee',
                  'Alabama', 'Mississippi', 'Louisiana', 'Arkansas', 'Kentucky'],
    'southwest': ['Texas', 'Arizona', 'New Mexico', 'Oklahoma', 'Nevada'],
    'pacific': ['California', 'Washington', 'Oregon', 'Hawaii', 'Alaska'],
    'mountain': ['Colorado', 'Utah', 'Nevada', 'Arizona', 'New Mexico', 'Idaho',
                 'Montana', 'Wyoming'],
}

# Industry-specific default states (ordered by market size)
# Updated to include all 15 industries
INDUSTRY_DEFAULT_STATES = {
    # Original 9 industries
    'technology': ['California', 'Washington', 'Texas', 'New York', 'Massachusetts'],
    'fashion': ['New York', 'California', 'Florida', 'Texas', 'Illinois'],
    'automotive': ['Michigan', 'Texas', 'California', 'Ohio', 'Indiana'],
    'finance': ['New York', 'California', 'Illinois', 'Texas', 'Massachusetts'],
    'entertainment': ['California', 'New York', 'Tennessee', 'Florida', 'Georgia'],
    'healthcare': ['California', 'Texas', 'New York', 'Florida', 'Pennsylvania'],
    'food': ['California', 'Texas', 'Illinois', 'Florida', 'New York'],
    'food & beverage': ['California', 'Texas', 'Illinois', 'Florida', 'New York'],
    'beauty': ['California', 'New York', 'Florida', 'Texas', 'Illinois'],
    'sports': ['California', 'Texas', 'Florida', 'New York', 'Pennsylvania'],
    # New 6 industries
    'home & living': ['California', 'Texas', 'Florida', 'New York', 'North Carolina'],
    'wellness': ['California', 'Colorado', 'New York', 'Florida', 'Arizona'],
    'luxury': ['New York', 'California', 'Florida', 'Texas', 'Nevada'],
    'travel': ['Florida', 'California', 'Nevada', 'Hawaii', 'New York'],
    'retail': ['California', 'Texas', 'New York', 'Florida', 'Illinois'],
    'education': ['California', 'Texas', 'New York', 'Massachusetts', 'Pennsylvania'],
}

# Top 10 states by population (default for national campaigns)
TOP_POPULATION_STATES = [
    'California', 'Texas', 'Florida', 'New York', 'Pennsylvania',
    'Illinois', 'Ohio', 'Georgia', 'North Carolina', 'Michigan'
]


def extract_states_from_text(text: str) -> Set[str]:
    """
    Extract explicit state mentions from text using pattern matching.

    Args:
        text: Campaign brief or RFP text

    Returns:
        Set of state names found in text
    """
    states_found = set()
    text_lower = text.lower()

    # Check for state names
    for state in US_STATES:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(state) + r'\b'
        if re.search(pattern, text_lower):
            # Convert to title case (except DC)
            if state == 'dc' or state == 'district of columbia':
                states_found.add('District of Columbia')
            else:
                states_found.add(state.title())

    return states_found


def extract_cities_from_text(text: str) -> Set[str]:
    """
    Extract cities from text and map them to states.

    Args:
        text: Campaign brief or RFP text

    Returns:
        Set of state names based on city mentions
    """
    states_from_cities = set()
    text_lower = text.lower()

    for city, state in CITY_TO_STATE.items():
        # Use word boundaries for city names
        pattern = r'\b' + re.escape(city) + r'\b'
        if re.search(pattern, text_lower):
            states_from_cities.add(state)
            logger.debug(f"Found city '{city}' → mapped to state '{state}'")

    return states_from_cities


def extract_regions_from_text(text: str) -> Set[str]:
    """
    Extract regional mentions and expand to state lists.

    Args:
        text: Campaign brief or RFP text

    Returns:
        Set of state names based on region mentions
    """
    states_from_regions = set()
    text_lower = text.lower()

    for region, states in REGION_TO_STATES.items():
        pattern = r'\b' + re.escape(region) + r'\b'
        if re.search(pattern, text_lower):
            states_from_regions.update(states)
            logger.debug(f"Found region '{region}' → expanded to {len(states)} states")

    return states_from_regions


def detect_national_scope(text: str) -> bool:
    """
    Detect if campaign has national scope.

    Args:
        text: Campaign brief or RFP text

    Returns:
        True if national campaign detected
    """
    text_lower = text.lower()

    national_keywords = [
        r'\bnational\b', r'\bnationwide\b', r'\ball states\b', r'\b50 states\b',
        r'\bcoast to coast\b', r'\bdomestic\b', r'\bus market\b', r'\bamerican market\b'
    ]

    for keyword in national_keywords:
        if re.search(keyword, text_lower):
            logger.debug(f"National scope detected: matched '{keyword}'")
            return True

    return False


def calculate_confidence(explicit_states: Set[str], cities: Set[str],
                        regions: Set[str], is_national: bool) -> float:
    """
    Calculate confidence score for geographic extraction.

    Args:
        explicit_states: States explicitly mentioned
        cities: States derived from city mentions
        regions: States derived from region mentions
        is_national: Whether national scope was detected

    Returns:
        Confidence score (0.0 to 1.0)
    """
    confidence = 0.0

    # Explicit state mentions have highest confidence
    if explicit_states:
        confidence += 0.5 * min(len(explicit_states) / 5, 1.0)

    # City mentions are moderately confident
    if cities:
        confidence += 0.3 * min(len(cities) / 3, 1.0)

    # Regional mentions are less specific
    if regions:
        confidence += 0.1

    # National scope is clear but not specific
    if is_national:
        confidence = max(confidence, 0.7)

    return min(confidence, 1.0)


def get_industry_default_states(industry: str) -> List[str]:
    """
    Get default states for a given industry.

    Args:
        industry: Industry name

    Returns:
        List of state names
    """
    industry_lower = industry.lower()

    for key, states in INDUSTRY_DEFAULT_STATES.items():
        if key in industry_lower:
            logger.debug(f"Using industry default states for '{industry}'")
            return states[:5]  # Return top 5

    return []


def extract_geography_from_brief(brief_text: str, industry: Optional[str] = None) -> Dict:
    """
    Main function to extract geographic targeting from campaign brief.

    This uses multiple strategies:
    1. Explicit state mentions
    2. City → state mapping
    3. Region → states expansion
    4. National scope detection
    5. Industry defaults (fallback)

    Args:
        brief_text: Campaign brief or RFP text
        industry: Industry classification (optional)

    Returns:
        Dictionary with:
        {
            'states': List[str] - List of target states
            'primary_state': str - Most likely primary state
            'confidence': float - Confidence score (0.0-1.0)
            'scope': str - 'state', 'regional', 'national'
            'source': str - How geography was determined
        }
    """
    if not brief_text:
        logger.warning("Empty brief text provided")
        return {
            'states': TOP_POPULATION_STATES[:5],
            'primary_state': 'California',
            'confidence': 0.3,
            'scope': 'national',
            'source': 'default'
        }

    # Extract using different methods
    explicit_states = extract_states_from_text(brief_text)
    cities = extract_cities_from_text(brief_text)
    regions = extract_regions_from_text(brief_text)
    is_national = detect_national_scope(brief_text)

    # Combine all findings
    all_states = explicit_states.union(cities).union(regions)

    # Calculate confidence
    confidence = calculate_confidence(explicit_states, cities, regions, is_national)

    # Determine scope and finalize state list
    if is_national:
        # National campaign - use top 10 states
        final_states = TOP_POPULATION_STATES[:10]
        scope = 'national'
        source = 'national_scope_detected'
        primary_state = final_states[0]

    elif len(all_states) > 0:
        # Specific states identified
        final_states = sorted(list(all_states))[:10]  # Limit to top 10
        scope = 'regional' if len(final_states) > 5 else 'state'
        source = 'extracted_from_brief'

        # Determine primary state (prefer explicit mentions)
        if explicit_states:
            primary_state = sorted(list(explicit_states))[0]
        elif cities:
            primary_state = sorted(list(cities))[0]
        else:
            primary_state = final_states[0]

    elif industry:
        # Use industry defaults
        final_states = get_industry_default_states(industry)
        if final_states:
            scope = 'industry_default'
            source = f'industry_default_{industry}'
            primary_state = final_states[0]
            confidence = max(confidence, 0.4)
        else:
            # Ultimate fallback
            final_states = TOP_POPULATION_STATES[:5]
            scope = 'national'
            source = 'fallback_default'
            primary_state = final_states[0]
            confidence = max(confidence, 0.3)

    else:
        # No geography found, no industry - use top states
        final_states = TOP_POPULATION_STATES[:5]
        scope = 'national'
        source = 'fallback_default'
        primary_state = final_states[0]
        confidence = max(confidence, 0.3)

    result = {
        'states': final_states,
        'primary_state': primary_state,
        'confidence': round(confidence, 2),
        'scope': scope,
        'source': source
    }

    logger.info(f"Geographic extraction complete: {len(final_states)} states, "
                f"confidence={result['confidence']}, scope={scope}")

    return result


def format_geographic_summary(geography: Dict) -> str:
    """
    Create a human-readable summary of geographic targeting.

    Args:
        geography: Result from extract_geography_from_brief()

    Returns:
        Formatted summary string
    """
    states = geography['states']
    confidence = geography['confidence']
    scope = geography['scope']

    if scope == 'national':
        return f"National campaign targeting top {len(states)} markets"
    elif len(states) <= 3:
        return f"Targeting: {', '.join(states)}"
    else:
        return f"Multi-state campaign: {', '.join(states[:3])} and {len(states) - 3} more"
