# Content and descriptions for the ARI analyzer

# Metrics and their descriptions
METRICS = {
    "Representation": {
        "high": "Featured a high-visibility figure aligned with the audience's identity and values.",
        "medium": "Some authentic representation included, but lacked consistent presence or depth.",
        "low": "Limited representation of the intended audience or cultural perspective."
    },
    "Cultural Relevance": {
        "high": "Included elements like music, sports, and fashion that resonate with audience interests.",
        "medium": "Relevant ideas are present, but stronger emotional or lifestyle ties could be made.",
        "low": "Audience interests weren't clearly reflected in campaign content."
    },
    "Platform Relevance": {
        "high": "Excellent implementation of omnichannel tactics across high-engagement platforms, utilizing interactive video, rich media, and audio where the audience is most active. Balanced frequency across devices with precise dayparting.",
        "medium": "Good platform coverage but underutilizes high-impact formats and interactive elements. Consider expanding audio presence and augmenting with interstitial formats in key engagement windows.",
        "low": "Tactical mix lacks depth in critical engagement channels. Prioritize interactive video, high-impact rich media, and geotargeted mobile experiences to better reach this audience where they consume content."
    },
    "Cultural Vernacular": {
        "high": "Tone, slang, and messaging felt natural and aligned with audience voice.",
        "medium": "Language is mostly appropriate but could feel more native or playful.",
        "low": "Messaging feels out of sync with audience expectations or vibe."
    },
    "Media Ownership Equity": {
        "high": "Campaign invested in platforms and creators trusted by the audience.",
        "medium": "Some budget directed toward representative media, but not consistently.",
        "low": "No clear support for audience-owned or representative media channels."
    },
    "Cultural Authority": {
        "high": "Campaign tapped into key lifestyle cues like sports, music, and creators.",
        "medium": "Familiar cultural symbols are present but not deeply integrated.",
        "low": "Lacked credible ties to the audience's culture or world."
    },
    "Buzz & Conversation": {
        "high": "Built to spark organic hype, memes, or fan-led content.",
        "medium": "Could create conversation but needs stronger creative moments.",
        "low": "Unlikely to drive significant social or peer-based attention."
    },
    "Commerce Bridge": {
        "high": "Clear path from campaign to product discovery or purchase.",
        "medium": "Product tie-in is visible but not strongly action-oriented.",
        "low": "Campaign and commerce feel disconnected."
    },
    "Geo-Cultural Fit": {
        "high": "Targeted regions align tightly with audience lifestyle and trends.",
        "medium": "Covers key markets but could add local nuances.",
        "low": "Misses where the audience actually lives or connects."
    }
}

# Media affinity sites with their QVI scores
MEDIA_AFFINITY_SITES = [
    {"name": "sparknotes.com", "category": "Education", "qvi": 562, "url": "https://sparknotes.com", "tooltip": "Great for literary tools and student engagement"},
    {"name": "basketball-reference.com", "category": "Sports", "qvi": 558, "url": "https://www.basketball-reference.com", "tooltip": "High-indexing for sports stats and active fans"},
    {"name": "coolmathgames.com", "category": "Education", "qvi": 543, "url": "https://www.coolmathgames.com", "tooltip": "Casual educational games popular with teens"},
    {"name": "nba.com", "category": "Sports", "qvi": 461, "url": "https://www.nba.com", "tooltip": "Official NBA content, big Gen Z crossover"},
    {"name": "theverge.com", "category": "Tech", "qvi": 450, "url": "https://www.theverge.com", "tooltip": "Tech and culture content with style relevance"}
]

# TV Network affinities
TV_NETWORKS = [
    {"name": "NBA TV", "category": "Sports", "qvi": 459},
    {"name": "Adult Swim", "category": "Alt Animation", "qvi": 315},
    {"name": "Cartoon Network", "category": "Youth", "qvi": 292},
    {"name": "MTV", "category": "Music / Culture", "qvi": 288},
    {"name": "Nickelodeon", "category": "Kids / Family", "qvi": 263}
]

# Streaming platforms
STREAMING_PLATFORMS = [
    {"name": "Peacock Premium", "category": "Entertainment", "qvi": 216},
    {"name": "HBO Max", "category": "Drama / Comedy", "qvi": 188},
    {"name": "Hulu", "category": "Variety", "qvi": 173},
    {"name": "ESPN+", "category": "Sports", "qvi": 172},
    {"name": "YouTube Premium", "category": "Video", "qvi": 167},
    {"name": "Disney+", "category": "Family / Animation", "qvi": 165}
]

# Additional content sections
PSYCHOGRAPHIC_HIGHLIGHTS = """
This audience is highly motivated by <strong>wealth, admiration, and excitement</strong>. 
They over-index for <strong>social status and peer recognition</strong>, and are more likely 
to play basketball, value athletic accomplishments, and participate in teams or classes.
"""

AUDIENCE_SUMMARY = """
This audience skews <strong>young, male, and single</strong> with a strong affinity for sports, 
education tools, and socially driven platforms. They're <strong>highly motivated by admiration, 
status, and excitement</strong>. A growth opportunity exists among <strong>older Gen Z and 
college-age students</strong> who index high for athletic lifestyle, peer validation, and 
mobile-first media behaviors.
"""

NEXT_STEPS = """
Every insight here ties to a tangible opportunity. <strong>Digital Culture Group offers solutions</strong>
—from creative production to media placement and performance measurement—to lift your lowest scoring areas.
"""

# Stock photos URLs
STOCK_PHOTOS = {
    "business_analytics": [
        "https://images.unsplash.com/photo-1608222351212-18fe0ec7b13b",
        "https://images.unsplash.com/photo-1599658880436-c61792e70672",
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
        "https://images.unsplash.com/photo-1591696205602-2f950c417cb9"
    ],
    "data_visualization": [
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
        "https://images.unsplash.com/photo-1584291527935-456e8e2dd734",
        "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3"
    ]
}
