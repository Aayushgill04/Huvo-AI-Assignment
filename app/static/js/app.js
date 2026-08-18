/**
 * Northstar Homes AI Sales Agent (Tara) - Interactive Client Application
 */

document.addEventListener('DOMContentLoaded', () => {
    // Generate or retrieve session ID
    let sessionId = localStorage.getItem('northstar_session_id') || 'sess_' + Math.random().toString(36).substring(2, 9);
    localStorage.setItem('northstar_session_id', sessionId);

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

    // Speech Synthesis (TTS) State
    let isVoiceEnabled = false;
    let currentAnalyticsData = null;

    // Initialize Event Listeners
    sendBtn.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });

    clearChatBtn.addEventListener('click', resetConversation);
    endChatBtn.addEventListener('click', handleEndConversation);
    
    closeModalBtn.addEventListener('click', () => analyticsModal.style.display = 'none');
    modalCloseActionBtn.addEventListener('click', () => analyticsModal.style.display = 'none');
    
    voiceToggle.addEventListener('change', (e) => {
        isVoiceEnabled = e.target.checked;
        if (isVoiceEnabled && 'speechSynthesis' in window) {
            speakText("Voice mode enabled. I am ready to assist you.");
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

    // Quick Prompt Chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const promptText = chip.getAttribute('data-prompt');
            userInput.value = promptText;
            handleSendMessage();
        });
    });

    // Load Scenarios
    loadScenarios();

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
                    simulate_booking_failure: failureToggle.checked
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
            renderMessage('bot', 'Apologies, I encountered a temporary connection issue. Could you please repeat that?');
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
        // Try selecting an English/Hindi pleasant female voice
        const preferredVoice = voices.find(v => (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha') || v.name.includes('Zira')) && v.lang.startsWith('en')) || voices[0];
        if (preferredVoice) utterance.voice = preferredVoice;

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
                body: JSON.stringify({ session_id: sessionId })
            });

            chatMessages.innerHTML = `
                <div class="message-group bot-group">
                    <div class="avatar">T</div>
                    <div class="message-content-wrapper">
                        <div class="sender-name">Tara <span class="role-tag">Senior Property Advisor</span></div>
                        <div class="message-bubble bot-bubble">
                            Hello and welcome! I am Tara from Northstar Homes. We are showcasing Northstar One in Sector 79, Gurugram, featuring luxury 2 BHK apartments from ₹1.35 Crore and 3 BHK from ₹1.75 Crore with scenic Aravalli views. Are you looking for a 2 BHK or 3 BHK home?
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
            metricLanguage.innerText = 'English';
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
            document.getElementById('modalLanguage').innerText = analytics.primary_language || 'English';
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
