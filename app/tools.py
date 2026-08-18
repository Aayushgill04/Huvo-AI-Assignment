"""Tool definitions and simulated CRM execution logic for Northstar Homes."""

import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SiteVisitBookingRequest(BaseModel):
    name: str = Field(..., description="Full name of the customer")
    phone: str = Field(..., description="Contact phone number of the customer")
    date: str = Field(..., description="Preferred date for site visit, e.g. '2026-08-23' or 'This Sunday'")
    time_slot: str = Field(..., description="Preferred time slot, e.g. '11:00 AM', '3:00 PM', '5:00 PM'")
    configuration: Optional[str] = Field("2 BHK / 3 BHK", description="Interested configuration")

class FollowUpRequest(BaseModel):
    name: Optional[str] = Field("Customer", description="Name of the customer")
    phone: Optional[str] = Field(None, description="Contact phone number")
    date_time: str = Field(..., description="Preferred date and time for follow-up")
    channel: str = Field("Phone Call", description="Preferred channel: Phone Call, WhatsApp, Email")
    reason: str = Field("Customer requested callback", description="Reason for follow-up")

class EscalationRequest(BaseModel):
    name: Optional[str] = Field("Customer", description="Customer name")
    phone: Optional[str] = Field(None, description="Customer phone")
    reason: str = Field(..., description="Reason for escalation e.g. pricing negotiation, dispute, manager request")
    urgency: str = Field("Normal", description="Urgency level: Low, Normal, High")

class DNDRequest(BaseModel):
    phone: Optional[str] = Field(None, description="Phone number to mark as DND")
    reason: str = Field("Customer opted out", description="Reason for opt-out")


# Tool definitions for LLM Function Calling (OpenAI format)
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "book_site_visit",
            "description": "Book an on-site visit and preview tour at Northstar One experience center in Sector 79, Gurugram.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer full name"},
                    "phone": {"type": "string", "description": "Customer phone number"},
                    "date": {"type": "string", "description": "Date requested for the visit (e.g. 'Saturday', '2026-08-23')"},
                    "time_slot": {"type": "string", "description": "Time slot requested (e.g. '11:00 AM', '2:00 PM', '4:30 PM')"},
                    "configuration": {"type": "string", "description": "Preferred configuration (2 BHK or 3 BHK)"}
                },
                "required": ["date", "time_slot"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_followup",
            "description": "Schedule a follow-up callback or WhatsApp message for busy customers or those requesting later contact.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer name if known"},
                    "phone": {"type": "string", "description": "Customer phone number"},
                    "date_time": {"type": "string", "description": "Requested date and time for callback"},
                    "channel": {"type": "string", "enum": ["Phone Call", "WhatsApp"], "description": "Preferred communication channel"},
                    "reason": {"type": "string", "description": "Reason or context for callback"}
                },
                "required": ["date_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate the conversation to a Senior Sales Manager when the customer demands a human, customized discounts, or complex structuring.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer name"},
                    "phone": {"type": "string", "description": "Customer phone number"},
                    "reason": {"type": "string", "description": "Reason for escalation"}
                },
                "required": ["reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_dnd",
            "description": "Mark the customer as Do-Not-Disturb (DND) and stop all future communications upon customer request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string", "description": "Customer phone number if available"},
                    "reason": {"type": "string", "description": "Opt-out reason"}
                },
                "required": []
            }
        }
    }
]


class RealEstateToolsHandler:
    """Handles execution of agent tools with simulation capabilities."""

    def __init__(self, simulate_failure: bool = False):
        self.simulate_failure = simulate_failure

    def book_site_visit(
        self,
        date: str,
        time_slot: str,
        name: Optional[str] = "Valued Customer",
        phone: Optional[str] = None,
        configuration: Optional[str] = "2 BHK / 3 BHK"
    ) -> Dict[str, Any]:
        """Simulate booking a site visit with failure handling."""
        
        # Check if booking should fail either via global flag or specific overbooked slots (e.g. 2 PM on weekends)
        is_blocked_slot = "2:00" in time_slot or "2 pm" in time_slot.lower() or "2pm" in time_slot.lower()
        if self.simulate_failure or is_blocked_slot:
            return {
                "success": False,
                "error": "SLOT_UNAVAILABLE",
                "message": f"The requested slot ({time_slot} on {date}) is fully booked.",
                "alternative_slots": ["4:30 PM this Sunday", "11:00 AM on Monday"],
                "instructions_for_agent": "Inform the customer warmly that the requested slot is full, and proactively suggest the alternative slots: 4:30 PM this Sunday or 11:00 AM on Monday."
            }

        booking_id = f"NSO-{uuid.uuid4().hex[:6].upper()}"
        return {
            "success": True,
            "booking_id": booking_id,
            "project": "Northstar One",
            "location": "Sector 79, Gurugram",
            "customer_name": name,
            "phone": phone or "Registered Number",
            "date": date,
            "time_slot": time_slot,
            "configuration": configuration,
            "message": f"Site visit successfully booked for {date} at {time_slot}. Booking ID: {booking_id}."
        }

    def schedule_followup(
        self,
        date_time: str,
        name: Optional[str] = "Customer",
        phone: Optional[str] = None,
        channel: str = "Phone Call",
        reason: str = "Callback requested"
    ) -> Dict[str, Any]:
        """Schedule a follow-up callback or message."""
        followup_id = f"FUP-{uuid.uuid4().hex[:6].upper()}"
        return {
            "success": True,
            "followup_id": followup_id,
            "date_time": date_time,
            "channel": channel,
            "customer_name": name,
            "reason": reason,
            "message": f"Follow-up scheduled via {channel} for {date_time}."
        }

    def escalate_to_human(
        self,
        reason: str,
        name: Optional[str] = "Customer",
        phone: Optional[str] = None,
        urgency: str = "Normal"
    ) -> Dict[str, Any]:
        """Log an escalation for a Senior Sales Manager."""
        ticket_id = f"ESC-{uuid.uuid4().hex[:6].upper()}"
        return {
            "success": True,
            "ticket_id": ticket_id,
            "assigned_to": "Senior Property Consultant",
            "reason": reason,
            "urgency": urgency,
            "customer_name": name,
            "phone": phone or "Registered Number",
            "message": f"Escalated to Senior Property Consultant under ticket {ticket_id}. Callback scheduled within 30 minutes."
        }

    def mark_dnd(
        self,
        phone: Optional[str] = None,
        reason: str = "Customer requested to stop communication"
    ) -> Dict[str, Any]:
        """Mark contact as DND."""
        return {
            "success": True,
            "dnd_status": "ACTIVE",
            "phone": phone or "Current Session",
            "reason": reason,
            "message": "Contact number marked as Do-Not-Disturb. All communications stopped immediately."
        }
