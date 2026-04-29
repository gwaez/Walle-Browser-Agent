# Walle Browser Agent

Walle is a smart browser assistant that uses a Chrome Extension to read web pages and a local Python agent to analyze content and suggest actions safely.

## Project Structure
- `/extension`: The Chrome Extension (Manifest V3).
- `/local-agent`: The FastAPI server.
- `/docs`: Documentation and assets.

## Setup Instructions

### 1. Local Agent (Python)
1. Navigate to `local-agent/`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
4. Add your `OPENAI_API_KEY` to the `.env` file.
5. Start the agent:
   ```bash
   python main.py
   ```
   The agent will run at `http://localhost:8787`.

### 2. Chrome Extension
1. Open Chrome and go to `chrome://extensions/`.
2. Enable **Developer mode** (top right).
3. Click **Load unpacked**.
4. Select the `extension/` folder from this project.
5. Pin the Walle extension for easy access.

## How to Use
1. Open the Walle side panel (click the extension icon or use the side panel menu).
2. Navigate to any website.
3. Click **"Read Page"**.
4. Walle will extract the DOM structure, forms, and buttons, then send them to the local agent.
5. The agent (GPT-4o-mini) will provide a summary and suggest next steps.
6. Type commands in the chat. If a command involves sensitive actions (e.g., "delete", "post"), Walle will ask for confirmation first.

## Safety Layer
Walle includes a safety layer that flags keywords like:
- `approve`, `submit`, `delete`, `cancel`, `send`, `save`, `post`, `payment`.

Any command containing these keywords will trigger a "Confirmation Required" UI in the sidebar before the agent proceeds.

## MVP Features
- [x] Page scraping (Text, Forms, Buttons, Tables)
- [x] Local FastAPI communication
- [x] AI-powered analysis and suggestions
- [x] Safety confirmation UI
- [x] Premium dark-mode UI
