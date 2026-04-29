# Walle Browser Agent

Walle is a smart browser assistant that uses a Chrome Extension to read web pages and a local Python agent to analyze content and suggest actions safely.

## Project Structure
- `/extension`: The Chrome Extension (Manifest V3).
- `/local-agent`: The FastAPI server.
- `/docs`: Documentation and assets.

## Setup Instructions

### 1. Local Agent (Python)
1. Open **PowerShell** or Command Prompt.
2. Navigate to `local-agent/`.
3. Create a virtual environment (Recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Setup environment:
   ```powershell
   copy .env.example .env
   ```
6. Add your `OPENAI_API_KEY` to the `.env` file.
7. Start the agent:
   ```powershell
   python main.py
   ```

### 2. Chrome Extension
1. Open Chrome and go to `chrome://extensions/`.
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the `extension/` folder.

## Troubleshooting

### "python is not recognized"
Ensure Python is added to your Windows PATH. You may need to use `py` or `python3` instead of `python`.

### "Local agent offline"
- Ensure `main.py` is running and shows `Uvicorn running on http://127.0.0.1:8787`.
- Check if a firewall is blocking port 8787.
- Refresh the Chrome extension after starting the agent.

### "OpenAI API Error" (insufficient_quota)
- **Important**: A ChatGPT Plus or Claude Pro subscription does **not** include API credits. You must have a positive balance in your provider's API dashboard.
- If you don't have credits, Walle will automatically switch to **Offline Fallback Mode**.

## Multi-LLM Provider Support
Walle now supports multiple AI backends. You can choose your preferred provider in the `.env` file:
- `LLM_PROVIDER`: `openai`, `gemini`, `anthropic`, `mistral`, `groq`, `openrouter`.
- `DEFAULT_MODEL`: Specify the model name (e.g., `gemini-2.0-flash`, `gpt-4o-mini`).

**Recommendation**: Use **Gemini** for free MVP testing (requires a free Google AI Studio key).

## Offline Fallback Mode
If your selected provider fails (quota exceeded, missing key), Walle remains functional by:
- Extracting and displaying page metadata (Title, Elements count).
- Providing generic but helpful suggested actions.
- Maintaining the safety layer for risky commands.

## Syntax Verification
Run these commands to verify the code is syntactically correct:
```powershell
# Python
python -m py_compile local-agent/main.py
python -m py_compile local-agent/llm_provider.py

# Javascript
node --check extension/background.js
node --check extension/sidebar.js
node --check extension/content.js
```

## MVP Scope (Read-Only)
Walle is currently in **Read-Only MVP mode**.
- [x] Extracts: URL, Title, Visible Text, Forms, Buttons, Tables, Links.
- [x] Analyzes: AI-powered (or fallback) summary and suggestions.
- [x] Safety: Confirmation required for 13+ risky keywords.
- [!] Execution: Real actions (clicking/typing) are **blocked** for safety.

See [TESTING.md](docs/TESTING.md) for detailed verification steps.
