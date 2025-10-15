"""
Enhanced CLI Interface for Legal Document Automation System
Provides user-friendly menu-driven interface
"""

import os
import sys
from pathlib import Path
from typing import Optional
import argparse

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.config import Config
from app.ai_parser import AIParser
from app.drive_manager_oauth import GoogleDriveManagerOAuth as GoogleDriveManager, DocumentCompletenessChecker
from app.notifier import NotificationManager


class LegalDocumentCLI:
    """Enhanced CLI interface for the automation system"""

    def __init__(self):
        self.automation = None
        self.colors = {
            'header': '\033[95m',
            'blue': '\033[94m',
            'cyan': '\033[96m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }

    def color_print(self, text, color='white'):
        """Print colored text"""
        if color in self.colors:
            print(f"{self.colors[color]}{text}{self.colors['end']}")
        else:
            print(text)

    def show_banner(self):
        """Display system banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                LEGAL DOCUMENT AUTOMATION SYSTEM              ║
║                     Version 1.0                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.color_print(banner, 'cyan')

    def show_status(self):
        """Display system status"""
        print("\n" + "="*60)
        self.color_print("📊 SYSTEM STATUS", 'bold')
        print("="*60)

        try:
            # Configuration
            self.color_print(f"📁 Watch Folder: {Config.WATCH_FOLDER}", 'blue')
            self.color_print(f"🤖 AI Model: {Config.OLLAMA_MODEL}", 'blue')
            self.color_print(f"📱 Admin WhatsApp: {Config.ADMIN_WHATSAPP_NUMBER}", 'blue')

            # Check if folder exists
            watch_folder = Path(Config.WATCH_FOLDER)
            if watch_folder.exists():
                self.color_print("✅ Watch folder exists", 'green')

                # Count files
                files = list(watch_folder.glob("*"))
                self.color_print(f"📄 Files in folder: {len(files)}", 'yellow')
            else:
                self.color_print("❌ Watch folder does not exist", 'red')

            # Test connections
            self.color_print("\n🔗 Testing Connections...", 'bold')

            # AI Parser
            try:
                ai_parser = AIParser()
                if ai_parser.test_connection():
                    self.color_print("✅ AI Parser (Ollama): Connected", 'green')
                else:
                    self.color_print("❌ AI Parser (Ollama): Failed", 'red')
            except:
                self.color_print("❌ AI Parser (Ollama): Error", 'red')

            # Google Drive
            try:
                drive_manager = GoogleDriveManager()
                if drive_manager.test_connection():
                    self.color_print("✅ Google Drive: Connected", 'green')
                else:
                    self.color_print("❌ Google Drive: Failed", 'red')
            except:
                self.color_print("❌ Google Drive: Error", 'red')

            # WAHA
            try:
                notifier = NotificationManager()
                if notifier.waha_notifier.test_connection():
                    self.color_print("✅ WAHA WhatsApp: Connected", 'green')
                else:
                    self.color_print("❌ WAHA WhatsApp: Failed", 'red')
            except:
                self.color_print("❌ WAHA WhatsApp: Error", 'red')

        except Exception as e:
            self.color_print(f"❌ Status check error: {str(e)}", 'red')

    def show_main_menu(self):
        """Display main menu"""
        menu_options = [
            "🚀 START MONITORING - Watch folder for new files",
            "📂 PROCESS EXISTING FILES - Process all files in watch folder",
            "📄 PROCESS SINGLE FILE - Select and process specific file",
            "🔍 CHECK DOCUMENT COMPLETENESS - Verify company documents",
            "📱 SEND TEST NOTIFICATION - Test WhatsApp notification",
            "📊 SYSTEM STATUS - Check all system connections",
            "⚙️  CONFIGURATION INFO - Show current settings",
            "🗂️  WATCH FOLDER FILES - List files in watch folder",
            "❌ EXIT"
        ]

        print("\n" + "="*60)
        self.color_print("🏠 MAIN MENU", 'bold')
        print("="*60)

        for i, option in enumerate(menu_options, 1):
            self.color_print(f"{i:2d}. {option}", 'cyan')

    def process_single_file(self):
        """Process a single file with user selection"""
        try:
            watch_folder = Path(Config.WATCH_FOLDER)
            if not watch_folder.exists():
                self.color_print("❌ Watch folder does not exist!", 'red')
                return

            # Get supported files
            supported_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.tiff', '.tif'}
            files = [f for f in watch_folder.iterdir()
                    if f.is_file() and f.suffix.lower() in supported_extensions]

            if not files:
                self.color_print("❌ No supported files found in watch folder!", 'yellow')
                return

            print("\n" + "="*60)
            self.color_print("📄 SELECT FILE TO PROCESS", 'bold')
            print("="*60)

            for i, file in enumerate(files, 1):
                size_mb = file.stat().st_size / (1024 * 1024)
                self.color_print(f"{i:2d}. {file.name} ({size_mb:.2f} MB)", 'blue')

            self.color_print(" 0. Cancel", 'yellow')

            while True:
                try:
                    choice = input(f"\nSelect file (1-{len(files)}): ").strip()
                    if choice == '0':
                        return

                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(files):
                        selected_file = files[choice_idx]
                        self.color_print(f"\n📄 Selected: {selected_file.name}", 'green')

                        # Get AI to parse file info
                        self.color_print("🤖 Analyzing file name...", 'yellow')
                        ai_parser = AIParser()

                        file_name_analysis = ai_parser.extract_company_and_job(selected_file.name)
                        self.color_print(f"AI Analysis: {file_name_analysis}", 'cyan')

                        # Let user confirm or modify
                        print("\n" + "-"*40)
                        self.color_print("📝 DOCUMENT INFORMATION", 'bold')
                        print("-"*40)

                        company = input(f"Company Name [{file_name_analysis.get('company', '')}]: ").strip()
                        if not company:
                            company = file_name_analysis.get('company', 'Unknown')

                        job_type = input(f"Job Type [{file_name_analysis.get('job_type', '')}]: ").strip()
                        if not job_type:
                            job_type = file_name_analysis.get('job_type', 'Unknown')

                        # Process the file
                        self.color_print(f"\n🚀 Processing {selected_file.name}...", 'yellow')

                        # Initialize automation system
                        from app.main import LegalDocumentAutomation
                        automation = LegalDocumentAutomation()

                        if automation.initialize():
                            user_command = {'company': company, 'job_type': job_type}
                            success = automation.process_file(str(selected_file), user_command)

                            if success:
                                self.color_print("✅ File processed successfully!", 'green')
                                self.color_print("📱 WhatsApp notification sent!", 'green')
                            else:
                                self.color_print("❌ File processing failed!", 'red')
                        else:
                            self.color_print("❌ System initialization failed!", 'red')

                        break
                    else:
                        self.color_print("❌ Invalid selection!", 'red')
                except ValueError:
                    self.color_print("❌ Please enter a valid number!", 'red')

        except Exception as e:
            self.color_print(f"❌ Error: {str(e)}", 'red')

    def show_config_info(self):
        """Display configuration information"""
        print("\n" + "="*60)
        self.color_print("⚙️  CONFIGURATION INFORMATION", 'bold')
        print("="*60)

        config_items = [
            ("Watch Folder", Config.WATCH_FOLDER),
            ("Ollama Base URL", Config.OLLAMA_BASE_URL),
            ("Ollama Model", Config.OLLAMA_MODEL),
            ("WAHA API URL", Config.WAHA_API_URL),
            ("Admin WhatsApp", Config.ADMIN_WHATSAPP_NUMBER),
            ("Google Drive Folder ID", Config.GOOGLE_DRIVE_FOLDER_ID[:20] + "..." if len(Config.GOOGLE_DRIVE_FOLDER_ID) > 20 else Config.GOOGLE_DRIVE_FOLDER_ID),
            ("Log Level", Config.LOG_LEVEL),
            ("Log File", Config.LOG_FILE)
        ]

        for key, value in config_items:
            self.color_print(f"📋 {key:.<25} {value}", 'blue')

        # Show document categories
        print(f"\n📂 Document Categories ({len(Config.DOCUMENT_CATEGORIES)}):")
        for category, keywords in Config.DOCUMENT_CATEGORIES.items():
            self.color_print(f"   • {category}: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}", 'cyan')

    def list_watch_folder_files(self):
        """List all files in the watch folder"""
        try:
            watch_folder = Path(Config.WATCH_FOLDER)
            if not watch_folder.exists():
                self.color_print("❌ Watch folder does not exist!", 'red')
                return

            print("\n" + "="*60)
            self.color_print(f"🗂️  FILES IN: {watch_folder}", 'bold')
            print("="*60)

            all_files = list(watch_folder.glob("*"))
            if not all_files:
                self.color_print("📁 Folder is empty", 'yellow')
                return

            supported_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.tiff', '.tif'}
            supported_files = []
            other_files = []

            for file in all_files:
                if file.is_file():
                    if file.suffix.lower() in supported_extensions:
                        supported_files.append(file)
                    else:
                        other_files.append(file)

            # Show supported files
            if supported_files:
                self.color_print(f"\n📄 Supported Files ({len(supported_files)}):", 'green')
                for file in supported_files:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    modified = file.stat().st_mtime
                    import datetime
                    mod_time = datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M')
                    self.color_print(f"   📋 {file.name:<40} {size_mb:>6.2f} MB  {mod_time}", 'blue')

            # Show other files
            if other_files:
                self.color_print(f"\n📁 Other Files ({len(other_files)}):", 'yellow')
                for file in other_files:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    self.color_print(f"   📄 {file.name:<40} {size_mb:>6.2f} MB", 'cyan')

        except Exception as e:
            self.color_print(f"❌ Error listing files: {str(e)}", 'red')

    def check_document_completeness(self):
        """Check document completeness for a company"""
        try:
            print("\n" + "="*60)
            self.color_print("🔍 DOCUMENT COMPLETENESS CHECK", 'bold')
            print("="*60)

            company_name = input("Enter company name: ").strip()
            if not company_name:
                self.color_print("❌ Company name required!", 'red')
                return

            # Initialize systems
            drive_manager = GoogleDriveManager()
            checker = DocumentCompletenessChecker(drive_manager)

            self.color_print(f"\n🔍 Checking documents for: {company_name}", 'yellow')

            result = checker.check_completeness(company_name)
            report = checker.generate_completeness_report(company_name)

            print("\n" + "-"*40)
            self.color_print("📊 COMPLETENESS REPORT", 'bold')
            print("-"*40)
            print(report)

            if result['status'] == 'complete':
                self.color_print("\n🎉 All documents are complete!", 'green')
            elif result['completion_percentage'] >= 75:
                self.color_print(f"\n✅ Almost complete ({result['completion_percentage']}%)", 'green')
            elif result['completion_percentage'] >= 50:
                self.color_print(f"\n⚠️  Partially complete ({result['completion_percentage']}%)", 'yellow')
            else:
                self.color_print(f"\n❌ Many documents missing ({result['completion_percentage']}%)", 'red')

        except Exception as e:
            self.color_print(f"❌ Error checking completeness: {str(e)}", 'red')

    def run(self):
        """Run the CLI interface"""
        while True:
            try:
                self.show_banner()
                self.show_main_menu()

                choice = input(f"\n{'='*60}\n🎯 Select option (1-9): ").strip()

                if choice == '1':
                    # Start monitoring
                    self.color_print("\n🚀 Starting file monitoring...", 'yellow')
                    from app.main import LegalDocumentAutomation
                    automation = LegalDocumentAutomation()
                    if automation.initialize():
                        automation.start_monitoring()
                    else:
                        self.color_print("❌ System initialization failed!", 'red')

                elif choice == '2':
                    # Process existing files
                    self.color_print("\n📂 Processing existing files...", 'yellow')
                    from app.main import LegalDocumentAutomation
                    automation = LegalDocumentAutomation()
                    if automation.initialize():
                        automation.process_existing_files()
                    else:
                        self.color_print("❌ System initialization failed!", 'red')

                elif choice == '3':
                    # Process single file
                    self.process_single_file()

                elif choice == '4':
                    # Check document completeness
                    self.check_document_completeness()

                elif choice == '5':
                    # Send test notification
                    self.color_print("\n📱 Sending test notification...", 'yellow')
                    try:
                        notifier = NotificationManager()
                        results = notifier.test_all_notifications()
                        print("\n📊 Notification Test Results:")
                        for test_name, result in results.items():
                            status = "✅" if result else "❌"
                            self.color_print(f"   {status} {test_name.replace('_', ' ').title()}", 'green' if result else 'red')
                    except Exception as e:
                        self.color_print(f"❌ Error sending test notification: {str(e)}", 'red')

                elif choice == '6':
                    # System status
                    self.show_status()

                elif choice == '7':
                    # Configuration info
                    self.show_config_info()

                elif choice == '8':
                    # List watch folder files
                    self.list_watch_folder_files()

                elif choice == '9':
                    # Exit
                    self.color_print("\n👋 Goodbye!", 'green')
                    break

                else:
                    self.color_print("❌ Invalid option! Please select 1-9.", 'red')

                if choice != '9':
                    input(f"\n{'='*60}\nPress Enter to continue...")

            except KeyboardInterrupt:
                self.color_print("\n\n👋 Exiting... Goodbye!", 'green')
                break
            except Exception as e:
                self.color_print(f"\n❌ Unexpected error: {str(e)}", 'red')
                input("Press Enter to continue...")


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description="Legal Document Automation CLI")
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')

    args = parser.parse_args()

    # Create and run CLI
    cli = LegalDocumentCLI()

    if args.no_color:
        # Disable colors if requested
        for color in cli.colors:
            cli.colors[color] = ''

    cli.run()


if __name__ == "__main__":
    main()