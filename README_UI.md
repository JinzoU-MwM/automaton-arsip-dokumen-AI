# Legal Document Automation System - User Interfaces

## 🚀 Easy Startup

### Method 1: Use the Startup Script (Recommended)
```bash
python start.py
```
This will start both the CLI and Web interfaces.

### Method 2: Start Specific Interface

#### Web Interface Only
```bash
python start.py --interface web --port 5000
```
Then open http://localhost:5000 in your browser.

#### CLI Interface Only
```bash
python start.py --interface cli
```

### Method 3: Direct Execution

#### Web Interface
```bash
python web_app.py
```

#### Enhanced CLI Interface
```bash
python cli_interface.py
```

#### Original CLI
```bash
python -m app.main --mode interactive
```

## 🌐 Web Interface Features

### Main Dashboard
- **Real-time System Status**: Monitor AI Parser, Google Drive, WAHA WhatsApp, and Watch Folder status
- **Statistics**: File counts, processing stats, and notification counts
- **Drag & Drop Upload**: Simply drag files to the upload zone
- **AI Text Analysis**: Test AI parsing with natural language input
- **File Management**: View, process, and manage files in the watch folder

### Key Features
1. **📁 File Upload**
   - Drag & drop files directly to upload
   - Automatic AI analysis of filenames
   - Manual override of company/job information

2. **🤖 AI Analysis**
   - Test AI parsing with any text input
   - Real-time extraction of company and job information
   - Supports Indonesian and English text

3. **📊 System Monitoring**
   - Live status indicators for all services
   - File listing with details (size, date modified)
   - Configuration information

4. **🔧 Quick Actions**
   - Process all existing files
   - Start automatic file monitoring
   - Check document completeness
   - Test WhatsApp notifications
   - View system configuration

### File Upload Process
1. Drag file to upload zone or click to select
2. AI automatically analyzes filename
3. Confirm/modify company and job information
4. Click "Upload & Process" to start automation
5. Receive WhatsApp notification when complete

## 💻 CLI Interface Features

### Main Menu Options
1. **🚀 START MONITORING** - Watch folder for new files automatically
2. **📂 PROCESS EXISTING FILES** - Process all files currently in watch folder
3. **📄 PROCESS SINGLE FILE** - Select and process a specific file
4. **🔍 CHECK DOCUMENT COMPLETENESS** - Verify company documents
5. **📱 SEND TEST NOTIFICATION** - Test WhatsApp notification
6. **📊 SYSTEM STATUS** - Check all system connections
7. **⚙️ CONFIGURATION INFO** - Show current settings
8. **🗂️ WATCH FOLDER FILES** - List files in watch folder
9. **❌ EXIT**

### Enhanced Features
- **Colored Output**: Easy-to-read status indicators
- **File Selection**: Interactive file browser
- **AI Integration**: Automatic filename analysis
- **Status Monitoring**: Real-time system health checks
- **Error Handling**: Clear error messages and recovery

## 📋 System Requirements

### Dependencies
```bash
pip install flask watchdog google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 requests pathlib argparse
```

### External Services
1. **Ollama AI**: Running on http://localhost:11434
2. **WAHA WhatsApp**: Running on http://localhost:3000
3. **Google Drive**: Configured with service account or OAuth

## 🔧 Configuration

Make sure your `.env` file is properly configured:
```env
# Folder Configuration
WATCH_FOLDER=D:\Source File

# Google Drive Configuration
GOOGLE_DRIVE_FOLDER_ID=your_folder_id

# Ollama AI Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:1.5b

# WAHA Configuration
WAHA_API_URL=http://localhost:3000
WAHA_API_KEY=your_api_key
ADMIN_WHATSAPP_NUMBER=your_number
```

## 🎯 Usage Examples

### Web Interface Workflow
1. Open http://localhost:5000
2. Check system status (all services should be green)
3. Drag a PDF file to the upload zone
4. AI analyzes the filename automatically
5. Confirm company/job information
6. Click upload
7. Receive WhatsApp notification when complete

### CLI Interface Workflow
1. Run `python cli_interface.py`
2. Select option 3 to process a single file
3. Choose from available files
4. AI analyzes the filename
5. Confirm or modify information
6. File is processed automatically
7. Check system status anytime with option 6

## 📱 Mobile Access

The web interface is mobile-responsive and can be accessed from:
- **Desktop**: Full functionality with drag-drop
- **Tablet**: Optimized touch interface
- **Mobile**: Simplified interface for essential functions

## 🚨 Troubleshooting

### Common Issues

1. **Services Not Connected**
   - Ensure Ollama is running: `docker ps` or check localhost:11434
   - Ensure WAHA is running: Check localhost:3000
   - Verify Google Drive credentials

2. **File Upload Fails**
   - Check file size (max 50MB)
   - Verify supported file types
   - Ensure watch folder exists

3. **WhatsApp Not Working**
   - Check WAHA session status
   - Verify phone number format
   - Ensure WhatsApp device is connected

4. **AI Analysis Fails**
   - Check Ollama model is installed
   - Verify model name in configuration
   - Test Ollama directly: `curl http://localhost:11434/api/tags`

### Getting Help
- Check system logs: `logs/legal_automation.log`
- Run configuration check: `python -m app.main --config-check`
- Test individual components with provided test scripts

## 📊 System Monitoring

### Status Indicators
- 🟢 **Green**: Service is online and functional
- 🔴 **Red**: Service is offline or has errors
- 🟡 **Yellow**: Service has warnings

### File Statistics
- Total files in watch folder
- Files processed today
- Active companies
- Notifications sent

### Real-time Updates
- System status refreshes every 30 seconds
- File list updates automatically
- Processing status shows in real-time

## 🎉 Enjoy Your Automated System!

The Legal Document Automation System is now ready to use with both beautiful web and powerful CLI interfaces. Choose the interface that works best for your workflow!