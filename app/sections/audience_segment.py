from components.audience_segments import AudienceSegmentComponent

import streamlit as st

def display_audience_segment(segment, segment_type='Primary', color='#10b981', bg_color='#f0fdf4'):
    """
    Display an audience segment in a styled card format.
    
    Args:
        segment (dict): The segment data dictionary
        segment_type (str): The type of segment (Primary, Secondary, etc.)
        color (str): The accent color for the card
        bg_color (str): The background color for the card
    """
    # Import the learning tips module
    from app.components.learning_tips import display_tip_bubble
    if not segment:
        return
    
    # CODE SEGMENTATION TRY
    component = AudienceSegmentComponent()
    component.display(segment, segment_type, color, bg_color)
