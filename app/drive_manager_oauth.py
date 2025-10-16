"""
Google Drive Manager with OAuth 2.0 authentication
Supports user authentication instead of service account
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from app.config import Config

logger = logging.getLogger(__name__)

class GoogleDriveManagerOAuth:
    """
    Google Drive Manager using OAuth 2.0 authentication
    """

    def __init__(self):
        """Initialize with OAuth authentication"""
        self.service = None
        self.root_folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
        self.credentials_path = 'credentials.json'
        self.token_path = 'token.json'
        self._authenticate()

    def _authenticate(self):
        """Authenticate using OAuth 2.0 flow"""
        try:
            # Define the required scopes
            scopes = [
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.metadata'
            ]

            creds = None

            # Check if we have existing token
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, scopes)
                logger.info("Loaded existing credentials from token file")

            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired credentials")
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(
                            f"OAuth credentials file not found: {self.credentials_path}\n"
                            "Please download credentials.json from Google Cloud Console"
                        )

                    logger.info("Starting OAuth flow - browser will open for authentication")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, scopes)
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
                logger.info("Saved credentials to token file")

            # Build the Drive API service
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Successfully authenticated with Google Drive using OAuth")

        except Exception as e:
            logger.error(f"Failed to authenticate with Google Drive: {str(e)}")
            raise

    def create_company_folder(self, company_name: str) -> Optional[str]:
        """
        Create a folder for the company if it doesn't exist

        Args:
            company_name: Name of the company

        Returns:
            Folder ID if successful, None otherwise
        """
        try:
            # Check if folder already exists
            existing_folder = self._find_folder(company_name, self.root_folder_id)
            if existing_folder:
                logger.info(f"Company folder already exists: {company_name}")
                return existing_folder

            # Create new folder
            folder_metadata = {
                'name': company_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.root_folder_id]
            }

            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()

            folder_id = folder.get('id')
            logger.info(f"Created company folder: {company_name} (ID: {folder_id})")

            # Create document category subfolders
            self._create_category_subfolders(folder_id)

            return folder_id

        except HttpError as e:
            logger.error(f"Failed to create company folder: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating company folder: {str(e)}")
            return None

    def _create_category_subfolders(self, parent_folder_id: str):
        """
        Create subfolders for each document category

        Args:
            parent_folder_id: ID of the parent company folder
        """
        try:
            for category in Config.DOCUMENT_CATEGORIES.keys():
                folder_metadata = {
                    'name': category,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_folder_id]
                }

                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()

                logger.debug(f"Created category subfolder: {category} (ID: {folder.get('id')})")

        except Exception as e:
            logger.error(f"Failed to create category subfolders: {str(e)}")

    def upload_file(self, file_path: str, company_name: str) -> Optional[str]:
        """
        Upload a file to the appropriate folder in Google Drive

        Args:
            file_path: Path to the file to upload
            company_name: Name of the company

        Returns:
            File ID if successful, None otherwise
        """
        try:
            # Get or create company folder
            company_folder_id = self.create_company_folder(company_name)
            if not company_folder_id:
                raise Exception("Failed to get or create company folder")

            # Determine file category
            category = self._categorize_file(file_path)
            if not category:
                logger.warning(f"Could not categorize file: {file_path}, using 'Uncategorized'")
                category = "Uncategorized"

            # Get category subfolder ID
            category_folder_id = self._find_folder(category, company_folder_id)
            if not category_folder_id:
                # Create uncategorized folder if category doesn't exist
                category_folder_id = self._create_folder(category, company_folder_id)

            # Upload file
            file_name = Path(file_path).name
            file_metadata = {
                'name': file_name,
                'parents': [category_folder_id]
            }

            media = MediaFileUpload(file_path, resumable=True)

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            file_id = file.get('id')
            logger.info(f"Uploaded file: {file_name} to {company_name}/{category} (ID: {file_id})")

            return file_id

        except HttpError as e:
            logger.error(f"Failed to upload file {file_path}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading file {file_path}: {str(e)}")
            return None

    def _categorize_file(self, file_path: str) -> Optional[str]:
        """
        Categorize file based on filename and document categories

        Args:
            file_path: Path to the file

        Returns:
            Category name if matched, None otherwise
        """
        file_name = Path(file_path).name.lower()

        for category, keywords in Config.DOCUMENT_CATEGORIES.items():
            for keyword in keywords:
                if keyword.lower() in file_name:
                    return category

        return None

    def _find_folder(self, folder_name: str, parent_id: str) -> Optional[str]:
        """
        Find a folder by name within a parent folder

        Args:
            folder_name: Name of the folder to find
            parent_id: ID of the parent folder

        Returns:
            Folder ID if found, None otherwise
        """
        try:
            query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"

            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            files = response.get('files', [])
            if files:
                return files[0]['id']

            return None

        except Exception as e:
            logger.error(f"Error finding folder {folder_name}: {str(e)}")
            return None

    def _create_folder(self, folder_name: str, parent_id: str) -> Optional[str]:
        """
        Create a new folder

        Args:
            folder_name: Name of the folder to create
            parent_id: ID of the parent folder

        Returns:
            Folder ID if successful, None otherwise
        """
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }

            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()

            return folder.get('id')

        except Exception as e:
            logger.error(f"Failed to create folder {folder_name}: {str(e)}")
            return None

    def check_document_completeness(self, company_name: str) -> Dict[str, List[str]]:
        """
        Check which required documents are present and missing for a company

        Args:
            company_name: Name of the company

        Returns:
            Dict with 'present' and 'missing' document lists
        """
        try:
            # Get company folder ID
            company_folder_id = self._find_folder(company_name, self.root_folder_id)
            if not company_folder_id:
                logger.warning(f"Company folder not found: {company_name}")
                return {'present': [], 'missing': Config.REQUIRED_DOCUMENTS.copy()}

            present_docs = []
            missing_docs = []

            for required_doc in Config.REQUIRED_DOCUMENTS:
                # Check if category folder exists and has files
                category_folder_id = self._find_folder(required_doc, company_folder_id)
                if category_folder_id and self._folder_has_files(category_folder_id):
                    present_docs.append(required_doc)
                else:
                    missing_docs.append(required_doc)

            result = {
                'present': present_docs,
                'missing': missing_docs
            }

            logger.info(f"Document completeness for {company_name}: Present={len(present_docs)}, Missing={len(missing_docs)}")
            return result

        except Exception as e:
            logger.error(f"Error checking document completeness for {company_name}: {str(e)}")
            return {'present': [], 'missing': Config.REQUIRED_DOCUMENTS.copy()}

    def _folder_has_files(self, folder_id: str) -> bool:
        """
        Check if a folder contains any files

        Args:
            folder_id: ID of the folder to check

        Returns:
            True if folder has files, False otherwise
        """
        try:
            query = f"'{folder_id}' in parents and trashed=false"

            response = self.service.files().list(
                q=query,
                spaces='drive',
                pageSize=1,
                fields='files(id)'
            ).execute()

            return len(response.get('files', [])) > 0

        except Exception as e:
            logger.error(f"Error checking folder contents: {str(e)}")
            return False

    def test_connection(self) -> bool:
        """
        Test connection to Google Drive

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.service.about().get(fields='user').execute()
            user = response.get('user', {})
            logger.info(f"Successfully connected to Google Drive as: {user.get('emailAddress', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Google Drive: {str(e)}")
            return False

    def get_user_info(self) -> Dict:
        """
        Get information about the authenticated user

        Returns:
            Dict with user information
        """
        try:
            response = self.service.about().get(fields='user').execute()
            user = response.get('user', {})
            return {
                'email': user.get('emailAddress', 'Unknown'),
                'name': user.get('displayName', 'Unknown'),
                'permission_id': user.get('permissionId', 'Unknown')
            }
        except Exception as e:
            logger.error(f"Failed to get user info: {str(e)}")
            return {}

    def get_company_files(self, company_name: str) -> List[Dict]:
        """
        Get all files for a company across all category folders

        Args:
            company_name: Name of the company

        Returns:
            List of file dictionaries with name, id, and folder info
        """
        try:
            # Get company folder ID
            company_folder_id = self._find_folder(company_name, self.root_folder_id)
            if not company_folder_id:
                logger.warning(f"Company folder not found: {company_name}")
                return []

            # Get all files in company folder and subfolders
            query = f"'{company_folder_id}' in parents and trashed=false"

            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, parents, mimeType)'
            ).execute()

            files = response.get('files', [])
            company_files = []

            for file in files:
                # Skip folders, only include files
                if file.get('mimeType') == 'application/vnd.google-apps.folder':
                    continue

                company_files.append({
                    'id': file.get('id'),
                    'name': file.get('name'),
                    'parents': file.get('parents', []),
                    'mimeType': file.get('mimeType', 'unknown')
                })

            logger.info(f"Found {len(company_files)} files for company: {company_name}")
            return company_files

        except Exception as e:
            logger.error(f"Error getting company files for {company_name}: {str(e)}")
            return []

# Test the OAuth authentication
if __name__ == "__main__":
    def test_oauth():
        """Test OAuth authentication and basic operations"""
        try:
            print("Testing OAuth Google Drive Manager...")

            manager = GoogleDriveManagerOAuth()

            # Test connection
            if manager.test_connection():
                print("✅ OAuth connection successful!")

                # Get user info
                user_info = manager.get_user_info()
                print(f"✅ Authenticated as: {user_info['name']} ({user_info['email']})")

                # Test folder creation
                test_company = "OAUTH TEST COMPANY"
                folder_id = manager.create_company_folder(test_company)
                if folder_id:
                    print(f"✅ Folder creation successful: {folder_id}")
                else:
                    print("❌ Folder creation failed")

            else:
                print("❌ OAuth connection failed")

        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            print("\nMake sure you have:")
            print("1. credentials.json in the project folder")
            print("2. Google Drive API enabled")
            print("3. OAuth client ID created")

    test_oauth()