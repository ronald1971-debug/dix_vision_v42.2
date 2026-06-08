"""Cognitive Development Pipeline (Cognitive Spine).

Sequential pipeline – no stage skipping:

  Observation
  → Knowledge Acquisition
  → Validation
  → Belief Formation
  → Hypothesis Generation
  → Simulation
  → Evaluation
  → Learning
  → Update
  → Evolution Proposal
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto

from core.types import ExecutionIntent
from governance.mcos_constraint_compiler import ExecutionConstraintSet
from mind.beliefs import BeliefSystem
from mind.hypotheses import HypothesisEngine
from mind.intent import IntentGenerator
from mind.knowledge import KnowledgeBase
from mind.observation import Observation, ObservationProcessor


class PipelineStage(Enum):
    OBSERVATION = auto()
    KNOWLEDGE_ACQUISITION = auto()
    VALIDATION = auto()
    BELIEF_FORMATION = auto()
    HYPOTHESIS_GENERATION = auto()
    SIMULATION = auto()
    EVALUATION = auto()
    LEARNING = auto()
    UPDATE = auto()
    EVOLUTION_PROPOSAL = auto()


@dataclass
class PipelineResult:
    """Result of a full cognitive pipeline cycle."""
    cycle_id: str = ""
    stages_completed: list[str] = field(default_factory=list)
    observations_processed: int = 0
    knowledge_acquired: int = 0
    beliefs_formed: int = 0
    hypotheses_generated: int = 0
    intents_produced: list[ExecutionIntent] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: float = field(default_factory=time.time)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


class CognitiveSpine:
    """Orchestrates the full cognitive development pipeline.

    Rules: No stage skipping. Each stage must complete before the next begins.
    """

    STAGE_ORDER = list(PipelineStage)

    def __init__(
        self,
        observation_processor: ObservationProcessor,
        knowledge_base: KnowledgeBase,
        belief_system: BeliefSystem,
        hypothesis_engine: HypothesisEngine,
        intent_generator: IntentGenerator,
        constraints: ExecutionConstraintSet | None = None,
    ) -> None:
        self._observer = observation_processor
        self._knowledge = knowledge_base
        self._beliefs = belief_system
        self._hypotheses = hypothesis_engine
        self._intent_gen = intent_generator
        self._constraints = constraints or ExecutionConstraintSet()
        self._cycle_count = 0
        self._last_result: PipelineResult | None = None

    def run_cycle(
        self, observations: list[Observation] | None = None
    ) -> PipelineResult:
        """Execute one full cognitive cycle through all stages."""
        start = time.time()
        self._cycle_count += 1
        result = PipelineResult(cycle_id=f"cycle_{self._cycle_count}")

        # Stage 1: Observation
        obs_list = observations or self._observer.buffer.get_recent(50)
        result.observations_processed = len(obs_list)
        result.stages_completed.append(PipelineStage.OBSERVATION.name)

        # Stage 2: Knowledge Acquisition
        knowledge_count = 0
        for obs in obs_list:
            if obs.confidence >= 0.5:
                self._knowledge.acquire(
                    category=obs.obs_type.name.lower(),
                    key=f"{obs.symbol}:{obs.obs_type.name}",
                    value=obs.value,
                    confidence=obs.confidence,
                    source_observations=[obs.observation_id],
                )
                knowledge_count += 1
        result.knowledge_acquired = knowledge_count
        result.stages_completed.append(PipelineStage.KNOWLEDGE_ACQUISITION.name)

        # Stage 3: Validation
        self._knowledge.consolidate(min_confidence=0.2)
        result.stages_completed.append(PipelineStage.VALIDATION.name)

        # Stage 4: Belief Formation
        beliefs_formed = 0
        regime_knowledge = self._knowledge.query(category="regime_signal")
        for ki in regime_knowledge:
            self._beliefs.form_belief(
                category="regime",
                claim=f"Regime signal: {ki.key}",
                confidence=ki.confidence,
                evidence_ids=[ki.item_id],
            )
            beliefs_formed += 1

        price_knowledge = self._knowledge.query(category="price_tick")
        for ki in price_knowledge[-5:]:
            self._beliefs.form_belief(
                category="price_action",
                claim=f"Price action: {ki.key} = {ki.value}",
                confidence=ki.confidence,
                evidence_ids=[ki.item_id],
            )
            beliefs_formed += 1
        result.beliefs_formed = beliefs_formed
        result.stages_completed.append(PipelineStage.BELIEF_FORMATION.name)

        # Stage 5: Hypothesis Generation
        hypotheses_generated = 0
        top_beliefs = self._beliefs.get_beliefs()[:3]
        for belief in top_beliefs:
            if belief.confidence >= 0.5:
                h = self._hypotheses.generate(
                    title=f"H:{belief.claim[:30]}",
                    thesis=belief.claim,
                    symbol=belief.metadata.get("symbol", ""),
                    direction="long" if belief.confidence > 0.6 else "short",
                    confidence=belief.confidence,
                    belief_ids=[belief.belief_id],
                    time_horizon_seconds=3600.0,
                )
                if h:
                    self._hypotheses.activate(h.hypothesis_id)
                    hypotheses_generated += 1
        result.hypotheses_generated = hypotheses_generated
        result.stages_completed.append(PipelineStage.HYPOTHESIS_GENERATION.name)

        # Stage 6: Simulation (placeholder evaluation)
        self._hypotheses.expire_stale()
        result.stages_completed.append(PipelineStage.SIMULATION.name)

        # Stage 7: Evaluation
        best = self._hypotheses.get_best_hypothesis()
        if best and best.confidence >= 0.6:
            self._hypotheses.validate(best.hypothesis_id)
        result.stages_completed.append(PipelineStage.EVALUATION.name)

        # Stage 8: Learning (belief pruning)
        self._beliefs.prune_stale(max_age_seconds=600.0)
        result.stages_completed.append(PipelineStage.LEARNING.name)

        # Stage 9: Update (generate intents from validated hypotheses)
        intents: list[ExecutionIntent] = []
        for h in self._hypotheses.get_validated():
            intent = self._intent_gen.generate_intent(h, self._constraints)
            if intent:
                intents.append(intent)
                self._hypotheses.mark_executed(h.hypothesis_id)
        result.intents_produced = intents
        result.stages_completed.append(PipelineStage.UPDATE.name)

        # Stage 10: Evolution Proposal (logged, not executed)
        result.stages_completed.append(PipelineStage.EVOLUTION_PROPOSAL.name)

        result.duration_seconds = time.time() - start
        self._last_result = result
        return result

    def update_constraints(self, constraints: ExecutionConstraintSet) -> None:
        self._constraints = constraints

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    @property
    def last_result(self) -> PipelineResult | None:
        return self._last_result
