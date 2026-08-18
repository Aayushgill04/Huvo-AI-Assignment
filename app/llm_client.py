"""LLM Provider Client and Mock Inference Gateway."""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
from app.prompts import SYSTEM_PROMPT
from app.tools import TOOLS_SCHEMA, RealEstateToolsHandler

logger = logging.getLogger(__name__)

class LLMClient:
    """Multi-provider LLM Client supporting OpenAI, Groq, OpenRouter, and Built-in Mock LLM."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.base_url = settings.OPENAI_BASE_URL
        self._openai_client = None

        if self.api_key and self.provider != "mock":
            try:
                from openai import OpenAI
                client_kwargs = {"api_key": self.api_key}
                if self.base_url:
                    client_kwargs["base_url"] = self.base_url
                self._openai_client = OpenAI(**client_kwargs)
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}. Falling back to mock engine.")
                self.provider = "mock"
        else:
            self.provider = "mock"

    def generate_chat_response(
        self,
        messages: List[Dict[str, Any]],
        tools_handler: Optional[RealEstateToolsHandler] = None,
        max_turns: int = 3,
        preferred_language: str = "English"
    ) -> Tuple[str, Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Generate conversational response for the agent.
        Returns:
            (assistant_reply_text, executed_tool_result, list_of_executed_actions)
        """
        if self.provider != "mock" and self._openai_client:
            try:
                return self._generate_openai_response(messages, tools_handler, max_turns, preferred_language)
            except Exception as e:
                logger.error(f"Error invoking LLM provider ({self.provider}): {e}. Falling back to Mock Engine.")
                return self._generate_mock_response(messages, tools_handler, preferred_language)
        else:
            return self._generate_mock_response(messages, tools_handler, preferred_language)

    def _generate_openai_response(
        self,
        messages: List[Dict[str, Any]],
        tools_handler: Optional[RealEstateToolsHandler],
        max_turns: int = 3,
        preferred_language: str = "English"
    ) -> Tuple[str, Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """Execute OpenAI / compatible provider chat completion with tool calling."""
        executed_actions = []
        last_tool_result = None

        # Ensure system prompt is first message with language directive
        lang_directive = f"\n\nIMPORTANT LANGUAGE PREFERENCE: The customer has selected {preferred_language}. You must reply naturally in {preferred_language} while maintaining natural spoken conversational voice guidelines."
        formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT + lang_directive}]
        
        for msg in messages:
            if msg.get("role") != "system":
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg.get("content") or ""
                })

        for _ in range(max_turns):
            response = self._openai_client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.4,
                max_tokens=450
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if not tool_calls:
                return (response_message.content or "").strip(), last_tool_result, executed_actions

            # Process tool calls
            formatted_messages.append(response_message)

            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                tool_result = self._execute_tool(fn_name, fn_args, tools_handler)
                
                last_tool_result = tool_result
                executed_actions.append({"tool": fn_name, "args": fn_args, "result": tool_result})

                formatted_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

        # Fallback return
        return (response_message.content or "").strip(), last_tool_result, executed_actions

    def _execute_tool(self, name: str, args: Dict[str, Any], handler: Optional[RealEstateToolsHandler]) -> Dict[str, Any]:
        """Execute tool logic."""
        if not handler:
            handler = RealEstateToolsHandler()

        if name == "book_site_visit":
            return handler.book_site_visit(
                date=args.get("date", "This Weekend"),
                time_slot=args.get("time_slot", "11:00 AM"),
                name=args.get("name", "Valued Customer"),
                phone=args.get("phone"),
                configuration=args.get("configuration", "2 BHK / 3 BHK")
            )
        elif name == "schedule_followup":
            return handler.schedule_followup(
                date_time=args.get("date_time", "Tomorrow"),
                name=args.get("name", "Customer"),
                phone=args.get("phone"),
                channel=args.get("channel", "Phone Call"),
                reason=args.get("reason", "Follow-up requested")
            )
        elif name == "escalate_to_human":
            return handler.escalate_to_human(
                reason=args.get("reason", "Customer requested human consultation"),
                name=args.get("name", "Customer"),
                phone=args.get("phone")
            )
        elif name == "mark_dnd":
            return handler.mark_dnd(
                phone=args.get("phone"),
                reason=args.get("reason", "Opt-out requested")
            )
        return {"status": "error", "message": f"Unknown tool: {name}"}

    def _generate_mock_response(
        self,
        messages: List[Dict[str, Any]],
        tools_handler: Optional[RealEstateToolsHandler] = None,
        preferred_language: str = "English"
    ) -> Tuple[str, Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Intelligent Mock LLM response generator that accurately simulates Tara's behavior
        for all key scenarios (English, Hindi, Hinglish, objections, DND, booking, failures, unknown queries).
        """
        if not tools_handler:
            tools_handler = RealEstateToolsHandler()

        # Find last user message
        user_messages = [m for m in messages if m.get("role") == "user"]
        last_user_msg = user_messages[-1]["content"] if user_messages else ""
        text_lower = last_user_msg.lower()

        # Determine target language: explicit preference or detected from text
        is_hindi = preferred_language == "Hindi" or any(w in text_lower for w in ["नमस्ते", "दूर", "महंगा", "करना", "चाहिए", "बताओ", "कैसी", "है", "नहीं", "दूरी", "व्यस्त"])
        is_hinglish = preferred_language == "Hinglish" or any(w in text_lower for w in ["kya", "hai", "mujhe", "batao", "chahiye", "theek", "hoon", "kaunsa", "aana", "zyada", "mehnga", "kitna", "baad"])

        executed_actions = []
        tool_result = None

        # 1. Stop Communication / DND Scenario
        if any(w in text_lower for w in ["don't call", "dont call", "stop calling", "remove my number", "dnd", "not interested", "mat karo", "call mat karna", "unsubscribe", "डिलीट", "बंद"]):
            tool_result = tools_handler.mark_dnd(reason="Customer requested DND")
            executed_actions.append({"tool": "mark_dnd", "args": {}, "result": tool_result})
            
            if is_hindi:
                reply = "बिल्कुल, मैं समझ सकती हूँ। मैंने आपका नंबर हमारी डू-नॉट-डिस्टर्ब सूची में दर्ज कर दिया है और आगे से कोई कॉल या संदेश नहीं आएगा। आपका दिन शुभ रहे!"
            elif is_hinglish:
                reply = "Bilkul, main samajh sakti hoon. Maine aapka number hamari Do-Not-Disturb list me mark kar diya hai aur aage se koi call ya message nahi aayega. Aapka din shubh rahe!"
            else:
                reply = "Understood. I have updated our records and marked your number on our Do-Not-Disturb list. You will not receive any further communication from our team. Have a wonderful day!"
            return reply, tool_result, executed_actions

        # 2. Busy / Contact Later Scenario
        if any(w in text_lower for w in ["driving", "busy", "call later", "call me later", "baad me", "baad mein", "meeting", "not free", "busy hoon", "व्यस्त", "बाद में"]):
            tool_result = tools_handler.schedule_followup(date_time="Tomorrow 5:00 PM", channel="Phone Call", reason="Customer was busy")
            executed_actions.append({"tool": "schedule_followup", "args": {"date_time": "Tomorrow 5:00 PM"}, "result": tool_result})
            
            if is_hindi:
                reply = "कोई बात नहीं! आप कब उपलब्ध होंगे जब मैं आपको दोबारा कॉल कर सकती हूँ, या क्या मैं व्हाट्सएप पर संक्षिप्त विवरण साझा कर दूँ?"
            elif is_hinglish:
                reply = "Koi baat nahi! Aap kab free honge jab main aapko dubara call kar sakti hoon, ya kya aapko WhatsApp par quick details share kar doon?"
            else:
                reply = "No worries at all! Could you please share a preferred day and time for me to reconnect, or would you prefer a quick overview on WhatsApp?"
            return reply, tool_result, executed_actions

        # 3. Human Escalation Scenario
        if any(w in text_lower for w in ["manager", "human", "agent", "real person", "senior", "discount baat", "negotiate", "director", "बात करनी"]):
            tool_result = tools_handler.escalate_to_human(reason="Customer requested senior manager for pricing discussion")
            executed_actions.append({"tool": "escalate_to_human", "args": {"reason": "Manager consultation requested"}, "result": tool_result})
            
            if is_hindi:
                reply = "मैं पूरी तरह समझ सकती हूँ। मैं हमारे वरिष्ठ बिक्री प्रबंधक को आपकी जानकारी भेज रही हूँ जो आपसे सीधे संपर्क करेंगे। क्या यह आपका सर्वोत्तम संपर्क नंबर है?"
            elif is_hinglish:
                reply = "Main bilkul samajh sakti hoon. Main hamare Senior Sales Manager ko request forward kar rahi hoon jo aapse direct connect karenge. Kya yeh aapka best contact number hai?"
            else:
                reply = "I completely understand. I am having our Senior Sales Manager connect with you directly to assist with this in detail. Could you confirm the best number and time to reach you?"
            return reply, tool_result, executed_actions

        # 4. Out of scope / Unknown Question (Anti-Hallucination)
        if any(w in text_lower for w in ["4 bhk", "4bhk", "penthouse", "private pool", "20% discount", "25% discount", "30% discount", "helipad", "floor plan tower c"]):
            if is_hindi:
                reply = "नॉर्थस्टार वन में वर्तमान में हमारे पास 2 BHK और 3 BHK लग्जरी कॉन्फ़िगरेशन उपलब्ध हैं। किसी भी विशेष कस्टमाइज़ेशन या छूट की सत्यापित जानकारी हमारे वरिष्ठ प्रॉपर्टी सलाहकार आपसे साझा करेंगे। क्या आप इस वीकेंड शो फ्लैट देखना चाहेंगे?"
            elif is_hinglish:
                reply = "Northstar One me currently hamare pass luxury 2 BHK aur 3 BHK configurations available hain. Specific customization ya special requests ki verified details hamare senior property specialist aapse share kar denge. Kya aap is weekend show flat visit karna chahenge?"
            else:
                reply = "Northstar One currently offers thoughtfully designed 2 BHK and 3 BHK luxury configurations. For specific custom layouts or special requests, our Senior Property Consultant can share the exact verified details with you. Would you like to schedule a quick site visit to explore our show flat?"
            return reply, None, executed_actions

        # 5. Site-Visit Booking Scenario & Failure Handling
        if any(w in text_lower for w in ["book", "visit", "aana", "sunday", "saturday", "tomorrow", "weekend", "dekhne", "site visit", "slot", "pm", "am", "देखने", "बुक"]):
            slot = "2:00 PM" if ("2 pm" in text_lower or "2:00" in text_lower or "2pm" in text_lower) else "11:00 AM"
            day = "Sunday" if "sunday" in text_lower else ("Saturday" if "saturday" in text_lower else "this weekend")
            
            name = "Valued Customer"
            if "amit" in text_lower:
                name = "Amit Sharma"
            elif "rohit" in text_lower:
                name = "Rohit Verma"
            
            tool_result = tools_handler.book_site_visit(date=day, time_slot=slot, name=name)
            executed_actions.append({"tool": "book_site_visit", "args": {"date": day, "time_slot": slot, "name": name}, "result": tool_result})

            if not tool_result.get("success"):
                if is_hindi:
                    reply = f"रविवार को {slot} का स्लॉट प्राइवेट गाइडेड टूर के लिए पूरी तरह बुक है। हालांकि रविवार शाम 4:30 PM या सोमवार सुबह 11:00 AM का स्लॉट उपलब्ध है। आपके लिए कौन सा समय उपयुक्त रहेगा?"
                elif is_hinglish:
                    reply = f"Sunday ka {slot} wala slot fully booked hai private guided tours ke liye. Lekin Sunday ko 4:30 PM ya Monday subah 11:00 AM ka slot available hai. Aapko kaunsa time suit karega?"
                else:
                    reply = f"It looks like the {slot} slot for {day} is completely filled up for private guided tours. However, I have an open slot at 4:30 PM this Sunday or 11:00 AM on Monday morning. Which of those works better for you?"
                return reply, tool_result, executed_actions
            else:
                booking_id = tool_result.get("booking_id", "NSO-1082")
                if is_hindi:
                    reply = f"बहुत बढ़िया! मैंने नॉर्थस्टार वन एक्सपीरियंस सेंटर, सेक्टर 79 के लिए {day} को {slot} पर आपकी साइट विजिट बुक कर दी है। बुकिंग संदर्भ: {booking_id}। हमारी टीम आपसे लोकेशन साझा कर देगी।"
                elif is_hinglish:
                    reply = f"Bahut badiya! Maine aapka site visit {day} ko {slot} par Northstar One experience center, Sector 79 ke liye book kar diya hai. Booking ID: {booking_id}. Hamari team aapko location share kar degi."
                else:
                    reply = f"Wonderful! I have confirmed your site visit for {day} at {slot} at the Northstar One experience center in Sector 79, Gurugram. Your booking reference is {booking_id}. We look forward to welcoming you!"
                return reply, tool_result, executed_actions

        # 6. Location / Connectivity Objection Handling
        if any(w in text_lower for w in ["far", "location", "distance", "connectivity", "door", "kahan", "दूर", "कनेक्टिविटी", "cyber city", "cybercity", "rasta"]):
            if is_hindi:
                reply = "सेक्टर 79 NH-48 और सदर्न पेरिफेरल रोड (SPR) से मात्र 5 मिनट की दूरी पर है, और क्लोवरलीफ़ फ्लाईओवर के माध्यम से साइबर सिटी तक सीधी कनेक्टिविटी है। साथ ही यहाँ अरावली पहाड़ियों के पास शांत और हरित वातावरण मिलता है। क्या आप इस वीकेंड साइट देखना चाहेंगे?"
            elif is_hinglish:
                reply = "Sector 79 NH-48 aur Southern Peripheral Road (SPR) se sirf 5 minute ki distance par hai, aur Cloverleaf flyover ke through Cyber City aur Golf Course Extension Road tak direct access hai. Saath hi yahan Aravalli foothills ke paas clean aur green environment milta hai. Kya aap is weekend location visit karna chahenge?"
            else:
                reply = "Sector 79 is strategically situated just 5 minutes from NH-48 and SPR, with seamless connectivity to Cyber City and Golf Course Extension Road via the Cloverleaf flyover, while giving you peaceful green surroundings near the Aravalli hills. Would you like to visit our site this weekend to see the location firsthand?"
            return reply, None, executed_actions

        # 7. Price Objection Handling
        if any(w in text_lower for w in ["expensive", "price", "budget", "costly", "mehnga", "rate", "daam", "zyada", "महंगा", "ज्यादा"]):
            if is_hindi:
                reply = "मैं आपकी चिंता समझ सकती हूँ। सेक्टर 79 में नॉर्थस्टार वन प्रीमियम निर्माण गुणवत्ता, अरावली के खुले दृश्य और 30+ लक्ज़री क्लब हाउस सुविधाएं प्रदान करता है जो बेहतरीन मूल्य देती हैं। मेरा सुझाव है कि आप शो फ्लैट देखकर खुद अनुभव करें। क्या इस रविवार का समय ठीक रहेगा?"
            elif is_hinglish:
                reply = "Main aapki baat samajh sakti hoon. Sector 79 me Northstar One premium construction quality, Aravalli green views aur luxury clubhouse amenities offer karta hai jo great value provide karta hai. Main suggest karungi ki aap ek baar show flat visit karke layout dekhein. Kya Sunday ka time theek rahega?"
            else:
                reply = "I completely understand your perspective. Northstar One offers premium low-density luxury, direct Aravalli views, and superior build quality starting at 1.35 Cr for 2 BHK and 1.75 Cr for 3 BHK. The best way to evaluate the true value is to experience our show flat in person. Would this weekend work for a short tour?"
            return reply, None, executed_actions

        # 8. Inquiry on 2 BHK / 3 BHK
        if "2 bhk" in text_lower or "2bhk" in text_lower:
            if is_hindi:
                reply = "नॉर्थस्टार वन में हमारा 2 BHK ₹1.35 करोड़ से शुरू होता है, जिसमें आधुनिक सुविधाएं और अरावली के दृश्य मिलते हैं। क्या आप इसे स्वयं रहने के लिए देख रहे हैं या निवेश के उद्देश्य से?"
            elif is_hinglish:
                reply = "Northstar One me hamara spacious 2 BHK ₹1.35 Crore onwards start hota hai, jo modern luxury amenities aur lush green views ke saath aata hai. Kya aap isko end-use ke liye dekh rahe hain ya investment purpose ke liye?"
            else:
                reply = "Our spacious 2 BHK luxury homes start from ₹1.35 Crore onwards with modern amenities and lush green Aravalli views. Are you exploring this for self-use or investment?"
            return reply, None, executed_actions

        if "3 bhk" in text_lower or "3bhk" in text_lower:
            if is_hindi:
                reply = "हमारा 3 BHK कॉन्फ़िगरेशन ₹1.75 करोड़ से शुरू होता है, जिसमें विशाल बालकनियाँ और प्राकृतिक रोशनी वाले लेआउट हैं। क्या आप जल्द शिफ्ट करने की योजना बना रहे हैं?"
            elif is_hinglish:
                reply = "Hamara 3 BHK configuration ₹1.75 Crore onwards start hota hai, jisme wide balconies aur natural light designed layouts hain. Kya aap immediate shifting plan kar rahe hain?"
            else:
                reply = "Our 3 BHK luxury residences start from ₹1.75 Crore onwards with expansive balconies and great sunlight. Are you planning to move in soon?"
            return reply, None, executed_actions

        # Default Greeting based on selected language
        if is_hindi:
            reply = "नमस्ते! मैं नॉर्थस्टार होम्स से तारा हूँ। हम सेक्टर 79, गुरुग्राम में नॉर्थस्टार वन पेश कर रहे हैं, जिसमें 2 BHK ₹1.35 करोड़ से और 3 BHK ₹1.75 करोड़ से शुरू होते हैं। आप किस कॉन्फ़िगरेशन में रुचि रखते हैं?"
        elif is_hinglish:
            reply = "Namaste! Main Tara hoon Northstar Homes se. Northstar One Sector 79 Gurugram me 2 BHK ₹1.35 Cr se aur 3 BHK ₹1.75 Cr se start hota hai. Aap kis configuration me interested hain?"
        else:
            reply = "Hello! I am Tara from Northstar Homes. We are currently showcasing Northstar One in Sector 79, Gurugram, offering luxury 2 BHK from ₹1.35 Cr and 3 BHK from ₹1.75 Cr. Are you looking for a 2 BHK or 3 BHK home?"
        
        return reply, None, executed_actions

    def extract_analytics(self, transcript_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze conversation transcript and extract structured intelligence data.
        """
        if self.provider != "mock" and self._openai_client:
            try:
                transcript_text = "\n".join([
                    f"{m.get('role', 'user').upper()}: {m.get('content', '')}"
                    for m in transcript_messages
                    if m.get('role') in ('user', 'assistant', 'system')
                ])
                
                response = self._openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a lead extraction analyst. Extract structured JSON analytics strictly adhering to the schema."},
                        {"role": "user", "content": f"Analyze this conversation transcript and extract JSON analytics:\n\n{transcript_text}"}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                return result
            except Exception as e:
                logger.error(f"Error extracting analytics with LLM: {e}. Using deterministic extraction.")

        return self._extract_deterministic_analytics(transcript_messages)

    def _extract_deterministic_analytics(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Heuristic-based extraction when offline or using Mock LLM."""
        user_msgs = [m.get("content", "") for m in messages if m.get("role") == "user"]
        user_text = " ".join(user_msgs).lower()
        full_text = " ".join([m.get("content", "") for m in messages]).lower()
        
        # Configuration
        config = "Undecided"
        has_2bhk = "2 bhk" in user_text or "2bhk" in user_text or "2-bhk" in user_text
        has_3bhk = "3 bhk" in user_text or "3bhk" in user_text or "3-bhk" in user_text

        if has_2bhk and has_3bhk:
            config = "Both"
        elif has_2bhk:
            config = "2 BHK"
        elif has_3bhk:
            config = "3 BHK"

        # Language
        lang = "English"
        if any(w in user_text for w in ["नमस्ते", "दूरी", "कैसी", "महंगा", "करना", "बताओ"]):
            lang = "Hindi"
        elif any(w in user_text for w in ["kya", "hai", "mujhe", "batao", "chahiye", "theek", "hoon", "kaunsa", "aana", "mehnga", "zyada"]):
            lang = "Hinglish"

        # DND
        is_dnd = any(w in user_text for w in ["don't call", "stop calling", "remove my number", "dnd", "not interested", "mat karo", "डिलीट", "बंद"])
        
        # Human Escalation
        is_escalated = any(w in user_text for w in ["manager", "human", "agent", "senior", "negotiate", "director", "बात करनी"])

        # Site Visit Status
        site_visit_status = "Not Discussed"
        site_visit_details = None
        if "fully booked" in full_text or "slot unavailable" in full_text or "पूरी तरह बुक" in full_text:
            site_visit_status = "Failed / Slot Unavailable"
            site_visit_details = {"date": "Sunday", "time_slot": "2:00 PM", "note": "Slot full, alternatives offered"}
        elif any(w in full_text for w in ["confirmed your site visit", "maine aapka site visit", "आपकी साइट विजिट बुक", "nso-", "booking id"]):
            site_visit_status = "Booked"
            site_visit_details = {"date": "Upcoming Weekend", "time_slot": "11:00 AM", "location": "Sector 79, Gurugram"}
        elif any(w in user_text for w in ["site visit", "visit", "aana", "dekhne", "देखना"]):
            site_visit_status = "Requested / Pending Details"

        # Objections
        objections = []
        if any(w in user_text for w in ["expensive", "costly", "mehnga", "budget", "महंगा"]):
            objections.append("Price / Budget constraints")
        if any(w in user_text for w in ["far", "door", "distance", "connectivity", "दूर", "कनेक्टिविटी"]):
            objections.append("Sector 79 Distance / Location")
        if any(w in user_text for w in ["4 bhk", "penthouse", "discount"]):
            objections.append("Unconfirmed configurations / Custom discount request")

        # Lead Status & Interest
        if is_dnd:
            interest = "DND"
            lead_status = "DND"
        elif is_escalated:
            interest = "High"
            lead_status = "Escalated"
        elif site_visit_status == "Booked":
            interest = "High"
            lead_status = "Hot"
        elif objections:
            interest = "Medium"
            lead_status = "Warm"
        else:
            interest = "Medium"
            lead_status = "Warm"

        # Follow-up Requirement
        follow_up = {
            "required": not is_dnd,
            "date_time": "Within 24 hours" if site_visit_status != "Booked" else "1 day prior to visit",
            "channel": "WhatsApp" if not is_dnd else "None",
            "reason": "Send site brochure and directions" if site_visit_status == "Booked" else ("Escalation callback" if is_escalated else "Nurture lead")
        }

        # Budget fit
        budget_fit = "Within Range" if config in ("2 BHK", "3 BHK") else "Not Disclosed"

        return {
            "customer_name": "Valued Prospect",
            "phone_number": "Provided in Session",
            "budget": "₹1.35 Cr - ₹1.75 Cr" if config != "Undecided" else "Not Disclosed",
            "budget_fit": budget_fit,
            "configuration_interest": config,
            "interest_level": interest,
            "purchase_timeline": "1-3 months",
            "purpose_of_purchase": "End-use",
            "site_visit_status": site_visit_status,
            "site_visit_details": site_visit_details,
            "lead_status": lead_status,
            "follow_up_requirement": follow_up,
            "human_escalation_required": is_escalated,
            "key_objections_raised": objections,
            "primary_language": lang,
            "conversation_summary": f"Customer engaged regarding Northstar One in {lang}. Discussed {config} options and project connectivity.",
            "sentiment": "Negative" if is_dnd else ("Hesitant" if objections else "Positive"),
            "next_steps": "Send site location coordinates and confirm host representative." if site_visit_status == "Booked" else ("Respect DND status." if is_dnd else "Schedule follow-up call.")
        }

llm_client = LLMClient()
