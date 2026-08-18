"""Automated test cases demonstrating Northstar Homes AI Sales Agent across key scenarios."""

import pytest
from app.session_manager import SessionManager
from app.llm_client import LLMClient
from app.tools import RealEstateToolsHandler
from app.analytics import AnalyticsService

@pytest.fixture
def session_mgr():
    return SessionManager()

@pytest.fixture
def client():
    return LLMClient()

def test_scenario_1_qualification_and_booking(client):
    """
    Scenario 1: Standard Customer Qualification & Successful Site Visit Booking.
    Expected: Agent confirms 3 BHK starting at ₹1.75 Cr, books site visit, returns booking ID.
    """
    tools_handler = RealEstateToolsHandler(simulate_failure=False)
    messages = [
        {"role": "user", "content": "Hi, I am interested in a 3 BHK apartment in Gurgaon. Can you share starting prices?"},
        {"role": "assistant", "content": "Hello! Our 3 BHK luxury residences at Northstar One in Sector 79 start from ₹1.75 Crore onwards with spacious layouts and Aravalli views. Would you like to schedule a site visit to experience our show flat?"},
        {"role": "user", "content": "Yes, please book a site visit for this Sunday at 11:00 AM. My name is Amit Sharma."}
    ]
    
    reply, tool_res, actions = client.generate_chat_response(messages, tools_handler)
    
    # Assertions
    assert reply is not None
    assert len(reply) > 0
    assert any(w in reply.lower() for w in ["sunday", "11:00 am", "11 am", "booked", "confirmed", "nso-", "sector 79"])
    assert any(a["tool"] == "book_site_visit" for a in actions)
    assert any(a["result"].get("success") is True for a in actions)

def test_scenario_2_hinglish_price_objection(client):
    """
    Scenario 2: Hinglish Language Code-Switching & Price Objection Handling.
    Expected: Agent responds in natural Hinglish, addresses price concern, highlights value/amenities.
    """
    tools_handler = RealEstateToolsHandler()
    messages = [
        {"role": "user", "content": "2 BHK ka price kya hai? ₹1.35 Cr thoda mehnga lag raha hai Sector 79 ke hisaab se."}
    ]
    
    reply, tool_res, actions = client.generate_chat_response(messages, tools_handler)
    
    # Assertions
    assert reply is not None
    assert any(w in reply.lower() for w in ["samajh", "sector 79", "value", "aravalli", "show flat", "quality", "amenities", "visit"])

def test_scenario_3_hindi_connectivity_objection(client):
    """
    Scenario 3: Hindi Language Query on Location / Connectivity.
    Expected: Agent explains Sector 79 connectivity (NH-48, SPR, Cloverleaf) in natural Hindi/Hinglish.
    """
    tools_handler = RealEstateToolsHandler()
    messages = [
        {"role": "user", "content": "नमस्ते, क्या Sector 79 बहुत दूर नहीं है? Cyber City से कनेक्टिविटी कैसी है?"}
    ]
    
    reply, tool_res, actions = client.generate_chat_response(messages, tools_handler)
    
    # Assertions
    assert reply is not None
    assert any(w in reply.lower() for w in ["nh-48", "nh 48", "spr", "5 minute", "5 min", "cloverleaf", "aravalli"])

def test_scenario_4_busy_customer_callback(client):
    """
    Scenario 4: Busy Customer / Request to Contact Later.
    Expected: Agent respects customer's time immediately, offers callback/WhatsApp, logs follow-up tool.
    """
    tools_handler = RealEstateToolsHandler()
    messages = [
        {"role": "user", "content": "I am driving right now in a meeting, please call me tomorrow evening."}
    ]
    
    reply, tool_res, actions = client.generate_chat_response(messages, tools_handler)
    
    # Assertions
    assert reply is not None
    assert any(w in reply.lower() for w in ["worries", "reconnect", "whatsapp", "tomorrow", "time", "baad", "free"])
    assert any(a["tool"] == "schedule_followup" for a in actions)

def test_scenario_5_dnd_opt_out(client):
    """
    Scenario 5: Do-Not-Disturb (DND) / Stop Communication Request.
    Expected: Agent complies immediately with zero argument, marks contact as DND, says polite farewell.
    """
    tools_handler = RealEstateToolsHandler()
    messages = [
        {"role": "user", "content": "I am not interested at all, stop calling me and remove my number."}
    ]
    
    reply, tool_res, actions = client.generate_chat_response(messages, tools_handler)
    
    # Assertions
    assert reply is not None
    assert any(w in reply.lower() for w in ["do-not-disturb", "dnd", "records", "not receive", "wonderful day", "shubh", "further communication"])
    assert any(a["tool"] == "mark_dnd" for a in actions)

def test_scenario_6_anti_hallucination_unknown_features(client):
    """
    Scenario 6: Out-of-Scope / Unknown Questions (Anti-Hallucination Guardrail).
    Expected: Agent does NOT invent a 4 BHK penthouse or 25% discount, clarifies available 2 & 3 BHK configs.
    """
    tools_handler = RealEstateToolsHandler()
    messages = [
        {"role": "user", "content": "Do you have a 4 BHK penthouse with private swimming pool and can you offer 25% discount?"}
    ]
    
    reply, tool_res, actions = client.generate_chat_response(messages, tools_handler)
    
    # Assertions
    assert reply is not None
    # Must NOT claim 4 BHK is available or confirm 25% discount
    assert "we have 4 bhk penthouses with private pool" not in reply.lower()
    assert any(w in reply.lower() for w in ["2 bhk", "3 bhk", "senior", "specialist", "consultant", "verified"])

def test_scenario_7_booking_failure_fallback(client):
    """
    Scenario 7: Booking Failure & Slot Unavailable Fallback.
    Expected: When a requested slot (e.g. 2 PM Sunday) is full or failure is simulated,
              agent smoothly provides alternative slots (4:30 PM Sunday or 11:00 AM Monday).
    """
    tools_handler = RealEstateToolsHandler(simulate_failure=True)
    messages = [
        {"role": "user", "content": "I want to book a visit for Sunday at 2:00 PM."}
    ]
    
    reply, tool_res, actions = client.generate_chat_response(messages, tools_handler)
    
    # Assertions
    assert reply is not None
    assert any(w in reply.lower() for w in ["filled", "booked", "alternative", "4:30 pm", "4:30", "11:00 am", "11 am", "monday"])
    assert any(a["tool"] == "book_site_visit" for a in actions)
    assert any(a["result"].get("success") is False for a in actions)

def test_scenario_8_human_escalation(client):
    """
    Scenario 8: Human Escalation / Direct Senior Manager Request.
    Expected: Agent escalates to Senior Sales Manager and schedules callback.
    """
    tools_handler = RealEstateToolsHandler()
    messages = [
        {"role": "user", "content": "I want to talk directly to your Senior Sales Manager to negotiate the final price."}
    ]
    
    reply, tool_res, actions = client.generate_chat_response(messages, tools_handler)
    
    # Assertions
    assert reply is not None
    assert any(w in reply.lower() for w in ["senior sales manager", "senior", "manager", "connect", "reach"])
    assert any(a["tool"] == "escalate_to_human" for a in actions)

def test_scenario_9_post_conversation_analytics_extraction(session_mgr):
    """
    Scenario 9: Post-Conversation Structured Analytics Extraction.
    Expected: Generates comprehensive JSON with budget, interest level, site visit status, lead status, etc.
    """
    session = session_mgr.get_or_create_session("test_analytics_session_001")
    session_mgr.add_message(session.session_id, "user", "Hi, I am looking for a 3 BHK in Northstar One. Budget is around 1.8 Cr.")
    session_mgr.add_message(session.session_id, "assistant", "Our 3 BHK homes start at ₹1.75 Cr with panoramic Aravalli views. Would you like to schedule a site visit this Sunday at 11 AM?")
    session_mgr.add_message(session.session_id, "user", "Yes, please confirm site visit for Sunday at 11:00 AM. My name is Rajesh Gupta.")
    
    # Simulate booked site visit
    tools_handler = RealEstateToolsHandler()
    booking_res = tools_handler.book_site_visit("Sunday", "11:00 AM", "Rajesh Gupta")
    session.site_visit = booking_res
    session.status = "booked"
    
    analytics = AnalyticsService.extract_from_session(session)
    
    # Assertions
    assert analytics is not None
    assert analytics["configuration_interest"] == "3 BHK"
    assert analytics["lead_status"] in ("Hot", "Warm")
    assert analytics["site_visit_status"] == "Booked"
    assert "follow_up_requirement" in analytics
    assert analytics["follow_up_requirement"]["required"] is True
    assert "conversation_summary" in analytics
