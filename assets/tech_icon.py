import base64
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

def create_tech_icon():
    """Generate a tech-looking icon and return as base64 image"""
    # Create figure with transparent background
    fig, ax = plt.subplots(figsize=(4, 4), facecolor='none')
    
    # Create a hexagon shape
    n_points = 6
    angles = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
    outer_radius = 0.8
    xs = outer_radius * np.cos(angles)
    ys = outer_radius * np.sin(angles)
    
    # Plot outer hexagon
    ax.plot(np.append(xs, xs[0]), np.append(ys, ys[0]), color='#5865f2', linewidth=2, alpha=0.7)
    
    # Plot inner hexagon
    inner_radius = 0.5
    xs_inner = inner_radius * np.cos(angles)
    ys_inner = inner_radius * np.sin(angles)
    ax.plot(np.append(xs_inner, xs_inner[0]), np.append(ys_inner, ys_inner[0]), 
            color='#5865f2', linewidth=2, alpha=0.9)
    
    # Plot connecting lines
    for i in range(n_points):
        ax.plot([xs[i], xs_inner[i]], [ys[i], ys_inner[i]], color='#5865f2', linewidth=1, alpha=0.5)
    
    # Add circular nodes
    ax.scatter(xs, ys, color='#5865f2', s=80, alpha=0.8)
    
    # Add decorative elements
    ax.scatter([0.4, -0.4, 0.2, -0.2], [0.4, -0.4, -0.3, 0.3], 
               color=['#10b981', '#3b82f6', '#f59e0b', '#f59e0b'], s=[120, 80, 100, 90], alpha=0.7)
    
    # Add a central dot
    ax.scatter([0], [0], color='#ff4d8f', s=150, alpha=0.9)
    
    # Remove axes
    ax.axis('off')
    plt.tight_layout()
    
    # Save to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True, dpi=120)
    plt.close()
    
    # Convert to base64
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"