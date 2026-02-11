"""
Google Analytics 4 (GA4) Integration Client

Provides OAuth2 authentication and data fetching for:
- Website traffic and engagement metrics
- User acquisition and behavior
- Conversion tracking
- Real-time analytics
- Custom reports
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import requests
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


@dataclass
class GoogleAnalyticsConfig:
    """Configuration for Google Analytics API access"""
    client_id: str
    client_secret: str
    redirect_uri: str
    property_id: str = ""  # GA4 Property ID (format: properties/XXXXXXXX)

    @property
    def auth_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def token_url(self) -> str:
        return "https://oauth2.googleapis.com/token"

    @property
    def api_base_url(self) -> str:
        return "https://analyticsdata.googleapis.com/v1beta"

    @classmethod
    def from_env(cls) -> 'GoogleAnalyticsConfig':
        """Create config from environment variables"""
        return cls(
            client_id=os.getenv('GOOGLE_CLIENT_ID', ''),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET', ''),
            redirect_uri=os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5104/integrations/google/callback'),
            property_id=os.getenv('GA4_PROPERTY_ID', '')
        )


@dataclass
class GoogleToken:
    """OAuth token storage"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    created_at: datetime = field(default_factory=datetime.utcnow)
    scope: str = ""

    @property
    def is_expired(self) -> bool:
        expiry = self.created_at + timedelta(seconds=self.expires_in - 60)
        return datetime.utcnow() >= expiry

    def to_dict(self) -> Dict[str, Any]:
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type,
            'expires_in': self.expires_in,
            'created_at': self.created_at.isoformat(),
            'scope': self.scope
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoogleToken':
        return cls(
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            token_type=data.get('token_type', 'Bearer'),
            expires_in=data.get('expires_in', 3600),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.utcnow(),
            scope=data.get('scope', '')
        )


class MetricType(Enum):
    """Common GA4 metrics"""
    ACTIVE_USERS = "activeUsers"
    NEW_USERS = "newUsers"
    TOTAL_USERS = "totalUsers"
    SESSIONS = "sessions"
    ENGAGED_SESSIONS = "engagedSessions"
    BOUNCE_RATE = "bounceRate"
    AVERAGE_SESSION_DURATION = "averageSessionDuration"
    SCREEN_PAGE_VIEWS = "screenPageViews"
    CONVERSIONS = "conversions"
    TOTAL_REVENUE = "totalRevenue"
    ECOMMERCE_PURCHASES = "ecommercePurchases"
    EVENT_COUNT = "eventCount"


class DimensionType(Enum):
    """Common GA4 dimensions"""
    DATE = "date"
    COUNTRY = "country"
    CITY = "city"
    DEVICE_CATEGORY = "deviceCategory"
    BROWSER = "browser"
    OPERATING_SYSTEM = "operatingSystem"
    SESSION_SOURCE = "sessionSource"
    SESSION_MEDIUM = "sessionMedium"
    SESSION_CAMPAIGN = "sessionCampaignName"
    PAGE_PATH = "pagePath"
    PAGE_TITLE = "pageTitle"
    LANDING_PAGE = "landingPage"
    EVENT_NAME = "eventName"


@dataclass
class AnalyticsReport:
    """Analytics report result"""
    dimensions: List[str]
    metrics: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    date_range: Tuple[str, str]
    totals: Dict[str, float] = field(default_factory=dict)


@dataclass
class TrafficSummary:
    """Traffic summary for a date range"""
    total_users: int
    new_users: int
    returning_users: int
    sessions: int
    pageviews: int
    avg_session_duration: float
    bounce_rate: float
    pages_per_session: float
    date_range: Tuple[str, str]


@dataclass
class AcquisitionData:
    """User acquisition breakdown"""
    by_source: List[Dict[str, Any]]
    by_medium: List[Dict[str, Any]]
    by_campaign: List[Dict[str, Any]]
    date_range: Tuple[str, str]


@dataclass
class ConversionData:
    """Conversion tracking data"""
    total_conversions: int
    conversion_rate: float
    by_goal: List[Dict[str, Any]]
    by_source: List[Dict[str, Any]]
    date_range: Tuple[str, str]


class GoogleAnalyticsClient:
    """
    Google Analytics 4 (GA4) API Client

    Handles OAuth2 authentication and provides methods for fetching
    marketing analytics data.
    """

    SCOPES = [
        'https://www.googleapis.com/auth/analytics.readonly'
    ]

    def __init__(self, config: GoogleAnalyticsConfig):
        self.config = config
        self.token: Optional[GoogleToken] = None
        self._session = requests.Session()

    # ========== OAuth Methods ==========

    def get_authorization_url(self, state: str = "") -> str:
        """Generate OAuth authorization URL for user consent"""
        params = {
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.SCOPES),
            'access_type': 'offline',
            'prompt': 'consent',
            'state': state
        }
        return f"{self.config.auth_url}?{urlencode(params)}"

    def exchange_code_for_token(self, authorization_code: str) -> GoogleToken:
        """Exchange authorization code for access token"""
        response = self._session.post(
            self.config.token_url,
            data={
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'code': authorization_code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.config.redirect_uri
            }
        )
        response.raise_for_status()
        data = response.json()

        self.token = GoogleToken(
            access_token=data['access_token'],
            refresh_token=data.get('refresh_token', ''),
            token_type=data.get('token_type', 'Bearer'),
            expires_in=data.get('expires_in', 3600),
            scope=data.get('scope', '')
        )
        return self.token

    def refresh_access_token(self) -> GoogleToken:
        """Refresh the access token using refresh token"""
        if not self.token or not self.token.refresh_token:
            raise ValueError("No refresh token available")

        response = self._session.post(
            self.config.token_url,
            data={
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret,
                'refresh_token': self.token.refresh_token,
                'grant_type': 'refresh_token'
            }
        )
        response.raise_for_status()
        data = response.json()

        self.token = GoogleToken(
            access_token=data['access_token'],
            refresh_token=self.token.refresh_token,  # Refresh token doesn't change
            token_type=data.get('token_type', 'Bearer'),
            expires_in=data.get('expires_in', 3600),
            scope=data.get('scope', self.token.scope)
        )
        return self.token

    def set_token(self, token: GoogleToken):
        """Set token from stored credentials"""
        self.token = token

    def set_property_id(self, property_id: str):
        """Set the GA4 property ID"""
        self.config.property_id = property_id

    def _ensure_valid_token(self):
        """Ensure we have a valid, non-expired token"""
        if not self.token:
            raise ValueError("No token set. Please authenticate first.")
        if self.token.is_expired:
            self.refresh_access_token()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request"""
        self._ensure_valid_token()

        url = f"{self.config.api_base_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.token.access_token}',
            'Content-Type': 'application/json'
        }

        response = self._session.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    # ========== Report Methods ==========

    def run_report(self, metrics: List[str], dimensions: List[str] = None,
                   start_date: str = "30daysAgo", end_date: str = "today",
                   limit: int = 1000) -> AnalyticsReport:
        """Run a custom GA4 report"""
        if not self.config.property_id:
            raise ValueError("Property ID not set")

        body = {
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "metrics": [{"name": m} for m in metrics],
            "limit": limit
        }

        if dimensions:
            body["dimensions"] = [{"name": d} for d in dimensions]

        data = self._make_request(
            'POST',
            f'{self.config.property_id}:runReport',
            json=body
        )

        # Parse response
        rows = []
        dimension_headers = [h['name'] for h in data.get('dimensionHeaders', [])]
        metric_headers = [h['name'] for h in data.get('metricHeaders', [])]

        for row in data.get('rows', []):
            row_data = {}

            # Add dimension values
            for i, dim_value in enumerate(row.get('dimensionValues', [])):
                row_data[dimension_headers[i]] = dim_value.get('value', '')

            # Add metric values
            for i, metric_value in enumerate(row.get('metricValues', [])):
                value = metric_value.get('value', '0')
                # Try to convert to number
                try:
                    row_data[metric_headers[i]] = float(value)
                except ValueError:
                    row_data[metric_headers[i]] = value

            rows.append(row_data)

        # Calculate totals
        totals = {}
        if data.get('totals'):
            for i, total in enumerate(data['totals'][0].get('metricValues', [])):
                try:
                    totals[metric_headers[i]] = float(total.get('value', 0))
                except ValueError:
                    totals[metric_headers[i]] = 0

        return AnalyticsReport(
            dimensions=dimension_headers,
            metrics=metric_headers,
            rows=rows,
            row_count=len(rows),
            date_range=(start_date, end_date),
            totals=totals
        )

    # ========== Traffic Analysis ==========

    def get_traffic_summary(self, start_date: str = "30daysAgo",
                           end_date: str = "today") -> TrafficSummary:
        """Get website traffic summary"""
        report = self.run_report(
            metrics=[
                MetricType.TOTAL_USERS.value,
                MetricType.NEW_USERS.value,
                MetricType.SESSIONS.value,
                MetricType.SCREEN_PAGE_VIEWS.value,
                MetricType.AVERAGE_SESSION_DURATION.value,
                MetricType.BOUNCE_RATE.value
            ],
            start_date=start_date,
            end_date=end_date
        )

        totals = report.totals
        total_users = int(totals.get('totalUsers', 0))
        new_users = int(totals.get('newUsers', 0))
        sessions = int(totals.get('sessions', 0))
        pageviews = int(totals.get('screenPageViews', 0))

        return TrafficSummary(
            total_users=total_users,
            new_users=new_users,
            returning_users=total_users - new_users,
            sessions=sessions,
            pageviews=pageviews,
            avg_session_duration=totals.get('averageSessionDuration', 0),
            bounce_rate=totals.get('bounceRate', 0) * 100,  # Convert to percentage
            pages_per_session=pageviews / sessions if sessions > 0 else 0,
            date_range=(start_date, end_date)
        )

    def get_traffic_by_date(self, start_date: str = "30daysAgo",
                           end_date: str = "today") -> List[Dict[str, Any]]:
        """Get daily traffic breakdown"""
        report = self.run_report(
            metrics=[
                MetricType.ACTIVE_USERS.value,
                MetricType.SESSIONS.value,
                MetricType.SCREEN_PAGE_VIEWS.value
            ],
            dimensions=[DimensionType.DATE.value],
            start_date=start_date,
            end_date=end_date
        )
        return report.rows

    def get_traffic_by_device(self, start_date: str = "30daysAgo",
                             end_date: str = "today") -> List[Dict[str, Any]]:
        """Get traffic breakdown by device category"""
        report = self.run_report(
            metrics=[
                MetricType.ACTIVE_USERS.value,
                MetricType.SESSIONS.value,
                MetricType.BOUNCE_RATE.value
            ],
            dimensions=[DimensionType.DEVICE_CATEGORY.value],
            start_date=start_date,
            end_date=end_date
        )
        return report.rows

    def get_traffic_by_location(self, start_date: str = "30daysAgo",
                                end_date: str = "today",
                                limit: int = 20) -> List[Dict[str, Any]]:
        """Get traffic breakdown by country"""
        report = self.run_report(
            metrics=[MetricType.ACTIVE_USERS.value, MetricType.SESSIONS.value],
            dimensions=[DimensionType.COUNTRY.value],
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return report.rows

    # ========== Acquisition Analysis ==========

    def get_acquisition_data(self, start_date: str = "30daysAgo",
                            end_date: str = "today") -> AcquisitionData:
        """Get user acquisition breakdown"""
        # By source
        source_report = self.run_report(
            metrics=[MetricType.ACTIVE_USERS.value, MetricType.NEW_USERS.value, MetricType.SESSIONS.value],
            dimensions=[DimensionType.SESSION_SOURCE.value],
            start_date=start_date,
            end_date=end_date,
            limit=20
        )

        # By medium
        medium_report = self.run_report(
            metrics=[MetricType.ACTIVE_USERS.value, MetricType.NEW_USERS.value, MetricType.SESSIONS.value],
            dimensions=[DimensionType.SESSION_MEDIUM.value],
            start_date=start_date,
            end_date=end_date,
            limit=20
        )

        # By campaign
        campaign_report = self.run_report(
            metrics=[MetricType.ACTIVE_USERS.value, MetricType.NEW_USERS.value, MetricType.SESSIONS.value],
            dimensions=[DimensionType.SESSION_CAMPAIGN.value],
            start_date=start_date,
            end_date=end_date,
            limit=20
        )

        return AcquisitionData(
            by_source=source_report.rows,
            by_medium=medium_report.rows,
            by_campaign=campaign_report.rows,
            date_range=(start_date, end_date)
        )

    # ========== Engagement Analysis ==========

    def get_top_pages(self, start_date: str = "30daysAgo",
                     end_date: str = "today",
                     limit: int = 20) -> List[Dict[str, Any]]:
        """Get top pages by views"""
        report = self.run_report(
            metrics=[
                MetricType.SCREEN_PAGE_VIEWS.value,
                MetricType.ACTIVE_USERS.value,
                MetricType.AVERAGE_SESSION_DURATION.value
            ],
            dimensions=[DimensionType.PAGE_PATH.value, DimensionType.PAGE_TITLE.value],
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return report.rows

    def get_landing_pages(self, start_date: str = "30daysAgo",
                         end_date: str = "today",
                         limit: int = 20) -> List[Dict[str, Any]]:
        """Get top landing pages"""
        report = self.run_report(
            metrics=[
                MetricType.SESSIONS.value,
                MetricType.BOUNCE_RATE.value,
                MetricType.AVERAGE_SESSION_DURATION.value
            ],
            dimensions=[DimensionType.LANDING_PAGE.value],
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return report.rows

    # ========== Conversion Analysis ==========

    def get_conversions(self, start_date: str = "30daysAgo",
                       end_date: str = "today") -> ConversionData:
        """Get conversion data"""
        # Total conversions
        total_report = self.run_report(
            metrics=[MetricType.CONVERSIONS.value, MetricType.SESSIONS.value],
            start_date=start_date,
            end_date=end_date
        )

        total_conversions = int(total_report.totals.get('conversions', 0))
        total_sessions = int(total_report.totals.get('sessions', 0))
        conversion_rate = (total_conversions / total_sessions * 100) if total_sessions > 0 else 0

        # By event/goal
        goal_report = self.run_report(
            metrics=[MetricType.EVENT_COUNT.value, MetricType.CONVERSIONS.value],
            dimensions=[DimensionType.EVENT_NAME.value],
            start_date=start_date,
            end_date=end_date,
            limit=20
        )

        # By source
        source_report = self.run_report(
            metrics=[MetricType.CONVERSIONS.value, MetricType.SESSIONS.value],
            dimensions=[DimensionType.SESSION_SOURCE.value],
            start_date=start_date,
            end_date=end_date,
            limit=20
        )

        return ConversionData(
            total_conversions=total_conversions,
            conversion_rate=conversion_rate,
            by_goal=goal_report.rows,
            by_source=source_report.rows,
            date_range=(start_date, end_date)
        )

    # ========== Marketing Summary ==========

    def get_marketing_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive marketing analytics summary"""
        end_date = "today"
        start_date = f"{days}daysAgo"

        # Previous period for comparison
        prev_end_date = f"{days + 1}daysAgo"
        prev_start_date = f"{days * 2}daysAgo"

        # Current period data
        traffic = self.get_traffic_summary(start_date, end_date)
        acquisition = self.get_acquisition_data(start_date, end_date)
        top_pages = self.get_top_pages(start_date, end_date, limit=10)
        daily_traffic = self.get_traffic_by_date(start_date, end_date)
        device_breakdown = self.get_traffic_by_device(start_date, end_date)
        geo_breakdown = self.get_traffic_by_location(start_date, end_date, limit=10)

        # Previous period for comparison
        prev_traffic = self.get_traffic_summary(prev_start_date, prev_end_date)

        # Calculate changes
        def calc_change(current, previous):
            if previous == 0:
                return 0
            return ((current - previous) / previous) * 100

        return {
            'period': {
                'start': start_date,
                'end': end_date,
                'days': days
            },
            'traffic': {
                'total_users': traffic.total_users,
                'new_users': traffic.new_users,
                'returning_users': traffic.returning_users,
                'sessions': traffic.sessions,
                'pageviews': traffic.pageviews,
                'avg_session_duration': round(traffic.avg_session_duration, 1),
                'bounce_rate': round(traffic.bounce_rate, 1),
                'pages_per_session': round(traffic.pages_per_session, 2),
                'changes': {
                    'users': round(calc_change(traffic.total_users, prev_traffic.total_users), 1),
                    'sessions': round(calc_change(traffic.sessions, prev_traffic.sessions), 1),
                    'pageviews': round(calc_change(traffic.pageviews, prev_traffic.pageviews), 1),
                    'bounce_rate': round(calc_change(traffic.bounce_rate, prev_traffic.bounce_rate), 1)
                }
            },
            'acquisition': {
                'top_sources': acquisition.by_source[:5],
                'top_mediums': acquisition.by_medium[:5],
                'top_campaigns': [c for c in acquisition.by_campaign[:5] if c.get(DimensionType.SESSION_CAMPAIGN.value, '(not set)') != '(not set)']
            },
            'engagement': {
                'top_pages': top_pages[:10],
                'daily_trend': daily_traffic
            },
            'devices': device_breakdown,
            'geography': geo_breakdown,
            'alerts': self._generate_alerts(traffic, prev_traffic, acquisition)
        }

    def _generate_alerts(self, traffic: TrafficSummary, prev_traffic: TrafficSummary,
                        acquisition: AcquisitionData) -> List[Dict[str, Any]]:
        """Generate marketing alerts based on analysis"""
        alerts = []

        # Traffic decline alert
        user_change = ((traffic.total_users - prev_traffic.total_users) / prev_traffic.total_users * 100) if prev_traffic.total_users > 0 else 0
        if user_change < -10:
            alerts.append({
                'type': 'warning',
                'category': 'Traffic',
                'message': f'Website traffic decreased by {abs(user_change):.1f}% compared to previous period',
                'recommendation': 'Review marketing campaigns and content strategy'
            })

        # High bounce rate alert
        if traffic.bounce_rate > 60:
            alerts.append({
                'type': 'warning',
                'category': 'Engagement',
                'message': f'Bounce rate is {traffic.bounce_rate:.1f}% (above 60% threshold)',
                'recommendation': 'Improve landing page content and user experience'
            })

        # Low session duration alert
        if traffic.avg_session_duration < 60:
            alerts.append({
                'type': 'info',
                'category': 'Engagement',
                'message': f'Average session duration is {traffic.avg_session_duration:.0f} seconds',
                'recommendation': 'Add more engaging content to increase time on site'
            })

        # Single source dependency
        if acquisition.by_source:
            top_source = acquisition.by_source[0]
            top_source_pct = (top_source.get('activeUsers', 0) / traffic.total_users * 100) if traffic.total_users > 0 else 0
            if top_source_pct > 60:
                alerts.append({
                    'type': 'info',
                    'category': 'Acquisition',
                    'message': f'{top_source.get("sessionSource", "Unknown")} accounts for {top_source_pct:.1f}% of traffic',
                    'recommendation': 'Diversify traffic sources to reduce dependency risk'
                })

        return alerts


# Demo mode for testing without real Google Analytics connection
class GoogleAnalyticsDemoClient(GoogleAnalyticsClient):
    """Demo client with mock data for testing"""

    def __init__(self):
        config = GoogleAnalyticsConfig(
            client_id='demo',
            client_secret='demo',
            redirect_uri='http://localhost:5104/demo',
            property_id='properties/demo'
        )
        super().__init__(config)
        self.token = GoogleToken(
            access_token='demo_token',
            refresh_token='demo_refresh'
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Return mock data instead of making real API calls"""
        return self._generate_mock_response(endpoint, kwargs.get('json', {}))

    def _generate_mock_response(self, endpoint: str, request_body: Dict) -> Dict[str, Any]:
        """Generate realistic mock GA4 response data"""
        import random

        metrics = [m['name'] for m in request_body.get('metrics', [])]
        dimensions = [d['name'] for d in request_body.get('dimensions', [])]

        # Generate mock headers
        response = {
            'dimensionHeaders': [{'name': d} for d in dimensions],
            'metricHeaders': [{'name': m} for m in metrics],
            'rows': [],
            'totals': [{'metricValues': []}]
        }

        # Generate mock rows
        num_rows = 30 if 'date' in dimensions else random.randint(5, 20)

        # Mock dimension values
        mock_dimensions = {
            'date': [(datetime.utcnow() - timedelta(days=i)).strftime('%Y%m%d') for i in range(30)],
            'country': ['United States', 'United Kingdom', 'Canada', 'Germany', 'France', 'Australia', 'India', 'Brazil', 'Japan', 'Mexico'],
            'deviceCategory': ['desktop', 'mobile', 'tablet'],
            'sessionSource': ['google', 'direct', 'facebook', 'linkedin', 'twitter', 'bing', 'email', 'referral'],
            'sessionMedium': ['organic', 'cpc', 'referral', 'social', 'email', '(none)'],
            'sessionCampaignName': ['spring_sale', 'brand_awareness', 'product_launch', 'newsletter', '(not set)'],
            'pagePath': ['/', '/products', '/about', '/contact', '/blog', '/pricing', '/demo', '/signup'],
            'pageTitle': ['Home', 'Products', 'About Us', 'Contact', 'Blog', 'Pricing', 'Demo', 'Sign Up'],
            'landingPage': ['/', '/products', '/blog/article-1', '/pricing', '/demo'],
            'eventName': ['page_view', 'scroll', 'click', 'form_submit', 'purchase', 'signup']
        }

        totals = {m: 0 for m in metrics}

        for i in range(min(num_rows, request_body.get('limit', 1000))):
            row = {
                'dimensionValues': [],
                'metricValues': []
            }

            # Add dimension values
            for dim in dimensions:
                if dim in mock_dimensions:
                    values = mock_dimensions[dim]
                    value = values[i % len(values)]
                else:
                    value = f"value_{i}"
                row['dimensionValues'].append({'value': value})

            # Add metric values
            for metric in metrics:
                if metric == 'activeUsers':
                    value = random.randint(100, 5000)
                elif metric == 'totalUsers':
                    value = random.randint(100, 5000)
                elif metric == 'newUsers':
                    value = random.randint(50, 2000)
                elif metric == 'sessions':
                    value = random.randint(150, 7000)
                elif metric == 'engagedSessions':
                    value = random.randint(100, 5000)
                elif metric == 'screenPageViews':
                    value = random.randint(300, 15000)
                elif metric == 'bounceRate':
                    value = random.uniform(0.3, 0.7)
                elif metric == 'averageSessionDuration':
                    value = random.uniform(60, 300)
                elif metric == 'conversions':
                    value = random.randint(5, 200)
                elif metric == 'eventCount':
                    value = random.randint(100, 5000)
                else:
                    value = random.randint(10, 1000)

                row['metricValues'].append({'value': str(value)})
                totals[metric] += value

            response['rows'].append(row)

        # Add totals
        response['totals'][0]['metricValues'] = [{'value': str(totals[m])} for m in metrics]

        return response
