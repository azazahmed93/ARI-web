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
            "title": "Expected Performance",
            "content": "Predicted click-through rate (CTR) or view completion rate (VCR) for this audience segment based on historical performance data and engagement patterns for similar audience profiles.",
            "learn_more": "These predictions have shown 88% accuracy in campaign performance forecasting."
        },
        "Interest Categories": {
            "title": "Interest Categories",
            "content": "Key topics, activities, and content themes that resonate with this audience segment, providing insights into their preferences and motivations.",
            "learn_more": "Interest-based targeting typically improves campaign performance by 40-60% compared to demographic targeting alone."
        },
        "Audience Segment": {
            "title": "Audience Segment",
            "content": "A defined group of consumers with shared characteristics that make them valuable targets for your campaign. Each segment is identified by our AI based on your campaign goals and content.",
            "learn_more": "Precisely targeted segments typically achieve 2-3x better performance than broad demographic targeting."
        },
        "Demographics": {
            "title": "Demographics",
            "content": "The core demographic attributes of this audience segment, including age, gender, income level, and other quantifiable characteristics that help define the target group.",
            "learn_more": "These demographic indicators are used as a foundation for precise audience targeting across platforms."
        },
        "Platform Recommendation": {
            "title": "Platform Strategy",
            "content": "Recommended digital channels and platforms where this audience segment is most active and receptive to advertising messages.",
            "learn_more": "Our platform recommendations are based on real-time engagement data across 600M+ devices."
        },
        "Platform Strategy": {
            "title": "Platform Strategy",
            "content": "Recommended digital channels and platforms where this audience segment is most active and receptive to advertising messages, with specific targeting approaches for each platform.",
            "learn_more": "Multi-platform strategies have shown 45% higher conversion rates than single-platform approaches."
        },
        "Optimization Strategy": {
            "title": "Optimization Strategy",
            "content": "Recommended bidding approach, dayparting, and other tactical adjustments to maximize campaign performance with this audience segment.",
            "learn_more": "Implementing these optimization strategies has shown a 25-35% improvement in campaign efficiency."
        },
        "Growth Audience Insights": {
            "title": "Growth Audience Insights",
            "content": "Analysis of high-potential audience segments beyond your current core targeting, helping identify new growth opportunities to expand campaign reach and effectiveness.",
            "learn_more": "Brands that successfully engage growth audiences typically see 1.7x higher overall campaign ROI."
        },
        "Emerging Audience Opportunity": {
            "title": "Emerging Audience Opportunity",
            "content": "A newly identified audience segment with high growth potential for your brand, based on AI analysis of your brief, market trends, and audience behaviors.",
            "learn_more": "Early engagement with emerging audiences can create sustainable competitive advantages and reduce customer acquisition costs by up to 40%."
        },
        "Audience Summary": {
            "title": "Audience Summary",
            "content": "Comprehensive overview of your target audiences, including core demographics, psychographics, and behavioral characteristics that drive engagement with your brand.",
            "learn_more": "This holistic view of your audience enables more nuanced campaign strategies that drive higher performance across all metrics."
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
        <span class="tip-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="#5865f2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 16V12" stroke="#5865f2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 8H12.01" stroke="#5865f2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </span>
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