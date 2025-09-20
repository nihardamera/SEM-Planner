#!/usr/bin/env python3
"""
Simplified script to generate Google Ads API refresh token.
This uses a more direct approach that should work better.
"""

import os
import webbrowser
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import requests

load_dotenv()

def generate_refresh_token():
    """Generate refresh token using manual OAuth flow."""

    # Use credentials from google-ads.yaml (updated credentials)
    client_id = "1008665885039-akmm0gk3qu6mcrbsvhfsobpeh5gl60hr.apps.googleusercontent.com"
    client_secret = "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"
    
    if not client_id or not client_secret:
        print("❌ Error: GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET must be set in .env file")
        return
    
    # Step 1: Generate authorization URL
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={client_id}&"
        "redirect_uri=urn:ietf:wg:oauth:2.0:oob&"
        "scope=https://www.googleapis.com/auth/adwords&"
        "response_type=code&"
        "access_type=offline&"
        "approval_prompt=force"
    )
    
    print("🔐 Google Ads API Refresh Token Generator")
    print("=" * 50)
    print("\n📋 STEP 1: Get Authorization Code")
    print("1. Click the link below (or copy-paste into browser):")
    print(f"\n🔗 {auth_url}\n")
    
    # Try to open browser automatically
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened automatically")
    except:
        print("⚠️  Please manually open the link above")
    
    print("\n📝 STEP 2: Complete Authentication")
    print("1. Sign in with your Google account")
    print("2. Grant permissions for Google Ads API access")
    print("3. Copy the authorization code from the page")
    
    # Get authorization code from user
    auth_code = input("\n🔑 Enter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return
    
    print("\n🔄 STEP 3: Exchanging code for refresh token...")
    
    # Step 2: Exchange authorization code for refresh token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        
        token_info = response.json()
        
        if "refresh_token" in token_info:
            refresh_token = token_info["refresh_token"]
            
            print("\n🎉 SUCCESS! Your refresh token:")
            print("=" * 50)
            print(f'refresh_token: "{refresh_token}"')
            print("=" * 50)
            
            print(f"\n📝 Next steps:")
            print(f"1. Copy the refresh token above")
            print(f"2. Edit ~/google-ads.yaml")
            print(f"3. Replace 'PLACEHOLDER_REFRESH_TOKEN' with your token")
            print(f"4. Save the file and restart your backend")
            
            return refresh_token
        else:
            print("❌ Error: No refresh token in response")
            print(f"Response: {token_info}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error exchanging code for token: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    generate_refresh_token()
