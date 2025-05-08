"""
Gmail API tools for the Email Agent.
"""

import os
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API authentication scopes - updated to match token.json
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def get_gmail_credentials():
    """Get and refresh Gmail API credentials"""
    creds = None
    # Define project root for finding files
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    token_path = os.path.join(project_root, 'token.json')
    
    # Check if token.json exists with stored credentials
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            print(f"Found token at {token_path}")
        except Exception as e:
            print(f"Error loading token: {e}")
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("Token refreshed successfully")
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None
        
        # If still no valid credentials, look for credentials.json
        if not creds:
            # Try multiple locations for credentials file
            potential_paths = [
                os.path.join(project_root, 'credentials.json'),
                os.path.join(project_root, 'static', 'credentials.json')
            ]
            
            client_secret_file = None
            for path in potential_paths:
                if os.path.exists(path):
                    client_secret_file = path
                    print(f"Using credentials from: {path}")
                    break
            
            if not client_secret_file:
                raise FileNotFoundError("No credentials.json file found in any of the expected locations.")
            
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future runs
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            print(f"Credentials saved to {token_path}")
    
    return creds

# Modified function signature to work better with ADK's automatic function calling
def send_email(to: str, subject: str, body: str) -> dict:
    """Sends an email using Gmail API.
    
    Args:
        to (string): Email address of the recipient
        subject (string): Subject of the email
        body (string): Body content of the email
        
    Returns:
        dict: Status of the email sending operation
    """
    try:
        # Get credentials and build service
        creds = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        # Create email message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Create the message payload
        create_message = {
            'raw': encoded_message
        }
        
        # Send the message
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        
        return {
            "status": "success",
            "message": f"Email sent successfully to {to}",
            "message_id": send_message['id']
        }
        
    except HttpError as error:
        return {
            "status": "error",
            "message": f"An error occurred: {error}"
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"An unexpected error occurred: {str(e)}"
        }
        
def list_email_labels() -> dict:
    """Lists the user's Gmail labels.
    
    Returns:
        dict: List of Gmail labels
    """
    try:
        # Get credentials and build service
        creds = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        # Call the Gmail API
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        
        label_names = [label["name"] for label in labels]
        
        return {
            "status": "success",
            "message": "Labels retrieved successfully",
            "labels": label_names
        }
        
    except HttpError as error:
        return {
            "status": "error",
            "message": f"An error occurred: {error}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }
        
print(send_email("examplespambusines@gmail.com", "X ceo", "Just wanted to let you know that the current CEO of X Corp. is Linda Yaccarino. She took the position in June 2023."))