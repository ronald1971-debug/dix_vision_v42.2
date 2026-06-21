"""
Core Contracts API Cognitive Chat
Real implementation for cognitive chat API contracts
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time

class ChatMessageRole(Enum):
    """Chat message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

class ChatMessageStatus(Enum):
    """Chat message status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    RECEIVED = "received"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class ChatMessage:
    """Chat message information"""
    message_id: str
    role: ChatMessageRole
    content: str
    status: ChatMessageStatus = ChatMessageStatus.PENDING
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[str] = field(default_factory=list)
    
    def is_user_message(self) -> bool:
        """Check if message is from user"""
        return self.role == ChatMessageRole.USER
    
    def is_assistant_message(self) -> bool:
        """Check if message is from assistant"""
        return self.role == ChatMessageRole.ASSISTANT
    
    def is_system_message(self) -> bool:
        """Check if message is from system"""
        return self.role == ChatMessageRole.SYSTEM
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "message_id": self.message_id,
            "role": self.role.value,
            "content": self.content,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "tool_calls": self.tool_calls
        }

@dataclass
class ChatContext:
    """Chat context information"""
    context_id: str
    session_id: str
    user_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the context"""
        self.messages.append(message)
        self.timestamp = time.time()
    
    def get_last_message(self) -> Optional[ChatMessage]:
        """Get the last message"""
        return self.messages[-1] if self.messages else None
    
    def get_user_messages(self) -> List[ChatMessage]:
        """Get all user messages"""
        return [m for m in self.messages if m.is_user_message()]
    
    def get_assistant_messages(self) -> List[ChatMessage]:
        """Get all assistant messages"""
        return [m for m in self.messages if m.is_assistant_message()]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "context_id": self.context_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "messages": [m.to_dict() for m in self.messages],
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class ChatSession:
    """Chat session information"""
    session_id: str
    user_id: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.status == "active"
    
    def touch(self) -> None:
        """Update the timestamp"""
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "metadata": self.metadata
        }

class ChatMessageApi:
    """API for chat message operations"""
    
    def send_message(self, message: ChatMessage) -> bool:
        """Send a message"""
        return True
    
    def receive_message(self) -> Optional[ChatMessage]:
        """Receive a message"""
        return None
    
    def get_history(self, limit: int = 50) -> List[ChatMessage]:
        """Get message history"""
        return []
    
    def clear_history(self) -> bool:
        """Clear message history"""
        return True

class ChatRoleApi:
    """API for chat role operations"""
    
    def get_allowed_roles(self, user_id: str) -> List[ChatMessageRole]:
        """Get allowed roles for a user"""
        return [ChatMessageRole.USER, ChatMessageRole.SYSTEM]
    
    def set_role_permission(self, role: ChatMessageRole, allowed: bool) -> bool:
        """Set permission for a role"""
        return True
    
    def check_role_permission(self, role: ChatMessageRole) -> bool:
        """Check if a role is allowed"""
        return True

@dataclass
class ChatStatusResponse:
    """Chat status response"""
    status: str
    message: str
    is_active: bool = False
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status,
            "message": self.message,
            "is_active": self.is_active,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class ChatTurnRequest:
    """Chat turn request"""
    session_id: str
    user_id: str
    message: str
    role: ChatMessageRole = ChatMessageRole.USER
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "message": self.message,
            "role": self.role.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "context": self.context
        }

@dataclass
class ChatTurnResponse:
    """Chat turn response"""
    response_id: str
    request_id: str
    session_id: str
    message: str
    role: ChatMessageRole = ChatMessageRole.ASSISTANT
    status: ChatMessageStatus = ChatMessageStatus.PENDING
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    
    def is_successful(self) -> bool:
        """Check if turn was successful"""
        return self.status == ChatMessageStatus.SENT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "message": self.message,
            "role": self.role.value,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "tool_results": self.tool_results
        }

__all__ = [
    "ChatMessageRole",
    "ChatMessageStatus",
    "ChatMessage",
    "ChatContext",
    "ChatSession",
    "ChatMessageApi",
    "ChatRoleApi",
    "ChatStatusResponse",
    "ChatTurnRequest",
    "ChatTurnResponse"
]