"""
DIX VISION v42.2+ Desktop Agent - Research Layer Orchestrator
Research assistant system orchestrator - Phase 7 implementation
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional


class ResearchOrchestrator:
    """Research layer orchestrator - coordinates research assistant components."""
    
    def __init__(self, parent_orchestrator):
        """Initialize the research orchestrator."""
        self.parent = parent_orchestrator
        self.logger = logging.getLogger("research_orchestrator")
        self.logger.setLevel(logging.INFO)
        
        # Research assistant components
        self._research_engine: Optional[Any] = None
        self._knowledge_graph: Optional[Any] = None
        self._citation_manager: Optional[Any] = None
        
        # State
        self._initialized = False
        self._running = False
        
        # Workflow tracking
        self._active_workflows: Dict[str, asyncio.Task] = {}
        
        # Research assistant status
        self._research_status = {
            "queries_executed": 0,
            "nodes_created": 0,
            "citations_added": 0,
            "active_query": None,
        }
        
        self.logger.info("Research Orchestrator created")
    
    async def initialize(self) -> bool:
        """Initialize the research orchestrator."""
        try:
            self.logger.info("Initializing Research Orchestrator...")
            
            # Initialize research engine
            try:
                import sys
                import os
                research_dir = os.path.dirname(os.path.abspath(__file__))
                if research_dir not in sys.path:
                    sys.path.insert(0, research_dir)
                
                from research_engine import ResearchEngine
                self._research_engine = ResearchEngine()
                await self._research_engine.initialize()
                self.logger.info("Research Engine initialized")
            except ImportError as ie:
                self.logger.warning(f"Research engine import failed: {ie}")
                self._research_engine = None
            except Exception as e:
                self.logger.warning(f"Research engine initialization failed: {e}")
                self._research_engine = None
            
            # Initialize knowledge graph
            try:
                from knowledge_graph import KnowledgeGraph
                self._knowledge_graph = KnowledgeGraph()
                await self._knowledge_graph.initialize()
                self.logger.info("Knowledge Graph initialized")
            except ImportError as ie:
                self.logger.warning(f"Knowledge graph import failed: {ie}")
                self._knowledge_graph = None
            except Exception as e:
                self.logger.warning(f"Knowledge graph initialization failed: {e}")
                self._knowledge_graph = None
            
            # Initialize citation manager
            try:
                from citation_manager import CitationManager
                self._citation_manager = CitationManager()
                await self._citation_manager.initialize()
                self.logger.info("Citation Manager initialized")
            except ImportError as ie:
                self.logger.warning(f"Citation manager import failed: {ie}")
                self._citation_manager = None
            except Exception as e:
                self.logger.warning(f"Citation manager initialization failed: {e}")
                self._citation_manager = None
            
            self._initialized = True
            self.logger.info("Research Orchestrator initialized successfully (Phase 7)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Research Orchestrator: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the research orchestrator."""
        try:
            if not self._initialized:
                await self.initialize()
            
            self.logger.info("Starting Research Orchestrator...")
            
            # Start research components
            if self._research_engine:
                self.logger.info("Research Engine ready")
            
            if self._knowledge_graph:
                self.logger.info("Knowledge Graph ready")
            
            if self._citation_manager:
                self.logger.info("Citation Manager ready")
            
            self._running = True
            self.logger.info("Research Orchestrator started successfully (Phase 7)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Research Orchestrator: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the research orchestrator."""
        try:
            self.logger.info("Stopping Research Orchestrator...")
            
            # Cancel active workflows
            for workflow_id, task in self._active_workflows.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self._active_workflows.clear()
            self._running = False
            self.logger.info("Research Orchestrator stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Research Orchestrator: {e}")
            return False
    
    async def execute_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Execute a research assistant workflow (Phase 7 implementation)."""
        try:
            workflow_id = workflow.get("id", "unknown")
            
            self.logger.info(f"Executing research workflow: {workflow_id}")
            
            # Extract workflow details
            action = workflow.get("action", "")
            
            if action == "execute_query" and self._research_engine:
                query_id = workflow.get("query_id", "")
                query_text = workflow.get("query_text", "")
                if query_id and query_text:
                    from research_engine import ResearchType
                    result = await self._research_engine.execute_query(
                        query_id,
                        query_text,
                        ResearchType.QUERY
                    )
                    if result:
                        self._research_status["queries_executed"] += 1
                        self._research_status["active_query"] = query_id
            
            elif action == "fact_check" and self._research_engine:
                statement = workflow.get("statement", "")
                if statement:
                    await self._research_engine.fact_check(statement)
                    self._research_status["queries_executed"] += 1
            
            elif action == "add_node" and self._knowledge_graph:
                node_id = workflow.get("node_id", "")
                node_type = workflow.get("node_type", "")
                label = workflow.get("label", "")
                if node_id and node_type and label:
                    from knowledge_graph import NodeType
                    result = await self._knowledge_graph.add_node(
                        node_id,
                        NodeType(node_type),
                        label,
                        workflow.get("properties", {})
                    )
                    if result:
                        self._research_status["nodes_created"] += 1
            
            elif action == "add_citation" and self._citation_manager:
                source_type = workflow.get("source_type", "")
                title = workflow.get("title", "")
                authors = workflow.get("authors", [])
                if title and authors:
                    from citation_manager import SourceType
                    result = await self._citation_manager.create_citation(
                        SourceType(source_type),
                        title,
                        authors,
                        **workflow.get("properties", {})
                    )
                    if result:
                        self._research_status["citations_added"] += 1
            
            self.logger.info(f"Research workflow {workflow_id} completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute research workflow: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "phase": "Phase 7 - Research Assistant",
            "research_status": self._research_status,
            "active_workflows": len(self._active_workflows),
            "components_available": {
                "research_engine": self._research_engine is not None,
                "knowledge_graph": self._knowledge_graph is not None,
                "citation_manager": self._citation_manager is not None,
            },
            "component_statuses": {
                "research_engine": self._research_engine.get_status() if self._research_engine else None,
                "knowledge_graph": self._knowledge_graph.get_status() if self._knowledge_graph else None,
                "citation_manager": self._citation_manager.get_status() if self._citation_manager else None,
            },
        }
    
    @property
    def research_engine(self) -> Optional[Any]:
        """Get the research engine instance."""
        return self._research_engine
    
    @property
    def knowledge_graph(self) -> Optional[Any]:
        """Get the knowledge graph instance."""
        return self._knowledge_graph
    
    @property
    def citation_manager(self) -> Optional[Any]:
        """Get the citation manager instance."""
        return self._citation_manager
    
    @property
    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        return self._running