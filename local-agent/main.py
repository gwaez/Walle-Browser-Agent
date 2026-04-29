import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

LOG_FULL_CONTENT = os.getenv("LOG_FULL_CONTENT", "false").lower() == "true"
OFFLINE_FALLBACK = os.getenv("OFFLINE_FALLBACK", "true").lower() == "true"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WalleAgent")

app = FastAPI(title="Walle Browser Agent MVP")

# Enable CORS for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI Client setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None

if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
else:
    logger.warning("OPENAI_API_KEY is missing or invalid. Agent will use fallback mode.")

class PageContext(BaseModel):
    url: str
    title: str
    text: str
    forms: List[dict]
    buttons: List[dict]
    tables: List[dict]
    links: Optional[List[dict]] = []

class AgentCommand(BaseModel):
    command: str
    context: Optional[dict] = None

class ActionConfirmation(BaseModel):
    action_id: str
    confirmed: bool

# Safety Layer Keywords - Expanded
DANGEROUS_KEYWORDS = [
    "approve", "submit", "delete", "cancel", "send", "save", "post", 
    "payment", "buy", "purchase", "transfer", "confirm", "reject"
]

def check_safety(proposed_action: str) -> bool:
    """Returns True if confirmation is required."""
    proposed_action_lower = proposed_action.lower()
    return any(keyword in proposed_action_lower for keyword in DANGEROUS_KEYWORDS)

def generate_fallback_analysis(context: PageContext, error_message: str) -> dict:
    """Generates a structured analysis without calling AI."""
    return {
        "summary": f"Walle read this page: '{context.title}'. It contains {len(context.text)} characters of text.",
        "suggested_actions": [
            f"Review the {len(context.forms)} forms found on the page.",
            f"Check the {len(context.buttons)} available buttons.",
            f"Ask a question about the page content.",
            "Extract key data (manual summary)"
        ],
        "safety_note": f"⚠️ AI analysis is unavailable ({error_message}). Walle is running in Offline Fallback Mode."
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "agent": "Walle", 
        "mode": "read-only-mvp",
        "ai_ready": client is not None,
        "fallback_enabled": OFFLINE_FALLBACK
    }

@app.post("/analyze-page")
async def analyze_page(context: PageContext):
    logger.info(f"ACTION: analyze-page | URL: {context.url} | TITLE: {context.title}")
    
    if not client:
        if OFFLINE_FALLBACK:
            return {"status": "success", "analysis": generate_fallback_analysis(context, "API Key Missing")}
        raise HTTPException(status_code=500, detail="OpenAI client not configured.")
    
    prompt = f"""
    You are Walle, a browser agent. Analyze the following page content and suggest the next best actions.
    
    URL: {context.url}
    Title: {context.title}
    
    Content Summary: {context.text[:2000]}...
    
    Elements found:
    - Forms: {len(context.forms)}
    - Buttons: {len(context.buttons)}
    - Tables: {len(context.tables)}
    - Links: {len(context.links) if context.links else 0}
    
    Return a JSON response with:
    1. 'summary': A brief overview of what this page is.
    2. 'suggested_actions': A list of possible actions the user might want to take.
    3. 'safety_note': Any potential risks identified.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful browser assistant. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        analysis = response.choices[0].message.content
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"ERROR: analyze-page | {str(e)}")
        
        # Check for quota/auth issues
        if "insufficient_quota" in error_msg or "rate_limit" in error_msg or "authentication" in error_msg:
            if OFFLINE_FALLBACK:
                logger.warning("Switching to offline fallback due to API error.")
                return {"status": "success", "analysis": generate_fallback_analysis(context, "API Quota Exceeded")}
        
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {str(e)}")

@app.post("/agent-command")
async def agent_command(cmd: AgentCommand):
    url = cmd.context.get('url') if cmd.context else "unknown"
    logger.info(f"ACTION: agent-command | CMD: {cmd.command} | URL: {url}")
    
    if check_safety(cmd.command):
        return {
            "status": "confirmation_required",
            "message": f"The action '{cmd.command}' requires your approval. Do you want to proceed?",
            "action_id": "pending_action_123"
        }
    
    return {
        "status": "success",
        "message": f"I've processed your request: '{cmd.command}'. In this MVP, I can only provide information, not perform actions.",
        "result": "Read-only response."
    }

@app.post("/confirm-action")
async def confirm_action(confirmation: ActionConfirmation):
    if confirmation.confirmed:
        logger.info(f"ACTION: confirm-action | ID: {confirmation.action_id} | STATUS: BLOCKED (MVP)")
        return {
            "status": "blocked",
            "message": "Action execution is not enabled in the read-only MVP."
        }
    else:
        logger.info(f"ACTION: confirm-action | ID: {confirmation.action_id} | STATUS: CANCELLED")
        return {"status": "cancelled", "message": "Action aborted by user."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8787)
