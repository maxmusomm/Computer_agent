import os
from dotenv import load_dotenv
load_dotenv()

#ADK imports
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session

#Tools imports
#Prompts imports
from . import prompts, tools, sub_agents

### STATIC VARIABLES ###

APP_NAME="main_orchestrator_agent"
USER_ID="user123"
SESSION_ID="1234"

GEMINI_MODEL = "gemini-2.0-flash-exp"
GEMINI_PRO_MODEL = "gemini-2.5-pro-exp-03-25"



### STATIC VARIABLES ###

###AGENTS###

# Define the main orchestrator agent
root_agent = Agent(
    name="main_orchestrator_agent",
    model=GEMINI_MODEL,
    description=prompts.main_agent_description,
    instruction=prompts.main_agent_intrcutions,
    tools=[
        tools.search_tool,
        tools.create_document_tool,
        tools.delete_document_tool,
        tools.edit_document_tool,
        
    ],
    sub_agents=[sub_agents.email_assistant_agent, sub_agents.spreadsheet_assistant_agent],  # List of sub-agents
)

# Session and Runner
session_service = InMemorySessionService()
session: Session= session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
