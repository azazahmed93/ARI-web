"""
Benchmark Configuration for Platform Metrics

This configuration file contains industry-standard benchmark metrics for different
advertising platforms. Metrics include Completion Rates, Click-Through Rates,
Engagement Rates, and Conversion Rates.

Source: benchmark-data.csv
Last Updated: 2025

Metric Types:
- CTR: Click-Through Rate
- VCR: Video Completion Rate
- LTR: Listen-Through Rate
- ER: Engagement Rate
- CVR: Conversion Rate
"""

# Platform benchmark configuration
# Format: {
#     'platform_type': {
#         'keywords': [...],  # Keywords to match against platform_targeting
#         'metric_name': 'Display Name',
#         'metric_value': 'Range',
#         'engagement_rate': 'Range' (optional),
#         'conversion_rate': 'Range' (optional),
#         'description': 'Brief description'
#     }
# }

PLATFORM_BENCHMARKS = {
    'display': {
        'keywords': ['display', 'banner'],
        'metric_name': 'Expected CTR',
        'metric_value': '0.06-0.20%',
        'engagement_rate': '2-8%',
        'description': 'Display advertising click-through rate'
    },

    'online_video': {
        'keywords': ['video', 'streaming video', 'online video'],
        'metric_name': 'Expected VCR',
        'metric_value': '70-95%',
        'engagement_rate': '1-5%',
        'description': 'Online video completion rate'
    },

    'ctv': {
        'keywords': ['ctv', 'ott', 'connected tv', 'streaming tv'],
        'metric_name': 'Expected VCR',
        'metric_value': '92-98%',
        'description': 'Connected TV / OTT video completion rate'
    },

    'digital_audio': {
        'keywords': ['audio', 'podcast', 'music', 'streaming audio', 'digital audio'],
        'metric_name': 'Expected LTR',
        'metric_value': '88-99%',
        'description': 'Digital audio listen-through rate'
    },

    'rich_media': {
        'keywords': ['rich media', 'interactive', 'high-impact'],
        'metric_name': 'Expected CTR',
        'metric_value': '0.5-2.0%',
        'description': 'Rich media interactive ad click-through rate'
    },

    'native': {
        'keywords': ['native', 'content', 'sponsored content'],
        'metric_name': 'Expected CTR',
        'metric_value': '0.4-1.0%',
        'engagement_rate': '2-6%',
        'description': 'Native advertising click-through rate'
    },

    'search': {
        'keywords': ['search', 'sem', 'paid search', 'search engine'],
        'metric_name': 'Expected CTR',
        'metric_value': '2-6%',
        'conversion_rate': '3-10%',
        'description': 'Search advertising click-through rate'
    },

    'paid_social': {
        'keywords': ['social', 'facebook', 'instagram', 'twitter', 'linkedin', 'tiktok', 'snapchat', 'paid social'],
        'metric_name': 'Expected CTR',
        'metric_value': '0.7-1.5%',
        'engagement_rate': '1-5%',
        'conversion_rate': '2-8%',
        'description': 'Paid social media click-through rate'
    },

    'dooh': {
        'keywords': ['dooh', 'digital out of home', 'out-of-home', 'ooh', 'billboard', 'transit'],
        'metric_name': 'Expected Outcome',
        'metric_value': 'N/A',
        'description': 'Digital out-of-home advertising (no completion/click metrics)'
    }
}


def get_platform_benchmark(platform_name: str) -> dict:
    """
    Get benchmark metrics for a given platform.

    Args:
        platform_name: Platform name from platform_targeting (e.g., "CTV/OTT", "Display", "Digital Audio")

    Returns:
        Dictionary with metric_name, metric_value, and optional engagement_rate/conversion_rate
    """
    if not platform_name:
        return {
            'metric_name': 'Expected CTR',
            'metric_value': 'N/A'
        }

    platform_lower = platform_name.lower()

    # Check each platform configuration for keyword matches
    for platform_type, config in PLATFORM_BENCHMARKS.items():
        for keyword in config['keywords']:
            if keyword in platform_lower:
                result = {
                    'metric_name': config['metric_name'],
                    'metric_value': config['metric_value'],
                    'description': config.get('description', '')
                }

                # Add engagement_rate if available
                if 'engagement_rate' in config:
                    result['engagement_rate'] = config['engagement_rate']

                # Add conversion_rate if available
                if 'conversion_rate' in config:
                    result['conversion_rate'] = config['conversion_rate']

                return result

    # Default fallback if no match found
    return {
        'metric_name': 'Expected CTR',
        'metric_value': 'N/A'
    }


def get_all_benchmarks() -> dict:
    """
    Get all platform benchmarks.

    Returns:
        Complete PLATFORM_BENCHMARKS dictionary
    """
    return PLATFORM_BENCHMARKS
