# services/audience_service.py
from core.models.audience import AudienceSegment
from typing import Dict

class AudienceService:
    def __init__(self):
        self.is_apple_segment = False
    
    def process_segment(self, segment_data: Dict, segment_type: str = 'Primary') -> AudienceSegment:
        """Process raw segment data into an AudienceSegment object."""
        self.is_apple_segment = 'expected_vcr' in segment_data or 'expected_ctr' in segment_data
        
        if self.is_apple_segment:
            return self._process_apple_segment(segment_data, segment_type)
        else:
            return self._process_standard_segment(segment_data, segment_type)
    
    def _process_apple_segment(self, segment_data: Dict, segment_type: str) -> AudienceSegment:
        """Process Apple TV+ specific segment data."""
        return AudienceSegment(
            name=segment_data.get('name', 'Audience Segment'),
            description=segment_data.get('description', ''),
            size=segment_data.get('size', ''),
            segment_type=segment_type,
            affinities=segment_data.get('affinities', []),
            channels=segment_data.get('channels', []),
            devices=segment_data.get('devices', []),
            expected_ctr=segment_data.get('expected_ctr'),
            expected_vcr=segment_data.get('expected_vcr'),
            ai_insight=segment_data.get('ai_insight'),
            languageRecommendations=segment_data.get('languageRecommendations', None)
        )
    
    def _process_standard_segment(self, segment_data: Dict, segment_type: str) -> AudienceSegment:
        """Process standard segment data."""
        targeting_params = segment_data.get('targeting_params', {})
        platform_targeting = segment_data.get('platform_targeting', [])
        performance = segment_data.get('expected_performance', {})
        demographics = segment_data.get('demographics', {})
        language_recommendations = segment_data.get('languageRecommendations', None)

        return AudienceSegment(
            name=segment_data.get('name', 'Audience Segment'),
            description=segment_data.get('description', ''),
            size=segment_data.get('size', segment_data.get('audience_size', '')),
            segment_type=segment_type,
            affinities=segment_data.get('interest_categories', segment_data.get('affinities', [])),
            channels=[],
            devices=[],
            targeting_params=targeting_params,
            platform_targeting=platform_targeting,
            expected_performance=performance,
            demographics=demographics,
            languageRecommendations=language_recommendations
        )
    
    def get_metrics(self, segment: AudienceSegment) -> Dict[str, str]:
        """Get performance metrics for the segment."""
        metrics = {}
        
        if self.is_apple_segment:
            if segment.expected_ctr:
                metrics['ctr'] = segment.expected_ctr
            if segment.expected_vcr:
                metrics['vcr'] = segment.expected_vcr
            if segment.expected_ltr:
                metrics['ltr'] = segment.expected_ltr
        else:
            if segment.expected_performance:
                metrics['ctr'] = segment.expected_performance.get('CTR', '0.20%')
        
        return metrics
