/**
 * Walle Background Service Worker
 * Proxy for local agent communication
 */

const LOCAL_AGENT_URL = "http://localhost:8787";

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "PROXY_TO_AGENT") {
        fetch(`${LOCAL_AGENT_URL}${request.endpoint}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(request.payload)
        })
        .then(async (res) => {
            if (!res.ok) {
                const errorText = await res.text();
                throw new Error(`Agent returned ${res.status}: ${errorText}`);
            }
            return res.json();
        })
        .then((data) => sendResponse({ success: true, data }))
        .catch((err) => {
            console.error("Agent Error:", err);
            sendResponse({ 
                success: false, 
                error: "Local agent is not reachable. Ensure 'python main.py' is running at http://localhost:8787" 
            });
        });
        
        return true; // Keep channel open for async response
    }
    
    if (request.action === "CHECK_AGENT_HEALTH") {
        fetch(`${LOCAL_AGENT_URL}/health`)
        .then((res) => res.json())
        .then((data) => sendResponse({ success: true, data }))
        .catch(() => sendResponse({ 
            success: false, 
            error: "Offline" 
        }));
        
        return true;
    }
});
