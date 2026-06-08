"""Simulation Runner – orchestrates full simulation pipelines.

All cognition is tested before deployment (Phase 12 exit criteria).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from governance.mcos_constraint_compiler import ConstraintCompiler
from governance.mcos_kernel import GovernanceKernel
from mind.beliefs import BeliefSystem
from mind.hypotheses import HypothesisEngine
from mind.intent import IntentGenerator
from mind.knowledge import KnowledgeBase
from mind.observation import ObservationProcessor
from runtime.mcos_cognitive_spine import CognitiveSpine, PipelineResult
from simulation.market_replay import MarketReplay


@dataclass
class SimulationConfig:
    num_ticks: int = 1000
    symbol: str = "SIM/USD"
    base_price: float = 100.0
    volatility: float = 0.02


@dataclass
class SimulationResult:
    cycles_run: int = 0
    total_observations: int = 0
    total_intents: int = 0
    total_hypotheses: int = 0
    beliefs_at_end: int = 0
    duration_seconds: float = 0.0
    pipeline_results: list[PipelineResult] = field(default_factory=list)


class SimulationRunner:
    """Runs a full simulation cycle with synthetic or replayed data."""

    def __init__(self, governance: GovernanceKernel) -> None:
        self._governance = governance

    def run(self, config: SimulationConfig | None = None) -> SimulationResult:
        cfg = config or SimulationConfig()
        start = time.time()

        observer = ObservationProcessor()
        knowledge = KnowledgeBase()
        beliefs = BeliefSystem()
        hypotheses = HypothesisEngine()
        intent_gen = IntentGenerator()
        compiler = ConstraintCompiler(self._governance)
        constraints = compiler.compile()

        spine = CognitiveSpine(
            observation_processor=observer,
            knowledge_base=knowledge,
            belief_system=beliefs,
            hypothesis_engine=hypotheses,
            intent_generator=intent_gen,
            constraints=constraints,
        )

        replay = MarketReplay()
        replay.generate_synthetic_data(
            symbol=cfg.symbol,
            num_ticks=cfg.num_ticks,
            base_price=cfg.base_price,
            volatility=cfg.volatility,
        )

        pipeline_results: list[PipelineResult] = []
        total_intents = 0
        batch: list[Any] = []
        batch_size = 50

        for obs in replay.replay():
            observer.buffer.add(obs)
            batch.append(obs)

            if len(batch) >= batch_size:
                result = spine.run_cycle(batch)
                pipeline_results.append(result)
                total_intents += len(result.intents_produced)
                batch = []

        if batch:
            result = spine.run_cycle(batch)
            pipeline_results.append(result)
            total_intents += len(result.intents_produced)

        return SimulationResult(
            cycles_run=len(pipeline_results),
            total_observations=cfg.num_ticks,
            total_intents=total_intents,
            total_hypotheses=sum(r.hypotheses_generated for r in pipeline_results),
            beliefs_at_end=beliefs.active_count,
            duration_seconds=time.time() - start,
            pipeline_results=pipeline_results,
        )
