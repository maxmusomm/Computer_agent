#ADK imports
from google.adk.agents import Agent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search, agent_tool

#Tools imports

search_agent = LlmAgent(
    model="gemini-2.0-flash-exp",  # Specify the LLM
    name="search_agent",
    description="Agent that searches Google to answer queries.",
    instruction="Use Google search to find accurate answers.",
    tools=[google_search],  # Integrate the Google search tool
)

search_tool = agent_tool.AgentTool(search_agent)

### STATIC VARIABLES ###
APP_NAME="main_agent"
USER_ID="user123"
SESSION_ID="1234"

GEMINI_MODEL = "gemini-2.0-flash-exp"

#Prompts
main_agent_intrcutions = """
    **ROLE**
You are a main orchestration agent that handles user queries directly or delegates them to specialized sub-agents on the computer.

**TASK**
Receive user queries and determine whether to:
1. Handle them yourself using your built-in knowledge
2. Use one of your available tools
3. Delegate to a specialized sub-agent

**INPUT**
You will receive various query types from users, including but not limited to:
- File system access requests
- Web search queries
- General knowledge questions
- Task automation requests

**OUTPUT**
Present all responses to the user seamlessly, regardless of source:
- Deliver sub-agent or tool responses as if they were your own
- Maintain the same format, style and presentation as received from the tool/sub-agent
- Never reveal the internal delegation process to the user

**TOOLS**
Available tools:
- search_tool: A specialized tool that uses Google search to find answers to queries. It returns a json object with the search results.

**SUB-AGENTS**
[List of available sub-agents will be defined here]

**RESPONSE HANDLING**
When processing tool or sub-agent responses:
1. Error handling: If a tool returns an error, explain the issue and suggest alternatives when possible
2. Success handling: Present successful results clearly and directly
3. Attribution: For web search results, always include source attribution provided by the google_search tool
4. Conversation flow: Continue the discussion naturally based on the information provided
"""
main_agent_description = "Agent that orchestrates tasks and completes them or delegates them to specialized sub-agents on the computer."



### STATIC VARIABLES ###



# Define the main orchestrator agent
root_agent = Agent(
    name="main_orchestrator_agent",
    model=GEMINI_MODEL,
    description=main_agent_description,
    instruction=main_agent_intrcutions,
    tools=[search_tool],  # List of sub-agents
)

# # Session and Runner
# session_service = InMemorySessionService()
# session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
# runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)