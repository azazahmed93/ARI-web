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
        gs = GridSpec(24, 12, figure=fig)
        
        # Header section
        ax_header = fig.add_subplot(gs[0:2, 0:12])
        ax_header.axis('off')
        ax_header.text(0.5, 0.7, 'Audience Resonance Index™ Scorecard', 
                fontsize=22, ha='center', fontweight='bold', color='#111827')
        ax_header.text(0.5, 0.3, 'Digital Culture Group - Proprietary Measurement Framework', 
                fontsize=10, ha='center', color='#4B5563')
        
        # Create radar chart
        ax_radar = fig.add_subplot(gs[2:9, 1:11], polar=True)
        
        # Prepare data for radar chart
        categories = list(scores.keys())
        values = list(scores.values())
        
        # Shorten category names if needed to fit on radar chart
        short_categories = []
        for cat in categories:
            words = cat.split()
            if len(words) > 1:
                short_categories.append(words[0] + "\n" + " ".join(words[1:]))
            else:
                short_categories.append(cat)
                
        # Add the first value at the end to close the loop
        categories.append(categories[0])
        short_categories.append(short_categories[0])
        values.append(values[0])
        
        # Number of variables
        N = len(categories) - 1
        
        # What will be the angle of each axis in the plot
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += [angles[0]]
        
        # Draw one axis per variable + add labels
        plt.xticks(angles[:-1], short_categories[:-1], color='#4B5563', size=8, fontweight='bold')
        
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
        
        # Add metrics bars section title
        ax_metrics_title = fig.add_subplot(gs[9:10, 1:11])
        ax_metrics_title.axis('off')
        ax_metrics_title.text(0.01, 0.5, "Metric Breakdown", fontsize=14, fontweight='bold', color='#111827')
        
        # Metrics layout - 2 columns
        metrics_items = list(scores.items())
        left_metrics = metrics_items[:len(metrics_items)//2 + len(metrics_items)%2]
        right_metrics = metrics_items[len(metrics_items)//2 + len(metrics_items)%2:]
        
        # Left column metrics
        ax_metrics_left = fig.add_subplot(gs[10:15, 1:6])
        ax_metrics_left.axis('off')
        
        # Right column metrics
        ax_metrics_right = fig.add_subplot(gs[10:15, 6:11])
        ax_metrics_right.axis('off')
        
        # Display each metric with a colored bar in left column
        y_pos = 1.0
        bar_height = 1.0 / (len(left_metrics) + 0.5)
        padding = bar_height * 0.15
        
        for i, (metric, score) in enumerate(left_metrics):
            # Get level description
            level = "high" if score >= 7 else "medium" if score >= 4 else "low"
            description = METRICS[metric][level]
            
            # Draw metric name and score
            ax_metrics_left.text(0.01, y_pos - padding/2, f"{metric}: {score}/10", 
                              fontsize=9, fontweight='bold', color='#111827')
            
            # Draw background bar
            ax_metrics_left.barh(y_pos - bar_height/2 - padding, 0.95, height=bar_height/2,
                              left=0.03, color='#E5E7EB', zorder=0)
            
            # Draw score bar
            score_width = 0.95 * (score / 10)
            ax_metrics_left.barh(y_pos - bar_height/2 - padding, score_width, height=bar_height/2,
                             left=0.03, color='#5865f2', alpha=0.7, zorder=1)
            
            # Draw description (wrapped to fit)
            desc_lines = []
            words = description.split()
            current_line = ""
            for word in words:
                if len(current_line + " " + word) <= 40:
                    current_line += " " + word if current_line else word
                else:
                    desc_lines.append(current_line)
                    current_line = word
            if current_line:
                desc_lines.append(current_line)
                
            # Draw description lines
            for j, line in enumerate(desc_lines):
                ax_metrics_left.text(0.03, y_pos - bar_height/2 - padding*2 - j*0.045, line,
                                 fontsize=7, color='#4B5563')
            
            y_pos -= bar_height
        
        # Display each metric with a colored bar in right column
        y_pos = 1.0
        bar_height = 1.0 / (len(right_metrics) + 0.5)
        
        for i, (metric, score) in enumerate(right_metrics):
            # Get level description
            level = "high" if score >= 7 else "medium" if score >= 4 else "low"
            description = METRICS[metric][level]
            
            # Draw metric name and score
            ax_metrics_right.text(0.01, y_pos - padding/2, f"{metric}: {score}/10", 
                               fontsize=9, fontweight='bold', color='#111827')
            
            # Draw background bar
            ax_metrics_right.barh(y_pos - bar_height/2 - padding, 0.95, height=bar_height/2,
                               left=0.03, color='#E5E7EB', zorder=0)
            
            # Draw score bar
            score_width = 0.95 * (score / 10)
            ax_metrics_right.barh(y_pos - bar_height/2 - padding, score_width, height=bar_height/2,
                              left=0.03, color='#5865f2', alpha=0.7, zorder=1)
            
            # Draw description (wrapped to fit)
            desc_lines = []
            words = description.split()
            current_line = ""
            for word in words:
                if len(current_line + " " + word) <= 40:
                    current_line += " " + word if current_line else word
                else:
                    desc_lines.append(current_line)
                    current_line = word
            if current_line:
                desc_lines.append(current_line)
                
            # Draw description lines
            for j, line in enumerate(desc_lines):
                ax_metrics_right.text(0.03, y_pos - bar_height/2 - padding*2 - j*0.045, line,
                                  fontsize=7, color='#4B5563')
            
            y_pos -= bar_height
        
        # Benchmark section
        ax_benchmark = fig.add_subplot(gs[15:17, 1:11])
        ax_benchmark.axis('off')
        
        # Add a styled box around benchmark
        benchmark_box = patches.FancyBboxPatch((0.005, 0.05), 0.99, 0.9, 
                                    boxstyle=patches.BoxStyle("Round", pad=0.02, rounding_size=0.05),
                                    fill=True, color='#f8fafc', 
                                    transform=ax_benchmark.transAxes, zorder=-1,
                                    linewidth=1, edgecolor='#cbd5e1')
        ax_benchmark.add_patch(benchmark_box)
        
        ax_benchmark.text(0.02, 0.8, '📊 Benchmark Comparison', fontsize=12, fontweight='bold', color='#111827')
        
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
            ax_benchmark.text(0.02, 0.65 - i*0.12, line, fontsize=8, color='#4B5563')
            
        # Add improvement areas
        improvement_text = f"Biggest opportunity areas: {', '.join(improvement_areas)}"
        ax_benchmark.text(0.02, 0.2, improvement_text, fontsize=8, color='#4B5563', fontweight='bold')
        
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
        ax_sites_title = fig.add_subplot(gs[2:3, 1:11])
        ax_sites_title.axis('off')
        ax_sites_title.text(0.01, 0.6, '🔥 Top Media Affinity Sites', 
                     fontsize=14, fontweight='bold', color='#111827')
        ax_sites_title.text(0.01, 0.2, 'QVI = Quality Visit Index, a score indicating audience engagement strength', 
                     fontsize=8, color='#4B5563')
        
        # Draw media site boxes - 5 sites in a row
        for i, site in enumerate(MEDIA_AFFINITY_SITES):
            col = i % 5
            
            # Calculate position
            ax_site = fig.add_subplot(gs[3:6, 1+col*2:3+col*2])
            ax_site.axis('off')
            
            # Draw box
            site_box = patches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9, 
                                   boxstyle=patches.BoxStyle("Round", pad=0.02, rounding_size=0.05),
                                   fill=True, color='#e0edff', 
                                   transform=ax_site.transAxes, zorder=-1,
                                   linewidth=1, edgecolor='#bfdbfe')
            ax_site.add_patch(site_box)
            
            # Draw site info
            site_name = site['name']
            if len(site_name) > 20:
                site_name = site_name[:17] + "..."
                
            ax_site.text(0.5, 0.8, site_name, fontsize=9, fontweight='bold', ha='center', color='#111827')
            ax_site.text(0.5, 0.6, site['category'], fontsize=8, ha='center', color='#4B5563')
            ax_site.text(0.5, 0.4, f"QVI: {site['qvi']}", fontsize=9, fontweight='bold', ha='center', color='#3b82f6')
            ax_site.text(0.5, 0.2, "Visit Site", fontsize=8, ha='center', color='#3b82f6')
        
        # TV Network Affinities
        ax_tv_title = fig.add_subplot(gs[7:8, 1:11])
        ax_tv_title.axis('off')
        ax_tv_title.text(0.01, 0.5, '📺 Top TV Network Affinities', 
                  fontsize=14, fontweight='bold', color='#111827')
        
        # Draw TV network boxes - 5 networks in a row
        for i, network in enumerate(TV_NETWORKS):
            col = i % 5
            
            # Calculate position
            ax_network = fig.add_subplot(gs[8:11, 1+col*2:3+col*2])
            ax_network.axis('off')
            
            # Draw box
            network_box = patches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9, 
                                      boxstyle=patches.BoxStyle("Round", pad=0.02, rounding_size=0.05),
                                      fill=True, color='#dbeafe', 
                                      transform=ax_network.transAxes, zorder=-1,
                                      linewidth=1, edgecolor='#bfdbfe')
            ax_network.add_patch(network_box)
            
            # Draw network info
            network_name = network['name']
            if len(network_name) > 15:
                network_name = network_name[:12] + "..."
                
            ax_network.text(0.5, 0.7, network_name, fontsize=9, fontweight='bold', ha='center', color='#111827')
            ax_network.text(0.5, 0.5, network['category'], fontsize=8, ha='center', color='#4B5563')
            ax_network.text(0.5, 0.3, f"QVI: {network['qvi']}", fontsize=9, fontweight='bold', ha='center', color='#1e88e5')
        
        # Streaming Platforms
        ax_stream_title = fig.add_subplot(gs[12:13, 1:11])
        ax_stream_title.axis('off')
        ax_stream_title.text(0.01, 0.5, '📶 Top Streaming Platforms', 
                      fontsize=14, fontweight='bold', color='#111827')
        
        # Draw streaming platform boxes - 3 platforms in a row, potentially 2 rows
        for i, platform in enumerate(STREAMING_PLATFORMS):
            col = i % 3
            row = i // 3
            
            # Calculate position
            ax_platform = fig.add_subplot(gs[13+row*3:16+row*3, 1+col*4:4+col*4])
            ax_platform.axis('off')
            
            # Draw box
            platform_box = patches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9, 
                                       boxstyle=patches.BoxStyle("Round", pad=0.02, rounding_size=0.05),
                                       fill=True, color='#d1fae5', 
                                       transform=ax_platform.transAxes, zorder=-1,
                                       linewidth=1, edgecolor='#a7f3d0')
            ax_platform.add_patch(platform_box)
            
            # Draw platform info
            platform_name = platform['name']
            if len(platform_name) > 18:
                platform_name = platform_name[:15] + "..."
                
            ax_platform.text(0.5, 0.7, platform_name, fontsize=9, fontweight='bold', ha='center', color='#111827')
            ax_platform.text(0.5, 0.5, platform['category'], fontsize=8, ha='center', color='#4B5563')
            ax_platform.text(0.5, 0.3, f"QVI: {platform['qvi']}", fontsize=9, fontweight='bold', ha='center', color='#059669')
        
        # Psychographic Highlights
        y_position = 19
        if len(STREAMING_PLATFORMS) > 3:
            y_position = 22
            
        ax_psycho = fig.add_subplot(gs[y_position:y_position+3, 1:11])
        ax_psycho.axis('off')
        
        # Draw box
        psycho_box = patches.FancyBboxPatch((0.005, 0.05), 0.99, 0.9, 
                                  boxstyle=patches.BoxStyle("Round", pad=0.02, rounding_size=0.05),
                                  fill=True, color='#fff7ed', 
                                  transform=ax_psycho.transAxes, zorder=-1,
                                  linewidth=1, edgecolor='#fed7aa')
        ax_psycho.add_patch(psycho_box)
        
        ax_psycho.text(0.02, 0.8, '🧠 Psychographic Highlights', fontsize=12, fontweight='bold', color='#111827')
        
        # Clean HTML tags from text
        psycho_text = PSYCHOGRAPHIC_HIGHLIGHTS.replace('<strong>', '').replace('</strong>', '').strip()
        
        # Format the text to wrap at appropriate points
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
            
        # Draw each line
        for i, line in enumerate(psycho_lines):
            ax_psycho.text(0.02, 0.6 - i*0.15, line, fontsize=8, color='#4B5563')
        
        # Audience Summary
        y_position += 4
        ax_audience = fig.add_subplot(gs[y_position:y_position+4, 1:11])
        ax_audience.axis('off')
        
        # Draw box
        audience_box = patches.FancyBboxPatch((0.005, 0.05), 0.99, 0.9, 
                                   boxstyle=patches.BoxStyle("Round", pad=0.02, rounding_size=0.05),
                                   fill=True, color='#f0f9ff', 
                                   transform=ax_audience.transAxes, zorder=-1,
                                   linewidth=1, edgecolor='#bae6fd')
        ax_audience.add_patch(audience_box)
        
        ax_audience.text(0.02, 0.85, '👥 Audience Summary', fontsize=12, fontweight='bold', color='#111827')
        
        # Clean HTML tags from text
        audience_text = AUDIENCE_SUMMARY.replace('<strong>', '').replace('</strong>', '').strip()
        
        # Format the text to wrap at appropriate points
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
            
        # Draw each line
        for i, line in enumerate(audience_lines):
            ax_audience.text(0.02, 0.7 - i*0.12, line, fontsize=8, color='#4B5563')
        
        # What's Next section
        y_position += 5
        ax_next = fig.add_subplot(gs[y_position:y_position+3, 1:11])
        ax_next.axis('off')
        
        # Draw box with light blue background
        next_box = patches.FancyBboxPatch((0.005, 0.05), 0.99, 0.9, 
                                boxstyle=patches.BoxStyle("Round", pad=0.02, rounding_size=0.05),
                                fill=True, color='#eff6ff', 
                                transform=ax_next.transAxes, zorder=-1,
                                linewidth=1, edgecolor='#bfdbfe')
        ax_next.add_patch(next_box)
        
        ax_next.text(0.02, 0.8, '🔧 What\'s Next?', fontsize=12, fontweight='bold', color='#111827')
        
        # Clean HTML tags from text
        next_text = NEXT_STEPS.replace('<strong>', '').replace('</strong>', '').strip()
        
        # Format the text to wrap at appropriate points
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
            
        # Draw each line
        for i, line in enumerate(next_lines):
            ax_next.text(0.02, 0.6 - i*0.15, line, fontsize=8, color='#4B5563')
            
        # Add additional text
        ax_next.text(0.02, 0.3, "Let's build a breakthrough growth strategy — Digital Culture Group has proven tactics", 
                 fontsize=8, color='#5865f2')
        ax_next.text(0.02, 0.2, "that boost underperforming areas.", 
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
