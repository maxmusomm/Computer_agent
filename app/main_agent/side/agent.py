from google.adk.agents import LlmAgent
from google.adk.tools import google_search

search_agent = LlmAgent(
    model="gemini-2.0-flash-exp",  # Specify the LLM
    name="search_agent",
    description="Agent that searches Google to answer queries.",
    instruction="Use Google search to find accurate answers.",
    tools=[google_search],  # Integrate the Google search tool
)