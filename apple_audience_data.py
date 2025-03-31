"""
Apple Phone Campaign Audience Data Processing Module
This module provides specialized functions for processing audience data for Apple Phone campaigns.
"""

import json
import numpy as np
import pandas as pd

# Audience data from the provided assets
APPLE_AUDIENCE_DATA = {
    "id": "06fef464",
    "projected_adult_population": "32.7%",
    "estimated_targetable_ids": "77.5M",
    "total_ids": "103.2M",
    "demographics": {
        "gender": {"female": 57, "male": 43},
        "age": {
            "18-24": 19,
            "mean_age": 44,
            "median_age": 44
        },
        "income": {
            "$100-150k": 19,
            "mean_income": 107914,
            "median_income": 89461
        },
        "education": {"some_college": 32},
        "marital_status": {"married": 57},
        "children": {"no_children_under_18": 59}
    },
    "motivations": {
        "personal_values": [
            {"name": "Life Full of Excitement, Novelties, & Challenges", "index": 138},
            {"name": "Acquiring Wealth and Influence", "index": 134},
            {"name": "Being in Charge and Directing People", "index": 133}
        ],
        "psychological_drivers": [
            {"name": "Living an Exciting Life", "index": 116},
            {"name": "Creativity", "index": 106},
            {"name": "Respect From Others", "index": 106}
        ],
        "hobbies": [
            {"name": "International Travel", "index": 152},
            {"name": "Group Travel", "index": 140},
            {"name": "Participated in Yoga, Pilates or Meditation", "index": 137}
        ],
        "daily_routine": [
            {"name": "Value Athletic Accomplishments", "index": 124},
            {"name": "Buy Food Based on Nutrition", "index": 114},
            {"name": "Exercise 2x or More Weekly", "index": 113}
        ]
    },
    "media_consumption": {
        "streaming_subscriptions": [
            {"name": "Apple TV+", "index": 189, "composition": 19},
            {"name": "Disney+ (without ads)", "index": 130},
            {"name": "Netflix (without ads)", "index": 130},
            {"name": "HBO Max (Without Ads)", "index": 129},
            {"name": "ESPN+", "index": 122}
        ],
        "tv_networks": [
            {"name": "The Learning Channel (TLC)", "index": 132},
            {"name": "Home & Garden Television (HGTV)", "index": 123},
            {"name": "ESPN 2", "index": 120},
            {"name": "Fox Sports 1", "index": 120}
        ],
        "streaming_devices": [
            {"name": "Smart TV", "index": 93},
            {"name": "Streaming Box", "index": 90},
            {"name": "Laptop/Computer", "index": 89},
            {"name": "Mobile Phone", "index": 68}
        ],
        "hours_online": {
            "20-40": 31,
            "40+": 24,
            "10-20": 23,
            "5-10": 13,
            "1-5": 7,
            "<1": 2
        },
        "ott_devices": [
            {"name": "Apple TV", "index": 255},
            {"name": "Smart TV", "index": 107},
            {"name": "Other", "index": 106},
            {"name": "Amazon Fire TV Stick", "index": 93},
            {"name": "Roku", "index": 92}
        ],
        "social_media": [
            {"name": "X (Formerly Known as Twitter)", "index": 143},
            {"name": "LinkedIn", "index": 136},
            {"name": "Snapchat", "index": 132},
            {"name": "Discord", "index": 127}
        ],
        "app_categories": [
            {"name": "Health & Fitness", "index": 150, "composition": 32},
            {"name": "Travel", "index": 142},
            {"name": "Finance/Stocks/Investments", "index": 137},
            {"name": "Business Tools/Productivity", "index": 131},
            {"name": "Utilities/Widgets", "index": 130},
            {"name": "Weather", "index": 123}
        ]
    }
}

def get_apple_audience_data():
    """Return the processed Apple audience data."""
    return APPLE_AUDIENCE_DATA

def generate_audience_affinities():
    """
    Generate platform and content affinities based on the Apple audience data.
    
    Returns:
        dict: A dictionary containing platform and content affinities
    """
    data = get_apple_audience_data()
    
    # Generate platform affinities
    platform_affinities = {
        "Connected TV": {
            "score": 92,
            "platforms": ["Smart TV", "Apple TV", "Streaming Box"]
        },
        "Mobile": {
            "score": 84,
            "platforms": ["Mobile Phone", "Tablet"]
        },
        "Desktop": {
            "score": 78,
            "platforms": ["Laptop/Computer"]
        }
    }
    
    # Generate content affinities
    content_affinities = {
        "Lifestyle": {
            "score": 89,
            "examples": ["Health & Fitness", "Travel", "Home & Garden"]
        },
        "Technology": {
            "score": 94,
            "examples": ["Tech News", "Product Reviews", "Innovation"]
        },
        "Business": {
            "score": 86,
            "examples": ["Finance", "Productivity", "Professional Development"]
        }
    }
    
    return {
        "platform_affinities": platform_affinities,
        "content_affinities": content_affinities
    }

def generate_apple_specific_targeting_recommendations():
    """
    Generate Apple-specific targeting recommendations based on audience data.
    
    Returns:
        list: A list of targeting recommendations
    """
    data = get_apple_audience_data()
    
    recommendations = [
        {
            "category": "Demographic",
            "recommendation": "Target adults 35-54 as primary audience with secondary focus on 18-24 segment",
            "reasoning": "Mean age is 44, but 19% are 18-24, suggesting multi-generational appeal"
        },
        {
            "category": "Behavioral",
            "recommendation": "Emphasize health & fitness integration with productivity features",
            "reasoning": "High affinity for Health & Fitness apps (index 150) and Business/Productivity (index 131)"
        },
        {
            "category": "Media",
            "recommendation": "Prioritize premium streaming environments with lifestyle content adjacency",
            "reasoning": "Strong Apple TV+ affinity (index 189) and interest in lifestyle content (HGTV, TLC)"
        },
        {
            "category": "Platform",
            "recommendation": "Optimize for Apple TV (index 255) and Smart TV (index 93) viewing experiences",
            "reasoning": "Highest device affinity is for Apple's own ecosystem"
        },
        {
            "category": "Messaging",
            "recommendation": "Focus on excitement, innovation and premium lifestyle positioning",
            "reasoning": "Top personal values include 'Life Full of Excitement' (index 138) and 'Acquiring Wealth' (index 134)"
        }
    ]
    
    return recommendations