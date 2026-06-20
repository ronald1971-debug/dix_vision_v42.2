# DIX VISION v42.2 — REPO RESEARCH & ADAPTATION PROMPTS
# =========================================================
# HOW TO USE:
# 1. Copy PART 1 (Master Safety Context) at the START of every AI session
# 2. Pick any repo block from PART 2
# 3. Paste the repo block into the same session
# 4. AI will research → identify → adapt → output ready-to-use DIX code
# 5. Run validators before committing: see PART 3
# =========================================================

# =========================================================
# PART 1 — MASTER SAFETY CONTEXT
# Copy this at the start of EVERY session before any repo prompt
# =========================================================

---MASTER SAFETY CONTEXT (paste at start of session)---

You are adapting battle-tested open-source code into DIX VISION v42.2.

SYSTEM RULES — NON-NEGOTIABLE:
1. NEVER write new trading logic from scratch. Extract from the source repo, then adapt.
2. NEVER import external repo code directly into hot_path/ tier modules.
3. NEVER call datetime.now() or time.time() directly — always accept TimeSource injection.
4. NEVER add global mutable state.
5. NEVER bypass the ledger — all execution events must emit to the ledger.
6. NEVER violate authority boundaries (tools/authority_lint.py rules T1, C2, C3, W1, L1, L2, L3, B1).
7. ALWAYS add # ADAPTED FROM: [repo] [original file path] at top of every adapted file.
8. ALWAYS implement the DIX Pydantic contract for the target module — never invent a new interface.
9. ALWAYS output a test file alongside every implementation file.
10. ALWAYS flag new pip dependencies — never silently add them.
11. ALWAYS preserve replay determinism (INV-15) — same inputs must produce same outputs.
12. ONE file per session. Never adapt multiple files in one response.

TIER RULES:
- RUNTIME tier (intelligence_engine, execution_engine, system_engine, governance_engine):
  No ML inference, no blocking I/O, no non-deterministic operations.
- OFFLINE tier (learning_engine, evolution_engine):
  Can use ML, can be slow, but must emit only UPDATE_PROPOSED events to runtime.
- ADAPTERS (execution_engine/adapters/):
  Must implement AdapterBase. Sandboxed behind adapter boundary. Never called from hot path directly.

BEFORE OUTPUTTING CODE:
- Mentally run: python tools/authority_lint.py --strict [output_file]
- Confirm: does this file respect tier separation?
- Confirm: does this file implement the exact DIX contract interface?
- Confirm: are all external dependencies wrapped (not bare-imported at module level in hot path)?

---END MASTER SAFETY CONTEXT---


# =========================================================
# PART 2 — REPO RESEARCH PROMPTS
# Priority S = critical path | A = high value | B = future wave | C = research only
# =========================================================

# ─────────────────────────────────────────────
# TIER S — DO THESE FIRST (fills P0/P1 gaps)
# ─────────────────────────────────────────────

## [S-01] ccxt — Binance + Exchange Adapters
## Priority: S | DIX Gap: execution_engine/adapters/binance.py (MISSING)
---REPO PROMPT S-01: ccxt---
Repo: https://github.com/ccxt/ccxt
Target DIX file: execution_engine/adapters/binance.py

STEP 1 — RESEARCH:
Fetch and read these files from the ccxt repo:
- python/ccxt/binance.py (focus on: create_order, cancel_order, fetch_order, fetch_balance, error handling, retry logic)
- python/ccxt/base/exchange.py (focus on: rate limiting, error hierarchy, request throttling)

List what ccxt does well that DIX should keep:
- Error handling and retry patterns
- Rate limit management
- Order state normalization
- Websocket reconnection logic

STEP 2 — MAP TO DIX:
Read these DIX files (I will paste them):
[PASTE: execution_engine/adapters/base.py]
[PASTE: core/contracts/events.py — ExecutionEvent section]
[PASTE: core/contracts/execution_intent.py]

STEP 3 — ADAPT:
Wrap ccxt's Binance implementation to satisfy execution_engine/adapters/base.py AdapterBase.
Rules:
- Keep ccxt's battle-tested error handling and retry logic verbatim
- Replace ccxt's internal clock with TimeSource parameter
- Map ccxt order responses → DIX ExecutionEvent
- Wrap ccxt import so it only loads outside hot_path
- Add # ADAPTED FROM: ccxt/python/ccxt/binance.py

Output:
1. execution_engine/adapters/binance.py
2. tests/test_binance_adapter.py
3. List any new pip dependencies needed
---END REPO PROMPT S-01---


## [S-02] hftbacktest — Slippage, Latency, Orderbook Simulation
## Priority: S | DIX Gap: simulation/slippage_model.py, simulation/latency_model.py (MISSING)
---REPO PROMPT S-02: hftbacktest---
Repo: https://github.com/nkaz001/hftbacktest
Target DIX files: simulation/slippage_model.py, simulation/latency_model.py

STEP 1 — RESEARCH:
Fetch and read these files from hftbacktest:
- hftbacktest/backtest/proc/local.py (fill logic, queue position, slippage calculation)
- hftbacktest/latency/ (latency modeling)
- hftbacktest/data/ (data normalization patterns)

Identify:
- The core mathematical model for slippage (keep this exactly)
- Queue-position estimation logic (keep this exactly)
- Latency distribution model (keep this exactly)
- Any external dependencies (numpy, etc.)

STEP 2 — MAP TO DIX:
Read:
[PASTE: core/contracts/simulation.py]
[PASTE: core/contracts/execution_intent.py — order types]

STEP 3 — ADAPT:
Rules:
- Preserve hftbacktest's mathematical model exactly — do not simplify
- Make deterministic: accept seed: int in __init__, use numpy.random.Generator(numpy.random.PCG64(seed)) — no global random state
- SlippageModel and LatencyModel must be OFFLINE only (never called from RUNTIME tier)
- Add # ADAPTED FROM: hftbacktest

Output:
1. simulation/slippage_model.py
2. simulation/latency_model.py
3. tests/test_slippage_model.py
4. tests/test_latency_model.py
---END REPO PROMPT S-02---


## [S-03] NautilusTrader — Simulation Engine Core + Event Loop
## Priority: S | DIX Gap: simulation/engine.py (MISSING)
---REPO PROMPT S-03: nautilus_trader---
Repo: https://github.com/nautechsystems/nautilus_trader
Target DIX file: simulation/engine.py

STEP 1 — RESEARCH:
Fetch and read from nautilus_trader:
- nautilus_trader/backtest/engine.py (BacktestEngine — event loop, clock, data feeding)
- nautilus_trader/common/clock.py (TestClock, deterministic time)
- nautilus_trader/backtest/data_client.py (data feeding patterns)

Identify:
- The deterministic event loop design (how time is stepped)
- How nautilus handles replay ordering (timestamp ordering, tie-breaking)
- Clock injection pattern (how they avoid datetime.now())

STEP 2 — MAP TO DIX:
Read:
[PASTE: core/contracts/simulation.py]
[PASTE: core/contracts/events.py]
[PASTE: system_engine/time_source.py if it exists, else describe what TimeSource should look like]

STEP 3 — ADAPT:
Rules:
- Keep nautilus's deterministic clock/event-loop architecture
- Replace nautilus event types with DIX SignalEvent/ExecutionEvent/SystemEvent/HazardEvent
- SimulationEngine must be OFFLINE tier only
- Must accept TimeSource injection — no internal clock
- Add # ADAPTED FROM: nautilus_trader/backtest/engine.py

Output:
1. simulation/engine.py
2. tests/test_simulation_engine.py
---END REPO PROMPT S-03---


## [S-04] EventStoreDB — Hash Chain Ledger
## Priority: S | DIX Gap: state/ledger/hash_chain.py (MISSING)
---REPO PROMPT S-04: EventStoreDB---
Repo: https://github.com/EventStore/EventStore
Concept repo (C#): extract architectural patterns only, implement in Python

STEP 1 — RESEARCH:
Read from EventStoreDB source:
- src/EventStore.Core/Services/Storage/ReaderIndex/ (hash chain concepts)
- src/EventStore.Core/TransactionLog/ (append-only log, CRC/hash validation)

Identify the pattern for:
- How each appended event includes a hash of the previous event
- How integrity is verified on read
- How snapshots work without breaking the chain

STEP 2 — MAP TO DIX:
Read:
[PASTE: state/ledger/reader.py — existing DIX ledger reader]
[PASTE: ui/_ledger_boot.py — existing ledger boot]

STEP 3 — ADAPT:
Implement Python hash chain on top of existing DIX SQLite ledger.
Rules:
- Each row must store: sha256(previous_hash + event_bytes)
- Verification must be O(n) scan, O(1) spot-check
- Must not break existing reader.py interface
- OFFLINE only — hash chain verification never called from hot path
- Add # ADAPTED FROM: EventStoreDB hash chain concepts

Output:
1. state/ledger/hash_chain.py
2. state/ledger/integrity.py
3. tests/test_ledger_hash_chain.py
---END REPO PROMPT S-04---


## [S-05] Qlib — PnL Attribution + Performance Analytics
## Priority: S | DIX Gap: learning_engine/performance_analysis/ (MISSING)
---REPO PROMPT S-05: Qlib---
Repo: https://github.com/microsoft/qlib
Target DIX files: learning_engine/performance_analysis/pnl_attribution.py,
                  learning_engine/performance_analysis/alpha_decay.py,
                  learning_engine/performance_analysis/execution_quality.py

STEP 1 — RESEARCH:
Fetch and read from Qlib:
- qlib/contrib/evaluate.py (backtest evaluation, PnL calculation)
- qlib/contrib/report/ (performance reporting, attribution)
- qlib/data/dataset/ (feature pipeline patterns)

Identify the core math for:
- PnL attribution (signal contribution vs execution slippage)
- Alpha decay measurement (how quickly a signal degrades)
- Execution quality scoring (VWAP deviation, timing)

STEP 2 — MAP TO DIX:
Read:
[PASTE: core/contracts/backtest_result.py]
[PASTE: core/contracts/learning.py]

STEP 3 — ADAPT:
Rules:
- Keep Qlib's statistical formulas exactly
- Remove Qlib's data loading dependencies — accept pre-loaded DataFrames
- OFFLINE tier only
- Output must be Pydantic models matching DIX contracts
- Add # ADAPTED FROM: qlib/contrib/evaluate.py

Output:
1. learning_engine/performance_analysis/pnl_attribution.py
2. learning_engine/performance_analysis/alpha_decay.py
3. learning_engine/performance_analysis/execution_quality.py
4. tests/test_pnl_attribution.py
---END REPO PROMPT S-05---


## [S-06] TradingAgents — Agent Base + Archetype Framework
## Priority: S | DIX Gap: intelligence_engine/agents/_base.py + archetypes (MISSING)
---REPO PROMPT S-06: TradingAgents---
Repo: https://github.com/TauricResearch/TradingAgents
(Note: if repo is private/unavailable, use AutoGen agent patterns instead)
Target DIX files: intelligence_engine/agents/_base.py, intelligence_engine/agents/scalper.py,
                  intelligence_engine/agents/swing_trader.py

STEP 1 — RESEARCH:
Fetch TradingAgents source. Read:
- The base agent class structure
- How roles are defined (analyst, trader, risk manager)
- How agents communicate signals
- How debate/committee logic works

STEP 2 — MAP TO DIX:
Read:
[PASTE: core/contracts/agent.py — AgentContract protocol]
[PASTE: registry/trader_archetypes.yaml]
[PASTE: core/contracts/events.py — SignalEvent]

STEP 3 — ADAPT:
Rules:
- Each agent must implement DIX AgentContract exactly
- Agents produce SignalEvent — never ExecutionEvent (authority rule)
- Agent must accept belief_state as input (not fetch it internally)
- LLM calls must be async and wrapped in timeout — never blocking hot path
- Add # ADAPTED FROM: TradingAgents

Output:
1. intelligence_engine/agents/_base.py
2. intelligence_engine/agents/scalper.py
3. intelligence_engine/agents/swing_trader.py
4. tests/test_agent_archetypes.py
---END REPO PROMPT S-06---


## [S-07] Firecrawl — Web Autolearn Crawler
## Priority: S | DIX Gap: sensory/web_autolearn/crawler.py (exists but stub)
---REPO PROMPT S-07: firecrawl---
Repo: https://github.com/mendableai/firecrawl
Target DIX file: sensory/web_autolearn/crawler.py

STEP 1 — RESEARCH:
Fetch and read from firecrawl:
- apps/api/src/scraper/ (core scraping logic)
- apps/api/src/lib/extract/ (content extraction)
- Python SDK: firecrawl-py/firecrawl/firecrawl.py

Identify:
- Content extraction pipeline
- Rate limiting approach
- Error handling for blocked sites
- Output normalization (how raw HTML becomes structured data)

STEP 2 — MAP TO DIX:
Read:
[PASTE: sensory/web_autolearn/crawler.py — current stub]
[PASTE: core/contracts/news.py — NewsItem contract]

STEP 3 — ADAPT:
Rules:
- Sandbox: crawler must run in isolated subprocess — never in RUNTIME tier
- Rate limit: max 1 request/second by default, configurable
- Output: always NewsItem Pydantic model — never raw HTML to other modules
- Sanitize: strip scripts, ads, tracking before outputting
- No firecrawl API dependency — adapt the extraction logic directly
- Add # ADAPTED FROM: firecrawl

Output:
1. sensory/web_autolearn/crawler.py (replace stub)
2. tests/test_web_crawler.py
---END REPO PROMPT S-07---


## [S-08] River — Online Feature Learning
## Priority: S | DIX Gap: learning_engine/online_features (feeds slow-loop learner)
---REPO PROMPT S-08: river---
Repo: https://github.com/online-ml/river
Target DIX file: learning_engine/online_learner.py (or extend slow_loop_learner.py)

STEP 1 — RESEARCH:
Fetch and read from river:
- river/drift/ (concept drift detection — ADWIN, PageHinkley)
- river/stats/ (online mean, variance, EWM)
- river/feature_extraction/ (online feature transforms)

Identify:
- ADWIN drift detector (keep math exactly)
- Online EWM (exponential weighted mean) implementation
- Stateful online mean/variance

STEP 2 — MAP TO DIX:
Read:
[PASTE: learning_engine/slow_loop_learner.py — existing]
[PASTE: core/contracts/learning.py]

STEP 3 — ADAPT:
Rules:
- River's drift detectors must be wrapped as DIX plugins
- State must be serializable (for ledger checkpointing)
- OFFLINE tier — never called from hot path
- Add # ADAPTED FROM: river

Output:
1. learning_engine/drift_detector.py
2. learning_engine/online_stats.py
3. tests/test_drift_detector.py
---END REPO PROMPT S-08---


## [S-09] PyPortfolioOpt — Portfolio Risk + Allocation
## Priority: S | DIX Gap: intelligence_engine/portfolio/ modules (MISSING)
---REPO PROMPT S-09: PyPortfolioOpt---
Repo: https://github.com/robertmartin8/PyPortfolioOpt
Target DIX files: intelligence_engine/portfolio/risk_parity.py,
                  intelligence_engine/portfolio/correlation_engine.py

STEP 1 — RESEARCH:
Fetch and read from PyPortfolioOpt:
- pypfopt/risk_models.py (covariance, correlation, shrinkage)
- pypfopt/efficient_frontier.py (optimization)
- pypfopt/black_litterman.py (if available)

Identify:
- Ledoit-Wolf shrinkage covariance (keep math exactly)
- Risk parity weight calculation
- Max Sharpe / Min Variance optimization

STEP 2 — MAP TO DIX:
Read:
[PASTE: core/contracts/portfolio.py]
[PASTE: intelligence_engine/portfolio/allocator.py — existing]
[PASTE: registry/portfolio_allocator.yaml]

STEP 3 — ADAPT:
Rules:
- All calculations must be deterministic given same inputs
- Accept numpy arrays — no pandas dependency in output
- OFFLINE tier — never in hot path
- Must emit UPDATE_PROPOSED event with new weights, never apply directly
- Add # ADAPTED FROM: PyPortfolioOpt

Output:
1. intelligence_engine/portfolio/risk_parity.py
2. intelligence_engine/portfolio/correlation_engine.py
3. tests/test_portfolio_risk.py
---END REPO PROMPT S-09---


## [S-10] ABIDES — Market Simulation + Order Book
## Priority: S | DIX Gap: simulation/adversarial/ + simulation/crowd_density_sim.py (MISSING)
---REPO PROMPT S-10: ABIDES---
Repo: https://github.com/abides-sim/abides-markets
Target DIX files: simulation/adversarial/flash_crash_synth.py,
                  simulation/crowd_density_sim.py

STEP 1 — RESEARCH:
Fetch and read from ABIDES:
- abides_markets/agents/market_makers/ (market maker behavior)
- abides_markets/agents/noise_agent.py (crowd/noise trader simulation)
- abides_markets/messages/ (order flow)
- abides_core/kernel.py (simulation kernel — extract event loop pattern)

Identify:
- Noise trader crowd density model (keep math)
- Market impact / flash crash triggering conditions
- Order flow simulation patterns

STEP 2 — MAP TO DIX:
Read:
[PASTE: core/contracts/simulation.py]
[PASTE: core/contracts/opponent.py]

STEP 3 — ADAPT:
Rules:
- Extract math only — do not import ABIDES as dependency
- All simulations must accept seed: int — no global random state
- OFFLINE tier only
- Output: DIX SimulationOutcome Pydantic model
- Add # ADAPTED FROM: abides-markets

Output:
1. simulation/crowd_density_sim.py
2. simulation/adversarial/flash_crash_synth.py
3. tests/test_flash_crash_sim.py
---END REPO PROMPT S-10---


# ─────────────────────────────────────────────
# TIER A — HIGH VALUE (after Tier S complete)
# ─────────────────────────────────────────────

## [A-01] Stable-Baselines3 — RL Policy Optimization
## Priority: A | DIX Gap: evolution_engine offline RL training
---REPO PROMPT A-01: stable-baselines3---
Repo: https://github.com/DLR-RM/stable-baselines3
Target DIX file: evolution_engine/rl_trainer.py

STEP 1 — RESEARCH:
Fetch and read from SB3:
- stable_baselines3/common/base_class.py
- stable_baselines3/common/policies.py
- stable_baselines3/ppo/ppo.py

Identify: policy training loop, evaluation logic, checkpoint saving.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/engine.py — OfflineEngine protocol]
[PASTE: evolution_engine/__init__.py]

STEP 3 — ADAPT:
Rules:
- SB3 trains only on historical data — never on live data
- Output: UPDATE_PROPOSED event with new policy weights — never apply directly to runtime
- OFFLINE tier only — training loop never blocks runtime
- Wrap SB3 behind DIX OfflineEngine protocol
- Add # ADAPTED FROM: stable-baselines3

Output:
1. evolution_engine/rl_trainer.py
2. tests/test_rl_trainer.py
---END REPO PROMPT A-01---


## [A-02] Evotorch — Strategy Evolution + Policy Mutation
## Priority: A | DIX Gap: evolution_engine/genetic/ (MISSING)
---REPO PROMPT A-02: evotorch---
Repo: https://github.com/nnaisense/evotorch
Target DIX files: evolution_engine/genetic/mutation_operators.py,
                  evolution_engine/genetic/crossover.py,
                  evolution_engine/genetic/fitness_inheritance.py

STEP 1 — RESEARCH:
Fetch and read from evotorch:
- evotorch/algorithms/ (ES, CMA-ES, PGPE)
- evotorch/core.py (Problem, Solution, Population classes)

Identify: mutation operators, crossover logic, fitness evaluation patterns.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/patch.py]
[PASTE: evolution_engine/update_validator.py if exists]

STEP 3 — ADAPT:
Rules:
- Population must be seeded deterministically
- Mutations produce UPDATE_PROPOSED events — never hot-patch runtime
- OFFLINE tier only
- Add # ADAPTED FROM: evotorch

Output:
1. evolution_engine/genetic/mutation_operators.py
2. evolution_engine/genetic/crossover.py
3. evolution_engine/genetic/fitness_inheritance.py
4. tests/test_genetic_operators.py
---END REPO PROMPT A-02---


## [A-03] DEAP — Evolutionary Strategy Breeding
## Priority: A | DIX Gap: simulation/strategy_arena/ (MISSING)
---REPO PROMPT A-03: DEAP---
Repo: https://github.com/DEAP/deap
Target DIX files: simulation/strategy_arena/arena.py,
                  simulation/strategy_arena/kill_underperformers.py,
                  simulation/strategy_arena/promotion_engine.py

STEP 1 — RESEARCH:
Fetch and read from DEAP:
- deap/algorithms.py (eaSimple, eaMuPlusLambda — tournament selection)
- deap/tools/selection.py (selTournament, selNSGA2)

Identify: tournament selection logic, elitism, population management.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/simulation.py]
[PASTE: docs/promotion_gates.yaml]
[PASTE: registry/trader_archetypes.yaml]

STEP 3 — ADAPT:
Rules:
- Arena runs in OFFLINE tier only
- Killing underperformers must emit STRATEGY_DEMOTED governance event
- Promotion must go through governance approval gate
- Add # ADAPTED FROM: DEAP

Output:
1. simulation/strategy_arena/arena.py
2. simulation/strategy_arena/kill_underperformers.py
3. simulation/strategy_arena/promotion_engine.py
4. tests/test_strategy_arena.py
---END REPO PROMPT A-03---


## [A-04] Nevergrad — Hyperparameter Evolution
## Priority: A | DIX Gap: evolution_engine/pipeline.py (MISSING)
---REPO PROMPT A-04: nevergrad---
Repo: https://github.com/facebookresearch/nevergrad
Target DIX file: evolution_engine/pipeline.py

STEP 1 — RESEARCH:
Fetch and read from nevergrad:
- nevergrad/optimization/base.py (Optimizer base class)
- nevergrad/optimization/optimizerlib.py (DE, PSO, CMA)

Identify: ask/tell interface (Nevergrad's canonical optimization loop).

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/engine.py — OfflineEngine]
[PASTE: core/contracts/patch.py]

STEP 3 — ADAPT:
Rules:
- Use ask/tell pattern — optimizer proposes, evaluator scores, optimizer updates
- OFFLINE only — never blocks runtime
- Output UPDATE_PROPOSED events only
- Add # ADAPTED FROM: nevergrad

Output:
1. evolution_engine/pipeline.py
2. tests/test_evolution_pipeline.py
---END REPO PROMPT A-04---


## [A-05] LangGraph — Cognitive Chat Workflow
## Priority: A | DIX Gap: intelligence_engine/cognitive/chat/ (partial)
---REPO PROMPT A-05: langgraph---
Repo: https://github.com/langchain-ai/langgraph
Target DIX file: intelligence_engine/cognitive/chat/ modules

STEP 1 — RESEARCH:
Fetch and read from LangGraph:
- langgraph/graph/state.py (StateGraph)
- langgraph/prebuilt/tool_node.py
- examples/agent_supervisor.py (multi-agent supervisor)

Identify: state graph pattern, human-in-the-loop nodes, conditional edges.

STEP 2 — MAP TO DIX:
[PASTE: ui/cognitive_chat_runtime.py — existing]
[PASTE: core/contracts/api/cognitive_chat.py]
[PASTE: core/contracts/api/cognitive_chat_approvals.py]

STEP 3 — ADAPT:
Rules:
- LangGraph only controls chat orchestration — never execution
- All tool calls must go through governance approval gate
- Human-in-the-loop nodes must use DIX ApprovalGate contract
- Keep LangGraph's state machine pattern verbatim
- Add # ADAPTED FROM: langgraph

Output:
1. Updated intelligence_engine/cognitive/chat/graph.py (or new file)
2. tests/test_cognitive_chat_langgraph.py
---END REPO PROMPT A-05---


## [A-06] DSPy — Structured AI Reasoning
## Priority: A | DIX Gap: intelligence_engine/cognitive/ reasoning quality
---REPO PROMPT A-06: dspy---
Repo: https://github.com/stanfordnlp/dspy
Target DIX file: intelligence_engine/cognitive/dspy_reasoner.py

STEP 1 — RESEARCH:
Fetch and read from DSPy:
- dspy/predict/predict.py (Predict module)
- dspy/signatures/ (typed signatures)
- dspy/teleprompt/bootstrap_finetune.py (optimizer)

Identify: signature definition pattern, chain-of-thought module, typed inputs/outputs.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/api/cognitive_chat.py]
[PASTE: core/contracts/signal_trust.py]

STEP 3 — ADAPT:
Rules:
- DSPy modules must be OFFLINE tier only for optimization
- Runtime inference must complete within 2s timeout
- Outputs must be typed DIX contracts — never raw strings to execution
- Add # ADAPTED FROM: dspy

Output:
1. intelligence_engine/cognitive/dspy_reasoner.py
2. tests/test_dspy_reasoner.py
---END REPO PROMPT A-06---


## [A-07] PydanticAI — Typed AI Provider Abstraction
## Priority: A | DIX Gap: AI provider layer in cognitive_chat_runtime
---REPO PROMPT A-07: pydantic-ai---
Repo: https://github.com/pydantic/pydantic-ai
Target DIX file: intelligence_engine/cognitive/ai_provider.py

STEP 1 — RESEARCH:
Fetch and read from pydantic-ai:
- pydantic_ai/agent.py (Agent class, model abstraction)
- pydantic_ai/models/ (model provider interfaces)

Identify: how pydantic-ai wraps different providers behind one interface.

STEP 2 — MAP TO DIX:
[PASTE: ui/cognitive_chat_runtime.py — existing AI calls]
[PASTE: core/contracts/api/cognitive_chat.py]

STEP 3 — ADAPT:
Rules:
- All AI provider calls must go through this abstraction
- Must support: OpenAI, Anthropic, Ollama (local fallback)
- Timeout must be enforced — never block indefinitely
- Responses must be typed DIX contracts
- Add # ADAPTED FROM: pydantic-ai

Output:
1. intelligence_engine/cognitive/ai_provider.py
2. tests/test_ai_provider.py
---END REPO PROMPT A-07---


## [A-08] LiteLLM — Unified LLM Gateway
## Priority: A | DIX Gap: AI router abstraction
---REPO PROMPT A-08: litellm---
Repo: https://github.com/BerriAI/litellm
Target DIX file: intelligence_engine/cognitive/ai_router.py

STEP 1 — RESEARCH:
Fetch and read from litellm:
- litellm/main.py (completion function, model routing)
- litellm/router.py (load balancing, failover)

Identify: model routing, fallback chains, cost tracking.

STEP 2 — MAP TO DIX:
[PASTE: intelligence_engine/cognitive/ai_provider.py — if A-07 done]
[PASTE: registry/plugins.yaml — AI model entries]

STEP 3 — ADAPT:
Rules:
- Router must support fallback chain: primary → secondary → local (ollama)
- Cost tracking must write to ledger
- Add # ADAPTED FROM: litellm

Output:
1. intelligence_engine/cognitive/ai_router.py
2. tests/test_ai_router.py
---END REPO PROMPT A-08---


## [A-09] FAISS — Memory Tensor Similarity Search
## Priority: A | DIX Gap: state/memory_tensor/ (MISSING)
---REPO PROMPT A-09: faiss---
Repo: https://github.com/facebookresearch/faiss
Target DIX files: state/memory_tensor/semantic.py,
                  state/memory_tensor/episodic.py

STEP 1 — RESEARCH:
Fetch and read from faiss:
- faiss/python/faiss/__init__.py (IndexFlatL2, IndexIVFFlat)
- demos/demo_auto_tune.py (index building patterns)

Identify: index creation, add vectors, search, serialization.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/trader_intelligence.py — memory contracts]

STEP 3 — ADAPT:
Rules:
- Index must be serializable to disk (for ledger checkpointing)
- OFFLINE tier — indexing never called from hot path
- Runtime lookup (search) is allowed but must be non-blocking
- Add # ADAPTED FROM: faiss

Output:
1. state/memory_tensor/semantic.py
2. state/memory_tensor/episodic.py
3. tests/test_memory_tensor.py
---END REPO PROMPT A-09---


## [A-10] Feast — Feature Store
## Priority: A | DIX Gap: state/feature_store.py (MISSING)
---REPO PROMPT A-10: feast---
Repo: https://github.com/feast-dev/feast
Target DIX file: state/feature_store.py

STEP 1 — RESEARCH:
Fetch and read from feast:
- sdk/python/feast/feature_store.py (FeatureStore class)
- sdk/python/feast/online_store/ (local sqlite online store)

Identify: feature retrieval, online vs offline store, TTL, feature views.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/learning.py]
[PASTE: state/ledger/reader.py]

STEP 3 — ADAPT:
Rules:
- Use SQLite backend only (no Redis/DynamoDB for now)
- Features must be tied to ledger timestamps (reproducible by event_id)
- Add # ADAPTED FROM: feast

Output:
1. state/feature_store.py
2. tests/test_feature_store.py
---END REPO PROMPT A-10---


## [A-11] Polars — High-Performance Replay Analytics
## Priority: A | DIX Gap: learning engine analytics speed
---REPO PROMPT A-11: polars---
Repo: https://github.com/pola-rs/polars
Target DIX: replace pandas in learning_engine/performance_analysis/

STEP 1 — RESEARCH:
Read from polars:
- py-polars/polars/dataframe/frame.py (key API differences from pandas)
- py-polars/polars/lazyframe/ (lazy evaluation — most important for DIX)

Identify: lazy API, streaming scan, groupby patterns.

STEP 2 — MAP TO DIX:
[PASTE: learning_engine/performance_analysis/pnl_attribution.py — if S-05 done]
[PASTE: any existing pandas usage in learning_engine/]

STEP 3 — ADAPT:
Rules:
- Replace pandas with polars lazy API where dataframes are large (>100k rows)
- Keep pandas for small contract-level data (no need to change)
- Must remain deterministic
- Add # ADAPTED FROM: polars lazy API

Output:
1. Updated learning_engine/performance_analysis/pnl_attribution.py (polars version)
2. tests/test_polars_analytics.py
---END REPO PROMPT A-11---


## [A-12] DuckDB — Offline Replay Analytics
## Priority: A | DIX Gap: replay analysis, large-scale ledger queries
---REPO PROMPT A-12: duckdb---
Repo: https://github.com/duckdb/duckdb
Target DIX file: state/ledger/reconstructor.py

STEP 1 — RESEARCH:
Read from duckdb Python API:
- tools/pythonpkg/src/ (core Python API)

Identify: read_parquet, SQL over SQLite, aggregation patterns.

STEP 2 — MAP TO DIX:
[PASTE: state/ledger/reader.py — existing SQLite reader]

STEP 3 — ADAPT:
Rules:
- DuckDB reads ledger for analytics — never writes to ledger
- OFFLINE only — never called from RUNTIME tier
- Add # ADAPTED FROM: duckdb

Output:
1. state/ledger/reconstructor.py
2. tests/test_ledger_reconstructor.py
---END REPO PROMPT A-12---


## [A-13] tsfresh — Automated Feature Extraction
## Priority: A | DIX Gap: learning_engine signal feature mining
---REPO PROMPT A-13: tsfresh---
Repo: https://github.com/blue-yonder/tsfresh
Target DIX file: learning_engine/feature_extractor.py

STEP 1 — RESEARCH:
Fetch from tsfresh:
- tsfresh/feature_extraction/feature_calculators.py (individual calculators)
- tsfresh/feature_extraction/extraction.py (extraction pipeline)

Identify: which feature calculators are most relevant for price/volume time series.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/learning.py]
[PASTE: state/feature_store.py — if A-10 done]

STEP 3 — ADAPT:
Rules:
- Wrap as OFFLINE DIX plugin
- Output features as typed dict mapping to feature_store keys
- Deterministic: same input → same output
- Add # ADAPTED FROM: tsfresh

Output:
1. learning_engine/feature_extractor.py
2. tests/test_feature_extractor.py
---END REPO PROMPT A-13---


## [A-14] OpenTelemetry — Distributed Tracing
## Priority: A | DIX Gap: system observability, latency tracing
---REPO PROMPT A-14: opentelemetry---
Repo: https://github.com/open-telemetry/opentelemetry-python
Target DIX file: system_engine/telemetry.py

STEP 1 — RESEARCH:
Read from opentelemetry-python:
- opentelemetry-api/src/opentelemetry/trace/ (tracer, span)
- opentelemetry-sdk/src/opentelemetry/sdk/trace/ (SDK setup)

Identify: span creation, context propagation, attribute setting.

STEP 2 — MAP TO DIX:
[PASTE: system_engine/engine.py — existing system engine]
[PASTE: core/contracts/events.py — HazardEvent]

STEP 3 — ADAPT:
Rules:
- Telemetry must be async — never block hot path
- Hazard events must always create a span
- Add # ADAPTED FROM: opentelemetry-python

Output:
1. system_engine/telemetry.py
2. tests/test_telemetry.py
---END REPO PROMPT A-14---


## [A-15] Z3 — Governance Invariant Verification
## Priority: A | DIX Gap: governance constraint formal verification
---REPO PROMPT A-15: z3---
Repo: https://github.com/Z3Prover/z3
Target DIX file: governance_engine/verifier.py

STEP 1 — RESEARCH:
Read from z3:
- src/api/python/z3/ (z3.py — Python API)
- examples/python/ (solver usage examples)

Identify: how to encode constraints as SMT formulas, satisfiability checking.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/governance.py — governance invariants]
[PASTE: immutable_core/axioms.py]

STEP 3 — ADAPT:
Rules:
- Z3 runs in CI and offline governance checks — never in hot path
- Each governance invariant must have a corresponding Z3 formula
- Verification failure must raise GovernanceViolation with specific invariant ID
- Add # ADAPTED FROM: z3

Output:
1. governance_engine/verifier.py
2. tests/test_governance_verifier.py
---END REPO PROMPT A-15---


## [A-16] Prometheus Python Client — Metrics Export
## Priority: A | DIX Gap: operator dashboard live metrics
---REPO PROMPT A-16: prometheus---
Repo: https://github.com/prometheus/client_python
Target DIX file: system_engine/metrics.py

STEP 1 — RESEARCH:
Read from prometheus_client:
- prometheus_client/metrics.py (Counter, Gauge, Histogram)
- prometheus_client/exposition.py (HTTP exposition)

Identify: metric types, label usage, exposition format.

STEP 2 — MAP TO DIX:
[PASTE: system_engine/engine.py]
[PASTE: core/contracts/events.py — HazardEvent for alerting]

STEP 3 — ADAPT:
Rules:
- Metrics must be labeled by engine_id and tier
- HazardEvent always increments hazard_count counter
- Exposition endpoint mounts on existing FastAPI server
- Add # ADAPTED FROM: prometheus/client_python

Output:
1. system_engine/metrics.py
2. tests/test_metrics.py
---END REPO PROMPT A-16---


## [A-17] OPA — Policy Enforcement
## Priority: A | DIX Gap: governance_engine policy runtime
---REPO PROMPT A-17: opa---
Repo: https://github.com/open-policy-agent/opa
Concept: extract Rego policy pattern — implement equivalent in Python

STEP 1 — RESEARCH:
Read from OPA:
- docs/docs/policy-language/ (Rego — policy-as-code pattern)
- rego/rego.go (query evaluation)

Identify: how OPA evaluates policy rules, how inputs map to decisions.

STEP 2 — MAP TO DIX:
[PASTE: governance_engine/control_plane/compliance_validator.py — existing]
[PASTE: core/contracts/governance.py]

STEP 3 — ADAPT:
Rules:
- Implement OPA-style policy evaluation in Python (no Go dependency)
- Policies defined in registry/enforcement_policies.yaml
- Policy evaluation runs in RUNTIME governance tier — must be fast (<1ms)
- Policy violations emit HazardEvent
- Add # ADAPTED FROM: opa policy evaluation pattern

Output:
1. governance_engine/policy_evaluator.py
2. tests/test_policy_evaluator.py
---END REPO PROMPT A-17---


## [A-18] cryptofeed — Institutional Market Data Feeds
## Priority: A | DIX Gap: execution_engine/market_data/ (MISSING)
---REPO PROMPT A-18: cryptofeed---
Repo: https://github.com/bmoscon/cryptofeed
Target DIX files: execution_engine/market_data/normalizer.py,
                  execution_engine/market_data/book_builder.py

STEP 1 — RESEARCH:
Fetch and read from cryptofeed:
- cryptofeed/exchanges/ (exchange websocket handlers)
- cryptofeed/types.py (Trade, OrderBook, Ticker types)
- cryptofeed/backends/ (data routing)

Identify: orderbook update logic, trade normalization, connection management.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/market.py]
[PASTE: ui/feeds/binance_public_ws.py — existing DIX feed]

STEP 3 — ADAPT:
Rules:
- Wrap behind DIX feed interface
- Never import cryptofeed in hot path
- Book updates must be timestamped with TimeSource
- Add # ADAPTED FROM: cryptofeed

Output:
1. execution_engine/market_data/normalizer.py
2. execution_engine/market_data/book_builder.py
3. tests/test_market_data.py
---END REPO PROMPT A-18---


## [A-19] Scrapy — News Ingestion Pipeline
## Priority: A | DIX Gap: sensory/ news ingestion at scale
---REPO PROMPT A-19: scrapy---
Repo: https://github.com/scrapy/scrapy
Target DIX file: sensory/news_ingestion_pipeline.py

STEP 1 — RESEARCH:
Read from scrapy:
- scrapy/spiders/__init__.py (Spider base)
- scrapy/pipelines/ (item pipeline)
- scrapy/downloadermiddlewares/retry.py (retry logic)

Identify: spider lifecycle, item pipeline, retry/rate-limit middleware.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/news.py]
[PASTE: ui/feeds/news_runner.py — existing]

STEP 3 — ADAPT:
Rules:
- Sandbox: scrapy runs in isolated process — never in RUNTIME tier
- Output: NewsItem Pydantic model piped to news_fanout
- Add # ADAPTED FROM: scrapy

Output:
1. sensory/news_ingestion_pipeline.py
2. tests/test_news_ingestion.py
---END REPO PROMPT A-19---


## [A-20] Freqtrade — Exchange Adapter Patterns + Paper Trading
## Priority: A | DIX Gap: paper adapter robustness + exchange patterns
---REPO PROMPT A-20: freqtrade---
Repo: https://github.com/freqtrade/freqtrade
Target DIX files: execution_engine/adapters/paper.py (harden existing)

STEP 1 — RESEARCH:
Fetch and read from freqtrade:
- freqtrade/exchange/exchange.py (error handling, rate limits, retry)
- freqtrade/exchange/common.py (retrier decorator)
- freqtrade/persistence/models.py (trade state tracking)

Identify:
- Retrier pattern (exponential backoff with jitter)
- Exchange error classification (recoverable vs fatal)
- Paper trading fill simulation

STEP 2 — MAP TO DIX:
[PASTE: execution_engine/adapters/paper.py — existing]
[PASTE: execution_engine/adapters/base.py]

STEP 3 — ADAPT:
Rules:
- Extract retrier logic verbatim — apply to all DIX exchange adapters
- Error classification must trigger appropriate HazardEvent severity
- Add # ADAPTED FROM: freqtrade/exchange/exchange.py

Output:
1. execution_engine/adapters/_retry_mixin.py (new shared mixin)
2. execution_engine/adapters/paper.py (updated with better fill simulation)
3. tests/test_retry_mixin.py
---END REPO PROMPT A-20---


# ─────────────────────────────────────────────
# TIER B — FUTURE WAVES (after Tier A complete)
# ─────────────────────────────────────────────

## [B-01] Norse — Spiking Neural Networks for Anomaly Detection
## Priority: B | DIX Gap: sensory/neuromorphic/ (MISSING, future phase)
---REPO PROMPT B-01: norse---
Repo: https://github.com/norse/norse
Target DIX file: sensory/neuromorphic/indira_signal.py

STEP 1 — RESEARCH:
Fetch and read from norse:
- norse/torch/functional/lif.py (Leaky Integrate-and-Fire neuron)
- norse/torch/module/lif.py (LIF module)
- examples/ (pattern detection examples)

Identify: LIF neuron dynamics, spike encoding of continuous signals, temporal patterns.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/events.py — SignalEvent]
[PASTE: system_engine/hazard_sensors/ — for comparison pattern]

STEP 3 — ADAPT:
Rules:
- SNN runs in OFFLINE tier — output is spike-encoded signal strength
- Spike events translate to DIX SignalEvent with snn_source tag
- Deterministic: fixed seed for initialization
- Add # ADAPTED FROM: norse

Output:
1. sensory/neuromorphic/indira_signal.py
2. tests/test_neuromorphic_signal.py
---END REPO PROMPT B-01---


## [B-02] BindsNET — Spiking Network Learning
## Priority: B | DIX Gap: sensory/neuromorphic/ anomaly learning
---REPO PROMPT B-02: bindsnet---
Repo: https://github.com/BindsNET/bindsnet
Target DIX file: sensory/neuromorphic/dyon_anomaly.py

STEP 1 — RESEARCH:
Fetch and read from bindsnet:
- bindsnet/network/ (Network class, topology)
- bindsnet/learning/ (STDP, Hebbian learning)
- examples/mnist/ (unsupervised pattern learning)

Identify: STDP learning rule, anomaly detection via spike rate deviation.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/events.py — HazardEvent]

STEP 3 — ADAPT:
Rules:
- OFFLINE learning only — spike patterns trained offline
- Runtime inference (anomaly scoring) allowed in RUNTIME system tier
- Score threshold triggers HazardEvent
- Add # ADAPTED FROM: bindsnet

Output:
1. sensory/neuromorphic/dyon_anomaly.py
2. tests/test_dyon_anomaly.py
---END REPO PROMPT B-02---


## [B-03] Ray — Distributed Simulation + Training
## Priority: B | DIX Gap: simulation/parallel_runner.py + evolution distributed training
---REPO PROMPT B-03: ray---
Repo: https://github.com/ray-project/ray
Target DIX file: simulation/parallel_runner.py

STEP 1 — RESEARCH:
Fetch and read from ray:
- python/ray/remote_function.py (@ray.remote decorator)
- rllib/env/multi_agent_env.py (multi-agent parallel rollouts)

Identify: @ray.remote pattern, parallel map, result gathering.

STEP 2 — MAP TO DIX:
[PASTE: simulation/engine.py — if S-03 done]
[PASTE: core/contracts/simulation.py]

STEP 3 — ADAPT:
Rules:
- Ray only used for OFFLINE simulation — never in RUNTIME tier
- Each parallel simulation must be fully isolated (no shared state)
- Results gathered as list of SimulationOutcome
- Add # ADAPTED FROM: ray

Output:
1. simulation/parallel_runner.py
2. tests/test_parallel_runner.py
---END REPO PROMPT B-03---


## [B-04] Flower — Federated Learning
## Priority: B | DIX Gap: future multi-node DIX learning
---REPO PROMPT B-04: flower---
Repo: https://github.com/adap/flower
Target DIX file: learning_engine/federated_coordinator.py

STEP 1 — RESEARCH:
Fetch and read from flower:
- src/py/flwr/server/strategy/fedavg.py (FedAvg aggregation)
- src/py/flwr/client/client.py (client interface)

Identify: FedAvg weight aggregation math, client/server protocol.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/engine.py — OfflineEngine]
[PASTE: learning_engine/slow_loop_learner.py]

STEP 3 — ADAPT:
Rules:
- Federated coordinator is OFFLINE only
- Each node contributes UPDATE_PROPOSED — coordinator aggregates
- Privacy: no raw data leaves node — gradients only
- Add # ADAPTED FROM: flower FedAvg

Output:
1. learning_engine/federated_coordinator.py
2. tests/test_federated_coordinator.py
---END REPO PROMPT B-04---


## [B-05] Neo4j — Strategy Knowledge Graph
## Priority: B | DIX Gap: state knowledge graph (future phase)
---REPO PROMPT B-05: neo4j---
Repo: https://github.com/neo4j/neo4j-python-driver
Target DIX file: state/knowledge_store.py

STEP 1 — RESEARCH:
Fetch from neo4j-python-driver:
- neo4j/sync/session.py (session, run query)
- neo4j/work/result.py (result handling)

Identify: Cypher query pattern, relationship creation, graph traversal.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/trader_intelligence.py]
[PASTE: core/contracts/strategy_registry.py]

STEP 3 — ADAPT:
Rules:
- Graph stores strategy lineage, signal ancestry, trader influence maps
- OFFLINE read/write — never in hot path
- Falls back to in-memory NetworkX if Neo4j unavailable
- Add # ADAPTED FROM: neo4j-python-driver

Output:
1. state/knowledge_store.py
2. tests/test_knowledge_store.py
---END REPO PROMPT B-05---


## [B-06] Bytewax — Streaming Signal Pipeline
## Priority: B | DIX Gap: continuous signal processing
---REPO PROMPT B-06: bytewax---
Repo: https://github.com/bytewax/bytewax
Target DIX file: sensory/streaming_pipeline.py

STEP 1 — RESEARCH:
Fetch and read from bytewax:
- pysrc/bytewax/dataflow.py (Dataflow class)
- pysrc/bytewax/operators/ (map, filter, window operators)

Identify: stateful operator pattern, windowing, output routing.

STEP 2 — MAP TO DIX:
[PASTE: ui/feeds/runner.py — existing feed runner]
[PASTE: core/contracts/events.py — SignalEvent]

STEP 3 — ADAPT:
Rules:
- Bytewax pipeline runs as separate process — feeds into DIX via queue
- Never imports from RUNTIME tier
- Outputs SignalEvent structs to multiprocessing queue
- Add # ADAPTED FROM: bytewax

Output:
1. sensory/streaming_pipeline.py
2. tests/test_streaming_pipeline.py
---END REPO PROMPT B-06---


## [B-07] spaCy — News Entity Extraction
## Priority: B | DIX Gap: sensory news NLP processing
---REPO PROMPT B-07: spacy---
Repo: https://github.com/explosion/spaCy
Target DIX file: sensory/news_entity_extractor.py

STEP 1 — RESEARCH:
Read from spaCy:
- spacy/pipeline/ner.py (NER pipeline)
- spacy/tokens/doc.py (Doc, Span, Token)

Identify: entity extraction pipeline, custom entity rules.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/news.py]

STEP 3 — ADAPT:
Rules:
- Runs in OFFLINE sensory tier
- Extract: ORG (companies), MONEY (prices), GPE (geopolitics), DATE
- Output tagged NewsItem with entities list
- Add # ADAPTED FROM: spaCy

Output:
1. sensory/news_entity_extractor.py
2. tests/test_news_entity_extractor.py
---END REPO PROMPT B-07---


## [B-08] vLLM — Local Model Inference Fallback
## Priority: B | DIX Gap: offline/emergency AI inference
---REPO PROMPT B-08: vllm---
Repo: https://github.com/vllm-project/vllm
Target DIX file: intelligence_engine/cognitive/local_model_provider.py

STEP 1 — RESEARCH:
Fetch from vllm:
- vllm/engine/async_llm_engine.py (async engine)
- vllm/entrypoints/openai/api_server.py (OpenAI-compatible server)

Identify: how vLLM exposes OpenAI-compatible endpoint.

STEP 2 — MAP TO DIX:
[PASTE: intelligence_engine/cognitive/ai_router.py — if A-08 done]

STEP 3 — ADAPT:
Rules:
- Local model is fallback only — not primary
- Must be OpenAI-compatible (drop-in for primary provider)
- Add # ADAPTED FROM: vllm

Output:
1. intelligence_engine/cognitive/local_model_provider.py
2. tests/test_local_model_provider.py
---END REPO PROMPT B-08---


## [B-09] CrossHair — Property-Based Contract Testing
## Priority: B | DIX Gap: governance invariant symbolic testing
---REPO PROMPT B-09: crosshair---
Repo: https://github.com/pschanely/CrossHair
Target DIX: CI invariant checks (no new module — enhances existing)

STEP 1 — RESEARCH:
Read from crosshair:
- crosshair/core.py (symbolic execution)
- crosshair/contract_checks.py (pre/post condition patterns)

Identify: how to annotate Python functions with contracts for symbolic checking.

STEP 2 — MAP TO DIX:
[PASTE: immutable_core/axioms.py]
[PASTE: tools/authority_lint.py — existing lint rules]

STEP 3 — ADAPT:
Rules:
- Add CrossHair-compatible contracts to immutable_core axioms
- CrossHair runs in CI only — never at runtime
- Add # ADAPTED FROM: crosshair

Output:
1. Updated immutable_core/axioms.py with CrossHair contracts
2. .github/workflows/crosshair.yml CI job
---END REPO PROMPT B-09---


## [B-10] Playwright — Sandboxed Web Automation
## Priority: B | DIX Gap: web_autolearn isolated browser
---REPO PROMPT B-10: playwright---
Repo: https://github.com/microsoft/playwright-python
Target DIX file: sensory/web_autolearn/sandbox_browser.py

STEP 1 — RESEARCH:
Read from playwright-python:
- playwright/async_api/_context_manager.py
- playwright/async_api/_generated.py (Page, BrowserContext)

Identify: context isolation, page.goto timeout, content extraction.

STEP 2 — MAP TO DIX:
[PASTE: sensory/web_autolearn/crawler.py]

STEP 3 — ADAPT:
Rules:
- Each crawl runs in isolated BrowserContext — no cookie sharing between crawls
- Hard timeout: 10s per page — never blocks indefinitely
- Output: raw HTML only — pass to crawler for extraction
- Subprocess only — never in RUNTIME process
- Add # ADAPTED FROM: playwright-python

Output:
1. sensory/web_autolearn/sandbox_browser.py
2. tests/test_sandbox_browser.py
---END REPO PROMPT B-10---


## [B-11] Helius SDK — Solana Onchain Data
## Priority: B | DIX Gap: memecoin subsystem onchain intelligence
---REPO PROMPT B-11: helius-sdk---
Repo: https://github.com/helius-labs/helius-sdk (TypeScript)
Target DIX file: ui/feeds/helius_ws.py (new feed)

STEP 1 — RESEARCH:
Fetch from helius-sdk TypeScript source. Read:
- src/types/ (transaction types, account types)
- src/utils/webhooks.ts (webhook patterns)

Identify: enhanced transaction parsing, wallet tracking, token metadata.

STEP 2 — MAP TO DIX:
[PASTE: ui/feeds/pumpfun_ws.py — existing onchain feed pattern]
[PASTE: core/contracts/events.py]

STEP 3 — ADAPT (in Python using httpx/websockets — no TS):
Rules:
- Implement Helius RPC + websocket client in Python
- Mirror pumpfun_ws.py pattern exactly
- Output parsed events to existing news_fanout
- Add # ADAPTED FROM: helius-sdk webhook patterns

Output:
1. ui/feeds/helius_ws.py
2. tests/test_helius_ws.py
---END REPO PROMPT B-11---


## [B-12] HashiCorp Vault — Secrets Management
## Priority: B | DIX Gap: system_engine credentials hardening
---REPO PROMPT B-12: vault---
Repo: https://github.com/hashicorp/vault
Python client: https://github.com/hvac/hvac
Target DIX file: system_engine/credentials/vault_backend.py

STEP 1 — RESEARCH:
Read from hvac (Python Vault client):
- hvac/api/secrets_engines/kv_v2.py (read_secret, create_or_update_secret)
- hvac/adapters.py (HTTP adapter)

Identify: secret read/write, token renewal, connection pooling.

STEP 2 — MAP TO DIX:
[PASTE: system_engine/credentials/dotenv_io.py — existing]
[PASTE: core/contracts/api/credentials.py]

STEP 3 — ADAPT:
Rules:
- Vault is optional backend — fallback to dotenv if Vault unavailable
- Credentials never logged or emitted to ledger
- Add # ADAPTED FROM: hvac Vault client

Output:
1. system_engine/credentials/vault_backend.py
2. tests/test_vault_backend.py
---END REPO PROMPT B-12---


## [B-13] Qdrant — Semantic Vector Store
## Priority: B | DIX Gap: state/memory_tensor (alternative to FAISS for persistence)
---REPO PROMPT B-13: qdrant---
Repo: https://github.com/qdrant/qdrant-client
Target DIX file: state/memory_tensor/vector_store.py

STEP 1 — RESEARCH:
Read from qdrant-client:
- qdrant_client/qdrant_client.py (upsert, search, collections)
- qdrant_client/models/ (PointStruct, SearchRequest)

Identify: collection creation, vector upsert, similarity search, filtering.

STEP 2 — MAP TO DIX:
[PASTE: state/memory_tensor/semantic.py — if A-09 done (FAISS)]

STEP 3 — ADAPT:
Rules:
- Abstract behind VectorStoreBase interface
- FAISS for offline/embedded, Qdrant for persistent/multi-node
- Add # ADAPTED FROM: qdrant-client

Output:
1. state/memory_tensor/vector_store.py (abstract base + both backends)
2. tests/test_vector_store.py
---END REPO PROMPT B-13---


## [B-14] MLflow — Experiment Tracking
## Priority: B | DIX Gap: evolution_engine experiment governance
---REPO PROMPT B-14: mlflow---
Repo: https://github.com/mlflow/mlflow
Target DIX file: evolution_engine/experiment_tracker.py

STEP 1 — RESEARCH:
Read from mlflow:
- mlflow/tracking/client.py (MlflowClient)
- mlflow/entities/ (Run, Metric, Param)

Identify: run creation, metric logging, model registry.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/patch.py]
[PASTE: evolution_engine/pipeline.py — if A-04 done]

STEP 3 — ADAPT:
Rules:
- Each evolution run creates MLflow run with governance metadata
- Model registry gated by governance approval
- OFFLINE only
- Add # ADAPTED FROM: mlflow

Output:
1. evolution_engine/experiment_tracker.py
2. tests/test_experiment_tracker.py
---END REPO PROMPT B-14---


## [B-15] vectorbt — Vectorized Strategy Research
## Priority: B | DIX Gap: simulation/backtester.py (MISSING)
---REPO PROMPT B-15: vectorbt---
Repo: https://github.com/polakowo/vectorbt
Target DIX file: simulation/backtester.py

STEP 1 — RESEARCH:
Fetch from vectorbt:
- vectorbt/portfolio/base.py (Portfolio class, from_signals)
- vectorbt/returns/accessors.py (Sharpe, Drawdown, Calmar)

Identify: signal-to-portfolio pipeline, performance metric calculations.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/backtest_result.py]
[PASTE: core/contracts/simulation.py]

STEP 3 — ADAPT:
Rules:
- Extract metric calculation math — do not use vectorbt Portfolio class directly
- Output DIX BacktestResult Pydantic model
- OFFLINE only
- Add # ADAPTED FROM: vectorbt

Output:
1. simulation/backtester.py
2. tests/test_backtester.py
---END REPO PROMPT B-15---


## [B-16] CleanRL — Single-File RL Implementations
## Priority: B | DIX Gap: evolution_engine clean RL baselines
---REPO PROMPT B-16: cleanrl---
Repo: https://github.com/vwxyzjn/cleanrl
Target DIX file: evolution_engine/rl_algorithms/ppo.py

STEP 1 — RESEARCH:
Fetch and read from cleanrl:
- cleanrl/ppo.py (single-file PPO — the whole thing)
- cleanrl/sac_continuous_action.py

Identify: the minimal PPO implementation — training loop, advantage estimation, policy update.

STEP 2 — MAP TO DIX:
[PASTE: evolution_engine/rl_trainer.py — if A-01 done]

STEP 3 — ADAPT:
Rules:
- Keep CleanRL's clean minimal implementation — do not abstract away
- Replace gym environment with DIX SimulationEngine
- OFFLINE tier only
- Deterministic: accept seed
- Add # ADAPTED FROM: cleanrl/ppo.py

Output:
1. evolution_engine/rl_algorithms/ppo.py
2. tests/test_ppo_algorithm.py
---END REPO PROMPT B-16---


## [B-17] Semantic Kernel — Reflection + Planning Loops
## Priority: B | DIX Gap: intelligence_engine cognitive reflection
---REPO PROMPT B-17: semantic-kernel---
Repo: https://github.com/microsoft/semantic-kernel
Target DIX file: intelligence_engine/cognitive/reflection_loop.py

STEP 1 — RESEARCH:
Read from semantic-kernel Python SDK:
- python/semantic_kernel/planners/ (planner patterns)
- python/semantic_kernel/memory/ (memory interface)

Identify: plan-execute-reflect pattern, memory retrieval pattern.

STEP 2 — MAP TO DIX:
[PASTE: intelligence_engine/cognitive/ai_provider.py — if A-07 done]

STEP 3 — ADAPT:
Rules:
- Reflection runs OFFLINE — output is UPDATE_PROPOSED
- Never reflects live execution decisions
- Add # ADAPTED FROM: semantic-kernel

Output:
1. intelligence_engine/cognitive/reflection_loop.py
2. tests/test_reflection_loop.py
---END REPO PROMPT B-17---


## [B-18] Dagster — Offline Pipeline Orchestration
## Priority: B | DIX Gap: learning_engine pipeline scheduling
---REPO PROMPT B-18: dagster---
Repo: https://github.com/dagster-io/dagster
Target DIX file: learning_engine/pipeline_orchestrator.py

STEP 1 — RESEARCH:
Read from dagster:
- python_modules/dagster/dagster/_core/definitions/job_definition.py
- python_modules/dagster/dagster/_core/definitions/asset.py

Identify: asset definition pattern, job scheduling, lineage tracking.

STEP 2 — MAP TO DIX:
[PASTE: learning_engine/slow_loop_learner.py]
[PASTE: evolution_engine/pipeline.py — if A-04 done]

STEP 3 — ADAPT:
Rules:
- Dagster orchestrates OFFLINE pipeline jobs only
- Never touches RUNTIME tier
- Add # ADAPTED FROM: dagster

Output:
1. learning_engine/pipeline_orchestrator.py
2. tests/test_pipeline_orchestrator.py
---END REPO PROMPT B-18---


## [B-19] Great Expectations — Data Quality Gates
## Priority: B | DIX Gap: sensory data validation
---REPO PROMPT B-19: great-expectations---
Repo: https://github.com/great-expectations/great_expectations
Target DIX file: sensory/data_quality_gate.py

STEP 1 — RESEARCH:
Read from great_expectations:
- great_expectations/core/expectation_suite.py
- great_expectations/expectations/core/ (column value expectations)

Identify: expectation definition, validation result, suite execution.

STEP 2 — MAP TO DIX:
[PASTE: core/contracts/news.py]
[PASTE: core/contracts/market.py]

STEP 3 — ADAPT:
Rules:
- Validation gate runs on ingested data before it enters the bus
- Validation failure emits HazardEvent — never silently drops
- Add # ADAPTED FROM: great-expectations

Output:
1. sensory/data_quality_gate.py
2. tests/test_data_quality_gate.py
---END REPO PROMPT B-19---


## [B-20] PyO3 — Rust Acceleration Bridge
## Priority: B | DIX Gap: future FastRiskCache Rust port
---REPO PROMPT B-20: pyo3---
Repo: https://github.com/PyO3/pyo3
Target: scripts/rust_bridge_template/ (template only — no live code yet)

STEP 1 — RESEARCH:
Read from pyo3:
- guide/src/class.md (Python class from Rust)
- guide/src/function.md (Python function from Rust)
- examples/word-count/

Identify: how to expose a Rust struct as a Python class, GIL handling.

STEP 2 — MAP TO DIX:
[PASTE: execution_engine/hot_path/__init__.py]

STEP 3 — PRODUCE:
Output a Rust template for the FastRiskCache hot path acceleration:
- Rust struct with same interface as Python FastRiskCache
- PyO3 bindings
- Cargo.toml
- README explaining how to compile and drop in as replacement
- Add # ADAPTED FROM: pyo3 examples

Output:
1. scripts/rust_bridge/src/lib.rs
2. scripts/rust_bridge/Cargo.toml
3. scripts/rust_bridge/README.md
---END REPO PROMPT B-20---


# ─────────────────────────────────────────────
# TIER C — RESEARCH ONLY (concept extraction)
# These are studied for patterns, not directly integrated yet
# ─────────────────────────────────────────────

## [C-01] LMAX Disruptor — Event Bus Architecture
---REPO PROMPT C-01: LMAX-disruptor---
Repo: https://github.com/LMAX-Exchange/disruptor
Java source — extract architectural concepts only

Read: src/main/java/com/lmax/disruptor/RingBuffer.java
      src/main/java/com/lmax/disruptor/EventProcessor.java

Produce a design document (not code) describing:
1. How the ring buffer eliminates lock contention
2. How sequence barriers enable dependency tracking
3. How this pattern could be applied to DIX's per-tick canonical bus
4. What the Python equivalent would be (asyncio.Queue vs multiprocessing)
5. Whether DIX's current bus in system_engine is a bottleneck this would solve

Output: docs/architecture/disruptor_analysis.md
---END REPO PROMPT C-01---


## [C-02] TLA+ — Governance State Machine Proofs
---REPO PROMPT C-02: tlaplus---
Repo: https://github.com/tlaplus/tlaplus
Read TLA+ specifications in: examples/

Produce:
A TLA+ specification for DIX's governance mode state machine:
- States: SHADOW → PAPER → SEMI_AUTO → AUTO → LOCKED
- Transitions and their guards
- Safety property: can never jump from SHADOW to AUTO directly
- Liveness property: system eventually reaches PAPER given valid config

Output: docs/formal/governance_state_machine.tla
---END REPO PROMPT C-02---


## [C-03] Aeron — Ultra-Low-Latency Messaging
---REPO PROMPT C-03: aeron---
Repo: https://github.com/real-logic/aeron
Java source — architecture study only

Read: aeron-driver/src/main/java/io/aeron/driver/
      aeron-client/src/main/java/io/aeron/

Produce a design document:
1. Aeron's IPC transport (same-machine zero-copy)
2. How exclusive publications eliminate contention
3. How flow control works without locks
4. Recommendation: at what DIX scale (messages/second) would Aeron be worth adopting
5. What the migration path from current asyncio bus would look like

Output: docs/architecture/aeron_analysis.md
---END REPO PROMPT C-03---


## [C-04] Chronicle Queue — Persistent Ring Buffer
---REPO PROMPT C-04: chronicle-queue---
Repo: https://github.com/OpenHFT/Chronicle-Queue

Read: src/main/java/net/openhft/chronicle/queue/

Produce a design document:
1. How Chronicle Queue achieves microsecond persistence
2. How roll-files work (daily/hourly rotation)
3. How tailers replay from any position
4. Comparison to DIX's current SQLite ledger for latency-sensitive writes
5. Python equivalent options (mmap-based write, asyncio file)

Output: docs/architecture/chronicle_queue_analysis.md
---END REPO PROMPT C-04---


## [C-05] Temporal — Deterministic Workflow Engine
---REPO PROMPT C-05: temporal---
Repo: https://github.com/temporalio/temporal
Read: service/worker/workflow/

Produce a design document:
1. How Temporal achieves deterministic workflow replay
2. How it handles side effects (activities vs workflow code)
3. How sagas work for multi-step compensating transactions
4. How DIX's patch_pipeline could use Temporal's saga pattern
5. Whether DIX's current governance workflow needs this level of reliability

Output: docs/architecture/temporal_analysis.md
---END REPO PROMPT C-05---


## [C-06] Akka / Proto.Actor — Actor Model for Event Sourcing
---REPO PROMPT C-06: actor-model---
Repo: https://github.com/AkkaNetContrib/Akka.Persistence (concept reference)

Produce a design document:
1. Actor model fundamentals (message passing, no shared state)
2. How persistent actors reconstruct state from event log
3. How this maps to DIX's engine isolation model
4. Whether DIX's current multiprocessing separation already implements this
5. What gaps remain and whether adopting an actor framework would help

Output: docs/architecture/actor_model_analysis.md
---END REPO PROMPT C-06---


## [C-07] FinRL — Finance RL Environments
---REPO PROMPT C-07: finrl---
Repo: https://github.com/AI4Finance-Foundation/FinRL
Read: finrl/meta/env_stock_trading/

Produce:
1. Analysis of FinRL's gym environment structure for stock trading
2. Mapping of FinRL state space to DIX SignalEvent + ExecutionEvent
3. Mapping of FinRL action space to DIX ExecutionIntent
4. Template for wrapping DIX's SimulationEngine as a gym.Env
5. Warning list: what FinRL assumes that violates DIX authority rules

Output: docs/architecture/finrl_gym_mapping.md
---END REPO PROMPT C-07---


## [C-08] MetaGPT — Multi-Agent Software Engineering
---REPO PROMPT C-08: metagpt---
Repo: https://github.com/geekan/MetaGPT
Read: metagpt/roles/

Produce:
1. Analysis of MetaGPT's role separation (Product Manager, Architect, Engineer)
2. How DIX's Indira/Dyon dual-charter maps to MetaGPT roles
3. How MetaGPT's structured output pattern could improve DIX cognitive chat
4. Warning: what MetaGPT assumptions conflict with DIX authority rules
5. Recommendation: which MetaGPT patterns to borrow vs avoid

Output: docs/architecture/metagpt_analysis.md
---END REPO PROMPT C-08---


# =========================================================
# PART 3 — VALIDATORS TO RUN AFTER EVERY SESSION
# Run these commands after each adapted file is generated
# =========================================================

---VALIDATION CHECKLIST (run after every session)---

# 1. Authority lint (catches tier violations)
python tools/authority_lint.py --strict .

# 2. Run the specific test just generated
pytest tests/test_[new_module].py -v

# 3. Full test suite (confirm nothing broken)
pytest --tb=short -q

# 4. Total validation
python tools/total_validation.py

# 5. Check for new imports that need requirements.txt
grep -r "^import \|^from " [new_file].py | grep -v "^from core\|^from execution\|^from learning\|^from governance\|^from intelligence\|^from system\|^from state\|^from sensory\|^from evolution"

# If any validation FAILS:
# Paste the exact error back to AI with:
# "Fix this violation without changing the [repo] core logic. Only adjust the DIX wrapper layer."

---END VALIDATION CHECKLIST---


# =========================================================
# PART 4 — SESSION LOG TEMPLATE
# Fill this in after each completed session
# =========================================================

---SESSION LOG---
| # | Prompt ID | DIX File Created | Source Repo | Lint Pass | Tests Pass | Date |
|---|---|---|---|---|---|---|
| 1 | S-01 | execution_engine/adapters/binance.py | ccxt | | | |
| 2 | S-02 | simulation/slippage_model.py | hftbacktest | | | |
---END SESSION LOG---
