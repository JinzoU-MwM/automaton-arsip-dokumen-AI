"""
Startup script for Legal Document Automation System
Provides easy access to CLI and Web interfaces
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Legal Document Automation System Launcher")
    parser.add_argument('--interface', choices=['cli', 'web', 'both'],
                       default='both', help='Interface to start')
    parser.add_argument('--port', type=int, default=5000, help='Web interface port')
    parser.add_argument('--host', default='0.0.0.0', help='Web interface host')

    args = parser.parse_args()

    print("="*60)
    print("🤖 LEGAL DOCUMENT AUTOMATION SYSTEM")
    print("="*60)
    print("🚀 Starting system components...")

    # Check dependencies
    try:
        import flask
        print("✅ Flask available")
    except ImportError:
        print("❌ Flask not installed. Install with: pip install flask")
        return

    try:
        import watchdog
        print("✅ Watchdog available")
    except ImportError:
        print("❌ Watchdog not installed. Install with: pip install watchdog")
        return

    # Start interfaces based on choice
    if args.interface in ['web', 'both']:
        print("\n🌐 Starting Web Interface...")
        print(f"   URL: http://{args.host}:{args.port}")
        print("   Features: Drag-drop upload, AI analysis, real-time status")

        if args.interface == 'both':
            import threading

            def start_web():
                os.system(f"python web_app.py --host {args.host} --port {args.port}")

            web_thread = threading.Thread(target=start_web)
            web_thread.daemon = True
            web_thread.start()

            # Give web server time to start
            import time
            time.sleep(2)

    if args.interface in ['cli', 'both']:
        if args.interface == 'both':
            print("\n" + "="*60)
            print("💻 CLI Interface also available in another terminal")
            print("   Run: python cli_interface.py")
        else:
            print("\n💻 Starting CLI Interface...")
            os.system("python cli_interface.py")

    if args.interface == 'web':
        print(f"\n🌐 Web interface starting on http://{args.host}:{args.port}")
        print("📱 Open your browser to access the system")
        os.system(f"python web_app.py --host {args.host} --port {args.port}")

if __name__ == "__main__":
    main()