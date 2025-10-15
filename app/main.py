"""
Main orchestrator for AI Legal Document Automation System
Coordinates file watching, AI parsing, Google Drive operations, and notifications
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Optional

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.config import Config
from app.watcher import LegalDocumentWatcher
from app.ai_parser import AIParser
from app.drive_manager_oauth import GoogleDriveManagerOAuth as GoogleDriveManager, DocumentCompletenessChecker
from app.notifier import NotificationManager

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)


class LegalDocumentAutomation:
    """
    Main automation system that orchestrates all components
    """

    def __init__(self):
        """Initialize the automation system"""
        self.ai_parser = None
        self.drive_manager = None
        self.completeness_checker = None
        self.notification_manager = None
        self.watcher = None
        self.is_running = False

    def initialize(self) -> bool:
        """
        Initialize all system components

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Legal Document Automation System...")

            # Validate configuration
            Config.validate()
            logger.info("✅ Configuration validated")

            # Initialize AI parser
            self.ai_parser = AIParser()
            if not self.ai_parser.test_connection():
                logger.error("❌ Failed to connect to Ollama. Please ensure Ollama is running.")
                return False
            logger.info("✅ AI parser initialized")

            # Initialize Google Drive manager
            self.drive_manager = GoogleDriveManager()
            if not self.drive_manager.test_connection():
                logger.error("❌ Failed to connect to Google Drive. Check credentials.")
                return False
            logger.info("✅ Google Drive manager initialized")

            # Initialize document completeness checker
            self.completeness_checker = DocumentCompletenessChecker(self.drive_manager)
            logger.info("✅ Document completeness checker initialized")

            # Initialize notification manager
            self.notification_manager = NotificationManager()
            test_results = self.notification_manager.test_all_notifications()

            if not all(test_results.values()):
                logger.warning("⚠️ Some notification systems failed. Check WAHA configuration.")
            else:
                logger.info("✅ All notification systems initialized")

            logger.info("🎉 System initialization complete!")
            return True

        except Exception as e:
            logger.error(f"❌ System initialization failed: {str(e)}")
            return False

    def get_user_command(self) -> Optional[dict]:
        """
        Get user command input for processing a file

        Returns:
            Dict with company and job_type, or None if failed
        """
        print("\n" + "="*60)
        print("🤖 AI Legal Document Automation System")
        print("="*60)
        print("Masukkan instruksi untuk dokumen yang baru ditambahkan:")
        print("Contoh: 'Ini untuk PT Jaminan Nasional Indonesia, pekerjaan pengurusan izin PPIU'")
        print("-"*60)

        try:
            user_input = input("\nInstruksi: ").strip()
            if not user_input:
                logger.warning("No input provided")
                return None

            logger.info(f"Processing user input: {user_input}")
            result = self.ai_parser.extract_company_and_job(user_input)
            logger.info(f"AI parsing result: {result}")

            return result

        except KeyboardInterrupt:
            logger.info("User cancelled input")
            return None
        except Exception as e:
            logger.error(f"Error processing user command: {str(e)}")
            return None

    def process_file(self, file_path: str, user_command: Optional[dict] = None) -> bool:
        """
        Process a single file through the entire pipeline

        Args:
            file_path: Path to the file to process
            user_command: Optional pre-parsed user command

        Returns:
            True if processing successful, False otherwise
        """
        try:
            logger.info(f"Starting processing for file: {file_path}")
            file_name = Path(file_path).name

            # Get user command if not provided
            if not user_command:
                user_command = self.get_user_command()
                if not user_command:
                    logger.error("No valid user command provided")
                    return False

            company_name = user_command.get('company', 'Unknown')
            job_type = user_command.get('job_type', 'Unknown')

            logger.info(f"Processing {file_name} for {company_name} - {job_type}")

            # Upload file to Google Drive
            file_id = self.drive_manager.upload_file(file_path, company_name)
            if not file_id:
                error_msg = f"Failed to upload file {file_name} to Google Drive"
                logger.error(error_msg)
                self.notification_manager.notify_system_error(error_msg, {
                    'file_path': file_path,
                    'company': company_name,
                    'job_type': job_type
                })
                return False

            logger.info(f"✅ File uploaded successfully (ID: {file_id})")

            # Check document completeness
            completeness_result = self.completeness_checker.check_completeness(company_name)
            logger.info(f"Document completeness result: {completeness_result}")

            # Send notifications
            notification_success = self.notification_manager.notify_file_processed(
                company_name, job_type, file_name, completeness_result
            )

            if notification_success:
                logger.info("✅ Notifications sent successfully")
            else:
                logger.warning("⚠️ Some notifications failed")

            logger.info(f"🎉 Processing complete for {file_name}")
            return True

        except Exception as e:
            error_msg = f"Error processing file {file_path}: {str(e)}"
            logger.error(error_msg)
            self.notification_manager.notify_system_error(error_msg, {
                'file_path': file_path,
                'company': user_command.get('company', 'Unknown') if user_command else 'Unknown',
                'job_type': user_command.get('job_type', 'Unknown') if user_command else 'Unknown'
            })
            return False

    def start_monitoring(self):
        """Start monitoring the watch folder for new files"""
        try:
            logger.info("Starting folder monitoring mode...")

            def on_file_created(file_path: str):
                """Handle new file creation"""
                logger.info(f"New file detected: {file_path}")
                try:
                    self.process_file(file_path)
                except Exception as e:
                    logger.error(f"Failed to process new file {file_path}: {str(e)}")

            # Initialize watcher
            self.watcher = LegalDocumentWatcher(on_file_created)
            self.is_running = True

            logger.info("🔍 Folder monitoring started. Press Ctrl+C to stop.")
            self.watcher.run_forever()

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
        finally:
            self.stop()

    def process_existing_files(self):
        """Process all existing files in the watch folder"""
        try:
            watch_folder = Path(Config.WATCH_FOLDER)
            if not watch_folder.exists():
                logger.error(f"Watch folder does not exist: {watch_folder}")
                return

            logger.info(f"Processing existing files in: {watch_folder}")

            supported_extensions = {
                '.pdf', '.doc', '.docx', '.xls', '.xlsx',
                '.jpg', '.jpeg', '.png', '.tiff', '.tif'
            }

            files_processed = 0
            for file_path in watch_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    logger.info(f"Found existing file: {file_path}")
                    if self.process_file(str(file_path)):
                        files_processed += 1

            logger.info(f"Processed {files_processed} existing files")

        except Exception as e:
            logger.error(f"Error processing existing files: {str(e)}")

    def run_interactive_mode(self):
        """Run in interactive mode for manual file processing"""
        try:
            logger.info("Starting interactive mode...")

            while True:
                print("\n" + "="*50)
                print("🤖 Legal Document Automation - Interactive Mode")
                print("="*50)
                print("1. Process a file")
                print("2. Process existing files in folder")
                print("3. Check document completeness")
                print("4. Send test notification")
                print("5. Exit")
                print("-"*50)

                choice = input("Select option (1-5): ").strip()

                if choice == '1':
                    file_path = input("Enter file path: ").strip()
                    if os.path.exists(file_path):
                        self.process_file(file_path)
                    else:
                        print("❌ File not found")

                elif choice == '2':
                    self.process_existing_files()

                elif choice == '3':
                    company_name = input("Enter company name: ").strip()
                    if company_name:
                        result = self.completeness_checker.check_completeness(company_name)
                        report = self.completeness_checker.generate_completeness_report(company_name)
                        print(f"\n{report}")

                elif choice == '4':
                    results = self.notification_manager.test_all_notifications()
                    print("\nNotification Test Results:")
                    for test_name, result in results.items():
                        status = "✅" if result else "❌"
                        print(f"{status} {test_name.replace('_', ' ').title()}")

                elif choice == '5':
                    print("👋 Goodbye!")
                    break

                else:
                    print("❌ Invalid option")

        except KeyboardInterrupt:
            logger.info("Interactive mode stopped by user")
        except Exception as e:
            logger.error(f"Interactive mode error: {str(e)}")

    def stop(self):
        """Stop the automation system"""
        logger.info("Stopping Legal Document Automation System...")
        self.is_running = False

        if self.watcher:
            self.watcher.stop()

        logger.info("System stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Legal Document Automation System")
    parser.add_argument('--mode', choices=['monitor', 'interactive', 'process-existing'],
                       default='monitor', help='Running mode')
    parser.add_argument('--file', type=str, help='Process specific file')
    parser.add_argument('--config-check', action='store_true', help='Check configuration only')

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    try:
        # Initialize system
        automation = LegalDocumentAutomation()

        if args.config_check:
            print("Checking system configuration...")
            if automation.initialize():
                print("✅ All systems ready!")
            else:
                print("❌ Configuration issues found. Check logs for details.")
            return

        if not automation.initialize():
            logger.error("❌ Failed to initialize system")
            sys.exit(1)

        # Run based on mode
        if args.file:
            # Process specific file
            if os.path.exists(args.file):
                automation.process_file(args.file)
            else:
                logger.error(f"File not found: {args.file}")
        elif args.mode == 'monitor':
            # Monitor folder for new files
            automation.start_monitoring()
        elif args.mode == 'interactive':
            # Interactive mode
            automation.run_interactive_mode()
        elif args.mode == 'process-existing':
            # Process existing files
            automation.process_existing_files()

    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()