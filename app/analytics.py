"""Analytics extraction and structured lead intelligence schema."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.llm_client import llm_client
from app.session_manager import SessionState

class SiteVisitDetails(BaseModel):
    date: Optional[str] = None
    time_slot: Optional[str] = None
    location: Optional[str] = "Sector 79, Gurugram"
    note: Optional[str] = None

class FollowUpDetails(BaseModel):
    required: bool = True
    date_time: Optional[str] = None
    channel: str = "WhatsApp"
    reason: Optional[str] = None

class ConversationAnalytics(BaseModel):
    """Complete structured intelligence data extracted after a conversation."""
    customer_name: str = Field("Unknown", description="Name of the customer")
    phone_number: str = Field("Not Provided", description="Customer phone number")
    budget: str = Field("Not Disclosed", description="Budget category or stated range")
    budget_fit: str = Field("Not Disclosed", description="Within Range, Below Starting Price, Above Starting Price")
    configuration_interest: str = Field("Undecided", description="2 BHK, 3 BHK, Both, Undecided, or Other")
    interest_level: str = Field("Medium", description="High, Medium, Low, Uninterested, or DND")
    purchase_timeline: str = Field("Unknown", description="Immediate (< 1 month), 1-3 months, 3-6 months, Exploring")
    purpose_of_purchase: str = Field("Not Disclosed", description="End-use, Investment, or Not Disclosed")
    site_visit_status: str = Field("Not Discussed", description="Booked, Rescheduled, Failed / Slot Unavailable, Requested, Declined, Not Discussed")
    site_visit_details: Optional[Dict[str, Any]] = None
    lead_status: str = Field("Warm", description="Hot, Warm, Cold, Escalated, DND, Unqualified")
    follow_up_requirement: Dict[str, Any] = Field(default_factory=dict)
    human_escalation_required: bool = False
    key_objections_raised: List[str] = Field(default_factory=list)
    primary_language: str = Field("English", description="English, Hindi, or Hinglish")
    conversation_summary: str = Field("", description="Executive summary of the interaction")
    sentiment: str = Field("Neutral", description="Positive, Neutral, Hesitant, or Negative")
    next_steps: str = Field("", description="Recommended next action for sales team")


class AnalyticsService:
    """Service to process and store analytics."""

    @staticmethod
    def extract_from_session(session: SessionState) -> Dict[str, Any]:
        """Extract structured analytics from an active or concluded session."""
        messages = [{"role": m.role, "content": m.content} for m in session.messages]
        if not messages:
            return ConversationAnalytics().model_dump()
        
        extracted_data = llm_client.extract_analytics(messages)
        
        # Merge any session-level tool execution outcomes
        if session.site_visit:
            extracted_data["site_visit_status"] = "Booked" if session.site_visit.get("success") else "Failed / Slot Unavailable"
            extracted_data["site_visit_details"] = session.site_visit
        
        if session.dnd_marked:
            extracted_data["lead_status"] = "DND"
            extracted_data["interest_level"] = "DND"

        if session.escalation:
            extracted_data["human_escalation_required"] = True
            extracted_data["lead_status"] = "Escalated"

        session.analytics = extracted_data
        return extracted_data

analytics_service = AnalyticsService()
