"""Marketing Benchmark Engine - Marketing Intelligence"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class KPIDirection(Enum):
    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"


class KPICategory(Enum):
    ACQUISITION = "Acquisition"
    ENGAGEMENT = "Engagement"
    CONVERSION = "Conversion"
    RETENTION = "Retention"
    REVENUE = "Revenue"
    BRAND = "Brand"
    CONTENT = "Content"


@dataclass
class KPIDefinition:
    kpi_id: str
    name: str
    benchmark_value: float
    direction: KPIDirection = KPIDirection.HIGHER_IS_BETTER
    category: KPICategory = KPICategory.ACQUISITION
    unit: str = ""
    weight: float = 1.0


@dataclass
class KPIScore:
    kpi_id: str
    kpi_name: str
    actual_value: float
    benchmark_value: float
    score: float
    gap: float
    gap_percent: float
    rating: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {"kpi_id": self.kpi_id, "kpi_name": self.kpi_name, "actual_value": self.actual_value,
                "benchmark_value": self.benchmark_value, "score": round(self.score, 1),
                "gap": round(self.gap, 2), "rating": self.rating, "recommendation": self.recommendation}


@dataclass
class BenchmarkReport:
    entity_id: str
    overall_score: float
    overall_rating: str
    grade: str
    category_scores: Dict[str, float]
    kpi_scores: List[KPIScore]
    strengths: List[str]
    improvements: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {"entity_id": self.entity_id, "overall_score": round(self.overall_score, 1),
                "overall_rating": self.overall_rating, "grade": self.grade,
                "category_scores": {k: round(v, 1) for k, v in self.category_scores.items()},
                "strengths": self.strengths, "improvements": self.improvements, "recommendations": self.recommendations}


class BenchmarkEngine:
    RATING_THRESHOLDS = {90: "Excellent", 75: "Good", 60: "Fair", 40: "Poor", 0: "Critical"}
    GRADE_THRESHOLDS = {90: "A", 80: "B", 70: "C", 60: "D", 0: "F"}

    def __init__(self, kpis: List[KPIDefinition], category_weights: Optional[Dict[str, float]] = None):
        self.kpis = {k.kpi_id: k for k in kpis}
        self.category_weights = category_weights or {}

    def analyze(self, actual_values: Dict[str, float], entity_id: str = "unknown") -> BenchmarkReport:
        kpi_scores = []
        category_totals: Dict[str, List[float]] = {}

        for kpi_id, kpi in self.kpis.items():
            actual = actual_values.get(kpi_id)
            if actual is None:
                continue
            score = self._score_kpi(kpi, actual)
            kpi_scores.append(score)
            cat = kpi.category.value
            if cat not in category_totals:
                category_totals[cat] = []
            category_totals[cat].append(score.score)

        category_scores = {cat: sum(scores) / len(scores) for cat, scores in category_totals.items() if scores}
        overall = sum(s * self.category_weights.get(c, 1) for c, s in category_scores.items()) / sum(self.category_weights.get(c, 1) for c in category_scores) if category_scores else 0

        sorted_kpis = sorted(kpi_scores, key=lambda x: x.score, reverse=True)
        strengths = [f"{k.kpi_name}: {k.actual_value}{self.kpis[k.kpi_id].unit}" for k in sorted_kpis[:3] if k.score >= 75]
        improvements = [f"{k.kpi_name}: {k.actual_value}{self.kpis[k.kpi_id].unit}" for k in sorted_kpis[-3:] if k.score < 60]
        recommendations = [k.recommendation for k in kpi_scores if k.rating in ["Poor", "Critical"]][:5]

        return BenchmarkReport(entity_id, overall, self._rate(overall), self._grade(overall),
                              category_scores, kpi_scores, strengths, improvements, recommendations)

    def _score_kpi(self, kpi: KPIDefinition, actual: float) -> KPIScore:
        benchmark = kpi.benchmark_value
        gap = actual - benchmark
        gap_pct = (gap / benchmark * 100) if benchmark != 0 else 0

        if kpi.direction == KPIDirection.HIGHER_IS_BETTER:
            score = min(120, (actual / benchmark * 100)) if benchmark > 0 else 100
        else:
            score = min(120, (benchmark / actual * 100)) if actual > 0 else 100

        rating = self._rate(score)
        direction = "increase" if kpi.direction == KPIDirection.HIGHER_IS_BETTER else "decrease"
        rec = f"Maintain {kpi.name}" if rating in ["Excellent", "Good"] else f"{direction.capitalize()} {kpi.name}"

        return KPIScore(kpi.kpi_id, kpi.name, actual, benchmark, score, gap, gap_pct, rating, rec)

    def _rate(self, score: float) -> str:
        for t, r in sorted(self.RATING_THRESHOLDS.items(), reverse=True):
            if score >= t: return r
        return "Critical"

    def _grade(self, score: float) -> str:
        for t, g in sorted(self.GRADE_THRESHOLDS.items(), reverse=True):
            if score >= t: return g
        return "F"


def create_marketing_benchmarks() -> BenchmarkEngine:
    kpis = [
        KPIDefinition("cac", "Customer Acquisition Cost", 50.0, KPIDirection.LOWER_IS_BETTER, KPICategory.ACQUISITION, "$"),
        KPIDefinition("cpl", "Cost per Lead", 25.0, KPIDirection.LOWER_IS_BETTER, KPICategory.ACQUISITION, "$"),
        KPIDefinition("conversion_rate", "Conversion Rate", 3.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.CONVERSION, "%"),
        KPIDefinition("lead_to_customer", "Lead to Customer Rate", 20.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.CONVERSION, "%"),
        KPIDefinition("email_open_rate", "Email Open Rate", 25.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.ENGAGEMENT, "%"),
        KPIDefinition("email_ctr", "Email Click-Through Rate", 3.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.ENGAGEMENT, "%"),
        KPIDefinition("social_engagement", "Social Engagement Rate", 2.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.ENGAGEMENT, "%"),
        KPIDefinition("customer_retention", "Customer Retention Rate", 85.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.RETENTION, "%"),
        KPIDefinition("churn_rate", "Churn Rate", 5.0, KPIDirection.LOWER_IS_BETTER, KPICategory.RETENTION, "%"),
        KPIDefinition("clv", "Customer Lifetime Value", 500.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.REVENUE, "$"),
        KPIDefinition("roas", "Return on Ad Spend", 400.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.REVENUE, "%"),
        KPIDefinition("marketing_roi", "Marketing ROI", 100.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.REVENUE, "%"),
        KPIDefinition("brand_awareness", "Brand Awareness", 30.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.BRAND, "%"),
        KPIDefinition("nps", "Net Promoter Score", 50.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.BRAND, ""),
    ]
    return BenchmarkEngine(kpis, {"Acquisition": 1.2, "Conversion": 1.2, "Revenue": 1.1, "Engagement": 1.0, "Retention": 1.0, "Brand": 0.9})


def create_digital_benchmarks() -> BenchmarkEngine:
    kpis = [
        KPIDefinition("website_traffic", "Monthly Website Traffic", 10000, KPIDirection.HIGHER_IS_BETTER, KPICategory.ACQUISITION, ""),
        KPIDefinition("bounce_rate", "Bounce Rate", 50.0, KPIDirection.LOWER_IS_BETTER, KPICategory.ENGAGEMENT, "%"),
        KPIDefinition("pages_per_session", "Pages per Session", 3.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.ENGAGEMENT, ""),
        KPIDefinition("session_duration", "Avg Session Duration", 180, KPIDirection.HIGHER_IS_BETTER, KPICategory.ENGAGEMENT, "sec"),
        KPIDefinition("organic_traffic", "Organic Traffic %", 40.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.ACQUISITION, "%"),
        KPIDefinition("paid_ctr", "Paid Ads CTR", 2.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.CONVERSION, "%"),
        KPIDefinition("landing_conversion", "Landing Page Conversion", 5.0, KPIDirection.HIGHER_IS_BETTER, KPICategory.CONVERSION, "%"),
        KPIDefinition("cart_abandonment", "Cart Abandonment Rate", 70.0, KPIDirection.LOWER_IS_BETTER, KPICategory.CONVERSION, "%"),
    ]
    return BenchmarkEngine(kpis)
