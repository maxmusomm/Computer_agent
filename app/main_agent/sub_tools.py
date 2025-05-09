"""
Gmail API tools for the Email Agent.
"""

import os
import base64
from email.mime.text import MIMEText
import datetime
import email.parser
from email.utils import parsedate_to_datetime
import re
from typing import List, Dict, Any, Optional

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

def get_emails(
    max_results: int = 10, 
    sender: str = "", 
    date_filter: str = "", 
    subject_filter: str = "",
    is_unread: bool = False
) -> dict:
    """Get emails from Gmail with optional filtering.
    
    Args:
        max_results (int): Maximum number of emails to return (default 10)
        sender (str): Filter emails from a specific sender email address
        date_filter (str): Filter by date (today, yesterday, week, month)
        subject_filter (str): Filter by text in the subject line
        is_unread (bool): Filter by unread emails only
        
    Returns:
        dict: Status and list of filtered emails
    """
    try:
        # Get credentials and build service
        creds = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        # Build the query string for Gmail API
        query_parts = []
        
        if sender:
            query_parts.append(f"from:{sender}")
        
        if date_filter:
            today = datetime.datetime.now().date()
            if date_filter.lower() == "today":
                date_str = today.strftime("%Y/%m/%d")
                query_parts.append(f"after:{date_str}")
            elif date_filter.lower() == "yesterday":
                yesterday = today - datetime.timedelta(days=1)
                date_str = yesterday.strftime("%Y/%m/%d")
                query_parts.append(f"after:{date_str} before:{today.strftime('%Y/%m/%d')}")
            elif date_filter.lower() == "week":
                week_ago = today - datetime.timedelta(days=7)
                date_str = week_ago.strftime("%Y/%m/%d")
                query_parts.append(f"after:{date_str}")
            elif date_filter.lower() == "month":
                month_ago = today - datetime.timedelta(days=30)
                date_str = month_ago.strftime("%Y/%m/%d")
                query_parts.append(f"after:{date_str}")
        
        if subject_filter:
            query_parts.append(f"subject:{subject_filter}")
        
        if is_unread:
            query_parts.append("is:unread")
        
        query = " ".join(query_parts) if query_parts else ""
        
        # Fetch messages that match the query
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        emails = []
        for message in messages:
            # Get the full message details
            msg = service.users().messages().get(userId="me", id=message["id"], format="full").execute()
            
            # Parse headers to get subject, from, and date
            headers = msg["payload"]["headers"]
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject")
            sender_email = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown")
            date_str = next((h["value"] for h in headers if h["name"].lower() == "date"), "")
            
            # Check if the message has a body
            body = ""
            if "parts" in msg["payload"]:
                for part in msg["payload"]["parts"]:
                    if part["mimeType"] == "text/plain":
                        if "data" in part["body"]:
                            body_bytes = base64.urlsafe_b64decode(part["body"]["data"])
                            body = body_bytes.decode("utf-8")
                            break
            elif "body" in msg["payload"] and "data" in msg["payload"]["body"]:
                body_bytes = base64.urlsafe_b64decode(msg["payload"]["body"]["data"])
                body = body_bytes.decode("utf-8")
            
            # Extract a snippet if no body is found
            if not body:
                body = msg.get("snippet", "")
            
            # Add to our email list
            emails.append({
                "id": message["id"],
                "threadId": msg["threadId"],
                "subject": subject,
                "from": sender_email,
                "date": date_str,
                "body_preview": body[:150] + "..." if len(body) > 150 else body,
                "has_attachments": any("filename" in part for part in msg["payload"].get("parts", []))
            })
        
        return {
            "status": "success",
            "message": f"Retrieved {len(emails)} emails",
            "emails": emails
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

def get_email_by_id(email_id: str) -> dict:
    """Get a specific email by its ID.
    
    Args:
        email_id (str): The Gmail message ID
        
    Returns:
        dict: The full email content
    """
    try:
        # Get credentials and build service
        creds = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        # Fetch the specific message
        msg = service.users().messages().get(userId="me", id=email_id, format="full").execute()
        
        # Parse headers
        headers = msg["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown")
        to = next((h["value"] for h in headers if h["name"].lower() == "to"), "Unknown")
        date_str = next((h["value"] for h in headers if h["name"].lower() == "date"), "")
        
        # Extract body
        body = extract_email_body(msg)
        
        # Extract attachment info
        attachments = []
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if "filename" in part and part["filename"]:
                    attachments.append({
                        "id": part["body"].get("attachmentId", ""),
                        "filename": part["filename"],
                        "mimeType": part["mimeType"],
                        "size": part["body"].get("size", 0)
                    })
        
        return {
            "status": "success",
            "message": "Email retrieved successfully",
            "email": {
                "id": email_id,
                "threadId": msg["threadId"],
                "subject": subject,
                "from": sender,
                "to": to,
                "date": date_str,
                "body": body,
                "attachments": attachments,
                "labels": msg["labelIds"]
            }
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

def extract_email_body(message):
    """Extract the plain text body from a Gmail message."""
    if not message["payload"]:
        return ""
    
    def get_body_from_part(part):
        """Recursive function to extract body from message parts."""
        if part.get("mimeType") == "text/plain":
            if "data" in part.get("body", {}):
                body_bytes = base64.urlsafe_b64decode(part["body"]["data"])
                return body_bytes.decode("utf-8")
        
        # Check for multipart
        if part.get("mimeType", "").startswith("multipart/"):
            for subpart in part.get("parts", []):
                body = get_body_from_part(subpart)
                if body:
                    return body
        
        return ""
    
    # Try to get body from payload directly
    if "body" in message["payload"] and "data" in message["payload"]["body"]:
        body_bytes = base64.urlsafe_b64decode(message["payload"]["body"]["data"])
        return body_bytes.decode("utf-8")
    
    # Try to get body from parts
    if "parts" in message["payload"]:
        for part in message["payload"]["parts"]:
            body = get_body_from_part(part)
            if body:
                return body
    
    # Fallback to snippet
    return message.get("snippet", "")

def mark_email_as_read(email_id: str) -> dict:
    """Mark an email as read.
    
    Args:
        email_id (str): The Gmail message ID
        
    Returns:
        dict: Status of the operation
    """
    try:
        # Get credentials and build service
        creds = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        # Remove UNREAD label
        service.users().messages().modify(
            userId="me",
            id=email_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        
        return {
            "status": "success",
            "message": "Email marked as read"
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

def count_unread_emails() -> dict:
    """Count the number of unread emails.
    
    Returns:
        dict: Count of unread emails
    """
    try:
        # Get credentials and build service
        creds = get_gmail_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        # Get unread messages
        results = service.users().messages().list(
            userId="me", 
            q="is:unread",
            maxResults=1
        ).execute()
        
        total = results.get("resultSizeEstimate", 0)
        
        return {
            "status": "success",
            "message": f"You have {total} unread emails",
            "count": total
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