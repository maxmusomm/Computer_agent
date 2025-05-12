from google.adk.tools import agent_tool
from google.adk.tools import FunctionTool
from . import sub_agents, sub_tools

# Create agent tools
search_tool = agent_tool.AgentTool(sub_agents.search_agent)

# Create function tools for Google Docs operations
create_document_tool = FunctionTool(func=sub_tools.create_document)
delete_document_tool = FunctionTool(func=sub_tools.delete_document)
edit_document_tool = FunctionTool(func=sub_tools.edit_document)

