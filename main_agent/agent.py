from google.adk.agents import Agent
from google.adk.tools import google_search 
import agent_tools.excel_agent_tools as excel_tools 
import Constants

# Define the Excel agent with the updated tool functions
excel_handler_agent = Agent(
    name="excel_handler_agent",
    model=Constants.GEMINI_MODEL,
    description=(
        "Agent that handles Excel document operations on the computer. It is able to create, read, update, and analyze Excel files anywhere on the computer."
    ),
    instruction=(
        "You are an Excel document handling agent. Your responsibilities include:"
        "1. Creating new Excel files with specified data and formatting"
        "2. Reading and extracting data from existing Excel files"
        "3. Updating and modifying existing Excel documents"
        "4. Performing data analysis on Excel data including sorting, filtering, and basic statistics"
        "5. Creating charts and visualizations from Excel data"
        "6. Handling multiple worksheets within a workbook"
        "7. Converting between Excel and other formats (CSV, PDF, etc.)"
        "8. Implementing formulas and functions in Excel sheets"
        "When given a task related to Excel operations, analyze the request, determine the "
        "appropriate Excel operations needed, and use the available tools to accomplish the task. Always confirm the success "
        "of operations and provide clear descriptions of what was done."
        "The tools you can use include creating Excel files, reading data from Excel files, updating existing files, "
        "analyzing data, creating charts, managing worksheets, converting between formats, and applying formulas."
    ),
    tools=[
        excel_tools.create_excel_file
    ]
)

# Define the main orchestrator agent
root_agent = Agent(
    name="main_orchestrator_agent",
    model=Constants.GEMINI_MODEL,
    description=(
        "Agent that orchestrates tasks and delegates them to specialized sub-agents on the computer."
        
    ),
    
    instruction=(
        "You have been assigned the role of an orchestrator agent. Your job is to receive tasks from users and delegate them to specialized sub-agents on the computer. The tasks may include file management, web browsing, and other specialized tasks. You will need to determine which sub-agent is best suited for each task and communicate with them accordingly. "
        "You will also need to handle any errors or exceptions that may arise during the task delegation process. Once the task is completed, you will need to communicate the results back to the user. "
        "You are expected to be proactive in identifying tasks that can be delegated to sub-agents and to communicate effectively with them."
        f"This is the system's main path {Constants.SYSTEM_PATH} . Use it to create paths that specify the locations the user talks about on the computer. "
        "The sub-agents you can delegate tasks to include: excel_handler_agent (for Excel-related tasks. ) "
        "You have access to the following tools: google_search (for web browsing and information retrieval). "
    ),
    tools=[google_search],
    sub_agents=[excel_handler_agent]
)