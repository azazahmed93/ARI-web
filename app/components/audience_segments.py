# app/components/audience_segment_component.py
import streamlit as st
from core.models.audience import AudienceSegment
from core.services.audience import AudienceService
from app.components.learning_tips import display_tip_bubble
from typing import Dict, Optional

import streamlit.components.v1 as components
import os
import json

class AudienceSegmentComponent:
    def __init__(self):
        self.audience_service = AudienceService()
    
    def display(self, segment_data: Dict, segment_type: str = 'Primary', 
                color: str = '#10b981', bg_color: str = '#f0fdf4'):
        """Display an audience segment."""
        if not segment_data:
            return
        
        # Process the segment data
        segment = self.audience_service.process_segment(segment_data, segment_type)
        metrics = self.audience_service.get_metrics(segment)
        
        # Display the segment
        if self.audience_service.is_apple_segment:
            self._display_apple_segment(segment, metrics, color, bg_color)
        else:
            self._display_standard_segment(segment, segment_type, metrics, color, bg_color)
    
    def _display_apple_segment(self, segment: AudienceSegment, metrics: Dict[str, str], 
                             color: str, bg_color: str):
        """Display Apple TV+ specific segment."""
        # Create learning tip bubbles
        audience_segment_tip = display_tip_bubble("audience", "Audience Segment", inline=True)
        interests_tip = display_tip_bubble("audience", "Interest Categories", inline=True)
        platform_tip = display_tip_bubble("audience", "Platform Recommendation", inline=True)
        ai_insight_tip = display_tip_bubble("audience", "AI Insight", inline=True)
        
        # Generate metrics HTML
        metrics_html = self._generate_metrics_html(metrics)
        
        # Generate AI insight HTML
        ai_insight_html = self._generate_ai_insight_html(segment.ai_insight, ai_insight_tip)
        
        # Display the segment
        st.markdown(self._generate_apple_segment_html(
            segment, metrics_html, ai_insight_html, color, bg_color,
            audience_segment_tip, interests_tip, platform_tip
        ), unsafe_allow_html=True)
    
    def _display_standard_segment(self, segment: AudienceSegment, segment_type: str, metrics: Dict[str, str],
                                color: str, bg_color: str):
        """Display standard segment."""
        # Create learning tip bubbles
        audience_segment_tip = display_tip_bubble("audience", "Audience Segment", inline=True)
        demographics_tip = display_tip_bubble("audience", "Demographics", inline=True)
        interests_tip = display_tip_bubble("audience", "Interest Categories", inline=True)
        platform_tip = display_tip_bubble("audience", "Platform Recommendation", inline=True)
        
        # Display the segment
        st.markdown(self._generate_standard_segment_html(
            segment, segment_type, metrics, color, bg_color,
            audience_segment_tip, demographics_tip, interests_tip, platform_tip
        ), unsafe_allow_html=True)
        
        import json
        from dataclasses import asdict
        segment_dict = asdict(segment)
        segment_json = json.dumps(segment_dict, indent=2)

        try:
            CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
            PARENT_DIR = os.path.dirname(CURRENT_DIR)
            HTML_FILE_PATH = os.path.join(PARENT_DIR, "static", "demographics-breakdown/index.html") 

            print(CURRENT_DIR)
            print(PARENT_DIR)
            print(HTML_FILE_PATH)
            with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
                html_code = f.read()

            html_code = html_code.replace("{{DEMOGRAPHICS_BREAKDOWN}}", segment_json)
            components.html(html_code, height=500, scrolling=True)

        except FileNotFoundError:
            st.error(f"ERROR: The HTML file was not found at '{HTML_FILE_PATH}'.")
            st.info("Please make sure 'index.html' is in the correct location.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    def _generate_metrics_html(self, metrics: Dict[str, str]) -> str:
        """Generate HTML for metrics display."""
        metrics_html = '<div style="display: flex; gap: 12px; margin-top: 8px;">'
        
        for metric_type, value in metrics.items():
            color_map = {
                'ctr': ('#065f46', 'rgba(16, 185, 129, 0.1)'),
                'vcr': ('#4338ca', 'rgba(79, 70, 229, 0.1)'),
                'ltr': ('#9a3412', 'rgba(249, 115, 22, 0.1)')
            }
            color, bg = color_map.get(metric_type, ('#333', '#f0f0f0'))
            metrics_html += f'<div style="background-color: {bg}; padding: 5px 8px; border-radius: 4px; flex: 1;">'
            metrics_html += f'<span style="font-weight:600; font-size: 0.75rem; color: {color};">Expected {metric_type.upper()}:</span>'
            metrics_html += f'<span style="font-size: 0.75rem; color: {color};">{value}</span></div>'
        
        metrics_html += '</div>'
        return metrics_html
    
    def _generate_ai_insight_html(self, ai_insight: Optional[str], ai_insight_tip: str) -> str:
        """Generate HTML for AI insight display."""
        if not ai_insight:
            return ""
        return f"""<div style="margin-top: 12px; padding: 8px 12px; background-color: rgba(88, 101, 242, 0.1); border-radius: 6px; border-left: 3px solid #5865f2;">
            <p style="margin: 0; font-size: 0.85rem; color: #333;">
                <span style="font-weight:600; margin-right:5px; display:inline-block; color: #4338ca;">AI Insight {ai_insight_tip}:</span>{ai_insight}
            </p>
        </div>"""
    
    def _generate_apple_segment_html(self, segment: AudienceSegment, metrics_html: str,
                                   ai_insight_html: str, color: str, bg_color: str,
                                   audience_segment_tip: str, interests_tip: str,
                                   platform_tip: str) -> str:
        """Generate HTML for Apple segment display."""
        channel_str = ", ".join(segment.channels) if segment.channels else "Multiple channels"
        device_str = ", ".join(segment.devices) if segment.devices else "Multiple devices"
        
        return f"""<div style="padding: 15px; border-radius: 8px; background-color: {bg_color}; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="color: {color}; font-weight: 600; font-size: 0.8rem;">{segment.segment_type} Audience {audience_segment_tip}</span>
                <span style="background-color: {color}; color: white; font-size: 0.7rem; padding: 3px 8px; border-radius: 12px;">Estimated Size: {segment.size}</span>
            </div>
            <h4 style="margin: 0 0 5px 0; font-size: 1.1rem; color: #333;">{segment.name}</h4>
            <p style="margin: 0 0 12px 0; font-size: 0.85rem; color: #555; font-style: italic;">{segment.description}</p>
            <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: #555;">
                <span style="font-weight:600; margin-right:5px; display:inline-block;">Affinities {interests_tip}:</span>{", ".join(segment.affinities)}
            </p>
            <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: #555;">
                <span style="font-weight:600; margin-right:5px; display:inline-block;">Channels {platform_tip}:</span>{channel_str}
            </p>
            <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: #555;">
                <span style="font-weight:600; margin-right:5px; display:inline-block;">Devices:</span>{device_str}
            </p>
            {metrics_html}
            {ai_insight_html}
        </div>"""
    
    def _generate_standard_segment_html(self, segment: AudienceSegment, segment_type: str, metrics: Dict[str, str],
                                      color: str, bg_color: str, audience_segment_tip: str,
                                      demographics_tip: str, interests_tip: str,
                                      platform_tip: str) -> str:
        """Generate HTML for standard segment display."""
        demographics = []
        if segment.targeting_params:
            if 'age_range' in segment.targeting_params:
                demographics.append(f"Age: {segment.targeting_params['age_range']}")
            if 'gender_targeting' in segment.targeting_params:
                demographics.append(f"Gender: {segment.targeting_params['gender_targeting']}")
            if 'income_targeting' in segment.targeting_params:
                demographics.append(f"Income: {segment.targeting_params['income_targeting']}")
        demographics_str = " | ".join(demographics) if demographics else "Custom targeting parameters"

        print(segment_type)
        print(metrics)
        print(color)
        print(bg_color)


        platform_rec = ""
        if segment.platform_targeting and len(segment.platform_targeting) > 0:
            platform_rec = segment.platform_targeting[0].get('platform', '')
        

        # platform_targeting = segment.get('platform_targeting', [])
        # if platform_targeting and len(platform_targeting) > 0:
        #     platform_rec = platform_targeting[0].get('platform', '')

        metric_name = "Expected CTR"
        # Get performance metrics
        performance = segment.expected_performance
        ctr = performance.get('CTR', 'N/A')


        if platform_rec:
            platform_lower = platform_rec.lower()
            print("platform_lower")
            print(platform_lower)
            
            # ONLY show Expected LTR for Audio platforms
            if 'audio' in platform_lower or 'podcast' in platform_lower or 'music' in platform_lower:
                metric_name = "Expected LTR"
                ctr = "90-100%"
                # Create a dynamic range based on segment name
                if 'young' in segment.name.lower() or 'gen z' in segment.name.lower():
                    # Younger audiences tend to have lower LTR ranges
                    ctr = "80-90%"
                elif 'fitness' in segment.name.lower():
                    # Fitness audience has medium-high LTR
                    ctr = "80-90%"
                elif 'professional' in segment.name.lower():
                    # Professional audiences tend to have high LTR
                    ctr = "80-90%"
                else:
                    # Default if we can't determine specifics
                    ctr = "80-90%"
            
            # ONLY show Expected VCR for Video platforms
            elif 'video' in platform_lower or 'ott' in platform_lower or 'ctv' in platform_lower or ('streaming' in platform_lower and 'audio' not in platform_lower):
                metric_name = "Expected VCR"
                # VCR should be 90-100% for all CTV/OTT recommendations
                ctr = "90-100%"
            
            # ONLY show Expected CTR for Display platforms
            elif 'display' in platform_lower or 'banner' in platform_lower or 'rich' in platform_lower or 'interactive' in platform_lower or 'high-impact' in platform_lower:
                metric_name = "Expected CTR"
                # Keep the provided CTR or use a default
                if performance and 'CTR' in performance:
                    ctr = performance.get('CTR')
                else:
                    # Default based on segment type
                    if 'primary' in segment_type.lower():
                        ctr = "0.22%"
                    elif 'secondary' in segment_type.lower():
                        ctr = "0.19%"
                    else:
                        ctr = "0.18%"
            elif 'DOOH' in platform_lower or 'digital out of home' in platform_lower or 'out-of-home' in platform_lower:
                metric_name = "Expected Outcome"
                ctr = "N/A"

        ctr_to_use = metrics.get('ctr', ctr)
        if 'DOOH' in platform_lower or 'digital out of home' in platform_lower or 'out-of-home' in platform_lower:
            ctr_to_use = 'N/A'
        elif 'video' in platform_lower:
            ctr_to_use = '70-90%'
        elif 'ott/ctv' in platform_lower or 'ctv/ott' in platform_lower:
            ctr_to_use = '90-100%'



        return f"""<div style="padding: 15px; border-radius: 8px; background-color: {bg_color}; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="color: {color}; font-weight: 600; font-size: 0.8rem;">{segment.segment_type} Audience {audience_segment_tip}</span>
                <span style="background-color: {color}; color: white; font-size: 0.7rem; padding: 3px 8px; border-radius: 12px;">{metric_name}: {ctr_to_use}</span>
            </div>
            <h4 style="margin: 0 0 5px 0; font-size: 1.1rem; color: #333;">{segment.name}</h4>
            <p style="margin: 0 0 12px 0; font-size: 0.85rem; color: #555; font-style: italic;">{segment.description}</p>
            <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: #555;">
                <span style="font-weight:600; margin-right:5px; display:inline-block;">Demographics {demographics_tip}</span>{demographics_str}
            </p>
            <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: #555;">
                <span style="font-weight:600; margin-right:5px; display:inline-block;">Interests {interests_tip}</span>{", ".join(segment.affinities)}
            </p>
            <p style="margin: 0 0 0 0; font-size: 0.85rem; color: #555;">
                <span style="font-weight:600; margin-right:5px; display:inline-block;">Recommended Platform {platform_tip}</span>{platform_rec}
            </p>
        </div>"""
