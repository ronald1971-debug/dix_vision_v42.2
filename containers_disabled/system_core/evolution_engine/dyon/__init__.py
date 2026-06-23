"""evolution_engine.dyon — DYON's autonomous engineering intelligence modules.

Per authority-lint B24, this package is one of two scopes permitted to
import langgraph / langchain* / langsmith. Outputs are advisory only —
they feed into the governance patch pipeline, never directly executed.

DYON modules in this package:
  topology_scanner — AST-based architectural drift detection
  indira_architecture_analyzer — INDIRA architecture analysis for system optimization
  indira_performance_monitor — INDIRA performance monitoring for system optimization
  indira_quality_analyzer — INDIRA code quality analysis for system improvement
  indira_analysis_system — Integrated INDIRA analysis for comprehensive system cognition
  advanced_repository_intelligence — Advanced repository intelligence with semantic understanding
  realtime_system_monitoring — Real-time system monitoring and health dashboard
  enhanced_patch_generation — Enhanced patch generation with safety validation
  predictive_maintenance — Predictive maintenance and issue anticipation (get_predictive_maintenance_system)
  system_behavior_modeling — System behavior modeling and simulation
  dependency_management — Dependency management and intelligence
  ml_predictive_engine — ML integration for enhanced predictive accuracy
  realtime_simulation — Real-time simulation for live system behavior analysis
  advanced_dependency_analysis — Advanced graph-based dependency analysis
  predictive_scaling — Predictive scaling for automatic resource management
  dy_indira_integration — DYON-INDIRA integration for system-market optimization synergy
  self_healing — Self-healing mechanisms for automated system recovery
  multi_environment_deps — Multi-environment dependency management support
  historical_trend_analysis — Historical trend analysis for system evolution
  cost_optimization — Cost optimization for cloud resource modeling

All DYON components provide SYSTEM COGNITION ONLY:
  - Analyze architecture, performance, and quality of system components
  - Monitor system health and generate improvement recommendations
  - Generate safe code transformations and patches
  - Never execute trades or perform trading operations
  - Never make trading decisions or analyze market data for trading
  - Respect strict domain separation: DYON (SYSTEM) vs INDIRA (MARKET)
"""

from .advanced_dependency_analysis import get_advanced_dependency_analysis
from .advanced_repository_intelligence import get_advanced_repository_intelligence
from .cost_optimization import get_cost_optimization_engine
from .dependency_management import get_dependency_management
from .dy_indira_integration import get_dy_indira_integration
from .enhanced_patch_generation import get_enhanced_patch_generator
from .historical_trend_analysis import get_historical_trend_analysis
from .indira_analysis_system import get_indira_analysis_system
from .indira_architecture_analyzer import get_indira_architecture_analyzer
from .indira_performance_monitor import get_indira_performance_monitor
from .indira_quality_analyzer import get_indira_quality_analyzer
from .ml_predictive_engine import get_ml_predictive_engine
from .multi_environment_deps import get_multi_environment_manager
from .predictive_maintenance import get_predictive_maintenance_system
from .predictive_scaling import get_predictive_scaling
from .realtime_simulation import get_realtime_simulation
from .realtime_system_monitoring import get_realtime_system_monitor
from .self_healing import get_self_healing_engine
from .system_behavior_modeling import get_system_behavior_modeling
from .topology_scanner import get_scanner

__all__ = [
    "get_scanner",
    "get_indira_architecture_analyzer",
    "get_indira_performance_monitor",
    "get_indira_quality_analyzer",
    "get_indira_analysis_system",
    "get_advanced_repository_intelligence",
    "get_realtime_system_monitor",
    "get_enhanced_patch_generator",
    "get_predictive_maintenance_system",
    "get_system_behavior_modeling",
    "get_dependency_management",
    "get_ml_predictive_engine",
    "get_realtime_simulation",
    "get_advanced_dependency_analysis",
    "get_predictive_scaling",
    "get_dy_indira_integration",
    "get_self_healing_engine",
    "get_multi_environment_manager",
    "get_historical_trend_analysis",
    "get_cost_optimization_engine",
]
