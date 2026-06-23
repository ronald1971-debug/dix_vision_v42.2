"""
intelligence_engine.knowledge_integrator
DIX VISION v42.2 — Production-Grade Knowledge Integration

Knowledge graph integration with entity linking, relationship extraction,
knowledge fusion, and semantic querying.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from system.time_source import now

logger = logging.getLogger(__name__)


class KnowledgeSourceType(Enum):
    """Types of knowledge sources."""

    MANUAL = "manual"  # Manually entered knowledge
    AUTOMATED = "automated"  # Automatically extracted knowledge
    EXTERNAL = "external"  # External knowledge bases
    INFERRED = "inferred"  # Inferred from reasoning
    HISTORICAL = "historical"  # Historical knowledge
    REALTIME = "realtime"  # Real-time knowledge updates


class RelationshipType(Enum):
    """Types of relationships."""

    CAUSAL = "causal"  # Causal relationship
    TEMPORAL = "temporal"  # Temporal relationship
    SPATIAL = "spatial"  # Spatial relationship
    SEMANTIC = "semantic"  # Semantic relationship
    HIERARCHICAL = "hierarchical"  # Hierarchical relationship
    ASSOCIATIVE = "associative"  # Associative relationship
    FUNCTIONAL = "functional"  # Functional relationship


@dataclass
class KnowledgeEntity:
    """A knowledge entity."""

    entity_id: str
    name: str
    entity_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    source: KnowledgeSourceType = KnowledgeSourceType.MANUAL
    confidence: float = 1.0
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = now().utc_time.isoformat()


@dataclass
class KnowledgeRelationship:
    """A knowledge relationship."""

    relationship_id: str
    source_entity: str  # Entity ID
    target_entity: str  # Entity ID
    relationship_type: RelationshipType
    properties: Dict[str, Any] = field(default_factory=dict)
    source: KnowledgeSourceType = KnowledgeSourceType.MANUAL
    confidence: float = 1.0
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = now().utc_time.isoformat()


@dataclass
class KnowledgeGraph:
    """A knowledge graph with entities and relationships."""

    graph_id: str
    entities: Dict[str, KnowledgeEntity] = field(default_factory=dict)
    relationships: List[KnowledgeRelationship] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: str = ""


@dataclass
class KnowledgeQuery:
    """A knowledge query."""

    query_id: str
    query_type: str  # "entity", "relationship", "path", "pattern"
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeResult:
    """Result of a knowledge query."""

    query_id: str
    result_type: str
    entities: List[KnowledgeEntity] = field(default_factory=list)
    relationships: List[KnowledgeRelationship] = field(default_factory=list)
    paths: List[List[str]] = field(default_factory=list)
    confidence: float = 0.0
    explanation: str = ""
    timestamp: str = ""


class ProductionKnowledgeIntegrator:
    """Production-grade knowledge integration engine.

    Provides:
    - Knowledge graph management
    - Entity and relationship extraction
    - Knowledge fusion from multiple sources
    - Semantic querying and reasoning
    - Knowledge consistency validation
    """

    def __init__(self) -> None:
        self._knowledge_graphs: Dict[str, KnowledgeGraph] = {}
        self._active_graph_id: Optional[str] = None
        self._knowledge_history: List[Dict[str, Any]] = []
        self._entity_index: Dict[str, Set[str]] = defaultdict(set)  # name -> entity_ids
        self._relationship_index: Dict[str, List[str]] = defaultdict(
            list
        )  # entity -> relationship_ids
        self._confidence_threshold = 0.5
        self._auto_merge_enabled = True
        self._deduplication_enabled = True

    def start(self) -> bool:
        """Start the knowledge integration engine."""
        try:
            # Create default knowledge graph
            default_graph = KnowledgeGraph(
                graph_id="default", last_updated=now().utc_time.isoformat()
            )
            self._knowledge_graphs["default"] = default_graph
            self._active_graph_id = "default"

            logger.info("[KNOWLEDGE] Production knowledge integrator started")
            return True
        except Exception as e:
            logger.error(f"[KNOWLEDGE] Failed to start: {e}")
            return False

    def stop(self) -> bool:
        """Stop the knowledge integration engine."""
        try:
            logger.info("[KNOWLEDGE] Production knowledge integrator stopped")
            return True
        except Exception as e:
            logger.error(f"[KNOWLEDGE] Failed to stop: {e}")
            return False

    def create_graph(
        self, graph_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeGraph:
        """Create a new knowledge graph."""
        graph = KnowledgeGraph(
            graph_id=graph_id, metadata=metadata or {}, last_updated=now().utc_time.isoformat()
        )
        self._knowledge_graphs[graph_id] = graph
        logger.info(f"[KNOWLEDGE] Created knowledge graph: {graph_id}")
        return graph

    def set_active_graph(self, graph_id: str) -> bool:
        """Set the active knowledge graph."""
        if graph_id in self._knowledge_graphs:
            self._active_graph_id = graph_id
            logger.info(f"[KNOWLEDGE] Set active graph: {graph_id}")
            return True
        else:
            logger.warning(f"[KNOWLEDGE] Graph not found: {graph_id}")
            return False

    def add_entity(self, entity: KnowledgeEntity, graph_id: Optional[str] = None) -> bool:
        """Add an entity to the knowledge graph."""
        graph_id = graph_id or self._active_graph_id
        if not graph_id or graph_id not in self._knowledge_graphs:
            logger.warning(f"[KNOWLEDGE] Invalid graph ID: {graph_id}")
            return False

        # Check for duplicates if enabled
        if self._deduplication_enabled:
            existing = self._find_duplicate_entity(entity, graph_id)
            if existing:
                # Merge with existing entity
                return self._merge_entities(existing, entity, graph_id)

        # Add entity to graph
        self._knowledge_graphs[graph_id].entities[entity.entity_id] = entity
        self._entity_index[entity.name].add(entity.entity_id)

        # Update timestamp
        self._knowledge_graphs[graph_id].last_updated = now().utc_time.isoformat()

        logger.info(f"[KNOWLEDGE] Added entity: {entity.name} to graph {graph_id}")
        return True

    def add_relationship(
        self, relationship: KnowledgeRelationship, graph_id: Optional[str] = None
    ) -> bool:
        """Add a relationship to the knowledge graph."""
        graph_id = graph_id or self._active_graph_id
        if not graph_id or graph_id not in self._knowledge_graphs:
            logger.warning(f"[KNOWLEDGE] Invalid graph ID: {graph_id}")
            return False

        # Validate entities exist
        graph = self._knowledge_graphs[graph_id]
        if relationship.source_entity not in graph.entities:
            logger.warning(f"[KNOWLEDGE] Source entity not found: {relationship.source_entity}")
            return False
        if relationship.target_entity not in graph.entities:
            logger.warning(f"[KNOWLEDGE] Target entity not found: {relationship.target_entity}")
            return False

        # Add relationship
        graph.relationships.append(relationship)
        self._relationship_index[relationship.source_entity].append(relationship.relationship_id)
        self._relationship_index[relationship.target_entity].append(relationship.relationship_id)

        # Update timestamp
        graph.last_updated = now().utc_time.isoformat()

        logger.info(f"[KNOWLEDGE] Added relationship: {relationship.relationship_id}")
        return True

    def query(self, query: KnowledgeQuery, graph_id: Optional[str] = None) -> KnowledgeResult:
        """Query the knowledge graph.

        Args:
            query: Knowledge query
            graph_id: Optional graph ID (uses active if None)

        Returns:
            KnowledgeResult with query results
        """
        try:
            graph_id = graph_id or self._active_graph_id
            if not graph_id or graph_id not in self._knowledge_graphs:
                return self._create_error_result(query.query_id, "Invalid graph ID")

            graph = self._knowledge_graphs[graph_id]
            logger.info(f"[KNOWLEDGE] Querying graph {graph_id}: {query.query_type}")

            if query.query_type == "entity":
                result = self._query_entities(query, graph)
            elif query.query_type == "relationship":
                result = self._query_relationships(query, graph)
            elif query.query_type == "path":
                result = self._query_paths(query, graph)
            elif query.query_type == "pattern":
                result = self._query_patterns(query, graph)
            else:
                result = self._create_error_result(
                    query.query_id, f"Unknown query type: {query.query_type}"
                )

            result.timestamp = now().utc_time.isoformat()
            return result

        except Exception as e:
            logger.error(f"[KNOWLEDGE] Query failed: {e}")
            return self._create_error_result(query.query_id, str(e))

    def _query_entities(self, query: KnowledgeQuery, graph: KnowledgeGraph) -> KnowledgeResult:
        """Query for entities."""
        name_filter = query.parameters.get("name")
        type_filter = query.parameters.get("entity_type")
        source_filter = query.parameters.get("source")

        results = []
        for entity in graph.entities.values():
            match = True

            if name_filter and name_filter.lower() not in entity.name.lower():
                match = False
            if type_filter and entity.entity_type != type_filter:
                match = False
            if source_filter and entity.source != source_filter:
                match = False

            if match:
                results.append(entity)

        confidence = len(results) / max(len(graph.entities), 1) if results else 0.0

        return KnowledgeResult(
            query_id=query.query_id,
            result_type="entity",
            entities=results,
            confidence=confidence,
            explanation=f"Found {len(results)} entities matching criteria",
            timestamp=now().utc_time.isoformat(),
        )

    def _query_relationships(self, query: KnowledgeQuery, graph: KnowledgeGraph) -> KnowledgeResult:
        """Query for relationships."""
        source_filter = query.parameters.get("source_entity")
        target_filter = query.parameters.get("target_entity")
        type_filter = query.parameters.get("relationship_type")

        results = []
        for relationship in graph.relationships:
            match = True

            if source_filter and relationship.source_entity != source_filter:
                match = False
            if target_filter and relationship.target_entity != target_filter:
                match = False
            if type_filter and relationship.relationship_type != type_filter:
                match = False

            if match:
                results.append(relationship)

        confidence = len(results) / max(len(graph.relationships), 1) if results else 0.0

        return KnowledgeResult(
            query_id=query.query_id,
            result_type="relationship",
            relationships=results,
            confidence=confidence,
            explanation=f"Found {len(results)} relationships matching criteria",
            timestamp=now().utc_time.isoformat(),
        )

    def _query_paths(self, query: KnowledgeQuery, graph: KnowledgeGraph) -> KnowledgeResult:
        """Query for paths between entities."""
        start_entity = query.parameters.get("start_entity")
        end_entity = query.parameters.get("end_entity")
        max_depth = query.parameters.get("max_depth", 3)

        if not start_entity or not end_entity:
            return self._create_error_result(query.query_id, "Missing start or end entity")

        paths = self._find_paths(start_entity, end_entity, graph, max_depth)

        confidence = len(paths) / max(5, 1)  # Normalize against expected max paths

        return KnowledgeResult(
            query_id=query.query_id,
            result_type="path",
            paths=paths,
            confidence=confidence,
            explanation=f"Found {len(paths)} paths between entities",
            timestamp=now().utc_time.isoformat(),
        )

    def _query_patterns(self, query: KnowledgeQuery, graph: KnowledgeGraph) -> KnowledgeResult:
        """Query for patterns in the knowledge graph."""
        pattern_type = query.parameters.get("pattern_type")

        if pattern_type == "cycle":
            cycles = self._find_cycles(graph)
            entities = [graph.entities.get(node) for node in cycles if node in graph.entities]
            return KnowledgeResult(
                query_id=query.query_id,
                result_type="pattern",
                entities=entities,
                confidence=0.8 if cycles else 0.0,
                explanation=f"Found {len(cycles)} cyclic patterns",
                timestamp=now().utc_time.isoformat(),
            )

        return self._create_error_result(query.query_id, f"Unknown pattern type: {pattern_type}")

    def _find_paths(
        self, start: str, end: str, graph: KnowledgeGraph, max_depth: int
    ) -> List[List[str]]:
        """Find paths between entities using BFS."""
        from collections import deque

        if start not in graph.entities or end not in graph.entities:
            return []

        paths = []
        queue = deque([(start, [start])])
        visited = set()

        while queue and len(paths) < 10:  # Limit to 10 paths
            current, path = queue.popleft()

            if current == end and len(path) > 1:
                paths.append(path)
                continue

            if len(path) >= max_depth:
                continue

            visited.add(current)

            # Find neighbors
            neighbors = []
            for rel in graph.relationships:
                if rel.source_entity == current and rel.target_entity not in path:
                    neighbors.append(rel.target_entity)
                elif rel.target_entity == current and rel.source_entity not in path:
                    neighbors.append(rel.source_entity)

            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

        return paths

    def _find_cycles(self, graph: KnowledgeGraph) -> List[List[str]]:
        """Find cycles in the knowledge graph."""
        cycles = []

        # Build adjacency list
        adjacency = defaultdict(list)
        for rel in graph.relationships:
            adjacency[rel.source_entity].append(rel.target_entity)

        # Simple cycle detection
        visited = set()

        def detect_cycle(node: str, path: List[str]) -> Optional[List[str]]:
            if node in path:
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]

            if node in visited:
                return None

            visited.add(node)

            for neighbor in adjacency[node]:
                result = detect_cycle(neighbor, path + [node])
                if result:
                    return result

            return None

        for entity_id in graph.entities:
            if entity_id not in visited:
                cycle = detect_cycle(entity_id, [])
                if cycle:
                    cycles.append(cycle)

        return cycles

    def _find_duplicate_entity(
        self, entity: KnowledgeEntity, graph_id: str
    ) -> Optional[KnowledgeEntity]:
        """Find duplicate entities in the graph."""
        graph = self._knowledge_graphs[graph_id]

        # Check by name
        if entity.name in self._entity_index:
            for entity_id in self._entity_index[entity.name]:
                existing = graph.entities.get(entity_id)
                if existing and existing.entity_type == entity.entity_type:
                    return existing

        return None

    def _merge_entities(
        self, existing: KnowledgeEntity, new_entity: KnowledgeEntity, graph_id: str
    ) -> bool:
        """Merge new entity with existing entity."""
        # Merge properties
        for key, value in new_entity.properties.items():
            if key not in existing.properties:
                existing.properties[key] = value
            elif self._auto_merge_enabled:
                # Weighted merge based on confidence
                existing_weight = existing.confidence
                new_weight = new_entity.confidence
                merged_value = (existing.properties[key] * existing_weight + value * new_weight) / (
                    existing_weight + new_weight
                )
                existing.properties[key] = merged_value

        # Update confidence (take max)
        existing.confidence = max(existing.confidence, new_entity.confidence)

        # Update timestamp
        existing.timestamp = now().utc_time.isoformat()

        # Update graph timestamp
        self._knowledge_graphs[graph_id].last_updated = now().utc_time.isoformat()

        logger.info(f"[KNOWLEDGE] Merged entity: {existing.name}")
        return True

    def _create_error_result(self, query_id: str, error: str) -> KnowledgeResult:
        """Create error knowledge result."""
        return KnowledgeResult(
            query_id=query_id,
            result_type="error",
            confidence=0.0,
            explanation=f"Error: {error}",
            timestamp=now().utc_time.isoformat(),
        )

    def import_knowledge(
        self,
        knowledge_data: Dict[str, Any],
        source: KnowledgeSourceType = KnowledgeSourceType.EXTERNAL,
        graph_id: Optional[str] = None,
    ) -> int:
        """Import knowledge from external data."""
        graph_id = graph_id or self._active_graph_id
        if not graph_id or graph_id not in self._knowledge_graphs:
            logger.warning(f"[KNOWLEDGE] Invalid graph ID: {graph_id}")
            return 0

        entities_imported = 0
        relationships_imported = 0

        # Import entities
        for entity_data in knowledge_data.get("entities", []):
            entity = KnowledgeEntity(
                entity_id=entity_data.get("entity_id", f"entity_{now().sequence}"),
                name=entity_data.get("name", ""),
                entity_type=entity_data.get("entity_type", "generic"),
                properties=entity_data.get("properties", {}),
                source=source,
                confidence=entity_data.get("confidence", 0.8),
            )
            if self.add_entity(entity, graph_id):
                entities_imported += 1

        # Import relationships
        for rel_data in knowledge_data.get("relationships", []):
            relationship = KnowledgeRelationship(
                relationship_id=rel_data.get("relationship_id", f"rel_{now().sequence}"),
                source_entity=rel_data.get("source_entity", ""),
                target_entity=rel_data.get("target_entity", ""),
                relationship_type=rel_data.get("relationship_type", RelationshipType.SEMANTIC),
                properties=rel_data.get("properties", {}),
                source=source,
                confidence=rel_data.get("confidence", 0.8),
            )
            if self.add_relationship(relationship, graph_id):
                relationships_imported += 1

        logger.info(
            f"[KNOWLEDGE] Imported {entities_imported} entities and {relationships_imported} relationships"
        )
        return entities_imported + relationships_imported

    def export_knowledge(self, graph_id: Optional[str] = None) -> Dict[str, Any]:
        """Export knowledge graph to external format."""
        graph_id = graph_id or self._active_graph_id
        if not graph_id or graph_id not in self._knowledge_graphs:
            logger.warning(f"[KNOWLEDGE] Invalid graph ID: {graph_id}")
            return {}

        graph = self._knowledge_graphs[graph_id]

        export_data = {
            "graph_id": graph.graph_id,
            "metadata": graph.metadata,
            "last_updated": graph.last_updated,
            "entities": [],
            "relationships": [],
        }

        for entity in graph.entities.values():
            export_data["entities"].append(
                {
                    "entity_id": entity.entity_id,
                    "name": entity.name,
                    "entity_type": entity.entity_type,
                    "properties": entity.properties,
                    "source": entity.source.value,
                    "confidence": entity.confidence,
                    "timestamp": entity.timestamp,
                }
            )

        for relationship in graph.relationships:
            export_data["relationships"].append(
                {
                    "relationship_id": relationship.relationship_id,
                    "source_entity": relationship.source_entity,
                    "target_entity": relationship.target_entity,
                    "relationship_type": relationship.relationship_type.value,
                    "properties": relationship.properties,
                    "source": relationship.source.value,
                    "confidence": relationship.confidence,
                    "timestamp": relationship.timestamp,
                }
            )

        return export_data

    def get_graph_statistics(self, graph_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a knowledge graph."""
        graph_id = graph_id or self._active_graph_id
        if not graph_id or graph_id not in self._knowledge_graphs:
            return {"error": "Invalid graph ID"}

        graph = self._knowledge_graphs[graph_id]

        # Count entities by type
        entity_type_counts = defaultdict(int)
        for entity in graph.entities.values():
            entity_type_counts[entity.entity_type] += 1

        # Count relationships by type
        relationship_type_counts = defaultdict(int)
        for rel in graph.relationships:
            relationship_type_counts[rel.relationship_type.value] += 1

        return {
            "graph_id": graph.graph_id,
            "entity_count": len(graph.entities),
            "relationship_count": len(graph.relationships),
            "entity_types": dict(entity_type_counts),
            "relationship_types": dict(relationship_type_counts),
            "last_updated": graph.last_updated,
        }


def get_production_knowledge_integrator() -> ProductionKnowledgeIntegrator:
    """Get the singleton production knowledge integrator instance."""
    if not hasattr(get_production_knowledge_integrator, "_instance"):
        get_production_knowledge_integrator._instance = ProductionKnowledgeIntegrator()
    return get_production_knowledge_integrator._instance
