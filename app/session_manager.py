"""Session and conversation context management."""

import time
import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: str  # 'system', 'user', 'assistant', 'tool'
    content: str
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    timestamp: float = Field(default_factory=time.time)

class SessionState(BaseModel):
    session_id: str
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    messages: List[Message] = Field(default_factory=list)
    status: str = "active"  # active, completed, dnd, escalated, booked
    simulate_booking_failure: bool = False
    
    # Tracked metadata
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    configuration: Optional[str] = None
    budget: Optional[str] = None
    site_visit: Optional[Dict[str, Any]] = None
    followup: Optional[Dict[str, Any]] = None
    escalation: Optional[Dict[str, Any]] = None
    dnd_marked: bool = False
    analytics: Optional[Dict[str, Any]] = None

class SessionManager:
    """In-memory session registry for active conversations."""

    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create_session(self, session_id: Optional[str] = None, simulate_failure: bool = False) -> SessionState:
        if not session_id or session_id not in self._sessions:
            new_id = session_id or str(uuid.uuid4())
            self._sessions[new_id] = SessionState(
                session_id=new_id,
                simulate_booking_failure=simulate_failure
            )
            return self._sessions[new_id]
        
        session = self._sessions[session_id]
        return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        return self._sessions.get(session_id)

    def add_message(self, session_id: str, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None, tool_call_id: Optional[str] = None):
        session = self.get_or_create_session(session_id)
        msg = Message(
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id,
            timestamp=time.time()
        )
        session.messages.append(msg)
        session.updated_at = time.time()

    def get_messages_for_llm(self, session_id: str) -> List[Dict[str, Any]]:
        session = self.get_or_create_session(session_id)
        llm_messages = []
        for msg in session.messages:
            entry: Dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                entry["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id
            llm_messages.append(entry)
        return llm_messages

    def set_simulate_failure(self, session_id: str, simulate: bool):
        session = self.get_or_create_session(session_id)
        session.simulate_booking_failure = simulate

    def reset_session(self, session_id: str) -> SessionState:
        simulate = False
        if session_id in self._sessions:
            simulate = self._sessions[session_id].simulate_booking_failure
        self._sessions[session_id] = SessionState(session_id=session_id, simulate_booking_failure=simulate)
        return self._sessions[session_id]

    def get_all_sessions(self) -> List[SessionState]:
        return list(self._sessions.values())

# Global session manager instance
session_manager = SessionManager()
