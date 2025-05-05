"""
Email Token Generator - Creates a dedicated token with Gmail API send permissions.
Run this script to ensure you have the proper permissions for sending emails.
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes we need
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def generate_email_token():
    """Generate a dedicated token for Gmail email sending."""
    creds = None
    email_token_path = 'email_token.json'
    
    # Delete existing email_token.json if it exists
    if os.path.exists(email_token_path):
        print(f"Removing existing token at {email_token_path}")
        os.remove(email_token_path)
    
    print("\n===== Email Token Generator =====")
    print("This will create a dedicated token for Gmail API with email sending permissions")
    
    # Get client secrets file
    client_secret_file = 'credentials.json'
    if not os.path.exists(client_secret_file):
        alt_path = os.path.join('static', 
                       'client_secret_214218856359-o80naasos3rvtg4mrh7nsbv4hbcqah70.apps.googleusercontent.com.json')
        if os.path.exists(alt_path):
            client_secret_file = alt_path
            print(f"Using client secret file from: {alt_path}")
        else:
            print("❌ ERROR: No credentials.json or client secret file found.")
            return False
    
    try:
        # Start the authentication flow
        print(f"\nStarting authentication with scopes:")
        for scope in SCOPES:
            print(f"  - {scope}")
        
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save the credentials to email_token.json
        with open(email_token_path, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\n✅ Success! Credentials saved to {email_token_path}")
        
        # Verify the scopes
        if 'https://www.googleapis.com/auth/gmail.send' in creds.scopes:
            print("✅ Email sending permission confirmed")
        else:
            print("❌ Warning: Email sending permission not found in token!")
            print(f"Token scopes: {creds.scopes}")
            return False
        
        # Test the token by getting the user's email address
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'unknown')
        print(f"\nAuthenticated as: {email}")
        
        # List some labels to verify read access
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        if labels:
            print("Sample labels:", ', '.join([label['name'] for label in labels[:3]]))
        
        print("\nToken is ready for use with the email agent!")
        return True
        
    except HttpError as error:
        print(f"❌ HTTP Error: {error}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    generate_email_token()