"""Marketing Channel Performance Analyzer"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class ChannelType(Enum):
    ORGANIC_SEARCH = "Organic Search"
    PAID_SEARCH = "Paid Search"
    SOCIAL_ORGANIC = "Social (Organic)"
    SOCIAL_PAID = "Social (Paid)"
    EMAIL = "Email"
    DISPLAY = "Display Ads"
    AFFILIATE = "Affiliate"
    REFERRAL = "Referral"
    DIRECT = "Direct"
    VIDEO = "Video"
    CONTENT = "Content Marketing"


@dataclass
class ChannelMetrics:
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    revenue: float = 0.0
    leads: int = 0
    new_customers: int = 0


@dataclass
class ChannelPerformance:
    channel: ChannelType
    metrics: ChannelMetrics
    ctr: float
    conversion_rate: float
    cpc: float
    cpa: float
    roas: float
    contribution_percent: float
    efficiency_score: float
    rating: str
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel": self.channel.value,
            "metrics": {
                "impressions": self.metrics.impressions,
                "clicks": self.metrics.clicks,
                "conversions": self.metrics.conversions,
                "spend": self.metrics.spend,
                "revenue": self.metrics.revenue,
                "leads": self.metrics.leads
            },
            "ctr": round(self.ctr, 2),
            "conversion_rate": round(self.conversion_rate, 2),
            "cpc": round(self.cpc, 2),
            "cpa": round(self.cpa, 2),
            "roas": round(self.roas, 2),
            "contribution_percent": round(self.contribution_percent, 1),
            "efficiency_score": round(self.efficiency_score, 1),
            "rating": self.rating,
            "recommendations": self.recommendations
        }


@dataclass
class ChannelMix:
    total_spend: float
    total_revenue: float
    total_conversions: int
    overall_roas: float
    channel_performances: List[ChannelPerformance]
    top_performers: List[str]
    underperformers: List[str]
    optimization_opportunities: List[str]
    recommended_budget_shifts: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_spend": round(self.total_spend, 2),
            "total_revenue": round(self.total_revenue, 2),
            "total_conversions": self.total_conversions,
            "overall_roas": round(self.overall_roas, 2),
            "channel_performances": [cp.to_dict() for cp in self.channel_performances],
            "top_performers": self.top_performers,
            "underperformers": self.underperformers,
            "optimization_opportunities": self.optimization_opportunities,
            "recommended_budget_shifts": {k: round(v, 1) for k, v in self.recommended_budget_shifts.items()}
        }


class ChannelAnalyzer:
    """Analyzes marketing channel performance and mix optimization."""

    CHANNEL_BENCHMARKS = {
        ChannelType.ORGANIC_SEARCH: {"ctr": 3.0, "conversion_rate": 3.0, "cpa": 30.0},
        ChannelType.PAID_SEARCH: {"ctr": 2.0, "conversion_rate": 2.5, "cpa": 50.0},
        ChannelType.SOCIAL_ORGANIC: {"ctr": 1.0, "conversion_rate": 1.5, "cpa": 0.0},
        ChannelType.SOCIAL_PAID: {"ctr": 1.5, "conversion_rate": 1.0, "cpa": 40.0},
        ChannelType.EMAIL: {"ctr": 3.5, "conversion_rate": 4.0, "cpa": 10.0},
        ChannelType.DISPLAY: {"ctr": 0.5, "conversion_rate": 0.5, "cpa": 60.0},
        ChannelType.AFFILIATE: {"ctr": 1.0, "conversion_rate": 2.0, "cpa": 35.0},
        ChannelType.REFERRAL: {"ctr": 2.5, "conversion_rate": 3.5, "cpa": 20.0},
        ChannelType.DIRECT: {"ctr": 0.0, "conversion_rate": 5.0, "cpa": 0.0},
        ChannelType.VIDEO: {"ctr": 1.2, "conversion_rate": 1.0, "cpa": 45.0},
        ChannelType.CONTENT: {"ctr": 2.0, "conversion_rate": 2.5, "cpa": 25.0},
    }

    RATING_THRESHOLDS = {90: "Excellent", 75: "Good", 60: "Fair", 40: "Poor", 0: "Critical"}

    def __init__(self, target_roas: float = 400.0):
        self.target_roas = target_roas

    def analyze_channel(self, channel: ChannelType, metrics: ChannelMetrics,
                        total_revenue: float = 0) -> ChannelPerformance:
        """Analyze individual channel performance."""
        # Calculate KPIs
        ctr = (metrics.clicks / metrics.impressions * 100) if metrics.impressions > 0 else 0
        conversion_rate = (metrics.conversions / metrics.clicks * 100) if metrics.clicks > 0 else 0
        cpc = metrics.spend / metrics.clicks if metrics.clicks > 0 else 0
        cpa = metrics.spend / metrics.conversions if metrics.conversions > 0 else 0
        roas = (metrics.revenue / metrics.spend * 100) if metrics.spend > 0 else 0
        contribution = (metrics.revenue / total_revenue * 100) if total_revenue > 0 else 0

        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency(channel, ctr, conversion_rate, cpa, roas)
        rating = self._get_rating(efficiency_score)

        # Generate recommendations
        recommendations = self._generate_channel_recommendations(
            channel, ctr, conversion_rate, cpa, roas, efficiency_score
        )

        return ChannelPerformance(
            channel=channel,
            metrics=metrics,
            ctr=ctr,
            conversion_rate=conversion_rate,
            cpc=cpc,
            cpa=cpa,
            roas=roas,
            contribution_percent=contribution,
            efficiency_score=efficiency_score,
            rating=rating,
            recommendations=recommendations
        )

    def analyze_channel_mix(self, channel_data: Dict[ChannelType, ChannelMetrics]) -> ChannelMix:
        """Analyze complete channel mix and optimize budget allocation."""
        total_spend = sum(m.spend for m in channel_data.values())
        total_revenue = sum(m.revenue for m in channel_data.values())
        total_conversions = sum(m.conversions for m in channel_data.values())
        overall_roas = (total_revenue / total_spend * 100) if total_spend > 0 else 0

        # Analyze each channel
        performances = []
        for channel, metrics in channel_data.items():
            perf = self.analyze_channel(channel, metrics, total_revenue)
            performances.append(perf)

        # Sort by efficiency
        performances.sort(key=lambda x: x.efficiency_score, reverse=True)

        # Identify top and bottom performers
        top_performers = [p.channel.value for p in performances[:3] if p.efficiency_score >= 70]
        underperformers = [p.channel.value for p in performances if p.efficiency_score < 50]

        # Generate optimization opportunities
        opportunities = self._identify_opportunities(performances, total_spend)

        # Calculate recommended budget shifts
        budget_shifts = self._calculate_budget_shifts(performances, total_spend)

        return ChannelMix(
            total_spend=total_spend,
            total_revenue=total_revenue,
            total_conversions=total_conversions,
            overall_roas=overall_roas,
            channel_performances=performances,
            top_performers=top_performers,
            underperformers=underperformers,
            optimization_opportunities=opportunities,
            recommended_budget_shifts=budget_shifts
        )

    def _calculate_efficiency(self, channel: ChannelType, ctr: float,
                              conversion_rate: float, cpa: float, roas: float) -> float:
        """Calculate channel efficiency score (0-100)."""
        benchmarks = self.CHANNEL_BENCHMARKS.get(channel, {})
        scores = []

        # CTR score
        if benchmarks.get("ctr", 0) > 0:
            ctr_score = min(100, (ctr / benchmarks["ctr"]) * 100)
            scores.append(ctr_score * 0.2)

        # Conversion rate score
        if benchmarks.get("conversion_rate", 0) > 0:
            conv_score = min(100, (conversion_rate / benchmarks["conversion_rate"]) * 100)
            scores.append(conv_score * 0.3)

        # CPA score (lower is better)
        if benchmarks.get("cpa", 0) > 0 and cpa > 0:
            cpa_score = min(100, (benchmarks["cpa"] / cpa) * 100)
            scores.append(cpa_score * 0.25)

        # ROAS score
        roas_score = min(100, (roas / self.target_roas) * 100)
        scores.append(roas_score * 0.25)

        return sum(scores) if scores else 50

    def _get_rating(self, score: float) -> str:
        for threshold, rating in sorted(self.RATING_THRESHOLDS.items(), reverse=True):
            if score >= threshold:
                return rating
        return "Critical"

    def _generate_channel_recommendations(self, channel: ChannelType, ctr: float,
                                          conversion_rate: float, cpa: float,
                                          roas: float, score: float) -> List[str]:
        """Generate channel-specific recommendations."""
        recommendations = []
        benchmarks = self.CHANNEL_BENCHMARKS.get(channel, {})

        if ctr < benchmarks.get("ctr", 0) * 0.8:
            recommendations.append(f"Improve {channel.value} CTR - test new ad creative and targeting")

        if conversion_rate < benchmarks.get("conversion_rate", 0) * 0.8:
            recommendations.append(f"Optimize {channel.value} landing pages for better conversion")

        if cpa > benchmarks.get("cpa", 0) * 1.2 and benchmarks.get("cpa", 0) > 0:
            recommendations.append(f"Reduce {channel.value} CPA through audience refinement")

        if roas < self.target_roas * 0.8:
            recommendations.append(f"Review {channel.value} targeting and bid strategy")

        if score >= 80:
            recommendations.append(f"Consider increasing {channel.value} budget - strong performer")

        return recommendations[:3]

    def _identify_opportunities(self, performances: List[ChannelPerformance],
                                total_spend: float) -> List[str]:
        """Identify optimization opportunities across channel mix."""
        opportunities = []

        # High efficiency, low spend
        for p in performances:
            spend_share = (p.metrics.spend / total_spend * 100) if total_spend > 0 else 0
            if p.efficiency_score > 75 and spend_share < 15:
                opportunities.append(
                    f"Scale {p.channel.value} - high efficiency ({p.efficiency_score:.0f}) but low budget share ({spend_share:.1f}%)"
                )

        # Low efficiency, high spend
        for p in performances:
            spend_share = (p.metrics.spend / total_spend * 100) if total_spend > 0 else 0
            if p.efficiency_score < 50 and spend_share > 20:
                opportunities.append(
                    f"Reduce {p.channel.value} spend - poor efficiency ({p.efficiency_score:.0f}) with high budget ({spend_share:.1f}%)"
                )

        return opportunities[:5]

    def _calculate_budget_shifts(self, performances: List[ChannelPerformance],
                                 total_spend: float) -> Dict[str, float]:
        """Calculate recommended budget reallocation."""
        shifts = {}

        for p in performances:
            current_share = (p.metrics.spend / total_spend * 100) if total_spend > 0 else 0

            if p.efficiency_score >= 80:
                recommended = min(current_share * 1.3, 40)  # Max 40% to any channel
                shift = recommended - current_share
            elif p.efficiency_score >= 60:
                shift = 0  # Maintain
            elif p.efficiency_score >= 40:
                shift = -current_share * 0.2  # Reduce 20%
            else:
                shift = -current_share * 0.4  # Reduce 40%

            if abs(shift) > 2:  # Only report significant shifts
                shifts[p.channel.value] = shift

        return shifts
