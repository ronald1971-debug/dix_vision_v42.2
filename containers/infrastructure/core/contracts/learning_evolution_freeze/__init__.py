"""
Core Contracts Learning Evolution Freeze
Real implementation for learning/evolution freeze policy
"""

from dataclasses import dataclass

@dataclass
class LearningEvolutionFreezePolicy:
    """Policy for learning/evolution freeze"""
    frozen: bool = False
    freeze_reason: str = ""
    allowed_patches: list = None
    mode: str = None  # System mode
    operator_override: bool = False  # Operator override flag
    
    def __post_init__(self):
        if self.allowed_patches is None:
            self.allowed_patches = []
    
    def is_frozen(self) -> bool:
        """Check if learning/evolution is frozen"""
        return self.frozen
    
    def is_unfrozen(self) -> bool:
        """Check if learning/evolution is unfrozen"""
        return not self.frozen
    
    def freeze(self, reason: str) -> None:
        """Freeze learning/evolution"""
        self.frozen = True
        self.freeze_reason = reason
    
    def unfreeze(self) -> None:
        """Unfreeze learning/evolution"""
        self.frozen = False
        self.freeze_reason = ""

# Global freeze policy
_freeze_policy = LearningEvolutionFreezePolicy()

def get_freeze_policy() -> LearningEvolutionFreezePolicy:
    """Get the global freeze policy"""
    return _freeze_policy

def assert_unfrozen(patch_id: str = None) -> None:
    """Assert that learning/evolution is not frozen"""
    policy = get_freeze_policy()
    if policy.is_frozen():
        if patch_id and patch_id in policy.allowed_patches:
            return  # This patch is allowed
        raise RuntimeError(f"Learning/evolution is frozen: {policy.freeze_reason}")
    return None

def freeze_learning_evolution(reason: str) -> None:
    """Freeze learning/evolution"""
    get_freeze_policy().freeze(reason)

def unfreeze_learning_evolution() -> None:
    """Unfreeze learning/evolution"""
    get_freeze_policy().unfreeze()

def allow_patch(patch_id: str) -> None:
    """Allow a specific patch during freeze"""
    policy = get_freeze_policy()
    if patch_id not in policy.allowed_patches:
        policy.allowed_patches.append(patch_id)

def disallow_patch(patch_id: str) -> None:
    """Disallow a specific patch during freeze"""
    policy = get_freeze_policy()
    if patch_id in policy.allowed_patches:
        policy.allowed_patches.remove(patch_id)

__all__ = [
    "LearningEvolutionFreezePolicy",
    "get_freeze_policy",
    "assert_unfrozen",
    "freeze_learning_evolution",
    "unfreeze_learning_evolution",
    "allow_patch",
    "disallow_patch"
]