# app/components/metrics_component.py
import streamlit as st
import plotly.graph_objects as go
from core.models.metrics import RadarChartData
from core.services.metrics import MetricsService
from components.learning_tips import display_tip_bubble
from typing import List
import textwrap

class MetricsComponent:
    def __init__(self):
        self.metrics_service = MetricsService()
    
    def display(self, metrics_data):
        """Display metrics summary."""
        # Process metrics data
        chart_data = self.metrics_service.process_metrics(metrics_data)
        
        # Create columns for layout
        col1, col2 = st.columns([3, 2])
        
        with col1:
            self._display_radar_chart(chart_data)
        
        with col2:
            self._display_metrics_summary(chart_data)
    
    def _display_radar_chart(self, data: RadarChartData):
        """Display radar chart."""
        fig = go.Figure()
        
        # Add current measurement trace
        fig.add_trace(go.Scatterpolar(
            r=data.values,
            theta=data.categories,
            fill='toself',
            fillcolor='rgba(88, 101, 242, 0.3)',
            line=dict(color='#5865f2', width=2),
            name='Current Measurement'
        ))
        
        # Add benchmark trace
        fig.add_trace(go.Scatterpolar(
            r=data.benchmark_values,
            theta=data.categories,
            fill='toself',
            fillcolor='rgba(16, 185, 129, 0.1)',
            line=dict(color='#10b981', width=1.5, dash='dot'),
            name='Hyperdimensional Potential'
        ))
        
        # Update layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    tickfont=dict(size=9),
                    tickvals=[2, 4, 6, 8, 10],
                    gridcolor="rgba(0,0,0,0.1)",
                ),
                angularaxis=dict(
                    tickfont=dict(size=10, color="#444"),
                    gridcolor="rgba(0,0,0,0.1)",
                )
            ),
            showlegend=True,
            legend=dict(
                x=0.85,
                y=1.2,
                orientation='h',
                font=dict(size=10)
            ),
            margin=dict(l=80, r=80, t=20, b=80),
            height=450,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_metrics_summary(self, data: RadarChartData):
        """Display metrics summary."""
        # Display RCC score
        rcc_tip = display_tip_bubble("advanced", "Resonance Convergence Coefficient", inline=True)
        st.markdown(self._generate_rcc_html(data.rcc_score, rcc_tip), unsafe_allow_html=True)
        
        # Display campaign strengths
        st.markdown(self._generate_strengths_html(data.top_strengths), unsafe_allow_html=True)
        
        # Display ROI potential
        st.markdown(self._generate_roi_html(data.roi_potential), unsafe_allow_html=True)
    
    def _generate_rcc_html(self, score: float, tip: str) -> str:
        """Generate HTML for RCC score display."""
        return f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 20px; margin: 20px 0; text-align: center;">
            <div style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2;">
                Resonance Convergence Coefficient {tip}
            </div>
            <div style="font-size: 3rem; font-weight: 700; color: #5865f2; margin: 10px 0;">{score:.1f}<span style="font-size: 1.5rem; color: #777;">/10</span></div>
        </div>
        """
    
    def _generate_strengths_html(self, strengths: List[str]) -> str:
        """Generate HTML for strengths display."""
        strengths_html = '<div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #777; margin: 15px 0 10px 0;">Campaign Strengths</div>'
        
        for strength in strengths:
            strengths_html += textwrap.dedent(f"""
            <div style="background: #f0f2ff; border-radius: 6px; padding: 10px 15px; margin-bottom: 10px;">
                <div style="font-weight: 600; color: #333; font-size: 0.9rem;">{strength}</div>
            </div>
            """).strip()
        return strengths_html
    
    def _generate_roi_html(self, roi_potential: str) -> str:
        """Generate HTML for ROI potential display."""
        return f"""
        <div style="background: #fff8f0; border-radius: 6px; padding: 10px 15px; margin: 15px 0;">
            <div style="font-weight: 600; color: #f43f5e; font-size: 0.9rem;">ROI Potential: {roi_potential}</div>
        </div>
        """

