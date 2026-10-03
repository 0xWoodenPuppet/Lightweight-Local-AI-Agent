// Initialize Lucide icons
lucide.createIcons();

const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const messagesArea = document.getElementById('chat-messages');

// Drawer elements
const drawer = document.getElementById('artifact-drawer');
const closeDrawerBtn = document.getElementById('close-drawer');
const drawerVerification = document.getElementById('drawer-verification');
const drawerVIcon = document.getElementById('drawer-v-icon');
const drawerVTitle = document.getElementById('drawer-v-title');
const drawerVReason = document.getElementById('drawer-v-reason');

const drawerTelemetry = document.getElementById('drawer-telemetry');
const teleRouterTime = document.getElementById('telemetry-router-time');
const teleSynthTime = document.getElementById('telemetry-synth-time');

const drawerToolTrace = document.getElementById('drawer-tool-trace');
const drawerSkillName = document.getElementById('drawer-skill-name');
const drawerSkillInput = document.getElementById('drawer-skill-input');
const drawerSkillOutput = document.getElementById('drawer-skill-output');

// Auto-resize textarea
chatInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);
closeDrawerBtn.addEventListener('click', closeDrawer);

function openDrawer() {
    drawer.classList.remove('translate-x-full');
}

function closeDrawer() {
    drawer.classList.add('translate-x-full');
}

function appendUserMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex w-full justify-end';
    msgDiv.innerHTML = `
        <div class="max-w-[80%] bg-slate-100 text-slate-800 p-4 rounded-2xl rounded-tr-sm shadow-sm msg-content">
            <p class="leading-relaxed">${text}</p>
        </div>
    `;
    messagesArea.appendChild(msgDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function appendAgentMessage(text, isLoading = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex w-full';
    
    let content = text;
    if (isLoading) {
        content = `<div class="flex gap-1 items-center h-6">
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0s"></div>
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
        </div>`;
    } else {
        content = marked.parse(text);
    }

    msgDiv.innerHTML = `
        <div class="max-w-[80%] bg-sage-500 text-white p-4 rounded-2xl rounded-tl-sm shadow-sm msg-content relative">
            ${content}
        </div>
    `;
    messagesArea.appendChild(msgDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    return msgDiv;
}

function formatDuration(nano) {
    if (!nano) return "-";
    const ms = nano / 1000000;
    if (ms > 1000) {
        return (ms / 1000).toFixed(2) + " s";
    }
    return ms.toFixed(0) + " ms";
}

async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    // UI Updates
    chatInput.value = '';
    chatInput.style.height = 'auto';
    appendUserMessage(query);
    const loadingMsg = appendAgentMessage('', true);
    closeDrawer();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        const data = await response.json();
        
        // Remove loading state
        loadingMsg.remove();

        if (data.error) {
            appendAgentMessage(`**Error:** ${data.error}`);
            return;
        }

        // Add final answer
        appendAgentMessage(data.final_answer);

        // Populate drawer
        populateDrawer(data);
        
        // Always open drawer if a tool was used
        if (data.chosen_skill !== "none") {
            openDrawer();
        }

    } catch (error) {
        loadingMsg.remove();
        appendAgentMessage(`**Connection Error:** ${error.message}`);
    }
}

function populateDrawer(data) {
    // 1. Verification
    if (data.verification) {
        drawerVerification.classList.remove('hidden');
        drawerVTitle.textContent = data.verification.status.toUpperCase();
        drawerVReason.textContent = data.verification.reason;
        
        if (data.verification.verified) {
            drawerVerification.className = 'mb-6 p-4 rounded-xl border bg-green-50 border-green-200 shadow-sm block';
            drawerVIcon.className = 'p-1 rounded-full bg-green-100 text-green-600 mt-0.5';
            drawerVIcon.innerHTML = `<i data-lucide="check" class="w-4 h-4"></i>`;
        } else {
            drawerVerification.className = 'mb-6 p-4 rounded-xl border bg-amber-50 border-amber-200 shadow-sm block';
            drawerVIcon.className = 'p-1 rounded-full bg-amber-100 text-amber-600 mt-0.5';
            drawerVIcon.innerHTML = `<i data-lucide="alert-triangle" class="w-4 h-4"></i>`;
        }
    } else {
        drawerVerification.classList.add('hidden');
    }

    // 2. Telemetry
    if (data.telemetry) {
        drawerTelemetry.classList.remove('hidden');
        const routerDur = data.telemetry.router ? data.telemetry.router.total_duration : null;
        const synthDur = data.telemetry.synthesis ? data.telemetry.synthesis.total_duration : null;
        
        teleRouterTime.textContent = formatDuration(routerDur);
        teleSynthTime.textContent = formatDuration(synthDur);
    } else {
        drawerTelemetry.classList.add('hidden');
    }

    // 3. Tool Trace
    if (data.chosen_skill !== "none") {
        drawerToolTrace.classList.remove('hidden');
        drawerSkillName.textContent = data.chosen_skill;
        drawerSkillInput.textContent = data.skill_input || "No input";
        drawerSkillOutput.textContent = data.skill_output || "No output";
    } else {
        drawerToolTrace.classList.add('hidden');
    }

    lucide.createIcons();
}
