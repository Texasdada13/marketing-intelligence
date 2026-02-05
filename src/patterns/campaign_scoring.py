"""Campaign Scoring Engine - Marketing Intelligence"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class CampaignStatus(Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"
    CRITICAL = "Critical"


@dataclass
class ScoringComponent:
    component_id: str
    name: str
    weight: float
    higher_is_better: bool = True
    min_value: float = 0
    max_value: float = 100


@dataclass
class ComponentScore:
    component_id: str
    name: str
    raw_value: float
    normalized_score: float
    weighted_score: float
    rating: str

    def to_dict(self) -> Dict[str, Any]:
        return {"component_id": self.component_id, "name": self.name, "raw_value": round(self.raw_value, 2),
                "normalized_score": round(self.normalized_score, 1), "weighted_score": round(self.weighted_score, 1), "rating": self.rating}


@dataclass
class CampaignScore:
    campaign_id: str
    campaign_name: str
    overall_score: float
    status: CampaignStatus
    component_scores: List[ComponentScore]
    strengths: List[str]
    improvements: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {"campaign_id": self.campaign_id, "campaign_name": self.campaign_name, "overall_score": round(self.overall_score, 1),
                "status": self.status.value, "component_scores": [c.to_dict() for c in self.component_scores],
                "strengths": self.strengths, "improvements": self.improvements, "recommendations": self.recommendations}


class CampaignScoringEngine:
    RATING_THRESHOLDS = {90: "Excellent", 75: "Good", 60: "Fair", 40: "Poor", 0: "Critical"}

    def __init__(self, components: List[ScoringComponent]):
        self.components = {c.component_id: c for c in components}
        self.total_weight = sum(c.weight for c in components)

    def score(self, campaign_id: str, campaign_name: str, values: Dict[str, float]) -> CampaignScore:
        component_scores = []
        total_weighted = 0
        total_weight_used = 0

        for comp_id, comp in self.components.items():
            raw = values.get(comp_id)
            if raw is None:
                continue
            normalized = self._normalize(raw, comp)
            weighted = normalized * (comp.weight / self.total_weight)
            rating = self._rate(normalized)
            component_scores.append(ComponentScore(comp_id, comp.name, raw, normalized, weighted * 100, rating))
            total_weighted += weighted
            total_weight_used += comp.weight / self.total_weight

        overall = (total_weighted / total_weight_used * 100) if total_weight_used > 0 else 0
        status = self._determine_status(overall)
        sorted_scores = sorted(component_scores, key=lambda x: x.normalized_score, reverse=True)
        strengths = [s.name for s in sorted_scores[:3] if s.normalized_score >= 70]
        improvements = [s.name for s in sorted_scores[-3:] if s.normalized_score < 60]
        recommendations = self._generate_recommendations(status, component_scores)

        return CampaignScore(campaign_id, campaign_name, overall, status, component_scores, strengths, improvements, recommendations)

    def _normalize(self, value: float, comp: ScoringComponent) -> float:
        range_size = comp.max_value - comp.min_value
        if range_size == 0:
            return 50
        if comp.higher_is_better:
            return max(0, min(100, ((value - comp.min_value) / range_size) * 100))
        return max(0, min(100, ((comp.max_value - value) / range_size) * 100))

    def _rate(self, score: float) -> str:
        for threshold, rating in sorted(self.RATING_THRESHOLDS.items(), reverse=True):
            if score >= threshold:
                return rating
        return "Critical"

    def _determine_status(self, score: float) -> CampaignStatus:
        if score >= 90: return CampaignStatus.EXCELLENT
        if score >= 75: return CampaignStatus.GOOD
        if score >= 60: return CampaignStatus.FAIR
        if score >= 40: return CampaignStatus.POOR
        return CampaignStatus.CRITICAL

    def _generate_recommendations(self, status: CampaignStatus, scores: List[ComponentScore]) -> List[str]:
        recs = []
        weak = [s for s in scores if s.normalized_score < 60]
        for s in weak[:3]:
            recs.append(f"Improve {s.name} performance")
        if status == CampaignStatus.CRITICAL:
            recs.insert(0, "Consider pausing campaign for optimization")
        elif status == CampaignStatus.EXCELLENT:
            recs.append("Scale successful tactics to other campaigns")
        return recs[:5]


def create_campaign_performance_engine() -> CampaignScoringEngine:
    components = [
        ScoringComponent("conversion_rate", "Conversion Rate", 25, True, 0, 10),
        ScoringComponent("click_through_rate", "Click-Through Rate", 20, True, 0, 5),
        ScoringComponent("cost_per_acquisition", "Cost per Acquisition", 20, False, 0, 100),
        ScoringComponent("return_on_ad_spend", "Return on Ad Spend", 20, True, 0, 500),
        ScoringComponent("engagement_rate", "Engagement Rate", 15, True, 0, 10),
    ]
    return CampaignScoringEngine(components)
