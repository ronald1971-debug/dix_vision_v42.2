"""
Structured Logger - Structured logging for observability
"""

import logging
import json
from typing import Dict, Any
from datetime import datetime
from pathlib import Path


class StructuredLogger:
    """
    Structured logger for consistent log formatting.
    
    Provides JSON-structured logging with consistent fields
    for easier parsing and analysis.
    """
    
    def __init__(self, name: str, log_file: str = "dix_vision.log"):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            log_file: Log file path
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log(
        self,
        level: str,
        message: str,
        context: Dict[str, Any] = None,
    ) -> None:
        """
        Log a structured message.
        
        Args:
            level: Log level (info, warning, error, debug)
            message: Log message
            context: Additional context
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "context": context or {},
        }
        
        log_message = json.dumps(log_data)
        
        if level == "info":
            self.logger.info(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        elif level == "error":
            self.logger.error(log_message)
        elif level == "debug":
            self.logger.debug(log_message)
            
    def info(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log info message."""
        self.log("info", message, context)
        
    def warning(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log warning message."""
        self.log("warning", message, context)
        
    def error(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log error message."""
        self.log("error", message, context)
        
    def debug(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log debug message."""
        self.log("debug", message, context)
