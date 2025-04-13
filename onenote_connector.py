# onenote_connector.py

import requests
import json
import re
from bs4 import BeautifulSoup

class OneNoteConnector:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.base_url = "https://graph.microsoft.com/v1.0/me/onenote"
        self.notebooks = []
        self.all_content = []
    
    def _make_request(self, endpoint):
        """Make authenticated request to Microsoft Graph API"""
        token = self.auth_manager.get_token()
        if not token:
            raise Exception("Authentication token not available")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
    
    def get_notebooks(self):
        """Get all notebooks"""
        data = self._make_request("/notebooks")
        self.notebooks = data.get("value", [])
        return self.notebooks
    
    def get_sections(self, notebook_id):
        """Get sections within a notebook"""
        data = self._make_request(f"/notebooks/{notebook_id}/sections")
        return data.get("value", [])
    
    def get_pages(self, section_id):
        """Get pages within a section"""
        data = self._make_request(f"/sections/{section_id}/pages")
        return data.get("value", [])
    
    def get_page_content(self, page_id):
        """Get content of a page"""
        token = self.auth_manager.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{self.base_url}/pages/{page_id}/content",
            headers=headers
        )
        
        if response.status_code == 200:
            # Parse HTML content to extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text(separator="\n", strip=True)
            return text_content
        else:
            raise Exception(f"Failed to get page content: {response.status_code} - {response.text}")
    
    def fetch_all_content(self):
        """Fetch content from all notebooks, sections, and pages"""
        all_content = []
        
        # Get all notebooks
        notebooks = self.get_notebooks()
        
        for notebook in notebooks:
            notebook_name = notebook.get("displayName", "Unnamed Notebook")
            notebook_id = notebook.get("id")
            
            # Get sections in the notebook
            sections = self.get_sections(notebook_id)
            
            for section in sections:
                section_name = section.get("displayName", "Unnamed Section")
                section_id = section.get("id")
                
                # Get pages in the section
                pages = self.get_pages(section_id)
                
                for page in pages:
                    page_name = page.get("title", "Unnamed Page")
                    page_id = page.get("id")
                    
                    try:
                        # Get page content
                        page_content = self.get_page_content(page_id)
                        
                        # Create document with metadata
                        document = {
                            "notebook": notebook_name,
                            "section": section_name,
                            "page": page_name,
                            "content": page_content,
                            "source": f"Notebook: {notebook_name}, Section: {section_name}, Page: {page_name}"
                        }
                        
                        all_content.append(document)
                        print(f"Fetched: {notebook_name} > {section_name} > {page_name}")
                    except Exception as e:
                        print(f"Error fetching page {page_name}: {str(e)}")
        
        self.all_content = all_content
        return all_content