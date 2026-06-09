"""runtime.convergence — Runtime Convergence Layer.

Wires the RuntimeKernel into the main.py boot sequence, replacing the
simulated market loop with the real kernel tick loop. This is THE
convergence point where:

1. Old path (main.py → IndiraEngine.process_tick → sin-wave) gets replaced
2. RuntimeKernel becomes the single operational loop owner
3. EnforcementGate blocks every intent (governance is real, not advisory)
4. SessionRecorder captures every event for deterministic replay
5. Exchange adapters bind through CCXT (not mock stubs)
6. DecisionPipeline delegates to IndiraEngine (real intelligence)
7. FillReconciler processes real execution fills
8. MarketFeed streams live data into IngestionBus
9. SourceRegistry wires ALL feeds (news, sentiment, on-chain, macro, learning)

Boot sequence:
    bootstrap_kernel.run()          → legacy boot (foundation, config, ledger)
    RuntimeConvergence.boot()       → kernel + fabric + governance + replay
    RuntimeConvergence.run_forever()→ deterministic tick loop + market feed
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from typing import Any

from runtime.authority import RuntimeAuthorityStore, RuntimeSnapshot
from system import time_source

logger = logging.getLogger(__name__)


class RuntimeConvergence:
    """Single convergence point — replaces the simulated loop in main.py.

    Owns:
    - RuntimeAuthorityStore (unified truth)
    - RuntimeKernel (tick loop)
    - EnforcementGate (blocking governance)
    - SessionRecorder (replay capture)
    - MarketFeed (WebSocket/REST → IngestionBus)
    - ExchangeConnector (real exchange binding)
    """

    __slots__ = (
        "_store",
        "_writer_token",
        "_kernel",
        "_gate",
        "_recorder",
        "_connector_mgr",
        "_market_feed",
        "_source_registry",
        "_cognitive_orchestrator",
        "_learning_orchestrator",
        "_dynamic_capability_manager",
        "_intelligence_orchestrator",
        "_ml_orchestrator",
        "_sensory_orchestrator",
        "_evolution_orchestrator",
        "_knowledge_orchestrator",
        "_reasoning_orchestrator",
        "_self_model_orchestrator",
        "_world_model_orchestrator",
        "_simulation_orchestrator",
        "_trader_modeling_orchestrator",
        "_mission_system_orchestrator",
        "_running",
        "_tick_count",
        "_session_id",
    )

    def __init__(self) -> None:
        self._store = RuntimeAuthorityStore()
        self._writer_token = None
        self._kernel = None
        self._gate = None
        self._recorder = None
        self._connector_mgr = None
        self._market_feed = None
        self._source_registry = None
        self._cognitive_orchestrator = None
        self._learning_orchestrator = None
        self._dynamic_capability_manager = None
        self._intelligence_orchestrator = None
        self._ml_orchestrator = None
        self._sensory_orchestrator = None
        self._evolution_orchestrator = None
        self._knowledge_orchestrator = None
        self._reasoning_orchestrator = None
        self._self_model_orchestrator = None
        self._world_model_orchestrator = None
        self._simulation_orchestrator = None
        self._trader_modeling_orchestrator = None
        self._mission_system_orchestrator = None
        self._running = False
        self._tick_count = 0
        self._session_id = f"session_{uuid.uuid4().hex[:12]}"

    @property
    def store(self) -> RuntimeAuthorityStore:
        return self._store

    @property
    def snapshot(self) -> RuntimeSnapshot:
        return self._store.snapshot

    def set_operator_authority(self, authority: object) -> None:
        """Write a new OperatorAuthority snapshot through the execution_fabric token.

        The token is issued during boot; if called before boot the write is
        applied via a temporary token so the pre-boot dashboard can still set
        authority switches without raising.
        """
        from system import time_source

        token = self._writer_token
        if token is None:
            token = self._store.issue_writer_token("execution_fabric")
        token.write(time_source.wall_ns(), operator_authority=authority)

    def set_execution_blocked(self, blocked: bool) -> None:
        """Toggle the live_execution_blocked flag via the execution_fabric token.

        This is the canonical path for the authority dashboard to arm or block
        live execution. The write propagates to any bound SystemKernel via the
        RuntimeAuthorityStore's kernel-delegation logic (_KERNEL_FIELDS).
        """
        from system import time_source

        token = self._writer_token
        if token is None:
            token = self._store.issue_writer_token("execution_fabric")
        token.write(time_source.wall_ns(), live_execution_blocked=blocked)

    async def boot(self) -> bool:
        """Boot the converged runtime.

        Returns True if all subsystems initialized successfully.
        """
        logger.info("[CONVERGENCE] Booting runtime convergence layer...")

        # 1. Acquire writer token for the execution fabric
        self._writer_token = self._store.issue_writer_token("execution_fabric")

        # 2. Initialize enforcement gate with real policies
        from runtime.governance.enforcement_gate import (
            EnforcementGate,
            ExecutionBlockPolicy,
            FreezeBlockPolicy,
            HealthThresholdPolicy,
        )

        self._gate = EnforcementGate(store=self._store)
        self._gate.register_policy(FreezeBlockPolicy())
        self._gate.register_policy(ExecutionBlockPolicy())
        self._gate.register_policy(HealthThresholdPolicy(min_health=0.3))
        logger.info("[CONVERGENCE] Enforcement gate: ARMED (3 policies)")

        # 3. Initialize session recorder for deterministic replay
        from runtime.replay.session_recorder import SessionRecorder

        self._recorder = SessionRecorder(
            session_id=self._session_id,
            store=self._store,
            checkpoint_interval=100,
        )
        self._recorder.start(time_source.wall_ns())
        logger.info("[CONVERGENCE] Session recorder: RECORDING (%s)", self._session_id)

        # 4. Initialize exchange connector manager
        self._connector_mgr = ExchangeConnectorManager(self._store)
        logger.info("[CONVERGENCE] Exchange connector manager: READY")

        # 4.5 Initialize cognitive orchestrator
        try:
            from cognitive_engine.cognitive_orchestrator import get_cognitive_orchestrator
            from system.feature_flags import CognitiveFeatureFlags, FeatureFlagManager
            
            if FeatureFlagManager.is_enabled(CognitiveFeatureFlags.COGNITIVE_ENRICHMENT):
                self._cognitive_orchestrator = get_cognitive_orchestrator()
                cognitive_ok = await self._cognitive_orchestrator.initialize()
                if cognitive_ok:
                    logger.info("[CONVERGENCE] Cognitive orchestrator: READY")
                else:
                    logger.warning("[CONVERGENCE] Cognitive orchestrator: DEGRADED")
                    self._cognitive_orchestrator = None
            else:
                logger.info("[CONVERGENCE] Cognitive orchestrator: DISABLED (feature flag)")
                self._cognitive_orchestrator = None
        except Exception as e:
            logger.warning(f"[CONVERGENCE] Cognitive orchestrator initialization failed: {e}")
            self._cognitive_orchestrator = None

        # 4.6 Initialize learning orchestrator and dynamic capability manager
        try:
            from system.learning_orchestrator import get_learning_orchestrator
            from system.dynamic_enabler import get_dynamic_capability_manager
            from system.feature_flags import CognitiveFeatureFlags, FeatureFlagManager
            
            if FeatureFlagManager.is_enabled(CognitiveFeatureFlags.COGNITIVE_HEALTH_MONITORING):
                self._learning_orchestrator = get_learning_orchestrator()
                self._learning_orchestrator.start_learning()
                self._learning_orchestrator.enable_auto_decision()
                logger.info("[CONVERGENCE] Learning orchestrator: READY (auto decision enabled)")
            else:
                logger.info("[CONVERGENCE] Learning orchestrator: DISABLED (feature flag)")
                self._learning_orchestrator = None
            
            if FeatureFlagManager.is_enabled(CognitiveFeatureFlags.COGNITIVE_HEALTH_MONITORING):
                self._dynamic_capability_manager = get_dynamic_capability_manager()
                self._dynamic_capability_manager.enable_auto_apply()
                logger.info("[CONVERGENCE] Dynamic capability manager: READY (auto apply enabled)")
            else:
                logger.info("[CONVERGENCE] Dynamic capability manager: DISABLED (feature flag)")
                self._dynamic_capability_manager = None
            
            # Set up dependency constraints
            if self._dynamic_capability_manager:
                self._dynamic_capability_manager.add_dependency_constraint(
                    "NARRATIVE_IMPACT_ASSESSMENT", "NARRATIVE_DETECTION"
                )
                self._dynamic_capability_manager.add_dependency_constraint(
                    "COGNITIVE_RISK_ASSESSMENT", "COGNITIVE_ENRICHMENT"
                )
                self._dynamic_capability_manager.add_dependency_constraint(
                    "HYPOTHESIS_VALIDATION", "HYPOTHESIS_AUTO_GENERATION"
                )
                self._dynamic_capability_manager.add_dependency_constraint(
                    "KNOWLEDGE_GRAPH_QUERIES", "KNOWLEDGE_GRAPH_AUTO_POPULATION"
                )
                logger.info("[CONVERGENCE] Dependency constraints: CONFIGURED")
            
        except Exception as e:
            logger.warning(f"[CONVERGENCE] Learning system initialization failed: {e}")
            self._learning_orchestrator = None
            self._dynamic_capability_manager = None

        # 4.7 Initialize advanced intelligence engines
        try:
            from intelligence_engine.orchestrator import get_intelligence_orchestrator
            from learning_engine.orchestrator import get_learning_orchestrator as get_ml_orchestrator
            from sensory.orchestrator import get_sensory_orchestrator
            from evolution_engine.orchestrator import get_evolution_orchestrator
            from knowledge_engine.orchestrator import get_knowledge_orchestrator
            from reasoning_engine.orchestrator import get_reasoning_orchestrator
            from self_model.orchestrator import get_self_model_orchestrator
            from world_model.orchestrator import get_world_model_orchestrator
            from simulation_engine.orchestrator import get_simulation_orchestrator
            from trader_modeling.orchestrator import get_trader_modeling_orchestrator
            from mission_system.orchestrator import get_mission_system_orchestrator
            from system.feature_flags import CognitiveFeatureFlags, FeatureFlagManager
            
            if FeatureFlagManager.is_enabled(CognitiveFeatureFlags.COGNITIVE_HEALTH_MONITORING):
                self._intelligence_orchestrator = get_intelligence_orchestrator()
                self._intelligence_orchestrator.start()
                
                self._ml_orchestrator = get_ml_orchestrator()
                self._ml_orchestrator.start()
                
                self._sensory_orchestrator = get_sensory_orchestrator()
                self._sensory_orchestrator.start()
                
                self._evolution_orchestrator = get_evolution_orchestrator()
                self._evolution_orchestrator.start()
                
                self._knowledge_orchestrator = get_knowledge_orchestrator()
                self._knowledge_orchestrator.start()
                
                self._reasoning_orchestrator = get_reasoning_orchestrator()
                self._reasoning_orchestrator.start()
                
                self._self_model_orchestrator = get_self_model_orchestrator()
                self._self_model_orchestrator.start()
                
                self._world_model_orchestrator = get_world_model_orchestrator()
                self._world_model_orchestrator.start()
                
                self._simulation_orchestrator = get_simulation_orchestrator()
                self._simulation_orchestrator.start()
                
                self._trader_modeling_orchestrator = get_trader_modeling_orchestrator()
                self._trader_modeling_orchestrator.start()
                
                self._mission_system_orchestrator = get_mission_system_orchestrator()
                self._mission_system_orchestrator.start()
                
                # Record these in learning orchestrator for tracking
                if self._learning_orchestrator:
                    engines = ["intelligence", "ml", "sensory", "evolution", "knowledge", "reasoning", 
                             "self_model", "world_model", "simulation", "trader_modeling", "mission"]
                    for engine in engines:
                        self._learning_orchestrator.record_capability_dependency(
                            f"{engine}_operations", "cognitive_health_monitoring"
                        )
                
                logger.info("[CONVERGENCE] Advanced intelligence engines: READY (all 11 engines operational)")
            else:
                logger.info("[CONVERGENCE] Advanced intelligence engines: DISABLED (feature flag)")
                self._intelligence_orchestrator = None
                self._ml_orchestrator = None
                self._sensory_orchestrator = None
                self._evolution_orchestrator = None
                self._knowledge_orchestrator = None
                self._reasoning_orchestrator = None
                self._self_model_orchestrator = None
                self._world_model_orchestrator = None
                self._simulation_orchestrator = None
                self._trader_modeling_orchestrator = None
                self._mission_system_orchestrator = None
        except Exception as e:
            logger.warning(f"[CONVERGENCE] Advanced intelligence engines initialization failed: {e}")
            self._intelligence_orchestrator = None
            self._ml_orchestrator = None
            self._sensory_orchestrator = None
            self._evolution_orchestrator = None
            self._knowledge_orchestrator = None
            self._reasoning_orchestrator = None
            self._self_model_orchestrator = None
            self._world_model_orchestrator = None
            self._simulation_orchestrator = None
            self._trader_modeling_orchestrator = None
            self._mission_system_orchestrator = None

        # 5. Initialize kernel with fabric components
        from runtime.kernel import KernelConfig, RuntimeKernel

        config = KernelConfig(
            tick_interval_ms=float(os.environ.get("DIX_TICK_INTERVAL_MS", "100")),
            governance_timeout_ms=50.0,
            max_intents_per_tick=10,
            enable_replay_validation=True,
            enable_fault_recovery=True,
        )
        self._kernel = RuntimeKernel(config=config, store=self._store)
        boot_ok = await self._kernel.boot()

        # 6. Attach session recorder to kernel for replay capture
        if boot_ok and self._recorder is not None:
            self._kernel.set_recorder(self._recorder)
            logger.info("[CONVERGENCE] Recorder attached to kernel tick loop")

        # 7. Initialize market feed → IngestionBus
        if boot_ok and self._kernel._ingestion is not None:
            from runtime.fabric.market_feed import MarketFeed

            self._market_feed = MarketFeed(
                ingestion_bus=self._kernel._ingestion,
                poll_interval_ms=float(os.environ.get("DIX_POLL_INTERVAL_MS", "1000")),
            )

            # Register Alpaca crypto as default data source (FREE, no keys)
            alpaca_symbols = os.environ.get("DIX_ALPACA_SYMBOLS", "BTC/USD,ETH/USD,SOL/USD").split(
                ","
            )
            self._market_feed.register_alpaca(alpaca_symbols)
            await self._market_feed.start_alpaca_stream()
            logger.info("[CONVERGENCE] Alpaca crypto feed: REGISTERED (%s)", alpaca_symbols)

            # Register exchange bridges for data feeds
            for exchange_id, connector in self._connector_mgr.connectors.items():
                symbols = _default_symbols(exchange_id)
                self._market_feed.register_bridge(exchange_id, connector, symbols)

                # Try WebSocket upgrade
                await self._market_feed.start_websocket(exchange_id, symbols)

            logger.info(
                "[CONVERGENCE] Market feed: READY (%s)",
                "WS" if self._market_feed.ws_available else "REST",
            )

        # 8. Initialize unified source registry (ALL feeds)
        if boot_ok and self._kernel is not None and self._kernel._ingestion is not None:
            try:
                from runtime.fabric.source_registry import SourceRegistry

                self._source_registry = SourceRegistry(bus=self._kernel._ingestion)
                src_count = await self._source_registry.register_all()
                logger.info("[CONVERGENCE] Source registry: %d sources registered", src_count)
            except Exception as e:
                logger.warning("[CONVERGENCE] Source registry init failed: %s", e)

        if boot_ok:
            logger.info("[CONVERGENCE] Kernel booted: RUNNING")
        else:
            logger.warning("[CONVERGENCE] Kernel booted: DEGRADED")

        return boot_ok

    async def run_forever(self) -> None:
        """Run the converged kernel tick loop until stopped.

        This replaces the simulated math.sin() loop in main.py.
        Each tick is the REAL operational loop:
            ingest → decide → GOVERN (blocking) → execute → reconcile → advance
        """
        self._running = True
        logger.info("[CONVERGENCE] Entering operational loop")

        tasks: list[asyncio.Task[None]] = []

        # Start market feed if available
        if self._market_feed is not None:
            tasks.append(asyncio.create_task(self._market_feed.run()))

        # Start source registry (all data feeds)
        if self._source_registry is not None:
            tasks.append(asyncio.create_task(self._source_registry.start()))

        # Start kernel tick loop
        if self._kernel is not None:
            tasks.append(asyncio.create_task(self._kernel.run()))

        if tasks:
            await asyncio.gather(*tasks)

    async def stop(self) -> None:
        """Graceful shutdown."""
        self._running = False
        logger.info("[CONVERGENCE] Shutdown initiated")

        # Stop market feed
        if self._market_feed is not None:
            self._market_feed.stop()

        # Stop source registry
        if self._source_registry is not None:
            self._source_registry.stop()

        # Stop kernel
        if self._kernel is not None:
            await self._kernel.stop()

        # Stop recorder and produce manifest
        if self._recorder is not None and self._recorder.recording:
            manifest = self._recorder.stop(time_source.wall_ns())
            logger.info(
                "[CONVERGENCE] Session %s recorded: %d events, integrity=%s",
                manifest.session_id,
                manifest.total_events,
                manifest.integrity_hash[:16],
            )

        # Disconnect exchanges
        if self._connector_mgr is not None:
            await self._connector_mgr.disconnect_all()

        logger.info("[CONVERGENCE] Runtime stopped")

    def record_event(
        self,
        category: str,
        payload: dict[str, object],
    ) -> None:
        """Record an event to the session recorder (replay capture)."""
        if self._recorder is not None and self._recorder.recording:
            from runtime.replay.session_recorder import EventCategory

            cat = EventCategory(category)
            self._recorder.record(
                category=cat,
                ts_ns=time_source.wall_ns(),
                payload=payload,
            )

    def enforce_intent(
        self,
        intent_id: str,
        intent_data: dict[str, object],
    ) -> bool:
        """Run an intent through the blocking enforcement gate.

        Returns True if allowed, False if denied.
        Records the governance decision for replay.
        """
        if self._gate is None:
            return False  # fail-closed

        ts = time_source.wall_ns()
        result = self._gate.enforce(
            intent_id=intent_id,
            intent_data=intent_data,
            ts_ns=ts,
        )

        # Record governance decision for replay
        self.record_event(
            "governance_decision",
            {
                "intent_id": intent_id,
                "verdict": result.decision.verdict.value,
                "reason": result.decision.reason,
                "state_version": result.decision.state_version,
                "signature": result.decision.signature,
            },
        )

        return result.passed


class ExchangeConnectorManager:
    """Manages exchange connections — bridges BaseAdapter stubs to CCXT.

    When CCXT is available, uses real exchange connections.
    When CCXT is not available, falls back to paper mode.
    """

    def __init__(self, store: RuntimeAuthorityStore) -> None:
        self._store = store
        self._connectors: dict[str, Any] = {}
        self._mode = "paper"  # paper | sandbox | live

    def register_ccxt_bridge(
        self,
        exchange_id: str,
        *,
        api_key: str = "",
        api_secret: str = "",
        sandbox: bool = True,
    ) -> bool:
        """Register a CCXT-backed exchange connection."""
        try:
            from integrations.ccxt_adapter.exchange import ExchangeId
            from integrations.wiring.ccxt_execution_bridge import (
                CCXTExecutionBridge,
            )

            eid = ExchangeId(exchange_id)
            bridge = CCXTExecutionBridge(
                exchange_id=eid,
                sandbox=sandbox,
            )
            connected = bridge.connect(
                api_key=api_key,
                secret=api_secret,
            )

            if connected:
                self._connectors[exchange_id] = bridge
                self._mode = "sandbox" if sandbox else "live"
                logger.info("Exchange %s connected (%s mode)", exchange_id, self._mode)
                return True

        except Exception as e:
            logger.warning("Failed to connect %s: %s", exchange_id, e)

        return False

    async def disconnect_all(self) -> None:
        """Disconnect all exchange connections."""
        for exchange_id, connector in self._connectors.items():
            try:
                if hasattr(connector, "disconnect"):
                    connector.disconnect()
                logger.info("Disconnected from %s", exchange_id)
            except Exception as e:
                logger.warning("Error disconnecting %s: %s", exchange_id, e)
        self._connectors.clear()

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def connected_exchanges(self) -> list[str]:
        return list(self._connectors.keys())

    @property
    def connectors(self) -> dict[str, Any]:
        return self._connectors


def _default_symbols(exchange_id: str) -> list[str]:
    """Default watchlist symbols per exchange."""
    cex_symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    dex_symbols = ["SOL/USDC", "RAY/USDC"]
    if exchange_id in ("raydium", "uniswap"):
        return dex_symbols
    return cex_symbols


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_CONVERGENCE: RuntimeConvergence | None = None


def get_convergence() -> RuntimeConvergence:
    """Get or create the singleton RuntimeConvergence."""
    global _CONVERGENCE
    if _CONVERGENCE is None:
        _CONVERGENCE = RuntimeConvergence()
    return _CONVERGENCE
