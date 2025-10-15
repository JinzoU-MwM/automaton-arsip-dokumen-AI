"""
Folder watcher module for monitoring changes in the Download Legalitas folder
Uses watchdog to detect new files and trigger processing
"""

import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import Callable, Optional

from app.config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LegalDocumentHandler(FileSystemEventHandler):
    """
    Handles file system events in the watched folder
    Triggers processing for new legal documents
    """

    def __init__(self, on_file_created: Optional[Callable] = None):
        """
        Initialize the handler with optional callback

        Args:
            on_file_created: Callback function to handle new files
        """
        self.on_file_created = on_file_created
        self.cooldown_time = 2  # seconds to wait for file to be fully written
        self.processed_files = set()  # Track already processed files

    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return

        file_path = event.src_path
        file_key = f"{file_path}_{os.path.getmtime(file_path) if os.path.exists(file_path) else 0}"

        # Avoid processing the same file multiple times
        if file_key in self.processed_files:
            return

        # Wait for file to be fully written
        time.sleep(self.cooldown_time)

        # Check if file still exists and is stable
        if not os.path.exists(file_path):
            logger.warning(f"File disappeared before processing: {file_path}")
            return

        # Add to processed files
        self.processed_files.add(file_key)

        # Check if it's a supported document type
        if self._is_supported_document(file_path):
            logger.info(f"New legal document detected: {file_path}")

            if self.on_file_created:
                try:
                    self.on_file_created(file_path)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
        else:
            logger.debug(f"Ignoring unsupported file: {file_path}")

    def _is_supported_document(self, file_path: str) -> bool:
        """
        Check if the file is a supported document type

        Args:
            file_path: Path to the file

        Returns:
            bool: True if supported, False otherwise
        """
        supported_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.jpg', '.jpeg', '.png', '.tiff', '.tif'
        }

        file_ext = Path(file_path).suffix.lower()
        return file_ext in supported_extensions


class LegalDocumentWatcher:
    """
    Main watcher class that monitors the folder for new legal documents
    """

    def __init__(self, on_file_created: Optional[Callable] = None):
        """
        Initialize the watcher

        Args:
            on_file_created: Callback function for handling new files
        """
        self.watch_folder = Config.WATCH_FOLDER
        self.on_file_created = on_file_created
        self.observer = Observer()
        self.event_handler = LegalDocumentHandler(on_file_created)
        self.is_running = False

    def start(self):
        """Start monitoring the folder"""
        try:
            # Create watch folder if it doesn't exist
            os.makedirs(self.watch_folder, exist_ok=True)

            logger.info(f"Starting folder watcher for: {self.watch_folder}")

            # Start observer
            self.observer.schedule(
                self.event_handler,
                self.watch_folder,
                recursive=False
            )
            self.observer.start()
            self.is_running = True

            logger.info("Folder watcher started successfully")

        except Exception as e:
            logger.error(f"Failed to start folder watcher: {str(e)}")
            raise

    def stop(self):
        """Stop monitoring the folder"""
        if self.is_running:
            logger.info("Stopping folder watcher...")
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("Folder watcher stopped")

    def run_forever(self):
        """Run the watcher indefinitely"""
        try:
            self.start()
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping watcher...")
            self.stop()
        except Exception as e:
            logger.error(f"Watcher error: {str(e)}")
            self.stop()
            raise

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# Example usage and testing
if __name__ == "__main__":
    def sample_callback(file_path: str):
        """Sample callback function for testing"""
        print(f"Processing new file: {file_path}")

    # Test the watcher
    try:
        with LegalDocumentWatcher(on_file_created=sample_callback) as watcher:
            print("Watcher is running... Press Ctrl+C to stop")
            watcher.run_forever()
    except KeyboardInterrupt:
        print("Watcher stopped by user")