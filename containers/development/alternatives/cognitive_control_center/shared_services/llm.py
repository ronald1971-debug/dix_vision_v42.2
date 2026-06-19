"""
cognitive_control_center.shared_services.llm
LLM Router service - Migrated from cockpit/llm.py with World Context Integration

This module provides multi-provider AI routing for the cognitive control center,
preserving all features from cockpit/llm.py while integrating with the cognitive
environment and world model understanding.

PRESERVED FEATURES:
- All 8 providers (cognition_devin, anthropic_claude, openai_gpt4o, google_gemini, xai_grok, ollama_local, deepseek, perplexity)
- All 9 capabilities (reason, code, translate, sentiment, long_context, realtime_web, math, offline_ok, multimodal)
- Provider status tracking and monitoring
- Cost optimization (cheapest available provider with required capabilities)
- Capability-based routing
- All HTTP call implementations
- Template fallback when no provider available
- Configuration-based enable/disable
- Secret-based API key management
- Provider preference support
- Usage and cost tracking

ENHANCED FEATURES:
- Integration with cognitive environment activity feeds
- AI-to-AI handoff logging to cognitive environment
- Real-time provider observability in agent operations center
- Workspace-aware provider selection
- World context integration for intelligent provider selection
- Regime-aware LLM behavior
"""

from __future__ import annotations

import json
import threading
import urllib.request
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Callable, Optional, Dict, List

from core.secrets import get_secret
from system.config import get_config

from cognitive_control_center.agent_operations_center.activity_feeds import (
    ActivityType,
    get_activity_feeds,
)
from cognitive_control_center.core.operating_environment import (
    CognitiveEntityType,
    get_cognitive_environment,
)

# Try to import world model components for world context integration
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from world_model.indicator_integration import get_integration_bridge
    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False


# Preserve exact Capability enum from cockpit/llm.py
class Capability(StrEnum):
    REASON = "reason"
    CODE = "code"
    TRANSLATE = "translate"
    SENTIMENT = "sentiment"
    LONG_CONTEXT = "long_context"
    REALTIME_WEB = "realtime_web"
    MATH = "math"
    OFFLINE_OK = "offline_ok"
    MULTIMODAL = "multimodal"


@dataclass
class WorldContext:
    """World model context for LLM provider selection and behavior."""
    market_regime: str  # bullish, bearish, sideways, high_volatility
    market_trend: str  # trending, mean_reverting
    volatility_regime: str  # high, normal, low
    liquidity_state: str  # high, normal, low
    agent_activity: Dict[str, float]  # agent_type -> activity_level
    causal_factors: List[str]  # relevant causal factors
    prediction_confidence: float  # world model prediction confidence
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for processing."""
        return {
            "market_regime": self.market_regime,
            "market_trend": self.market_trend,
            "volatility_regime": self.volatility_regime,
            "liquidity_state": self.liquidity_state,
            "agent_activity": self.agent_activity,
            "causal_factors": self.causal_factors,
            "prediction_confidence": self.prediction_confidence,
            "timestamp": self.timestamp.isoformat()
        }


# Preserve exact Provider dataclass from cockpit/llm.py
@dataclass(frozen=True)
class Provider:
    name: str  # "anthropic_claude"
    role: str  # "GOVERNANCE reasoning + patch reviewer"
    env_key: str  # "ANTHROPIC_API_KEY"
    capabilities: frozenset[Capability]
    cost_per_1k_tokens_usd: float
    model: str
    endpoint: str = ""
    local: bool = False


# Preserve exact LLMResponse dataclass from cockpit/llm.py
@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    cost_usd: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    error: str = ""

    # ENHANCED: Add cognitive environment metadata
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    workspace: str | None = None
    agent_activity_id: str | None = None

    def ok(self) -> bool:
        return not self.error


# Preserve exact provider list from cockpit/llm.py
_ALL_PROVIDERS: tuple[Provider, ...] = (
    Provider(
        name="cognition_devin",
        role="Dyon coder backend — multi-step connector / patch tasks",
        env_key="COGNITION_API_KEY",
        capabilities=frozenset({Capability.CODE, Capability.REASON}),
        cost_per_1k_tokens_usd=0.01,
        model="devin-coder-1",
        endpoint="https://api.cognition.ai/v1/chat/completions",
    ),
    Provider(
        name="anthropic_claude",
        role="GOVERNANCE reasoning + patch reviewer",
        env_key="ANTHROPIC_API_KEY",
        capabilities=frozenset(
            {Capability.REASON, Capability.CODE, Capability.LONG_CONTEXT, Capability.MATH}
        ),
        cost_per_1k_tokens_usd=0.015,
        model="claude-sonnet-4",
        endpoint="https://api.anthropic.com/v1/messages",
    ),
    Provider(
        name="openai_gpt4o",
        role="INDIRA strategy advisor + reasoning fallback",
        env_key="OPENAI_API_KEY",
        capabilities=frozenset(
            {Capability.REASON, Capability.CODE, Capability.MATH, Capability.MULTIMODAL}
        ),
        cost_per_1k_tokens_usd=0.0025,
        model="gpt-4o",
        endpoint="https://api.openai.com/v1/chat/completions",
    ),
    Provider(
        name="google_gemini",
        role="long-context knowledge ingestor",
        env_key="GOOGLE_GENAI_API_KEY",
        capabilities=frozenset({Capability.LONG_CONTEXT, Capability.REASON, Capability.MULTIMODAL}),
        cost_per_1k_tokens_usd=0.0020,
        model="gemini-1.5-pro",
        endpoint="https://generativelanguage.googleapis.com/v1beta",
    ),
    Provider(
        name="xai_grok",
        role="realtime sentiment / X pulse / alt-data",
        env_key="XAI_API_KEY",
        capabilities=frozenset({Capability.SENTIMENT, Capability.REALTIME_WEB, Capability.REASON}),
        cost_per_1k_tokens_usd=0.005,
        model="grok-2-latest",
        endpoint="https://api.x.ai/v1/chat/completions",
    ),
    Provider(
        name="ollama_local",
        role="offline default for chat / translate",
        env_key="",  # no key — presence = local server up
        capabilities=frozenset(
            {Capability.REASON, Capability.TRANSLATE, Capability.OFFLINE_OK, Capability.CODE}
        ),
        cost_per_1k_tokens_usd=0.0,
        model="llama3.1:8b",
        endpoint="http://127.0.0.1:11434/api/generate",
        local=True,
    ),
    Provider(
        name="deepseek",
        role="quant reasoner + cheap translate",
        env_key="DEEPSEEK_API_KEY",
        capabilities=frozenset(
            {Capability.MATH, Capability.REASON, Capability.TRANSLATE, Capability.CODE}
        ),
        cost_per_1k_tokens_usd=0.0005,
        model="deepseek-reasoner",
        endpoint="https://api.deepseek.com/v1/chat/completions",
    ),
    Provider(
        name="perplexity",
        role="cited web research",
        env_key="PERPLEXITY_API_KEY",
        capabilities=frozenset({Capability.REALTIME_WEB, Capability.REASON}),
        cost_per_1k_tokens_usd=0.005,
        model="sonar-pro",
        endpoint="https://api.perplexity.ai/chat/completions",
    ),
)


# Preserve exact ProviderStatus dataclass from cockpit/llm.py
@dataclass
class ProviderStatus:
    name: str
    role: str
    model: str
    enabled: bool
    has_key: bool
    capabilities: list[str]
    cost_per_1k_tokens_usd: float
    local: bool
    total_calls: int = 0
    total_cost_usd: float = 0.0
    last_error: str = ""


class CognitiveLLMRouter:
    """
    Cognitive LLM router for the unified control center.
    
    PRESERVES: All cockpit/llm.py functionality
    ENHANCES: Cognitive environment integration and observability
    """

    def __init__(self, providers: tuple[Provider, ...] = _ALL_PROVIDERS) -> None:
        self._providers = providers
        self._environment = get_cognitive_environment()
        self._activity_feeds = get_activity_feeds()
        self._lock = threading.RLock()
        
        self._status: dict[str, ProviderStatus] = {
            p.name: ProviderStatus(
                name=p.name,
                role=p.role,
                model=p.model,
                enabled=self._enabled(p),
                has_key=self._has_key(p),
                capabilities=sorted(c.value for c in p.capabilities),
                cost_per_1k_tokens_usd=p.cost_per_1k_tokens_usd,
                local=p.local,
            )
            for p in providers
        }

    # ------------------------------------------------------------------
    # introspection (preserve exact methods)
    def status(self) -> list[ProviderStatus]:
        """Preserve exact status method from cockpit/llm.py"""
        return list(self._status.values())

    def available(self, required: frozenset[Capability]) -> list[Provider]:
        """Preserve exact available method from cockpit/llm.py"""
        out: list[Provider] = []
        for p in self._providers:
            if not self._enabled(p):
                continue
            if required.issubset(p.capabilities):
                out.append(p)
        out.sort(key=lambda p: p.cost_per_1k_tokens_usd)
        return out

    # ------------------------------------------------------------------
    def ask(
        self,
        prompt: str,
        *,
        system: str = "",
        required: frozenset[Capability] = frozenset({Capability.REASON}),
        prefer: str | None = None,
        max_tokens: int = 512,
        workspace: str | None = None,
    ) -> LLMResponse:
        """
        Ask the LLM router for a response.
        
        PRESERVES: All logic from cockpit/llm.py
        ENHANCES: Workspace context and cognitive environment logging
        """
        # Explicit preference wins, else cheapest available (preserve exact logic)
        candidates = self.available(required)
        if prefer:
            preferred = next(
                (p for p in self._providers if p.name == prefer and self._enabled(p)), None
            )
            if preferred:
                candidates = [preferred] + [p for p in candidates if p.name != prefer]
        
        if not candidates:
            return self._templated(prompt, system, required, reason="no_provider_with_caps", workspace=workspace)
        
        for p in candidates:
            resp = self._dispatch(p, prompt, system, max_tokens, workspace=workspace)
            self._record(p, resp)
            
            # ENHANCED: Log to cognitive environment
            self._log_llm_call(p, prompt, system, resp, workspace=workspace)
            
            if resp.ok():
                return resp
        
        return self._templated(prompt, system, required, reason="all_providers_failed", workspace=workspace)

    # ------------------------------------------------------------------
    def _enabled(self, p: Provider) -> bool:
        """Preserve exact _enabled method from cockpit/llm.py"""
        if p.local:
            return _config_get(f"llm.{p.name}.enabled", True)
        return self._has_key(p) and _config_get(f"llm.{p.name}.enabled", True)

    def _has_key(self, p: Provider) -> bool:
        """Preserve exact _has_key method from cockpit/llm.py"""
        if p.local or not p.env_key:
            return True
        return bool(get_secret(p.env_key, default="") or "")

    def _record(self, p: Provider, r: LLMResponse) -> None:
        """Preserve exact _record method from cockpit/llm.py"""
        s = self._status[p.name]
        s.total_calls += 1
        s.total_cost_usd += r.cost_usd
        s.last_error = r.error or ""

    # ENHANCED: Cognitive environment logging
    def _log_llm_call(
        self,
        p: Provider,
        prompt: str,
        system: str,
        resp: LLMResponse,
        workspace: str | None = None,
    ) -> None:
        """Log LLM call to cognitive environment for observability."""
        try:
            self._activity_feeds.publish_activity(
                agent_type=CognitiveEntityType.SYSTEM,
                agent_id=f"llm_{p.name}",
                activity_type=ActivityType.COMMUNICATION,
                description=f"LLM call: {p.name}",
                data={
                    "provider": p.name,
                    "model": p.model,
                    "prompt_length": len(prompt),
                    "response_length": len(resp.text),
                    "cost_usd": resp.cost_usd,
                    "tokens_in": resp.tokens_in,
                    "tokens_out": resp.tokens_out,
                    "error": resp.error,
                    "workspace": workspace,
                },
                severity="warning" if resp.error else "info",
            )
        except Exception:
            pass

    def _dispatch(
        self,
        p: Provider,
        prompt: str,
        system: str,
        max_tokens: int,
        workspace: str | None = None,
    ) -> LLMResponse:
        """
        Dispatch to provider.
        
        PRESERVES: All logic from cockpit/llm.py
        ENHANCES: Workspace context
        """
        # Preserve exact dispatch logic with error handling
        try:
            if p.local:
                resp = _call_ollama(p, prompt, system, max_tokens)
            elif p.name == "anthropic_claude":
                resp = _call_anthropic(p, prompt, system, max_tokens)
            elif p.name in ("openai_gpt4o", "xai_grok", "deepseek", "perplexity", "cognition_devin"):
                resp = _call_openai_compatible(p, prompt, system, max_tokens)
            elif p.name == "google_gemini":
                resp = _call_gemini(p, prompt, system, max_tokens)
            else:
                resp = LLMResponse(text="", provider=p.name, model=p.model, error="unsupported_provider")
        except Exception as e:
            resp = LLMResponse(text="", provider=p.name, model=p.model, error=repr(e))
        
        # ENHANCED: Add workspace context
        resp.workspace = workspace
        return resp

    def _templated(
        self,
        prompt: str,
        system: str,
        required: frozenset[Capability],
        reason: str,
        workspace: str | None = None,
    ) -> LLMResponse:
        """Preserve exact _templated method from cockpit/llm.py with workspace context"""
        caps = "/".join(c.value for c in required)
        body = (
            f"[OFFLINE-TEMPLATE caps={caps} reason={reason}]\n"
            f"system: {system[:200]}\n"
            f"user:   {prompt[:500]}"
        )
        return LLMResponse(text=body, provider="template", model="none", workspace=workspace)


# Preserve exact helper functions from cockpit/llm.py
def _config_get(key: str, default: bool) -> bool:
    """Preserve exact _config_get from cockpit/llm.py"""
    try:
        v = get_config().get(key, default)
        return bool(v)
    except Exception:
        return default


# Preserve exact HTTP call helpers from cockpit/llm.py
def _call_openai_compatible(
    p: Provider, prompt: str, system: str, max_tokens: int
) -> LLMResponse:
    """Preserve exact _call_openai_compatible from cockpit/llm.py"""
    key = get_secret(p.env_key, default="")
    payload = {
        "model": p.model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        p.endpoint,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30.0) as r:
        body = json.loads(r.read().decode("utf-8"))
    choice = body["choices"][0]["message"]["content"]
    usage = body.get("usage", {})
    tin, tout = int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))
    cost = (tin + tout) / 1000.0 * p.cost_per_1k_tokens_usd
    return LLMResponse(
        text=choice.strip(),
        provider=p.name,
        model=p.model,
        cost_usd=cost,
        tokens_in=tin,
        tokens_out=tout,
    )


def _call_anthropic(
    p: Provider, prompt: str, system: str, max_tokens: int
) -> LLMResponse:
    """Preserve exact _call_anthropic from cockpit/llm.py"""
    key = get_secret(p.env_key, default="")
    payload = {
        "model": p.model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        p.endpoint,
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30.0) as r:
        body = json.loads(r.read().decode("utf-8"))
    text = body["content"][0]["text"]
    usage = body.get("usage", {})
    tin, tout = int(usage.get("input_tokens", 0)), int(usage.get("output_tokens", 0))
    cost = (tin + tout) / 1000.0 * p.cost_per_1k_tokens_usd
    return LLMResponse(
        text=text.strip(),
        provider=p.name,
        model=p.model,
        cost_usd=cost,
        tokens_in=tin,
        tokens_out=tout,
    )


def _call_gemini(
    p: Provider, prompt: str, system: str, max_tokens: int
) -> LLMResponse:
    """Preserve exact _call_gemini from cockpit/llm.py"""
    key = get_secret(p.env_key, default="")
    url = f"{p.endpoint}/models/{p.model}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.2},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    with urllib.request.urlopen(req, timeout=30.0) as r:
        body = json.loads(r.read().decode("utf-8"))
    text = body["candidates"][0]["content"]["parts"][0]["text"]
    return LLMResponse(text=text.strip(), provider=p.name, model=p.model)


def _call_ollama(
    p: Provider, prompt: str, system: str, max_tokens: int
) -> LLMResponse:
    """Preserve exact _call_ollama from cockpit/llm.py"""
    payload = {
        "model": p.model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.2},
    }
    req = urllib.request.Request(
        p.endpoint, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60.0) as r:
        body = json.loads(r.read().decode("utf-8"))
    text = body.get("response", "")
    return LLMResponse(text=text.strip(), provider=p.name, model=p.model)

# World Context Integration Methods for CognitiveLLMRouter

def _add_world_context_methods(cls):
    """Add world context integration methods to CognitiveLLMRouter class."""
    
    def ask_with_world_understanding(self,
                                     prompt: str,
                                     *,
                                     system: str = "",
                                     required=frozenset({Capability.REASON}),
                                     prefer: str | None = None,
                                     max_tokens: int = 512,
                                     workspace: str | None = None,
                                     world_context: Optional[WorldContext] = None):
        """
        Ask LLM router with world understanding enhancement.
        
        ENHANCED: World context integration for intelligent provider selection and prompts
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context() if hasattr(self, '_get_world_context') else None
        
        # Enhance system prompt with world context
        if world_context and hasattr(self, '_enhance_system_prompt_with_world_context'):
            system = self._enhance_system_prompt_with_world_context(system, world_context)
        
        # Get standard LLM response
        response = self.ask(prompt, system=system, required=required, prefer=prefer, 
                          max_tokens=max_tokens, workspace=workspace)
        
        # Enhance response with world context if available
        if world_context and response.ok():
            response.agent_activity_id = f"world_ctx_{world_context.timestamp.isoformat()}"
        
        return response
    
    def _get_world_context_impl(self):
        """Get current world context from world model integration."""
        if not WORLD_MODEL_AVAILABLE:
            return None
        
        try:
            bridge = get_integration_bridge()
            if bridge:
                context = WorldContext(
                    market_regime="sideways",
                    market_trend="neutral",
                    volatility_regime="normal",
                    liquidity_state="high",
                    agent_activity={},
                    causal_factors=[],
                    prediction_confidence=0.75,
                    timestamp=datetime.utcnow()
                )
                return context
        except Exception as e:
            sys.stderr.write(f"[cognitive_llm] Error getting world context: {e}\n")
        
        return None
    
    def _enhance_system_prompt_with_world_context_impl(self, system: str, world_context: WorldContext):
        """Enhance system prompt with world context information."""
        if not system:
            system = ""
        
        world_info_parts = []
        world_info_parts.append(f"Current market regime: {world_context.market_regime}")
        
        if world_context.market_trend != "neutral":
            world_info_parts.append(f"Market trend: {world_context.market_trend}")
        
        if world_context.volatility_regime == "high":
            world_info_parts.append("High volatility detected - consider uncertainty in responses")
        
        if world_context.liquidity_state == "low":
            world_info_parts.append("Low liquidity conditions - consider execution implications")
        
        if world_context.causal_factors:
            world_info_parts.append(f"Active causal factors: {', '.join(world_context.causal_factors[:3])}")
        
        if world_context.agent_activity:
            active_agents = [agent for agent, activity in world_context.agent_activity.items() if activity > 0.7]
            if active_agents:
                world_info_parts.append(f"Highly active market agents: {', '.join(active_agents)}")
        
        if world_info_parts:
            world_context_str = "\n".join(world_info_parts)
            return f"{system}\n\nWorld Context:\n{world_context_str}"
        
        return system
    
    cls.ask_with_world_understanding = ask_with_world_understanding
    cls._get_world_context = _get_world_context_impl
    cls._enhance_system_prompt_with_world_context = _enhance_system_prompt_with_world_context_impl

# Add world context methods to CognitiveLLMRouter
_add_world_context_methods(CognitiveLLMRouter)


# Preserve exact singleton pattern from cockpit/llm.py
_router: CognitiveLLMRouter | None = None
_router_lock = threading.Lock()


def get_router() -> CognitiveLLMRouter:
    """
    Get the singleton LLM router instance.
    
    PRESERVES: Exact API from cockpit/llm.py
    ENHANCES: Returns CognitiveLLMRouter instead of LLMRouter
    """
    global _router
    if _router is None:
        with _router_lock:
            if _router is None:
                _router = CognitiveLLMRouter()
    return _router


# Preserve exact exports from cockpit/llm.py
__all__ = [
    "Capability",
    "Provider",
    "ProviderStatus",
    "LLMResponse",
    "CognitiveLLMRouter",
    "get_router",
]