import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WalleAgent")

app = FastAPI(title="Walle Browser Agent")

# Enable CORS for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the extension ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI Client setup
openai.api_key = os.getenv("OPENAI_API_KEY")

class PageContext(BaseModel):
    url: str
    title: str
    text: str
    forms: List[dict]
    buttons: List[dict]
    tables: List[dict]

class AgentCommand(BaseModel):
    command: str
    context: Optional[dict] = None

class ActionConfirmation(BaseModel):
    action_id: str
    confirmed: bool

# Safety Layer Keywords
DANGEROUS_KEYWORDS = ["approve", "submit", "delete", "cancel", "send", "save", "post", "payment", "buy", "purchase"]

def check_safety(proposed_action: str) -> bool:
    """Returns True if confirmation is required."""
    proposed_action_lower = proposed_action.lower()
    return any(keyword in proposed_action_lower for keyword in DANGEROUS_KEYWORDS)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "Walle"}

@app.post("/analyze-page")
async def analyze_page(context: PageContext):
    logger.info(f"Analyzing page: {context.url} - {context.title}")
    
    prompt = f"""
    You are Walle, a browser agent. Analyze the following page content and suggest the next best actions.
    
    URL: {context.url}
    Title: {context.title}
    
    Content Summary: {context.text[:2000]}...
    
    Elements found:
    - Forms: {len(context.forms)}
    - Buttons: {len(context.buttons)}
    - Tables: {len(context.tables)}
    
    Return a JSON response with:
    1. 'summary': A brief overview of what this page is.
    2. 'suggested_actions': A list of possible actions the user might want to take.
    3. 'safety_note': Any potential risks identified.
    """
    
    try:
        # Note: Using modern OpenAI API structure if available, or fallback
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini", # or gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful browser assistant. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        analysis = response.choices[0].message.content
        logger.info(f"Analysis complete for {context.url}")
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        logger.error(f"Error calling OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent-command")
async def agent_command(cmd: AgentCommand):
    logger.info(f"Received command: {cmd.command}")
    
    # Check if the command involves dangerous actions
    if check_safety(cmd.command):
        return {
            "status": "confirmation_required",
            "message": f"The action '{cmd.command}' requires your approval. Do you want to proceed?",
            "action_id": "pending_action_123" # In a real app, generate a unique ID
        }
    
    # Simulate execution or call LLM for execution plan
    return {
        "status": "success",
        "message": f"Executing: {cmd.command}",
        "result": "Action simulated successfully."
    }

@app.post("/confirm-action")
async def confirm_action(confirmation: ActionConfirmation):
    if confirmation.confirmed:
        logger.info(f"Action {confirmation.action_id} confirmed by user.")
        return {"status": "success", "message": "Action executed."}
    else:
        logger.info(f"Action {confirmation.action_id} cancelled by user.")
        return {"status": "cancelled", "message": "Action aborted."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8787)
