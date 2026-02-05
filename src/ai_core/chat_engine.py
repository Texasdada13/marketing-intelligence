"""Marketing Intelligence - AI Chat Engine with CMO Conversation Modes"""
from enum import Enum
from typing import Dict, List, Optional, Generator, Any
from .claude_client import ClaudeClient
from .suggestion_engine import MarketingSuggestionEngine, SuggestedPrompt


class ConversationMode(Enum):
    """CMO-focused conversation modes."""
    GENERAL = "general"
    CAMPAIGN_ANALYSIS = "campaign_analysis"
    CHANNEL_OPTIMIZATION = "channel_optimization"
    CONTENT_STRATEGY = "content_strategy"
    FUNNEL_ANALYSIS = "funnel_analysis"
    ROI_REVIEW = "roi_review"
    BENCHMARK_DISCUSSION = "benchmark_discussion"
    MARKETING_PLANNING = "marketing_planning"


MODE_DESCRIPTIONS = {
    ConversationMode.GENERAL: "General marketing questions and guidance",
    ConversationMode.CAMPAIGN_ANALYSIS: "Analyze campaign performance and optimize",
    ConversationMode.CHANNEL_OPTIMIZATION: "Optimize marketing channel mix and budget",
    ConversationMode.CONTENT_STRATEGY: "Content marketing strategy and performance",
    ConversationMode.FUNNEL_ANALYSIS: "Marketing funnel optimization",
    ConversationMode.ROI_REVIEW: "Marketing ROI and spend efficiency",
    ConversationMode.BENCHMARK_DISCUSSION: "Industry benchmarks and competitive analysis",
    ConversationMode.MARKETING_PLANNING: "Strategic marketing planning and roadmaps",
}


SUGGESTED_PROMPTS = {
    ConversationMode.GENERAL: [
        "What marketing metrics should I track for a B2B SaaS company?",
        "How can I improve our marketing team's efficiency?",
        "What's the best approach to marketing attribution?",
    ],
    ConversationMode.CAMPAIGN_ANALYSIS: [
        "Analyze our campaign performance and identify improvement areas",
        "Which campaigns are underperforming and why?",
        "How should we adjust our campaign strategy?",
    ],
    ConversationMode.CHANNEL_OPTIMIZATION: [
        "Which marketing channels are most effective for us?",
        "How should we reallocate our channel budget?",
        "Compare our channel performance to industry benchmarks",
    ],
    ConversationMode.CONTENT_STRATEGY: [
        "What content types are driving the most leads?",
        "How can we improve our content marketing ROI?",
        "What content gaps exist in our funnel?",
    ],
    ConversationMode.FUNNEL_ANALYSIS: [
        "Where are the biggest leaks in our marketing funnel?",
        "How can we improve our conversion rates?",
        "What's causing drop-off at the consideration stage?",
    ],
    ConversationMode.ROI_REVIEW: [
        "What's our marketing ROI by channel?",
        "How can we reduce customer acquisition cost?",
        "Are we spending efficiently on marketing?",
    ],
    ConversationMode.BENCHMARK_DISCUSSION: [
        "How do our marketing KPIs compare to industry standards?",
        "Where are we underperforming vs benchmarks?",
        "What metrics should we prioritize improving?",
    ],
    ConversationMode.MARKETING_PLANNING: [
        "Help me build a Q1 marketing plan",
        "What should be our top marketing priorities?",
        "How should we allocate next year's marketing budget?",
    ],
}


SYSTEM_PROMPTS = {
    ConversationMode.GENERAL: """You are a Fractional CMO (Chief Marketing Officer) - an expert marketing executive providing strategic guidance to SMB companies. You help with all aspects of marketing strategy, from brand building to demand generation.

Your expertise includes:
- Marketing strategy and planning
- Brand development and positioning
- Demand generation and lead nurturing
- Digital marketing and analytics
- Content marketing strategy
- Marketing team building and operations

Provide actionable, practical advice tailored to resource-constrained organizations. Be strategic but pragmatic.""",

    ConversationMode.CAMPAIGN_ANALYSIS: """You are a Fractional CMO specializing in campaign performance analysis. You help organizations understand what's working and what's not in their marketing campaigns.

For campaign analysis, you focus on:
- Performance metrics: impressions, clicks, conversions, ROAS
- Creative effectiveness and messaging resonance
- Audience targeting and segmentation
- A/B testing insights
- Budget efficiency and optimization opportunities

Analyze campaigns objectively, identify root causes of underperformance, and provide specific optimization recommendations.""",

    ConversationMode.CHANNEL_OPTIMIZATION: """You are a Fractional CMO specializing in marketing channel strategy and optimization. You help organizations build an effective marketing mix.

For channel optimization, you focus on:
- Channel performance comparison (organic, paid, social, email, etc.)
- Budget allocation across channels
- Channel synergies and attribution
- Emerging channel opportunities
- Cost efficiency (CPC, CPA, ROAS by channel)

Recommend data-driven budget shifts and channel strategies that maximize ROI.""",

    ConversationMode.CONTENT_STRATEGY: """You are a Fractional CMO specializing in content marketing strategy. You help organizations create and optimize content that drives business results.

For content strategy, you focus on:
- Content performance analysis by type and topic
- Content mapping to buyer journey stages
- SEO and organic visibility
- Lead generation and conversion from content
- Content repurposing and distribution

Recommend content strategies that build audience, generate leads, and support sales.""",

    ConversationMode.FUNNEL_ANALYSIS: """You are a Fractional CMO specializing in marketing funnel optimization. You help organizations improve conversion rates at every stage.

For funnel analysis, you focus on:
- Stage-by-stage conversion rates
- Drop-off points and friction analysis
- Lead scoring and qualification
- Nurture sequence effectiveness
- Sales and marketing alignment

Identify funnel leaks and recommend specific interventions to improve flow.""",

    ConversationMode.ROI_REVIEW: """You are a Fractional CMO specializing in marketing ROI and financial performance. You help organizations maximize the return on their marketing investment.

For ROI review, you focus on:
- Marketing ROI calculation and tracking
- Customer acquisition cost (CAC) analysis
- Customer lifetime value (CLV) optimization
- Attribution modeling
- Budget efficiency and waste reduction

Provide clear financial analysis and recommendations to improve marketing profitability.""",

    ConversationMode.BENCHMARK_DISCUSSION: """You are a Fractional CMO specializing in marketing benchmarking and competitive analysis. You help organizations understand their performance relative to industry standards.

For benchmarking, you focus on:
- KPI comparison to industry standards
- Competitive positioning analysis
- Best practice identification
- Performance gap analysis
- Improvement prioritization

Provide context on where the organization stands and what "good" looks like in their industry.""",

    ConversationMode.MARKETING_PLANNING: """You are a Fractional CMO specializing in strategic marketing planning. You help organizations build effective marketing plans and roadmaps.

For marketing planning, you focus on:
- Goal setting and OKRs
- Budget planning and allocation
- Campaign calendars and timing
- Resource planning and team structure
- Success metrics and tracking

Create actionable plans that align marketing activities with business objectives.""",
}


class ChatEngine:
    """AI-powered chat engine for Marketing Intelligence."""

    def __init__(self, claude_client: ClaudeClient = None):
        self.client = claude_client or ClaudeClient()
        self.suggestion_engine = MarketingSuggestionEngine()

    def get_modes(self) -> Dict[str, str]:
        """Get available conversation modes with descriptions."""
        return {mode.value: desc for mode, desc in MODE_DESCRIPTIONS.items()}

    def get_suggested_prompts(self, mode: ConversationMode) -> List[str]:
        """Get suggested prompts for a conversation mode."""
        return SUGGESTED_PROMPTS.get(mode, SUGGESTED_PROMPTS[ConversationMode.GENERAL])

    def get_dynamic_suggestions(
        self,
        mode: str,
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, Any]] = None,
        discussed_topics: List[str] = None,
        dismissed_prompts: List[str] = None,
        max_suggestions: int = 4
    ) -> List[Dict[str, Any]]:
        """Get context-aware dynamic suggestions."""
        suggestions = self.suggestion_engine.get_suggestions(
            mode=mode,
            context=context or {},
            conversation_history=conversation_history or [],
            discussed_topics=discussed_topics,
            dismissed_prompts=dismissed_prompts,
            max_suggestions=max_suggestions
        )
        return [s.to_dict() for s in suggestions]

    def extract_topics(self, message: str) -> List[str]:
        """Extract topic tags from a message."""
        return self.suggestion_engine.extract_topics(message)

    def chat(self, message: str, mode: ConversationMode = ConversationMode.GENERAL,
             history: List[Dict[str, str]] = None, context: Dict[str, Any] = None) -> str:
        """Send a message and get a response."""
        system_prompt = self._build_system_prompt(mode, context)
        messages = self._build_messages(message, history)

        return self.client.chat(messages, system=system_prompt)

    def chat_stream(self, message: str, mode: ConversationMode = ConversationMode.GENERAL,
                    history: List[Dict[str, str]] = None,
                    context: Dict[str, Any] = None) -> Generator[str, None, None]:
        """Stream a chat response."""
        system_prompt = self._build_system_prompt(mode, context)
        messages = self._build_messages(message, history)

        return self.client.chat_stream(messages, system=system_prompt)

    def _build_system_prompt(self, mode: ConversationMode, context: Dict[str, Any] = None) -> str:
        """Build system prompt with mode and context."""
        base_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS[ConversationMode.GENERAL])

        if context:
            context_str = self._format_context(context)
            return f"{base_prompt}\n\n## Current Context\n{context_str}"

        return base_prompt

    def _build_messages(self, message: str, history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """Build message list from history and new message."""
        messages = []

        if history:
            for msg in history[-10:]:  # Keep last 10 messages for context
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": message})
        return messages

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context data for the system prompt."""
        parts = []

        if "organization" in context:
            org = context["organization"]
            parts.append(f"**Organization**: {org.get('name', 'Unknown')}")
            if org.get('industry'):
                parts.append(f"**Industry**: {org['industry']}")
            if org.get('annual_marketing_budget'):
                parts.append(f"**Annual Marketing Budget**: ${org['annual_marketing_budget']:,.0f}")

        if "campaigns" in context:
            campaigns = context["campaigns"]
            parts.append(f"\n**Active Campaigns**: {len(campaigns)}")
            for c in campaigns[:5]:
                parts.append(f"- {c.get('name')}: {c.get('status')} (Score: {c.get('overall_score', 'N/A')})")

        if "channels" in context:
            channels = context["channels"]
            parts.append(f"\n**Marketing Channels**: {len(channels)}")
            for ch in channels[:5]:
                parts.append(f"- {ch.get('name')}: ROAS {ch.get('roas', 0):.0f}%, Score: {ch.get('efficiency_score', 'N/A')}")

        if "metrics" in context:
            m = context["metrics"]
            parts.append(f"\n**Key Metrics**:")
            if m.get('cac'):
                parts.append(f"- CAC: ${m['cac']:.2f}")
            if m.get('clv'):
                parts.append(f"- CLV: ${m['clv']:.2f}")
            if m.get('roas'):
                parts.append(f"- ROAS: {m['roas']:.0f}%")
            if m.get('marketing_roi'):
                parts.append(f"- Marketing ROI: {m['marketing_roi']:.0f}%")

        if "benchmark" in context:
            b = context["benchmark"]
            parts.append(f"\n**Benchmark Summary**:")
            parts.append(f"- Overall Score: {b.get('overall_score', 'N/A')}")
            parts.append(f"- Grade: {b.get('grade', 'N/A')}")
            if b.get('strengths'):
                parts.append(f"- Strengths: {', '.join(b['strengths'][:3])}")

        return "\n".join(parts) if parts else "No additional context available."

    def analyze_with_ai(self, data: Dict[str, Any], analysis_type: str) -> str:
        """Perform AI-powered analysis on marketing data."""
        prompts = {
            "campaign_performance": "Analyze this campaign performance data and provide insights on what's working, what's not, and specific recommendations for improvement.",
            "channel_mix": "Analyze this channel performance data and recommend an optimized budget allocation strategy.",
            "content_effectiveness": "Analyze this content performance data and recommend a content strategy to improve results.",
            "funnel_optimization": "Analyze this funnel data and identify the biggest opportunities to improve conversion rates.",
            "roi_analysis": "Analyze this marketing ROI data and recommend ways to improve marketing efficiency.",
        }

        prompt = prompts.get(analysis_type, "Analyze this marketing data and provide actionable insights.")
        context = f"Data for analysis:\n```json\n{data}\n```"

        messages = [{"role": "user", "content": f"{prompt}\n\n{context}"}]
        system = SYSTEM_PROMPTS[ConversationMode.GENERAL]

        return self.client.chat(messages, system=system)
