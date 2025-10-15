"""
Web App Interface for Legal Document Automation System
Flask-based web interface with drag-drop file upload
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import json
from datetime import datetime
import threading
import time

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.config import Config
from app.ai_parser import AIParser
from app.drive_manager_oauth import GoogleDriveManagerOAuth as GoogleDriveManager, DocumentCompletenessChecker
from app.notifier import NotificationManager
from app.main import LegalDocumentAutomation

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

# Create temp upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global automation instance
automation_system = None

def init_automation():
    """Initialize automation system"""
    global automation_system
    try:
        automation_system = LegalDocumentAutomation()
        return automation_system.initialize()
    except Exception as e:
        print(f"Failed to initialize automation: {str(e)}")
        return False

def get_system_status():
    """Get current system status"""
    status = {
        'automation_initialized': automation_system is not None,
        'config': {
            'watch_folder': Config.WATCH_FOLDER,
            'ai_model': Config.OLLAMA_MODEL,
            'admin_whatsapp': Config.ADMIN_WHATSAPP_NUMBER
        },
        'services': {
            'ai_parser': False,
            'google_drive': False,
            'waha': False
        },
        'watch_folder': {
            'exists': False,
            'file_count': 0
        }
    }

    try:
        # Check watch folder
        watch_folder = Path(Config.WATCH_FOLDER)
        status['watch_folder']['exists'] = watch_folder.exists()
        if watch_folder.exists():
            files = [f for f in watch_folder.iterdir() if f.is_file()]
            status['watch_folder']['file_count'] = len(files)

        # Test services
        if automation_system:
            # AI Parser
            try:
                ai_parser = AIParser()
                status['services']['ai_parser'] = ai_parser.test_connection()
            except:
                pass

            # Google Drive
            try:
                drive_manager = GoogleDriveManager()
                status['services']['google_drive'] = drive_manager.test_connection()
            except:
                pass

            # WAHA
            try:
                notifier = NotificationManager()
                status['services']['waha'] = notifier.waha_notifier.test_connection()
            except:
                pass

    except Exception as e:
        status['error'] = str(e)

    return status

def get_watch_folder_files():
    """Get list of files in watch folder"""
    try:
        watch_folder = Path(Config.WATCH_FOLDER)
        if not watch_folder.exists():
            return []

        supported_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.tiff', '.tif'}
        files = []

        for file in watch_folder.iterdir():
            if file.is_file() and file.suffix.lower() in supported_extensions:
                stat = file.stat()
                files.append({
                    'name': file.name,
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'extension': file.suffix.lower()
                })

        # Sort by modified date (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        return files

    except Exception as e:
        return [{'error': str(e)}]

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify(get_system_status())

@app.route('/api/files')
def api_files():
    """API endpoint for watch folder files"""
    files = get_watch_folder_files()
    return jsonify({
        'files': files,
        'count': len(files),
        'watch_folder': Config.WATCH_FOLDER
    })

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for AI analysis"""
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        ai_parser = AIParser()
        result = ai_parser.extract_company_and_job(text)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint for file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        company = request.form.get('company', '')
        job_type = request.form.get('job_type', '')

        if not company or not job_type:
            return jsonify({'error': 'Company and job type required'}), 400

        # Save file temporarily
        filename = file.filename
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)

        # Process file
        if not automation_system or not automation_system.initialize():
            return jsonify({'error': 'System not initialized'}), 500

        user_command = {'company': company, 'job_type': job_type}
        success = automation_system.process_file(temp_path, user_command)

        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass

        if success:
            return jsonify({
                'success': True,
                'message': 'File processed successfully',
                'company': company,
                'job_type': job_type
            })
        else:
            return jsonify({'error': 'File processing failed'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process_existing', methods=['POST'])
def api_process_existing():
    """API endpoint to process existing files"""
    try:
        if not automation_system or not automation_system.initialize():
            return jsonify({'error': 'System not initialized'}), 500

        # Run in background thread
        def process_files():
            try:
                automation_system.process_existing_files()
            except Exception as e:
                print(f"Error processing existing files: {str(e)}")

        thread = threading.Thread(target=process_files)
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Started processing existing files'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check_completeness', methods=['POST'])
def api_check_completeness():
    """API endpoint to check document completeness"""
    try:
        data = request.get_json()
        company_name = data.get('company', '')

        if not company_name:
            return jsonify({'error': 'Company name required'}), 400

        drive_manager = GoogleDriveManager()
        checker = DocumentCompletenessChecker(drive_manager)

        result = checker.check_completeness(company_name)
        report = checker.generate_completeness_report(company_name)

        return jsonify({
            'success': True,
            'result': result,
            'report': report
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test_notification', methods=['POST'])
def api_test_notification():
    """API endpoint to test notifications"""
    try:
        notifier = NotificationManager()
        results = notifier.test_all_notifications()

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start_monitoring', methods=['POST'])
def api_start_monitoring():
    """API endpoint to start file monitoring"""
    try:
        if not automation_system or not automation_system.initialize():
            return jsonify({'error': 'System not initialized'}), 500

        # Run monitoring in background thread
        def monitor():
            try:
                automation_system.start_monitoring()
            except Exception as e:
                print(f"Monitoring error: {str(e)}")

        thread = threading.Thread(target=monitor)
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'message': 'File monitoring started'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize automation system
    print("Initializing Legal Document Automation System...")
    if init_automation():
        print("✅ System initialized successfully")
        print("🌐 Starting web server on http://localhost:5000")
        print("📱 Open your browser and navigate to http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Failed to initialize system")
        print("Please check your configuration and try again")