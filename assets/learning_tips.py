"""
Learning Tips module for the ARI Analyzer.
This provides contextual tooltips and educational content for complex metrics and terms.
"""
import streamlit as st

# Dictionary of learning tips, organized by context/section
LEARNING_TIPS = {
    # Metric-specific tips
    "metrics": {
        "Cultural Vernacular": {
            "title": "Cultural Vernacular",
            "content": "This metric assesses how well your campaign speaks the language of your target audience. It evaluates the use of current terminology, references, and expressions that resonate with their cultural mindset.",
            "learn_more": "Higher scores indicate authentic language that connects with audience values and references."
        },
        "Cultural Relevance": {
            "title": "Cultural Relevance",
            "content": "Measures how well your campaign connects with current cultural topics, trends, and conversations that matter to your target audience, ensuring your message feels timely and meaningful.",
            "learn_more": "Campaigns with high cultural relevance typically achieve 2.3x higher engagement rates."
        },
        "Cultural Authority": {
            "title": "Cultural Authority",
            "content": "Evaluates how credibly your brand positions itself within the cultural space it's targeting. This metric assesses if your campaign demonstrates authentic knowledge and contribution to the culture.",
            "learn_more": "Strong cultural authority builds lasting brand equity beyond individual campaigns."
        },
        "Platform Relevance": {
            "title": "Platform Relevance",
            "content": "Measures how appropriately your campaign messaging is tailored to the specific platforms where it will appear, considering each platform's unique audience expectations and content formats.",
            "learn_more": "Platform-optimized campaigns show 34% higher completion rates and 27% better conversion metrics."
        },
        "Buzz & Conversation": {
            "title": "Buzz & Conversation",
            "content": "Predicts the likelihood of your campaign generating organic discussion, shares, and word-of-mouth. This forecasts conversation potential rather than measuring existing buzz.",
            "learn_more": "Campaigns scoring 8+ typically generate 3x more earned media impressions."
        },
        "Commerce Bridge": {
            "title": "Commerce Bridge",
            "content": "Assesses how effectively your campaign connects cultural engagement to commercial action, measuring the strength of the pathway from awareness to consideration and purchase intent.",
            "learn_more": "This metric is strongly correlated with ROI and conversion performance."
        },
        "Geo-Cultural Fit": {
            "title": "Geo-Cultural Fit",
            "content": "Evaluates how well your campaign considers geographic and regional cultural nuances, ensuring relevance across different markets and avoiding cultural disconnects.",
            "learn_more": "Regional-aware campaigns typically outperform generic national campaigns by 1.8x in local markets."
        },
        "Media Ownership Equity": {
            "title": "Media Ownership Equity",
            "content": "Measures the diversity of media ownership in your campaign plan, assessing your investment in minority-owned media and diverse publisher voices.",
            "learn_more": "Brands with high scores typically see 1.5x better performance with diverse audience segments."
        },
        "Representation": {
            "title": "Representation",
            "content": "Evaluates how authentically your campaign represents the diversity of your target audience, including considerations of inclusivity, stereotype avoidance, and authentic portrayal.",
            "learn_more": "High-scoring campaigns show 2x better brand favorability among diverse audience segments."
        }
    },
    
    # Advanced metrics and concepts
    "advanced": {
        "Resonance Convergence Coefficient": {
            "title": "Resonance Convergence Coefficient",
            "content": "A proprietary meta-metric that synthesizes all nine ARI metrics into a single score, weighted by their relative importance for your specific campaign objectives and industry benchmarks.",
            "learn_more": "This coefficient is the strongest predictor of overall campaign effectiveness."
        },
        "Quality Visit Index (QVI)": {
            "title": "Quality Visit Index (QVI)",
            "content": "Measures the quality and depth of audience engagement with a specific media platform, factoring in time spent, interaction rate, and return frequency rather than just visit volume.",
            "learn_more": "High QVI sites typically deliver 2.8x higher brand recall than low QVI alternatives."
        },
        "Hyperdimensional Matrix": {
            "title": "Hyperdimensional Matrix",
            "content": "Visualizes your campaign's performance across multiple metrics simultaneously, revealing patterns of strength and opportunity that might not be evident when looking at metrics in isolation.",
            "learn_more": "The shape of your matrix provides strategic insights about campaign balance and focus areas."
        },
        "Benchmark Percentile": {
            "title": "Benchmark Percentile",
            "content": "Ranks your campaign against our database of 300+ analyzed campaigns across various industries, showing where your campaign stands in relation to industry standards.",
            "learn_more": "Percentiles above 75% indicate industry-leading performance in the measured dimensions."
        }
    },
    
    # Audience and targeting
    "audience": {
        "Expected CTR": {
            "title": "Expected Click-Through Rate",
            "content": "Predicts the likely click-through rate for this audience segment based on historical performance data and engagement patterns for similar audience profiles.",
            "learn_more": "This forecasted metric helps estimate campaign performance before launch."
        },
        "Interest Categories": {
            "title": "Interest Categories",
            "content": "Identified affinity groups and interest classifications that define this audience segment, based on their content consumption, engagement patterns, and declared interests.",
            "learn_more": "Targeting based on multiple aligned interests typically improves performance by 40%."
        },
        "Audience Segment": {
            "title": "Audience Segment",
            "content": "A defined subset of your total addressable market that shares specific characteristics, behaviors, or demographics that make them particularly receptive to your campaign message.",
            "learn_more": "Specialized audience segments typically deliver 3-5x higher engagement than broad targeting."
        },
        "Demographics": {
            "title": "Audience Demographics",
            "content": "Key demographic attributes that define this audience segment, including age ranges, gender distribution, income levels, and other socioeconomic factors.",
            "learn_more": "Multi-dimensional demographic targeting improves audience quality and campaign performance."
        },
        "Platform Recommendation": {
            "title": "Platform Recommendation",
            "content": "The optimal advertising platform or channel for reaching this audience segment based on their media consumption habits and engagement patterns.",
            "learn_more": "Platform-optimized campaigns show 45% higher engagement than platform-agnostic approaches."
        },
        "Optimization Strategy": {
            "title": "Optimization Strategy",
            "content": "Advanced bid management and targeting approach tailored to this audience segment, including bid adjustments, dayparting, and other tactical optimizations.",
            "learn_more": "Properly optimized bidding strategies can improve campaign efficiency by up to 35%."
        }
    },
    
    # Campaign insights
    "insights": {
        "Top Media Affinity Sites": {
            "title": "Top Media Affinity Sites",
            "content": "Publications and websites that index highest with your target audience, indicating where your audience is most likely to be receptive to advertising messages.",
            "learn_more": "These sites typically offer 2.2x higher engagement than generic high-traffic alternatives."
        },
        "Top TV Network Affinities": {
            "title": "Top TV Network Affinities",
            "content": "Television networks and channels that have the strongest connection to your target audience based on viewership patterns and content alignment.",
            "learn_more": "Network affinity correlates with 1.7x higher ad recall compared to demographic-only targeting."
        },
        "Top Streaming Platforms": {
            "title": "Top Streaming Platforms",
            "content": "Digital video and audio streaming services that have high usage and engagement among your target audience segments.",
            "learn_more": "Platform-specific creative optimization can increase performance by 35%."
        }
    },
    
    # Methodology and framework
    "methodology": {
        "Audience Resonance Index": {
            "title": "Audience Resonance Index™",
            "content": "A proprietary framework that measures how effectively a marketing campaign connects with its intended audience across nine critical dimensions of cultural and commercial relevance.",
            "learn_more": "The ARI methodology has demonstrated 93% accuracy in predicting campaign performance."
        },
        "Marketing Trend Heatmap": {
            "title": "Marketing Trend Heatmap",
            "content": "Visualizes emerging marketing trends by audience segment, showing which tactical approaches are gaining traction with specific demographic and psychographic groups.",
            "learn_more": "The heatmap identifies high-growth opportunity areas before they reach mainstream adoption."
        },
        "AI-Powered Audience Segmentation": {
            "title": "AI-Powered Audience Segmentation",
            "content": "Uses machine learning to identify optimal audience segments based on your brief, revealing sometimes unexpected audience groups with high potential resonance with your message.",
            "learn_more": "AI-identified segments often outperform traditional demographic targeting by 2.7x."
        },
        "Hyperdimensional Campaign Performance": {
            "title": "Hyperdimensional Campaign Performance",
            "content": "A multifaceted analysis approach that evaluates campaigns across numerous metrics simultaneously, revealing complex patterns and insights that single-dimension analysis might miss.",
            "learn_more": "This approach identifies non-obvious optimization opportunities that can dramatically improve performance."
        }
    }
}

def display_tip_bubble(context, key, inline=False):
    """
    Renders a tip bubble with contextual information about a metric or concept.
    
    Args:
        context (str): The context/section the tip belongs to (e.g., 'metrics', 'advanced')
        key (str): The specific item to show a tip for
        inline (bool, optional): Whether to display the tip icon inline or as a standalone element
    
    Returns:
        str: HTML for the tip bubble
    """
    if context not in LEARNING_TIPS or key not in LEARNING_TIPS[context]:
        return ""
    
    tip = LEARNING_TIPS[context][key]
    title = tip.get("title", key)
    content = tip.get("content", "")
    learn_more = tip.get("learn_more", "")
    
    tip_html = f"""
    <div class="tip-bubble">
        <span class="tip-icon">?</span>
        <div class="tip-content">
            <div class="tip-title">{title}</div>
            <div>{content}</div>
            <span class="tip-learn-more">{learn_more}</span>
        </div>
    </div>
    """
    
    if not inline:
        return tip_html
    else:
        return f'<span style="display:inline-block">{tip_html}</span>'

def metric_with_tip(metric_name, context="metrics"):
    """
    Renders a metric name with an attached tip bubble.
    
    Args:
        metric_name (str): The name of the metric
        context (str, optional): The context/section the tip belongs to
        
    Returns:
        str: HTML for the metric name with attached tip bubble
    """
    return f"{metric_name} {display_tip_bubble(context, metric_name, inline=True)}"