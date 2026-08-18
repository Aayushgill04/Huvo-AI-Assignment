"""Chat and conversational interaction endpoints."""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.session_manager import session_manager
from app.llm_client import llm_client
from app.tools import RealEstateToolsHandler
from app.analytics import analytics_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, description="Customer message text")
    simulate_booking_failure: Optional[bool] = False

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    status: str
    tool_action: Optional[Dict[str, Any]] = None
    all_actions: List[Dict[str, Any]] = Field(default_factory=list)
    live_analytics: Optional[Dict[str, Any]] = None

class ResetRequest(BaseModel):
    session_id: str

class ToggleFailureRequest(BaseModel):
    session_id: str
    simulate_failure: bool

class EndConversationRequest(BaseModel):
    session_id: str

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process incoming customer message, maintain context, invoke LLM,
    execute real-estate tools if requested, and return response.
    """
    session = session_manager.get_or_create_session(
        session_id=request.session_id,
        simulate_failure=request.simulate_booking_failure or False
    )

    if request.simulate_booking_failure is not None:
        session.simulate_booking_failure = request.simulate_booking_failure

    # Record user message in history
    session_manager.add_message(session.session_id, role="user", content=request.message)

    # Initialize tools handler with session's failure flag
    tools_handler = RealEstateToolsHandler(simulate_failure=session.simulate_booking_failure)

    # Retrieve all messages for LLM
    llm_history = session_manager.get_messages_for_llm(session.session_id)

    # Generate reply & execute tools
    reply_text, tool_result, actions = llm_client.generate_chat_response(
        messages=llm_history,
        tools_handler=tools_handler
    )

    # Record assistant message in history
    session_manager.add_message(session.session_id, role="assistant", content=reply_text)

    # Update session metadata if tools executed
    for action in actions:
        tool_name = action.get("tool")
        res = action.get("result", {})
        if tool_name == "book_site_visit":
            session.site_visit = res
            session.status = "booked" if res.get("success") else "booking_failed"
        elif tool_name == "mark_dnd":
            session.dnd_marked = True
            session.status = "dnd"
        elif tool_name == "escalate_to_human":
            session.escalation = res
            session.status = "escalated"
        elif tool_name == "schedule_followup":
            session.followup = res

    # Generate live preview analytics
    live_analytics = analytics_service.extract_from_session(session)

    return ChatResponse(
        session_id=session.session_id,
        reply=reply_text,
        status=session.status,
        tool_action=tool_result,
        all_actions=actions,
        live_analytics=live_analytics
    )

@router.post("/reset")
async def reset_session(request: ResetRequest):
    """Clear session history and reset context."""
    session = session_manager.reset_session(request.session_id)
    return {"message": "Session reset successfully", "session_id": session.session_id}

@router.post("/simulate-failure")
async def toggle_failure(request: ToggleFailureRequest):
    """Toggle site-visit booking failure simulation."""
    session_manager.set_simulate_failure(request.session_id, request.simulate_failure)
    return {
        "session_id": request.session_id,
        "simulate_booking_failure": request.simulate_failure,
        "message": f"Site-visit booking failure simulation set to {request.simulate_failure}"
    }

@router.post("/end")
async def end_conversation(request: EndConversationRequest):
    """
    Formally conclude the conversation session and generate
    comprehensive post-conversation analytics and lead intelligence data.
    """
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "completed" if session.status == "active" else session.status
    final_analytics = analytics_service.extract_from_session(session)

    return {
        "session_id": session.session_id,
        "status": session.status,
        "total_messages": len(session.messages),
        "analytics": final_analytics
    }

@router.get("/scenarios")
async def get_test_scenarios():
    """Returns interactive test scenarios demonstrating agent capabilities."""
    return {
        "scenarios": [
            {
                "id": "qualification_booking",
                "title": "Lead Qualification & Site Visit Booking",
                "category": "Happy Path",
                "language": "English",
                "prompt": "Hi, I am looking for a 3 BHK apartment in Gurgaon with good amenities. Can you share details?",
                "follow_up": "Budget around 1.8 Cr looks good. Can I visit this Sunday at 11 AM?",
                "expected": "Qualifies budget, confirms 3 BHK starting at ₹1.75 Cr, and schedules site visit at 11:00 AM."
            },
            {
                "id": "hinglish_price_objection",
                "title": "Hinglish Price Objection",
                "category": "Objection Handling",
                "language": "Hinglish",
                "prompt": "Hi, 2 BHK ka price kya hai? ₹1.35 Cr thoda zyada lag raha hai Sector 79 ke hisaab se.",
                "expected": "Responds empathetically in Hinglish, highlights Aravalli views, premium build quality, and invites to see the show flat."
            },
            {
                "id": "location_connectivity_hindi",
                "title": "Hindi Location / Distance Query",
                "category": "Multilingual & Objections",
                "language": "Hindi",
                "prompt": "नमस्ते, क्या Sector 79 बहुत दूर नहीं है? Cyber City से कनेक्टिविटी कैसी है?",
                "expected": "Explains in natural Hindi that Sector 79 is 5 mins from NH-48/SPR with direct access via Cloverleaf flyover."
            },
            {
                "id": "booking_failure_fallback",
                "title": "Booking Failure / Slot Unavailable Fallback",
                "category": "Edge Case & Recovery",
                "language": "English",
                "prompt": "I want to book a site visit for this Sunday at 2:00 PM.",
                "expected": "Handles overbooked slot gracefully and offers alternative slots (4:30 PM Sunday or 11:00 AM Monday)."
            },
            {
                "id": "unknown_question_hallucination",
                "title": "Unknown Feature & Anti-Hallucination",
                "category": "Anti-Hallucination Guardrail",
                "language": "English",
                "prompt": "Do you have a 4 BHK penthouse with private swimming pool and can you give 25% discount?",
                "expected": "Strictly avoids inventing specs or discounts, clarifies 2 & 3 BHK availability, offers senior consultant callback."
            },
            {
                "id": "busy_customer_callback",
                "title": "Busy Customer / Contact Later",
                "category": "Call Flow Handling",
                "language": "English",
                "prompt": "I am driving right now, please call me later tomorrow evening.",
                "expected": "Respects time immediately, logs follow-up callback for tomorrow, offers WhatsApp brochure."
            },
            {
                "id": "dnd_opt_out",
                "title": "Do-Not-Disturb (DND) / Stop Communication",
                "category": "Compliance & DND",
                "language": "Hinglish",
                "prompt": "Mujhe koi interest nahi hai, please call mat karna aur number delete kar do.",
                "expected": "Immediately complies with zero pushback, marks contact as DND, and wraps up politely."
            },
            {
                "id": "human_escalation",
                "title": "Human Escalation / Manager Request",
                "category": "Escalation",
                "language": "English",
                "prompt": "I want to speak with your Senior Sales Manager directly to negotiate pricing.",
                "expected": "De-escalates smoothly and arranges a direct callback with the Senior Property Consultant."
            }
        ]
    }
