from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent import chat_with_agent
from app.core.sessions import get_session, append_message
from app.schemas.profile import UserProfile

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please submit your profile first.")
    
    profile = UserProfile(**session["profile"])
    recommended_policy = session["recommendation"].get("recommended_policy_name", "")
    history = session["history"]
    
    append_message(request.session_id, "user", request.message)
    result = chat_with_agent(profile, recommended_policy, history, request.message)
    append_message(request.session_id, "assistant", result["reply"])
    
    return ChatResponse(reply=result["reply"], sources=result["sources"])
