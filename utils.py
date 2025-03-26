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
        # First page - Main scorecard with radar chart
        fig = plt.figure(figsize=(8.5, 11), dpi=100)
        fig.patch.set_facecolor('#ffffff')
        
        # Set up grid for layout
        gs = fig.add_gridspec(20, 12)
        
        # Header section
        ax_header = fig.add_subplot(gs[0:2, 0:12])
        ax_header.axis('off')
        ax_header.text(0.5, 0.5, 'Audience Resonance Index (ARI)', 
                fontsize=22, ha='center', fontweight='bold')
        ax_header.text(0.5, 0.0, 'A proprietary framework by Digital Culture Group', 
                fontsize=12, ha='center', color='#555555')
        
        # Description
        ax_desc = fig.add_subplot(gs[2:3, 2:10])
        ax_desc.axis('off')
        ax_desc.text(0.5, 0.5, 
                'ARI measures how effectively a campaign connects with audiences.',
                fontsize=9, ha='center', color='#666666', wrap=True)
        
        # Create radar chart
        ax_radar = fig.add_subplot(gs[3:9, 1:11], polar=True)
        
        # Prepare data for radar chart
        categories = list(scores.keys())
        values = list(scores.values())
        
        # Shorten category names if needed to fit on radar chart
        short_categories = []
        for cat in categories:
            if len(cat) > 15:
                parts = cat.split()
                if len(parts) > 1:
                    short_categories.append(parts[0] + "\n" + " ".join(parts[1:]))
                else:
                    short_categories.append(cat[:12] + "...")
            else:
                short_categories.append(cat)
                
        # Add the first value at the end to close the loop
        short_categories.append(short_categories[0])
        values.append(values[0])
        
        # Number of variables
        N = len(categories)
        
        # What will be the angle of each axis in the plot
        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        angles += [angles[0]]
        
        # Draw one axis per variable + add labels
        plt.xticks(angles[:-1], short_categories[:-1], color='grey', size=7)
        
        # Draw ylabels
        ax_radar.set_rlabel_position(0)
        plt.yticks([2, 4, 6, 8, 10], ["2", "4", "6", "8", "10"], color="grey", size=7)
        plt.ylim(0, 10)
        
        # Plot data
        ax_radar.plot(angles, values, linewidth=1, linestyle='solid', color='#5865f2')
        
        # Fill area
        ax_radar.fill(angles, values, '#5865f2', alpha=0.25)
        
        # Add metrics bars
        ax_metrics = fig.add_subplot(gs[9:14, 1:11])
        ax_metrics.axis('off')
        
        # Display each metric with a colored bar
        y_pos = 1.0
        bar_height = 1.0 / (len(scores) + 1)  # Height for each bar
        padding = bar_height * 0.2  # Padding between bars
        
        for metric, score in scores.items():
            # Truncate long metric names
            display_metric = metric
            if len(metric) > 25:
                display_metric = metric[:22] + "..."
                
            # Draw metric name
            ax_metrics.text(0.01, y_pos - bar_height/2 - 0.01, display_metric, fontsize=8, fontweight='bold')
            ax_metrics.text(0.95, y_pos - bar_height/2 - 0.01, f'{score}/10', fontsize=8, ha='right')
            
            # Draw background bar
            ax_metrics.barh(y_pos - bar_height/2, 0.9, height=bar_height - padding,
                          left=0.05, color='#e3e3e3', zorder=0)
            
            # Draw score bar
            score_width = 0.9 * (score / 10)
            ax_metrics.barh(y_pos - bar_height/2, score_width, height=bar_height - padding,
                         left=0.05, color='#5865f2', alpha=0.7 + 0.3 * (score / 10), zorder=1)
            
            y_pos -= bar_height
        
        # Benchmark section
        ax_benchmark = fig.add_subplot(gs[14:16, 1:11])
        ax_benchmark.axis('off')
        ax_benchmark.text(0.01, 0.8, 'Benchmark Comparison:', fontsize=10, fontweight='bold')
        ax_benchmark.text(0.01, 0.4, 
                    f'This campaign ranks in the top {percentile}% of Gen Z campaigns.',
                    fontsize=9)
        
        # Format improvement areas text to ensure it fits
        improvement_text = ", ".join(improvement_areas)
        if len(improvement_text) > 70:
            improvement_text = improvement_text[:67] + "..."
            
        ax_benchmark.text(0.01, 0.1, 
                    f'Top improvement areas: {improvement_text}', 
                    fontsize=9, wrap=True)
        
        # Add a styled box around benchmark
        benchmark_box = plt.Rectangle((0.005, 0.05), 0.99, 0.85, 
                         fill=True, color='#f5f7fa', 
                         transform=ax_benchmark.transAxes, zorder=-1,
                         linewidth=1, edgecolor='#3b82f6')
        ax_benchmark.add_patch(benchmark_box)
        
        # Psychographic Highlights
        ax_psycho = fig.add_subplot(gs[16:18, 1:11])
        ax_psycho.axis('off')
        ax_psycho.text(0.01, 0.8, 'Psychographic Highlights', fontsize=10, fontweight='bold')
        ax_psycho.text(0.01, 0.4, 
                 'This audience is highly motivated by wealth, admiration, and excitement.',
                 fontsize=9)
        
        # Add a styled box around psychographics
        psycho_box = plt.Rectangle((0.005, 0.05), 0.99, 0.85, 
                       fill=True, color='#fff9f1', 
                       transform=ax_psycho.transAxes, zorder=-1,
                       linewidth=1, edgecolor='#f4b400')
        ax_psycho.add_patch(psycho_box)
        
        # Footer
        ax_footer = fig.add_subplot(gs[18:20, 0:12])
        ax_footer.axis('off')
        ax_footer.text(0.5, 0.5, 'Powered by Digital Culture Group', 
                 fontsize=8, ha='center', color='#555555')
        
        # Adjust layout using tight_layout with custom parameters
        plt.subplots_adjust(left=0.1, right=0.9, top=0.95, bottom=0.05, hspace=0.3)
        
        # Save the page
        pdf.savefig(fig)
        plt.close(fig)
        
        # Second page - Media Affinities and audience insights
        fig = plt.figure(figsize=(8.5, 11), dpi=100)
        fig.patch.set_facecolor('#ffffff')
        
        # Set up grid for layout
        gs = fig.add_gridspec(20, 12)
        
        # Header section
        ax_header = fig.add_subplot(gs[0:2, 0:12])
        ax_header.axis('off')
        ax_header.text(0.5, 0.5, 'ARI - Media Affinities', 
                fontsize=18, ha='center', fontweight='bold')
        
        # Media Affinity title
        ax_media_title = fig.add_subplot(gs[2:3, 1:11])
        ax_media_title.axis('off')
        ax_media_title.text(0.01, 0.5, 'Top Media Affinity Sites', fontsize=12, fontweight='bold')
        ax_media_title.text(0.5, 0.1, 'QVI = Quality Visit Index, a score indicating audience engagement strength', 
                     fontsize=8, color='#666666')
        
        # Media websites - just visual placeholders in the PDF
        media_sites = [
            {"name": "sparknotes.com", "category": "Education", "qvi": 562},
            {"name": "basketball-reference.com", "category": "Sports", "qvi": 558},
            {"name": "coolmathgames.com", "category": "Education", "qvi": 543},
            {"name": "nba.com", "category": "Sports", "qvi": 461},
            {"name": "theverge.com", "category": "Tech", "qvi": 450}
        ]
        
        # Draw media site boxes
        for i, site in enumerate(media_sites):
            col = i % 3
            row = i // 3
            
            # Calculate position
            ax_site = fig.add_subplot(gs[3+row*2:5+row*2, 1+col*4:4+col*4])
            ax_site.axis('off')
            
            # Draw site info - ensure text fits
            site_name = site['name']
            if len(site_name) > 20:
                site_name = site_name[:17] + "..."
                
            ax_site.text(0.5, 0.7, site_name, fontsize=9, fontweight='bold', ha='center')
            ax_site.text(0.5, 0.5, site['category'], fontsize=8, ha='center')
            ax_site.text(0.5, 0.3, f"QVI: {site['qvi']}", fontsize=9, fontweight='bold', ha='center', color='#3b82f6')
            
            # Add a styled box around the site
            site_box = plt.Rectangle((0.05, 0.05), 0.9, 0.9, 
                        fill=True, color='#e0edff', 
                        transform=ax_site.transAxes, zorder=-1,
                        linewidth=1, edgecolor='#3b82f6', alpha=0.7)
            ax_site.add_patch(site_box)
        
        # TV Network title
        ax_tv_title = fig.add_subplot(gs[8:9, 1:11])
        ax_tv_title.axis('off')
        ax_tv_title.text(0.01, 0.5, 'Top TV Network Affinities', fontsize=12, fontweight='bold')
        
        # Placeholder TV networks
        tv_networks = [
            {"name": "NBA TV", "category": "Sports", "qvi": 459},
            {"name": "Adult Swim", "category": "Alt Animation", "qvi": 315},
            {"name": "Cartoon Network", "category": "Youth", "qvi": 292},
            {"name": "MTV", "category": "Music / Culture", "qvi": 288},
            {"name": "Nickelodeon", "category": "Kids / Family", "qvi": 263}
        ]
        
        # Draw network boxes
        for i, network in enumerate(tv_networks):
            col = i % 5
            
            # Calculate position
            ax_network = fig.add_subplot(gs[9:11, 1+col*2:3+col*2])
            ax_network.axis('off')
            
            # Draw network info
            ax_network.text(0.5, 0.7, network['name'], fontsize=8, fontweight='bold', ha='center')
            ax_network.text(0.5, 0.5, network['category'], fontsize=7, ha='center')
            ax_network.text(0.5, 0.3, f"QVI: {network['qvi']}", fontsize=8, fontweight='bold', ha='center', color='#1e88e5')
            
            # Add a styled box around the network
            network_box = plt.Rectangle((0.05, 0.05), 0.9, 0.9, 
                           fill=True, color='#dbeafe', 
                           transform=ax_network.transAxes, zorder=-1,
                           linewidth=1, edgecolor='#1e88e5', alpha=0.7)
            ax_network.add_patch(network_box)
        
        # Audience Summary
        ax_audience = fig.add_subplot(gs[12:14, 1:11])
        ax_audience.axis('off')
        ax_audience.text(0.01, 0.8, 'Audience Summary', fontsize=10, fontweight='bold')
        
        # Break text into multiple lines to ensure it fits
        ax_audience.text(0.01, 0.6, 
                  'This audience skews young, male, and single with a', 
                  fontsize=9)
        ax_audience.text(0.01, 0.4, 
                  'strong affinity for sports, education tools, and', 
                  fontsize=9)
        ax_audience.text(0.01, 0.2, 
                  'social platforms. Motivated by admiration and status.',
                  fontsize=9)
        
        # Add a styled box around audience summary
        audience_box = plt.Rectangle((0.005, 0.05), 0.99, 0.85, 
                        fill=True, color='#e8f0fe', 
                        transform=ax_audience.transAxes, zorder=-1,
                        linewidth=1, edgecolor='#3367d6')
        ax_audience.add_patch(audience_box)
        
        # What's Next
        ax_next = fig.add_subplot(gs[15:17, 1:11])
        ax_next.axis('off')
        ax_next.text(0.01, 0.8, 'What\'s Next?', fontsize=10, fontweight='bold')
        ax_next.text(0.01, 0.5, 
                'Digital Culture Group offers solutions to lift your lowest scoring areas.', 
                fontsize=9)
        ax_next.text(0.01, 0.2, 
                'Let\'s build a breakthrough growth strategy together.', 
                fontsize=9, color='#5865f2')
        
        # Footer
        ax_footer = fig.add_subplot(gs[18:20, 0:12])
        ax_footer.axis('off')
        ax_footer.text(0.5, 0.5, 'Powered by Digital Culture Group', 
                 fontsize=8, ha='center', color='#555555')
        
        # Adjust layout using custom parameters instead of tight_layout
        plt.subplots_adjust(left=0.1, right=0.9, top=0.95, bottom=0.05, hspace=0.3)
        
        # Save the page
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
