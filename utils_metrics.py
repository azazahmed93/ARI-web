import streamlit as st

def render_metric_card(metric, score, metrics_dict, level_function):
    """
    Render a single metric card with premium styling.
    
    Args:
        metric (str): The name of the metric
        score (float): The score value (0-10)
        metrics_dict (dict): Dictionary of metric descriptions
        level_function (function): Function to determine level from score
    """
    # Define color based on score
    if score >= 7:
        color = "#10b981"  # green
        emoji = "🔥"
        label = "STRONG"
    elif score >= 5:
        color = "#3b82f6"  # blue
        emoji = "✓"
        label = "GOOD"
    else:
        color = "#f43f5e"  # red
        emoji = "⚠️"
        label = "NEEDS IMPROVEMENT"
    
    # Special case for Representation using fixed styling from user request
    if metric == "Representation":
        metric_html = f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); 
                    padding: 15px; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="font-weight: 600; font-size: 1.05rem; color: #333;">{metric}</div>
                <div style="font-size: 0.7rem; background: #3b82f6; color: white; padding: 3px 8px; 
                        border-radius: 4px; font-weight: 500;">{label}</div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="flex-grow: 1; background: #f0f0f0; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="width: 68.0%; background: #3b82f6; height: 100%;"></div>
                </div>
                <div style="margin-left: 10px; font-weight: 600; color: #3b82f6;">6.8/10</div>
            </div>
            
            <div style="font-size: 0.9rem; color: #555; line-height: 1.4;">
                Limited representation of the intended audience or cultural perspective.
            </div>
        </div>
        """
    else:
        # Generate the HTML for all other metric cards
        metric_html = f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); 
                    padding: 15px; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="font-weight: 600; font-size: 1.05rem; color: #333;">{metric}</div>
                <div style="font-size: 0.7rem; background: {color}; color: white; padding: 3px 8px; 
                        border-radius: 4px; font-weight: 500;">{label}</div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="flex-grow: 1; background: #f0f0f0; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="width: {score*10}%; background: {color}; height: 100%;"></div>
                </div>
                <div style="margin-left: 10px; font-weight: 600; color: {color};">{score}/10</div>
            </div>
            
            <div style="font-size: 0.9rem; color: #555; line-height: 1.4;">
                {metrics_dict[metric][level_function(score)]}
            </div>
        </div>
        """
    return st.markdown(metric_html, unsafe_allow_html=True)