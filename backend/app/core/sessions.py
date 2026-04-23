from typing import Dict, Any
from uuid import uuid4

# In-memory session store (sufficient for prototype; document as known limitation)
_sessions: Dict[str, Dict[str, Any]] = {}

def create_session(profile: Dict[str, Any], recommendation: Dict[str, Any]) -> str:
    session_id = str(uuid4())
    _sessions[session_id] = {
        "profile": profile,
        "recommendation": recommendation,
        "history": [],
    }
    return session_id

def get_session(session_id: str) -> Dict[str, Any] | None:
    return _sessions.get(session_id)

def append_message(session_id: str, role: str, content: str):
    session = _sessions.get(session_id)
    if session:
        session["history"].append({"role": role, "content": content})
