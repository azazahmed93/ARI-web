"""
Data integration module for handling media and psychographics data.
This module provides functionality to integrate uploaded data with AI-generated insights.
"""

from typing import Dict, Optional
from core.ai_insights import generate_deep_insights, generate_audience_segments

class DataIntegrator:
    """Class that handles integration of uploaded data with AI-generated insights."""
    
    def __init__(self):
        """Initialize the data integrator."""
        self.media_data = None
        self.psychographics_data = None
    
    def set_media_data(self, media_data: Dict):
        """Set the uploaded media data."""
        self.media_data = media_data
    
    def set_psychographics_data(self, psychographics_data: Dict):
        """Set the uploaded psychographics data."""
        self.psychographics_data = psychographics_data
    
    def get_relevant_media_insights(self, brief_text: str, industry: str) -> Dict:
        """
        Get relevant media insights, using uploaded data if available, otherwise falling back to AI-generated insights.
        
        Args:
            brief_text (str): The marketing brief or RFP text
            industry (str): The industry classification
            
        Returns:
            dict: Media insights data
        """
        if self.media_data:
            # Process uploaded media data
            return self._process_media_data(self.media_data, brief_text, industry)
        else:
            # Fallback to AI-generated insights
            return self._generate_media_insights(brief_text, industry)
    
    def get_relevant_psychographics(self, brief_text: str, industry: str) -> Dict:
        """
        Get relevant psychographic insights, using uploaded data if available, otherwise falling back to AI-generated insights.
        
        Args:
            brief_text (str): The marketing brief or RFP text
            industry (str): The industry classification
            
        Returns:
            dict: Psychographic insights data
        """
        if self.psychographics_data:
            # Process uploaded psychographics data
            return self._process_psychographics_data(self.psychographics_data, brief_text, industry)
        else:
            # Fallback to AI-generated insights
            return self._generate_psychographic_insights(brief_text, industry)
    
    def _process_media_data(self, media_data: Dict, brief_text: str, industry: str) -> Dict:
        """Process uploaded media data to extract relevant insights."""
        # Extract campaign vertical from brief
        vertical = self._extract_campaign_vertical(brief_text)
        
        # Filter media data based on vertical and industry
        filtered_data = self._filter_media_data(media_data, vertical, industry)
        
        # Format insights for display
        return {
            'top_platforms': self._get_top_platforms(filtered_data),
            'media_affinities': self._get_media_affinities(filtered_data),
            'platform_recommendations': self._get_platform_recommendations(filtered_data, brief_text)
        }
    
    def _process_psychographics_data(self, psychographics_data: Dict, brief_text: str, industry: str) -> Dict:
        """Process uploaded psychographics data to extract relevant insights."""
        # Extract audience keywords from brief
        keywords = self._extract_audience_keywords(brief_text)
        
        # Filter psychographics data based on keywords and industry
        filtered_data = self._filter_psychographics_data(psychographics_data, keywords, industry)
        
        # Format insights for display
        return {
            'audience_size': filtered_data.get('audience_size', 'N/A'),
            'engagement_rate': filtered_data.get('engagement_rate', 'N/A'),
            'conversion_rate': filtered_data.get('conversion_rate', 'N/A'),
            'demographics': filtered_data.get('demographics', {}),
            'values': filtered_data.get('values', []),
            'drivers': filtered_data.get('drivers', [])
        }
    
    def _generate_media_insights(self, brief_text: str, industry: str) -> Dict:
        """Generate AI-powered media insights when no data is uploaded."""
        # Use AI to generate insights based on brief and industry
        ai_insights = generate_deep_insights(brief_text, {})
        
        return {
            'top_platforms': ai_insights.get('media_platforms', []),
            'media_affinities': ai_insights.get('media_affinities', []),
            'platform_recommendations': ai_insights.get('platform_recommendations', [])
        }
    
    def _generate_psychographic_insights(self, brief_text: str, industry: str) -> Dict:
        """Generate AI-powered psychographic insights when no data is uploaded."""
        # Use AI to generate insights based on brief and industry
        ai_insights = generate_audience_segments(brief_text, {})
        
        return {
            'audience_size': ai_insights.get('audience_size', 'N/A'),
            'engagement_rate': ai_insights.get('engagement_rate', 'N/A'),
            'conversion_rate': ai_insights.get('conversion_rate', 'N/A'),
            'demographics': ai_insights.get('demographics', {}),
            'values': ai_insights.get('values', []),
            'drivers': ai_insights.get('drivers', [])
        }
    
    def _extract_campaign_vertical(self, brief_text: str) -> str:
        """Extract campaign vertical from brief text."""
        # Simple implementation - in production, this would use NLP
        verticals = ['entertainment', 'technology', 'retail', 'finance', 'healthcare']
        brief_lower = brief_text.lower()
        for vertical in verticals:
            if vertical in brief_lower:
                return vertical
        return 'general'
    
    def _extract_audience_keywords(self, brief_text: str) -> list:
        """Extract audience keywords from brief text."""
        # Simple implementation - in production, this would use NLP
        keywords = []
        brief_lower = brief_text.lower()
        
        # Common audience descriptors
        descriptors = ['young', 'millennial', 'gen z', 'gen x', 'baby boomer',
                      'urban', 'suburban', 'rural', 'affluent', 'budget-conscious']
        
        for desc in descriptors:
            if desc in brief_lower:
                keywords.append(desc)
        
        return keywords
    
    def _filter_media_data(self, media_data: Dict, vertical: str, industry: str) -> Dict:
        """Filter media data based on campaign vertical and industry."""
        # Simple implementation - in production, this would use more sophisticated filtering
        filtered_data = {}
        
        # Filter platforms based on vertical and industry
        if 'platforms' in media_data:
            filtered_data['platforms'] = [
                p for p in media_data['platforms']
                if vertical in p.get('verticals', []) or 'general' in p.get('verticals', [])
            ]
        
        # Filter affinities based on industry
        if 'affinities' in media_data:
            filtered_data['affinities'] = [
                a for a in media_data['affinities']
                if industry.lower() in a.get('industries', []) or 'general' in a.get('industries', [])
            ]
        
        return filtered_data
    
    def _filter_psychographics_data(self, psychographics_data: Dict, keywords: list, industry: str) -> Dict:
        """Filter psychographics data based on keywords and industry."""
        # Simple implementation - in production, this would use more sophisticated filtering
        filtered_data = {}
        
        # Filter demographics based on keywords
        if 'demographics' in psychographics_data:
            filtered_data['demographics'] = {
                k: v for k, v in psychographics_data['demographics'].items()
                if any(keyword in k.lower() for keyword in keywords)
            }
        
        # Filter values and drivers based on industry
        if 'values' in psychographics_data:
            filtered_data['values'] = [
                v for v in psychographics_data['values']
                if industry.lower() in v.get('industries', []) or 'general' in v.get('industries', [])
            ]
        
        if 'drivers' in psychographics_data:
            filtered_data['drivers'] = [
                d for d in psychographics_data['drivers']
                if industry.lower() in d.get('industries', []) or 'general' in d.get('industries', [])
            ]
        
        return filtered_data
    
    def _get_top_platforms(self, media_data: Dict) -> list:
        """Get top performing platforms from media data."""
        if 'platforms' not in media_data:
            return []
        
        # Sort platforms by engagement score
        platforms = sorted(
            media_data['platforms'],
            key=lambda x: x.get('engagement_score', 0),
            reverse=True
        )
        
        return platforms[:5]  # Return top 5 platforms
    
    def _get_media_affinities(self, media_data: Dict) -> list:
        """Get media affinities from media data."""
        if 'affinities' not in media_data:
            return []
        
        # Format affinities for display
        return [
            {
                'platform': a.get('platform', ''),
                'affinity_score': a.get('score', 0),
                'audience_overlap': a.get('overlap', 0)
            }
            for a in media_data['affinities']
        ]
    
    def _get_platform_recommendations(self, media_data: Dict, brief_text: str) -> list:
        """Get platform-specific recommendations based on media data and brief."""
        if 'platforms' not in media_data:
            return []
        
        # Generate recommendations for each platform
        recommendations = []
        for platform in media_data['platforms']:
            recommendations.append({
                'platform': platform.get('name', ''),
                'recommendation': platform.get('recommendation', ''),
                'expected_impact': platform.get('impact_score', 0)
            })
        
        return recommendations 
