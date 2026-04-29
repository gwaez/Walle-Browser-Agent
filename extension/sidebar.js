/**
 * Walle Sidebar Logic
 */

const chatContainer = document.getElementById('chat-container');
const readPageBtn = document.getElementById('read-page-btn');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
let currentPageContext = null;
let isLoading = false;

async function checkServerStatus() {
    chrome.runtime.sendMessage({ action: "CHECK_AGENT_HEALTH" }, (response) => {
        if (response && response.success) {
            statusBadge.innerText = "Online";
            statusBadge.className = "status-badge online";
        } else {
            const errorMsg = response ? response.error : "Offline";
            statusBadge.innerText = errorMsg;
            statusBadge.className = "status-badge offline";
        }
    });
}

function setLoading(loading) {
    isLoading = loading;
    readPageBtn.disabled = loading;
    sendBtn.disabled = loading;
    readPageBtn.innerHTML = loading ? '<span class="spinner"></span> Processing...' : '<span class="btn-icon">🔍</span> Read Page';
}

async function handleReadPage() {
    if (isLoading) return;
    setLoading(true);
    addMessage("system", "Extracting page data...");
    
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!tab) throw new Error("No active tab found.");

        chrome.tabs.sendMessage(tab.id, { action: "EXTRACT_PAGE_DATA" }, (pageData) => {
            if (chrome.runtime.lastError || !pageData) {
                addMessage("system", "Error: Could not read page. Try refreshing the page.");
                setLoading(false);
                return;
            }

            currentPageContext = pageData;
            addMessage("system", "Analyzing page content...");
            
            chrome.runtime.sendMessage({ 
                action: "PROXY_TO_AGENT", 
                endpoint: "/analyze-page",
                payload: pageData 
            }, (response) => {
                setLoading(false);
                if (response && response.success) {
                    try {
                        const analysis = typeof response.data.analysis === 'string' ? JSON.parse(response.data.analysis) : response.data.analysis;
                        displayAnalysis(analysis);
                    } catch (e) {
                        addMessage("agent", "Received summary: " + response.data.analysis);
                    }
                } else {
                    addMessage("system", "Error: " + (response.error || "Agent is not responding."));
                }
            });
        });
    } catch (err) {
        addMessage("system", "Error: " + err.message);
        setLoading(false);
    }
}

async function handleSendMessage() {
    const text = userInput.value.trim();
    if (!text || isLoading) return;

    addMessage("user", text);
    userInput.value = "";
    setLoading(true);

    chrome.runtime.sendMessage({ 
        action: "PROXY_TO_AGENT", 
        endpoint: "/agent-command",
        payload: { 
            command: text,
            context: currentPageContext 
        } 
    }, (response) => {
        setLoading(false);
        if (response && response.success) {
            const data = response.data;
            if (data.status === "confirmation_required") {
                addMessage("agent", data.message);
                showConfirmation(data.action_id);
            } else if (data.status === "blocked") {
                addMessage("system", "🚫 " + data.message);
            } else {
                addMessage("agent", data.message);
            }
        } else {
            addMessage("agent", "Error: " + (response.error || "Communication failed."));
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
