"""ROI Analyzer - Marketing Intelligence"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ROIStatus(Enum):
    HIGHLY_PROFITABLE = "Highly Profitable"
    PROFITABLE = "Profitable"
    BREAK_EVEN = "Break Even"
    UNPROFITABLE = "Unprofitable"
    HIGHLY_UNPROFITABLE = "Highly Unprofitable"


@dataclass
class ChannelROI:
    channel: str
    investment: float
    revenue: float
    roi_percentage: float
    status: ROIStatus
    cost_per_acquisition: float
    customer_lifetime_value: float
    payback_period: float
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {"channel": self.channel, "investment": self.investment, "revenue": self.revenue,
                "roi_percentage": round(self.roi_percentage, 1), "status": self.status.value,
                "cost_per_acquisition": round(self.cost_per_acquisition, 2),
                "customer_lifetime_value": round(self.customer_lifetime_value, 2),
                "payback_period": round(self.payback_period, 1), "recommendations": self.recommendations}


@dataclass
class ROIReport:
    report_id: str
    organization_id: str
    total_investment: float
    total_revenue: float
    overall_roi: float
    overall_status: ROIStatus
    channel_analysis: List[ChannelROI]
    top_performers: List[str]
    underperformers: List[str]
    optimization_opportunities: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {"report_id": self.report_id, "total_investment": self.total_investment,
                "total_revenue": self.total_revenue, "overall_roi": round(self.overall_roi, 1),
                "overall_status": self.overall_status.value, "channel_analysis": [c.to_dict() for c in self.channel_analysis],
                "top_performers": self.top_performers, "underperformers": self.underperformers,
                "recommendations": self.recommendations}


class ROIAnalyzer:
    ROI_THRESHOLDS = {200: ROIStatus.HIGHLY_PROFITABLE, 50: ROIStatus.PROFITABLE, 0: ROIStatus.BREAK_EVEN,
                      -50: ROIStatus.UNPROFITABLE, -100: ROIStatus.HIGHLY_UNPROFITABLE}

    def __init__(self, target_roi: float = 100, target_cpa: float = 50, avg_clv: float = 500):
        self.target_roi = target_roi
        self.target_cpa = target_cpa
        self.avg_clv = avg_clv

    def analyze_channel(self, channel: str, investment: float, revenue: float, conversions: int) -> ChannelROI:
        roi = ((revenue - investment) / investment * 100) if investment > 0 else 0
        status = self._determine_status(roi)
        cpa = investment / conversions if conversions > 0 else investment
        clv = revenue / conversions if conversions > 0 else 0
        payback = investment / (revenue / 12) if revenue > 0 else 99
        recommendations = self._generate_channel_recommendations(channel, roi, cpa, status)
        return ChannelROI(channel, investment, revenue, roi, status, cpa, clv, payback, recommendations)

    def create_report(self, report_id: str, org_id: str, channel_data: List[Dict[str, Any]]) -> ROIReport:
        channel_analysis = [self.analyze_channel(c['channel'], c['investment'], c['revenue'], c.get('conversions', 1))
                           for c in channel_data]
        total_inv = sum(c.investment for c in channel_analysis)
        total_rev = sum(c.revenue for c in channel_analysis)
        overall_roi = ((total_rev - total_inv) / total_inv * 100) if total_inv > 0 else 0
        overall_status = self._determine_status(overall_roi)

        sorted_channels = sorted(channel_analysis, key=lambda x: x.roi_percentage, reverse=True)
        top = [c.channel for c in sorted_channels[:3] if c.roi_percentage > 50]
        under = [c.channel for c in sorted_channels[-3:] if c.roi_percentage < 0]

        opportunities = []
        for c in channel_analysis:
            if c.roi_percentage > 100:
                opportunities.append(f"Scale {c.channel} - high ROI potential")
            elif c.roi_percentage < 0:
                opportunities.append(f"Optimize or reduce {c.channel} spend")

        recommendations = self._generate_report_recommendations(overall_roi, channel_analysis)

        return ROIReport(report_id, org_id, total_inv, total_rev, overall_roi, overall_status,
                        channel_analysis, top, under, opportunities[:5], recommendations)

    def _determine_status(self, roi: float) -> ROIStatus:
        for threshold, status in sorted(self.ROI_THRESHOLDS.items(), reverse=True):
            if roi >= threshold:
                return status
        return ROIStatus.HIGHLY_UNPROFITABLE

    def _generate_channel_recommendations(self, channel: str, roi: float, cpa: float, status: ROIStatus) -> List[str]:
        recs = []
        if status == ROIStatus.HIGHLY_PROFITABLE:
            recs.append(f"Increase {channel} budget allocation")
        elif status in [ROIStatus.UNPROFITABLE, ROIStatus.HIGHLY_UNPROFITABLE]:
            recs.append(f"Review {channel} targeting and creative")
            recs.append(f"Consider reducing {channel} spend")
        if cpa > self.target_cpa:
            recs.append(f"Optimize {channel} to reduce CPA")
        return recs[:3]

    def _generate_report_recommendations(self, overall_roi: float, channels: List[ChannelROI]) -> List[str]:
        recs = []
        if overall_roi < self.target_roi:
            recs.append(f"Overall ROI ({overall_roi:.0f}%) below target ({self.target_roi}%)")
        profitable = [c for c in channels if c.roi_percentage > 100]
        if profitable:
            recs.append(f"Reallocate budget to top performers: {', '.join(c.channel for c in profitable[:2])}")
        unprofitable = [c for c in channels if c.roi_percentage < 0]
        if unprofitable:
            recs.append(f"Reduce spend on underperformers: {', '.join(c.channel for c in unprofitable[:2])}")
        return recs[:5]


def create_marketing_roi_analyzer(target_roi: float = 100) -> ROIAnalyzer:
    return ROIAnalyzer(target_roi=target_roi)
