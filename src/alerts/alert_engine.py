"""Alert engine for Marketing Intelligence - monitors marketing metrics and generates alerts."""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertCategory(Enum):
    ROI = "roi"
    SPEND = "spend"
    PERFORMANCE = "performance"
    CAMPAIGN = "campaign"
    CHANNEL = "channel"


@dataclass
class Alert:
    """Represents a marketing alert."""
    id: str
    severity: AlertSeverity
    category: AlertCategory
    title: str
    message: str
    metric_name: str
    current_value: Any
    threshold_value: Any
    recommendation: str
    created_at: datetime

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'severity': self.severity.value,
            'category': self.category.value,
            'title': self.title,
            'message': self.message,
            'metric_name': self.metric_name,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'recommendation': self.recommendation,
            'created_at': self.created_at.isoformat()
        }


class AlertEngine:
    """Engine for generating marketing alerts based on thresholds."""

    # Default thresholds
    THRESHOLDS = {
        'roas_critical': 1.0,      # ROAS below 1.0 is losing money
        'roas_warning': 2.0,       # ROAS below 2.0 needs attention
        'roi_critical': 0,         # Negative ROI is critical
        'roi_warning': 50,         # ROI below 50% needs attention
        'spend_utilization_low': 50,   # Below 50% spend utilization
        'spend_utilization_high': 95,  # Above 95% may need more budget
        'conversion_rate_low': 1.0,    # Below 1% conversion rate
        'cpa_high_multiplier': 2.0,    # CPA 2x above target
    }

    def __init__(self, custom_thresholds: Optional[Dict] = None):
        self.thresholds = {**self.THRESHOLDS}
        if custom_thresholds:
            self.thresholds.update(custom_thresholds)
        self._alert_counter = 0

    def _generate_id(self) -> str:
        self._alert_counter += 1
        return f"mkt-alert-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._alert_counter}"

    def check_metrics(self, data: Dict[str, Any]) -> List[Alert]:
        """Check all metrics and generate alerts."""
        alerts = []

        metrics = data.get('metrics', {})
        channels = data.get('channels', [])
        campaigns = data.get('campaigns', [])

        # Check ROAS
        roas = metrics.get('roas', 0)
        if roas > 0:
            if roas < self.thresholds['roas_critical']:
                alerts.append(Alert(
                    id=self._generate_id(),
                    severity=AlertSeverity.CRITICAL,
                    category=AlertCategory.ROI,
                    title="Critical: ROAS Below Break-Even",
                    message=f"Your ROAS is {roas:.2f}x, which means you're losing money on marketing spend.",
                    metric_name="ROAS",
                    current_value=roas,
                    threshold_value=self.thresholds['roas_critical'],
                    recommendation="Immediately pause underperforming campaigns and reallocate budget to high-performing channels.",
                    created_at=datetime.now()
                ))
            elif roas < self.thresholds['roas_warning']:
                alerts.append(Alert(
                    id=self._generate_id(),
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.ROI,
                    title="Warning: ROAS Needs Improvement",
                    message=f"Your ROAS is {roas:.2f}x, below the recommended {self.thresholds['roas_warning']}x target.",
                    metric_name="ROAS",
                    current_value=roas,
                    threshold_value=self.thresholds['roas_warning'],
                    recommendation="Review campaign targeting and creative assets. Consider A/B testing to improve conversion rates.",
                    created_at=datetime.now()
                ))

        # Check individual channel performance
        for channel in channels:
            channel_roi = channel.get('roi', 0)
            channel_name = channel.get('name', 'Unknown')

            if channel_roi < self.thresholds['roi_critical']:
                alerts.append(Alert(
                    id=self._generate_id(),
                    severity=AlertSeverity.CRITICAL,
                    category=AlertCategory.CHANNEL,
                    title=f"Critical: {channel_name} Has Negative ROI",
                    message=f"{channel_name} is showing {channel_roi:.1f}% ROI - you're losing money on this channel.",
                    metric_name=f"{channel_name} ROI",
                    current_value=channel_roi,
                    threshold_value=0,
                    recommendation=f"Pause {channel_name} campaigns immediately and investigate targeting, creative, and landing pages.",
                    created_at=datetime.now()
                ))
            elif channel_roi < self.thresholds['roi_warning']:
                alerts.append(Alert(
                    id=self._generate_id(),
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.CHANNEL,
                    title=f"Warning: {channel_name} Underperforming",
                    message=f"{channel_name} ROI is {channel_roi:.1f}%, below the {self.thresholds['roi_warning']}% target.",
                    metric_name=f"{channel_name} ROI",
                    current_value=channel_roi,
                    threshold_value=self.thresholds['roi_warning'],
                    recommendation=f"Optimize {channel_name} targeting and bid strategies. Consider reducing budget if performance doesn't improve.",
                    created_at=datetime.now()
                ))

        # Check campaign budget utilization
        for campaign in campaigns:
            budget = campaign.get('budget', 0)
            spent = campaign.get('spent', 0)
            name = campaign.get('name', 'Unknown')
            status = campaign.get('status', '')

            if budget > 0 and status == 'active':
                utilization = (spent / budget) * 100

                if utilization > self.thresholds['spend_utilization_high']:
                    alerts.append(Alert(
                        id=self._generate_id(),
                        severity=AlertSeverity.WARNING,
                        category=AlertCategory.SPEND,
                        title=f"Budget Nearly Exhausted: {name}",
                        message=f"Campaign '{name}' has used {utilization:.1f}% of its budget.",
                        metric_name="Budget Utilization",
                        current_value=utilization,
                        threshold_value=self.thresholds['spend_utilization_high'],
                        recommendation="Review campaign performance. If performing well, consider increasing budget to capture more conversions.",
                        created_at=datetime.now()
                    ))
                elif utilization < self.thresholds['spend_utilization_low']:
                    alerts.append(Alert(
                        id=self._generate_id(),
                        severity=AlertSeverity.INFO,
                        category=AlertCategory.SPEND,
                        title=f"Low Budget Utilization: {name}",
                        message=f"Campaign '{name}' has only used {utilization:.1f}% of its budget.",
                        metric_name="Budget Utilization",
                        current_value=utilization,
                        threshold_value=self.thresholds['spend_utilization_low'],
                        recommendation="Check if targeting is too narrow or bids are too low. Consider broadening audience or increasing bids.",
                        created_at=datetime.now()
                    ))

        # Sort by severity (critical first)
        severity_order = {AlertSeverity.CRITICAL: 0, AlertSeverity.WARNING: 1, AlertSeverity.INFO: 2}
        alerts.sort(key=lambda a: severity_order[a.severity])

        return alerts

    def get_alert_summary(self, alerts: List[Alert]) -> Dict:
        """Get a summary of alerts by severity."""
        summary = {
            'total': len(alerts),
            'critical': sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL),
            'warning': sum(1 for a in alerts if a.severity == AlertSeverity.WARNING),
            'info': sum(1 for a in alerts if a.severity == AlertSeverity.INFO),
            'categories': {}
        }

        for alert in alerts:
            cat = alert.category.value
            if cat not in summary['categories']:
                summary['categories'][cat] = 0
            summary['categories'][cat] += 1

        return summary


def create_alert_engine(custom_thresholds: Optional[Dict] = None) -> AlertEngine:
    """Factory function to create an alert engine."""
    return AlertEngine(custom_thresholds)
