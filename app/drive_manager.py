"""
Google Drive Manager module for handling file uploads, folder creation,
and document organization according to company and document categories
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from app.config import Config

logger = logging.getLogger(__name__)


class GoogleDriveManager:
    """
    Manages Google Drive operations including folder creation,
    file uploads, and document organization
    """

    def __init__(self):
        """Initialize Google Drive manager with service account"""
        self.service = None
        self.root_folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
        self.credentials_path = Config.GOOGLE_DRIVE_CREDENTIALS_PATH
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive using service account"""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Service account file not found: {self.credentials_path}")

            # Define the required scopes (including shared drives support)
            scopes = [
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.metadata'
            ]

            # Load service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scopes
            )

            # Build the Drive API service
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("Successfully authenticated with Google Drive")

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
                fields='id',
                supportsAllDrives=True
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
                fields='id',
                supportsAllDrives=True
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
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
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
                fields='id',
                supportsAllDrives=True
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
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
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


class DocumentCompletenessChecker:
    """
    Specialized class for checking document completeness
    Works with GoogleDriveManager to validate required documents
    """

    def __init__(self, drive_manager: GoogleDriveManager):
        """Initialize with a GoogleDriveManager instance"""
        self.drive_manager = drive_manager

    def check_completeness(self, company_name: str) -> Dict[str, any]:
        """
        Comprehensive completeness check with detailed results

        Args:
            company_name: Name of the company to check

        Returns:
            Dict with comprehensive completeness information
        """
        try:
            # Get basic completeness from drive manager
            completeness = self.drive_manager.check_document_completeness(company_name)

            # Calculate completion percentage
            total_required = len(Config.REQUIRED_DOCUMENTS)
            present_count = len(completeness['present'])
            completion_percentage = (present_count / total_required) * 100

            # Determine status
            if completion_percentage == 100:
                status = "complete"
            elif completion_percentage >= 75:
                status = "mostly_complete"
            elif completion_percentage >= 50:
                status = "partially_complete"
            else:
                status = "incomplete"

            result = {
                'company': company_name,
                'status': status,
                'completion_percentage': round(completion_percentage, 1),
                'present_documents': completeness['present'],
                'missing_documents': completeness['missing'],
                'total_required': total_required,
                'total_present': present_count,
                'total_missing': len(completeness['missing']),
                'timestamp': self._get_current_timestamp()
            }

            logger.info(f"Completeness check for {company_name}: {status} ({completion_percentage:.1f}%)")
            return result

        except Exception as e:
            logger.error(f"Error in completeness check for {company_name}: {str(e)}")
            return self._get_error_result(company_name, str(e))

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()

    def _get_error_result(self, company_name: str, error_message: str) -> Dict[str, any]:
        """Return error result structure"""
        return {
            'company': company_name,
            'status': 'error',
            'completion_percentage': 0,
            'present_documents': [],
            'missing_documents': Config.REQUIRED_DOCUMENTS.copy(),
            'total_required': len(Config.REQUIRED_DOCUMENTS),
            'total_present': 0,
            'total_missing': len(Config.REQUIRED_DOCUMENTS),
            'error': error_message,
            'timestamp': self._get_current_timestamp()
        }

    def get_missing_critical_documents(self, company_name: str) -> List[str]:
        """
        Get list of critical missing documents

        Args:
            company_name: Company name to check

        Returns:
            List of critical missing document types
        """
        try:
            completeness = self.check_completeness(company_name)
            missing = completeness.get('missing_documents', [])

            # Define critical documents (most important for legal compliance)
            critical_docs = ['Akta', 'NIB', 'NPWP', 'KTP Pengurus']

            critical_missing = [doc for doc in missing if doc in critical_docs]
            return critical_missing

        except Exception as e:
            logger.error(f"Error getting critical missing documents: {str(e)}")
            return []

    def generate_completeness_report(self, company_name: str) -> str:
        """
        Generate human-readable completeness report

        Args:
            company_name: Company name to generate report for

        Returns:
            Formatted string report
        """
        try:
            result = self.check_completeness(company_name)

            report = f"📄 Laporan Kelengkapan Dokumen - {company_name}\n"
            report += f"📊 Status: {result['status'].replace('_', ' ').title()}\n"
            report += f"📈 Persentase: {result['completion_percentage']}%\n"
            report += f"✅ Dokumen Ada ({result['total_present']}): {', '.join(result['present_documents']) if result['present_documents'] else 'Tidak ada'}\n"
            report += f"❌ Dokumen Kurang ({result['total_missing']}): {', '.join(result['missing_documents']) if result['missing_documents'] else 'Tidak ada'}\n"
            report += f"📅 Periksa: {result['timestamp']}"

            if 'error' in result:
                report += f"\n⚠️ Error: {result['error']}"

            return report

        except Exception as e:
            logger.error(f"Error generating completeness report: {str(e)}")
            return f"❌ Gagal generate laporan: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    def test_drive_manager():
        """Test the Google Drive manager"""
        try:
            manager = GoogleDriveManager()

            # Test connection
            if not manager.test_connection():
                print("Failed to connect to Google Drive")
                return

            print("Google Drive connection successful")

            # Test company folder creation
            test_company = "PT Test Company"
            folder_id = manager.create_company_folder(test_company)
            print(f"Company folder ID: {folder_id}")

            # Test document completeness checker
            checker = DocumentCompletenessChecker(manager)
            completeness = checker.check_completeness(test_company)
            print(f"Document completeness: {completeness}")

            # Generate report
            report = checker.generate_completeness_report(test_company)
            print(f"Report:\n{report}")

        except Exception as e:
            print(f"Test failed: {str(e)}")

    test_drive_manager()