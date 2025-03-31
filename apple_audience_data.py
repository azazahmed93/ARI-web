"""
Apple TV+ Campaign Audience Data Processing Module
This module provides specialized functions for processing audience data for Apple TV+ campaigns.
"""

import random

def get_apple_audience_data():
    """
    Return the processed Apple TV+ audience data.
    
    Returns:
        dict: Dictionary containing Apple TV+ audience data
    """
    # Primary audience segments for Apple TV+
    primary_segments = [
        {
            "name": "Premium Content Seekers",
            "description": "Affluent professionals (25-54) who prioritize quality storytelling and production value over quantity of content. They're willing to pay for premium entertainment experiences.",
            "size": "32M",
            "affinities": ["High-quality dramas", "Award-winning content", "Premium tech products", "Design-forward brands"],
            "expected_ctr": "0.18%",
            "expected_vcr": "83%",
            "channels": ["Connected TV", "Premium digital video", "Audio streaming", "High-impact display"],
            "devices": ["Smart TVs", "High-end mobile devices", "Tablets", "Laptops"]
        },
        {
            "name": "Entertainment Enthusiasts",
            "description": "Adults (25-45) who actively seek out critically acclaimed shows and films. They value original content and participate in entertainment culture conversations.",
            "size": "28M",
            "affinities": ["Prestige television", "Film festivals", "Cultural events", "Premium audio content"],
            "expected_ctr": "0.22%",
            "expected_vcr": "79%",
            "channels": ["Connected TV", "Interactive video", "Rich media", "Premium digital environments"],
            "devices": ["Smart TVs", "Gaming consoles", "Premium mobile devices", "Laptops"]
        },
        {
            "name": "Apple Ecosystem Users",
            "description": "Current Apple product owners (18-65) who haven't yet subscribed to Apple TV+. They value ecosystem integration and the Apple design philosophy.",
            "size": "45M",
            "affinities": ["Apple hardware", "Minimalist design", "Premium tech services", "Ecosystem integrations"],
            "expected_ctr": "0.31%",
            "expected_vcr": "81%",
            "channels": ["Connected device targeting", "Premium digital video", "Rich media", "Interactive display"],
            "devices": ["Apple devices", "Smart TVs", "Connected home devices"]
        }
    ]
    
    # Secondary audience segments
    secondary_segments = [
        {
            "name": "Culture-Forward Millennials",
            "description": "Adults (25-40) who use entertainment choices as cultural currency and regularly discuss shows on social platforms and in person.",
            "size": "22M",
            "affinities": ["Trending shows", "Cultural commentary", "Premium experiences", "Social discussions"],
            "expected_ctr": "0.19%",
            "expected_vcr": "77%",
            "channels": ["Digital video", "Audio streaming", "Interactive formats", "High-impact units"],
            "devices": ["Mobile devices", "Smart TVs", "Laptops", "Tablets"]
        },
        {
            "name": "Quality-Conscious Gen X",
            "description": "Adults (40-55) who prefer thoughtful, well-crafted content over mainstream entertainment and have high disposable income.",
            "size": "18M",
            "affinities": ["Literary adaptations", "Historical dramas", "Quality journalism", "Premium experiences"],
            "expected_ctr": "0.15%",
            "expected_vcr": "84%",
            "channels": ["Connected TV", "Premium digital environments", "Audio streaming", "High-impact display"],
            "devices": ["Smart TVs", "Tablets", "Desktop computers", "Premium mobile devices"]
        }
    ]
    
    # Growth opportunity segments
    growth_segments = [
        {
            "name": "Content-Curious Gen Z",
            "description": "Young adults (18-24) who actively seek out unique, diverse storytelling and value authenticity in entertainment.",
            "size": "14M",
            "affinities": ["Diverse creators", "Unique storytelling", "Authentic narratives", "Short-form complementary content"],
            "expected_ctr": "0.24%",
            "expected_vcr": "75%",
            "channels": ["Digital video", "Audio streaming", "Interactive formats", "Rich media"],
            "devices": ["Mobile devices", "Smart TVs", "Gaming consoles", "Laptops"]
        },
        {
            "name": "Subscription Optimizers",
            "description": "Budget-conscious entertainment fans (25-45) who carefully curate their streaming services based on current content offerings.",
            "size": "30M",
            "affinities": ["Free trials", "Bundle offerings", "Award-winning content", "Limited series"],
            "expected_ctr": "0.16%",
            "expected_vcr": "76%",
            "channels": ["Connected TV", "Digital video", "Audio streaming", "High-impact units"],
            "devices": ["Smart TVs", "Mobile devices", "Desktop computers", "Streaming devices"]
        }
    ]
    
    return {
        "primary": primary_segments,
        "secondary": secondary_segments,
        "growth": growth_segments
    }

def generate_audience_affinities():
    """
    Generate platform and content affinities based on the Apple TV+ audience data.
    
    Returns:
        dict: A dictionary containing platform and content affinities
    """
    # Platform affinities for Apple TV+
    platform_affinities = {
        "Connected TV": 88,
        "Premium Digital Video": 82,
        "Audio Streaming": 76,
        "Rich Media Display": 68,
        "Interactive Video": 70,
        "High-Impact Units": 66,
        "Digital Out-of-Home": 59
    }
    
    # Content affinities
    content_affinities = {
        "Drama Series": 85,
        "Prestige Television": 82,
        "Documentary Content": 79,
        "Comedy Series": 77,
        "Premium Films": 81,
        "Sci-Fi/Speculative": 72,
        "Quality Family Content": 68
    }
    
    # Demographic affinities (always showing ages 18+ for compliance)
    demographic_affinities = {
        "Adults 25-34": 80,
        "Adults 35-44": 85,
        "Adults 45-54": 76,
        "Adults 18-24": 69,
        "Adults 55+": 62,
        "High Income": 83,
        "College Educated": 79
    }
    
    # Device affinities
    device_affinities = {
        "Smart TVs": 86,
        "Premium Mobile": 82,
        "Tablets": 78,
        "Laptops": 72,
        "Desktop": 65,
        "Connected Devices": 80
    }
    
    return {
        "platforms": platform_affinities,
        "content": content_affinities,
        "demographics": demographic_affinities,
        "devices": device_affinities
    }

def generate_apple_specific_targeting_recommendations():
    """
    Generate Apple TV+ specific targeting recommendations based on audience data.
    
    Returns:
        list: A list of targeting recommendations
    """
    recommendations = [
        {
            "title": "Premium Content Environment Targeting",
            "description": "Target placements within premium content environments that align with Apple's brand values of quality, creativity, and innovation.",
            "implementation": "Focus on high-viewability inventory within curated premium content environments with strong brand safety measures.",
            "expected_lift": "15-20% higher engagement compared to standard targeting"
        },
        {
            "title": "Apple Device Precision Targeting",
            "description": "Leverage device data to identify and target current Apple hardware users who haven't yet subscribed to Apple TV+.",
            "implementation": "Create device-specific creative variations that highlight ecosystem benefits and simplified sign-up process.",
            "expected_lift": "25-30% higher conversion rates among existing Apple customers"
        },
        {
            "title": "Entertainment Enthusiast Behavioral Targeting",
            "description": "Target users who actively engage with entertainment content, reviews, and cultural discussion forums.",
            "implementation": "Implement behavioral targeting based on content consumption patterns and entertainment-related interests.",
            "expected_lift": "18-22% improvement in qualified audience reach"
        },
        {
            "title": "Connected TV Contextual Alignment",
            "description": "Place ads in contextually relevant streaming environments that won't compete directly with Apple TV+ content.",
            "implementation": "Develop contextual targeting segments based on content genre and viewing quality to ensure alignment with premium positioning.",
            "expected_lift": "12-15% higher completion rates and brand recall"
        },
        {
            "title": "Audio Companion Strategy",
            "description": "Complement video strategy with premium audio placements to extend reach and reinforce messaging.",
            "implementation": "Target premium audio inventory with high listening completion rates and complement with synchronized display messaging.",
            "expected_lift": "10-15% incremental reach with 80-90% expected listen-through rates"
        }
    ]
    
    return recommendations