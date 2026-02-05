"""Content Performance Analysis"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class ContentType(Enum):
    BLOG_POST = "Blog Post"
    VIDEO = "Video"
    PODCAST = "Podcast"
    INFOGRAPHIC = "Infographic"
    EBOOK = "eBook"
    WHITEPAPER = "Whitepaper"
    CASE_STUDY = "Case Study"
    WEBINAR = "Webinar"
    SOCIAL_POST = "Social Post"
    EMAIL = "Email"
    LANDING_PAGE = "Landing Page"


class ContentStage(Enum):
    TOFU = "Top of Funnel"
    MOFU = "Middle of Funnel"
    BOFU = "Bottom of Funnel"


@dataclass
class ContentMetrics:
    views: int = 0
    unique_visitors: int = 0
    time_on_page: float = 0.0  # seconds
    bounce_rate: float = 0.0
    shares: int = 0
    comments: int = 0
    downloads: int = 0
    leads_generated: int = 0
    conversions: int = 0


@dataclass
class ContentPerformance:
    content_id: str
    title: str
    content_type: ContentType
    stage: ContentStage
    metrics: ContentMetrics
    engagement_score: float
    conversion_score: float
    overall_score: float
    rating: str
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_id": self.content_id,
            "title": self.title,
            "content_type": self.content_type.value,
            "stage": self.stage.value,
            "metrics": {
                "views": self.metrics.views,
                "unique_visitors": self.metrics.unique_visitors,
                "time_on_page": round(self.metrics.time_on_page, 1),
                "bounce_rate": round(self.metrics.bounce_rate, 1),
                "shares": self.metrics.shares,
                "leads_generated": self.metrics.leads_generated,
                "conversions": self.metrics.conversions
            },
            "engagement_score": round(self.engagement_score, 1),
            "conversion_score": round(self.conversion_score, 1),
            "overall_score": round(self.overall_score, 1),
            "rating": self.rating,
            "recommendations": self.recommendations
        }


@dataclass
class ContentAnalysisReport:
    total_content_pieces: int
    total_views: int
    total_leads: int
    total_conversions: int
    avg_engagement_score: float
    top_performers: List[ContentPerformance]
    underperformers: List[ContentPerformance]
    content_by_type: Dict[str, int]
    content_by_stage: Dict[str, int]
    content_gaps: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_content_pieces": self.total_content_pieces,
            "total_views": self.total_views,
            "total_leads": self.total_leads,
            "total_conversions": self.total_conversions,
            "avg_engagement_score": round(self.avg_engagement_score, 1),
            "top_performers": [p.to_dict() for p in self.top_performers],
            "underperformers": [p.to_dict() for p in self.underperformers],
            "content_by_type": self.content_by_type,
            "content_by_stage": self.content_by_stage,
            "content_gaps": self.content_gaps,
            "recommendations": self.recommendations
        }


class ContentAnalyzer:
    """Analyzes content marketing performance."""

    # Benchmarks by content type
    TYPE_BENCHMARKS = {
        ContentType.BLOG_POST: {"time_on_page": 180, "bounce_rate": 60, "engagement_rate": 2},
        ContentType.VIDEO: {"time_on_page": 120, "bounce_rate": 45, "engagement_rate": 4},
        ContentType.PODCAST: {"time_on_page": 900, "bounce_rate": 30, "engagement_rate": 3},
        ContentType.INFOGRAPHIC: {"time_on_page": 60, "bounce_rate": 50, "engagement_rate": 5},
        ContentType.EBOOK: {"time_on_page": 300, "bounce_rate": 40, "engagement_rate": 8},
        ContentType.WHITEPAPER: {"time_on_page": 360, "bounce_rate": 35, "engagement_rate": 10},
        ContentType.CASE_STUDY: {"time_on_page": 240, "bounce_rate": 40, "engagement_rate": 6},
        ContentType.WEBINAR: {"time_on_page": 2400, "bounce_rate": 25, "engagement_rate": 12},
        ContentType.SOCIAL_POST: {"time_on_page": 15, "bounce_rate": 70, "engagement_rate": 3},
        ContentType.EMAIL: {"time_on_page": 30, "bounce_rate": 0, "engagement_rate": 3},
        ContentType.LANDING_PAGE: {"time_on_page": 90, "bounce_rate": 50, "engagement_rate": 5},
    }

    RATING_THRESHOLDS = {90: "Excellent", 75: "Good", 60: "Fair", 40: "Poor", 0: "Critical"}

    def analyze_content(self, content_id: str, title: str, content_type: ContentType,
                        stage: ContentStage, metrics: ContentMetrics) -> ContentPerformance:
        """Analyze individual content piece performance."""
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(content_type, metrics)

        # Calculate conversion score
        conversion_score = self._calculate_conversion_score(content_type, stage, metrics)

        # Overall weighted score
        if stage == ContentStage.TOFU:
            overall_score = engagement_score * 0.7 + conversion_score * 0.3
        elif stage == ContentStage.MOFU:
            overall_score = engagement_score * 0.5 + conversion_score * 0.5
        else:  # BOFU
            overall_score = engagement_score * 0.3 + conversion_score * 0.7

        rating = self._get_rating(overall_score)
        recommendations = self._generate_content_recommendations(
            content_type, stage, metrics, engagement_score, conversion_score
        )

        return ContentPerformance(
            content_id=content_id,
            title=title,
            content_type=content_type,
            stage=stage,
            metrics=metrics,
            engagement_score=engagement_score,
            conversion_score=conversion_score,
            overall_score=overall_score,
            rating=rating,
            recommendations=recommendations
        )

    def analyze_content_library(self, content_list: List[Dict[str, Any]]) -> ContentAnalysisReport:
        """Analyze complete content library."""
        performances = []

        for content in content_list:
            metrics = ContentMetrics(**content.get("metrics", {}))
            perf = self.analyze_content(
                content_id=content.get("id", ""),
                title=content.get("title", ""),
                content_type=ContentType(content.get("type", ContentType.BLOG_POST.value)),
                stage=ContentStage(content.get("stage", ContentStage.TOFU.value)),
                metrics=metrics
            )
            performances.append(perf)

        # Aggregate metrics
        total_views = sum(p.metrics.views for p in performances)
        total_leads = sum(p.metrics.leads_generated for p in performances)
        total_conversions = sum(p.metrics.conversions for p in performances)
        avg_engagement = sum(p.engagement_score for p in performances) / len(performances) if performances else 0

        # Sort by performance
        sorted_perf = sorted(performances, key=lambda x: x.overall_score, reverse=True)
        top_performers = [p for p in sorted_perf[:5] if p.overall_score >= 70]
        underperformers = [p for p in sorted_perf if p.overall_score < 50][-5:]

        # Content distribution
        by_type = {}
        for p in performances:
            key = p.content_type.value
            by_type[key] = by_type.get(key, 0) + 1

        by_stage = {}
        for p in performances:
            key = p.stage.value
            by_stage[key] = by_stage.get(key, 0) + 1

        # Identify gaps
        gaps = self._identify_content_gaps(by_type, by_stage, performances)

        # Generate recommendations
        recommendations = self._generate_library_recommendations(
            performances, by_type, by_stage, total_leads, total_conversions
        )

        return ContentAnalysisReport(
            total_content_pieces=len(performances),
            total_views=total_views,
            total_leads=total_leads,
            total_conversions=total_conversions,
            avg_engagement_score=avg_engagement,
            top_performers=top_performers,
            underperformers=underperformers,
            content_by_type=by_type,
            content_by_stage=by_stage,
            content_gaps=gaps,
            recommendations=recommendations
        )

    def _calculate_engagement_score(self, content_type: ContentType,
                                    metrics: ContentMetrics) -> float:
        """Calculate content engagement score (0-100)."""
        benchmarks = self.TYPE_BENCHMARKS.get(content_type, {})
        scores = []

        # Time on page score
        expected_time = benchmarks.get("time_on_page", 120)
        time_score = min(100, (metrics.time_on_page / expected_time) * 100)
        scores.append(time_score * 0.3)

        # Bounce rate score (lower is better)
        expected_bounce = benchmarks.get("bounce_rate", 50)
        if expected_bounce > 0:
            bounce_score = min(100, (expected_bounce / max(metrics.bounce_rate, 1)) * 100)
            scores.append(bounce_score * 0.3)

        # Share/comment engagement
        if metrics.views > 0:
            engagement_rate = ((metrics.shares + metrics.comments) / metrics.views) * 100
            expected_engagement = benchmarks.get("engagement_rate", 2)
            eng_score = min(100, (engagement_rate / expected_engagement) * 100)
            scores.append(eng_score * 0.4)

        return sum(scores) if scores else 50

    def _calculate_conversion_score(self, content_type: ContentType,
                                    stage: ContentStage, metrics: ContentMetrics) -> float:
        """Calculate content conversion score (0-100)."""
        if metrics.unique_visitors == 0:
            return 0

        # Lead generation rate
        lead_rate = (metrics.leads_generated / metrics.unique_visitors) * 100

        # Conversion rate
        conv_rate = (metrics.conversions / metrics.unique_visitors) * 100

        # Expected rates by stage
        expected_leads = {
            ContentStage.TOFU: 2,
            ContentStage.MOFU: 5,
            ContentStage.BOFU: 10
        }
        expected_conv = {
            ContentStage.TOFU: 0.5,
            ContentStage.MOFU: 2,
            ContentStage.BOFU: 5
        }

        lead_score = min(100, (lead_rate / expected_leads.get(stage, 5)) * 100)
        conv_score = min(100, (conv_rate / expected_conv.get(stage, 2)) * 100)

        return lead_score * 0.4 + conv_score * 0.6

    def _get_rating(self, score: float) -> str:
        for threshold, rating in sorted(self.RATING_THRESHOLDS.items(), reverse=True):
            if score >= threshold:
                return rating
        return "Critical"

    def _generate_content_recommendations(self, content_type: ContentType,
                                          stage: ContentStage, metrics: ContentMetrics,
                                          engagement: float, conversion: float) -> List[str]:
        """Generate content-specific recommendations."""
        recommendations = []
        benchmarks = self.TYPE_BENCHMARKS.get(content_type, {})

        if metrics.time_on_page < benchmarks.get("time_on_page", 120) * 0.7:
            recommendations.append("Improve content depth and engagement to increase time on page")

        if metrics.bounce_rate > benchmarks.get("bounce_rate", 50) * 1.3:
            recommendations.append("Add internal links and CTAs to reduce bounce rate")

        if engagement < 50:
            recommendations.append("Promote content more actively on social channels")

        if conversion < 40 and stage != ContentStage.TOFU:
            recommendations.append("Add stronger calls-to-action and lead capture forms")

        if metrics.leads_generated == 0 and metrics.views > 100:
            recommendations.append("Add lead magnets or gated content upgrades")

        return recommendations[:3]

    def _identify_content_gaps(self, by_type: Dict[str, int], by_stage: Dict[str, int],
                               performances: List[ContentPerformance]) -> List[str]:
        """Identify gaps in content strategy."""
        gaps = []

        # Check funnel balance
        tofu_count = by_stage.get(ContentStage.TOFU.value, 0)
        mofu_count = by_stage.get(ContentStage.MOFU.value, 0)
        bofu_count = by_stage.get(ContentStage.BOFU.value, 0)
        total = tofu_count + mofu_count + bofu_count

        if total > 0:
            if mofu_count / total < 0.2:
                gaps.append("Need more middle-of-funnel content for lead nurturing")
            if bofu_count / total < 0.1:
                gaps.append("Need more bottom-of-funnel content for conversions")

        # Check content type variety
        high_value_types = [ContentType.CASE_STUDY, ContentType.WHITEPAPER, ContentType.WEBINAR]
        for ct in high_value_types:
            if by_type.get(ct.value, 0) == 0:
                gaps.append(f"No {ct.value} content - high-value format for lead generation")

        return gaps[:5]

    def _generate_library_recommendations(self, performances: List[ContentPerformance],
                                          by_type: Dict[str, int], by_stage: Dict[str, int],
                                          leads: int, conversions: int) -> List[str]:
        """Generate content library recommendations."""
        recommendations = []

        # Repurpose top performers
        top = [p for p in performances if p.overall_score >= 80]
        if top:
            recommendations.append(
                f"Repurpose top-performing content: {top[0].title} into other formats"
            )

        # Update or retire underperformers
        poor = [p for p in performances if p.overall_score < 40]
        if poor:
            recommendations.append(
                f"Update or retire {len(poor)} underperforming content pieces"
            )

        # Lead generation focus
        if leads == 0:
            recommendations.append("Add lead capture mechanisms to existing content")

        # Content frequency
        if len(performances) < 20:
            recommendations.append("Increase content production frequency")

        return recommendations[:5]
