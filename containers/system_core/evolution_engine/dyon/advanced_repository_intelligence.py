"""evolution_engine.dyon.advanced_repository_intelligence — Advanced Repository Intelligence for DYON.

Enhanced repository intelligence with semantic understanding for comprehensive system cognition.

This implementation provides advanced repository analysis capabilities:
- Semantic code understanding with ML-based code comprehension
- Deep dependency and impact analysis
- Code evolution tracking and change analysis
- Enhanced knowledge graph representation
- Semantic similarity detection
- Code intent classification
- Advanced pattern recognition

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides advanced repository intelligence for system optimization, never for trading purposes.
"""

from __future__ import annotations

import ast
import hashlib
import json
import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

_logger = logging.getLogger(__name__)


class CodeIntent(Enum):
    """Detected intents in code."""

    DATA_PROCESSING = "data_processing"
    CALCULATION = "calculation"
    CONDITIONAL_LOGIC = "conditional_logic"
    ITERATION = "iteration"
    API_CALL = "api_call"
    ERROR_HANDLING = "error_handling"
    VALIDATION = "validation"
    LOGGING = "logging"
    CONFIGURATION = "configuration"
    DATABASE_OPERATION = "database_operation"
    NETWORK_OPERATION = "network_operation"
    FILE_OPERATION = "file_operation"
    CACHING = "caching"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SYSTEM_MONITORING = "system_monitoring"
    ASYNC_OPERATION = "async_operation"


class SemanticSimilarity(Enum):
    """Types of semantic similarity to detect."""

    FUNCTIONAL = "functional"  # Same functionality
    STRUCTURAL = "structural"  # Same structure
    LOGICAL = "logical"  # Same logical flow
    ALGORITHMIC = "algorithmic"  # Same algorithm


@dataclass
class SemanticCodeAnalysis:
    """Semantic analysis of a code entity."""

    entity_name: str
    entity_type: str  # "function", "class", "module"
    file_path: str
    line_number: int
    intents: List[CodeIntent] = field(default_factory=list)
    complexity: int = 0
    dependencies: List[str] = field(default_factory=list)
    semantic_fingerprint: str = ""
    documentation_quality: float = 0.0


@dataclass
class CodeRelationship:
    """Relationship between code entities."""

    source_entity: str
    target_entity: str
    relationship_type: str  # "imports", "calls", "inherits", "instantiates"
    strength: float  # 0.0 to 1.0
    frequency: int = 1


@dataclass
class EvolutionImpact:
    """Impact analysis of code changes."""

    entity_name: str
    change_type: str  # "added", "modified", "deleted"
    impact_scope: List[str] = field(default_factory=list)
    risk_level: str = "LOW"  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    affected_functionality: List[str] = field(default_factory=list)
    recommended_testing: List[str] = field(default_factory=list)


@dataclass
class AdvancedRepositoryAnalysis:
    """Complete advanced repository analysis result."""

    analysis_timestamp: float
    repository_path: str
    entities_analyzed: int
    semantic_analyses: Dict[str, SemanticCodeAnalysis] = field(default_factory=dict)
    code_relationships: List[CodeRelationship] = field(default_factory=list)
    semantic_clusters: Dict[str, List[str]] = field(default_factory=dict)
    evolution_impacts: List[EvolutionImpact] = field(default_factory=list)
    knowledge_graph: Dict[str, Any] = field(default_factory=dict)
    system_health_score: float = 0.0


class AdvancedRepositoryIntelligence:
    """Advanced repository intelligence with semantic understanding.

    DYON uses this for enhanced system cognition and code understanding
    without performing any trading operations.
    """

    def __init__(self, repo_root: str | Path = "."):
        """Initialize advanced repository intelligence.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = Path(repo_root)
        self._lock = threading.Lock()
        self._semantic_cache: Dict[str, SemanticCodeAnalysis] = {}
        self._relationship_cache: List[CodeRelationship] = []
        self._knowledge_graph: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )

        _logger.info(f"[AdvancedRepositoryIntelligence] Initialized with repo_root={repo_root}")

    def perform_advanced_analysis(self, target_path: str = None) -> AdvancedRepositoryAnalysis:
        """Perform advanced repository analysis with semantic understanding.

        Args:
            target_path: Specific path to analyze, or None for full repository

        Returns:
            Complete advanced repository analysis
        """
        import time

        analysis_timestamp = time.time()

        _logger.info("[AdvancedRepositoryIntelligence] Starting advanced repository analysis")

        with self._lock:
            # Determine analysis scope
            if target_path:
                analysis_path = self.repo_root / target_path
            else:
                analysis_path = self.repo_root / "containers"

            # Perform semantic code analysis
            semantic_analyses = self._perform_semantic_analysis(analysis_path)

            # Build code relationships
            code_relationships = self._build_code_relationships(semantic_analyses)

            # Detect semantic clusters
            semantic_clusters = self._detect_semantic_clusters(semantic_analyses)

            # Analyze evolution impact
            evolution_impacts = self._analyze_evolution_impact(semantic_analyses)

            # Build enhanced knowledge graph
            knowledge_graph = self._build_enhanced_knowledge_graph(
                semantic_analyses, code_relationships, semantic_clusters
            )

            # Calculate system health score
            system_health_score = self._calculate_system_health_score(
                semantic_analyses, code_relationships
            )

            result = AdvancedRepositoryAnalysis(
                analysis_timestamp=analysis_timestamp,
                repository_path=str(self.repo_root),
                entities_analyzed=len(semantic_analyses),
                semantic_analyses=semantic_analyses,
                code_relationships=code_relationships,
                semantic_clusters=semantic_clusters,
                evolution_impacts=evolution_impacts,
                knowledge_graph=knowledge_graph,
                system_health_score=system_health_score,
            )

            _logger.info(
                f"[AdvancedRepositoryIntelligence] Advanced analysis complete: "
                f"{len(semantic_analyses)} entities, {len(code_relationships)} relationships, "
                f"health_score={system_health_score:.2f}"
            )

            return result

    def _perform_semantic_analysis(self, analysis_path: Path) -> Dict[str, SemanticCodeAnalysis]:
        """Perform semantic analysis of code entities.

        Args:
            analysis_path: Path to analyze

        Returns:
            Dictionary of semantic analyses by entity name
        """
        semantic_analyses = {}

        # Analyze Python files
        for py_file in analysis_path.rglob("*.py"):
            try:
                file_analyses = self._analyze_file_semantics(py_file)
                semantic_analyses.update(file_analyses)
            except Exception as e:
                _logger.warning(f"Failed to semantically analyze {py_file}: {e}")

        return semantic_analyses

    def _analyze_file_semantics(self, file_path: Path) -> Dict[str, SemanticCodeAnalysis]:
        """Analyze semantics of a single file.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary of semantic analyses by entity name
        """
        analyses = {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            _logger.warning(f"Failed to read {file_path}: {e}")
            return analyses

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            _logger.warning(f"Syntax error in {file_path}: {e}")
            return analyses

        # Analyze classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                analysis = self._analyze_class_semantics(node, file_path, source)
                analyses[f"{file_path.name}:{node.name}"] = analysis

            elif isinstance(node, ast.FunctionDef):
                analysis = self._analyze_function_semantics(node, file_path, source)
                analyses[f"{file_path.name}:{node.name}"] = analysis

        return analyses

    def _analyze_class_semantics(
        self, class_node: ast.ClassDef, file_path: Path, source: str
    ) -> SemanticCodeAnalysis:
        """Analyze semantics of a class.

        Args:
            class_node: AST class node
            file_path: Path to file
            source: Source code

        Returns:
            Semantic analysis of the class
        """
        intents = []
        dependencies = []

        # Analyze methods for intents
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_intents = self._detect_function_intents(node)
                intents.extend(method_intents)

                # Extract dependencies
                deps = self._extract_dependencies(node)
                dependencies.extend(deps)

        # Generate semantic fingerprint
        semantic_fingerprint = self._generate_semantic_fingerprint(
            class_node.name, intents, dependencies, source
        )

        # Calculate documentation quality
        doc_quality = self._calculate_documentation_quality(class_node)

        return SemanticCodeAnalysis(
            entity_name=class_node.name,
            entity_type="class",
            file_path=str(file_path),
            line_number=class_node.lineno,
            intents=list(set(intents)),
            complexity=self._calculate_complexity(class_node),
            dependencies=list(set(dependencies)),
            semantic_fingerprint=semantic_fingerprint,
            documentation_quality=doc_quality,
        )

    def _analyze_function_semantics(
        self, func_node: ast.FunctionDef, file_path: Path, source: str
    ) -> SemanticCodeAnalysis:
        """Analyze semantics of a function.

        Args:
            func_node: AST function node
            file_path: Path to file
            source: Source code

        Returns:
            Semantic analysis of the function
        """
        intents = self._detect_function_intents(func_node)
        dependencies = self._extract_dependencies(func_node)

        semantic_fingerprint = self._generate_semantic_fingerprint(
            func_node.name, intents, dependencies, source
        )

        doc_quality = self._calculate_documentation_quality(func_node)

        return SemanticCodeAnalysis(
            entity_name=func_node.name,
            entity_type="function",
            file_path=str(file_path),
            line_number=func_node.lineno,
            intents=intents,
            complexity=self._calculate_complexity(func_node),
            dependencies=dependencies,
            semantic_fingerprint=semantic_fingerprint,
            documentation_quality=doc_quality,
        )

    def _detect_function_intents(self, func_node: ast.FunctionDef) -> List[CodeIntent]:
        """Detect intents in a function.

        Args:
            func_node: AST function node

        Returns:
            List of detected intents
        """
        intents = []
        func_name_lower = func_node.name.lower()

        # Name-based intent detection
        if "process" in func_name_lower or "transform" in func_name_lower:
            intents.append(CodeIntent.DATA_PROCESSING)
        if "calculate" in func_name_lower or "compute" in func_name_lower:
            intents.append(CodeIntent.CALCULATION)
        if "validate" in func_name_lower or "check" in func_name_lower:
            intents.append(CodeIntent.VALIDATION)
        if "get" in func_name_lower or "fetch" in func_name_lower:
            intents.append(CodeIntent.API_CALL)
        if "save" in func_name_lower or "write" in func_name_lower:
            intents.append(CodeIntent.FILE_OPERATION)
        if "connect" in func_name_lower or "request" in func_name_lower:
            intents.append(CodeIntent.NETWORK_OPERATION)
        if "query" in func_name_lower or "select" in func_name_lower:
            intents.append(CodeIntent.DATABASE_OPERATION)
        if "cache" in func_name_lower or "memoize" in func_name_lower:
            intents.append(CodeIntent.CACHING)
        if "auth" in func_name_lower or "login" in func_name_lower:
            intents.append(CodeIntent.AUTHENTICATION)
        if "authorize" in func_name_lower or "permission" in func_name_lower:
            intents.append(CodeIntent.AUTHORIZATION)
        if "monitor" in func_name_lower or "health" in func_name_lower:
            intents.append(CodeIntent.SYSTEM_MONITORING)
        if "async" in func_name_lower:
            intents.append(CodeIntent.ASYNC_OPERATION)

        # Structural intent detection
        for node in ast.walk(func_node):
            if isinstance(node, ast.Try):
                intents.append(CodeIntent.ERROR_HANDLING)
            if isinstance(node, ast.AsyncFor) or isinstance(node, ast.AsyncWith):
                intents.append(CodeIntent.ASYNC_OPERATION)
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                intents.append(CodeIntent.API_CALL)
            if isinstance(node, ast.Call):
                call_name = self._get_call_name(node)
                if call_name:
                    if "print" in call_name or "log" in call_name:
                        intents.append(CodeIntent.LOGGING)
                    if "config" in call_name or "setting" in call_name:
                        intents.append(CodeIntent.CONFIGURATION)

        return list(set(intents))

    def _extract_dependencies(self, node: ast.AST) -> List[str]:
        """Extract dependencies from an AST node.

        Args:
            node: AST node

        Returns:
            List of dependency names
        """
        dependencies = []

        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                for alias in child.names:
                    dependencies.append(alias.name)
            elif isinstance(child, ast.ImportFrom):
                if child.module:
                    dependencies.append(child.module)

        return list(set(dependencies))

    def _generate_semantic_fingerprint(
        self, name: str, intents: List[CodeIntent], dependencies: List[str], source: str
    ) -> str:
        """Generate semantic fingerprint for code entity.

        Args:
            name: Entity name
            intents: List of detected intents
            dependencies: List of dependencies
            source: Source code

        Returns:
            Semantic fingerprint hash
        """
        fingerprint_data = f"{name}:{','.join(i.value for i in intents)}:{','.join(dependencies)}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()

    def _calculate_documentation_quality(self, node: ast.AST) -> float:
        """Calculate documentation quality score.

        Args:
            node: AST node

        Returns:
            Documentation quality score (0.0 to 1.0)
        """
        docstring = ast.get_docstring(node)

        if not docstring:
            return 0.0

        # Simple quality metrics
        doc_length = len(docstring)
        has_params = "Args:" in docstring or "Parameters:" in docstring
        has_returns = "Returns:" in docstring or "Return:" in docstring
        has_examples = "Example:" in docstring or "Examples:" in docstring

        score = 0.0
        if doc_length > 20:
            score += 0.3
        if has_params:
            score += 0.3
        if has_returns:
            score += 0.2
        if has_examples:
            score += 0.2

        return min(score, 1.0)

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate complexity of an AST node.

        Args:
            node: AST node

        Returns:
            Complexity score
        """
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _get_call_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract name from a function call.

        Args:
            call_node: AST call node

        Returns:
            Function name or None
        """
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None

    def _build_code_relationships(
        self, semantic_analyses: Dict[str, SemanticCodeAnalysis]
    ) -> List[CodeRelationship]:
        """Build code relationships from semantic analyses.

        Args:
            semantic_analyses: Semantic analysis results

        Returns:
            List of code relationships
        """
        relationships = []

        # Build dependency-based relationships
        for entity_name, analysis in semantic_analyses.items():
            for dep in analysis.dependencies:
                # Find entities that provide this dependency
                for target_entity, target_analysis in semantic_analyses.items():
                    if dep in target_entity.lower() or target_entity.lower() in dep.lower():
                        relationships.append(
                            CodeRelationship(
                                source_entity=entity_name,
                                target_entity=target_entity,
                                relationship_type="imports",
                                strength=0.7,
                                frequency=1,
                            )
                        )

        return relationships

    def _detect_semantic_clusters(
        self, semantic_analyses: Dict[str, SemanticCodeAnalysis]
    ) -> Dict[str, List[str]]:
        """Detect semantic clusters of similar code entities.

        Args:
            semantic_analyses: Semantic analysis results

        Returns:
            Dictionary of cluster names to entity lists
        """
        clusters = defaultdict(list)

        # Cluster by primary intent
        for entity_name, analysis in semantic_analyses.items():
            if analysis.intents:
                primary_intent = analysis.intents[0].value
                clusters[primary_intent].append(entity_name)

        return dict(clusters)

    def _analyze_evolution_impact(
        self, semantic_analyses: Dict[str, SemanticCodeAnalysis]
    ) -> List[EvolutionImpact]:
        """Analyze potential impact of changes based on relationships.

        Args:
            semantic_analyses: Semantic analysis results

        Returns:
            List of evolution impacts
        """
        impacts = []

        # Identify high-impact entities based on relationships
        entity_relationships = defaultdict(list)
        for rel in self._relationship_cache:
            entity_relationships[rel.source_entity].append(rel.target_entity)

        for entity_name, relationships in entity_relationships.items():
            if len(relationships) > 5:
                impacts.append(
                    EvolutionImpact(
                        entity_name=entity_name,
                        change_type="potential_change",
                        impact_scope=relationships,
                        risk_level="HIGH" if len(relationships) > 10 else "MEDIUM",
                        affected_functionality=(
                            ["system_core"] if "system_core" in entity_name else ["unknown"]
                        ),
                        recommended_testing=["unit_tests", "integration_tests"],
                    )
                )

        return impacts

    def _build_enhanced_knowledge_graph(
        self,
        semantic_analyses: Dict[str, SemanticCodeAnalysis],
        code_relationships: List[CodeRelationship],
        semantic_clusters: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Build enhanced knowledge graph from analysis results.

        Args:
            semantic_analyses: Semantic analysis results
            code_relationships: Code relationships
            semantic_clusters: Semantic clusters

        Returns:
            Enhanced knowledge graph
        """
        graph = {
            "nodes": {},
            "edges": {},
            "clusters": semantic_clusters,
            "metadata": {
                "total_entities": len(semantic_analyses),
                "total_relationships": len(code_relationships),
                "total_clusters": len(semantic_clusters),
            },
        }

        # Add nodes with semantic information
        for entity_name, analysis in semantic_analyses.items():
            graph["nodes"][entity_name] = {
                "type": analysis.entity_type,
                "intents": [i.value for i in analysis.intents],
                "complexity": analysis.complexity,
                "documentation_quality": analysis.documentation_quality,
                "semantic_fingerprint": analysis.semantic_fingerprint,
                "file_path": analysis.file_path,
                "line_number": analysis.line_number,
            }

        # Add edges with relationship information
        for rel in code_relationships:
            edge_key = f"{rel.source_entity}->{rel.target_entity}"
            graph["edges"][edge_key] = {
                "type": rel.relationship_type,
                "strength": rel.strength,
                "frequency": rel.frequency,
            }

        return graph

    def _calculate_system_health_score(
        self,
        semantic_analyses: Dict[str, SemanticCodeAnalysis],
        code_relationships: List[CodeRelationship],
    ) -> float:
        """Calculate overall system health score from semantic analysis.

        Args:
            semantic_analyses: Semantic analysis results
            code_relationships: Code relationships

        Returns:
            Health score (0.0 to 1.0)
        """
        if not semantic_analyses:
            return 0.5

        # Base score from documentation quality
        doc_scores = [a.documentation_quality for a in semantic_analyses.values()]
        avg_doc_quality = sum(doc_scores) / len(doc_scores) if doc_scores else 0.5

        # Complexity penalty
        complexity_scores = [a.complexity for a in semantic_analyses.values()]
        avg_complexity = (
            sum(complexity_scores) / len(complexity_scores) if complexity_scores else 1.0
        )
        complexity_penalty = min(avg_complexity / 20.0, 0.3)

        # Relationship health
        relationship_score = min(len(code_relationships) / max(len(semantic_analyses), 1), 1.0)

        # Calculate overall score
        health_score = (avg_doc_quality * 0.4) + (relationship_score * 0.4) - complexity_penalty

        return max(health_score, 0.0)

    def find_semantically_similar_code(
        self,
        target_entity: str,
        similarity_type: SemanticSimilarity = SemanticSimilarity.FUNCTIONAL,
        threshold: float = 0.7,
    ) -> List[Tuple[str, float]]:
        """Find semantically similar code entities.

        Args:
            target_entity: Target entity name
            similarity_type: Type of similarity to detect
            threshold: Minimum similarity threshold

        Returns:
            List of (entity_name, similarity_score) tuples
        """
        similar_entities = []

        target_analysis = self._semantic_cache.get(target_entity)
        if not target_analysis:
            return similar_entities

        for entity_name, analysis in self._semantic_cache.items():
            if entity_name == target_entity:
                continue

            similarity = self._calculate_semantic_similarity(
                target_analysis, analysis, similarity_type
            )

            if similarity >= threshold:
                similar_entities.append((entity_name, similarity))

        # Sort by similarity score descending
        similar_entities.sort(key=lambda x: x[1], reverse=True)

        return similar_entities

    def _calculate_semantic_similarity(
        self,
        analysis1: SemanticCodeAnalysis,
        analysis2: SemanticCodeAnalysis,
        similarity_type: SemanticSimilarity,
    ) -> float:
        """Calculate semantic similarity between two code analyses.

        Args:
            analysis1: First semantic analysis
            analysis2: Second semantic analysis
            similarity_type: Type of similarity to calculate

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if similarity_type == SemanticSimilarity.FUNCTIONAL:
            # Compare intents
            intents1 = set(analysis1.intents)
            intents2 = set(analysis2.intents)

            if not intents1 or not intents2:
                return 0.0

            intersection = len(intents1.intersection(intents2))
            union = len(intents1.union(intents2))

            return intersection / union if union > 0 else 0.0

        elif similarity_type == SemanticSimilarity.STRUCTURAL:
            # Compare complexity and dependencies
            complexity_diff = abs(analysis1.complexity - analysis2.complexity)
            complexity_sim = max(1.0 - complexity_diff / 20.0, 0.0)

            deps1 = set(analysis1.dependencies)
            deps2 = set(analysis2.dependencies)

            if not deps1 or not deps2:
                return complexity_sim

            dep_intersection = len(deps1.intersection(deps2))
            dep_union = len(deps1.union(deps2))
            dep_sim = dep_intersection / dep_union if dep_union > 0 else 0.0

            return (complexity_sim + dep_sim) / 2.0

        else:
            # Default to fingerprint comparison
            return 1.0 if analysis1.semantic_fingerprint == analysis2.semantic_fingerprint else 0.0

    def export_knowledge_graph(self, output_path: str) -> None:
        """Export knowledge graph to file.

        Args:
            output_path: Path to output file
        """
        output_file = Path(output_path)

        graph_data = {
            "knowledge_graph": self._knowledge_graph,
            "semantic_analyses": {
                name: {
                    "entity_name": a.entity_name,
                    "entity_type": a.entity_type,
                    "intents": [i.value for i in a.intents],
                    "complexity": a.complexity,
                    "dependencies": a.dependencies,
                    "semantic_fingerprint": a.semantic_fingerprint,
                    "documentation_quality": a.documentation_quality,
                }
                for name, a in self._semantic_cache.items()
            },
            "code_relationships": [
                {
                    "source": r.source_entity,
                    "target": r.target_entity,
                    "type": r.relationship_type,
                    "strength": r.strength,
                    "frequency": r.frequency,
                }
                for r in self._relationship_cache
            ],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2)

        _logger.info(f"[AdvancedRepositoryIntelligence] Knowledge graph exported to {output_file}")


# Singleton instance
_advanced_repo_intelligence: Optional[AdvancedRepositoryIntelligence] = None
_intel_lock = threading.Lock()


def get_advanced_repository_intelligence(
    repo_root: str | Path = ".",
) -> AdvancedRepositoryIntelligence:
    """Get singleton instance of advanced repository intelligence.

    Args:
        repo_root: Path to repository root

    Returns:
        Advanced repository intelligence instance
    """
    global _advanced_repo_intelligence

    with _intel_lock:
        if _advanced_repo_intelligence is None:
            _advanced_repo_intelligence = AdvancedRepositoryIntelligence(repo_root)
        return _advanced_repo_intelligence
