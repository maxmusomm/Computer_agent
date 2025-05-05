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

# Gmail API authentication scopes - we need .send permission to send emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_credentials():
    """Get and refresh Gmail API credentials"""
    creds = None
    # Check if token.json exists with stored credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Look for credentials.json in current directory
            # If not found, check in the static directory for client_secret file
            client_secret_file = 'credentials.json'
            if not os.path.exists(client_secret_file):
                # Try alternate location for client secret file
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
                alt_path = os.path.join(project_root, 'static', 'client_secret_214218856359-o80naasos3rvtg4mrh7nsbv4hbcqah70.apps.googleusercontent.com.json')
                if os.path.exists(alt_path):
                    client_secret_file = alt_path
                    print(f"Using client secret file from: {alt_path}")
                else:
                    raise FileNotFoundError("No credentials.json or client secret file found.")
            
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

# Modified function signature to work better with ADK's automatic function calling
def send_email(to: str, subject: str, body: str) -> dict:
    """Sends an email using Gmail API.
    
    Args:
        to: Email address of the recipient
        subject: Subject of the email
        body: Body content of the email
        
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