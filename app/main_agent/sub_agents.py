"""
Email Agent Module - An agent for handling email operations with Gmail API.
"""

import asyncio
import logging
from typing import Dict, Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, google_search
from google.genai import types

from . import sub_tools

# Set up logging
logger = logging.getLogger(__name__)

search_agent = LlmAgent(
    model="gemini-2.0-flash-exp",  # Specify the LLM
    name="search_agent",
    description="Agent that searches Google to answer queries.",
    instruction="Use Google search to find accurate answers.",
    tools=[google_search],  # Integrate the Google search tool
)

class EmailAgent:
    """
    Email Agent class to handle email operations through Gmail API.
    """
    
    def __init__(self, model: str = "gemini-2.0-flash"):
        """
        Initialize the Email Agent.
        
        Args:
            model (str): The LLM model to use
        """
        self.model = model
        self.name = "email_assistant_agent"
        
        # Create tools from our Gmail functions
        self.send_email_tool = FunctionTool(func=sub_tools.send_email)
        self.list_labels_tool = FunctionTool(func=sub_tools.list_email_labels)
        
        # Create the LLM agent with our tools
        self.agent = LlmAgent(
            name=self.name,
            model=self.model,
            tools=[self.send_email_tool, self.list_labels_tool],
            instruction="""You are an Email Assistant that can send emails via Gmail and check email labels.
            
            You have access to these tools:
            1. send_email: Use this to send emails when requested
            2. list_email_labels: Use this to list available Gmail labels (mainly for testing)
            
            When a user asks you to send an email:
            - Ask for recipient, subject, and email body if not provided
            - Confirm the email details before sending
            - Use a professional tone in your responses
            - Report success or errors clearly
            - Only send emails when explicitly asked to do so
            
            For security reasons:
            - Never send emails to multiple recipients at once
            - Refuse to send emails with sensitive content
            - Do not store email content in memory between sessions
            
            When confirming email details before sending, display:
            - To: [recipient]
            - Subject: [subject]
            - Body: 
            [preview of the body]
            
            Then ask for confirmation before sending.
            """,
            description="An assistant that can send emails via Gmail API."
        )
    
    async def process_message(self, 
                             message: str, 
                             user_id: str = "user_1",
                             session_id: str = None) -> Dict[str, Any]:
        """
        Process a message and perform the appropriate email operation.
        
        Args:
            message (str): The user message
            user_id (str): User identifier
            session_id (str): Session identifier
            
        Returns:
            Dict: The response from the agent
        """
        try:
            # Create the message content
            content = types.Content(role='user', parts=[types.Part(text=message)])
            
            # Call events and collect responses
            responses = []
            function_calls = []
            final_response = None
            
            # Process the events from the agent
            async for event in self.agent.run_async(new_message=content):
                # Track function calls
                if event.get_function_calls():
                    call = event.get_function_calls()[0]
                    function_calls.append({
                        "name": call.name,
                        "args": call.args
                    })
                
                # Track function responses
                elif event.get_function_responses():
                    response = event.get_function_responses()[0]
                    responses.append({
                        "name": response.name,
                        "response": response.response
                    })
                
                # Track the final text response
                elif event.is_final_response() and event.content and event.content.parts:
                    final_response = event.content.parts[0].text.strip()
            
            # Return the collected data
            return {
                "final_response": final_response,
                "function_calls": function_calls,
                "function_responses": responses
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "error": str(e),
                "final_response": f"Sorry, there was an error processing your email request: {str(e)}"
            }
    
    async def send_email_async(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Send an email directly without LLM interaction.
        
        Args:
            recipient (str): Email address of the recipient
            subject (str): Subject of the email
            body (str): Body content of the email
            
        Returns:
            Dict: Status of the email sending operation
        """
        return sub_tools.send_email(to=recipient, subject=subject, body=body)
    
    def send_email_sync(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for sending emails.
        
        Args:
            recipient (str): Email address of the recipient
            subject (str): Subject of the email
            body (str): Body content of the email
            
        Returns:
            Dict: Status of the email sending operation
        """
        return asyncio.run(self.send_email_async(recipient=recipient, subject=subject, body=body))
    
    async def list_labels_async(self) -> Dict[str, Any]:
        """
        List Gmail labels asynchronously.
        
        Returns:
            Dict: List of Gmail labels
        """
        return sub_tools.list_email_labels()
    
    def list_labels_sync(self) -> Dict[str, Any]:
        """
        Synchronous wrapper for listing Gmail labels.
        
        Returns:
            Dict: List of Gmail labels
        """
        return asyncio.run(self.list_labels_async())