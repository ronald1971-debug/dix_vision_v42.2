"""
DIX VISION v42.2+ Desktop Agent - Documents Layer Orchestrator
Document intelligence system orchestrator - Phase 6 implementation
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional


class DocumentsOrchestrator:
    """Documents layer orchestrator - coordinates document intelligence components."""
    
    def __init__(self, parent_orchestrator):
        """Initialize the documents orchestrator."""
        self.parent = parent_orchestrator
        self.logger = logging.getLogger("documents_orchestrator")
        self.logger.setLevel(logging.INFO)
        
        # Document intelligence components
        self._document_processor: Optional[Any] = None
        self._ocr_reader: Optional[Any] = None
        self._document_classifier: Optional[Any] = None
        
        # State
        self._initialized = False
        self._running = False
        
        # Workflow tracking
        self._active_workflows: Dict[str, asyncio.Task] = {}
        
        # Document intelligence status
        self._document_status = {
            "documents_processed": 0,
            "ocr_operations": 0,
            "classifications_performed": 0,
            "active_document": None,
        }
        
        self.logger.info("Documents Orchestrator created")
    
    async def initialize(self) -> bool:
        """Initialize the documents orchestrator."""
        try:
            self.logger.info("Initializing Documents Orchestrator...")
            
            # Initialize document processor
            try:
                import sys
                import os
                documents_dir = os.path.dirname(os.path.abspath(__file__))
                if documents_dir not in sys.path:
                    sys.path.insert(0, documents_dir)
                
                from document_processor import DocumentProcessor
                self._document_processor = DocumentProcessor()
                await self._document_processor.initialize()
                self.logger.info("Document Processor initialized")
            except ImportError as ie:
                self.logger.warning(f"Document processor import failed: {ie}")
                self._document_processor = None
            except Exception as e:
                self.logger.warning(f"Document processor initialization failed: {e}")
                self._document_processor = None
            
            # Initialize OCR reader
            try:
                from ocr_reader import OCRReader
                self._ocr_reader = OCRReader()
                await self._ocr_reader.initialize()
                self.logger.info("OCR Reader initialized")
            except ImportError as ie:
                self.logger.warning(f"OCR reader import failed: {ie}")
                self._ocr_reader = None
            except Exception as e:
                self.logger.warning(f"OCR reader initialization failed: {e}")
                self._ocr_reader = None
            
            # Initialize document classifier
            try:
                from document_classifier import DocumentClassifier
                self._document_classifier = DocumentClassifier()
                await self._document_classifier.initialize()
                self.logger.info("Document Classifier initialized")
            except ImportError as ie:
                self.logger.warning(f"Document classifier import failed: {ie}")
                self._document_classifier = None
            except Exception as e:
                self.logger.warning(f"Document classifier initialization failed: {e}")
                self._document_classifier = None
            
            self._initialized = True
            self.logger.info("Documents Orchestrator initialized successfully (Phase 6)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Documents Orchestrator: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the documents orchestrator."""
        try:
            if not self._initialized:
                await self.initialize()
            
            self.logger.info("Starting Documents Orchestrator...")
            
            # Start document components
            if self._document_processor:
                self.logger.info("Document Processor ready")
            
            if self._ocr_reader:
                self.logger.info("OCR Reader ready")
            
            if self._document_classifier:
                self.logger.info("Document Classifier ready")
            
            self._running = True
            self.logger.info("Documents Orchestrator started successfully (Phase 6)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Documents Orchestrator: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the documents orchestrator."""
        try:
            self.logger.info("Stopping Documents Orchestrator...")
            
            # Cancel active workflows
            for workflow_id, task in self._active_workflows.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self._active_workflows.clear()
            self._running = False
            self.logger.info("Documents Orchestrator stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Documents Orchestrator: {e}")
            return False
    
    async def execute_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Execute a document intelligence workflow (Phase 6 implementation)."""
        try:
            workflow_id = workflow.get("id", "unknown")
            
            self.logger.info(f"Executing document workflow: {workflow_id}")
            
            # Extract workflow details
            action = workflow.get("action", "")
            
            if action == "process_document" and self._document_processor:
                document_id = workflow.get("document_id", "")
                file_path = workflow.get("file_path", "")
                if document_id and file_path:
                    result = await self._document_processor.process_document(document_id, file_path)
                    if result:
                        self._document_status["documents_processed"] += 1
                        self._document_status["active_document"] = document_id
            
            elif action == "extract_ocr" and self._ocr_reader:
                ocr_id = workflow.get("ocr_id", "")
                image_path = workflow.get("image_path", "")
                if ocr_id and image_path:
                    result = await self._ocr_reader.extract_text(ocr_id, image_path)
                    if result:
                        self._document_status["ocr_operations"] += 1
            
            elif action == "classify_document" and self._document_classifier:
                document_id = workflow.get("document_id", "")
                text = workflow.get("text", "")
                if document_id and text:
                    result = await self._document_classifier.classify_document(document_id, text)
                    if result:
                        self._document_status["classifications_performed"] += 1
            
            self.logger.info(f"Document workflow {workflow_id} completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute document workflow: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "phase": "Phase 6 - Document Intelligence",
            "document_status": self._document_status,
            "active_workflows": len(self._active_workflows),
            "components_available": {
                "document_processor": self._document_processor is not None,
                "ocr_reader": self._ocr_reader is not None,
                "document_classifier": self._document_classifier is not None,
            },
            "component_statuses": {
                "document_processor": self._document_processor.get_status() if self._document_processor else None,
                "ocr_reader": self._ocr_reader.get_status() if self._ocr_reader else None,
                "document_classifier": self._document_classifier.get_status() if self._document_classifier else None,
            },
        }
    
    @property
    def document_processor(self) -> Optional[Any]:
        """Get the document processor instance."""
        return self._document_processor
    
    @property
    def ocr_reader(self) -> Optional[Any]:
        """Get the OCR reader instance."""
        return self._ocr_reader
    
    @property
    def document_classifier(self) -> Optional[Any]:
        """Get the document classifier instance."""
        return self._document_classifier
    
    @property
    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        return self._running