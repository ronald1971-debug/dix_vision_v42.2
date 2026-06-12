"""
cognitive_control_center.shared_services.chat
Chat service - Migrated from cockpit/chat.py

This module provides chat functionality for the cognitive control center, preserving all
features from cockpit/chat.py while integrating with the cognitive environment and agent
operations center.

PRESERVED FEATURES:
- Multi-voice routing (INDIRA/DYON/GOVERNANCE)
- Keyword-based intent detection
- Charter-grounded responses
- API URL sniffing
- LLM paraphrase (optional)
- Chat history management
- Ledger audit logging
- Language detection
- Locale support
- Voice forcing

ENHANCED FEATURES:
- Integration with agent operations center
- Real-time chat activity feeds
- Workspace-based chat contexts
- Cognitive environment awareness
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass, field
from typing import Callable

from core.charter import Voice, all_charters
from core.introspection import Introspection, introspect
from mind.knowledge.language import detect_language
from state.ledger.writer import get_writer
from system.locale import current as current_locale

from cognitive_control_center.agent_operations_center.activity_feeds import (
    ActivityType,
    get_activity_feeds,
)
from cognitive_control_center.core.operating_environment import (
    CognitiveEntityType,
    get_cognitive_environment,
)

# Preserve exact regex from cockpit/chat.py
_URL_RE = re.compile(
    r"(https?://[^\s<>\"']+|[a-z0-9][a-z0-9\-]*\.[a-z]{2,}(?:/[^\s<>\"']*)?)", re.IGNORECASE
)

# Preserve exact charter imports (critical for voice behavior)
import cognitive_governance.charter as _cogov_charter  # noqa: F401, E402
import evolution_engine.charter.dyon as _dyon_charter  # noqa: F401, E402
import intelligence_engine.charter.indira as _indira_charter  # noqa: F401, E402
import system_monitor.charter as _sysmon_charter  # noqa: F401, E402
from cockpit import charter as _cockpit_charter  # noqa: F401, E402
from governance import charter as _gov_charter  # noqa: F401, E402
from mind import charter as _mind_charter  # noqa: F401, E402

# Preserve exact keyword lists
_INDIRA_KEYWORDS = (
    "trade",
    "order",
    "buy",
    "sell",
    "fill",
    "adapter",
    "strategy",
    "signal",
    "slippage",
    "mev",
    "market",
    "position",
    "portfolio",
    "pnl",
    "execution",
)

_DYON_KEYWORDS = (
    "hazard",
    "heartbeat",
    "latency",
    "feed",
    "queue",
    "disk",
    "memory",
    "patch",
    "coder",
    "deploy",
    "canary",
    "rollback",
    "onboard",
    "add adapter",
    "add source",
    "add api",
    "connect to",
    "sniff",
    "probe",
    "discover",
    "system",
    "monitor",
    "code",
    "function",
    "module",
    "debug",
    "trace",
)

_GOV_KEYWORDS = (
    "mode",
    "safe",
    "halt",
    "resume",
    "kill",
    "governance",
    "policy",
    "constraint",
    "approve",
    "reject",
    "promote",
    "explain",
    "why did",
    "how does",
    "architecture",
    "ledger",
)


@dataclass
class ChatTurn:
    """Preserve exact ChatTurn structure from cockpit/chat.py"""
    operator_message: str
    voice: Voice
    answer: str
    language: str
    intent: list[str] = field(default_factory=list)
    ledger_refs: list[int] = field(default_factory=list)
    model_used: str = "template"
    introspection: Introspection | None = None

    # ENHANCED: Add cognitive environment metadata
    workspace: str | None = None
    timestamp: str | None = None
    agent_activity_id: str | None = None


class Router:
    """Preserve exact Router logic from cockpit/chat.py"""
    
    def route(self, message: str, forced_voice: Voice | None = None) -> Voice:
        if forced_voice is not None:
            return forced_voice
        m = message.lower()
        scores: dict[Voice, int] = {v: 0 for v in Voice}
        for kw in _INDIRA_KEYWORDS:
            if kw in m:
                scores[Voice.INDIRA] += 1
        for kw in _DYON_KEYWORDS:
            if kw in m:
                scores[Voice.DYON] += 1
        for kw in _GOV_KEYWORDS:
            if kw in m:
                scores[Voice.GOVERNANCE] += 1
        best, score = max(scores.items(), key=lambda x: x[1])
        return best if score > 0 else Voice.GOVERNANCE


class CognitiveChat:
    """
    Cognitive chat service for the unified control center.
    
    PRESERVES: All cockpit/chat.py functionality
    ENHANCES: Agent operations center integration and cognitive environment awareness
    """

    def __init__(self) -> None:
        self._router = Router()
        self._history: list[ChatTurn] = []
        self._environment = get_cognitive_environment()
        self._activity_feeds = get_activity_feeds()
        self._lock = threading.RLock()

    def history(self, limit: int = 50) -> list[ChatTurn]:
        """Preserve exact history method from cockpit/chat.py"""
        with self._lock:
            return list(self._history[-limit:])

    def send(
        self, message: str, forced_voice: Voice | None = None, locale_tag: str = "", workspace: str | None = None
    ) -> ChatTurn:
        """
        Send a chat message and get a response.
        
        PRESERVES: All logic from cockpit/chat.py
        ENHANCES: Workspace context and cognitive environment integration
        """
        lang = detect_language(message) or "en"
        
        # Preserve exact URL sniffing logic
        urls = _URL_RE.findall(message or "")
        sniffed: list[dict[str, object]] = []
        for u in urls[:3]:
            try:
                from mind.sources.providers.api_sniffer import propose_candidate
                sniffed.append(propose_candidate(u).to_dict())
            except Exception:
                continue
        
        voice = self._router.route(message, forced_voice=forced_voice)
        if urls and not forced_voice:
            voice = Voice.DYON
        
        peers = [v for v in Voice if v is not voice]
        info = introspect(voice, message, peers=peers)
        answer = info.render()
        
        # Preserve exact sniffed output formatting
        if sniffed:
            lines = ["", "API SNIFFER (DYON):"]
            for s in sniffed:
                surfaces = ", ".join(s.get("api_surfaces") or []) or "none"
                lines.append(
                    f"  - {s.get('host')}: surfaces=[{surfaces}] "
                    f"auth={s.get('auth_required')} "
                    f"relevance={s.get('relevance_score')}"
                )
            answer = answer + "\n" + "\n".join(lines)
        
        model_used = "template"
        
        # Preserve exact LLM paraphrase logic
        try:
            from cockpit.llm import Capability
            from cockpit.llm import get_router as get_llm_router

            llm = get_llm_router()
            system = (
                f"You are the {voice.value} voice of DIX VISION v42.2. "
                f"Stay within your charter. Reply in language '{lang}'. "
                "Keep answers concise and ground every claim in the ledger."
            )
            paraphrase = llm.ask(answer, system=system, required=frozenset({Capability.REASON}))
            if paraphrase.ok() and paraphrase.provider != "template":
                answer = paraphrase.text
                model_used = f"{paraphrase.provider}:{paraphrase.model}"
        except Exception:
            pass

        # ENHANCED: Create enhanced ChatTurn with cognitive metadata
        from datetime import datetime
        turn = ChatTurn(
            operator_message=message,
            voice=voice,
            answer=answer,
            language=lang,
            intent=[voice.value],
            ledger_refs=info.ledger_refs,
            model_used=model_used,
            introspection=info,
            workspace=workspace,
            timestamp=datetime.utcnow().isoformat(),
        )
        
        with self._lock:
            self._history.append(turn)

        # Preserve exact ledger audit logic
        try:
            get_writer().write(
                "SYSTEM",
                "CHAT",
                voice.value,
                {
                    "message": message,
                    "voice": voice.value,
                    "language": lang,
                    "locale": locale_tag or current_locale().tag,
                    "model_used": model_used,
                    "answer_chars": len(answer),
                    "workspace": workspace,
                },
            )
        except Exception:
            pass

        # ENHANCED: Log to cognitive environment and activity feeds
        try:
            # Map voice to entity type for cognitive environment
            entity_type = {
                Voice.INDIRA: CognitiveEntityType.INDIRA,
                Voice.DYON: CognitiveEntityType.DYON,
                Voice.GOVERNANCE: CognitiveEntityType.SYSTEM,
            }.get(voice, CognitiveEntityType.SYSTEM)

            # Publish to activity feeds
            self._activity_feeds.publish_activity(
                agent_type=entity_type,
                agent_id=voice.value,
                activity_type=ActivityType.COMMUNICATION,
                description=f"Chat: {message[:50]}...",
                data={
                    "voice": voice.value,
                    "language": lang,
                    "model_used": model_used,
                    "workspace": workspace,
                },
            )
        except Exception:
            pass

        return turn


# Preserve exact singleton pattern from cockpit/chat.py
_chat: CognitiveChat | None = None
_chat_lock = threading.Lock()


def get_chat() -> CognitiveChat:
    """
    Get the singleton chat instance.
    
    PRESERVES: Exact API from cockpit/chat.py
    ENHANCES: Returns CognitiveChat instead of Chat
    """
    global _chat
    if _chat is None:
        with _chat_lock:
            if _chat is None:
                _chat = CognitiveChat()
    return _chat


# Preserve exact API
def available_voices() -> list[str]:
    """Preserve exact API from cockpit/chat.py"""
    return [v.value for v in all_charters().keys()]


__all__ = [
    "CognitiveChat",
    "ChatTurn", 
    "Router",
    "get_chat",
    "available_voices",
]