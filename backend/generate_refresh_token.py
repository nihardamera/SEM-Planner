#!/usr/bin/env python3
"""
Script to generate a refresh token for Google Ads API.
Run this script to get the refresh token needed for google-ads.yaml

Usage:
    python generate_refresh_token.py
"""

import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

# OAuth2 scope for Google Ads API
SCOPES = ['https://www.googleapis.com/auth/adwords']

def generate_refresh_token():
    """Generate a refresh token for Google Ads API."""
    
    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Error: GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET must be set in .env file")
        return
    
    # Create the OAuth2 flow
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"]
            }
        },
        SCOPES
    )
    
    # Run the OAuth2 flow
    print("Opening browser for authentication...")
    print("Please complete the authentication process in your browser.")
    
    credentials = flow.run_local_server(port=0)
    
    print(f"\n✅ Success! Your refresh token is:")
    print(f"refresh_token: \"{credentials.refresh_token}\"")
    print(f"\n📝 Please update your google-ads.yaml file with this refresh token.")
    print(f"Replace 'PLACEHOLDER_REFRESH_TOKEN' with the token above.")
    
    return credentials.refresh_token

if __name__ == "__main__":
    try:
        generate_refresh_token()
    except Exception as e:
        print(f"❌ Error generating refresh token: {e}")
        print("\nMake sure you have:")
        print("1. Valid GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET in .env")
        print("2. Internet connection")
        print("3. Access to the Google account associated with your Google Ads account")
