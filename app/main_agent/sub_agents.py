import asyncio
import email
import logging
from typing import Dict, List, Any, Optional

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.tools import FunctionTool
from google.genai import types
from google.adk.tools import google_search

from . import sub_tools, prompts


# Create search agent
search_agent = LlmAgent(
    model="gemini-2.0-flash-exp",  # Specify the LLM
    name="search_agent",
    description="Agent that searches Google to answer queries.",
    instruction="Use Google search to find accurate answers.",
    tools=[google_search],  # Integrate the Google search tool
)

# Create function tools for email operations
send_email_tool = FunctionTool(func=sub_tools.send_email)
list_labels_tool = FunctionTool(func=sub_tools.list_email_labels)
get_emails_tool = FunctionTool(func=sub_tools.get_emails)
get_email_by_id_tool = FunctionTool(func=sub_tools.get_email_by_id)
mark_email_as_read_tool = FunctionTool(func=sub_tools.mark_email_as_read)
count_unread_emails_tool = FunctionTool(func=sub_tools.count_unread_emails)

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

# Create function tools for Google Sheets operations
create_spreadsheet_tool = FunctionTool(func=sub_tools.create_new_spreadsheet)
add_sheet_tool = FunctionTool(func=sub_tools.add_sheet_to_spreadsheet)
get_sheet_values_tool = FunctionTool(func=sub_tools.get_sheet_values)
update_sheet_values_tool = FunctionTool(func=sub_tools.update_sheet_values)
delete_sheet_tool = FunctionTool(func=sub_tools.delete_sheet_from_spreadsheet)
search_drive_files_tool = FunctionTool(func=sub_tools.search_drive_files_by_name)

spreadsheet_assistant_agent = LlmAgent(
    name="spreadsheet_assistant_agent",
    model="gemini-2.0-flash-exp", # You can use the same model or a different one
    tools=[
        create_spreadsheet_tool,
        add_sheet_tool,
        get_sheet_values_tool,
        update_sheet_values_tool,
        delete_sheet_tool,
        search_drive_files_tool
    ],
    instruction=prompts.spreadsheet_assistant_agent_instruction, # We will define this in prompts.py
    description="An assistant that can create, read, update, and delete Google Spreadsheets and their sheets, and search for spreadsheets by name."
)