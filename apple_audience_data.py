"""
Apple TV+ Campaign Audience Data Processing Module
This module provides specialized functions for processing audience data for Apple TV+ campaigns.
"""

import random
import json

def get_apple_audience_data():
    """
    Return the processed Apple TV+ audience data.
    
    Returns:
        dict: Dictionary containing Apple TV+ audience data
    """
    # Apple TV+ audience data with a focus on streaming content
    apple_tv_audience = {
        "primary_segments": [
            {
                "name": "Streaming Enthusiasts",
                "description": "Heavy consumers of streaming content across multiple platforms with high engagement in original series and films.",
                "age_range": "18-34",
                "income_level": "Upper Middle-Class to Affluent",
                "interests": ["Premium Content", "Award-Winning Series", "Original Programming", "Film & TV Narratives"],
                "behaviors": ["Multiple Service Subscriptions", "High Screen Time", "Binges Full Series", "Watches on Multiple Devices"],
                "expected_ctr": "2.7-3.2%",
                "expected_vcr": "78-85%"
            },
            {
                "name": "Quality Content Seekers",
                "description": "Discerning viewers who prioritize high-production value content and critically acclaimed programming.",
                "age_range": "25-49",
                "income_level": "Middle to Upper Income",
                "interests": ["Award-Winning Content", "Director-Driven Projects", "Prestige Drama", "Celebrity Talent"],
                "behaviors": ["Research Shows Before Watching", "Less Price Sensitive", "Share Recommendations", "Loyal to Quality Services"],
                "expected_ctr": "2.3-2.8%",
                "expected_vcr": "75-82%"
            }
        ],
        "secondary_segments": [
            {
                "name": "Tech Ecosystem Users",
                "description": "Apple product owners who value ecosystem integration and seamless device experiences.",
                "age_range": "22-45",
                "income_level": "Upper Middle Income",
                "interests": ["Apple Ecosystem", "Tech Integration", "Premium User Experience", "Digital Lifestyle"],
                "behaviors": ["Multi-device Viewing", "Uses Apple Products", "Values UI/UX", "Early Tech Adopter"],
                "expected_ctr": "2.1-2.6%",
                "expected_vcr": "76-83%"
            },
            {
                "name": "Entertainment Trendsetters",
                "description": "Cultural influencers who discover and share trending content with their networks.",
                "age_range": "18-39",
                "income_level": "Varied",
                "interests": ["New Releases", "Trending Topics", "Social Commentary", "Cultural Zeitgeist"],
                "behaviors": ["Social Media Sharing", "Word-of-Mouth Recommendations", "Content Discussion", "Pop Culture Engagement"],
                "expected_ctr": "2.5-3.0%",
                "expected_vcr": "77-84%"
            }
        ],
        "platform_affinities": {
            "high": ["Connected TV", "Premium Video", "Entertainment Apps", "News & Information Sites"],
            "medium": ["Gaming Platforms", "Lifestyle Content", "Mobile Video", "Premium Publishers"],
            "moderate": ["Digital Audio", "Podcasts", "Social Video", "E-commerce"]
        },
        "content_affinities": {
            "high": ["Drama Series", "Original Films", "Documentary Content", "A-List Talent Projects"],
            "medium": ["Comedy Programming", "Limited Series", "Thriller/Mystery", "High-Concept SciFi"],
            "moderate": ["Family-Friendly Content", "Animation", "Reality Programming", "Talk Shows"]
        },
        "media_consumption": {
            "streaming_services": {
                "current_usage": ["Major SVOD Services", "Premium Cable", "AVOD Platforms"],
                "content_preferences": ["Original Series", "Prestige Drama", "Limited Series", "Documentary"],
                "viewing_habits": ["Prime Time Evening", "Weekend Binge", "Multi-Episode Sessions"],
                "device_usage": ["Smart TV", "Tablet", "Mobile", "Laptop"]
            },
            "digital_channels": {
                "high_performing": ["Premium CTV", "High-Impact Video", "Entertainment Verticals"],
                "targeting_recommendations": ["Content Affinity", "Viewership Behavior", "Premium Contextual"],
                "expected_ltr": "82-90%"
            }
        },
        "competitors": {
            "direct": ["Major SVOD Services", "Premium Entertainment Platforms"],
            "indirect": ["Free AVOD Services", "User-Generated Content Platforms", "Cable Networks"]
        },
        "opportunity_vectors": {
            "audience_expansion": ["Film Enthusiasts", "Premium Content Subscribers", "Cultural Trend Followers"],
            "messaging_angles": ["Exclusive Content", "Award-Winning Talent", "Unique Storytelling", "Quality Production Value"],
            "tactical_approaches": ["Content Preview Formats", "Interactive Video", "Rich Media Expandable", "Seamless Viewing Experience"]
        }
    }
    
    return apple_tv_audience

def generate_audience_affinities():
    """
    Generate platform and content affinities based on the Apple TV+ audience data.
    
    Returns:
        dict: A dictionary containing platform and content affinities
    """
    affinities = {
        "platform_affinities": {
            "high": [
                {"name": "Connected TV", "affinity": 87},
                {"name": "Premium Video Sites", "affinity": 83},
                {"name": "Entertainment Apps", "affinity": 79},
                {"name": "News & Information Sites", "affinity": 76}
            ],
            "medium": [
                {"name": "Gaming Platforms", "affinity": 68},
                {"name": "Lifestyle Content", "affinity": 65},
                {"name": "Mobile Video", "affinity": 62},
                {"name": "Premium Publishers", "affinity": 61}
            ],
            "moderate": [
                {"name": "Digital Audio", "affinity": 58},
                {"name": "Podcasts", "affinity": 55},
                {"name": "Social Video", "affinity": 52},
                {"name": "E-commerce Sites", "affinity": 49}
            ]
        },
        "content_affinities": {
            "high": [
                {"name": "Drama Series", "affinity": 85},
                {"name": "Original Films", "affinity": 82},
                {"name": "Documentary Content", "affinity": 78},
                {"name": "A-List Talent Projects", "affinity": 77}
            ],
            "medium": [
                {"name": "Comedy Programming", "affinity": 69},
                {"name": "Limited Series", "affinity": 67},
                {"name": "Thriller/Mystery", "affinity": 65},
                {"name": "High-Concept SciFi", "affinity": 62}
            ],
            "moderate": [
                {"name": "Family-Friendly Content", "affinity": 56},
                {"name": "Animation", "affinity": 54},
                {"name": "Reality Programming", "affinity": 52},
                {"name": "Talk Shows", "affinity": 50}
            ]
        }
    }
    
    return affinities

def generate_apple_specific_targeting_recommendations():
    """
    Generate Apple TV+ specific targeting recommendations based on audience data.
    
    Returns:
        list: A list of targeting recommendations
    """
    # Recommendations use omnichannel tactics terminology without mentioning specific platforms
    recommendations = [
        {
            "title": "Premium Content Contextual Alignment",
            "description": "Target editorial contexts related to entertainment, streaming reviews, and award-winning content to reach viewers actively researching quality programming.",
            "implementation": "Leverage high-impact rich media units within entertainment verticals and premium video environments.",
            "expected_performance": "Expected VCR: 75-85%, Expected CTR: 2.2-2.8%"
        },
        {
            "title": "Entertainment Enthusiast Behavioral Targeting",
            "description": "Target users with demonstrated interest in premium streaming content, film festivals, and director/actor-focused content.",
            "implementation": "Deploy interactive video formats highlighting exclusive Apple TV+ content with seamless subscription CTAs.",
            "expected_performance": "Expected VCR: 78-85%, Expected CTR: 2.5-3.1%"
        },
        {
            "title": "Cross-Device Premium Video Strategy",
            "description": "Implement coordinated messaging across CTV, mobile, and desktop to create an omnipresent but frequency-controlled campaign presence.",
            "implementation": "Prioritize high-viewability placements with 15-second non-skippable video to maximize completion rates.",
            "expected_performance": "Expected VCR: 76-84%, Expected CTR: 2.3-2.9%"
        },
        {
            "title": "Advanced Audience Segmentation",
            "description": "Layer content affinity data with viewer behaviors to identify high-value subscription prospects beyond basic demographics.",
            "implementation": "Use rich media placements with dynamic content that adjusts based on viewer interests (drama vs. comedy emphasis).",
            "expected_performance": "Expected VCR: 77-85%, Expected LTR: 82-90%"
        }
    ]
    
    return recommendations