"""
Setup script for Gmail API authorization.
This script authorizes the application with user consent
and saves the token for future use.
"""

import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import argparse

# Gmail API scopes needed for the email agent
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.readonly'  # For reading emails
]

def setup_gmail_auth(credentials_file='credentials.json'):
    """
    Set up Gmail API authorization and save token.
    
    Args:
        credentials_file: Path to the credentials.json file from Google Cloud Console
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        print("Found existing token.json file.")
        try:
            creds = Credentials.from_authorized_user_info(
                json.loads(open('token.json').read()), SCOPES)
            
            # Check if token is valid
            if creds.valid:
                print("Token is valid! Authorization complete.")
                return
            
            # Try to refresh if expired
            if creds.expired and creds.refresh_token:
                print("Token expired. Attempting to refresh...")
                creds.refresh(Request())
                # Save refreshed token
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print("Token refreshed successfully!")
                return
            else:
                print("Token expired and can't be refreshed. Creating new token...")
        except Exception as e:
            print(f"Error reading token: {e}")
            print("Creating new token...")
    
    # No valid credentials available, let the user log in
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            f"No {credentials_file} file found. Please download it from the Google Cloud Console.")
    
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    print("Starting local authorization server...")
    creds = flow.run_local_server(port=0)
    
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    print("Authorization successful! Token saved to 'token.json'")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set up Gmail API authorization.')
    parser.add_argument('--credentials', '-c', default='credentials.json',
                        help='Path to the credentials.json file (default: credentials.json)')
    args = parser.parse_args()
    
    setup_gmail_auth(args.credentials)