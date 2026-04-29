# Walle Browser Agent Implementation Plan

Create a Chrome Extension and a local Python Agent that work together to analyze web pages and suggest actions safely.

## User Review Required

> [!IMPORTANT]
> The extension requires a local server running at `http://localhost:8787`. You will need to install Python dependencies and provide an OpenAI API key in a `.env` file.

> [!WARNING]
> Chrome Extensions communicating with `localhost` may require specific CSP settings or user permissions if deployed, but for development (unpacked), it should work directly.

## Proposed Changes

### 1. Extension Component (`/extension`)

The extension will use Manifest V3 and the `sidePanel` API for a modern sidebar experience.

#### [NEW] [manifest.json](file:///c:/New%20folder%20(2)/Codz/Walle%20Browser%20Agent/extension/manifest.json)
- Define permissions: `sidePanel`, `activeTab`, `scripting`.
- Set `side_panel` default path to `sidebar.html`.

#### [NEW] [sidebar.html](file:///c:/New%20folder%20(2)/Codz/Walle%20Browser%20Agent/extension/sidebar.html) & [sidebar.css](file:///c:/New%20folder%20(2)/Codz/Walle%20Browser%20Agent/extension/sidebar.css)
- Premium dark UI with glassmorphism effects.
- Chat interface and "Read Page" button.

#### [NEW] [sidebar.js](file:///c:/New%20folder%20(2)/Codz/Walle%20Browser%20Agent/extension/sidebar.js)
- Handle UI events.
- Communicate with `background.js` or `content.js`.

#### [NEW] [content.js](file:///c:/New%20folder%20(2)/Codz/Walle%20Browser%20Agent/extension/content.js)
- Extract text, forms, buttons, and tables from the active tab.

#### [NEW] [background.js](file:///c:/New%20folder%20(2)/Codz/Walle%20Browser%20Agent/extension/background.js)
- Act as a proxy for fetch requests to `localhost:8787` to avoid CORS issues from the content script.

---

### 2. Local Agent Component (`/local-agent`)

A FastAPI server to process page data and interface with OpenAI.

#### [NEW] [main.py](file:///c:/New%20folder%20(2)/Codz/Walle%20Browser%20Agent/local-agent/main.py)
- FastAPI endpoints: `/health`, `/analyze-page`, `/agent-command`, `/confirm-action`.
- Implementation of the safety layer.

#### [NEW] [requirements.txt](file:///c:/New%20folder%20(2)/Codz/Walle%20Browser%20Agent/local-agent/requirements.txt)
- `fastapi`, `uvicorn`, `python-dotenv`, `openai`, `pydantic`.

#### [NEW] [.env.example](file:///c:/New%20folder%20(2)/Codz/Walle%20Browser%20Agent/local-agent/.env.example)
- Placeholder for `OPENAI_API_KEY`.

---

### 3. Documentation (`/docs`)

#### [NEW] [README.md](file:///c:/New%20folder%20(2)/Codz/Walle%20Browser%20Agent/README.md)
- Step-by-step setup for both extension and local agent.

## Verification Plan

### Automated Tests
- Run `uvicorn main:app --port 8787` and test health/analyze endpoints via `curl` or a test script.

### Manual Verification
- Load the `/extension` folder as an unpacked extension in Chrome.
- Open the side panel.
- Click "Read Page" and verify the agent's response in the UI.
