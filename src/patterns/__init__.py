"""Marketing Intelligence - Reusable Patterns"""
from .campaign_scoring import CampaignScoringEngine, create_campaign_performance_engine
from .roi_analyzer import ROIAnalyzer, create_marketing_roi_analyzer
from .benchmark_engine import BenchmarkEngine, create_marketing_benchmarks, create_digital_benchmarks
__all__ = ['CampaignScoringEngine', 'create_campaign_performance_engine', 'ROIAnalyzer', 'create_marketing_roi_analyzer', 'BenchmarkEngine', 'create_marketing_benchmarks', 'create_digital_benchmarks']
