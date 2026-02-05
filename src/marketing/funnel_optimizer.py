"""Marketing Funnel Analysis and Optimization"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class FunnelStage(Enum):
    AWARENESS = "Awareness"
    INTEREST = "Interest"
    CONSIDERATION = "Consideration"
    INTENT = "Intent"
    EVALUATION = "Evaluation"
    PURCHASE = "Purchase"
    RETENTION = "Retention"
    ADVOCACY = "Advocacy"


@dataclass
class StageMetrics:
    stage: FunnelStage
    visitors: int
    conversions: int
    conversion_rate: float
    drop_off_rate: float
    avg_time_in_stage: float  # hours
    cost_per_stage: float


@dataclass
class FunnelAnalysis:
    stages: List[StageMetrics]
    overall_conversion_rate: float
    total_visitors: int
    total_conversions: int
    total_cost: float
    cost_per_conversion: float
    biggest_leaks: List[str]
    optimization_priorities: List[str]
    projected_lift: float  # Potential conversion improvement %

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stages": [
                {
                    "stage": s.stage.value,
                    "visitors": s.visitors,
                    "conversions": s.conversions,
                    "conversion_rate": round(s.conversion_rate, 2),
                    "drop_off_rate": round(s.drop_off_rate, 2),
                    "avg_time_in_stage": round(s.avg_time_in_stage, 1),
                    "cost_per_stage": round(s.cost_per_stage, 2)
                }
                for s in self.stages
            ],
            "overall_conversion_rate": round(self.overall_conversion_rate, 2),
            "total_visitors": self.total_visitors,
            "total_conversions": self.total_conversions,
            "total_cost": round(self.total_cost, 2),
            "cost_per_conversion": round(self.cost_per_conversion, 2),
            "biggest_leaks": self.biggest_leaks,
            "optimization_priorities": self.optimization_priorities,
            "projected_lift": round(self.projected_lift, 1)
        }


class FunnelOptimizer:
    """Analyzes and optimizes marketing/sales funnel performance."""

    # Industry benchmark conversion rates by stage
    STAGE_BENCHMARKS = {
        FunnelStage.AWARENESS: {"conversion": 30.0, "time": 24},
        FunnelStage.INTEREST: {"conversion": 50.0, "time": 48},
        FunnelStage.CONSIDERATION: {"conversion": 40.0, "time": 72},
        FunnelStage.INTENT: {"conversion": 60.0, "time": 48},
        FunnelStage.EVALUATION: {"conversion": 50.0, "time": 96},
        FunnelStage.PURCHASE: {"conversion": 70.0, "time": 24},
        FunnelStage.RETENTION: {"conversion": 85.0, "time": 720},
        FunnelStage.ADVOCACY: {"conversion": 30.0, "time": 2160},
    }

    def __init__(self, stages: Optional[List[FunnelStage]] = None):
        self.stages = stages or [
            FunnelStage.AWARENESS,
            FunnelStage.INTEREST,
            FunnelStage.CONSIDERATION,
            FunnelStage.INTENT,
            FunnelStage.PURCHASE
        ]

    def analyze_funnel(self, stage_data: Dict[FunnelStage, Dict[str, Any]]) -> FunnelAnalysis:
        """Analyze funnel performance and identify optimization opportunities."""
        stage_metrics = []
        previous_visitors = None

        for stage in self.stages:
            data = stage_data.get(stage, {})
            visitors = data.get("visitors", 0)
            conversions = data.get("conversions", 0)
            time_in_stage = data.get("avg_time", 0)
            cost = data.get("cost", 0)

            conversion_rate = (conversions / visitors * 100) if visitors > 0 else 0
            drop_off = 100 - conversion_rate

            if previous_visitors is not None and previous_visitors > 0:
                # Calculate stage-to-stage drop-off
                stage_entry_rate = (visitors / previous_visitors * 100)
                drop_off = 100 - stage_entry_rate

            stage_metrics.append(StageMetrics(
                stage=stage,
                visitors=visitors,
                conversions=conversions,
                conversion_rate=conversion_rate,
                drop_off_rate=drop_off,
                avg_time_in_stage=time_in_stage,
                cost_per_stage=cost
            ))

            previous_visitors = conversions  # Next stage entry = this stage conversions

        # Calculate overall metrics
        total_visitors = stage_metrics[0].visitors if stage_metrics else 0
        total_conversions = stage_metrics[-1].conversions if stage_metrics else 0
        overall_rate = (total_conversions / total_visitors * 100) if total_visitors > 0 else 0
        total_cost = sum(s.cost_per_stage for s in stage_metrics)
        cpc = (total_cost / total_conversions) if total_conversions > 0 else 0

        # Identify biggest leaks
        leaks = self._identify_leaks(stage_metrics)

        # Generate optimization priorities
        priorities = self._generate_priorities(stage_metrics)

        # Calculate projected lift
        lift = self._calculate_projected_lift(stage_metrics)

        return FunnelAnalysis(
            stages=stage_metrics,
            overall_conversion_rate=overall_rate,
            total_visitors=total_visitors,
            total_conversions=total_conversions,
            total_cost=total_cost,
            cost_per_conversion=cpc,
            biggest_leaks=leaks,
            optimization_priorities=priorities,
            projected_lift=lift
        )

    def _identify_leaks(self, stages: List[StageMetrics]) -> List[str]:
        """Identify stages with biggest conversion drop-offs."""
        leaks = []

        for stage in stages:
            benchmark = self.STAGE_BENCHMARKS.get(stage.stage, {})
            expected_rate = benchmark.get("conversion", 50)

            if stage.conversion_rate < expected_rate * 0.7:
                gap = expected_rate - stage.conversion_rate
                leaks.append(
                    f"{stage.stage.value}: {stage.drop_off_rate:.1f}% drop-off "
                    f"(benchmark: {100 - expected_rate:.1f}%)"
                )

        # Sort by severity (highest drop-off first)
        leaks.sort(key=lambda x: float(x.split(": ")[1].split("%")[0]), reverse=True)
        return leaks[:5]

    def _generate_priorities(self, stages: List[StageMetrics]) -> List[str]:
        """Generate optimization priorities based on funnel analysis."""
        priorities = []
        stage_opportunities = []

        for i, stage in enumerate(stages):
            benchmark = self.STAGE_BENCHMARKS.get(stage.stage, {})
            expected_rate = benchmark.get("conversion", 50)
            expected_time = benchmark.get("time", 48)

            # Calculate potential impact
            if stage.conversion_rate < expected_rate:
                improvement = expected_rate - stage.conversion_rate
                # Impact = improvement * visitors remaining
                potential_new_conversions = stage.visitors * (improvement / 100)
                stage_opportunities.append({
                    "stage": stage.stage,
                    "current_rate": stage.conversion_rate,
                    "target_rate": expected_rate,
                    "potential_gain": potential_new_conversions,
                    "improvement_pct": improvement
                })

            # Check for time issues
            if stage.avg_time_in_stage > expected_time * 1.5:
                priorities.append(
                    f"Reduce time in {stage.stage.value} stage - "
                    f"currently {stage.avg_time_in_stage:.0f}h vs {expected_time:.0f}h benchmark"
                )

        # Sort opportunities by potential gain
        stage_opportunities.sort(key=lambda x: x["potential_gain"], reverse=True)

        for opp in stage_opportunities[:3]:
            priorities.insert(0,
                f"Optimize {opp['stage'].value}: +{opp['improvement_pct']:.1f}% could add "
                f"{opp['potential_gain']:.0f} conversions"
            )

        return priorities[:5]

    def _calculate_projected_lift(self, stages: List[StageMetrics]) -> float:
        """Calculate potential conversion improvement if all stages hit benchmarks."""
        if not stages:
            return 0

        current_rate = 1.0
        potential_rate = 1.0

        for stage in stages:
            benchmark = self.STAGE_BENCHMARKS.get(stage.stage, {})
            expected = benchmark.get("conversion", 50) / 100

            current = stage.conversion_rate / 100
            current_rate *= current
            potential_rate *= max(current, expected)

        if current_rate > 0:
            return ((potential_rate / current_rate) - 1) * 100
        return 0

    def simulate_improvement(self, stage_data: Dict[FunnelStage, Dict[str, Any]],
                            improvements: Dict[FunnelStage, float]) -> Dict[str, Any]:
        """Simulate funnel performance with proposed improvements."""
        modified_data = {}

        for stage, data in stage_data.items():
            modified = data.copy()
            if stage in improvements:
                # Apply improvement to conversion rate
                current_conv = data.get("conversions", 0)
                visitors = data.get("visitors", 0)
                current_rate = (current_conv / visitors) if visitors > 0 else 0
                new_rate = min(1.0, current_rate + (improvements[stage] / 100))
                modified["conversions"] = int(visitors * new_rate)
            modified_data[stage] = modified

        # Cascade the improvements through the funnel
        prev_conversions = None
        for stage in self.stages:
            if stage in modified_data:
                if prev_conversions is not None:
                    modified_data[stage]["visitors"] = prev_conversions
                    rate = stage_data.get(stage, {}).get("conversions", 0) / \
                           max(1, stage_data.get(stage, {}).get("visitors", 1))
                    if stage in improvements:
                        rate = min(1.0, rate + (improvements[stage] / 100))
                    modified_data[stage]["conversions"] = int(prev_conversions * rate)
                prev_conversions = modified_data[stage].get("conversions", 0)

        # Analyze the simulated funnel
        simulated = self.analyze_funnel(modified_data)
        original = self.analyze_funnel(stage_data)

        return {
            "original_conversion_rate": original.overall_conversion_rate,
            "simulated_conversion_rate": simulated.overall_conversion_rate,
            "improvement_percent": simulated.overall_conversion_rate - original.overall_conversion_rate,
            "original_conversions": original.total_conversions,
            "simulated_conversions": simulated.total_conversions,
            "additional_conversions": simulated.total_conversions - original.total_conversions
        }
