"""Tests for INDIRA mind components – observation, beliefs, hypotheses, intent."""

from governance.mcos_constraint_compiler import ExecutionConstraintSet
from mind.beliefs import BeliefSystem
from mind.hypotheses import HypothesisEngine, HypothesisStatus
from mind.intent import IntentGenerator
from mind.knowledge import KnowledgeBase
from mind.observation import ObservationBuffer, ObservationProcessor, ObservationType


def test_observation_processor_tick():
    proc = ObservationProcessor()
    obs = proc.process_tick("BTC/USD", 50000.0, 100.0, "test")
    assert obs.obs_type == ObservationType.PRICE_TICK
    assert obs.symbol == "BTC/USD"
    assert proc.buffer.size == 1


def test_observation_buffer_eviction():
    buf = ObservationBuffer(max_size=5)
    proc = ObservationProcessor()
    for i in range(10):
        obs = proc.process_tick("BTC", float(i), 1.0)
        buf.add(obs)
    assert buf.size <= 5


def test_knowledge_base_acquire_and_query():
    kb = KnowledgeBase()
    kb.acquire("market_structure", "btc_support", 48000.0, confidence=0.8)
    kb.acquire("correlation", "btc_eth", 0.92, confidence=0.9)

    items = kb.query(category="market_structure")
    assert len(items) == 1
    assert items[0].value == 48000.0

    all_items = kb.query()
    assert len(all_items) == 2


def test_knowledge_base_consolidate():
    kb = KnowledgeBase()
    kb.acquire("test", "low_conf", 1.0, confidence=0.1)
    kb.acquire("test", "high_conf", 2.0, confidence=0.9)
    removed = kb.consolidate(min_confidence=0.3)
    assert removed == 1
    assert kb.item_count == 1


def test_belief_system_form_and_update():
    bs = BeliefSystem()
    belief = bs.form_belief("regime", "Market trending up", 0.7)
    assert belief.confidence == 0.7
    assert bs.active_count == 1

    bs.update_belief(belief.belief_id, 0.9)
    updated = bs.get_beliefs("regime")
    assert updated[0].confidence == 0.9


def test_belief_system_invalidate():
    bs = BeliefSystem()
    belief = bs.form_belief("test", "test claim", 0.5)
    bs.invalidate_belief(belief.belief_id)
    assert bs.active_count == 0


def test_hypothesis_engine_generate():
    engine = HypothesisEngine(max_active=5)
    h = engine.generate(
        title="BTC Long",
        thesis="BTC breaking resistance",
        symbol="BTC/USD",
        direction="long",
        confidence=0.75,
    )
    assert h is not None
    assert h.status == HypothesisStatus.FORMING


def test_hypothesis_lifecycle():
    engine = HypothesisEngine()
    h = engine.generate("Test", "thesis", "BTC", "long", 0.8)
    assert h is not None
    engine.activate(h.hypothesis_id)
    assert engine.get_active()[0].status == HypothesisStatus.ACTIVE
    engine.validate(h.hypothesis_id)
    assert engine.get_validated()[0].status == HypothesisStatus.VALIDATED


def test_hypothesis_max_active_limit():
    engine = HypothesisEngine(max_active=2)
    engine.generate("H1", "t", "BTC", "long", 0.5)
    engine.generate("H2", "t", "ETH", "short", 0.6)
    h3 = engine.generate("H3", "t", "SOL", "long", 0.7)
    assert h3 is None


def test_intent_generator():
    engine = HypothesisEngine()
    h = engine.generate("Test", "thesis", "BTC/USD", "long", 0.8)
    assert h is not None
    engine.activate(h.hypothesis_id)
    engine.validate(h.hypothesis_id)

    constraints = ExecutionConstraintSet(min_confidence=0.5, max_position_pct=0.1)
    gen = IntentGenerator()
    intent = gen.generate_intent(h, constraints, position_size=5.0)
    assert intent is not None
    assert intent.symbol == "BTC/USD"
    assert intent.direction == "long"
