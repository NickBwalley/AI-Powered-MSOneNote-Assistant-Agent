# ms_auth.py

import os
import msal
from dotenv import load_dotenv

load_dotenv()

class MSAuth:
    def __init__(self):
        self.client_id = os.getenv("MS_CLIENT_ID")
        self.tenant_id = os.getenv("MS_TENANT_ID")
        self.client_secret = os.getenv("MS_CLIENT_SECRET")
        self.redirect_uri = os.getenv("MS_REDIRECT_URI")
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["Notes.Read"]
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret
        )
        self.token = None
    
    def get_auth_url(self):
        """Generate authorization URL for user consent"""
        return self.app.get_authorization_request_url(
            self.scope,
            redirect_uri=self.redirect_uri
        )
    
    def get_token_from_code(self, auth_code):
        """Exchange authorization code for access token"""
        result = self.app.acquire_token_by_authorization_code(
            auth_code,
            scopes=self.scope,
            redirect_uri=self.redirect_uri
        )
        if "access_token" in result:
            self.token = result["access_token"]
            return self.token
        else:
            raise Exception(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
    
    def get_token(self):
        """Get existing token or acquire a new one"""
        return self.token