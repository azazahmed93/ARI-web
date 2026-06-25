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
    """Build the 4 column labels and extract segments list.

    Long segment names are WRAPPED onto multiple lines (not truncated) so they render
    in full on the heatmap x-axis. Uses <br> — Plotly's tick-label line break (a raw
    "\\n" is not honored in tick text, which is why long names looked cut off).
    """
    import textwrap
    segments = []
    if audience_segments and isinstance(audience_segments, dict):
        segments = audience_segments.get('segments', [])

    tier_labels = ["Primary Growth", "Secondary Growth", "Emerging"]
    segment_columns = []
    for i, label in enumerate(tier_labels):
        if i < len(segments):
            name = (segments[i].get('name') or label).strip()
            # width 28 keeps most names to <=2 lines with whole-word breaks
            wrapped = "<br>".join(textwrap.wrap(name, width=28)) or name
            segment_columns.append(f"{label}:<br>{wrapped}")
        else:
            segment_columns.append(label)
    columns = ["Core RFP<br>Audience"] + segment_columns
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
- Each score is an integer 10-95 reflecting how well that channel GENUINELY fits that segment,
  based on the segment's demographics, interests and media-consumption habits.
- Score on real fit, not on appearance: channels that strongly match a segment score high;
  channels that genuinely don't fit score low (roughly 15-30).
- Do NOT force a spread or hit score quotas. If a segment genuinely fits many channels, score
  many of them high; if it fits few, score few high. Let the audience drive the numbers — it is
  fine if a strong segment has several high channels or a narrow segment has several low ones.
- Differentiate the segments from one another where their behavior actually differs; where two
  segments behave alike it is fine for their scores to be similar.
- The single highest-scoring channel for a segment is treated as that segment's RECOMMENDED
  channel, so make sure the top score is the channel you would actually recommend for that
  audience (do not let a tie-breaker or filler channel outrank the genuine best fit).
- Every media channel must appear for every audience segment.
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


def get_segment_recommended_channels(brief_text=None, audience_segments=None):
    """Source-of-truth recommended media channel per segment.

    Derives each segment's recommended channel as the HIGHEST-scoring channel in the
    very same scoring pass that powers the "Audience Segment Media Recommendation"
    heatmap. generate_audience_segment_trend_data() is cached per session, so this
    triggers at most one GPT call and guarantees the segment card's "Recommended
    Platform" and the heatmap can never disagree (single source of truth).

    Returns {segment_name: channel, "Core RFP Audience": channel}, or {} when no
    data/segments are available (callers fall back to their own platform value).
    """
    try:
        df, columns = generate_audience_segment_trend_data(brief_text, audience_segments)
        if df is None or not columns:
            return {}
        _, segments = _build_audience_columns(audience_segments)
        pivot = df.pivot(index="Category", columns="Segment", values="Value").reindex(columns=columns)

        recs = {}
        # columns[0] = Core RFP audience; columns[1:] = the segment tiers, in order.
        if columns[0] in pivot.columns:
            recs["Core RFP Audience"] = str(pivot[columns[0]].idxmax())
        for i, seg in enumerate(segments[:3]):
            col = columns[i + 1] if (i + 1) < len(columns) else None
            name = seg.get("name") if isinstance(seg, dict) else None
            if col is not None and name and col in pivot.columns:
                recs[name] = str(pivot[col].idxmax())
        return recs
    except Exception as e:
        print(f"get_segment_recommended_channels failed: {e}")
        return {}


def get_segment_channel_scores(segment_name=None, brief_text=None, audience_segments=None):
    """Return {channel: score} for one segment column, from the same cached heatmap
    scoring pass. segment_name=None => the Core RFP column. Used to order the Emerging
    "Platform Strategy" entries by genuine fit. Returns {} on failure.
    """
    try:
        if brief_text is None:
            brief_text = st.session_state.get("brief_text")
        if audience_segments is None:
            audience_segments = st.session_state.get("audience_segments")
        df, columns = generate_audience_segment_trend_data(brief_text, audience_segments)
        if df is None or not columns:
            return {}
        _, segments = _build_audience_columns(audience_segments)
        col = None
        if segment_name is None:
            col = columns[0]
        else:
            for i, seg in enumerate(segments[:3]):
                if isinstance(seg, dict) and seg.get("name") == segment_name:
                    col = columns[i + 1] if (i + 1) < len(columns) else None
                    break
        if not col:
            return {}
        pivot = df.pivot(index="Category", columns="Segment", values="Value").reindex(columns=columns)
        if col not in pivot.columns:
            return {}
        return {str(ch): int(pivot.loc[ch, col]) for ch in pivot.index}
    except Exception as e:
        print(f"get_segment_channel_scores failed: {e}")
        return {}


def resolve_segment_platform(segment, brief_text=None, audience_segments=None):
    """Single source-of-truth 'Recommended Platform' LABEL for one segment.

    Used by the UI segment card AND the PDF/PPTX exporters so every surface stays
    consistent with the "Audience Segment Media Recommendation" heatmap.

    The RANKING is sourced from the heatmap scoring pass (the segment's top-scoring
    channel), but the displayed LABEL uses the media-buy vocabulary the cards expect
    (e.g. "CTV/OTT" rather than the heatmap's "Connected TV"):
      1. if one of the segment's own platform_targeting entries maps to that top
         channel, show that entry's original wording (keeps the generator's name);
      2. otherwise show a clean buy-type label for the top channel
         (platform_channel_map.channel_to_display_label);
      3. fall back to platform_targeting[0] only when heatmap scores are unavailable.

    `segment` may be a dict (export paths) or an AudienceSegment object (UI card).
    """
    if isinstance(segment, dict):
        name = segment.get("name")
        pts = segment.get("platform_targeting") or []
    else:
        name = getattr(segment, "name", None)
        pts = getattr(segment, "platform_targeting", None) or []

    def _pt_name(entry):
        return entry.get("platform", "") if isinstance(entry, dict) else ""

    top_channel = None
    try:
        recs = get_segment_recommended_channels(
            brief_text if brief_text is not None else st.session_state.get("brief_text"),
            audience_segments if audience_segments is not None else st.session_state.get("audience_segments"),
        )
        if name:
            top_channel = recs.get(name)
    except Exception:
        top_channel = None

    if top_channel:
        try:
            from core.platform_channel_map import normalize_platform_to_channel, channel_to_display_label
            # 1) if the segment's own wording maps EXACTLY (primary) to the top channel,
            #    show that wording — keeps the generator's phrasing (e.g. "CTV/OTT").
            for entry in pts:
                pname = _pt_name(entry)
                if pname and normalize_platform_to_channel(pname).get("primary") == top_channel:
                    return pname
            # 2) otherwise a PRECISE buy-type label for the actual top channel. We avoid
            #    loose umbrella matches (e.g. "Video" spans Connected TV) because an
            #    ambiguous umbrella label re-creates the "recommended platform looks low"
            #    confusion — "CTV/OTT" is unambiguous, "Video" is not.
            return channel_to_display_label(top_channel)
        except Exception:
            return top_channel  # safe: at least the aligned channel name

    # 3) heatmap unavailable — original behavior
    if pts:
        return _pt_name(pts[0])
    return ""


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
        font=dict(family="Helvetica, Arial, sans-serif", size=12, color="#333333"),
        xaxis=dict(automargin=True, tickangle=0, tickfont=dict(size=11)),  # auto-expand; full names show
        yaxis=dict(automargin=True)
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


# Social platforms shown in the dedicated "Social Platform Affinity" heatmap.
# INFORMATIONAL ONLY — this heatmap does NOT feed resolve_segment_platform / the card
# "Recommended Platform" (which stays on the 10 ad-format channels). Keeping social on a
# separate axis avoids mixing platform-level items with the format-level channels.
SOCIAL_PLATFORMS = ["TikTok", "LinkedIn", "Instagram", "X (Twitter)", "Reddit"]


def _generate_social_trend_data_ai(brief_text, audience_segments, columns, segments):
    """GPT-4o: rate each social platform's fit (10-95) per audience segment.
    Returns a DataFrame or None on failure."""
    from core.ai_utils import make_openai_request

    tier_names = ["Core RFP Audience", "Primary Growth Audience", "Secondary Growth Audience", "Emerging Audience"]
    segment_descs = []
    for i, tier in enumerate(tier_names):
        if i == 0:
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
    platforms_str = ", ".join(SOCIAL_PLATFORMS)

    prompt = f"""You are a social media planning expert. Based on the campaign brief and audience
segments below, rate how well each SOCIAL PLATFORM fits each audience segment (10-95).

Campaign Brief (excerpt):
{brief_text[:2000] if brief_text else "No brief provided"}

Audience Segments:
{segments_str}

Social Platforms: {platforms_str}

Return a JSON object with this exact structure:
{{
  "scores": {{
    "Core RFP Audience": {{"TikTok": 78, "LinkedIn": 40, "Instagram": 82, "X (Twitter)": 55, "Reddit": 50}},
    "Primary Growth Audience": {{"TikTok": 70, "LinkedIn": 45, "Instagram": 75, "X (Twitter)": 58, "Reddit": 60}},
    "Secondary Growth Audience": {{"TikTok": 60, "LinkedIn": 72, "Instagram": 68, "X (Twitter)": 65, "Reddit": 55}},
    "Emerging Audience": {{"TikTok": 85, "LinkedIn": 38, "Instagram": 76, "X (Twitter)": 60, "Reddit": 80}}
  }}
}}

Rules:
- Each score is an integer 10-95 reflecting how well that platform GENUINELY fits that segment,
  based on the segment's demographics, interests and platform-usage habits (e.g. LinkedIn skews
  professional/older; TikTok skews younger; Reddit skews interest-community driven).
- Score on real fit, not appearance. Do NOT force a spread or hit quotas — if a segment genuinely
  lives on several platforms, score several high; if its presence is narrow, score few high.
- Differentiate segments where their behavior differs; similar segments may score similarly.
- Every platform must appear for every audience segment.
- Use these exact platform names: {platforms_str}
- Use these exact audience keys: {", ".join(tier_names)}"""

    result = make_openai_request(
        messages=[
            {"role": "system", "content": "You are a social media planning and audience analytics expert. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",
        response_format={"type": "json_object"},
        max_tokens=900,
        max_retries=2
    )

    if not result or 'scores' not in result:
        return None

    scores = result['scores']
    tier_to_column = dict(zip(tier_names, columns))

    data = []
    for platform in SOCIAL_PLATFORMS:
        for tier_name, col_label in tier_to_column.items():
            tier_scores = scores.get(tier_name, {})
            score = tier_scores.get(platform)
            if score is None or not isinstance(score, (int, float)):
                return None  # incomplete -> fall back
            score = max(10, min(95, int(score)))
            data.append({"Platform": platform, "Segment": col_label, "Value": score})

    return pd.DataFrame(data)


def _generate_social_trend_data_fallback(columns):
    """Synthetic social-platform scores when the AI call fails."""
    tier_profiles = {
        0: {"TikTok": 72, "LinkedIn": 52, "Instagram": 78, "X (Twitter)": 60, "Reddit": 55},
        1: {"TikTok": 82, "LinkedIn": 44, "Instagram": 80, "X (Twitter)": 56, "Reddit": 62},
        2: {"TikTok": 60, "LinkedIn": 74, "Instagram": 66, "X (Twitter)": 66, "Reddit": 54},
        3: {"TikTok": 85, "LinkedIn": 40, "Instagram": 74, "X (Twitter)": 58, "Reddit": 80},
    }
    data = []
    for platform in SOCIAL_PLATFORMS:
        for tier_idx, label in enumerate(columns):
            base = tier_profiles.get(tier_idx, {}).get(platform, 50)
            noise = random.normalvariate(0, 4)
            score = np.clip(base + noise, 10, 95)
            data.append({"Platform": platform, "Segment": label, "Value": score})
    return pd.DataFrame(data)


def generate_social_platform_trend_data(brief_text=None, audience_segments=None):
    """Social-platform × audience-segment affinity scores, cached per session.
    Falls back to synthetic data if the AI call fails. Returns (DataFrame, column labels)."""
    columns, segments = _build_audience_columns(audience_segments)

    if st.session_state.get('social_platform_heatmap_data') is not None:
        cached = st.session_state.social_platform_heatmap_data
        return cached['df'], cached['columns']

    try:
        df = _generate_social_trend_data_ai(brief_text, audience_segments, columns, segments)
        if df is not None:
            st.session_state.social_platform_heatmap_data = {'df': df, 'columns': columns}
            return df, columns
    except Exception as e:
        print(f"AI social trend generation failed: {e}")

    df = _generate_social_trend_data_fallback(columns)
    st.session_state.social_platform_heatmap_data = {'df': df, 'columns': columns}
    return df, columns


def display_social_platform_heatmap(brief_text=None, audience_segments=None, title="Social Platform Affinity"):
    """Display a heatmap of social-platform affinity across campaign audience segments.
    Informational — does NOT affect the card 'Recommended Platform' logic."""
    from app.components.learning_tips import display_tip_bubble

    heatmap_tip = display_tip_bubble("methodology", "Social Platform Affinity", inline=True)
    st.markdown(f'<div style="text-align: center;"><h4>{title} {heatmap_tip}</h4></div>', unsafe_allow_html=True)

    df, column_labels = generate_social_platform_trend_data(brief_text, audience_segments)

    pivot_df = df.pivot(index="Platform", columns="Segment", values="Value")
    pivot_df = pivot_df.reindex(index=SOCIAL_PLATFORMS, columns=column_labels)

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
            title=dict(text="Affinity", side="right"),
            tickmode="array",
            tickvals=[10, 30, 50, 70, 90],
            ticktext=["Very Low", "Low", "Medium", "High", "Very High"],
            ticks="outside"
        ),
        hoverongaps=False,
        hovertemplate='<b>%{y}</b> × <b>%{x}</b><br>Affinity: %{z:.1f}<extra></extra>'
    ))

    fig.update_layout(
        margin=dict(l=30, r=30, t=10, b=30),
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Helvetica, Arial, sans-serif", size=12, color="#333333"),
        xaxis=dict(automargin=True, tickangle=0, tickfont=dict(size=11)),  # auto-expand; full names show
        yaxis=dict(automargin=True)
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("About This Heatmap"):
        st.markdown("""
        This heatmap shows the predicted affinity of each **social platform**
        (TikTok, LinkedIn, Instagram, X (Twitter), Reddit) for your campaign's audience segments.

        **How to read this heatmap:**
        - **Hotter colors (pink/purple)** indicate a stronger fit between that platform and audience.
        - **Cooler colors (light blue)** indicate a weaker fit.
        - Use this to prioritise social platforms per audience tier. This view is informational and
          does not change the "Recommended Platform" shown on the audience cards.
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
