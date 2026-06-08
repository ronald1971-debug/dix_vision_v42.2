"""Intent Generation – converts validated hypotheses to ExecutionIntents.

Fast Path: Market Data → Indira → Governance Constraints → Execution
"""

from __future__ import annotations

import time
import uuid

from core.types import ExecutionIntent
from governance.mcos_constraint_compiler import ExecutionConstraintSet
from mind.hypotheses import Hypothesis, HypothesisStatus


class IntentGenerator:
    """Converts hypotheses into governed execution intents."""

    def __init__(self) -> None:
        self._generated_intents: list[ExecutionIntent] = []

    def generate_intent(
        self,
        hypothesis: Hypothesis,
        constraints: ExecutionConstraintSet,
        position_size: float = 1.0,
    ) -> ExecutionIntent | None:
        if hypothesis.status not in (
            HypothesisStatus.VALIDATED,
            HypothesisStatus.ACTIVE,
        ):
            return None

        if not constraints.allows_execution():
            return None

        if not constraints.check_confidence(hypothesis.confidence):
            return None

        adjusted_size = min(position_size, constraints.max_position_pct * 100)

        intent = ExecutionIntent(
            intent_id=uuid.uuid4().hex[:12],
            symbol=hypothesis.symbol,
            direction=hypothesis.direction,
            quantity=adjusted_size,
            confidence=hypothesis.confidence,
            reasoning=hypothesis.thesis,
            hypothesis_id=hypothesis.hypothesis_id,
            constraints={
                "max_position_pct": constraints.max_position_pct,
                "max_loss_pct": constraints.max_loss_pct,
            },
            timestamp=time.time(),
        )
        self._generated_intents.append(intent)
        return intent

    def get_generated_intents(self) -> list[ExecutionIntent]:
        return list(self._generated_intents)

    @property
    def intent_count(self) -> int:
        return len(self._generated_intents)
