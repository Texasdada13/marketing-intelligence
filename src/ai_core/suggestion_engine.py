"""Context-Aware Suggestion Engine for Marketing Intelligence"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum


class SuggestionCategory(Enum):
    URGENT = "urgent"  # Immediate attention needed
    OPPORTUNITY = "opportunity"  # Growth/improvement opportunity
    FOLLOW_UP = "follow_up"  # Continue previous discussion
    GENERAL = "general"  # Standard prompts


@dataclass
class SuggestedPrompt:
    prompt_text: str
    relevance_score: float  # 0-100
    category: SuggestionCategory
    rationale: str  # Why this is suggested (for UI tooltip)
    topic_tags: List[str]  # For tracking discussed topics

    def to_dict(self) -> Dict[str, Any]:
        return {
            'prompt': self.prompt_text,
            'relevance': round(self.relevance_score, 1),
            'category': self.category.value,
            'rationale': self.rationale,
            'tags': self.topic_tags
        }


class MarketingSuggestionEngine:
    """Generates context-aware prompt suggestions for Marketing Intelligence."""

    # Base prompts by mode (fallback when no context signals)
    BASE_PROMPTS = {
        'general': [
            ("What are the top marketing priorities I should focus on?", ["priorities", "strategy"]),
            ("How is our overall marketing performance?", ["performance", "overview"]),
            ("What quick wins can we achieve this quarter?", ["quick-wins", "tactics"]),
        ],
        'campaign_analysis': [
            ("Which campaigns are underperforming and why?", ["campaigns", "performance"]),
            ("What's the ROI breakdown by campaign type?", ["campaigns", "roi"]),
            ("How do our campaigns compare to benchmarks?", ["campaigns", "benchmarks"]),
        ],
        'channel_optimization': [
            ("Which channels should we invest more in?", ["channels", "investment"]),
            ("Where are we wasting marketing spend?", ["channels", "waste", "efficiency"]),
            ("How should we reallocate our channel budget?", ["channels", "budget"]),
        ],
        'roi_review': [
            ("What's our overall marketing ROI?", ["roi", "overview"]),
            ("Which activities have the best cost-per-acquisition?", ["roi", "cpa"]),
            ("How can we improve our return on ad spend?", ["roi", "roas"]),
        ],
        'content_strategy': [
            ("What content is driving the most engagement?", ["content", "engagement"]),
            ("Where are the gaps in our content funnel?", ["content", "funnel"]),
            ("Which content types should we produce more of?", ["content", "strategy"]),
        ],
        'funnel_analysis': [
            ("Where are prospects dropping off in our funnel?", ["funnel", "dropoff"]),
            ("How can we improve conversion rates?", ["funnel", "conversion"]),
            ("What's causing cart abandonment?", ["funnel", "abandonment"]),
        ],
        'benchmark_discussion': [
            ("How do we compare to industry benchmarks?", ["benchmarks", "comparison"]),
            ("Where are we behind competitors?", ["benchmarks", "competitors"]),
            ("What KPIs should we prioritize improving?", ["benchmarks", "kpis"]),
        ],
        'marketing_planning': [
            ("Help me plan next quarter's marketing strategy", ["planning", "strategy"]),
            ("What should our marketing goals be?", ["planning", "goals"]),
            ("How should we allocate our marketing budget?", ["planning", "budget"]),
        ],
    }

    # Context-triggered prompts (signal -> prompt)
    CONTEXT_TRIGGERS = {
        # ROI/Performance triggers
        'low_roas': {
            'condition': lambda ctx: ctx.get('metrics', {}).get('roas', 999) < 150,
            'prompt': "Your ROAS is {roas}%, below the 150% threshold. What's driving the low return?",
            'category': SuggestionCategory.URGENT,
            'relevance': 95,
            'tags': ['roi', 'roas', 'urgent']
        },
        'high_cac': {
            'condition': lambda ctx: ctx.get('metrics', {}).get('cac', 0) > ctx.get('metrics', {}).get('clv', 999) * 0.3,
            'prompt': "Your CAC (${cac}) is high relative to CLV. Should we discuss acquisition efficiency?",
            'category': SuggestionCategory.URGENT,
            'relevance': 90,
            'tags': ['cac', 'clv', 'efficiency']
        },
        'negative_roi': {
            'condition': lambda ctx: ctx.get('metrics', {}).get('marketing_roi', 100) < 0,
            'prompt': "Marketing ROI is negative ({marketing_roi}%). Let's identify the problem areas.",
            'category': SuggestionCategory.URGENT,
            'relevance': 98,
            'tags': ['roi', 'urgent', 'loss']
        },

        # Channel performance triggers
        'underperforming_channel': {
            'condition': lambda ctx: any(ch.get('efficiency_score', 100) < 50 for ch in ctx.get('channels', [])),
            'prompt': "Some channels are underperforming. Should we review channel efficiency?",
            'category': SuggestionCategory.OPPORTUNITY,
            'relevance': 85,
            'tags': ['channels', 'efficiency', 'optimization']
        },
        'high_performing_channel': {
            'condition': lambda ctx: any(ch.get('roas', 0) > 400 for ch in ctx.get('channels', [])),
            'prompt': "You have high-performing channels (ROAS > 400%). Ready to scale them?",
            'category': SuggestionCategory.OPPORTUNITY,
            'relevance': 80,
            'tags': ['channels', 'scaling', 'growth']
        },

        # Campaign triggers
        'campaigns_below_benchmark': {
            'condition': lambda ctx: len([c for c in ctx.get('campaigns', []) if c.get('overall_score', 100) < 60]) >= 2,
            'prompt': "Multiple campaigns are below benchmark. Let's analyze what's not working.",
            'category': SuggestionCategory.URGENT,
            'relevance': 88,
            'tags': ['campaigns', 'performance', 'analysis']
        },

        # Benchmark triggers
        'below_industry_average': {
            'condition': lambda ctx: ctx.get('benchmark', {}).get('overall_score', 100) < 70,
            'prompt': "Your benchmark score ({overall_score}) is below industry average. Where should we focus?",
            'category': SuggestionCategory.OPPORTUNITY,
            'relevance': 82,
            'tags': ['benchmarks', 'improvement', 'strategy']
        },

        # Content triggers
        'low_engagement': {
            'condition': lambda ctx: ctx.get('metrics', {}).get('social_engagement_rate', 100) < 1,
            'prompt': "Social engagement is low ({social_engagement_rate}%). How can we boost it?",
            'category': SuggestionCategory.OPPORTUNITY,
            'relevance': 75,
            'tags': ['content', 'engagement', 'social']
        },

        # Conversion triggers
        'high_churn': {
            'condition': lambda ctx: ctx.get('metrics', {}).get('churn_rate', 0) > 10,
            'prompt': "Churn rate is {churn_rate}%, above healthy levels. Let's discuss retention strategies.",
            'category': SuggestionCategory.URGENT,
            'relevance': 92,
            'tags': ['retention', 'churn', 'customers']
        },
        'low_conversion': {
            'condition': lambda ctx: ctx.get('metrics', {}).get('conversion_rate', 100) < 2,
            'prompt': "Conversion rate is only {conversion_rate}%. What's blocking conversions?",
            'category': SuggestionCategory.OPPORTUNITY,
            'relevance': 85,
            'tags': ['conversion', 'funnel', 'optimization']
        },
    }

    def __init__(self):
        pass

    def get_suggestions(
        self,
        mode: str,
        context: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        discussed_topics: List[str] = None,
        dismissed_prompts: List[str] = None,
        max_suggestions: int = 4
    ) -> List[SuggestedPrompt]:
        """
        Generate context-aware suggestions.

        Args:
            mode: Current conversation mode
            context: Business context (metrics, campaigns, channels, etc.)
            conversation_history: Previous messages
            discussed_topics: Topics already covered
            dismissed_prompts: Prompts user has dismissed
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of SuggestedPrompt objects sorted by relevance
        """
        discussed_topics = discussed_topics or []
        dismissed_prompts = dismissed_prompts or []

        suggestions = []

        # 1. Check context-triggered prompts first (highest priority)
        for trigger_name, trigger in self.CONTEXT_TRIGGERS.items():
            try:
                if trigger['condition'](context):
                    prompt_text = self._format_prompt(trigger['prompt'], context)

                    # Skip if already discussed or dismissed
                    if self._is_topic_discussed(trigger['tags'], discussed_topics):
                        continue
                    if prompt_text in dismissed_prompts:
                        continue

                    suggestions.append(SuggestedPrompt(
                        prompt_text=prompt_text,
                        relevance_score=trigger['relevance'],
                        category=trigger['category'],
                        rationale=f"Based on your current {trigger_name.replace('_', ' ')} metrics",
                        topic_tags=trigger['tags']
                    ))
            except Exception:
                continue  # Skip malformed triggers

        # 2. Add base prompts for the mode (fill remaining slots)
        base_prompts = self.BASE_PROMPTS.get(mode, self.BASE_PROMPTS['general'])
        for prompt_text, tags in base_prompts:
            if self._is_topic_discussed(tags, discussed_topics):
                continue
            if prompt_text in dismissed_prompts:
                continue

            # Lower relevance for base prompts
            relevance = 50 - (len(suggestions) * 5)  # Decreasing relevance

            suggestions.append(SuggestedPrompt(
                prompt_text=prompt_text,
                relevance_score=max(relevance, 20),
                category=SuggestionCategory.GENERAL,
                rationale=f"Common question for {mode.replace('_', ' ')}",
                topic_tags=tags
            ))

        # 3. Add follow-up suggestions based on conversation history
        if conversation_history:
            follow_ups = self._generate_follow_ups(conversation_history, discussed_topics)
            suggestions.extend(follow_ups)

        # Sort by relevance and return top N
        suggestions.sort(key=lambda x: x.relevance_score, reverse=True)
        return suggestions[:max_suggestions]

    def _format_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """Format prompt template with context values."""
        metrics = context.get('metrics', {})
        benchmark = context.get('benchmark', {})

        # Flatten context for formatting
        format_dict = {**metrics, **benchmark}

        try:
            return template.format(**format_dict)
        except KeyError:
            return template  # Return unformatted if values missing

    def _is_topic_discussed(self, tags: List[str], discussed: List[str]) -> bool:
        """Check if topic tags overlap with discussed topics."""
        return any(tag in discussed for tag in tags)

    def _generate_follow_ups(
        self,
        history: List[Dict[str, Any]],
        discussed: List[str]
    ) -> List[SuggestedPrompt]:
        """Generate follow-up suggestions based on conversation history."""
        follow_ups = []

        if not history:
            return follow_ups

        # Get last assistant message
        last_messages = [m for m in history[-4:] if m.get('role') == 'assistant']
        if not last_messages:
            return follow_ups

        last_response = last_messages[-1].get('content', '').lower()

        # Check for actionable topics mentioned
        follow_up_triggers = [
            {
                'keywords': ['recommend', 'suggest', 'should consider'],
                'prompt': "Can you elaborate on those recommendations?",
                'tags': ['follow-up', 'recommendations']
            },
            {
                'keywords': ['campaign', 'campaigns'],
                'prompt': "Which specific campaign should we focus on first?",
                'tags': ['follow-up', 'campaigns']
            },
            {
                'keywords': ['budget', 'spend', 'investment'],
                'prompt': "How should we reallocate budget based on this?",
                'tags': ['follow-up', 'budget']
            },
            {
                'keywords': ['roi', 'return', 'roas'],
                'prompt': "What's the fastest way to improve our ROI?",
                'tags': ['follow-up', 'roi']
            },
        ]

        for trigger in follow_up_triggers:
            if any(kw in last_response for kw in trigger['keywords']):
                if not self._is_topic_discussed(trigger['tags'], discussed):
                    follow_ups.append(SuggestedPrompt(
                        prompt_text=trigger['prompt'],
                        relevance_score=70,
                        category=SuggestionCategory.FOLLOW_UP,
                        rationale="Follow up on our previous discussion",
                        topic_tags=trigger['tags']
                    ))

        return follow_ups[:2]  # Max 2 follow-ups

    def extract_topics(self, message: str) -> List[str]:
        """Extract topic tags from a message."""
        topics = []

        topic_keywords = {
            'roi': ['roi', 'return', 'roas', 'profitability'],
            'campaigns': ['campaign', 'campaigns', 'ads', 'advertising'],
            'channels': ['channel', 'channels', 'paid', 'organic', 'social'],
            'content': ['content', 'blog', 'video', 'article'],
            'conversion': ['conversion', 'convert', 'funnel', 'leads'],
            'budget': ['budget', 'spend', 'investment', 'cost'],
            'benchmarks': ['benchmark', 'compare', 'industry', 'competitors'],
            'retention': ['retention', 'churn', 'loyalty', 'customer lifetime'],
            'engagement': ['engagement', 'engagement rate', 'interaction'],
        }

        message_lower = message.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in message_lower for kw in keywords):
                topics.append(topic)

        return topics


# Factory function
def create_marketing_suggestion_engine() -> MarketingSuggestionEngine:
    return MarketingSuggestionEngine()
