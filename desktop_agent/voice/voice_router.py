"""
DIX VISION v42.2+ Desktop Agent - Voice Router
Main coordinator for voice system operations
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional
from enum import Enum


class VoiceState(Enum):
    """Voice system states."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


class VoiceCommandType(Enum):
    """Types of voice commands."""
    WAKE_WORD = "wake_word"
    SYSTEM_COMMAND = "system_command"
    QUERY = "query"
    ACTION = "action"
    UNKNOWN = "unknown"


class VoiceRouter:
    """Main router for voice system operations."""
    
    def __init__(self):
        """Initialize the Voice Router."""
        self.logger = logging.getLogger("voice_router")
        self.logger.setLevel(logging.INFO)
        
        # State management
        self._state = VoiceState.IDLE
        self._current_command: Optional[str] = None
        self._current_command_type = VoiceCommandType.UNKNOWN
        
        # Component references (to be initialized)
        self._wake_word_detector: Optional[Any] = None
        self._speech_to_text: Optional[Any] = None
        self._text_to_speech: Optional[Any] = None
        
        # Command queue
        self._command_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        
        # Statistics
        self._commands_processed = 0
        self._commands_successful = 0
        self._commands_failed = 0
        
        # Configuration
        self._config: Dict[str, Any] = {
            "wake_word_enabled": True,
            "wake_word_sensitivity": 0.5,
            "speech_timeout": 30,
            "max_command_length": 500,
        }
        
        self.logger.info("Voice Router initialized")
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the voice router and its components."""
        try:
            self.logger.info("Initializing Voice Router...")
            
            # Load configuration
            if config:
                self._config.update(config)
            
            # Initialize wake word detector
            try:
                import sys
                import os
                voice_dir = os.path.dirname(os.path.abspath(__file__))
                if voice_dir not in sys.path:
                    sys.path.insert(0, voice_dir)
                
                from wake_word import WakeWordDetector
                self._wake_word_detector = WakeWordDetector()
                await self._wake_word_detector.initialize()
                self.logger.info("Wake word detector initialized")
            except ImportError:
                self.logger.warning("Wake word detector not available")
            
            # Initialize speech to text
            try:
                from speech_to_text import SpeechToText
                self._speech_to_text = SpeechToText()
                await self._speech_to_text.initialize()
                self.logger.info("Speech to text initialized")
            except ImportError:
                self.logger.warning("Speech to text not available")
            
            # Initialize text to speech
            try:
                from text_to_speech import TextToSpeech
                self._text_to_speech = TextToSpeech()
                await self._text_to_speech.initialize()
                self.logger.info("Text to speech initialized")
            except ImportError:
                self.logger.warning("Text to speech not available")
            
            # Start command processing
            self._processing_task = asyncio.create_task(self._process_commands())
            
            self.logger.info("Voice Router initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Voice Router: {e}")
            return False
    
    async def start_listening(self) -> bool:
        """Start listening for voice commands."""
        try:
            if self._state != VoiceState.IDLE:
                self.logger.warning(f"Cannot start listening, current state: {self._state}")
                return False
            
            self._state = VoiceState.LISTENING
            self.logger.info("Started listening for voice commands")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start listening: {e}")
            return False
    
    async def stop_listening(self) -> bool:
        """Stop listening for voice commands."""
        try:
            if self._state == VoiceState.LISTENING:
                self._state = VoiceState.IDLE
                self.logger.info("Stopped listening for voice commands")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop listening: {e}")
            return False
    
    async def process_audio_input(self, audio_data: bytes) -> Optional[str]:
        """Process audio input and return transcribed text."""
        try:
            if not self._speech_to_text:
                self.logger.error("Speech to text not available")
                return None
            
            self._state = VoiceState.PROCESSING
            self.logger.info("Processing audio input...")
            
            # Transcribe audio
            text = await self._speech_to_text.transcribe(audio_data)
            
            if text:
                self.logger.info(f"Transcribed: {text}")
                await self._queue_command(text)
            else:
                self.logger.warning("No text transcribed from audio")
            
            self._state = VoiceState.LISTENING
            return text
            
        except Exception as e:
            self.logger.error(f"Failed to process audio input: {e}")
            self._state = VoiceState.ERROR
            return None
    
    async def speak(self, text: str) -> bool:
        """Convert text to speech and play it."""
        try:
            if not self._text_to_speech:
                self.logger.warning("Text to speech not available, text would be logged only")
                self.logger.info(f"Would speak: {text}")
                return True
            
            self._state = VoiceState.SPEAKING
            self.logger.info(f"Speaking: {text}")
            
            # Generate speech
            await self._text_to_speech.speak(text)
            
            self._state = VoiceState.IDLE
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to speak: {e}")
            self._state = VoiceState.ERROR
            return False
    
    async def _queue_command(self, command: str) -> None:
        """Queue a command for processing."""
        try:
            # Determine command type
            command_type = self._classify_command(command)
            
            command_data = {
                "command": command,
                "type": command_type.value,
                "timestamp": asyncio.get_event_loop().time(),
            }
            
            await self._command_queue.put(command_data)
            self.logger.info(f"Queued command: {command} (type: {command_type.value})")
            
        except Exception as e:
            self.logger.error(f"Failed to queue command: {e}")
    
    def _classify_command(self, command: str) -> VoiceCommandType:
        """Classify the type of voice command."""
        command_lower = command.lower().strip()
        
        # Check for wake word
        if any(wake_word in command_lower for wake_word in ["hey dex", "ok dex", "desktop agent"]):
            return VoiceCommandType.WAKE_WORD
        
        # Check for system commands
        system_keywords = ["stop", "pause", "resume", "status", "help", "exit"]
        if any(keyword in command_lower for keyword in system_keywords):
            return VoiceCommandType.SYSTEM_COMMAND
        
        # Check for queries
        query_keywords = ["what", "how", "why", "when", "where", "who", "tell me"]
        if any(keyword in command_lower for keyword in query_keywords):
            return VoiceCommandType.QUERY
        
        # Check for actions
        action_keywords = ["open", "close", "start", "launch", "go to", "navigate"]
        if any(keyword in command_lower for keyword in action_keywords):
            return VoiceCommandType.ACTION
        
        return VoiceCommandType.UNKNOWN
    
    async def _process_commands(self) -> None:
        """Process commands from the queue."""
        try:
            while True:
                command_data = await self._command_queue.get()
                
                try:
                    self._commands_processed += 1
                    command = command_data["command"]
                    command_type = command_data["type"]
                    
                    self.logger.info(f"Processing command: {command} (type: {command_type})")
                    
                    # Process based on command type
                    if command_type == VoiceCommandType.WAKE_WORD.value:
                        await self._handle_wake_word(command)
                    elif command_type == VoiceCommandType.SYSTEM_COMMAND.value:
                        await self._handle_system_command(command)
                    elif command_type == VoiceCommandType.QUERY.value:
                        await self._handle_query(command)
                    elif command_type == VoiceCommandType.ACTION.value:
                        await self._handle_action(command)
                    else:
                        await self._handle_unknown(command)
                    
                    self._commands_successful += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to process command {command_data}: {e}")
                    self._commands_failed += 1
                
                finally:
                    self._command_queue.task_done()
                    
        except asyncio.CancelledError:
            self.logger.info("Command processing cancelled")
        except Exception as e:
            self.logger.error(f"Command processing error: {e}")
    
    async def _handle_wake_word(self, command: str) -> None:
        """Handle wake word detection."""
        self.logger.info(f"Wake word detected: {command}")
        # Could trigger specific behavior on wake word
    
    async def _handle_system_command(self, command: str) -> None:
        """Handle system commands."""
        self.logger.info(f"System command: {command}")
        
        if "stop" in command.lower():
            await self.stop_listening()
        elif "status" in command.lower():
            status = self.get_status()
            await self.speak(f"Voice system status: {status['state']}")
    
    async def _handle_query(self, command: str) -> None:
        """Handle query commands."""
        self.logger.info(f"Query: {command}")
        # Would integrate with cognitive engines for query processing
        await self.speak("I heard your query. Processing is not yet implemented.")
    
    async def _handle_action(self, command: str) -> None:
        """Handle action commands."""
        self.logger.info(f"Action: {command}")
        # Would integrate with browser/desktop controllers for action execution
        await self.speak("I heard your action. Execution is not yet implemented.")
    
    async def _handle_unknown(self, command: str) -> None:
        """Handle unknown commands."""
        self.logger.info(f"Unknown command: {command}")
        await self.speak("I didn't understand that command.")
    
    async def stop(self) -> bool:
        """Stop the voice router."""
        try:
            self.logger.info("Stopping Voice Router...")
            
            # Stop processing
            if self._processing_task:
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    pass
            
            # Stop components
            if self._wake_word_detector:
                await self._wake_word_detector.stop()
            if self._speech_to_text:
                await self._speech_to_text.stop()
            if self._text_to_speech:
                await self._text_to_speech.stop()
            
            self._state = VoiceState.IDLE
            self.logger.info("Voice Router stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Voice Router: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the voice router."""
        return {
            "state": self._state.value,
            "current_command": self._current_command,
            "current_command_type": self._current_command_type.value if self._current_command_type else None,
            "queue_size": self._command_queue.qsize(),
            "commands_processed": self._commands_processed,
            "commands_successful": self._commands_successful,
            "commands_failed": self._commands_failed,
            "wake_word_available": self._wake_word_detector is not None,
            "speech_to_text_available": self._speech_to_text is not None,
            "text_to_speech_available": self._text_to_speech is not None,
            "config": self._config,
        }
    
    @property
    def state(self) -> VoiceState:
        """Get the current state."""
        return self._state
    
    @property
    def is_listening(self) -> bool:
        """Check if currently listening."""
        return self._state == VoiceState.LISTENING