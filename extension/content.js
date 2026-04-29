/**
 * Walle Content Script
 * Responsible for extracting page data
 */

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "EXTRACT_PAGE_DATA") {
        const pageData = extractData();
        sendResponse(pageData);
    }
    return true; // Keep channel open for async
});

function extractData() {
    return {
        url: window.location.href,
        title: document.title,
        text: document.body.innerText.substring(0, 5000), // Limit for MVP
        forms: Array.from(document.querySelectorAll('form')).map(f => ({
            id: f.id,
            action: f.action,
            inputs: Array.from(f.querySelectorAll('input, select, textarea')).map(i => ({
                name: i.name,
                type: i.type,
                placeholder: i.placeholder
            }))
        })),
        buttons: Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).map(b => ({
            text: b.innerText || b.value,
            id: b.id,
            className: b.className
        })),
        tables: Array.from(document.querySelectorAll('table')).map(t => ({
            rows: t.rows.length,
            headers: Array.from(t.querySelectorAll('th')).map(th => th.innerText)
        }))
    };
}
