# core/models/audience.py
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class AudienceSegment:
    name: str
    description: str
    size: str
    segment_type: str
    affinities: List[str]
    channels: List[str]
    devices: List[str]
    expected_ctr: Optional[str] = None
    expected_vcr: Optional[str] = None
    expected_ltr: Optional[str] = None
    ai_insight: Optional[str] = None
    targeting_params: Optional[Dict] = None
    platform_targeting: Optional[List[Dict]] = None
    expected_performance: Optional[Dict] = None
    demographics: Optional[Dict] = None
    languageRecommendations: Optional[List[Dict]] = None
