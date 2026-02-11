"""
External Data Integrations for Marketing Intelligence

Provides connections to:
- Google Analytics 4 (GA4)
- Google Ads
- Social Media APIs (future)
"""

from .google_analytics_client import GoogleAnalyticsClient, GoogleAnalyticsConfig
from .integration_manager import MarketingIntegrationManager, IntegrationType

__all__ = [
    'GoogleAnalyticsClient',
    'GoogleAnalyticsConfig',
    'MarketingIntegrationManager',
    'IntegrationType'
]
