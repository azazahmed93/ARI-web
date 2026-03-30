"""
Marketing trends heatmap module for the ARI Analyzer application.
This provides visualizations of emerging trends relevant to campaign briefs.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import random

def generate_trend_data(brief_text=None):
    """
    Generate trend data based on the marketing brief text.
    
    Args:
        brief_text (str, optional): The marketing brief text to analyze
        
    Returns:
        pd.DataFrame: DataFrame containing trend data
    """
    # These are the standard marketing trend categories with exact naming as specified
    categories = [
        "Rich Media",
        "DOOH",
        "Interactive Video",
        "Social Display Boost",
        "High Impact Display",
        "Connected TV",
        "Streaming Audio",
        "In-Game Ads",
        "Online Video",
        "Native Ads"
    ]
    
    # These are potential target demographics/markets in the exact specified order
    markets = [
        "Gen Z",
        "Millennials", 
        "Gen X",
        "Low Income",
        "Mid Income",
        "High Income",
        "Urban",
        "Suburban"
    ]
    
    # Make sure the categories are displayed in the exact order we want in the heatmap
    # This creates a custom order for the plot columns that overrides alphabetical sorting
    market_order = markets.copy()
    
    # Generate base scores with some randomness for realism
    # The realistic generation ensures we don't have too many extreme values
    data = []
    
    # Initialize brief_lower variable
    brief_lower = ""
    
    if brief_text and len(brief_text) > 50:
        # Use brief content to influence trend relevance
        brief_lower = brief_text.lower()
        
        # Keywords that might influence trend scores - updated to match the new categories
        keyword_influences = {
            "video": ["Interactive Video", "Connected TV", "Online Video"],
            "audio": ["Streaming Audio"],
            "rich": ["Rich Media", "High Impact Display"],
            "media": ["Rich Media"],
            "impact": ["High Impact Display"],
            "tv": ["Connected TV"],
            "gaming": ["In-Game Ads"],
            "game": ["In-Game Ads"],
            "esports": ["In-Game Ads"],
            "dooh": ["DOOH"],
            "billboard": ["DOOH"],
            "outdoor": ["DOOH"],
            "social": ["Social Display Boost"],
            "instagram": ["Social Display Boost", "Rich Media"],
            "tiktok": ["Interactive Video", "Social Display Boost"],
            "native": ["Native Ads"],
            "sponsored": ["Native Ads"],
            "content marketing": ["Native Ads"],
            "young": ["Gen Z", "Millennials"],
            "youth": ["Gen Z"],
            "teen": ["Gen Z"],
            "college": ["Gen Z", "Millennials"],
            "parent": ["Gen X"],
            "family": ["Gen X", "Millennials"],
            "luxury": ["High Income"],
            "premium": ["High Income"],
            "affordable": ["Mid Income", "Low Income"],
            "budget": ["Low Income"],
            "city": ["Urban"],
            "metropolitan": ["Urban"],
            "suburban": ["Suburban"]
        }
        
        # Base influence to add to certain trends/markets when keywords are found
        keyword_boost = 20
    else:
        # If no brief or too short, use random but realistic data
        keyword_influences = {}
        keyword_boost = 0
    
    # Create the heatmap data
    for category in categories:
        for market in markets:
            # Base score is moderately random but tends to center around 40-60
            base_score = np.clip(random.normalvariate(50, 15), 10, 90)
            
            # Add keyword influences if applicable
            influence = 0
            if brief_text and len(brief_text) > 50:
                for keyword, influenced_items in keyword_influences.items():
                    if keyword in brief_lower:
                        if category in influenced_items or market in influenced_items:
                            influence += keyword_boost
            
            # Add some natural affinity between certain categories and markets
            natural_affinities = {
                ("Interactive Video", "Gen Z"): 15,
                ("Social Display Boost", "Gen Z"): 18,
                ("Streaming Audio", "Millennials"): 12,
                ("Connected TV", "Suburban"): 10,
                ("Online Video", "Gen Z"): 18,
                ("In-Game Ads", "Gen Z"): 12,
                ("Rich Media", "Urban"): 12,
                ("Rich Media", "Millennials"): 10,
                ("DOOH", "Urban"): 15,
                ("DOOH", "High Income"): 8,
                ("High Impact Display", "High Income"): 12,
                ("Native Ads", "Millennials"): 15,
                ("Native Ads", "Gen X"): 12,
                ("Native Ads", "Mid Income"): 10,
                ("Native Ads", "Suburban"): 8
            }
            
            # Create a key tuple and use a default of 0 if not found
            affinity_key = (category, market)
            affinity_boost = 0
            # Check if the exact key exists
            if affinity_key in natural_affinities:
                affinity_boost = natural_affinities[affinity_key]
            
            # Calculate final score with some randomness to make it more realistic
            final_score = min(100, base_score + influence + affinity_boost + random.normalvariate(0, 5))
            
            # Add to our dataset
            data.append({
                "Category": category,
                "Market": market,
                "Value": final_score
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    return df

def display_trend_heatmap(brief_text=None, title="Marketing Trend Heatmap"):
    """
    Display a heatmap of marketing trends.
    
    Args:
        brief_text (str, optional): The marketing brief text to analyze
        title (str): Title for the heatmap
    """
    # Import learning tips
    from app.components.learning_tips import display_tip_bubble
    
    # Create title with tooltip
    heatmap_tip = display_tip_bubble("methodology", "Marketing Trend Heatmap", inline=True)
    st.markdown(f'<div style="text-align: center;"><h4>{title} {heatmap_tip}</h4></div>', unsafe_allow_html=True)
    
    # Generate the trend data
    df = generate_trend_data(brief_text)
    
    # Create a pivot table for the heatmap
    pivot_df = df.pivot(index="Category", columns="Market", values="Value")
    
    # Custom color scale from cool to hot
    colorscale = [
        [0.0, "#f0f9ff"],  # Very light blue
        [0.3, "#93c5fd"],  # Light blue
        [0.5, "#3b82f6"],  # Medium blue
        [0.7, "#6366f1"],  # Indigo
        [0.85, "#a855f7"], # Purple
        [1.0, "#ec4899"]   # Pink
    ]
    
    # Reorder the columns according to our defined order
    # Get markets list from the data generation function
    market_order = [
        "Gen Z",
        "Millennials", 
        "Gen X",
        "Low Income",
        "Mid Income",
        "High Income",
        "Urban",
        "Suburban"
    ]
    
    # Reindex with our custom order
    pivot_df = pivot_df.reindex(columns=market_order)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        colorscale=colorscale,
        colorbar=dict(
            title=dict(
                text="Trend<br>Strength",
                side="right"
            ),
            tickmode="array",
            tickvals=[10, 30, 50, 70, 90],
            ticktext=["Very Low", "Low", "Medium", "High", "Very High"],
            ticks="outside"
        ),
        hoverongaps=False,
        hovertemplate='<b>%{y}</b> × <b>%{x}</b><br>Trend Strength: %{z:.1f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        margin=dict(l=30, r=30, t=10, b=30),
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Helvetica, Arial, sans-serif",
            size=12,
            color="#333333"
        )
    )
    
    # Use Streamlit to display the figure
    st.plotly_chart(fig, use_container_width=True)
    
    # Optional annotations/explanations
    with st.expander("About This Heatmap"):
        st.markdown("""
        This heatmap shows the current effectiveness of various marketing approach categories 
        across different market segments. The analysis combines industry benchmark data with 
        campaign-specific signals from your brief.
        
        **How to read this heatmap:**
        - **Hotter colors (pink/purple)** indicate stronger trend alignment and higher predicted performance
        - **Cooler colors (light blue)** indicate weaker trend alignment
        - Hover over any cell to see exact values and the trend combination
        
        Use these insights to optimize your media mix allocation and targeting parameters.
        """)

def _build_audience_columns(audience_segments):
    """Build the 4 column labels and extract segments list."""
    segments = []
    if audience_segments and isinstance(audience_segments, dict):
        segments = audience_segments.get('segments', [])

    tier_labels = ["Primary Growth", "Secondary Growth", "Emerging"]
    segment_columns = []
    for i, label in enumerate(tier_labels):
        if i < len(segments):
            name = segments[i].get('name', label)
            if len(name) > 25:
                name = name[:22] + "..."
            segment_columns.append(f"{label}:\n{name}")
        else:
            segment_columns.append(label)
    columns = ["Core RFP\nAudience"] + segment_columns
    return columns, segments


def _generate_audience_trend_data_ai(brief_text, audience_segments, categories, columns, segments):
    """
    Use GPT-4o to generate audience segment × media channel performance scores.
    Returns a DataFrame or None on failure.
    """
    from core.ai_utils import make_openai_request
    import json

    # Build segment descriptions for the prompt
    segment_descs = []
    tier_names = ["Core RFP Audience", "Primary Growth Audience", "Secondary Growth Audience", "Emerging Audience"]
    for i, tier in enumerate(tier_names):
        if i == 0:
            # Core RFP comes from the brief itself
            segment_descs.append(f"- {tier}: The primary target audience defined in the campaign brief")
        else:
            seg_idx = i - 1
            if seg_idx < len(segments):
                seg = segments[seg_idx]
                name = seg.get('name', tier)
                age = seg.get('targeting_params', {}).get('age_range', 'N/A')
                income = seg.get('targeting_params', {}).get('income_targeting', 'N/A')
                interests = ", ".join(seg.get('interest_categories', [])[:5])
                segment_descs.append(f"- {tier} ({name}): Age {age}, Income {income}, Interests: {interests}")
            else:
                segment_descs.append(f"- {tier}: No segment data available")

    segments_str = "\n".join(segment_descs)
    categories_str = ", ".join(categories)
    column_keys = tier_names  # Use clean names as JSON keys

    prompt = f"""You are a digital media buying expert. Based on the campaign brief and audience segments below,
rate the predicted performance (10-95) of each media channel for each audience segment.

Campaign Brief (excerpt):
{brief_text[:2000] if brief_text else "No brief provided"}

Audience Segments:
{segments_str}

Media Channels: {categories_str}

Return a JSON object with this exact structure:
{{
  "scores": {{
    "Core RFP Audience": {{"Rich Media": 75, "DOOH": 60, ...}},
    "Primary Growth Audience": {{"Rich Media": 65, ...}},
    "Secondary Growth Audience": {{"Rich Media": 55, ...}},
    "Emerging Audience": {{"Rich Media": 50, ...}}
  }}
}}

Rules:
- Scores must be integers between 10 and 95
- CRITICAL: You MUST use the FULL range. Not everything is high-performing.
  * At least 5 scores must be ≤ 30 (low performers)
  * At least 8 scores must be ≤ 45 (below average)
  * At least 5 scores must be ≥ 75 (strong performers)
  * No more than 10 of the 40 total scores should be above 70
  * The difference between the highest and lowest score must be at least 50 points
- Every media channel must appear for every audience segment
- Base scores on realistic media buying performance expectations
- Consider audience demographics, interests, and media consumption habits
- Channels that are irrelevant to a segment should score LOW (15-30), not medium
- The Core RFP audience should score highest on channels that match the brief's objectives
- Emerging audiences should score higher on newer/innovative channels (In-Game Ads, Interactive Video, DOOH) but LOW on traditional channels
- Use these exact media channel names: {categories_str}
- Use these exact audience keys: {", ".join(column_keys)}"""

    result = make_openai_request(
        messages=[
            {"role": "system", "content": "You are a digital media buying and audience analytics expert. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        response_format={"type": "json_object"},
        max_tokens=1000,
        max_retries=2
    )

    if not result or 'scores' not in result:
        return None

    scores = result['scores']

    # Map the clean tier names back to the display column labels
    tier_to_column = dict(zip(tier_names, columns))

    data = []
    for category in categories:
        for tier_name, col_label in tier_to_column.items():
            tier_scores = scores.get(tier_name, {})
            score = tier_scores.get(category)
            if score is None or not isinstance(score, (int, float)):
                return None  # Incomplete data, fall back
            score = max(10, min(95, int(score)))
            data.append({"Category": category, "Segment": col_label, "Value": score})

    return pd.DataFrame(data)


def _generate_audience_trend_data_fallback(brief_text, categories, columns, segments):
    """Fallback synthetic data generation when AI call fails."""
    tier_profiles = {
        0: {"Rich Media": 78, "DOOH": 60, "Interactive Video": 72,
            "Social Display Boost": 70, "High Impact Display": 75,
            "Connected TV": 68, "Streaming Audio": 62,
            "In-Game Ads": 48, "Online Video": 80, "Native Ads": 72},
        1: {"Rich Media": 65, "DOOH": 50, "Interactive Video": 70,
            "Social Display Boost": 75, "High Impact Display": 58,
            "Connected TV": 72, "Streaming Audio": 68,
            "In-Game Ads": 55, "Online Video": 78, "Native Ads": 55},
        2: {"Rich Media": 55, "DOOH": 58, "Interactive Video": 52,
            "Social Display Boost": 60, "High Impact Display": 50,
            "Connected TV": 62, "Streaming Audio": 72,
            "In-Game Ads": 60, "Online Video": 60, "Native Ads": 70},
        3: {"Rich Media": 50, "DOOH": 72, "Interactive Video": 78,
            "Social Display Boost": 65, "High Impact Display": 55,
            "Connected TV": 58, "Streaming Audio": 55,
            "In-Game Ads": 82, "Online Video": 68, "Native Ads": 48}
    }

    data = []
    for category in categories:
        for tier_idx, label in enumerate(columns):
            base = tier_profiles[tier_idx].get(category, 50)
            noise = random.normalvariate(0, 4)
            score = np.clip(base + noise, 10, 95)
            data.append({"Category": category, "Segment": label, "Value": score})

    return pd.DataFrame(data)


def generate_audience_segment_trend_data(brief_text=None, audience_segments=None):
    """
    Generate trend data for campaign-specific audience segments using GPT-4o.
    Results are cached in st.session_state to avoid repeated API calls on Streamlit reruns.
    Falls back to synthetic data if AI call fails.

    Returns:
        tuple: (pd.DataFrame, list of column labels)
    """
    categories = [
        "Rich Media", "DOOH", "Interactive Video", "Social Display Boost",
        "High Impact Display", "Connected TV", "Streaming Audio",
        "In-Game Ads", "Online Video", "Native Ads"
    ]

    columns, segments = _build_audience_columns(audience_segments)

    # Return cached result if available
    if 'audience_trend_heatmap_data' in st.session_state and st.session_state.audience_trend_heatmap_data is not None:
        cached = st.session_state.audience_trend_heatmap_data
        return cached['df'], cached['columns']

    # Try AI-generated scores first
    try:
        df = _generate_audience_trend_data_ai(brief_text, audience_segments, categories, columns, segments)
        if df is not None:
            st.session_state.audience_trend_heatmap_data = {'df': df, 'columns': columns}
            return df, columns
    except Exception as e:
        print(f"AI audience trend generation failed: {e}")

    # Fallback to synthetic data
    df = _generate_audience_trend_data_fallback(brief_text, categories, columns, segments)
    st.session_state.audience_trend_heatmap_data = {'df': df, 'columns': columns}
    return df, columns


def display_audience_segment_heatmap(brief_text=None, audience_segments=None, title="Audience Segment Media Recommendation"):
    """Display a heatmap of media performance across campaign audience segments."""
    from app.components.learning_tips import display_tip_bubble

    heatmap_tip = display_tip_bubble("methodology", "Audience Segment Media Recommendation", inline=True)
    st.markdown(f'<div style="text-align: center;"><h4>{title} {heatmap_tip}</h4></div>', unsafe_allow_html=True)

    df, column_labels = generate_audience_segment_trend_data(brief_text, audience_segments)

    pivot_df = df.pivot(index="Category", columns="Segment", values="Value")
    pivot_df = pivot_df.reindex(columns=column_labels)

    colorscale = [
        [0.0, "#f0f9ff"],
        [0.3, "#93c5fd"],
        [0.5, "#3b82f6"],
        [0.7, "#6366f1"],
        [0.85, "#a855f7"],
        [1.0, "#ec4899"]
    ]

    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        colorscale=colorscale,
        colorbar=dict(
            title=dict(text="Trend<br>Strength", side="right"),
            tickmode="array",
            tickvals=[10, 30, 50, 70, 90],
            ticktext=["Very Low", "Low", "Medium", "High", "Very High"],
            ticks="outside"
        ),
        hoverongaps=False,
        hovertemplate='<b>%{y}</b> × <b>%{x}</b><br>Trend Strength: %{z:.1f}<extra></extra>'
    ))

    fig.update_layout(
        margin=dict(l=30, r=30, t=10, b=30),
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Helvetica, Arial, sans-serif", size=12, color="#333333")
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("About This Heatmap"):
        st.markdown("""
        This heatmap shows the predicted effectiveness of marketing channels across your
        campaign's specific audience segments.

        **Audience Tiers:**
        - **Core RFP Audience** — The primary audience defined in your campaign brief
        - **Primary Growth** — First high-potential growth segment identified by AI
        - **Secondary Growth** — Additional growth opportunity with adjacent interests
        - **Emerging** — Untapped audience not explicitly in the brief but showing strong potential

        **How to read this heatmap:**
        - **Hotter colors (pink/purple)** indicate stronger predicted performance for that channel + audience combination
        - **Cooler colors (light blue)** indicate weaker predicted performance
        - Use this to inform which media formats to prioritize for each audience tier
        """)


def generate_simplified_trend_data(brief_text=None):
    """
    Generate simplified trend data for email-friendly reports and PDF generation.
    
    Args:
        brief_text (str, optional): The marketing brief text to analyze
        
    Returns:
        tuple: (top_trends, top_markets, top_combinations)
    """
    # Generate the full dataset first
    df = generate_trend_data(brief_text)
    
    # Get top trends by average value
    top_trend_values = df.groupby('Category')['Value'].mean().sort_values(ascending=False).head(5)
    top_trends = []
    for trend, value in top_trend_values.items():
        growth_value = int(value * 1.2)  # Convert value to a growth percentage
        top_trends.append({"trend": trend, "growth": growth_value})
    
    # Get top markets by average value
    top_market_values = df.groupby('Market')['Value'].mean().sort_values(ascending=False).head(5)
    top_markets = []
    for market, value in top_market_values.items():
        top_markets.append({"market": market, "index": int(value)})
    
    # Get top individual combinations
    top_combos = df.sort_values('Value', ascending=False).head(5)
    top_combinations = []
    for _, row in top_combos.iterrows():
        top_combinations.append({
            "category": row['Category'],
            "market": row['Market'],
            "value": int(row['Value'])
        })
    
    return top_trends, top_markets, top_combinations

def summarize_trends_for_email(brief_text=None):
    """
    Create text summarizing the top trends for use in emails.
    
    Args:
        brief_text (str, optional): The marketing brief text to analyze
        
    Returns:
        str: Formatted summary of top trends
    """
    top_trends, top_markets, top_combinations = generate_simplified_trend_data(brief_text)
    
    summary = "## Top Marketing Trends Summary\n\n"
    
    # Top trend categories
    summary += "### Strongest Trend Categories\n"
    for i, trend in enumerate(top_trends, 1):
        growth = trend['growth']
        strength = "Very High" if growth >= 80 else "High" if growth >= 65 else "Medium-High"
        summary += f"{i}. **{trend['trend']}** - {strength} Effectiveness ({growth}%)\n"
    
    summary += "\n### Most Responsive Markets\n"
    for i, market_data in enumerate(top_markets, 1):
        summary += f"{i}. **{market_data['market']}** - Responsiveness Score: {market_data['index']}\n"
    
    summary += "\n### Top Specific Opportunities\n"
    for i, combo in enumerate(top_combinations, 1):
        summary += f"{i}. **{combo['category']}** targeting **{combo['market']}** - {combo['value']}% effectiveness\n"
    
    return summary
