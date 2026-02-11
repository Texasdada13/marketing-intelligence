"""
Integration Manager for Marketing Intelligence

Provides a unified interface for managing marketing data integrations.
Supports Google Analytics 4, with extensibility for additional platforms.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .google_analytics_client import (
    GoogleAnalyticsClient, GoogleAnalyticsConfig, GoogleToken,
    GoogleAnalyticsDemoClient, TrafficSummary, AcquisitionData
)

logger = logging.getLogger(__name__)


class IntegrationType(Enum):
    GOOGLE_ANALYTICS = "google_analytics"
    GOOGLE_ADS = "google_ads"  # Future
    FACEBOOK_ADS = "facebook_ads"  # Future
    LINKEDIN_ADS = "linkedin_ads"  # Future
    DEMO = "demo"


@dataclass
class IntegrationStatus:
    """Status of an integration connection"""
    integration_type: IntegrationType
    is_connected: bool
    last_sync: Optional[datetime] = None
    account_name: Optional[str] = None
    property_id: Optional[str] = None
    error_message: Optional[str] = None


class MarketingIntegrationManager:
    """
    Manages marketing data integrations for Marketing Intelligence.

    Provides a unified interface for:
    - OAuth authentication flows
    - Data fetching from multiple sources
    - Normalized data formats
    - Token storage and refresh
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'instance', 'integrations'
        )
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

        self._ga_client: Optional[GoogleAnalyticsClient] = None
        self._demo_mode = False

    # ========== Configuration ==========

    def configure_google_analytics(self, config: Optional[GoogleAnalyticsConfig] = None):
        """Configure Google Analytics integration"""
        config = config or GoogleAnalyticsConfig.from_env()
        self._ga_client = GoogleAnalyticsClient(config)
        self._load_stored_token(IntegrationType.GOOGLE_ANALYTICS)

    def enable_demo_mode(self):
        """Enable demo mode with mock data"""
        self._demo_mode = True
        self._ga_client = GoogleAnalyticsDemoClient()

    # ========== OAuth Authentication ==========

    def get_auth_url(self, integration_type: IntegrationType, state: str = "") -> str:
        """Get OAuth authorization URL for an integration"""
        if integration_type == IntegrationType.GOOGLE_ANALYTICS:
            if not self._ga_client:
                self.configure_google_analytics()
            return self._ga_client.get_authorization_url(state)
        else:
            raise ValueError(f"Unsupported integration type: {integration_type}")

    def handle_oauth_callback(self, integration_type: IntegrationType,
                               authorization_code: str) -> bool:
        """Handle OAuth callback and exchange code for tokens"""
        try:
            if integration_type == IntegrationType.GOOGLE_ANALYTICS:
                if not self._ga_client:
                    self.configure_google_analytics()
                token = self._ga_client.exchange_code_for_token(authorization_code)
                self._store_token(IntegrationType.GOOGLE_ANALYTICS, token.to_dict())
                return True

        except Exception as e:
            logger.error(f"OAuth callback failed for {integration_type}: {e}")
            return False

        return False

    def set_property_id(self, property_id: str):
        """Set the GA4 property ID"""
        if self._ga_client:
            self._ga_client.set_property_id(property_id)
            # Store property ID
            config_path = os.path.join(self.storage_path, 'ga_config.json')
            with open(config_path, 'w') as f:
                json.dump({'property_id': property_id}, f)

    def disconnect(self, integration_type: IntegrationType):
        """Disconnect an integration and remove stored tokens"""
        token_file = self._get_token_path(integration_type)
        if os.path.exists(token_file):
            os.remove(token_file)

        if integration_type == IntegrationType.GOOGLE_ANALYTICS:
            self._ga_client = None

    # ========== Status ==========

    def get_status(self, integration_type: IntegrationType) -> IntegrationStatus:
        """Get the status of an integration"""
        is_connected = False
        property_id = None
        error_message = None

        try:
            if integration_type == IntegrationType.GOOGLE_ANALYTICS and self._ga_client:
                if self._ga_client.token:
                    is_connected = True
                    property_id = self._ga_client.config.property_id

            elif integration_type == IntegrationType.DEMO:
                is_connected = self._demo_mode

        except Exception as e:
            error_message = str(e)

        return IntegrationStatus(
            integration_type=integration_type,
            is_connected=is_connected,
            property_id=property_id,
            error_message=error_message
        )

    def get_all_statuses(self) -> List[IntegrationStatus]:
        """Get status for all configured integrations"""
        statuses = []

        if self._ga_client:
            statuses.append(self.get_status(IntegrationType.GOOGLE_ANALYTICS))
        if self._demo_mode:
            statuses.append(self.get_status(IntegrationType.DEMO))

        return statuses

    # ========== Data Access ==========

    def get_traffic_summary(self, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get traffic summary from Google Analytics"""
        if not self._ga_client or not self._ga_client.token:
            return None

        try:
            summary = self._ga_client.get_traffic_summary(
                start_date=f"{days}daysAgo",
                end_date="today"
            )
            return {
                'total_users': summary.total_users,
                'new_users': summary.new_users,
                'returning_users': summary.returning_users,
                'sessions': summary.sessions,
                'pageviews': summary.pageviews,
                'avg_session_duration': summary.avg_session_duration,
                'bounce_rate': summary.bounce_rate,
                'pages_per_session': summary.pages_per_session,
                'date_range': summary.date_range
            }
        except Exception as e:
            logger.error(f"Error fetching traffic summary: {e}")
            return None

    def get_acquisition_data(self, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get acquisition breakdown from Google Analytics"""
        if not self._ga_client or not self._ga_client.token:
            return None

        try:
            data = self._ga_client.get_acquisition_data(
                start_date=f"{days}daysAgo",
                end_date="today"
            )
            return {
                'by_source': data.by_source,
                'by_medium': data.by_medium,
                'by_campaign': data.by_campaign,
                'date_range': data.date_range
            }
        except Exception as e:
            logger.error(f"Error fetching acquisition data: {e}")
            return None

    def get_top_pages(self, days: int = 30, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """Get top pages from Google Analytics"""
        if not self._ga_client or not self._ga_client.token:
            return None

        try:
            return self._ga_client.get_top_pages(
                start_date=f"{days}daysAgo",
                end_date="today",
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error fetching top pages: {e}")
            return None

    def get_traffic_by_date(self, days: int = 30) -> Optional[List[Dict[str, Any]]]:
        """Get daily traffic trend"""
        if not self._ga_client or not self._ga_client.token:
            return None

        try:
            return self._ga_client.get_traffic_by_date(
                start_date=f"{days}daysAgo",
                end_date="today"
            )
        except Exception as e:
            logger.error(f"Error fetching daily traffic: {e}")
            return None

    def get_device_breakdown(self, days: int = 30) -> Optional[List[Dict[str, Any]]]:
        """Get traffic by device category"""
        if not self._ga_client or not self._ga_client.token:
            return None

        try:
            return self._ga_client.get_traffic_by_device(
                start_date=f"{days}daysAgo",
                end_date="today"
            )
        except Exception as e:
            logger.error(f"Error fetching device breakdown: {e}")
            return None

    def get_geo_breakdown(self, days: int = 30, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """Get traffic by location"""
        if not self._ga_client or not self._ga_client.token:
            return None

        try:
            return self._ga_client.get_traffic_by_location(
                start_date=f"{days}daysAgo",
                end_date="today",
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error fetching geo breakdown: {e}")
            return None

    def get_marketing_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive marketing analytics summary"""
        if not self._ga_client or not self._ga_client.token:
            return {'error': 'Not connected to Google Analytics'}

        try:
            return self._ga_client.get_marketing_summary(days=days)
        except Exception as e:
            logger.error(f"Error fetching marketing summary: {e}")
            return {'error': str(e)}

    # ========== Token Storage ==========

    def _get_token_path(self, integration_type: IntegrationType) -> str:
        """Get the file path for storing tokens"""
        return os.path.join(self.storage_path, f'{integration_type.value}_token.json')

    def _store_token(self, integration_type: IntegrationType, token_data: Dict[str, Any]):
        """Store OAuth token to file"""
        token_path = self._get_token_path(integration_type)
        with open(token_path, 'w') as f:
            json.dump(token_data, f)

    def _load_stored_token(self, integration_type: IntegrationType):
        """Load stored OAuth token from file"""
        token_path = self._get_token_path(integration_type)

        if not os.path.exists(token_path):
            return

        try:
            with open(token_path, 'r') as f:
                token_data = json.load(f)

            if integration_type == IntegrationType.GOOGLE_ANALYTICS and self._ga_client:
                self._ga_client.set_token(GoogleToken.from_dict(token_data))

            # Also load property ID if stored
            config_path = os.path.join(self.storage_path, 'ga_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    if 'property_id' in config_data and self._ga_client:
                        self._ga_client.set_property_id(config_data['property_id'])

        except Exception as e:
            logger.error(f"Failed to load stored token for {integration_type}: {e}")


# Factory function for easy creation
def create_marketing_integration_manager(demo_mode: bool = False) -> MarketingIntegrationManager:
    """Create a MarketingIntegrationManager with appropriate configuration"""
    manager = MarketingIntegrationManager()

    if demo_mode:
        manager.enable_demo_mode()
    else:
        # Configure from environment variables if available
        if os.getenv('GOOGLE_CLIENT_ID'):
            manager.configure_google_analytics()

    return manager
