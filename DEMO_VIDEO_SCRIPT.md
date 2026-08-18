# Demo Video Recording Guide & Script
### Huvo AI — Forward Deployed Engineer Assignment
**Candidate Demo Walkthrough Guide (Duration: 3 - 5 Minutes)**

---

## 🎬 Video Overview & Outline

| Timestamp | Section | Key Talking Points | Screen Activity |
|---|---|---|---|
| **0:00 - 0:45** | **Introduction & Problem Statement** | Introduce yourself, state the project goal (AI Sales Agent "Tara" for Northstar Homes in Sector 79 Gurugram). | Show FastAPI app running in browser at `http://localhost:8000`. |
| **0:45 - 1:45** | **Prompt Engineering & Voice-First Approach** | Explain dual-modality (voice + chat), 1-3 sentence spoken cadence, zero markdown clutter, multilingual English/Hindi/Hinglish mirroring, strict anti-hallucination. | Show `PROMPT.md` in editor. |
| **1:45 - 3:00** | **Live Bot Demonstration & Scenarios** | 1. Hinglish inquiry & Price objection<br>2. Hindi connectivity question<br>3. Site visit booking & Slot full failure fallback<br>4. DND opt-out / Human escalation. | Interact with live Web UI, show Voice audio output toggle. |
| **3:00 - 3:45** | **Post-Conversation Analytics Extraction** | Click *"End & Generate Analytics"*, show structured JSON lead intelligence (Budget fit, Configuration, Lead Status, Objections). | Showcase the Analytics Modal & raw JSON. |
| **3:45 - 4:30** | **Technical Implementation & Test Suite** | FastAPI modular architecture, session manager, tools simulation, automated pytest suite (14 passing tests). | Show terminal running `python -m pytest` and `python tests/run_scenarios.py`. |
| **4:30 - 4:45** | **Conclusion & Wrap Up** | Thank the Huvo AI team, recap how this architecture scales for enterprise voice/chat bots. | Closing screen. |

---

## 🎙️ Step-by-Step Spoken Script

### 1. Introduction (0:00 - 0:45)
> *"Hello Huvo AI team! My name is [Your Name], and this is my submission for the Forward Deployed Engineer assignment.*
>
> *I have built an AI conversational sales agent named 'Tara' for Northstar Homes, showcasing their luxury residential project 'Northstar One' in Sector 79, Gurugram. The agent is built with a FastAPI backend and a responsive real-estate web interface, designed to operate seamlessly across both telephony voice calls and text chat."*

---

### 2. Prompt Engineering Approach (0:45 - 1:45)
> *(Switch screen to `PROMPT.md`)*
>
> *"Let's take a quick look at the prompt approach:*
> 1. *Voice & Telephony Readiness: The prompt is structured for natural spoken cadence—keeping responses between 1 to 3 sentences per turn and strictly omitting markdown asterisks, bullet points, or emojis that degrade TTS clarity.*
> 2. *Multilingual Code-Switching: Tara naturally mirrors customer language in English, Hindi, and Hinglish.*
> 3. *Strict Anti-Hallucination Guardrail: Tara only uses confirmed project facts (2 BHK from ₹1.35 Cr, 3 BHK from ₹1.75 Cr, Sector 79). If asked for unconfirmed specs or discounts, she gracefully routes the customer to Senior Property Consultants.*
> 4. *Robust Behavior Playbooks: We have dedicated playbooks for lead qualification, objection handling, busy customers, DND requests, site-visit booking, and slot failure recovery."*

---

### 3. Live Bot Demonstration (1:45 - 3:00)
> *(Switch screen to browser at `http://localhost:8000`)*
>
> *"Now let's see Tara in action.*
>
> *First, let's test Hinglish language and price objection handling. I'll type:*
> `'2 BHK ka price kya hai? ₹1.35 Cr thoda mehnga lag raha hai Sector 79 ke hisaab se.'`
>
> *Notice how Tara empathizes in natural Hinglish, highlights the Aravalli foothills view, luxury amenities, and invites the customer to experience the show flat in person.*
>
> *Next, let's test site visit booking with failure fallback. Let's toggle the 'Simulate Booking Failure' switch and ask:*
> `'I want to book a visit for Sunday at 2:00 PM.'`
>
> *Tara identifies that the 2 PM slot is full and gracefully offers alternative open slots for Sunday 4:30 PM or Monday 11:00 AM without breaking the conversational flow.*
>
> *Notice also that the Live Lead Qualification Card on the right sidebar updates in real time with the detected budget, configuration, and lead temperature."*

---

### 4. Post-Conversation Analytics (3:00 - 3:45)
> *(Click the 'End & Generate Analytics' button)*
>
> *"When a conversation ends, our FastAPI backend triggers an automated intelligence extraction pipeline. Here we get a structured CRM lead profile:*
> - *Lead status (Hot / Warm / Cold / DND)*
> - *Stated configuration and budget range*
> - *Site visit status and appointment details*
> - *Sentiment, key objections, and recommended next steps for sales reps.*
>
> *This can be copied or downloaded as clean JSON for direct CRM ingestion."*

---

### 5. Code Architecture & Test Suite (3:45 - 4:30)
> *(Switch screen to Terminal / IDE)*
>
> *"Under the hood, the backend is built with FastAPI in Python 3.11. It features a modular provider gateway that supports OpenAI, Groq, OpenRouter, and a built-in Mock LLM engine for offline testing.*
>
> *Let's run our test suite:*
> `python -m pytest -v`
>
> *All 14 unit and integration tests pass across qualification, Hindi/Hinglish handling, DND, anti-hallucination, and booking failure recovery.*
>
> *We also have a standalone scenario evaluator in `tests/run_scenarios.py` that generates a complete Markdown verification log in `test_results.md`."*

---

### 6. Closing (4:30 - 4:45)
> *"Thank you for your time and for reviewing my submission. I look forward to discussing how we can build high-impact AI agents together at Huvo AI!"*
