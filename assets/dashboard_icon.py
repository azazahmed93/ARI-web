import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np

def create_dashboard_icon():
    """Generate a dashboard-like visualization and return it as a base64 image."""
    
    # Create a figure with a professional-looking background
    fig, ax = plt.subplots(figsize=(6, 3), facecolor='#f8f9fa')
    
    # Set the background color
    ax.set_facecolor('#f8f9fa')
    
    # Sample data for a bar chart
    categories = ['Cat 1', 'Cat 2', 'Cat 3', 'Cat 4', 'Cat 5']
    values = [85, 67, 92, 76, 88]
    colors = ['#4361EE', '#3A0CA3', '#7209B7', '#F72585', '#4CC9F0']
    
    # Create a bar chart
    bars = ax.bar(categories, values, color=colors, alpha=0.7)
    
    # Add a line chart on top
    x = np.arange(len(categories))
    line_values = [80, 72, 88, 82, 90]
    ax.plot(x, line_values, marker='o', color='#4CC9F0', linewidth=2)
    
    # Add some random scatter points for decoration
    scatter_x = np.random.uniform(0, 4, 10)
    scatter_y = np.random.uniform(60, 95, 10)
    ax.scatter(scatter_x, scatter_y, color='#F72585', alpha=0.5, s=30)
    
    # Customize the chart
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#dddddd')
    ax.spines['bottom'].set_color('#dddddd')
    ax.tick_params(axis='x', colors='#888888')
    ax.tick_params(axis='y', colors='#888888')
    
    # Set title
    ax.set_title('Enterprise Analytics', fontsize=14, color='#333333', pad=15)
    
    # Show grid lines
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    plt.close()
    
    # Convert to base64
    buffer.seek(0)
    image_png = buffer.getvalue()
    image_base64 = base64.b64encode(image_png).decode('utf-8')
    
    return f"data:image/png;base64,{image_base64}"