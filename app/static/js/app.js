/**
 * Northstar Homes AI Sales Agent (Tara) - Interactive Client Application
 */

document.addEventListener('DOMContentLoaded', () => {
    // Generate or retrieve session ID
    let sessionId = localStorage.getItem('northstar_session_id') || 'sess_' + Math.random().toString(36).substring(2, 9);
    localStorage.setItem('northstar_session_id', sessionId);

    // State Variables
    let currentLanguage = 'English'; // English | Hindi | Hinglish
    let isVoiceEnabled = false;
    let currentAnalyticsData = null;

    // DOM Elements
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const typingIndicator = document.getElementById('typingIndicator');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const voiceToggle = document.getElementById('voiceToggle');
    const failureToggle = document.getElementById('failureToggle');
    const endChatBtn = document.getElementById('endChatBtn');
    const scenariosContainer = document.getElementById('scenariosContainer');
    const promptsChipsContainer = document.getElementById('promptsChipsContainer');
    const currentLangBadge = document.getElementById('currentLangBadge');
    const navLangPills = document.querySelectorAll('.lang-pill');

    // Live Metrics Elements
    const liveLeadStatus = document.getElementById('liveLeadStatus');
    const metricConfig = document.getElementById('metricConfig');
    const metricBudget = document.getElementById('metricBudget');
    const metricSiteVisit = document.getElementById('metricSiteVisit');
    const metricLanguage = document.getElementById('metricLanguage');
    const toolExecutionAlert = document.getElementById('toolExecutionAlert');
    const toolActionTitle = document.getElementById('toolActionTitle');
    const toolActionDetails = document.getElementById('toolActionDetails');

    // Modal Elements
    const analyticsModal = document.getElementById('analyticsModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const modalCloseActionBtn = document.getElementById('modalCloseActionBtn');
    const copyJsonBtn = document.getElementById('copyJsonBtn');
    const downloadJsonBtn = document.getElementById('downloadJsonBtn');
    const rawJsonContent = document.getElementById('rawJsonContent');

    // Language Data & Prompts
    const languageConfig = {
        English: {
            flagBadge: '🇬🇧 English',
            placeholder: 'Type a message in English (e.g. Tell me about 3 BHK pricing)...',
            greeting: 'Hello and welcome! I am Tara from Northstar Homes. We are showcasing Northstar One in Sector 79, Gurugram, featuring luxury 2 BHK apartments from ₹1.35 Crore and 3 BHK from ₹1.75 Crore with scenic Aravalli views. Are you looking for a 2 BHK or 3 BHK home?',
            prompts: [
                { label: '3 BHK Pricing', prompt: 'Hi, I am interested in a 3 BHK. What are the key details and pricing?' },
                { label: 'Price Objection', prompt: '₹1.35 Cr feels too high for Sector 79. Do you offer any discount?' },
                { label: 'Location & Connectivity', prompt: 'How is the connectivity from Sector 79 to Cyber City and Airport?' },
                { label: 'Book Visit (11 AM)', prompt: 'Can I book a site visit for this Sunday at 11:00 AM? My name is Amit Sharma.' },
                { label: 'Test Slot Full (2 PM)', prompt: 'I want to book a visit for Sunday at 2:00 PM.' },
                { label: 'Busy / Call Later', prompt: 'I am driving right now in a meeting, please call me tomorrow evening.' },
                { label: 'DND Opt-Out', prompt: 'I am not interested at all, please stop calling me and remove my number.' },
                { label: '4 BHK Penthouse Query', prompt: 'Do you have a 4 BHK penthouse with private swimming pool and 25% discount?' },
                { label: 'Manager Escalation', prompt: 'I want to speak directly with your Senior Sales Manager for pricing.' }
            ]
        },
        Hindi: {
            flagBadge: '🇮🇳 हिंदी',
            placeholder: 'हिंदी में संदेश लिखें (जैसे: 2 BHK की कीमत और लोकेशन की जानकारी दीजिए)...',
            greeting: 'नमस्ते और नॉर्थस्टार होम्स में आपका स्वागत है! मैं तारा हूँ। हम सेक्टर 79, गुरुग्राम में नॉर्थस्टार वन पेश कर रहे हैं, जिसमें 2 BHK ₹1.35 करोड़ से और 3 BHK ₹1.75 करोड़ से उपलब्ध हैं। क्या आप 2 BHK या 3 BHK घर की तलाश में हैं?',
            prompts: [
                { label: '3 BHK की जानकारी', prompt: 'नमस्ते, मुझे 3 BHK फ्लैट की जानकारी और शुरुआती कीमत चाहिए।' },
                { label: 'कीमत पर आपत्ति', prompt: '₹1.35 करोड़ सेक्टर 79 के हिसाब से काफी महंगा लग रहा है। क्या कोई छूट मिलेगी?' },
                { label: 'कनेक्टिविटी प्रश्न', prompt: 'क्या Sector 79 बहुत दूर नहीं है? Cyber City से कनेक्टिविटी कैसी है?' },
                { label: 'साइट विजिट बुक करें', prompt: 'क्या मैं इस रविवार सुबह 11:00 बजे साइट विजिट बुक कर सकता हूँ? मेरा नाम अमित है।' },
                { label: 'फुल स्लॉट टेस्ट (2 PM)', prompt: 'मुझे रविवार दोपहर 2:00 बजे का स्लॉट बुक करना है।' },
                { label: 'व्यस्त / बाद में कॉल करें', prompt: 'मैं अभी ड्राइविंग कर रहा हूँ, कृपया कल शाम को कॉल करें।' },
                { label: 'कॉल मत करना (DND)', prompt: 'मुझे कोई रुचि नहीं है, कृपया मुझे दोबारा कॉल मत करना और नंबर हटा दीजिए।' },
                { label: '4 BHK पेंटहाउस प्रश्न', prompt: 'क्या आपके पास प्राइवेट स्विमिंग पूल वाला 4 BHK पेंटहाउस है और 25% डिस्काउंट मिलेगा?' },
                { label: 'सीनियर मैनेजर से बात', prompt: 'मुझे कीमत पर बातचीत के लिए आपके सीनियर सेल्स मैनेजर से सीधे बात करनी है।' }
            ]
        },
        Hinglish: {
            flagBadge: '🗣️ Hinglish',
            placeholder: 'Hinglish mein message likhein (jaise: 2 BHK ka price kya hai aur discount milega kya?)...',
            greeting: 'Namaste aur Northstar Homes me aapka swagat hai! Main Tara hoon. Hamara luxury project Northstar One Sector 79 Gurugram me 2 BHK ₹1.35 Crore se aur 3 BHK ₹1.75 Crore se shuru hota hai. Aap 2 BHK dekh rahe hain ya 3 BHK?',
            prompts: [
                { label: '3 BHK Inquiry', prompt: 'Hi, 3 BHK ka price aur details kya hai Northstar One me?' },
                { label: 'Price Objection', prompt: 'Price bahut zyada lag raha hai, Sector 79 ke hisaab se discount milega kya?' },
                { label: 'Location Query', prompt: 'Sector 79 kitna door hai Cyber City se aur connectivity kaisa hai?' },
                { label: 'Book Visit (11 AM)', prompt: 'Can I book a site visit for this Sunday at 11:00 AM? Mera naam Amit Sharma hai.' },
                { label: 'Slot Full Test (2 PM)', prompt: 'I want to book a visit for Sunday at 2:00 PM.' },
                { label: 'Busy / Call Later', prompt: 'Abhi driving kar raha hoon meeting me, please kal evening me call karna.' },
                { label: 'DND Opt-Out', prompt: 'Mujhe koi interest nahi hai, please call mat karna aur number delete kar do.' },
                { label: 'Out of Scope Query', prompt: 'Kya aapke pass 4 BHK penthouse hai with private pool aur 25% discount?' },
                { label: 'Human Escalation', prompt: 'Mujhe Senior Sales Manager se directly baat karni hai pricing finalize karne ke liye.' }
            ]
        }
    };

    // Initialize Event Listeners
    sendBtn.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });

    clearChatBtn.addEventListener('click', resetConversation);
    endChatBtn.addEventListener('click', handleEndConversation);
    
    closeModalBtn.addEventListener('click', () => analyticsModal.style.display = 'none');
    modalCloseActionBtn.addEventListener('click', () => analyticsModal.style.display = 'none');
    
    // Language Pill Clicks
    navLangPills.forEach(pill => {
        pill.addEventListener('click', () => {
            const selectedLang = pill.getAttribute('data-lang');
            setLanguage(selectedLang);
        });
    });

    voiceToggle.addEventListener('change', (e) => {
        isVoiceEnabled = e.target.checked;
        if (isVoiceEnabled && 'speechSynthesis' in window) {
            const voiceConfirm = currentLanguage === 'Hindi' 
                ? 'वॉयस मोड सक्षम किया गया है। मैं आपकी सहायता के लिए तैयार हूँ।'
                : (currentLanguage === 'Hinglish' ? 'Voice mode on hai. Main aapki help ke liye ready hoon.' : 'Voice mode enabled. I am ready to assist you.');
            speakText(voiceConfirm);
        }
    });

    failureToggle.addEventListener('change', async (e) => {
        const simulate = e.target.checked;
        try {
            await fetch('/api/chat/simulate-failure', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, simulate_failure: simulate })
            });
        } catch (err) {
            console.error("Failed to toggle failure simulation:", err);
        }
    });

    copyJsonBtn.addEventListener('click', () => {
        if (currentAnalyticsData) {
            navigator.clipboard.writeText(JSON.stringify(currentAnalyticsData, null, 2));
            copyJsonBtn.innerText = 'Copied!';
            setTimeout(() => copyJsonBtn.innerText = 'Copy JSON', 2000);
        }
    });

    downloadJsonBtn.addEventListener('click', () => {
        if (currentAnalyticsData) {
            const blob = new Blob([JSON.stringify(currentAnalyticsData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `lead_analytics_${sessionId}.json`;
            a.click();
            URL.revokeObjectURL(url);
        }
    });

    // Set Initial Language Mode & Prompts
    setLanguage('English', false);

    // Load Scenarios
    loadScenarios();

    // =========================================================================
    // Language Switching Logic
    // =========================================================================

    function setLanguage(lang, updateGreeting = true) {
        if (!languageConfig[lang]) return;
        currentLanguage = lang;

        // Update Nav Pills Active State
        navLangPills.forEach(pill => {
            if (pill.getAttribute('data-lang') === lang) {
                pill.classList.add('active');
            } else {
                pill.classList.remove('active');
            }
        });

        // Update Project Banner Badge
        currentLangBadge.innerText = languageConfig[lang].flagBadge;

        // Update Input Placeholder
        userInput.placeholder = languageConfig[lang].placeholder;

        // Update Sidebar Metric
        metricLanguage.innerText = lang;

        // Update Quick Prompt Chips
        renderQuickPrompts(lang);

        // Update Greeting if fresh chat
        if (updateGreeting) {
            const initialGreetingBubble = document.getElementById('initialGreetingBubble');
            if (initialGreetingBubble && chatMessages.children.length === 1) {
                initialGreetingBubble.innerText = languageConfig[lang].greeting;
            }
        }
    }

    function renderQuickPrompts(lang) {
        const config = languageConfig[lang];
        promptsChipsContainer.innerHTML = '';

        config.prompts.forEach(p => {
            const chip = document.createElement('button');
            chip.className = 'chip';
            chip.innerText = p.label;
            chip.setAttribute('data-prompt', p.prompt);
            chip.addEventListener('click', () => {
                userInput.value = p.prompt;
                handleSendMessage();
            });
            promptsChipsContainer.appendChild(chip);
        });
    }

    // =========================================================================
    // Core Chat Interaction
    // =========================================================================

    async function handleSendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // Render User Message
        renderMessage('user', text);
        userInput.value = '';
        userInput.focus();

        // Show Typing Indicator
        typingIndicator.style.display = 'flex';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    message: text,
                    simulate_booking_failure: failureToggle.checked,
                    preferred_language: currentLanguage
                })
            });

            if (!response.ok) throw new Error('API Error: ' + response.statusText);

            const data = await response.json();
            
            // Hide Typing
            typingIndicator.style.display = 'none';

            // Render Bot Message
            renderMessage('bot', data.reply, data.all_actions);

            // Trigger Voice TTS if enabled
            if (isVoiceEnabled) {
                speakText(data.reply);
            }

            // Update Live Lead Card
            if (data.live_analytics) {
                updateLiveMetrics(data.live_analytics);
            }

            // Show Tool Execution Alert if any action happened
            if (data.all_actions && data.all_actions.length > 0) {
                const lastAction = data.all_actions[data.all_actions.length - 1];
                showToolAlert(lastAction);
            }

        } catch (error) {
            typingIndicator.style.display = 'none';
            const errReply = currentLanguage === 'Hindi'
                ? 'माफ़ कीजिए, कनेक्शन में अस्थायी समस्या आई है। क्या आप दोबारा संदेश भेज सकते हैं?'
                : 'Apologies, I encountered a temporary connection issue. Could you please repeat that?';
            renderMessage('bot', errReply);
            console.error('Chat error:', error);
        }
    }

    function renderMessage(role, text, actions = []) {
        const group = document.createElement('div');
        group.className = `message-group ${role === 'user' ? 'user-group' : 'bot-group'}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerText = role === 'user' ? 'U' : 'T';

        const wrapper = document.createElement('div');
        wrapper.className = 'message-content-wrapper';

        const sender = document.createElement('div');
        sender.className = 'sender-name';
        sender.innerHTML = role === 'user' ? 'You' : 'Tara <span class="role-tag">Senior Property Advisor</span>';

        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${role === 'user' ? 'user-bubble' : 'bot-bubble'}`;
        bubble.innerText = text;

        wrapper.appendChild(sender);
        wrapper.appendChild(bubble);

        // Append tool badges if present
        if (actions && actions.length > 0) {
            actions.forEach(action => {
                const pill = document.createElement('div');
                const isSuccess = action.result && action.result.success !== false;
                pill.className = `tool-badge-pill ${isSuccess ? 'success' : 'danger'}`;
                
                if (action.tool === 'book_site_visit') {
                    pill.innerHTML = isSuccess 
                        ? `📅 Site Visit Confirmed: ${action.result.booking_id || 'NSO-Booked'}` 
                        : `⚠️ Slot Unavailable: Alternatives Offered`;
                } else if (action.tool === 'mark_dnd') {
                    pill.innerHTML = `🛡️ Do-Not-Disturb (DND) Activated`;
                } else if (action.tool === 'escalate_to_human') {
                    pill.innerHTML = `👤 Escalated to Senior Sales Manager`;
                } else if (action.tool === 'schedule_followup') {
                    pill.innerHTML = `⏰ Callback Scheduled: ${action.args.date_time || 'Tomorrow'}`;
                }
                wrapper.appendChild(pill);
            });
        }

        const meta = document.createElement('div');
        meta.className = 'message-meta';
        const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        meta.innerText = `${now} • ${role === 'user' ? 'Customer' : 'Voice-Ready'}`;
        wrapper.appendChild(meta);

        group.appendChild(avatar);
        group.appendChild(wrapper);

        chatMessages.appendChild(group);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // =========================================================================
    // Web Speech API / TTS
    // =========================================================================

    function speakText(text) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel(); // Stop ongoing speech

        // Clean any unexpected characters
        const cleanText = text.replace(/[*#_`]/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        
        utterance.rate = 1.0;
        utterance.pitch = 1.05;
        
        const voices = window.speechSynthesis.getVoices();
        
        // Pick language appropriate voice
        if (currentLanguage === 'Hindi' || /[\u0900-\u097F]/.test(cleanText)) {
            utterance.lang = 'hi-IN';
            const hindiVoice = voices.find(v => v.lang.startsWith('hi') || v.name.includes('Hindi') || v.name.includes('Kalpana') || v.name.includes('Hemant'));
            if (hindiVoice) utterance.voice = hindiVoice;
        } else {
            utterance.lang = 'en-IN';
            const preferredVoice = voices.find(v => (v.lang === 'en-IN' || v.name.includes('Indian') || v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha') || v.name.includes('Zira')) && v.lang.startsWith('en')) || voices[0];
            if (preferredVoice) utterance.voice = preferredVoice;
        }

        window.speechSynthesis.speak(utterance);
    }

    // =========================================================================
    // Live Lead & Sidebar Management
    // =========================================================================

    function updateLiveMetrics(analytics) {
        if (!analytics) return;

        if (analytics.lead_status) {
            liveLeadStatus.innerText = analytics.lead_status;
            liveLeadStatus.className = 'badge ' + (
                analytics.lead_status === 'Hot' ? 'badge-hot' :
                analytics.lead_status === 'Warm' ? 'badge-warm' :
                analytics.lead_status === 'DND' ? 'badge-dnd' : 'badge-neutral'
            );
        }

        if (analytics.configuration_interest) {
            metricConfig.innerText = analytics.configuration_interest;
        }

        if (analytics.budget) {
            metricBudget.innerText = analytics.budget;
        }

        if (analytics.site_visit_status) {
            metricSiteVisit.innerText = analytics.site_visit_status;
        }

        if (analytics.primary_language) {
            metricLanguage.innerText = analytics.primary_language;
        }
    }

    function showToolAlert(action) {
        toolExecutionAlert.style.display = 'flex';
        toolActionTitle.innerText = `Action: ${action.tool}`;
        toolActionDetails.innerText = JSON.stringify(action.args || {});
    }

    async function loadScenarios() {
        try {
            const res = await fetch('/api/scenarios');
            const data = await res.json();
            
            scenariosContainer.innerHTML = '';
            data.scenarios.forEach(sc => {
                const item = document.createElement('div');
                item.className = 'scenario-item';
                item.innerHTML = `
                    <div class="scenario-top">
                        <span class="scenario-title">${sc.title}</span>
                        <span class="scenario-tag">${sc.language}</span>
                    </div>
                    <div class="scenario-preview">${sc.prompt}</div>
                `;
                item.addEventListener('click', () => {
                    if (sc.language === 'Hindi' || sc.language === 'Hinglish') {
                        setLanguage(sc.language, false);
                    } else {
                        setLanguage('English', false);
                    }
                    userInput.value = sc.prompt;
                    handleSendMessage();
                });
                scenariosContainer.appendChild(item);
            });
        } catch (e) {
            console.error("Failed to load scenarios:", e);
        }
    }

    async function resetConversation() {
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        
        try {
            await fetch('/api/chat/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, preferred_language: currentLanguage })
            });

            chatMessages.innerHTML = `
                <div class="message-group bot-group">
                    <div class="avatar">T</div>
                    <div class="message-content-wrapper">
                        <div class="sender-name">Tara <span class="role-tag">Senior Property Advisor</span></div>
                        <div class="message-bubble bot-bubble" id="initialGreetingBubble">
                            ${languageConfig[currentLanguage].greeting}
                        </div>
                        <div class="message-meta">Just now • Reset completed</div>
                    </div>
                </div>
            `;
            
            liveLeadStatus.innerText = 'Warm';
            liveLeadStatus.className = 'badge badge-neutral';
            metricConfig.innerText = 'Undecided';
            metricBudget.innerText = 'Not Disclosed';
            metricSiteVisit.innerText = 'Not Discussed';
            metricLanguage.innerText = currentLanguage;
            toolExecutionAlert.style.display = 'none';

        } catch (err) {
            console.error("Failed to reset session:", err);
        }
    }

    // =========================================================================
    // End Conversation & Analytics Extraction Modal
    // =========================================================================

    async function handleEndConversation() {
        try {
            const res = await fetch('/api/chat/end', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });

            const data = await res.json();
            const analytics = data.analytics;
            currentAnalyticsData = analytics;

            // Populate Modal
            document.getElementById('modalLeadStatus').innerText = analytics.lead_status || 'Warm';
            document.getElementById('modalConfig').innerText = analytics.configuration_interest || 'Undecided';
            document.getElementById('modalBudget').innerText = analytics.budget || 'Not Disclosed';
            document.getElementById('modalSiteVisitStatus').innerText = analytics.site_visit_status || 'Not Discussed';
            
            document.getElementById('modalSummaryText').innerText = analytics.conversation_summary || 'No summary available.';
            document.getElementById('modalInterestLevel').innerText = analytics.interest_level || 'Medium';
            document.getElementById('modalTimeline').innerText = analytics.purchase_timeline || 'Unknown';
            document.getElementById('modalPurpose').innerText = analytics.purpose_of_purchase || 'Not Disclosed';
            document.getElementById('modalLanguage').innerText = analytics.primary_language || currentLanguage;
            document.getElementById('modalSentiment').innerText = analytics.sentiment || 'Neutral';
            document.getElementById('modalEscalation').innerText = analytics.human_escalation_required ? 'Yes (Escalated)' : 'No';

            const followUp = analytics.follow_up_requirement || {};
            document.getElementById('modalFollowupRequired').innerText = followUp.required ? 'Yes' : 'No';
            document.getElementById('modalFollowupChannel').innerText = followUp.channel || 'None';
            
            const objections = analytics.key_objections_raised || [];
            document.getElementById('modalObjections').innerText = objections.length > 0 ? objections.join(', ') : 'None raised';
            document.getElementById('modalNextSteps').innerText = analytics.next_steps || 'Standard CRM follow-up';

            rawJsonContent.innerText = JSON.stringify(analytics, null, 2);

            analyticsModal.style.display = 'flex';

        } catch (err) {
            console.error("Failed to end conversation:", err);
            alert("Could not extract analytics for this session.");
        }
    }
});
