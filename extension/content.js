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
    // Helper to check if element is visible
    const isVisible = (el) => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);

    return {
        url: window.location.href,
        title: document.title,
        text: document.body.innerText.substring(0, 3000), // Reduced limit for cleaner payloads
        forms: Array.from(document.querySelectorAll('form')).map(f => ({
            id: f.id,
            action: f.action,
            inputs: Array.from(f.querySelectorAll('input, select, textarea'))
                .filter(i => i.type !== 'password' && i.type !== 'hidden') // Filter sensitive/hidden
                .map(i => ({
                    name: i.name || i.id,
                    type: i.type,
                    placeholder: i.placeholder
                }))
        })).filter(f => f.inputs.length > 0),
        buttons: Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'))
            .filter(isVisible)
            .map(b => ({
                text: (b.innerText || b.value || b.title || "").trim(),
                id: b.id,
                className: b.className
            })).filter(b => b.text.length > 0),
        tables: Array.from(document.querySelectorAll('table'))
            .filter(isVisible)
            .map(t => ({
                rows: t.rows.length,
                headers: Array.from(t.querySelectorAll('th')).map(th => th.innerText.trim())
            })),
        links: Array.from(document.querySelectorAll('a'))
            .filter(isVisible)
            .slice(0, 20) // Limit links to top 20
            .map(l => ({
                text: l.innerText.trim(),
                href: l.href
            })).filter(l => l.text.length > 0)
    };
}
