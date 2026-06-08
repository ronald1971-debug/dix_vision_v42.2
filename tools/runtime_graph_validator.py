"""Runtime Graph Validator — Validates architectural domain boundaries.

Stage 4 — Architecture Graph Validation

Validates that INDIRA may talk to Strategy (allowed) but DYON may not
(denied via INV-DIX-05).

The graph becomes machine-verifiable. Domain definitions are loaded from
contracts/ownership_registry.yaml via ownership_registry_loader.py.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# Lazy-load domain definitions from registry
_INDRA_DOMAINS_CACHE: frozenset[str] | None = None
_DYLON_DOMAINS_CACHE: frozenset[str] | None = None


def _get_indira_domains() -> frozenset[str]:
    """Load INDIRA domains from ownership_registry.yaml."""
    global _INDRA_DOMAINS_CACHE
    if _INDRA_DOMAINS_CACHE is None:
        try:
            from tools.ownership_registry_loader import indira_owned_domains
            _INDRA_DOMAINS_CACHE = frozenset(indira_owned_domains())
        except Exception:
            _INDRA_DOMAINS_CACHE = frozenset({
                "market_intelligence",
                "trader_intelligence",
                "strategy_intelligence",
                "portfolio_intelligence",
                "allocation_intelligence",
                "position_intelligence",
                "execution_feedback_intelligence",
            })
    return _INDRA_DOMAINS_CACHE


def _get_dyon_domains() -> frozenset[str]:
    """Load DYON domains from ownership_registry.yaml."""
    global _DYON_DOMAINS_CACHE
    if _DYON_DOMAINS_CACHE is None:
        try:
            from tools.ownership_registry_loader import dyon_owned_domains
            _DYON_DOMAINS_CACHE = frozenset(dyon_owned_domains())
        except Exception:
            _DYON_DOMAINS_CACHE = frozenset({
                "repository_intelligence",
                "architecture_intelligence",
                "runtime_intelligence",
                "infrastructure_intelligence",
            })
    return _DYON_DOMAINS_CACHE


INDIRA_DOMAINS_CACHE: frozenset[str] | None = None
DYON_DOMAINS_CACHE: frozenset[str] | None = None


def _load_indira_domains() -> frozenset[str]:
    """Load INDIRA domains from ownership_registry.yaml."""
    global INDIRA_DOMAINS_CACHE
    if INDIRA_DOMAINS_CACHE is None:
        try:
            from tools.ownership_registry_loader import indira_owned_domains
            INDIRA_DOMAINS_CACHE = frozenset(indira_owned_domains())
        except Exception:
            INDIRA_DOMAINS_CACHE = frozenset({
                "market_intelligence",
                "trader_intelligence",
                "strategy_intelligence",
                "portfolio_intelligence",
                "allocation_intelligence",
                "position_intelligence",
                "execution_feedback_intelligence",
            })
    return INDIRA_DOMAINS_CACHE


def _load_dyon_domains() -> frozenset[str]:
    """Load DYON domains from ownership_registry.yaml."""
    global DYON_DOMAINS_CACHE
    if DYON_DOMAINS_CACHE is None:
        try:
            from tools.ownership_registry_loader import dyon_owned_domains
            DYON_DOMAINS_CACHE = frozenset(dyon_owned_domains())
        except Exception:
            DYON_DOMAINS_CACHE = frozenset({
                "repository_intelligence",
                "architecture_intelligence",
                "runtime_intelligence",
                "infrastructure_intelligence",
            })
    return DYON_DOMAINS_CACHE


def get_indira_domains() -> frozenset[str]:
    """Public accessor for INDIRA domains."""
    return _load_indira_domains()


def get_dyon_domains() -> frozenset[str]:
    """Public accessor for DYON domains."""
    return _load_dyon_domains()

# Allowed domain edges (from -> to)
ALLOWED_EDGES: frozenset[tuple[str, str]] = frozenset({
    ("indira", "strategy_intelligence"),  # INDIRA → Strategy: allowed
    ("indira", "market_intelligence"),
    ("indira", "trader_intelligence"),
    ("indira", "portfolio_intelligence"),
    ("system", "repository_intelligence"),
    ("system", "architecture_intelligence"),
    ("execution", "broker_access"),
    ("execution", "exchange_access"),
})

# Forbidden domain edges
FORBIDDEN_EDGES: frozenset[tuple[str, str]] = frozenset({
    ("dyon", "strategy_intelligence"),  # DYON → Strategy: forbidden
    ("dyon", "market_intelligence"),
    ("dyon", "trader_intelligence"),
    ("dyon", "portfolio_intelligence"),
})


@dataclass(frozen=True, slots=True)
class EdgeValidationResult:
    """Result of validating a domain edge."""
    edge: tuple[str, str]
    allowed: bool
    invariant: str | None
    reason: str


def validate_edge(source: str, target: str) -> EdgeValidationResult:
    """Validate a source->target domain edge.

    Args:
        source: The source engine (indira, dyon, execution, etc.)
        target: The target domain

    Returns:
        EdgeValidationResult with allowed status and invariant reference.
    """
    indira_domains = _load_indira_domains()
    dyon_domains = _load_dyon_domains()

    # Check forbidden edges first
    if (source.lower(), target.lower()) in FORBIDDEN_EDGES:
        return EdgeValidationResult(
            edge=(source, target),
            allowed=False,
            invariant="INV-DIX-05",
            reason=f"{source} may not access {target} — INV-DIX-05 violation",
        )

    if (source.lower(), target.lower()) in ALLOWED_EDGES:
        return EdgeValidationResult(
            edge=(source, target),
            allowed=True,
            invariant=None,
            reason=f"{source} → {target} is explicitly allowed",
        )

    # Default: check domain ownership
    if source.lower() == "dyon" and target in indira_domains:
        return EdgeValidationResult(
            edge=(source, target),
            allowed=False,
            invariant="INV-DIX-05",
            reason=f"DYON may not access INDIRA domain {target}",
        )

    if source.lower() == "indira" and target in dyon_domains:
        return EdgeValidationResult(
            edge=(source, target),
            allowed=False,
            invariant="INV-DIX-04",
            reason=f"INDIRA may not access DYON domain {target}",
        )

    return EdgeValidationResult(
        edge=(source, target),
        allowed=True,
        invariant=None,
        reason="edge not explicitly constrained",
    )


def generate_runtime_graph(output_path: Path) -> None:
    """Generate the runtime graph JSON for the dashboard.

    Creates docs/system_audit/runtime_graph.json with all domain edges.
    """
    indira_domains = _load_indira_domains()
    dyon_domains = _load_dyon_domains()

    graph = {
        "version": "v42.2-arch",
        "domains": {
            "indira": list(indira_domains),
            "dyon": list(dyon_domains),
        },
        "allowed_edges": [list(e) for e in ALLOWED_EDGES],
        "forbidden_edges": [list(e) for e in FORBIDDEN_EDGES],
        "validations": [],
    }

    # Generate all possible edges for validation tracking
    all_domains = list(indira_domains | dyon_domains)
    all_actors = ["indira", "dyon", "execution", "governance", "learning", "system"]

    for actor in all_actors:
        for domain in all_domains:
            result = validate_edge(actor, domain)
            graph["validations"].append({
                "source": actor,
                "target": domain,
                "allowed": result.allowed,
                "invariant": result.invariant,
                "reason": result.reason,
            })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(graph, f, indent=2)


def load_runtime_graph(path: Path) -> dict:
    """Load the runtime graph JSON."""
    if not path.exists():
        generate_runtime_graph(path)
    with path.open() as f:
        return json.load(f)


__all__ = [
    "ALLOWED_EDGES",
    "FORBIDDEN_EDGES",
    "get_indira_domains",
    "get_dyon_domains",
    "EdgeValidationResult",
    "generate_runtime_graph",
    "load_runtime_graph",
    "validate_edge",
]