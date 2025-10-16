#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production Startup Script for Legal Document Automation System
Indonesian WhatsApp Notifications - Ready for Deployment
"""

import os
import sys
from pathlib import Path

def print_production_banner():
    print("=" * 80)
    print("LEGAL DOCUMENT AUTOMATION SYSTEM - PRODUCTION")
    print("=" * 80)
    print("Indonesian WhatsApp Notifications - Automatic Missing Documents Alert")
    print("Checklist Evaluation: BG PIHK PT, BG PPIU PT, Laporan Keuangan")
    print("AI Document Classification & Processing")
    print("WhatsApp Integration: Real-time notifications to clients")
    print("=" * 80)

def check_production_requirements():
    """Check production requirements"""
    print("Checking production requirements...")

    # Check essential files
    required_files = [
        'final_web_app.py',
        'whatsapp_notifier.py',
        'requirements.txt',
        'templates/index.html',
        'credentials.json'
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
            print(f"[MISSING]: {file}")
        else:
            print(f"[OK]: {file}")

    if missing_files:
        print(f"\n[ERROR] Missing required files: {', '.join(missing_files)}")
        return False

    print("[OK] All required files present")
    return True

def set_production_config():
    """Set production environment variables"""
    print("\nSetting production configuration...")

    # Production settings
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DEBUG'] = 'False'

    # Default configuration (can be overridden with .env file)
    default_config = {
        'WATCH_FOLDER': 'D:/Download Legalitas',
        'OLLAMA_MODEL': 'llama3',
        'ADMIN_WHATSAPP_NUMBER': '628123456789',  # Replace with actual number
        'WAHA_API_URL': 'http://localhost:3000'
    }

    for key, value in default_config.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"[SET] {key}: {value}")

    print("[OK] Production configuration set")

def start_production_server():
    """Start the production Flask server"""
    print("\nStarting production server...")
    print("Server will be available at: http://localhost:5000")
    print("WhatsApp notifications will be sent automatically")
    print("Real-time document processing enabled")
    print("\nPress CTRL+C to stop the server")
    print("=" * 80)

    try:
        # Import and run the main application
        sys.path.append(str(Path(__file__).parent))
        import final_web_app

        # Run with production settings
        final_web_app.app.run(
            debug=False,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\nProduction server stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Error starting server: {e}")
        return False

    return True

def main():
    """Main production startup function"""
    print_production_banner()

    if not check_production_requirements():
        print("\n[ERROR] Production requirements not met. Please fix issues before deploying.")
        return False

    set_production_config()

    print("\n[OK] Production system ready!")
    print("Features:")
    print("   • Automatic WhatsApp notifications for missing documents")
    print("   • Indonesian message format for client communication")
    print("   • Real-time checklist evaluation")
    print("   • AI-powered document classification")
    print("   • Web dashboard for management")

    start_production_server()
    return True

if __name__ == "__main__":
    main()