"""Marketing Intelligence - Repository Pattern for Data Access"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import db, Organization, Campaign, Channel, Content, MarketingMetrics, BenchmarkResult, ChatSession, ChatMessage


class OrganizationRepository:
    """Repository for Organization operations."""

    @staticmethod
    def create(name: str, **kwargs) -> Organization:
        org = Organization(name=name, **kwargs)
        db.session.add(org)
        db.session.commit()
        return org

    @staticmethod
    def get_by_id(org_id: str) -> Optional[Organization]:
        return Organization.query.get(org_id)

    @staticmethod
    def get_all() -> List[Organization]:
        return Organization.query.order_by(Organization.name).all()

    @staticmethod
    def update(org_id: str, **kwargs) -> Optional[Organization]:
        org = Organization.query.get(org_id)
        if org:
            for key, value in kwargs.items():
                if hasattr(org, key):
                    setattr(org, key, value)
            db.session.commit()
        return org

    @staticmethod
    def delete(org_id: str) -> bool:
        org = Organization.query.get(org_id)
        if org:
            db.session.delete(org)
            db.session.commit()
            return True
        return False


class CampaignRepository:
    """Repository for Campaign operations."""

    @staticmethod
    def create(organization_id: str, name: str, **kwargs) -> Campaign:
        campaign = Campaign(organization_id=organization_id, name=name, **kwargs)
        db.session.add(campaign)
        db.session.commit()
        return campaign

    @staticmethod
    def get_by_id(campaign_id: str) -> Optional[Campaign]:
        return Campaign.query.get(campaign_id)

    @staticmethod
    def get_by_organization(org_id: str) -> List[Campaign]:
        return Campaign.query.filter_by(organization_id=org_id).order_by(Campaign.created_at.desc()).all()

    @staticmethod
    def get_active(org_id: str) -> List[Campaign]:
        return Campaign.query.filter_by(organization_id=org_id, status='active').all()

    @staticmethod
    def update(campaign_id: str, **kwargs) -> Optional[Campaign]:
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            for key, value in kwargs.items():
                if hasattr(campaign, key):
                    setattr(campaign, key, value)
            db.session.commit()
        return campaign

    @staticmethod
    def delete(campaign_id: str) -> bool:
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            db.session.delete(campaign)
            db.session.commit()
            return True
        return False


class ChannelRepository:
    """Repository for Channel operations."""

    @staticmethod
    def create(organization_id: str, name: str, channel_type: str, **kwargs) -> Channel:
        channel = Channel(organization_id=organization_id, name=name, channel_type=channel_type, **kwargs)
        db.session.add(channel)
        db.session.commit()
        return channel

    @staticmethod
    def get_by_id(channel_id: str) -> Optional[Channel]:
        return Channel.query.get(channel_id)

    @staticmethod
    def get_by_organization(org_id: str) -> List[Channel]:
        return Channel.query.filter_by(organization_id=org_id).all()

    @staticmethod
    def update(channel_id: str, **kwargs) -> Optional[Channel]:
        channel = Channel.query.get(channel_id)
        if channel:
            for key, value in kwargs.items():
                if hasattr(channel, key):
                    setattr(channel, key, value)
            db.session.commit()
        return channel


class ContentRepository:
    """Repository for Content operations."""

    @staticmethod
    def create(organization_id: str, title: str, content_type: str, **kwargs) -> Content:
        content = Content(organization_id=organization_id, title=title, content_type=content_type, **kwargs)
        db.session.add(content)
        db.session.commit()
        return content

    @staticmethod
    def get_by_id(content_id: str) -> Optional[Content]:
        return Content.query.get(content_id)

    @staticmethod
    def get_by_organization(org_id: str) -> List[Content]:
        return Content.query.filter_by(organization_id=org_id).order_by(Content.created_at.desc()).all()

    @staticmethod
    def get_by_funnel_stage(org_id: str, stage: str) -> List[Content]:
        return Content.query.filter_by(organization_id=org_id, funnel_stage=stage).all()

    @staticmethod
    def update(content_id: str, **kwargs) -> Optional[Content]:
        content = Content.query.get(content_id)
        if content:
            for key, value in kwargs.items():
                if hasattr(content, key):
                    setattr(content, key, value)
            db.session.commit()
        return content


class MarketingMetricsRepository:
    """Repository for Marketing Metrics operations."""

    @staticmethod
    def create(organization_id: str, period_start: datetime, period_end: datetime, **kwargs) -> MarketingMetrics:
        metrics = MarketingMetrics(
            organization_id=organization_id,
            period_start=period_start,
            period_end=period_end,
            **kwargs
        )
        db.session.add(metrics)
        db.session.commit()
        return metrics

    @staticmethod
    def get_latest(org_id: str) -> Optional[MarketingMetrics]:
        return MarketingMetrics.query.filter_by(organization_id=org_id)\
            .order_by(MarketingMetrics.period_end.desc()).first()

    @staticmethod
    def get_by_period(org_id: str, period: str) -> List[MarketingMetrics]:
        return MarketingMetrics.query.filter_by(organization_id=org_id, period=period)\
            .order_by(MarketingMetrics.period_start.desc()).all()


class BenchmarkResultRepository:
    """Repository for Benchmark Result operations."""

    @staticmethod
    def create(organization_id: str, benchmark_type: str, **kwargs) -> BenchmarkResult:
        result = BenchmarkResult(organization_id=organization_id, benchmark_type=benchmark_type, **kwargs)
        db.session.add(result)
        db.session.commit()
        return result

    @staticmethod
    def get_latest(org_id: str, benchmark_type: str = None) -> Optional[BenchmarkResult]:
        query = BenchmarkResult.query.filter_by(organization_id=org_id)
        if benchmark_type:
            query = query.filter_by(benchmark_type=benchmark_type)
        return query.order_by(BenchmarkResult.created_at.desc()).first()


class ChatRepository:
    """Repository for Chat operations."""

    @staticmethod
    def create_session(mode: str = 'general', organization_id: str = None,
                       title: str = None, context: Dict = None) -> ChatSession:
        session = ChatSession(
            mode=mode,
            organization_id=organization_id,
            title=title or f"Chat Session",
            context=context or {}
        )
        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def get_session(session_id: str) -> Optional[ChatSession]:
        return ChatSession.query.get(session_id)

    @staticmethod
    def get_sessions(organization_id: str = None, limit: int = 20) -> List[ChatSession]:
        query = ChatSession.query
        if organization_id:
            query = query.filter_by(organization_id=organization_id)
        return query.order_by(ChatSession.updated_at.desc()).limit(limit).all()

    @staticmethod
    def add_message(session_id: str, role: str, content: str) -> ChatMessage:
        message = ChatMessage(session_id=session_id, role=role, content=content)
        db.session.add(message)

        # Update session timestamp
        session = ChatSession.query.get(session_id)
        if session:
            session.updated_at = datetime.utcnow()

        db.session.commit()
        return message

    @staticmethod
    def get_messages(session_id: str) -> List[ChatMessage]:
        return ChatMessage.query.filter_by(session_id=session_id)\
            .order_by(ChatMessage.created_at).all()

    @staticmethod
    def delete_session(session_id: str) -> bool:
        session = ChatSession.query.get(session_id)
        if session:
            ChatMessage.query.filter_by(session_id=session_id).delete()
            db.session.delete(session)
            db.session.commit()
            return True
        return False
