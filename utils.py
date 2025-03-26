import base64
import io
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import numpy as np
from PIL import Image
import requests
from assets.content import (
    MEDIA_AFFINITY_SITES, 
    TV_NETWORKS, 
    STREAMING_PLATFORMS, 
    PSYCHOGRAPHIC_HIGHLIGHTS,
    AUDIENCE_SUMMARY,
    NEXT_STEPS,
    METRICS
)

# Remove HTML tags from a string
def strip_html(text):
    """Remove HTML tags from a string."""
    import re
    return re.sub('<[^<]+?>', '', text).strip()

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
    
    # Setup matplotlib to use a specific font that looks modern
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # Create a PDF with matplotlib
    with PdfPages(buf) as pdf:
        # First page - Main scorecard with radar chart
        fig = plt.figure(figsize=(8.5, 11), dpi=150)
        fig.patch.set_facecolor('#ffffff')
        
        # Set up grid for layout
        gs = GridSpec(30, 12, figure=fig)
        
        # Header section
        ax_header = fig.add_subplot(gs[0:2, 0:12])
        ax_header.axis('off')
        ax_header.text(0.5, 0.5, 'Audience Resonance Index™ Scorecard', 
                fontsize=22, ha='center', fontweight='bold', color='#111827')
        
        # Create radar chart
        ax_radar = fig.add_subplot(gs[2:8, 1:11], polar=True)
        
        # Prepare data for radar chart
        categories = list(scores.keys())
        values = list(scores.values())
        
        # Add the first value at the end to close the loop
        categories.append(categories[0])
        values.append(values[0])
        
        # Number of variables
        N = len(categories) - 1
        
        # What will be the angle of each axis in the plot
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += [angles[0]]
        
        # Draw one axis per variable + add labels
        plt.xticks(angles[:-1], categories[:-1], color='#4B5563', size=8)
        
        # Draw ylabels
        ax_radar.set_rlabel_position(0)
        plt.yticks([2, 4, 6, 8, 10], ["2", "4", "6", "8", "10"], color="#4B5563", size=7)
        plt.ylim(0, 10)
        
        # Plot data
        ax_radar.plot(angles, values, linewidth=2, linestyle='solid', color='#5865f2')
        
        # Fill area
        ax_radar.fill(angles, values, '#5865f2', alpha=0.3)
        
        # Style the chart further
        ax_radar.spines['polar'].set_visible(False)
        ax_radar.grid(color='#E5E7EB', linestyle='-', linewidth=0.5, alpha=0.7)
        
        # Add metrics breakdown section title
        ax_metrics_title = fig.add_subplot(gs[8:9, 1:11])
        ax_metrics_title.axis('off')
        ax_metrics_title.text(0.5, 0.5, "Metric Breakdown", fontsize=16, fontweight='bold', color='#111827', ha='center')
        
        # Metrics layout - 2 columns
        metrics_items = list(scores.items())
        left_metrics = metrics_items[:len(metrics_items)//2 + len(metrics_items)%2]
        right_metrics = metrics_items[len(metrics_items)//2 + len(metrics_items)%2:]
        
        # Left column metrics
        ax_metrics_left = fig.add_subplot(gs[9:18, 1:6])
        ax_metrics_left.axis('off')
        
        # Right column metrics
        ax_metrics_right = fig.add_subplot(gs[9:18, 6:11])
        ax_metrics_right.axis('off')
        
        # Display each metric with a colored background in left column
        y_pos = 1.0
        metric_height = 1.0 / (len(left_metrics))
        padding = 0.05
        
        for i, (metric, score) in enumerate(left_metrics):
            # Get level description
            level = "high" if score >= 7 else "medium" if score >= 4 else "low"
            description = METRICS[metric][level]
            
            # Background color based on metric level
            bg_color = '#e0edff' if i % 2 == 0 else '#f0f9ff'
            
            # Draw background
            rect = patches.Rectangle((0, y_pos - metric_height + padding), 
                                    1, metric_height - padding, 
                                    facecolor=bg_color, edgecolor='none', alpha=0.7)
            ax_metrics_left.add_patch(rect)
            
            # Draw metric name and score
            ax_metrics_left.text(0.02, y_pos - metric_height/5, f"{metric}: {score}/10", 
                              fontsize=9, fontweight='bold', color='#111827')
            
            # Draw description
            ax_metrics_left.text(0.02, y_pos - metric_height/2, description, 
                              fontsize=7, color='#4B5563')
            
            y_pos -= metric_height
        
        # Display each metric with a colored background in right column
        y_pos = 1.0
        metric_height = 1.0 / (len(right_metrics))
        
        for i, (metric, score) in enumerate(right_metrics):
            # Get level description
            level = "high" if score >= 7 else "medium" if score >= 4 else "low"
            description = METRICS[metric][level]
            
            # Background color based on metric level
            bg_color = '#e0edff' if i % 2 == 0 else '#f0f9ff'
            
            # Draw background
            rect = patches.Rectangle((0, y_pos - metric_height + padding), 
                                    1, metric_height - padding, 
                                    facecolor=bg_color, edgecolor='none', alpha=0.7)
            ax_metrics_right.add_patch(rect)
            
            # Draw metric name and score
            ax_metrics_right.text(0.02, y_pos - metric_height/5, f"{metric}: {score}/10", 
                               fontsize=9, fontweight='bold', color='#111827')
            
            # Draw description
            ax_metrics_right.text(0.02, y_pos - metric_height/2, description, 
                               fontsize=7, color='#4B5563')
            
            y_pos -= metric_height
        
        # Benchmark section
        ax_benchmark = fig.add_subplot(gs[18:21, 1:11])
        ax_benchmark.axis('off')
        
        # Draw section title
        ax_benchmark.text(0.01, 0.9, 'Benchmark Comparison', fontsize=12, fontweight='bold', color='#111827')
        
        # Formatted benchmark text
        benchmark_text = (f"This campaign ranks in the top {percentile}% of Gen Z-facing national campaigns "
                        f"for Audience Resonance Index™ (ARI). That means it outperforms the majority of "
                        f"peer campaigns in relevance, authenticity, and emotional connection — based on "
                        f"Digital Culture Group's analysis of 300+ national efforts.")
        
        # Format the text to wrap at appropriate points
        benchmark_lines = []
        words = benchmark_text.split()
        line = ""
        for word in words:
            if len(line + " " + word) <= 95:
                line += " " + word if line else word
            else:
                benchmark_lines.append(line)
                line = word
        if line:
            benchmark_lines.append(line)
            
        # Draw each line
        for i, line in enumerate(benchmark_lines):
            ax_benchmark.text(0.01, 0.75 - i*0.12, line, fontsize=8, color='#4B5563')
            
        # Add improvement areas
        improvement_text = f"Biggest opportunity areas: {', '.join(improvement_areas)}"
        ax_benchmark.text(0.01, 0.3, improvement_text, fontsize=8, color='#4B5563', fontweight='bold')
        
        # Save the first page
        pdf.savefig(fig)
        plt.close(fig)
        
        # Second page - Media Affinities
        fig = plt.figure(figsize=(8.5, 11), dpi=150)
        fig.patch.set_facecolor('#ffffff')
        
        # Set up grid for layout
        gs = GridSpec(36, 12, figure=fig)
        
        # Header
        ax_header = fig.add_subplot(gs[0:2, 0:12])
        ax_header.axis('off')
        ax_header.text(0.5, 0.5, 'Media Affinities & Audience Insights', 
                fontsize=18, ha='center', fontweight='bold', color='#111827')
        
        # Top Media Affinity Sites
        ax_sites_title = fig.add_subplot(gs[2:3, 0:12])
        ax_sites_title.axis('off')
        ax_sites_title.text(0.1, 0.6, 'Top Media Affinity Sites', 
                     fontsize=14, fontweight='bold', color='#111827')
        ax_sites_title.text(0.1, 0.2, 'QVI = Quality Visit Index, a score indicating audience engagement strength', 
                     fontsize=8, color='#4B5563')
        
        # Draw media site boxes - 5 sites in a row
        site_width = 0.17
        site_margin = 0.01
        
        for i, site in enumerate(MEDIA_AFFINITY_SITES):
            # Calculate position
            left = 0.1 + i * (site_width + site_margin)
            
            # Site box in light blue
            rect = patches.Rectangle((left, 0.75), site_width, 0.15, 
                                   facecolor='#e0edff', edgecolor='none',
                                   transform=ax_sites_title.transAxes)
            ax_sites_title.add_patch(rect)
            
            # Site info
            site_name = site['name']
            if len(site_name) > 20:
                site_name = site_name[:17] + "..."
                
            # Center of the box
            center_x = left + site_width/2
            
            ax_sites_title.text(center_x, 0.85, site_name, 
                             fontsize=8, ha='center', va='center', 
                             fontweight='bold', color='#111827', 
                             transform=ax_sites_title.transAxes)
            
            ax_sites_title.text(center_x, 0.81, site['category'], 
                             fontsize=7, ha='center', va='center', 
                             color='#4B5563', transform=ax_sites_title.transAxes)
            
            ax_sites_title.text(center_x, 0.77, f"QVI: {site['qvi']}", 
                             fontsize=7, ha='center', va='center', 
                             fontweight='bold', color='#3b82f6', 
                             transform=ax_sites_title.transAxes)
            
            ax_sites_title.text(center_x, 0.73, "Visit Site", 
                             fontsize=7, ha='center', va='center', 
                             color='#3b82f6', transform=ax_sites_title.transAxes)
        
        # TV Network Affinities
        ax_tv_title = fig.add_subplot(gs[5:6, 0:12])
        ax_tv_title.axis('off')
        ax_tv_title.text(0.1, 0.6, 'Top TV Network Affinities', 
                  fontsize=14, fontweight='bold', color='#111827')
        
        # Draw network boxes
        for i, network in enumerate(TV_NETWORKS):
            # Calculate position
            left = 0.1 + i * (site_width + site_margin)
            
            # Network box in light blue
            rect = patches.Rectangle((left, 0.25), site_width, 0.15, 
                                   facecolor='#dbeafe', edgecolor='none',
                                   transform=ax_tv_title.transAxes)
            ax_tv_title.add_patch(rect)
            
            # Network info
            network_name = network['name']
            if len(network_name) > 15:
                network_name = network_name[:12] + "..."
            
            # Center of the box
            center_x = left + site_width/2
            
            ax_tv_title.text(center_x, 0.35, network_name, 
                          fontsize=8, ha='center', va='center', 
                          fontweight='bold', color='#111827', 
                          transform=ax_tv_title.transAxes)
            
            ax_tv_title.text(center_x, 0.3, network['category'], 
                          fontsize=7, ha='center', va='center', 
                          color='#4B5563', transform=ax_tv_title.transAxes)
            
            ax_tv_title.text(center_x, 0.25, f"QVI: {network['qvi']}", 
                          fontsize=7, ha='center', va='center', 
                          fontweight='bold', color='#1e88e5', 
                          transform=ax_tv_title.transAxes)
        
        # Streaming Platforms
        ax_stream_title = fig.add_subplot(gs[9:10, 0:12])
        ax_stream_title.axis('off')
        ax_stream_title.text(0.1, 0.6, 'Top Streaming Platforms', 
                      fontsize=14, fontweight='bold', color='#111827')
        
        # Draw streaming platform boxes - 3 in a row, bigger boxes
        platform_width = 0.26
        platform_margin = 0.02
        
        # First row
        platforms_first_row = STREAMING_PLATFORMS[:3]
        
        for i, platform in enumerate(platforms_first_row):
            # Calculate position
            left = 0.1 + i * (platform_width + platform_margin)
            
            # Platform box in light green
            rect = patches.Rectangle((left, 0.2), platform_width, 0.2, 
                                   facecolor='#d1fae5', edgecolor='none',
                                   transform=ax_stream_title.transAxes)
            ax_stream_title.add_patch(rect)
            
            # Platform info
            platform_name = platform['name']
            if len(platform_name) > 18:
                platform_name = platform_name[:15] + "..."
            
            # Center of the box
            center_x = left + platform_width/2
            
            ax_stream_title.text(center_x, 0.35, platform_name, 
                              fontsize=8, ha='center', va='center', 
                              fontweight='bold', color='#111827', 
                              transform=ax_stream_title.transAxes)
            
            ax_stream_title.text(center_x, 0.3, platform['category'], 
                              fontsize=7, ha='center', va='center', 
                              color='#4B5563', transform=ax_stream_title.transAxes)
            
            ax_stream_title.text(center_x, 0.25, f"QVI: {platform['qvi']}", 
                              fontsize=7, ha='center', va='center', 
                              fontweight='bold', color='#059669', 
                              transform=ax_stream_title.transAxes)
        
        # Second row if needed
        if len(STREAMING_PLATFORMS) > 3:
            ax_stream_row2 = fig.add_subplot(gs[12:13, 0:12])
            ax_stream_row2.axis('off')
            
            platforms_second_row = STREAMING_PLATFORMS[3:6]
            
            for i, platform in enumerate(platforms_second_row):
                # Calculate position
                left = 0.1 + i * (platform_width + platform_margin)
                
                # Platform box in light green
                rect = patches.Rectangle((left, 0.2), platform_width, 0.2, 
                                       facecolor='#d1fae5', edgecolor='none',
                                       transform=ax_stream_row2.transAxes)
                ax_stream_row2.add_patch(rect)
                
                # Platform info
                platform_name = platform['name']
                if len(platform_name) > 18:
                    platform_name = platform_name[:15] + "..."
                
                # Center of the box
                center_x = left + platform_width/2
                
                ax_stream_row2.text(center_x, 0.35, platform_name, 
                                  fontsize=8, ha='center', va='center', 
                                  fontweight='bold', color='#111827', 
                                  transform=ax_stream_row2.transAxes)
                
                ax_stream_row2.text(center_x, 0.3, platform['category'], 
                                  fontsize=7, ha='center', va='center', 
                                  color='#4B5563', transform=ax_stream_row2.transAxes)
                
                ax_stream_row2.text(center_x, 0.25, f"QVI: {platform['qvi']}", 
                                  fontsize=7, ha='center', va='center', 
                                  fontweight='bold', color='#059669', 
                                  transform=ax_stream_row2.transAxes)
            
            # Adjust y-position for next sections
            y_position = 16
        else:
            y_position = 13
        
        # Psychographic Highlights
        ax_psycho = fig.add_subplot(gs[y_position:y_position+4, 1:11])
        ax_psycho.axis('off')
        
        # Draw background
        psycho_rect = patches.Rectangle((0, 0), 1, 1, 
                                       facecolor='#fff7ed', edgecolor='none',
                                       transform=ax_psycho.transAxes)
        ax_psycho.add_patch(psycho_rect)
        
        # Title and content
        ax_psycho.text(0.02, 0.9, 'Psychographic Highlights', 
                     fontsize=12, fontweight='bold', color='#111827')
        
        # Clean HTML tags from content and format text
        psycho_text = strip_html(PSYCHOGRAPHIC_HIGHLIGHTS)
        psycho_lines = []
        words = psycho_text.split()
        line = ""
        
        for word in words:
            if len(line + " " + word) <= 95:
                line += " " + word if line else word
            else:
                psycho_lines.append(line)
                line = word
        if line:
            psycho_lines.append(line)
            
        # Draw text
        for i, line in enumerate(psycho_lines):
            ax_psycho.text(0.02, 0.8 - i*0.1, line, fontsize=8, color='#4B5563')
        
        # Audience Summary
        ax_audience = fig.add_subplot(gs[y_position+5:y_position+9, 1:11])
        ax_audience.axis('off')
        
        # Draw background
        audience_rect = patches.Rectangle((0, 0), 1, 1, 
                                        facecolor='#f0f9ff', edgecolor='none',
                                        transform=ax_audience.transAxes)
        ax_audience.add_patch(audience_rect)
        
        # Title and content
        ax_audience.text(0.02, 0.9, 'Audience Summary', 
                       fontsize=12, fontweight='bold', color='#111827')
        
        # Clean HTML tags from content and format text
        audience_text = strip_html(AUDIENCE_SUMMARY)
        audience_lines = []
        words = audience_text.split()
        line = ""
        
        for word in words:
            if len(line + " " + word) <= 95:
                line += " " + word if line else word
            else:
                audience_lines.append(line)
                line = word
        if line:
            audience_lines.append(line)
            
        # Draw text
        for i, line in enumerate(audience_lines):
            ax_audience.text(0.02, 0.8 - i*0.1, line, fontsize=8, color='#4B5563')
        
        # What's Next section
        ax_next = fig.add_subplot(gs[y_position+10:y_position+14, 1:11])
        ax_next.axis('off')
        
        # Draw background
        next_rect = patches.Rectangle((0, 0), 1, 1, 
                                     facecolor='#eff6ff', edgecolor='none',
                                     transform=ax_next.transAxes)
        ax_next.add_patch(next_rect)
        
        # Title and content
        ax_next.text(0.02, 0.9, 'What\'s Next?', 
                   fontsize=12, fontweight='bold', color='#111827')
        
        # Clean HTML tags from content and format text
        next_text = strip_html(NEXT_STEPS)
        next_lines = []
        words = next_text.split()
        line = ""
        
        for word in words:
            if len(line + " " + word) <= 95:
                line += " " + word if line else word
            else:
                next_lines.append(line)
                line = word
        if line:
            next_lines.append(line)
            
        # Draw text
        for i, line in enumerate(next_lines):
            ax_next.text(0.02, 0.8 - i*0.1, line, fontsize=8, color='#4B5563')
            
        # Additional text
        ax_next.text(0.02, 0.5, "Let's build a breakthrough growth strategy — Digital Culture Group has proven tactics", 
                   fontsize=8, color='#5865f2')
        ax_next.text(0.02, 0.4, "that boost underperforming areas.", 
                   fontsize=8, color='#5865f2')
        
        # Footer
        ax_footer = fig.add_subplot(gs[33:35, 0:12])
        ax_footer.axis('off')
        ax_footer.text(0.5, 0.5, 'Powered by Digital Culture Group © 2023', 
                     fontsize=8, ha='center', color='#6B7280')
        
        # Save the second page
        pdf.savefig(fig)
        plt.close(fig)
    
    # Generate download link
    b64 = base64.b64encode(buf.getbuffer()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="ari_scorecard.pdf" style="display: inline-block; padding: 10px 15px; background-color: #5865f2; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">⬇ Download Scorecard as PDF</a>'

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
        st.progress(score/10, "rgb(88, 101, 242)")

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
