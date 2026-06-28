"""Authority Graph – defines the immutable authority chain.

Authority flows strictly downward:

    Operator
      ↓
    Governance
      ↓
    Cognition
      ↓
    Execution
      ↓
    Capital
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AuthorityLevel(Enum):
    OPERATOR = 0
    GOVERNANCE = 1
    COGNITION = 2
    EXECUTION = 3
    CAPITAL = 4


@dataclass(frozen=True)
class AuthorityNode:
    level: AuthorityLevel
    name: str
    can_halt: bool = False
    can_approve: bool = False
    can_execute: bool = False
    can_allocate_capital: bool = False


_AUTHORITY_CHAIN: list[AuthorityNode] = [
    AuthorityNode(
        level=AuthorityLevel.OPERATOR,
        name="Operator",
        can_halt=True,
        can_approve=True,
    ),
    AuthorityNode(
        level=AuthorityLevel.GOVERNANCE,
        name="Governance",
        can_halt=True,
        can_approve=True,
    ),
    AuthorityNode(
        level=AuthorityLevel.COGNITION,
        name="Cognition",
        can_halt=False,
        can_approve=False,
    ),
    AuthorityNode(
        level=AuthorityLevel.EXECUTION,
        name="Execution",
        can_execute=True,
    ),
    AuthorityNode(
        level=AuthorityLevel.CAPITAL,
        name="Capital",
        can_allocate_capital=True,
    ),
]


@dataclass
class AuthorityGraph:
    """Enforces the authority hierarchy.

    No lower-level node may override a higher-level decision.
    """

    nodes: list[AuthorityNode] = field(default_factory=lambda: list(_AUTHORITY_CHAIN))

    def get_node(self, level: AuthorityLevel) -> AuthorityNode:
        for node in self.nodes:
            if node.level == level:
                return node
        raise ValueError(f"No node at level {level}")

    def can_override(self, requester: AuthorityLevel, target: AuthorityLevel) -> bool:
        """Return True if requester has authority over target."""
        return requester.value < target.value

    def validate_action(self, actor_level: AuthorityLevel, action: str) -> tuple[bool, str]:
        """Validate whether an authority level can perform an action."""
        node = self.get_node(actor_level)

        action_map = {
            "halt": node.can_halt,
            "approve": node.can_approve,
            "execute": node.can_execute,
            "allocate_capital": node.can_allocate_capital,
        }

        if action not in action_map:
            return False, f"Unknown action: {action}"

        if action_map[action]:
            return True, f"{node.name} authorized for {action}"
        return False, f"{node.name} not authorized for {action}"

    def get_chain(self) -> list[AuthorityNode]:
        return sorted(self.nodes, key=lambda n: n.level.value)

    def authority_path(self) -> list[str]:
        return [n.name for n in self.get_chain()]
