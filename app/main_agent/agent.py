import os
from dotenv import load_dotenv
load_dotenv()

#ADK imports
from google.adk.agents import Agent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

#Tools imports
#Prompts imports
from . import prompts, tools

### STATIC VARIABLES ###

APP_NAME="main_agent"
USER_ID="user123"
SESSION_ID="1234"

GEMINI_MODEL = "gemini-2.0-flash-exp"

### STATIC VARIABLES ###

###AGENTS###

# Define the main orchestrator agent
root_agent = Agent(
    name="main_orchestrator_agent",
    model=GEMINI_MODEL,
    description=prompts.main_agent_description,
    instruction=prompts.main_agent_intrcutions,
    tools=[tools.search_tool, tools.email_tool]  # Include both traditional and OpenAPI tools
)

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)