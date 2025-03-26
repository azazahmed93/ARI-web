import base64
import io
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.backends.backend_pdf import PdfPages

def create_pdf_download_link(scores, improvement_areas, percentile):
    """
    Create a PDF report and return a download link.
    
    Args:
        scores (dict): Dictionary of ARI scores
        improvement_areas (list): List of improvement areas
        percentile (float): Benchmark percentile
        
    Returns:
        str: HTML link for downloading the PDF
    """
    # Create a PDF buffer
    buf = io.BytesIO()
    
    # Create a PDF with matplotlib
    with PdfPages(buf) as pdf:
        # Create the scores page
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        # Add title
        ax.text(0.5, 0.98, 'Audience Resonance Index™ (ARI) Scorecard', 
                fontsize=16, ha='center', fontweight='bold')
        ax.text(0.5, 0.95, 'Digital Culture Group', fontsize=12, ha='center')
        
        # Add scores
        y_pos = 0.85
        for metric, score in scores.items():
            ax.text(0.1, y_pos, metric, fontsize=10, fontweight='bold')
            ax.text(0.85, y_pos, f'{score}/10', fontsize=10, ha='right')
            
            # Draw score bar
            bar_width = score / 10 * 0.7
            ax.barh(y_pos - 0.02, bar_width, height=0.02, left=0.1, 
                   color=plt.cm.RdYlBu(score/10))
            
            y_pos -= 0.08
        
        # Add benchmark
        ax.text(0.1, 0.1, f'Benchmark Comparison:', fontsize=10, fontweight='bold')
        ax.text(0.1, 0.07, f'This campaign ranks in the top {percentile}% of Gen Z-facing national campaigns', 
                fontsize=9)
        
        # Add improvement areas
        ax.text(0.1, 0.04, f'Top improvement areas: {", ".join(improvement_areas)}', fontsize=9)
        
        # Add footer
        ax.text(0.5, 0.01, 'Powered by Digital Culture Group', fontsize=8, ha='center')
        
        pdf.savefig(fig)
        plt.close()
    
    # Generate download link
    b64 = base64.b64encode(buf.getbuffer()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="ari_scorecard.pdf">⬇ Download Scorecard as PDF</a>'

def display_metric_bar(metric, score):
    """
    Display a metric with a colored progress bar.
    
    Args:
        metric (str): Name of the metric
        score (float): Score value (0-10)
    """
    # Create a container for the metric
    metric_container = st.container()
    
    with metric_container:
        # Display metric label and score
        col1, col2 = st.columns([4, 1])
        col1.markdown(f"**{metric}**")
        col2.markdown(f"**{score}/10**")
        
        # Show the progress bar
        st.progress(score/10)

def get_tone_of_brief(brief_text):
    """
    Analyze the tone of a campaign brief. This is a simulated function that
    would be replaced with actual NLP analysis in a real implementation.
    
    Args:
        brief_text (str): The campaign brief text
        
    Returns:
        str: Tone description
    """
    tones = [
        "professional and strategic",
        "creative and innovative",
        "data-driven and analytical",
        "adventurous and bold",
        "modern and tech-savvy",
        "community-focused and authentic"
    ]
    
    if not brief_text or brief_text.strip() == "":
        return tones[0]
    
    # Choose tone based on text length as a simple heuristic
    # This would be replaced with actual tone analysis in a real implementation
    index = len(brief_text.strip()) % len(tones)
    return tones[index]
