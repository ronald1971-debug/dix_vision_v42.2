"""
preservation_layer.py
DIX VISION v42.2 — Preservation Compatibility Layer

Ensures no functionality is lost during cognitive architecture refactoring.
Maintains compatibility between existing engines and new INDIRA/DYON architecture.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MigrationStatus:
    """Tracks migration status for each function."""
    function_name: str
    original_location: str
    new_location: str = ""
    migration_complete: bool = False
    tested: bool = False
    performance_validated: bool = False
    migration_date: Optional[datetime] = None
    notes: str = ""


class PreservationLayer:
    """Compatibility layer to preserve all existing functionality during migration."""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Preserve existing engines
        self._cognitive_orchestrator = None
        self._intelligence_orchestrator = None
        self._reasoning_orchestrator = None
        self._learning_orchestrator = None
        self._knowledge_orchestrator = None
        self._system_orchestrator = None
        self._simulation_orchestrator = None
        
        # New architecture components (to be connected)
        self._indira_brain = None
        self._dyon_brain = None
        self._coordination_layer = None
        
        # Migration settings
        self._migration_mode = True  # Start in compatibility mode
        self._preserve_all_functions = True
        self._fallback_on_failure = True
        
        # Legacy function storage (for fallback)
        self._legacy_functions: Dict[str, Callable] = {}
        
        # Migration tracking
        self._migration_status: Dict[str, MigrationStatus] = {}
        
        # Performance tracking
        self._performance_metrics: Dict[str, Dict[str, float]] = {}


# Global preservation layer instance
_preservation_layer: Optional[PreservationLayer] = None
_preservation_lock = threading.Lock()


def get_preservation_layer() -> PreservationLayer:
    """Get the global preservation layer instance (thread-safe singleton)."""
    global _preservation_layer
    with _preservation_lock:
        if _preservation_layer is None:
            _preservation_layer = PreservationLayer()
    return _preservation_layer
        
    def initialize_legacy_engines(self) -> bool:
        """Initialize and preserve all existing engines."""
        try:
            logger.info("[PRESERVATION] Initializing legacy engines...")
            
            # Import existing engines
            try:
                from cognitive_engine.cognitive_orchestrator import CognitiveOrchestrator
                self._cognitive_orchestrator = CognitiveOrchestrator()
                logger.info("[PRESERVATION] Cognitive Orchestrator initialized")
            except ImportError as e:
                logger.warning(f"[PRESERVATION] Could not import Cognitive Orchestrator: {e}")
            
            try:
                from intelligence_engine.orchestrator import IntelligenceOrchestrator
                self._intelligence_orchestrator = IntelligenceOrchestrator()
                logger.info("[PRESERVATION] Intelligence Orchestrator initialized")
            except ImportError as e:
                logger.warning(f"[PRESERVATION] Could not import Intelligence Orchestrator: {e}")
            
            try:
                from reasoning_engine.orchestrator import ReasoningOrchestrator
                self._reasoning_orchestrator = ReasoningOrchestrator()
                logger.info("[PRESERVATION] Reasoning Orchestrator initialized")
            except ImportError as e:
                logger.warning(f"[PRESERVATION] Could not import Reasoning Orchestrator: {e}")
            
            try:
                from learning_engine.orchestrator import LearningOrchestrator
                self._learning_orchestrator = LearningOrchestrator()
                logger.info("[PRESERVATION] Learning Orchestrator initialized")
            except ImportError as e:
                logger.warning(f"[PRESERVATION] Could not import Learning Orchestrator: {e}")
            
            try:
                from knowledge_engine.orchestrator import KnowledgeOrchestrator
                self._knowledge_orchestrator = KnowledgeOrchestrator()
                logger.info("[PRESERVATION] Knowledge Orchestrator initialized")
            except ImportError as e:
                logger.warning(f"[PRESERVATION] Could not import Knowledge Orchestrator: {e}")
            
            try:
                from system_engine.orchestrator import SystemOrchestrator
                self._system_orchestrator = SystemOrchestrator()
                logger.info("[PRESERVATION] System Orchestrator initialized")
            except ImportError as e:
                logger.warning(f"[PRESERVATION] Could not import System Orchestrator: {e}")
            
            try:
                from simulation_engine.orchestrator import SimulationOrchestrator
                self._simulation_orchestrator = SimulationOrchestrator()
                logger.info("[PRESERVATION] Simulation Orchestrator initialized")
            except ImportError as e:
                logger.warning(f"[PRESERVATION] Could not import Simulation Orchestrator: {e}")
            
            logger.info("[PRESERVATION] Legacy engines initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"[PRESERVATION] Failed to initialize legacy engines: {e}")
            return False
    
    def connect_new_architecture(
        self,
        indira_brain = None,
        dyon_brain = None,
        coordination_layer = None
    ) -> bool:
        """Connect new architecture components."""
        try:
            logger.info("[PRESERVATION] Connecting new architecture components...")
            
            self._indira_brain = indira_brain
            self._dyon_brain = dyon_brain
            self._coordination_layer = coordination_layer
            
            if self._indira_brain:
                logger.info("[PRESERVATION] INDIRA Brain connected")
            if self._dyon_brain:
                logger.info("[PRESERVATION] DYON Brain connected")
            if self._coordination_layer:
                logger.info("[PRESERVATION] Coordination Layer connected")
            
            return True
        except Exception as e:
            logger.error(f"[PRESERVATION] Failed to connect new architecture: {e}")
            return False
    
    def migrate_function(
        self,
        function_name: str,
        new_implementation: Callable,
        original_location: str = "",
        new_location: str = ""
    ) -> bool:
        """Migrate a function while preserving old implementation for fallback."""
        try:
            with self._lock:
                # Store legacy implementation if available
                if self._preserve_all_functions:
                    legacy_func = self._find_legacy_function(function_name)
                    if legacy_func:
                        self._legacy_functions[function_name] = legacy_func
                        logger.info(f"[PRESERVATION] Legacy implementation preserved for {function_name}")
                
                # Create migration status
                self._migration_status[function_name] = MigrationStatus(
                    function_name=function_name,
                    original_location=original_location,
                    new_location=new_location,
                    migration_complete=True,
                    migration_date=datetime.utcnow()
                )
                
                # Add new implementation as attribute
                setattr(self, function_name, new_implementation)
                
                logger.info(f"[PRESERVATION] Migrated {function_name} -> {new_location}")
                return True
                
        except Exception as e:
            logger.error(f"[PRESERVATION] Failed to migrate {function_name}: {e}")
            return False
    
    def _find_legacy_function(self, function_name: str) -> Optional[Callable]:
        """Find legacy function from existing engines."""
        # Try cognitive orchestrator
        if self._cognitive_orchestrator:
            func = getattr(self._cognitive_orchestrator, function_name, None)
            if func and callable(func):
                return func
        
        # Try intelligence orchestrator
        if self._intelligence_orchestrator:
            func = getattr(self._intelligence_orchestrator, function_name, None)
            if func and callable(func):
                return func
        
        # Try reasoning orchestrator
        if self._reasoning_orchestrator:
            func = getattr(self._reasoning_orchestrator, function_name, None)
            if func and callable(func):
                return func
        
        # Try learning orchestrator
        if self._learning_orchestrator:
            func = getattr(self._learning_orchestrator, function_name, None)
            if func and callable(func):
                return func
        
        # Try knowledge orchestrator
        if self._knowledge_orchestrator:
            func = getattr(self._knowledge_orchestrator, function_name, None)
            if func and callable(func):
                return func
        
        # Try system orchestrator
        if self._system_orchestrator:
            func = getattr(self._system_orchestrator, function_name, None)
            if func and callable(func):
                return func
        
        # Try simulation orchestrator
        if self._simulation_orchestrator:
            func = getattr(self._simulation_orchestrator, function_name, None)
            if func and callable(func):
                return func
        
        return None
    
    def fallback_to_legacy(self, function_name: str, *args, **kwargs) -> Any:
        """Fallback to legacy implementation if new one fails."""
        if not self._fallback_on_failure:
            raise AttributeError(f"Fallback disabled, no legacy implementation for {function_name}")
        
        legacy_function = self._legacy_functions.get(function_name)
        if legacy_function:
            logger.warning(f"[PRESERVATION] Falling back to legacy implementation for {function_name}")
            try:
                return legacy_function(*args, **kwargs)
            except Exception as e:
                logger.error(f"[PRESERVATION] Legacy implementation also failed for {function_name}: {e}")
                raise
        
        raise AttributeError(f"No legacy implementation available for {function_name}")
    
    def call_with_preservation(
        self,
        function_name: str,
        use_new: bool = True,
        *args,
        **kwargs
    ) -> Any:
        """Call function with automatic fallback to legacy if new fails."""
        if not use_new or not self._migration_mode:
            # Use legacy directly
            legacy_func = self._find_legacy_function(function_name)
            if legacy_func:
                return legacy_func(*args, **kwargs)
            raise AttributeError(f"No implementation found for {function_name}")
        
        # Try new implementation first
        try:
            new_func = getattr(self, function_name, None)
            if new_func and callable(new_func):
                return new_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"[PRESERVATION] New implementation failed for {function_name}: {e}")
            if self._fallback_on_failure:
                return self.fallback_to_legacy(function_name, *args, **kwargs)
            raise
        
        # If no new implementation, try legacy
        legacy_func = self._find_legacy_function(function_name)
        if legacy_func:
            return legacy_func(*args, **kwargs)
        
        raise AttributeError(f"No implementation found for {function_name}")
    
    def mark_function_tested(self, function_name: str, tested: bool = True) -> None:
        """Mark a function as tested."""
        with self._lock:
            if function_name in self._migration_status:
                self._migration_status[function_name].tested = tested
                logger.info(f"[PRESERVATION] {function_name} marked as tested: {tested}")
    
    def mark_function_performance_validated(
        self,
        function_name: str,
        validated: bool = True,
        metrics: Optional[Dict[str, float]] = None
    ) -> None:
        """Mark a function as performance validated."""
        with self._lock:
            if function_name in self._migration_status:
                self._migration_status[function_name].performance_validated = validated
                if metrics:
                    self._performance_metrics[function_name] = metrics
                logger.info(f"[PRESERVATION] {function_name} marked as performance validated: {validated}")
    
    def get_migration_report(self) -> Dict[str, Any]:
        """Get comprehensive migration status report."""
        with self._lock:
            total_functions = len(self._migration_status)
            migrated_count = sum(
                1 for status in self._migration_status.values()
                if status.migration_complete
            )
            tested_count = sum(
                1 for status in self._migration_status.values()
                if status.tested
            )
            validated_count = sum(
                1 for status in self._migration_status.values()
                if status.performance_validated
            )
            
            return {
                "total_functions": total_functions,
                "migrated_count": migrated_count,
                "tested_count": tested_count,
                "validated_count": validated_count,
                "migration_percentage": (migrated_count / total_functions * 100) if total_functions > 0 else 0,
                "testing_percentage": (tested_count / total_functions * 100) if total_functions > 0 else 0,
                "validation_percentage": (validated_count / total_functions * 100) if total_functions > 0 else 0,
                "migration_mode": self._migration_mode,
                "fallback_enabled": self._fallback_on_failure,
                "legacy_functions_preserved": len(self._legacy_functions),
                "migration_details": {
                    name: {
                        "original_location": status.original_location,
                        "new_location": status.new_location,
                        "migrated": status.migration_complete,
                        "tested": status.tested,
                        "validated": status.performance_validated,
                        "migration_date": status.migration_date.isoformat() if status.migration_date else None,
                        "notes": status.notes
                    }
                    for name, status in self._migration_status.items()
                }
            }
    
    def enable_migration_mode(self, enabled: bool = True) -> None:
        """Enable or disable migration mode."""
        self._migration_mode = enabled
        logger.info(f"[PRESERVATION] Migration mode {'enabled' if enabled else 'disabled'}")
    
    def enable_fallback(self, enabled: bool = True) -> None:
        """Enable or disable fallback to legacy implementations."""
        self._fallback_on_failure = enabled
        logger.info(f"[PRESERVATION] Fallback {'enabled' if enabled else 'disabled'}")
    
    def get_preserved_functions(self) -> List[str]:
        """Get list of preserved legacy functions."""
        return list(self._legacy_functions.keys())
    
    def validate_no_functionality_loss(self) -> Dict[str, Any]:
        """Validate that no functionality has been lost during migration."""
        with self._lock:
            # Check that all migrated functions have either working new or legacy implementations
            missing_functions = []
            at_risk_functions = []
            
            for func_name in self._migration_status:
                new_func = getattr(self, func_name, None)
                legacy_func = self._legacy_functions.get(func_name)
                
                if not new_func and not legacy_func:
                    missing_functions.append(func_name)
                elif not new_func and legacy_func:
                    at_risk_functions.append(func_name)
            
            return {
                "validation_complete": True,
                "total_functions_checked": len(self._migration_status),
                "missing_functions": missing_functions,
                "at_risk_functions": at_risk_functions,
                "functions_safe": len(self._migration_status) - len(missing_functions) - len(at_risk_functions),
                "validation_passed": len(missing_functions) == 0,
                "recommendations": [
                    f"Implement missing function: {func}" for func in missing_functions
                ] + [
                    f"Test at-risk function: {func}" for func in at_risk_functions
                ]
            }


# Global instance
_preservation_layer: Optional[PreservationLayer] = None
_preservation_lock = threading.Lock()


def get_preservation_layer() -> PreservationLayer:
    """Get global preservation layer instance."""
    global _preservation_layer
    if _preservation_layer is None:
        with _preservation_lock:
            if _preservation_layer is None:
                _preservation_layer = PreservationLayer()
    return _preservation_layer


__all__ = [
    "PreservationLayer",
    "MigrationStatus",
    "get_preservation_layer",
]