"""
Census Bureau API Integration

This module provides functions to fetch demographic data from the US Census Bureau API.
It includes state-level demographics, trend analysis, and caching for performance.

API Documentation: https://www.census.gov/data/developers/data-sets.html
"""

import os
import requests
from typing import Dict, List, Optional, Any
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# State name to FIPS code mapping
STATE_FIPS_MAPPING = {
    'alabama': '01', 'alaska': '02', 'arizona': '04', 'arkansas': '05',
    'california': '06', 'colorado': '08', 'connecticut': '09', 'delaware': '10',
    'florida': '12', 'georgia': '13', 'hawaii': '15', 'idaho': '16',
    'illinois': '17', 'indiana': '18', 'iowa': '19', 'kansas': '20',
    'kentucky': '21', 'louisiana': '22', 'maine': '23', 'maryland': '24',
    'massachusetts': '25', 'michigan': '26', 'minnesota': '27', 'mississippi': '28',
    'missouri': '29', 'montana': '30', 'nebraska': '31', 'nevada': '32',
    'new hampshire': '33', 'new jersey': '34', 'new mexico': '35', 'new york': '36',
    'north carolina': '37', 'north dakota': '38', 'ohio': '39', 'oklahoma': '40',
    'oregon': '41', 'pennsylvania': '42', 'rhode island': '44', 'south carolina': '45',
    'south dakota': '46', 'tennessee': '47', 'texas': '48', 'utah': '49',
    'vermont': '50', 'virginia': '51', 'washington': '53', 'west virginia': '54',
    'wisconsin': '55', 'wyoming': '56', 'district of columbia': '11', 'dc': '11'
}

# Reverse mapping for FIPS to state name
FIPS_TO_STATE = {v: k.title() for k, v in STATE_FIPS_MAPPING.items() if k != 'dc'}
FIPS_TO_STATE['11'] = 'District of Columbia'

# Census ACS variables for demographics
CENSUS_VARIABLES = {
    'B02001_001E': 'total_population',
    'B02001_002E': 'white_alone',
    'B02001_003E': 'black_alone',
    'B02001_005E': 'asian_alone',
    'B02001_006E': 'hawaiian_pacific_islander_alone',
    'B02001_008E': 'two_or_more_races',
    'B03003_003E': 'hispanic_latino'
}

# Base Census API URL
CENSUS_BASE_URL = "https://api.census.gov/data"


def get_census_api_key() -> Optional[str]:
    """Get Census API key from environment variables."""
    return os.getenv('CENSUS_API_KEY')


def map_state_to_fips(state_name: str) -> Optional[str]:
    """
    Convert state name to FIPS code.

    Args:
        state_name: State name (e.g., "California", "CA")

    Returns:
        FIPS code (e.g., "06") or None if not found
    """
    state_lower = state_name.lower().strip()

    # Direct lookup
    if state_lower in STATE_FIPS_MAPPING:
        return STATE_FIPS_MAPPING[state_lower]

    # Try abbreviation lookup (CA → California)
    state_abbrev_map = {
        'al': 'alabama', 'ak': 'alaska', 'az': 'arizona', 'ar': 'arkansas',
        'ca': 'california', 'co': 'colorado', 'ct': 'connecticut', 'de': 'delaware',
        'fl': 'florida', 'ga': 'georgia', 'hi': 'hawaii', 'id': 'idaho',
        'il': 'illinois', 'in': 'indiana', 'ia': 'iowa', 'ks': 'kansas',
        'ky': 'kentucky', 'la': 'louisiana', 'me': 'maine', 'md': 'maryland',
        'ma': 'massachusetts', 'mi': 'michigan', 'mn': 'minnesota', 'ms': 'mississippi',
        'mo': 'missouri', 'mt': 'montana', 'ne': 'nebraska', 'nv': 'nevada',
        'nh': 'new hampshire', 'nj': 'new jersey', 'nm': 'new mexico', 'ny': 'new york',
        'nc': 'north carolina', 'nd': 'north dakota', 'oh': 'ohio', 'ok': 'oklahoma',
        'or': 'oregon', 'pa': 'pennsylvania', 'ri': 'rhode island', 'sc': 'south carolina',
        'sd': 'south dakota', 'tn': 'tennessee', 'tx': 'texas', 'ut': 'utah',
        'vt': 'vermont', 'va': 'virginia', 'wa': 'washington', 'wv': 'west virginia',
        'wi': 'wisconsin', 'wy': 'wyoming', 'dc': 'district of columbia'
    }

    if state_lower in state_abbrev_map:
        return STATE_FIPS_MAPPING[state_abbrev_map[state_lower]]

    logger.warning(f"Could not map state name to FIPS: {state_name}")
    return None


@lru_cache(maxsize=128)
def fetch_census_demographics(state_fips: str, year: int = 2024) -> Optional[Dict[str, Any]]:
    """
    Fetch demographic data for a state from Census ACS API.

    Args:
        state_fips: State FIPS code (e.g., "06" for California)
        year: Census year (default: 2024)

    Returns:
        Dictionary with demographic data or None if error
    """
    api_key = get_census_api_key()
    if not api_key:
        logger.error("Census API key not configured. Set CENSUS_API_KEY environment variable.")
        return None

    # Build variable list
    variables = ','.join(CENSUS_VARIABLES.keys())

    # Construct API URL
    url = f"{CENSUS_BASE_URL}/{year}/acs/acs1"
    params = {
        'get': f'NAME,{variables}',
        'for': f'state:{state_fips}',
        'key': api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Parse response
        if len(data) < 2:
            logger.error(f"Unexpected Census API response format for state {state_fips}")
            return None

        headers = data[0]
        values = data[1]

        # Create result dictionary
        result = {
            'state_fips': state_fips,
            'state_name': values[0],
            'year': year,
            'raw_counts': {},
            'percentages': {}
        }

        # Extract raw counts
        for i, header in enumerate(headers[1:], start=1):
            if header in CENSUS_VARIABLES:
                var_name = CENSUS_VARIABLES[header]
                try:
                    result['raw_counts'][var_name] = int(values[i])
                except (ValueError, IndexError):
                    result['raw_counts'][var_name] = 0

        # Calculate percentages
        total_pop = result['raw_counts'].get('total_population', 0)
        if total_pop > 0:
            result['percentages'] = {
                'White': round((result['raw_counts'].get('white_alone', 0) / total_pop) * 100, 1),
                'Hispanic or Latino': round((result['raw_counts'].get('hispanic_latino', 0) / total_pop) * 100, 1),
                'Black or African American': round((result['raw_counts'].get('black_alone', 0) / total_pop) * 100, 1),
                'Asian': round((result['raw_counts'].get('asian_alone', 0) / total_pop) * 100, 1),
                'Native Hawaiian/Pacific Islander': round((result['raw_counts'].get('hawaiian_pacific_islander_alone', 0) / total_pop) * 100, 1),
                'Two or More Races': round((result['raw_counts'].get('two_or_more_races', 0) / total_pop) * 100, 1)
            }

        logger.info(f"Successfully fetched Census data for {result['state_name']} ({year})")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Census data for state {state_fips}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing Census data: {e}")
        return None


def fetch_census_trends(state_fips: str, years: List[int] = [2023, 2024]) -> Optional[Dict[str, Any]]:
    """
    Fetch demographic trends over multiple years.

    Args:
        state_fips: State FIPS code
        years: List of years to fetch (default: [2023, 2024])

    Returns:
        Dictionary with trend data including year-over-year changes
    """
    if len(years) < 2:
        logger.warning("Need at least 2 years for trend analysis")
        return None

    # Fetch data for each year
    yearly_data = {}
    for year in years:
        data = fetch_census_demographics(state_fips, year)
        if data:
            yearly_data[year] = data

    if len(yearly_data) < 2:
        logger.warning(f"Could not fetch data for enough years to calculate trends")
        return None

    # Calculate year-over-year changes
    sorted_years = sorted(yearly_data.keys())
    current_year = sorted_years[-1]
    previous_year = sorted_years[-2]

    current_data = yearly_data[current_year]['percentages']
    previous_data = yearly_data[previous_year]['percentages']

    trends = {
        'state_fips': state_fips,
        'state_name': yearly_data[current_year]['state_name'],
        'current_year': current_year,
        'previous_year': previous_year,
        'current_demographics': current_data,
        'yoy_changes': {}
    }

    # Calculate changes for each demographic
    for demographic in current_data.keys():
        current_val = current_data.get(demographic, 0)
        previous_val = previous_data.get(demographic, 0)
        change = round(current_val - previous_val, 1)

        trends['yoy_changes'][demographic] = {
            'change': change,
            'direction': 'up' if change > 0 else 'down' if change < 0 else 'stable',
            'previous_value': previous_val,
            'current_value': current_val
        }

    logger.info(f"Calculated trends for {trends['state_name']} ({previous_year}-{current_year})")
    return trends


def fetch_multiple_states(state_names: List[str], year: int = 2024) -> Dict[str, Any]:
    """
    Fetch Census data for multiple states.

    Args:
        state_names: List of state names
        year: Census year

    Returns:
        Dictionary mapping state names to demographic data
    """
    results = {}

    for state_name in state_names:
        fips = map_state_to_fips(state_name)
        if fips:
            data = fetch_census_demographics(fips, year)
            if data:
                results[state_name] = data
            else:
                logger.warning(f"Could not fetch Census data for {state_name}")
        else:
            logger.warning(f"Could not map state name to FIPS: {state_name}")

    return results


def get_national_demographics(year: int = 2024) -> Optional[Dict[str, Any]]:
    """
    Get aggregated national demographics (all states combined).

    This fetches data for all 50 states + DC and aggregates the results.
    Note: This is a simplified aggregation and may not match Census national estimates exactly.

    Args:
        year: Census year

    Returns:
        Aggregated national demographic data
    """
    # For simplicity, we can use the national-level API endpoint
    api_key = get_census_api_key()
    if not api_key:
        return None

    variables = ','.join(CENSUS_VARIABLES.keys())
    url = f"{CENSUS_BASE_URL}/{year}/acs/acs1"
    params = {
        'get': f'NAME,{variables}',
        'for': 'us:1',  # National level
        'key': api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if len(data) < 2:
            return None

        headers = data[0]
        values = data[1]

        result = {
            'geography': 'National',
            'year': year,
            'raw_counts': {},
            'percentages': {}
        }

        # Extract raw counts
        for i, header in enumerate(headers[1:], start=1):
            if header in CENSUS_VARIABLES:
                var_name = CENSUS_VARIABLES[header]
                try:
                    result['raw_counts'][var_name] = int(values[i])
                except (ValueError, IndexError):
                    result['raw_counts'][var_name] = 0

        # Calculate percentages
        total_pop = result['raw_counts'].get('total_population', 0)
        if total_pop > 0:
            result['percentages'] = {
                'White': round((result['raw_counts'].get('white_alone', 0) / total_pop) * 100, 1),
                'Hispanic or Latino': round((result['raw_counts'].get('hispanic_latino', 0) / total_pop) * 100, 1),
                'Black or African American': round((result['raw_counts'].get('black_alone', 0) / total_pop) * 100, 1),
                'Asian': round((result['raw_counts'].get('asian_alone', 0) / total_pop) * 100, 1),
                'Native Hawaiian/Pacific Islander': round((result['raw_counts'].get('hawaiian_pacific_islander_alone', 0) / total_pop) * 100, 1),
                'Two or More Races': round((result['raw_counts'].get('two_or_more_races', 0) / total_pop) * 100, 1)
            }

        return result

    except Exception as e:
        logger.error(f"Error fetching national demographics: {e}")
        return None
