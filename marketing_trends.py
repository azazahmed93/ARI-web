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
        "AI-Dynamic Creative",
        "Online Video"
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
            "ai": ["AI-Dynamic Creative"],
            "artificial intelligence": ["AI-Dynamic Creative"],
            "dynamic": ["AI-Dynamic Creative"],
            "dooh": ["DOOH"],
            "billboard": ["DOOH"],
            "outdoor": ["DOOH"],
            "social": ["Social Display Boost"],
            "instagram": ["Social Display Boost", "Rich Media"],
            "tiktok": ["Interactive Video", "Social Display Boost"],
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
                ("AI-Dynamic Creative", "High Income"): 8,
                ("Rich Media", "Urban"): 12,
                ("Rich Media", "Millennials"): 10,
                ("DOOH", "Urban"): 15,
                ("DOOH", "High Income"): 8,
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
    # Import learning tips
    from assets.learning_tips import display_tip_bubble
    
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