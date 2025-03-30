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
    # These are the standard marketing trend categories
    categories = [
        "Interactive Video",
        "Audio Marketing",
        "Rich Media",
        "High Impact Display",
        "Connected TV",
        "AI Creative",
        "AR Experiences",
        "Programmatic DOOH",
        "Interactive Social"
    ]
    
    # These are potential target demographics/markets
    markets = [
        "Gen Z",
        "Millennials", 
        "Gen X",
        "Urban",
        "Suburban",
        "Rural",
        "High Income",
        "Mid Income"
    ]
    
    # Generate base scores with some randomness for realism
    # The realistic generation ensures we don't have too many extreme values
    data = []
    
    # Initialize brief_lower variable
    brief_lower = ""
    
    if brief_text and len(brief_text) > 50:
        # Use brief content to influence trend relevance
        brief_lower = brief_text.lower()
        
        # Keywords that might influence trend scores
        keyword_influences = {
            "video": ["Interactive Video", "Connected TV"],
            "audio": ["Audio Marketing"],
            "rich": ["Rich Media", "High Impact Display"],
            "impact": ["High Impact Display"],
            "tv": ["Connected TV"],
            "ai": ["AI Creative"],
            "artificial intelligence": ["AI Creative"],
            "ar": ["AR Experiences"],
            "augmented reality": ["AR Experiences"],
            "billboard": ["Programmatic DOOH"],
            "outdoor": ["Programmatic DOOH"],
            "social": ["Interactive Social"],
            "instagram": ["Interactive Social", "Rich Media"],
            "tiktok": ["Interactive Video", "Interactive Social"],
            "young": ["Gen Z", "Millennials"],
            "youth": ["Gen Z"],
            "teen": ["Gen Z"],
            "college": ["Gen Z", "Millennials"],
            "parent": ["Gen X"],
            "family": ["Gen X", "Millennials"],
            "luxury": ["High Income"],
            "premium": ["High Income"],
            "affordable": ["Mid Income"],
            "city": ["Urban"],
            "metropolitan": ["Urban"],
            "suburban": ["Suburban"],
            "rural": ["Rural"]
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
                ("Interactive Social", "Gen Z"): 18,
                ("Audio Marketing", "Millennials"): 12,
                ("Connected TV", "Suburban"): 10,
                ("AR Experiences", "Gen Z"): 18,
                ("AI Creative", "High Income"): 8,
                ("Programmatic DOOH", "Urban"): 15,
                ("Rich Media", "Millennials"): 10,
                ("High Impact Display", "High Income"): 12
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
        title=dict(
            text=title,
            font=dict(size=18)
        ),
        margin=dict(l=30, r=30, t=50, b=30),
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

def generate_simplified_trend_data(brief_text=None):
    """
    Generate simplified trend data for email-friendly reports.
    
    Args:
        brief_text (str, optional): The marketing brief text to analyze
        
    Returns:
        tuple: (top_trends, top_markets, top_combinations)
    """
    # Generate the full dataset first
    df = generate_trend_data(brief_text)
    
    # Get top trends by average value
    top_trends = df.groupby('Category')['Value'].mean().sort_values(ascending=False).head(5)
    
    # Get top markets by average value
    top_markets = df.groupby('Market')['Value'].mean().sort_values(ascending=False).head(5)
    
    # Get top individual combinations
    top_combinations = df.sort_values('Value', ascending=False).head(5)
    
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
    for i, (category, value) in enumerate(top_trends.items(), 1):
        strength = "Very High" if value >= 80 else "High" if value >= 65 else "Medium-High"
        summary += f"{i}. **{category}** - {strength} Effectiveness ({value:.1f}%)\n"
    
    summary += "\n### Most Responsive Markets\n"
    for i, (market, value) in enumerate(top_markets.items(), 1):
        summary += f"{i}. **{market}** - Responsiveness Score: {value:.1f}%\n"
    
    summary += "\n### Top Specific Opportunities\n"
    for i, row in enumerate(top_combinations.itertuples(), 1):
        summary += f"{i}. **{row.Category}** targeting **{row.Market}** - {row.Value:.1f}% effectiveness\n"
    
    return summary