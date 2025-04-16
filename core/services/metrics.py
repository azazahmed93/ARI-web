# services/metrics_service.py
from core.models.metrics import MetricsData, RadarChartData
from core.utils import hash
from typing import Dict, List, Optional

class MetricsService:
    def __init__(self):
        self.weighted_metrics = {
            "Cultural Authority": 1.5,
            "Buzz & Conversation": 1.3,
            "Cultural Vernacular": 1.2,
            "Commerce Bridge": 1.2,
            "Platform Relevance": 1.1
        }
    
    def process_metrics(self, metrics_data: MetricsData) -> RadarChartData:
        """Process raw metrics data into structured format for visualization."""
        # Calculate average score
        avg_score = sum(metrics_data.scores.values()) / len(metrics_data.scores)
        
        # Process scores for radar chart
        categories = list(metrics_data.scores.keys())
        values = list(metrics_data.scores.values())
        
        # Add first value at end to close the loop
        categories.append(categories[0])
        values.append(values[0])
        
        # Generate benchmark values
        benchmark_values = self._generate_benchmark_values(
            metrics_data.scores, 
            metrics_data.brief_text
        )
        
        # Calculate RCC score
        rcc_score = self._calculate_rcc_score(
            metrics_data.scores, 
            metrics_data.brief_text, 
            avg_score
        )
        
        # Calculate ROI potential
        roi_potential = self._calculate_roi_potential(
            metrics_data.scores, 
            metrics_data.ai_insights
        )
        
        # Get top strengths
        top_strengths = self._get_top_strengths(
            metrics_data.scores, 
            metrics_data.ai_insights
        )
        
        return RadarChartData(
            categories=categories,
            values=values,
            benchmark_values=benchmark_values,
            rcc_score=rcc_score,
            roi_potential=roi_potential,
            top_strengths=top_strengths
        )
    
    def _generate_benchmark_values(self, scores: Dict[str, float], brief_text: str) -> List[float]:
        """Generate benchmark values based on brief content."""
        benchmark_adjustments = self._get_benchmark_adjustments(brief_text)
        
        benchmark_values = []
        for metric in scores.keys():
            current_score = scores[metric]
            adjustment = benchmark_adjustments.get(metric, 1.5)
            benchmark = min(10.0, current_score + adjustment)
            benchmark_values.append(benchmark)
        
        # Add first value at end to close the loop
        benchmark_values.append(benchmark_values[0])
        return benchmark_values
    
    def _get_benchmark_adjustments(self, brief_text: str) -> Dict[str, float]:
        """Get benchmark adjustments based on brief content."""
        if not brief_text:
            return {}
            
        if "Gen Z" in brief_text or "GenZ" in brief_text or "Generation Z" in brief_text:
            return {
                "Cultural Vernacular": 2.0,
                "Platform Relevance": 2.2,
                "Buzz & Conversation": 2.0
            }
        elif "Hispanic" in brief_text or "Latino" in brief_text:
            return {
                "Cultural Relevance": 2.1,
                "Representation": 2.0,
                "Geo-Cultural Fit": 1.8
            }
        elif "luxury" in brief_text.lower() or "premium" in brief_text.lower():
            return {
                "Cultural Authority": 2.2,
                "Media Ownership Equity": 1.8,
                "Commerce Bridge": 1.7
            }
        elif "retail" in brief_text.lower() or "shopping" in brief_text.lower():
            return {
                "Commerce Bridge": 2.3,
                "Platform Relevance": 1.9,
                "Buzz & Conversation": 1.7
            }
        else:
            return {
                "Cultural Relevance": 1.7,
                "Platform Relevance": 1.8,
                "Cultural Vernacular": 1.7,
                "Cultural Authority": 1.7,
                "Buzz & Conversation": 1.8,
                "Commerce Bridge": 1.7,
                "Geo-Cultural Fit": 1.6,
                "Media Ownership Equity": 1.6,
                "Representation": 1.7
            }
    
    def _calculate_rcc_score(self, scores: Dict[str, float], brief_text: str, avg_score: float) -> float:
        """Calculate Resonance Convergence Coefficient score."""
        if not brief_text or not scores:
            return avg_score
            
        weights = {
            "Cultural Authority": 1.3,
            "Cultural Vernacular": 1.2,
            "Cultural Relevance": 1.2,
            "Buzz & Conversation": 1.1,
            "Platform Relevance": 1.0,
            "Representation": 1.0,
            "Geo-Cultural Fit": 0.9,
            "Commerce Bridge": 0.9,
            "Media Ownership Equity": 0.8
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for metric, score in scores.items():
            weight = weights.get(metric, 1.0)
            weighted_sum += score * weight
            total_weight += weight
        
        weighted_avg = weighted_sum / total_weight if total_weight > 0 else avg_score
        
        brief_hash = hash(brief_text)
        score_adjustment = ((brief_hash % 100) / 100) * 0.4 - 0.2
        
        adjusted_score = min(10, max(1, weighted_avg + score_adjustment))
        return round(adjusted_score * 10) / 10
    
    def _calculate_roi_potential(self, scores: Dict[str, float], ai_insights: Optional[Dict]) -> str:
        """Calculate ROI potential."""
        if ai_insights and 'performance_prediction' in ai_insights:
            prediction = ai_insights['performance_prediction']
            if '%' in prediction:
                import re
                roi_match = re.search(r'(\+\d+%|\d+%)', prediction)
                if roi_match:
                    roi_potential = roi_match.group(0)
                    if not roi_potential.startswith('+'):
                        roi_potential = f"+{roi_potential}"
                    return roi_potential
        
        roi_sum = 0
        roi_weight_total = 0
        
        for metric, score in scores.items():
            weight = self.weighted_metrics.get(metric, 0.8)
            roi_sum += score * weight
            roi_weight_total += weight
        
        if roi_weight_total > 0:
            roi_score = roi_sum / roi_weight_total
            roi_percent = int(5 + (roi_score / 10) * 20)
            return f"+{roi_percent}%"
        else:
            avg_score = sum(scores.values()) / len(scores)
            roi_percent = int(5 + (avg_score / 10) * 20)
            return f"+{roi_percent}%"
    
    def _get_top_strengths(self, scores: Dict[str, float], ai_insights: Optional[Dict]) -> List[str]:
        """Get top campaign strengths."""
        if ai_insights and 'strengths' in ai_insights:
            strengths = ai_insights['strengths']
            return [s.get('area', 'Cultural Alignment') for s in strengths[:2]]
        
        metric_scores = list(scores.items())
        metric_scores.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in metric_scores[:2]]
