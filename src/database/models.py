"""Marketing Intelligence - Database Models"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


def generate_uuid():
    return str(uuid.uuid4())


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))  # SMB, Mid-Market, Enterprise
    annual_marketing_budget = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaigns = db.relationship('Campaign', backref='organization', lazy=True)
    channels = db.relationship('Channel', backref='organization', lazy=True)
    content = db.relationship('Content', backref='organization', lazy=True)
    chat_sessions = db.relationship('ChatSession', backref='organization', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'industry': self.industry,
            'size': self.size,
            'annual_marketing_budget': self.annual_marketing_budget,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    campaign_type = db.Column(db.String(50))  # Lead Gen, Brand Awareness, Product Launch, etc.
    status = db.Column(db.String(20), default='draft')  # draft, active, paused, completed
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    budget = db.Column(db.Float, default=0.0)
    spend = db.Column(db.Float, default=0.0)

    # Performance Metrics
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    leads = db.Column(db.Integer, default=0)
    revenue = db.Column(db.Float, default=0.0)

    # Calculated Scores
    performance_score = db.Column(db.Float)
    roi_score = db.Column(db.Float)
    overall_score = db.Column(db.Float)
    rating = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.name,
            'campaign_type': self.campaign_type,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'budget': self.budget,
            'spend': self.spend,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'conversions': self.conversions,
            'leads': self.leads,
            'revenue': self.revenue,
            'performance_score': self.performance_score,
            'roi_score': self.roi_score,
            'overall_score': self.overall_score,
            'rating': self.rating
        }


class Channel(db.Model):
    __tablename__ = 'channels'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    channel_type = db.Column(db.String(50))  # Organic Search, Paid Search, Social, Email, etc.
    status = db.Column(db.String(20), default='active')

    # Channel Metrics
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    spend = db.Column(db.Float, default=0.0)
    revenue = db.Column(db.Float, default=0.0)
    leads = db.Column(db.Integer, default=0)
    new_customers = db.Column(db.Integer, default=0)

    # Calculated KPIs
    ctr = db.Column(db.Float)
    conversion_rate = db.Column(db.Float)
    cpc = db.Column(db.Float)
    cpa = db.Column(db.Float)
    roas = db.Column(db.Float)
    efficiency_score = db.Column(db.Float)
    rating = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.name,
            'channel_type': self.channel_type,
            'status': self.status,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'conversions': self.conversions,
            'spend': self.spend,
            'revenue': self.revenue,
            'ctr': self.ctr,
            'conversion_rate': self.conversion_rate,
            'cpa': self.cpa,
            'roas': self.roas,
            'efficiency_score': self.efficiency_score,
            'rating': self.rating
        }


class Content(db.Model):
    __tablename__ = 'content'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    content_type = db.Column(db.String(50))  # Blog, Video, Whitepaper, etc.
    funnel_stage = db.Column(db.String(20))  # TOFU, MOFU, BOFU
    status = db.Column(db.String(20), default='published')
    publish_date = db.Column(db.DateTime)
    url = db.Column(db.String(500))

    # Content Metrics
    views = db.Column(db.Integer, default=0)
    unique_visitors = db.Column(db.Integer, default=0)
    time_on_page = db.Column(db.Float, default=0.0)
    bounce_rate = db.Column(db.Float, default=0.0)
    shares = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    leads_generated = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)

    # Scores
    engagement_score = db.Column(db.Float)
    conversion_score = db.Column(db.Float)
    overall_score = db.Column(db.Float)
    rating = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'title': self.title,
            'content_type': self.content_type,
            'funnel_stage': self.funnel_stage,
            'status': self.status,
            'views': self.views,
            'unique_visitors': self.unique_visitors,
            'time_on_page': self.time_on_page,
            'bounce_rate': self.bounce_rate,
            'shares': self.shares,
            'leads_generated': self.leads_generated,
            'engagement_score': self.engagement_score,
            'conversion_score': self.conversion_score,
            'overall_score': self.overall_score,
            'rating': self.rating
        }


class MarketingMetrics(db.Model):
    __tablename__ = 'marketing_metrics'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    period = db.Column(db.String(20))  # monthly, quarterly, yearly
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)

    # Acquisition Metrics
    cac = db.Column(db.Float)  # Customer Acquisition Cost
    cpl = db.Column(db.Float)  # Cost per Lead
    website_traffic = db.Column(db.Integer)
    organic_traffic_pct = db.Column(db.Float)

    # Conversion Metrics
    conversion_rate = db.Column(db.Float)
    lead_to_customer_rate = db.Column(db.Float)
    cart_abandonment_rate = db.Column(db.Float)

    # Engagement Metrics
    email_open_rate = db.Column(db.Float)
    email_ctr = db.Column(db.Float)
    social_engagement_rate = db.Column(db.Float)

    # Retention Metrics
    customer_retention_rate = db.Column(db.Float)
    churn_rate = db.Column(db.Float)

    # Revenue Metrics
    clv = db.Column(db.Float)  # Customer Lifetime Value
    roas = db.Column(db.Float)  # Return on Ad Spend
    marketing_roi = db.Column(db.Float)
    total_revenue = db.Column(db.Float)
    total_spend = db.Column(db.Float)

    # Brand Metrics
    brand_awareness = db.Column(db.Float)
    nps = db.Column(db.Float)  # Net Promoter Score

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'period': self.period,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'cac': self.cac,
            'cpl': self.cpl,
            'conversion_rate': self.conversion_rate,
            'clv': self.clv,
            'roas': self.roas,
            'marketing_roi': self.marketing_roi,
            'customer_retention_rate': self.customer_retention_rate,
            'nps': self.nps
        }


class BenchmarkResult(db.Model):
    __tablename__ = 'benchmark_results'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    benchmark_type = db.Column(db.String(50))  # marketing, digital, campaign
    overall_score = db.Column(db.Float)
    overall_rating = db.Column(db.String(20))
    grade = db.Column(db.String(2))
    category_scores = db.Column(db.JSON)
    strengths = db.Column(db.JSON)
    improvements = db.Column(db.JSON)
    recommendations = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'benchmark_type': self.benchmark_type,
            'overall_score': self.overall_score,
            'overall_rating': self.overall_rating,
            'grade': self.grade,
            'category_scores': self.category_scores,
            'strengths': self.strengths,
            'improvements': self.improvements,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=True)
    mode = db.Column(db.String(50), default='general')
    title = db.Column(db.String(200))
    context = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Enhanced chat fields
    discussed_topics = db.Column(db.JSON, default=list)  # Topics already covered
    dismissed_suggestions = db.Column(db.JSON, default=list)  # User-dismissed prompts
    conversation_summary = db.Column(db.Text)  # Running summary for long conversations
    summary_updated_at = db.Column(db.DateTime)
    topic_tags = db.Column(db.JSON, default=list)  # Extracted topic tags
    key_insights = db.Column(db.JSON, default=list)  # Important insights from conversation

    messages = db.relationship('ChatMessage', backref='session', lazy=True,
                               order_by='ChatMessage.created_at')
    uploaded_files = db.relationship('UploadedFile', backref='session', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'mode': self.mode,
            'title': self.title,
            'context': self.context,
            'discussed_topics': self.discussed_topics or [],
            'topic_tags': self.topic_tags or [],
            'has_summary': self.conversation_summary is not None,
            'file_count': len(self.uploaded_files) if self.uploaded_files else 0,
            'message_count': len(self.messages) if self.messages else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    session_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UploadedFile(db.Model):
    """Uploaded files for chat analysis."""
    __tablename__ = 'uploaded_files'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    session_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=True)

    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # csv, xlsx, json
    file_size = db.Column(db.Integer)  # bytes

    # Store analysis results, not raw file (for security and size)
    analysis_result = db.Column(db.JSON)  # Full analysis as JSON
    context_summary = db.Column(db.Text)  # Formatted for prompt injection
    row_count = db.Column(db.Integer)
    column_count = db.Column(db.Integer)
    detected_metrics = db.Column(db.JSON)  # Auto-detected metric columns

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'detected_metrics': self.detected_metrics,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
