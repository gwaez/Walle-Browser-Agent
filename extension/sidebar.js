/**
 * Walle Sidebar Logic
 */

const chatContainer = document.getElementById('chat-container');
const readPageBtn = document.getElementById('read-page-btn');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const statusBadge = document.getElementById('server-status');

// Initialize
checkServerStatus();
setInterval(checkServerStatus, 5000);

// Event Listeners
readPageBtn.addEventListener('click', handleReadPage);
sendBtn.addEventListener('click', handleSendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSendMessage();
});

async function checkServerStatus() {
    chrome.runtime.sendMessage({ action: "CHECK_AGENT_HEALTH" }, (response) => {
        if (response && response.success) {
            statusBadge.innerText = "Online";
            statusBadge.className = "status-badge online";
        } else {
            statusBadge.innerText = "Offline";
            statusBadge.className = "status-badge offline";
        }
    });
}

async function handleReadPage() {
    addMessage("system", "Extracting page data...");
    
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab) {
        addMessage("system", "Error: No active tab found.");
        return;
    }

    // Request data from content script
    chrome.tabs.sendMessage(tab.id, { action: "EXTRACT_PAGE_DATA" }, (pageData) => {
        if (!pageData) {
            addMessage("system", "Error: Could not read page. Try refreshing the page.");
            return;
        }

        addMessage("system", "Sending data to Walle Agent...");
        
        // Proxy to local agent
        chrome.runtime.sendMessage({ 
            action: "PROXY_TO_AGENT", 
            endpoint: "/analyze-page",
            payload: pageData 
        }, (response) => {
            if (response && response.success) {
                const analysis = JSON.parse(response.data.analysis);
                displayAnalysis(analysis);
            } else {
                addMessage("system", "Error: Agent is not responding. Ensure local server is running at :8787");
            }
        });
    });
}

async function handleSendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage("user", text);
    userInput.value = "";

    chrome.runtime.sendMessage({ 
        action: "PROXY_TO_AGENT", 
        endpoint: "/agent-command",
        payload: { command: text } 
    }, (response) => {
        if (response && response.success) {
            const data = response.data;
            if (data.status === "confirmation_required") {
                addMessage("agent", data.message);
                showConfirmation(data.action_id);
            } else {
                addMessage("agent", data.message);
            }
        } else {
            addMessage("agent", "Error communicating with agent.");
        }
    });
}

function addMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    msgDiv.innerText = text;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function displayAnalysis(analysis) {
    const content = `
        **Summary:** ${analysis.summary}
        
        **Suggested Actions:**
        ${analysis.suggested_actions.map(a => `• ${a}`).join('\n')}
        
        **Safety:** ${analysis.safety_note || "None"}
    `;
    addMessage("agent", content);
}

function showConfirmation(actionId) {
    const confirmDiv = document.createElement('div');
    confirmDiv.className = 'message agent confirmation';
    confirmDiv.innerHTML = `
        <div style="margin-top: 10px; display: flex; gap: 10px;">
            <button id="confirm-${actionId}" style="background: #22c55e; border: none; padding: 5px 10px; border-radius: 5px; color: white; cursor: pointer;">Approve</button>
            <button id="cancel-${actionId}" style="background: #ef4444; border: none; padding: 5px 10px; border-radius: 5px; color: white; cursor: pointer;">Deny</button>
        </div>
    `;
    chatContainer.appendChild(confirmDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    document.getElementById(`confirm-${actionId}`).onclick = () => handleConfirm(actionId, true);
    document.getElementById(`cancel-${actionId}`).onclick = () => handleConfirm(actionId, false);
}

async function handleConfirm(actionId, confirmed) {
    chrome.runtime.sendMessage({ 
        action: "PROXY_TO_AGENT", 
        endpoint: "/confirm-action",
        payload: { action_id: actionId, confirmed: confirmed } 
    }, (response) => {
        if (response && response.success) {
            addMessage("system", response.data.message);
        }
    });
}
