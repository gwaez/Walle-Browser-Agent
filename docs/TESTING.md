# Testing Walle Browser Agent MVP

Follow these manual tests to verify the hardened MVP.

## 1. Local Agent Tests
- [ ] **Start Agent**: Run `python main.py` in `local-agent/`.
- [ ] **Verify Health**: Open `http://localhost:8787/health` in your browser.
  - *Expected*: `{"status": "healthy", "agent": "Walle", "mode": "read-only-mvp"}`
- [ ] **Verify Logs**: Check `agent.log` is created.

## 2. Extension UI Tests
- [ ] **Connect Extension**: Load unpacked extension in Chrome.
- [ ] **Check Status**: Open sidebar. 
  - *Expected*: Badge should show "Online" (green).
- [ ] **Read Simple Page**: Go to `example.com` and click "Read Page".
  - *Expected*: Sidebar shows summary and suggested actions.
- [ ] **Read Complex Page**: Go to a page with tables (e.g., Wikipedia).
  - *Expected*: Summary includes table details.

## 3. Safety & Read-Only Tests
- [ ] **Risk Detection**: Type "Click the approve button" in chat.
  - *Expected*: Sidebar shows "The action 'Click the approve button' requires your approval...".
- [ ] **Confirm Action**: Click "Approve" in the sidebar.
  - *Expected*: Sidebar shows "🚫 Action execution is not enabled in the read-only MVP."
- [ ] **Cancel Action**: Type another risky command and click "Deny".
  - *Expected*: Sidebar shows "Action aborted by user."

## 4. Troubleshooting Tests
- [ ] **Offline Detection**: Stop the Python agent.
  - *Expected*: Sidebar badge turns red and says "Offline".
- [ ] **Error Message**: Try "Read Page" while agent is offline.
  - *Expected*: Sidebar shows "Error: Local agent is not reachable...".
