# core/models/metrics.py
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MetricsData:
    scores: Dict[str, float]
    brief_text: str
    improvement_areas: List[str]
    ai_insights: Optional[Dict] = None

@dataclass
class RadarChartData:
    categories: List[str]
    values: List[float]
    benchmark_values: List[float]
    rcc_score: float
    roi_potential: str
    top_strengths: List[str]
