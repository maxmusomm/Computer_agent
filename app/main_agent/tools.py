from google.adk.tools import agent_tool
from . import sub_agents

search_tool = agent_tool.AgentTool(sub_agents.search_agent)