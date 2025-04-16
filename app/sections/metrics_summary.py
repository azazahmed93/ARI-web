import streamlit as st
from core.models.metrics import MetricsData
from app.components.metrics import MetricsComponent

def display_metrics_summary(scores, improvement_areas=None, brief_text=""):
    """
    Display a summary of key metrics using a radar chart visualization.
    
    Args:
        scores (dict): Dictionary of metric scores
        improvement_areas (list, optional): List of improvement areas
        brief_text (str, optional): The brief text for audience analysis
    """
    if improvement_areas is None:
        improvement_areas = []
    
    # Create metrics data object
    metrics_data = MetricsData(
        scores=scores,
        brief_text=brief_text,
        improvement_areas=improvement_areas,
        ai_insights=st.session_state.get('ai_insights')
    )
    
    # Create and display metrics component
    component = MetricsComponent()
    component.display(metrics_data)
