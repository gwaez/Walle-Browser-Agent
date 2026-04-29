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
        .then(res => res.json())
        .then(data => sendResponse({ success: true, data }))
        .catch(err => sendResponse({ success: false, error: err.message }));
        
        return true; // async
    }
    
    if (request.action === "CHECK_AGENT_HEALTH") {
        fetch(`${LOCAL_AGENT_URL}/health`)
        .then(res => res.json())
        .then(data => sendResponse({ success: true, data }))
        .catch(err => sendResponse({ success: false, error: err.message }));
        
        return true;
    }
});
