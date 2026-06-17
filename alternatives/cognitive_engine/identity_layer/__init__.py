"""Identity Layer - system self-model.

A mature DIXVISION knows:
- Who am I? (architecturally, not philosophically)
- Capabilities
- Current limits
- Current maturity
- Active objectives
- Disabled capabilities
"""

from cognitive_engine.identity_layer.capabilities import Capability, CapabilityStatus
from cognitive_engine.identity_layer.identity import Identity
from cognitive_engine.identity_layer.maturity import MaturityAssessment, MaturityLevel

__all__ = [
    "Capability",
    "CapabilityStatus",
    "Identity",
    "MaturityAssessment",
    "MaturityLevel",
]