from google.adk.tools import  agent_tool

from . import sub_agents

# Create the search agent


# Create the email agent instance
email_agent = sub_agents.EmailAgent(model="gemini-2.0-flash").agent

# Create a function tool that uses our context-aware email handler
search_tool = agent_tool.AgentTool(sub_agents.search_agent)
email_tool = agent_tool.AgentTool(agent=email_agent)