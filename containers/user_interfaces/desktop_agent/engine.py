"""
DIX VISION v42.2+ Desktop Agent - Core Engine
Main orchestration engine for the Desktop Agent System
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from flask import Flask, jsonify, request

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "governance"))
sys.path.append(str(Path(__file__).parent.parent / "coordination_layer"))
sys.path.append(str(Path(__file__).parent.parent / "system"))


class DesktopAgentEngine:
    """Core orchestration engine for Desktop Agent System."""
    
    def __init__(self):
        """Initialize the Desktop Agent Engine."""
        self.logger = logging.getLogger("desktop_agent_engine")
        self.logger.setLevel(logging.INFO)
        
        # Core components
        self._orchestrator: Optional[Any] = None
        self._authority_router: Optional[Any] = None
        self._session_manager: Optional[Any] = None
        self._activity_tracker: Optional[Any] = None
        
        # State management
        self._running = False
        self._initialized = False
        
        # Configuration
        self._config: Dict[str, Any] = {}
        
        # Flask app for health checks
        self.app = Flask(__name__)
        self._setup_flask_routes()
        
        self.logger.info("Desktop Agent Engine initialized")
    
    def _setup_flask_routes(self):
        """Setup Flask routes for health checks and status."""
        @self.app.route('/health')
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "running": self._running,
                "initialized": self._initialized
            }), 200
        
        @self.app.route('/status')
        def status_check():
            """Detailed status endpoint."""
            return jsonify(self.get_status()), 200
        
        @self.app.route('/')
        def index():
            """Root endpoint."""
            return jsonify({
                "name": "DIX VISION v42.2+ Desktop Agent",
                "version": "42.2.0",
                "phase": "Phase 9 - Complete (All Phases)",
                "status": "operational"
            }), 200
        
        # Voice system endpoints
        @self.app.route('/voice/status')
        def voice_status():
            """Voice system status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("voice"):
                return jsonify(self._orchestrator._layer_orchestrators["voice"].get_status()), 200
            return jsonify({"error": "Voice system not available"}), 503
        
        @self.app.route('/voice/start', methods=['POST'])
        def voice_start():
            """Start voice listening."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("voice"):
                import asyncio
                try:
                    # Get event loop or create one
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    success = loop.run_until_complete(
                        self._orchestrator._layer_orchestrators["voice"].execute_workflow({
                            "id": "manual_start",
                            "action": "start_listening"
                        })
                    )
                    if success:
                        return jsonify({"status": "started"}), 200
                    else:
                        return jsonify({"error": "Failed to start voice listening"}), 500
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
            return jsonify({"error": "Voice system not available"}), 503
        
        @self.app.route('/voice/stop', methods=['POST'])
        def voice_stop():
            """Stop voice listening."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("voice"):
                import asyncio
                try:
                    # Get event loop or create one
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    success = loop.run_until_complete(
                        self._orchestrator._layer_orchestrators["voice"].execute_workflow({
                            "id": "manual_stop",
                            "action": "stop_listening"
                        })
                    )
                    if success:
                        return jsonify({"status": "stopped"}), 200
                    else:
                        return jsonify({"error": "Failed to stop voice listening"}), 500
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
            return jsonify({"error": "Voice system not available"}), 503
        
        @self.app.route('/voice/speak', methods=['POST'])
        def voice_speak():
            """Speak text through voice system."""
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({"error": "Missing text parameter"}), 400
            
            text = data['text']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("voice"):
                import asyncio
                try:
                    # Get event loop or create one
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    success = loop.run_until_complete(
                        self._orchestrator._layer_orchestrators["voice"].execute_workflow({
                            "id": "manual_speak",
                            "action": "speak",
                            "text": text
                        })
                    )
                    if success:
                        return jsonify({"status": "speaking", "text": text}), 200
                    else:
                        return jsonify({"error": "Failed to speak text"}), 500
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
            return jsonify({"error": "Voice system not available"}), 503
        
        # Browser system endpoints
        @self.app.route('/browser/status')
        def browser_status():
            """Browser system status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("browser"):
                return jsonify(self._orchestrator._layer_orchestrators["browser"].get_status()), 200
            return jsonify({"error": "Browser system not available"}), 503
        
        @self.app.route('/browser/navigate', methods=['POST'])
        def browser_navigate():
            """Navigate browser to URL."""
            data = request.get_json()
            if not data or 'url' not in data:
                return jsonify({"error": "Missing url parameter"}), 400
            
            url = data['url']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("browser"):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(
                    self._orchestrator._layer_orchestrators["browser"].execute_workflow({
                        "id": "manual_navigate",
                        "action": "navigate",
                        "url": url
                    })
                )
                if success:
                    return jsonify({"status": "navigated", "url": url}), 200
                else:
                    return jsonify({"error": "Failed to navigate"}), 500
            return jsonify({"error": "Browser system not available"}), 503
        
        @self.app.route('/browser/click', methods=['POST'])
        def browser_click():
            """Click element on page."""
            data = request.get_json()
            if not data or 'selector' not in data:
                return jsonify({"error": "Missing selector parameter"}), 400
            
            selector = data['selector']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("browser"):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(
                    self._orchestrator._layer_orchestrators["browser"].execute_workflow({
                        "id": "manual_click",
                        "action": "click",
                        "selector": selector
                    })
                )
                if success:
                    return jsonify({"status": "clicked", "selector": selector}), 200
                else:
                    return jsonify({"error": "Failed to click element"}), 500
            return jsonify({"error": "Browser system not available"}), 503
        
        @self.app.route('/browser/tabs', methods=['GET'])
        def browser_tabs():
            """Get browser tabs."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("browser"):
                browser_orch = self._orchestrator._layer_orchestrators["browser"]
                if browser_orch._tab_manager:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    tabs = loop.run_until_complete(browser_orch._tab_manager.get_all_tabs())
                    return jsonify({"tabs": tabs}), 200
            return jsonify({"error": "Browser system not available"}), 503
        
        @self.app.route('/browser/tabs', methods=['POST'])
        def browser_create_tab():
            """Create new browser tab."""
            data = request.get_json()
            url = data.get('url', None) if data else None
            
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("browser"):
                browser_orch = self._orchestrator._layer_orchestrators["browser"]
                if browser_orch._tab_manager:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    tab_id = loop.run_until_complete(browser_orch.create_tab(url))
                    if tab_id:
                        return jsonify({"status": "created", "tab_id": tab_id}), 200
                    else:
                        return jsonify({"error": "Failed to create tab"}), 500
            return jsonify({"error": "Browser system not available"}), 503
        
        # Learning system endpoints
        @self.app.route('/learning/status')
        def learning_status():
            """Learning system status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("learning"):
                return jsonify(self._orchestrator._layer_orchestrators["learning"].get_status()), 200
            return jsonify({"error": "Learning system not available"}), 503
        
        @self.app.route('/learning/analyze_platform', methods=['POST'])
        def learning_analyze_platform():
            """Analyze a platform."""
            data = request.get_json()
            if not data or 'platform_id' not in data or 'url' not in data:
                return jsonify({"error": "Missing platform_id or url parameter"}), 400
            
            platform_id = data['platform_id']
            url = data['url']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("learning"):
                learning_orch = self._orchestrator._layer_orchestrators["learning"]
                if learning_orch._platform_profiler:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    success = loop.run_until_complete(
                        learning_orch.execute_workflow({
                            "id": "analyze_platform",
                            "action": "analyze_platform",
                            "platform_id": platform_id,
                            "url": url
                        })
                    )
                    if success:
                        return jsonify({"status": "analyzed", "platform_id": platform_id}), 200
                    else:
                        return jsonify({"error": "Failed to analyze platform"}), 500
            return jsonify({"error": "Learning system not available"}), 503
        
        @self.app.route('/learning/platforms', methods=['GET'])
        def learning_platforms():
            """Get learned platforms."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("learning"):
                learning_orch = self._orchestrator._layer_orchestrators["learning"]
                if learning_orch._platform_profiler:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    profiles = loop.run_until_complete(learning_orch._platform_profiler.get_all_profiles())
                    return jsonify({"platforms": profiles}), 200
            return jsonify({"error": "Learning system not available"}), 503
        
        @self.app.route('/learning/workflows', methods=['GET'])
        def learning_workflows():
            """Get learned workflow patterns."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("learning"):
                learning_orch = self._orchestrator._layer_orchestrators["learning"]
                if learning_orch._workflow_profiler:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    patterns = loop.run_until_complete(learning_orch._workflow_profiler.get_all_patterns())
                    return jsonify({"patterns": patterns}), 200
            return jsonify({"error": "Learning system not available"}), 503
        
        # Desktop system endpoints
        @self.app.route('/desktop/status')
        def desktop_status():
            """Desktop system status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("desktop"):
                return jsonify(self._orchestrator._layer_orchestrators["desktop"].get_status()), 200
            return jsonify({"error": "Desktop system not available"}), 503
        
        @self.app.route('/desktop/click', methods=['POST'])
        def desktop_click():
            """Click at specified coordinates."""
            data = request.get_json()
            if not data or 'x' not in data or 'y' not in data:
                return jsonify({"error": "Missing x or y parameter"}), 400
            
            x = data['x']
            y = data['y']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("desktop"):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(
                    self._orchestrator._layer_orchestrators["desktop"].execute_workflow({
                        "id": "manual_click",
                        "action": "click",
                        "x": x,
                        "y": y
                    })
                )
                if success:
                    return jsonify({"status": "clicked", "x": x, "y": y}), 200
                else:
                    return jsonify({"error": "Failed to click"}), 500
            return jsonify({"error": "Desktop system not available"}), 503
        
        @self.app.route('/desktop/type', methods=['POST'])
        def desktop_type():
            """Type text using keyboard."""
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({"error": "Missing text parameter"}), 400
            
            text = data['text']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("desktop"):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(
                    self._orchestrator._layer_orchestrators["desktop"].execute_workflow({
                        "id": "manual_type",
                        "action": "type",
                        "text": text
                    })
                )
                if success:
                    return jsonify({"status": "typed", "text": text}), 200
                else:
                    return jsonify({"error": "Failed to type text"}), 500
            return jsonify({"error": "Desktop system not available"}), 503
        
        @self.app.route('/desktop/applications', methods=['GET'])
        def desktop_applications():
            """Get desktop applications."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("desktop"):
                desktop_orch = self._orchestrator._layer_orchestrators["desktop"]
                if desktop_orch._application_manager:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    applications = loop.run_until_complete(desktop_orch._application_manager.get_all_applications())
                    return jsonify({"applications": applications}), 200
            return jsonify({"error": "Desktop system not available"}), 503
        
        @self.app.route('/desktop/applications', methods=['POST'])
        def desktop_create_application():
            """Create new application."""
            data = request.get_json()
            app_id = data.get('app_id', None) if data else None
            name = data.get('name', None) if data else None
            
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("desktop"):
                desktop_orch = self._orchestrator._layer_orchestrators["desktop"]
                if desktop_orch._application_manager:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(
                        desktop_orch.execute_workflow({
                            "id": "create_application",
                            "action": "start_application",
                            "app_id": app_id,
                            "name": name
                        })
                    )
                    if result:
                        return jsonify({"status": "created", "app_id": app_id}), 200
                    else:
                        return jsonify({"error": "Failed to create application"}), 500
            return jsonify({"error": "Desktop system not available"}), 503
        
        @self.app.route('/desktop/windows', methods=['GET'])
        def desktop_windows():
            """Get desktop windows."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("desktop"):
                desktop_orch = self._orchestrator._layer_orchestrators["desktop"]
                if desktop_orch._window_manager:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    windows = loop.run_until_complete(desktop_orch._window_manager.get_all_windows())
                    return jsonify({"windows": windows}), 200
            return jsonify({"error": "Desktop system not available"}), 503
        
        # Document intelligence endpoints
        @self.app.route('/documents/status')
        def documents_status():
            """Document intelligence status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("documents"):
                return jsonify(self._orchestrator._layer_orchestrators["documents"].get_status()), 200
            return jsonify({"error": "Document intelligence not available"}), 503
        
        @self.app.route('/documents/process', methods=['POST'])
        def documents_process():
            """Process a document."""
            data = request.get_json()
            if not data or 'document_id' not in data or 'file_path' not in data:
                return jsonify({"error": "Missing document_id or file_path parameter"}), 400
            
            document_id = data['document_id']
            file_path = data['file_path']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("documents"):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(
                    self._orchestrator._layer_orchestrators["documents"].execute_workflow({
                        "id": "process_document",
                        "action": "process_document",
                        "document_id": document_id,
                        "file_path": file_path
                    })
                )
                if success:
                    return jsonify({"status": "processed", "document_id": document_id}), 200
                else:
                    return jsonify({"error": "Failed to process document"}), 500
            return jsonify({"error": "Document intelligence not available"}), 503
        
        @self.app.route('/documents/search', methods=['POST'])
        def documents_search():
            """Search documents."""
            data = request.get_json()
            if not data or 'query' not in data:
                return jsonify({"error": "Missing query parameter"}), 400
            
            query = data['query']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("documents"):
                documents_orch = self._orchestrator._layer_orchestrators["documents"]
                if documents_orch._document_processor:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    results = loop.run_until_complete(documents_orch._document_processor.search_documents(query))
                    return jsonify({"results": results}), 200
            return jsonify({"error": "Document intelligence not available"}), 503
        
        @self.app.route('/documents/ocr', methods=['POST'])
        def documents_ocr():
            """Extract text using OCR."""
            data = request.get_json()
            if not data or 'ocr_id' not in data or 'image_path' not in data:
                return jsonify({"error": "Missing ocr_id or image_path parameter"}), 400
            
            ocr_id = data['ocr_id']
            image_path = data['image_path']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("documents"):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(
                    self._orchestrator._layer_orchestrators["documents"].execute_workflow({
                        "id": "extract_ocr",
                        "action": "extract_ocr",
                        "ocr_id": ocr_id,
                        "image_path": image_path
                    })
                )
                if success:
                    return jsonify({"status": "extracted", "ocr_id": ocr_id}), 200
                else:
                    return jsonify({"error": "Failed to extract OCR text"}), 500
            return jsonify({"error": "Document intelligence not available"}), 503
        
        # Research assistant endpoints
        @self.app.route('/research/status')
        def research_status():
            """Research assistant status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("research"):
                return jsonify(self._orchestrator._layer_orchestrators["research"].get_status()), 200
            return jsonify({"error": "Research assistant not available"}), 503
        
        @self.app.route('/research/query', methods=['POST'])
        def research_query():
            """Execute a research query."""
            data = request.get_json()
            if not data or 'query_id' not in data or 'query_text' not in data:
                return jsonify({"error": "Missing query_id or query_text parameter"}), 400
            
            query_id = data['query_id']
            query_text = data['query_text']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("research"):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(
                    self._orchestrator._layer_orchestrators["research"].execute_workflow({
                        "id": "execute_query",
                        "action": "execute_query",
                        "query_id": query_id,
                        "query_text": query_text
                    })
                )
                if success:
                    return jsonify({"status": "executed", "query_id": query_id}), 200
                else:
                    return jsonify({"error": "Failed to execute research query"}), 500
            return jsonify({"error": "Research assistant not available"}), 503
        
        @self.app.route('/research/fact_check', methods=['POST'])
        def research_fact_check():
            """Perform fact-checking on a statement."""
            data = request.get_json()
            if not data or 'statement' not in data:
                return jsonify({"error": "Missing statement parameter"}), 400
            
            statement = data['statement']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("research"):
                research_orch = self._orchestrator._layer_orchestrators["research"]
                if research_orch._research_engine:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(research_orch._research_engine.fact_check(statement))
                    return jsonify(result), 200
            return jsonify({"error": "Research assistant not available"}), 503
        
        # Notifications endpoints
        @self.app.route('/notifications/status')
        def notifications_status():
            """Notifications system status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("notifications"):
                return jsonify(self._orchestrator._layer_orchestrators["notifications"].get_status()), 200
            return jsonify({"error": "Notifications system not available"}), 503
        
        @self.app.route('/notifications/create', methods=['POST'])
        def notifications_create():
            """Create a new notification."""
            data = request.get_json()
            if not data or 'notification_id' not in data or 'title' not in data or 'message' not in data:
                return jsonify({"error": "Missing notification_id, title, or message parameter"}), 400
            
            notification_id = data['notification_id']
            title = data['title']
            message = data['message']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("notifications"):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(
                    self._orchestrator._layer_orchestrators["notifications"].execute_workflow({
                        "id": "create_notification",
                        "action": "create_notification",
                        "notification_id": notification_id,
                        "title": title,
                        "message": message
                    })
                )
                if success:
                    return jsonify({"status": "created", "notification_id": notification_id}), 200
                else:
                    return jsonify({"error": "Failed to create notification"}), 500
            return jsonify({"error": "Notifications system not available"}), 503
        
        @self.app.route('/notifications/alerts', methods=['POST'])
        def notifications_alerts():
            """Create a new alert."""
            data = request.get_json()
            if not data or 'alert_id' not in data or 'name' not in data:
                return jsonify({"error": "Missing alert_id or name parameter"}), 400
            
            alert_id = data['alert_id']
            name = data['name']
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("notifications"):
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                success = loop.run_until_complete(
                    self._orchestrator._layer_orchestrators["notifications"].execute_workflow({
                        "id": "create_alert",
                        "action": "create_alert",
                        "alert_id": alert_id,
                        "name": name
                    })
                )
                if success:
                    return jsonify({"status": "created", "alert_id": alert_id}), 200
                else:
                    return jsonify({"error": "Failed to create alert"}), 500
            return jsonify({"error": "Notifications system not available"}), 503
        
        # Phase 9 layer status endpoints
        @self.app.route('/presence/status')
        def presence_status():
            """Presence system status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("presence"):
                return jsonify(self._orchestrator._layer_orchestrators["presence"].get_status()), 200
            return jsonify({"error": "Presence system not available"}), 503
        
        @self.app.route('/automation/status')
        def automation_status():
            """Automation system status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("automation"):
                return jsonify(self._orchestrator._layer_orchestrators["automation"].get_status()), 200
            return jsonify({"error": "Automation system not available"}), 503
        
        @self.app.route('/security/status')
        def security_status():
            """Security system status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("security"):
                return jsonify(self._orchestrator._layer_orchestrators["security"].get_status()), 200
            return jsonify({"error": "Security system not available"}), 503
        
        @self.app.route('/memory/status')
        def memory_status():
            """Memory system status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("memory"):
                return jsonify(self._orchestrator._layer_orchestrators["memory"].get_status()), 200
            return jsonify({"error": "Memory system not available"}), 503
        
        @self.app.route('/integrations/status')
        def integrations_status():
            """Integrations system status endpoint."""
            if self._orchestrator and self._orchestrator._layer_orchestrators.get("integrations"):
                return jsonify(self._orchestrator._layer_orchestrators["integrations"].get_status()), 200
            return jsonify({"error": "Integrations system not available"}), 503
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize all Desktop Agent components."""
        try:
            self.logger.info("Initializing Desktop Agent components...")
            
            # Load configuration
            self._config = config or {}
            
            # Initialize orchestrator (will be imported after creation)
            from orchestrator import DesktopAgentOrchestrator
            self._orchestrator = DesktopAgentOrchestrator(self)
            await self._orchestrator.initialize()
            
            # Initialize authority router
            from authority_router import DesktopAgentAuthorityRouter
            self._authority_router = DesktopAgentAuthorityRouter()
            await self._authority_router.initialize()
            
            # Initialize session manager
            from session_manager import DesktopAgentSessionManager
            self._session_manager = DesktopAgentSessionManager()
            await self._session_manager.initialize()
            
            # Initialize activity tracker
            from activity_tracker import DesktopAgentActivityTracker
            self._activity_tracker = DesktopAgentActivityTracker()
            await self._activity_tracker.initialize()
            
            self._initialized = True
            self.logger.info("Desktop Agent components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Desktop Agent: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the Desktop Agent Engine."""
        try:
            if not self._initialized:
                await self.initialize()
            
            self.logger.info("Starting Desktop Agent Engine...")
            
            # Start orchestrator
            if self._orchestrator:
                await self._orchestrator.start()
            
            # Start session manager
            if self._session_manager:
                await self._session_manager.start()
            
            # Start activity tracker
            if self._activity_tracker:
                await self._activity_tracker.start()
            
            self._running = True
            self.logger.info("Desktop Agent Engine started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Desktop Agent Engine: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the Desktop Agent Engine."""
        try:
            self.logger.info("Stopping Desktop Agent Engine...")
            
            # Stop activity tracker
            if self._activity_tracker:
                await self._activity_tracker.stop()
            
            # Stop session manager
            if self._session_manager:
                await self._session_manager.stop()
            
            # Stop orchestrator
            if self._orchestrator:
                await self._orchestrator.stop()
            
            self._running = False
            self.logger.info("Desktop Agent Engine stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Desktop Agent Engine: {e}")
            return False
    
    @property
    def orchestrator(self) -> Optional[Any]:
        """Get the orchestrator component."""
        return self._orchestrator
    
    @property
    def authority_router(self) -> Optional[Any]:
        """Get the authority router component."""
        return self._authority_router
    
    @property
    def session_manager(self) -> Optional[Any]:
        """Get the session manager component."""
        return self._session_manager
    
    @property
    def activity_tracker(self) -> Optional[Any]:
        """Get the activity tracker component."""
        return self._activity_tracker
    
    @property
    def is_running(self) -> bool:
        """Check if the engine is running."""
        return self._running
    
    @property
    def is_initialized(self) -> bool:
        """Check if the engine is initialized."""
        return self._initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the engine."""
        return {
            "running": self._running,
            "initialized": self._initialized,
            "orchestrator_status": self._orchestrator.get_status() if self._orchestrator else None,
            "authority_router_status": self._authority_router.get_status() if self._authority_router else None,
            "session_manager_status": self._session_manager.get_status() if self._session_manager else None,
            "activity_tracker_status": self._activity_tracker.get_status() if self._activity_tracker else None,
        }
    
    def run_flask_server(self, host='0.0.0.0', port=9186):
        """Run the Flask server in a separate thread."""
        from threading import Thread
        import threading
        
        def run_app():
            self.app.run(host=host, port=port, threaded=True)
        
        flask_thread = Thread(target=run_app, daemon=True)
        flask_thread.start()
        self.logger.info(f"Flask server started on {host}:{port}")
        return flask_thread


async def main():
    """Main entry point for Desktop Agent Engine."""
    engine = DesktopAgentEngine()
    
    try:
        # Start Flask server for health checks
        engine.run_flask_server()
        
        success = await engine.start()
        if success:
            print("Desktop Agent Engine started successfully")
            # Keep engine running
            while engine.is_running:
                await asyncio.sleep(1)
        else:
            print("Failed to start Desktop Agent Engine")
            sys.exit(1)
    except KeyboardInterrupt:
        print("Shutting down Desktop Agent Engine...")
        await engine.stop()
    except Exception as e:
        print(f"Desktop Agent Engine error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
