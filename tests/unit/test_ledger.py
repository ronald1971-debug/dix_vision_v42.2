"""Tests for ledger – event store, hash chain, writer, stream router."""

from core.types import HazardEvent, Severity, Stream
from state.ledger.mcos_event_store import EventStore
from state.ledger.mcos_hash_chain import HashChain
from state.ledger.mcos_stream_router import StreamRouter
from state.ledger.mcos_writer import LedgerWriter


def test_hash_chain_append_and_verify():
    chain = HashChain()
    chain.append("governance", "policy_update", {"rule": "test"})
    chain.append("execution", "trade", {"symbol": "BTC"})
    valid, msg = chain.verify_chain()
    assert valid
    assert chain.length == 2


def test_hash_chain_genesis():
    chain = HashChain()
    assert chain.head_hash == HashChain.GENESIS_HASH


def test_event_store_append_and_retrieve():
    store = EventStore()
    ev = store.append("governance", "test_event", {"key": "value"})
    assert store.count == 1
    assert ev.stream == "governance"

    retrieved = store.get_by_sequence(0)
    assert retrieved is not None
    assert retrieved.event_id == ev.event_id


def test_event_store_stream_filtering():
    store = EventStore()
    store.append("governance", "ev1", {})
    store.append("execution", "ev2", {})
    store.append("governance", "ev3", {})

    gov_events = store.get_by_stream("governance")
    assert len(gov_events) == 2
    exec_events = store.get_by_stream("execution")
    assert len(exec_events) == 1


def test_event_store_integrity():
    store = EventStore()
    store.append("governance", "ev1", {"a": 1})
    store.append("cognition", "ev2", {"b": 2})
    valid, _ = store.verify_integrity()
    assert valid


def test_ledger_writer():
    store = EventStore()
    writer = LedgerWriter(store)
    writer.write_governance_event("policy_change", {"policy": "new_rule"})
    writer.write_cognition_event("belief_formed", {"belief": "trend_up"})
    assert store.count == 2

    gov = store.get_by_stream("governance")
    assert len(gov) == 1
    cog = store.get_by_stream("cognition")
    assert len(cog) == 1


def test_ledger_writer_hazard():
    store = EventStore()
    writer = LedgerWriter(store)
    hazard = HazardEvent(
        hazard_id="h1",
        hazard_type="stale_feed",
        severity=Severity.WARNING,
        source="feed:BTC",
        description="Feed stale",
    )
    writer.write_hazard(hazard)
    sys_events = store.get_by_stream("system")
    assert len(sys_events) == 1


def test_stream_router():
    store = EventStore()
    router = StreamRouter(store)

    received: list[str] = []
    router.subscribe(Stream.GOVERNANCE, lambda ev: received.append(ev.event_type))

    router.route("governance", "policy_update", {"rule": "test"})
    assert len(received) == 1
    assert received[0] == "policy_update"


def test_stream_router_invalid_stream():
    store = EventStore()
    router = StreamRouter(store)
    try:
        router.route("invalid_stream", "ev", {})
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass


def test_stream_router_summary():
    store = EventStore()
    router = StreamRouter(store)
    router.route("governance", "ev1", {})
    router.route("governance", "ev2", {})
    router.route("execution", "ev3", {})
    summary = router.get_all_streams_summary()
    assert summary["governance"] == 2
    assert summary["execution"] == 1
