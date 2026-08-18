"""Analytics endpoints for retrieving conversation intelligence."""

from fastapi import APIRouter, HTTPException
from app.session_manager import session_manager
from app.analytics import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/{session_id}")
async def get_session_analytics(session_id: str):
    """Retrieve full structured analytics for a specific conversation session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    analytics = analytics_service.extract_from_session(session)
    return {
        "session_id": session.session_id,
        "status": session.status,
        "message_count": len(session.messages),
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "analytics": analytics
    }

@router.get("")
async def list_all_analytics():
    """Retrieve high-level lead summary for all sessions in memory."""
    all_sessions = session_manager.get_all_sessions()
    summaries = []
    
    for s in all_sessions:
        analytics = s.analytics or analytics_service.extract_from_session(s)
        summaries.append({
            "session_id": s.session_id,
            "status": s.status,
            "message_count": len(s.messages),
            "lead_status": analytics.get("lead_status", "Unknown"),
            "configuration": analytics.get("configuration_interest", "Undecided"),
            "budget": analytics.get("budget", "Not Disclosed"),
            "site_visit_status": analytics.get("site_visit_status", "Not Discussed"),
            "language": analytics.get("primary_language", "English")
        })
        
    return {"total_sessions": len(summaries), "sessions": summaries}

@router.get("/export/{session_id}")
async def export_transcript_and_analytics(session_id: str):
    """Export complete session transcript and analytics data for CRM ingestion."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    analytics = analytics_service.extract_from_session(session)
    return {
        "session_id": session.session_id,
        "status": session.status,
        "transcript": [m.model_dump() for m in session.messages],
        "analytics": analytics
    }
