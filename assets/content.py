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
        "high": "Used top platforms where the audience is most active and engaged.",
        "medium": "Covers key platforms but misses niche or community-driven spaces.",
        "low": "Platform mix doesn't align with where this audience actually spends time."
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

# SiteOne Hispanic Media Affinities based on Resonate data
SITEONE_HISPANIC_SOCIAL_MEDIA = [
    {"name": "Twitch", "category": "Streaming", "qvi": 208},
    {"name": "Discord", "category": "Social", "qvi": 178},
    {"name": "TikTok", "category": "Video", "qvi": 146},
    {"name": "Reddit", "category": "Forums", "qvi": 140}
]

# TV Network affinities - Updated based on Audience_06fef464_Media_Consumption data
TV_NETWORKS = [
    {"name": "The Learning Channel (TLC)", "category": "Education", "qvi": 132},
    {"name": "Home & Garden Television (HGTV)", "category": "Lifestyle", "qvi": 123},
    {"name": "ESPN 2", "category": "Sports", "qvi": 120},
    {"name": "Fox Sports 1", "category": "Sports", "qvi": 120},
    {"name": "None of the Above", "category": "Other", "qvi": 116}
]

# SiteOne Hispanic TV Networks based on Resonate data
SITEONE_HISPANIC_TV_NETWORKS = [
    {"name": "Univision", "category": "Spanish", "qvi": 1357},
    {"name": "NFL Network", "category": "Sports", "qvi": 295},
    {"name": "Comedy Central", "category": "Comedy", "qvi": 282},
    {"name": "Adult Swim", "category": "Animation", "qvi": 276},
    {"name": "HBO", "category": "Premium", "qvi": 195}
]

# Streaming platforms - Updated based on Audience_06fef464_Media_Consumption data
STREAMING_PLATFORMS = [
    {"name": "Apple TV+", "category": "Entertainment", "qvi": 189},
    {"name": "Disney+ (without ads)", "category": "Entertainment", "qvi": 130},
    {"name": "Netflix (without ads)", "category": "Entertainment", "qvi": 130},
    {"name": "HBO Max (Without Ads)", "category": "Entertainment", "qvi": 129},
    {"name": "ESPN+", "category": "Sports", "qvi": 122},
    {"name": "Paramount+ (without ads)", "category": "Entertainment", "qvi": 120}
]

# SiteOne Hispanic Streaming Platforms based on Resonate data
SITEONE_HISPANIC_STREAMING = [
    {"name": "Disney+ (without ads)", "category": "Entertainment", "qvi": 184},
    {"name": "Netflix (without ads)", "category": "Entertainment", "qvi": 164},
    {"name": "Disney+ (with ads)", "category": "Entertainment", "qvi": 132},
    {"name": "Paramount+ (with ads)", "category": "Entertainment", "qvi": 132},
    {"name": "YouTube TV/Premium", "category": "Video", "qvi": 123},
    {"name": "Hulu (without ads)", "category": "Entertainment", "qvi": 120}
]

# Additional content sections
PSYCHOGRAPHIC_HIGHLIGHTS = """
This audience values <strong>life full of excitement, novelties, and challenges (index 138)</strong>, 
<strong>acquiring wealth and influence (index 134)</strong>, and <strong>being in charge and directing people (index 133)</strong>. 
Their top psychological drivers include <strong>living an exciting life (index 116)</strong> and <strong>creativity (index 106)</strong>.
They have exceptionally high indexes for <strong>international travel (index 152)</strong>, <strong>group travel (index 140)</strong>, 
and <strong>yoga/meditation (index 137)</strong>. Their daily routines emphasize <strong>athletic accomplishments (index 124)</strong>, 
<strong>nutrition-based food choices (index 114)</strong>, and <strong>regular exercise (index 113)</strong>.
"""

# SiteOne Hispanic Psychographic Highlights based on Resonate data
SITEONE_HISPANIC_PSYCHOGRAPHIC = """
This audience strongly values <strong>maintaining traditions (161)</strong>, <strong>acquiring wealth and 
influence (143)</strong>, and <strong>being humble (142)</strong>. Their top psychological drivers are 
<strong>living an exciting life (204)</strong> and <strong>social/professional status (166)</strong>. 
They have exceptionally high indexes for <strong>soccer (419)</strong>, <strong>gambling on sports (265)</strong>, 
and <strong>basketball (249)</strong>.
"""

AUDIENCE_SUMMARY = """
<div style="margin-bottom: 15px;">
<strong>Core Audience:</strong> This audience skews <strong>female (57%)</strong> with a <strong>mean age of 44</strong> and <strong>19% in the $100-150k income bracket</strong> (mean income: $107,914). They have a strong affinity for Apple TV+ (index 189), health & fitness apps (32%), and premium streaming content. <strong>57% are married</strong> and <strong>59% do not have children under age 18</strong>.
</div>

<div style="margin-bottom: 15px;">
<strong>Primary Audience Signal:</strong> Our AI analysis identifies <strong>Tech-Savvy Streamers</strong> who value life full of excitement, novelties, and challenges (index 138). They have high engagement with international travel (index 152) and group travel (index 140). This audience shows strong affinities for connected TV (index 132) and premium digital video, with 2.8x higher completion rates when targeted with high-quality storytelling that emphasizes exciting experiences and creative content.
</div>

<div>
<strong>Secondary Audience Insight:</strong> Additional opportunity exists with <strong>Lifestyle & Culture Enthusiasts</strong> who value arts and entertainment (index 124), premium lifestyle content (index 114), and cultural experiences (index 113). This segment indexes high for digital subscriptions (index 150) and demonstrates strong engagement with TV shows & movies content (index 137).
</div>
"""

# SiteOne Hispanic Audience Summary based on Resonate data
SITEONE_HISPANIC_SUMMARY = """
<div style="margin-bottom: 15px;">
<strong>Core Audience:</strong> This audience is <strong>93% male</strong>, with <strong>39% ages 25-34</strong>, <strong>33% 
in the $25-50k income bracket</strong>, and <strong>42% with high school education</strong>. 
They're <strong>highly engaged on mobile devices (313)</strong> and spend significant time 
online with <strong>33% spending 10-20 hours per week</strong> online.
</div>

<div style="margin-bottom: 15px;">
<strong>Primary Audience Signal:</strong> Our AI analysis reveals <strong>Cultural Connectors</strong> (bilingual, tech-savvy family influencers, 30-45) who make purchasing decisions for multigenerational households. This audience demonstrates 3.2x higher engagement with culturally-relevant audio content and shows strong affinity for interactive and shoppable video formats that seamlessly integrate with their mobile-first behaviors.
</div>

<div>
<strong>Media Consumption:</strong> Their media consumption shows very strong indexes for <strong>Univision (1357)</strong> and <strong>sports content</strong>, with significant engagement on <strong>Twitch (208)</strong> and <strong>Discord (178)</strong>.
</div>
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
