"""Demo Data Generator for Marketing Intelligence"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid


class MarketingDemoGenerator:
    """Generates realistic demo data for Marketing Intelligence product."""

    CHANNEL_TYPES = [
        'Paid Search', 'Organic Search', 'Social Media', 'Email Marketing',
        'Display Advertising', 'Content Marketing', 'Affiliate', 'Direct',
        'Referral', 'Video Advertising'
    ]

    CAMPAIGN_NAMES = [
        'Q1 Brand Awareness', 'Product Launch 2024', 'Holiday Sale',
        'Summer Promotion', 'Lead Gen Campaign', 'Retargeting Blast',
        'Newsletter Drive', 'Webinar Series', 'Free Trial Push',
        'Enterprise Outreach', 'SMB Acquisition', 'Customer Win-Back'
    ]

    INDUSTRIES = [
        'Technology', 'Healthcare', 'Financial Services', 'Retail',
        'Manufacturing', 'Professional Services', 'Education', 'Media'
    ]

    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)

    def generate_organization(self, name: str = None) -> Dict[str, Any]:
        """Generate a demo organization."""
        name = name or f"Demo Company {random.randint(1000, 9999)}"
        return {
            'id': str(uuid.uuid4()),
            'name': name,
            'industry': random.choice(self.INDUSTRIES),
            'monthly_budget': random.randint(10000, 500000),
            'annual_revenue': random.randint(1000000, 100000000),
            'employee_count': random.randint(10, 1000),
            'created_at': datetime.utcnow().isoformat()
        }

    def generate_channels(self, org_id: str, count: int = 6) -> List[Dict[str, Any]]:
        """Generate marketing channel data."""
        channels = []
        selected_channels = random.sample(self.CHANNEL_TYPES, min(count, len(self.CHANNEL_TYPES)))

        for channel_name in selected_channels:
            # Generate realistic metrics with some variation
            spend = random.randint(5000, 100000)
            roi_multiplier = random.uniform(0.5, 4.0)
            revenue = int(spend * roi_multiplier)

            impressions = random.randint(50000, 5000000)
            clicks = int(impressions * random.uniform(0.01, 0.08))
            conversions = int(clicks * random.uniform(0.02, 0.15))

            channels.append({
                'id': str(uuid.uuid4()),
                'organization_id': org_id,
                'name': channel_name,
                'spend': spend,
                'revenue': revenue,
                'roi': round((revenue - spend) / spend * 100, 1) if spend > 0 else 0,
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'ctr': round(clicks / impressions * 100, 2) if impressions > 0 else 0,
                'conversion_rate': round(conversions / clicks * 100, 2) if clicks > 0 else 0,
                'cpc': round(spend / clicks, 2) if clicks > 0 else 0,
                'cac': round(spend / conversions, 2) if conversions > 0 else 0,
                'status': random.choice(['active', 'active', 'active', 'paused']),
                'period': 'last_30_days'
            })

        return channels

    def generate_campaigns(self, org_id: str, count: int = 8) -> List[Dict[str, Any]]:
        """Generate campaign data."""
        campaigns = []
        selected_names = random.sample(self.CAMPAIGN_NAMES, min(count, len(self.CAMPAIGN_NAMES)))

        for name in selected_names:
            start_date = datetime.utcnow() - timedelta(days=random.randint(7, 90))
            budget = random.randint(5000, 50000)
            spent = int(budget * random.uniform(0.3, 1.1))
            leads = random.randint(50, 500)
            customers = int(leads * random.uniform(0.05, 0.25))

            campaigns.append({
                'id': str(uuid.uuid4()),
                'organization_id': org_id,
                'name': name,
                'channel': random.choice(self.CHANNEL_TYPES[:5]),
                'status': random.choice(['active', 'active', 'completed', 'paused']),
                'budget': budget,
                'spent': spent,
                'budget_utilization': round(spent / budget * 100, 1),
                'leads': leads,
                'customers': customers,
                'conversion_rate': round(customers / leads * 100, 1) if leads > 0 else 0,
                'cpl': round(spent / leads, 2) if leads > 0 else 0,
                'cac': round(spent / customers, 2) if customers > 0 else 0,
                'start_date': start_date.isoformat(),
                'end_date': (start_date + timedelta(days=random.randint(30, 90))).isoformat()
            })

        return campaigns

    def generate_metrics_summary(self, channels: List[Dict], campaigns: List[Dict]) -> Dict[str, Any]:
        """Generate overall marketing metrics summary."""
        total_spend = sum(c['spend'] for c in channels)
        total_revenue = sum(c['revenue'] for c in channels)
        total_conversions = sum(c['conversions'] for c in channels)
        total_impressions = sum(c['impressions'] for c in channels)
        total_clicks = sum(c['clicks'] for c in channels)

        # Calculate health score based on metrics
        roas = total_revenue / total_spend if total_spend > 0 else 0
        avg_ctr = total_clicks / total_impressions * 100 if total_impressions > 0 else 0
        avg_conv_rate = total_conversions / total_clicks * 100 if total_clicks > 0 else 0

        # Weighted health score
        health_score = min(100, int(
            (min(roas / 3, 1) * 40) +  # ROAS contributes 40%
            (min(avg_ctr / 5, 1) * 25) +  # CTR contributes 25%
            (min(avg_conv_rate / 5, 1) * 35)  # Conversion rate contributes 35%
        ))

        return {
            'total_spend': total_spend,
            'total_revenue': total_revenue,
            'total_profit': total_revenue - total_spend,
            'roas': round(roas, 2),
            'roi_percentage': round((total_revenue - total_spend) / total_spend * 100, 1) if total_spend > 0 else 0,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'avg_ctr': round(avg_ctr, 2),
            'avg_conversion_rate': round(avg_conv_rate, 2),
            'avg_cac': round(total_spend / total_conversions, 2) if total_conversions > 0 else 0,
            'active_campaigns': len([c for c in campaigns if c['status'] == 'active']),
            'total_campaigns': len(campaigns),
            'active_channels': len([c for c in channels if c['status'] == 'active']),
            'health_score': health_score,
            'period': 'last_30_days',
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Generate daily trend data."""
        trends = []
        base_spend = random.randint(500, 2000)
        base_revenue = base_spend * random.uniform(1.5, 3.0)

        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days - i - 1)
            daily_spend = int(base_spend * random.uniform(0.7, 1.3))
            daily_revenue = int(base_revenue * random.uniform(0.6, 1.4))

            trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'spend': daily_spend,
                'revenue': daily_revenue,
                'impressions': random.randint(5000, 50000),
                'clicks': random.randint(100, 2000),
                'conversions': random.randint(5, 100)
            })

        return trends

    def generate_full_demo(self, org_name: str = None) -> Dict[str, Any]:
        """Generate complete demo dataset."""
        org = self.generate_organization(org_name)
        channels = self.generate_channels(org['id'])
        campaigns = self.generate_campaigns(org['id'])
        metrics = self.generate_metrics_summary(channels, campaigns)
        trends = self.generate_trends()

        return {
            'organization': org,
            'channels': channels,
            'campaigns': campaigns,
            'metrics_summary': metrics,
            'trends': trends,
            'context_for_ai': self._build_ai_context(metrics, channels, campaigns)
        }

    def _build_ai_context(
        self,
        metrics: Dict[str, Any],
        channels: List[Dict],
        campaigns: List[Dict]
    ) -> Dict[str, Any]:
        """Build context dictionary for AI suggestion engine."""
        # Find best and worst performing channels
        sorted_channels = sorted(channels, key=lambda x: x['roi'], reverse=True)
        best_channel = sorted_channels[0] if sorted_channels else None
        worst_channel = sorted_channels[-1] if sorted_channels else None

        # Identify underperforming channels (ROI < 50%)
        underperforming = [c for c in channels if c['roi'] < 50]

        return {
            'roas': metrics['roas'],
            'roi_percentage': metrics['roi_percentage'],
            'avg_cac': metrics['avg_cac'],
            'health_score': metrics['health_score'],
            'total_spend': metrics['total_spend'],
            'best_channel': best_channel['name'] if best_channel else None,
            'best_channel_roi': best_channel['roi'] if best_channel else 0,
            'worst_channel': worst_channel['name'] if worst_channel else None,
            'worst_channel_roi': worst_channel['roi'] if worst_channel else 0,
            'underperforming_channels': [c['name'] for c in underperforming],
            'active_campaigns': metrics['active_campaigns'],
            'campaigns_over_budget': len([c for c in campaigns if c['budget_utilization'] > 100])
        }


def create_marketing_demo_generator(seed: int = None) -> MarketingDemoGenerator:
    """Factory function to create demo generator."""
    return MarketingDemoGenerator(seed)
