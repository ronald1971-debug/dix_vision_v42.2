"""
execution_unified.consolidation.legacy_system_analyzer
DIX VISION v42.2 — Legacy System Analyzer (Quick Win)

Analyzes legacy systems to plan consolidation and migration.
This is a quick win implementation for system consolidation.
"""

from __future__ import annotations

import logging
import os
import ast
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class LegacySystemType(Enum):
    """Types of legacy systems."""
    GOVERNANCE = "GOVERNANCE"
    EXECUTION = "EXECUTION"
    INTELLIGENCE = "INTELLIGENCE"
    EVOLUTION = "EVOLUTION"
    OTHER = "OTHER"


@dataclass
class LegacySystemAnalysis:
    """Analysis result for a legacy system."""
    
    system_name: str
    system_type: LegacySystemType
    path: str
    file_count: int
    total_lines: int
    estimated_complexity: str  # LOW, MEDIUM, HIGH, VERY_HIGH
    active_usage: bool
    last_modified: datetime
    dependencies: List[str] = field(default_factory=list)
    functionality_overlap: List[str] = field(default_factory=list)
    migration_complexity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, VERY_HIGH
    recommended_action: str = "ARCHIVE"  # ARCHIVE, MIGRATE, KEEP
    notes: str = ""


@dataclass
class ConsolidationPlan:
    """Plan for system consolidation."""
    
    legacy_systems: List[LegacySystemAnalysis]
    migration_priority: List[str]  # System names in migration order
    estimated_migration_time_days: int
    risk_assessment: str  # LOW, MEDIUM, HIGH
    recommended_timeline: str


class LegacySystemAnalyzer:
    """Analyzes legacy systems for consolidation planning."""
    
    def __init__(self):
        self._legacy_systems: Dict[str, LegacySystemAnalysis] = {}
        logger.info("[LEGACY_ANALYZER] Initialized")
    
    def analyze_legacy_systems(self, base_path: str = ".") -> ConsolidationPlan:
        """
        Analyze all legacy systems in the codebase.
        
        Args:
            base_path: Base path to analyze from
            
        Returns:
            Consolidation plan with analysis results
        """
        base_path = Path(base_path)
        
        # Identify legacy systems
        legacy_paths = [
            ("governance", LegacySystemType.GOVERNANCE),
            ("governance_engine", LegacySystemType.GOVERNANCE),
            ("financial_governance", LegacySystemType.GOVERNANCE),
            ("operator_governance", LegacySystemType.GOVERNANCE),
            ("execution", LegacySystemType.EXECUTION),
            ("execution_engine", LegacySystemType.EXECUTION),
            ("mind", LegacySystemType.INTELLIGENCE),
            ("intelligence_engine", LegacySystemType.INTELLIGENCE),
        ]
        
        analyses = []
        
        for system_path, system_type in legacy_paths:
            full_path = base_path / system_path
            if full_path.exists():
                analysis = self._analyze_system(full_path, system_type)
                analyses.append(analysis)
                self._legacy_systems[system_path] = analysis
        
        # Generate consolidation plan
        plan = self._generate_consolidation_plan(analyses)
        
        return plan
    
    def _analyze_system(self, system_path: Path, system_type: LegacySystemType) -> LegacySystemAnalysis:
        """Analyze a specific legacy system."""
        # Count files and lines
        file_count = 0
        total_lines = 0
        python_files = []
        
        for file_path in system_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                total_lines += lines
                file_count += 1
                python_files.append(str(file_path))
            except Exception:
                pass
        
        # Estimate complexity
        if total_lines < 1000:
            complexity = "LOW"
        elif total_lines < 5000:
            complexity = "MEDIUM"
        elif total_lines < 15000:
            complexity = "HIGH"
        else:
            complexity = "VERY_HIGH"
        
        # Check last modification
        last_modified = datetime.fromtimestamp(max(
            os.path.getmtime(f) for f in system_path.rglob("*") if os.path.isfile(f)
        ) if list(system_path.rglob("*")) else datetime.now())
        
        # Determine recommended action
        if total_lines < 500:
            recommended_action = "ARCHIVE"  # Small systems, safe to archive
        elif system_path.name in ["governance_unified", "execution_unified", "indira_cognitive"]:
            recommended_action = "KEEP"  # These are the unified systems
        else:
            recommended_action = "ARCHIVE"  # Legacy systems should be archived
        
        return LegacySystemAnalysis(
            system_name=system_path.name,
            system_type=system_type,
            path=str(system_path),
            file_count=file_count,
            total_lines=total_lines,
            estimated_complexity=complexity,
            active_usage=not recommended_action == "ARCHIVE",
            last_modified=last_modified,
            dependencies=[],
            functionality_overlap=[],
            migration_complexity=complexity,
            recommended_action=recommended_action,
            notes=f"Legacy {system_type.value} system with {file_count} Python files"
        )
    
    def _generate_consolidation_plan(self, analyses: List[LegacySystemAnalysis]) -> ConsolidationPlan:
        """Generate consolidation plan from analyses."""
        # Prioritize by complexity and lines of code
        prioritized = sorted(
            [a for a in analyses if a.recommended_action == "ARCHIVE"],
            key=lambda x: (x.total_lines, x.estimated_complexity),
            reverse=True
        )
        
        migration_priority = [a.system_name for a in prioritized]
        
        # Estimate migration time (rough estimate: 1000 lines = 1 day)
        total_legacy_lines = sum(a.total_lines for a in prioritized)
        estimated_days = max(1, total_legacy_lines // 1000)
        
        # Risk assessment
        if total_legacy_lines < 10000:
            risk_assessment = "LOW"
        elif total_legacy_lines < 50000:
            risk_assessment = "MEDIUM"
        else:
            risk_assessment = "HIGH"
        
        return ConsolidationPlan(
            legacy_systems=analyses,
            migration_priority=migration_priority,
            estimated_migration_time_days=estimated_days,
            risk_assessment=risk_assessment,
            recommended_timeline=f"{estimated_days} days for safe migration"
        )
    
    def archive_legacy_system(self, system_name: str, archive_dir: str = "archive") -> bool:
        """
        Archive a legacy system.
        
        Args:
            system_name: Name of the system to archive
            archive_dir: Archive directory
            
        Returns:
            Success status
        """
        if system_name not in self._legacy_systems:
            logger.error(f"[LEGACY_ANALYZER] System {system_name} not found in analysis")
            return False
        
        system_analysis = self._legacy_systems[system_name]
        
        if system_analysis.recommended_action != "ARCHIVE":
            logger.warning(f"[LEGACY_ANALYZER] System {system_name} recommended action is {system_analysis.recommended_action}")
            return False
        
        try:
            source_path = Path(system_analysis.path)
            archive_path = Path(archive_dir) / f"{system_name}_archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create archive directory
            archive_path.mkdir(parents=True, exist_ok=True)
            
            # Move files to archive
            import shutil
            shutil.move(str(source_path), str(archive_path / source_path.name))
            
            logger.info(f"[LEGACY_ANALYZER] Archived {system_name} to {archive_path}")
            return True
            
        except Exception as e:
            logger.error(f"[LEGACY_ANALYZER] Failed to archive {system_name}: {e}")
            return False
    
    def get_analysis_report(self) -> Dict[str, Any]:
        """Get comprehensive analysis report."""
        if not self._legacy_systems:
            return {"message": "No legacy systems analyzed yet. Run analyze_legacy_systems() first."}
        
        total_files = sum(a.file_count for a in self._legacy_systems.values())
        total_lines = sum(a.total_lines for a in self._legacy_systems.values())
        
        by_type = {}
        for analysis in self._legacy_systems.values():
            system_type = analysis.system_type.value
            if system_type not in by_type:
                by_type[system_type] = {"count": 0, "files": 0, "lines": 0}
            by_type[system_type]["count"] += 1
            by_type[system_type]["files"] += analysis.file_count
            by_type[system_type]["lines"] += analysis.total_lines
        
        return {
            "total_systems": len(self._legacy_systems),
            "total_files": total_files,
            "total_lines": total_lines,
            "by_type": by_type,
            "systems": [
                {
                    "name": analysis.system_name,
                    "type": analysis.system_type.value,
                    "files": analysis.file_count,
                    "lines": analysis.total_lines,
                    "complexity": analysis.estimated_complexity,
                    "recommended_action": analysis.recommended_action,
                    "notes": analysis.notes
                }
                for analysis in self._legacy_systems.values()
            ]
        }


# Singleton instance
_legacy_analyzer: Optional[LegacySystemAnalyzer] = None
_legacy_analyzer_lock = object()  # Using object as lock for simplicity

def get_legacy_analyzer() -> LegacySystemAnalyzer:
    """Get the singleton legacy analyzer instance."""
    global _legacy_analyzer
    if _legacy_analyzer is None:
        _legacy_analyzer = LegacySystemAnalyzer()
    return _legacy_analyzer


__all__ = [
    "LegacySystemType",
    "LegacySystemAnalysis",
    "ConsolidationPlan",
    "LegacySystemAnalyzer",
    "get_legacy_analyzer",
]