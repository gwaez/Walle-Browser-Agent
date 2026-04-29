import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from llm_provider import LLMProvider

# Load environment variables
load_dotenv()

LOG_FULL_CONTENT = os.getenv("LOG_FULL_CONTENT", "false").lower() == "true"

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

# Initialize LLM Provider
llm = LLMProvider()

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


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "agent": "Walle", 
        "mode": "read-only-mvp",
        "provider": llm.provider_name
    }

@app.post("/analyze-page")
async def analyze_page(context: PageContext):
    logger.info(f"ACTION: analyze-page | URL: {context.url} | PROVIDER: {llm.provider_name}")
    
    try:
        analysis = llm.analyze(context.dict())
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        logger.error(f"ERROR: analyze-page | {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM Provider Error: {str(e)}")

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
