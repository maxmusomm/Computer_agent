import asyncio
import email
import logging
from typing import Dict, List, Any, Optional

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.tools import FunctionTool
from google.genai import types
from google.adk.tools import google_search

from . import sub_tools, prompts


# Create function tools for email operations
send_email_tool = FunctionTool(func=sub_tools.send_email)
list_labels_tool = FunctionTool(func=sub_tools.list_email_labels)
get_emails_tool = FunctionTool(func=sub_tools.get_emails)
get_email_by_id_tool = FunctionTool(func=sub_tools.get_email_by_id)
mark_email_as_read_tool = FunctionTool(func=sub_tools.mark_email_as_read)
count_unread_emails_tool = FunctionTool(func=sub_tools.count_unread_emails)

search_agent = LlmAgent(
    model="gemini-2.0-flash-exp",  # Specify the LLM
    name="search_agent",
    description="Agent that searches Google to answer queries.",
    instruction="Use Google search to find accurate answers.",
    tools=[google_search],  # Integrate the Google search tool
)

email_assistant_agent = LlmAgent(
            name="email_assistant_agent",
            model="gemini-2.0-flash-exp",
            tools=[
                send_email_tool, 
                list_labels_tool,
                get_emails_tool,
                get_email_by_id_tool,
                mark_email_as_read_tool,
                count_unread_emails_tool
            ],
            instruction=prompts.email_assistant_agent_instruction,
            description="An assistant that can send and receive emails via Gmail API."
        )