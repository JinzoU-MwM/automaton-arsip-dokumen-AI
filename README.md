# 🤖 Legal Document Automation System

AI-powered system for automated legal document processing with Google Drive integration and WhatsApp notifications.

## ✨ Features

- 🤖 **AI-Powered Analysis**: Automatically extracts company and job information from document names
- 📁 **Smart File Organization**: Creates company folders with categorized subfolders
- 📤 **Google Drive Integration**: Uploads documents to appropriate folders automatically
- 📱 **WhatsApp Notifications**: Real-time alerts via WAHA API
- 📊 **Document Completeness Tracking**: Monitors required documents for each company
- 🌐 **Web Interface**: Beautiful drag-and-drop dashboard
- 💻 **CLI Interface**: Powerful command-line interface
- 🔍 **File Monitoring**: Automatic processing of new files

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Ollama AI (with qwen2:1.5b model)
- WAHA WhatsApp API
- Google Drive API access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/automaton-arsip-dev.git
   cd automaton-arsip-dev
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama**
   ```bash
   # Install Ollama (if not already installed)
   # Pull the required model
   ollama pull qwen2:1.5b
   ```

4. **Set up WAHA**
   ```bash
   # Using Docker (recommended)
   docker-compose up -d
   ```

5. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Set up Google Drive OAuth**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Enable Google Drive API
   - Create OAuth credentials (Desktop app)
   - Download `credentials.json` to project root
   - Run the system to authenticate

### Usage

#### Web Interface (Recommended)
```bash
python start.py --interface web
# Open http://localhost:5000
```

#### CLI Interface
```bash
python cli_interface.py
```

#### Direct Commands
```bash
# Monitor folder for new files
python -m app.main --mode monitor

# Process existing files
python -m app.main --mode process-existing

# Process specific file
python -m app.main --file "path/to/document.pdf"

# Interactive mode
python -m app.main --mode interactive
```

## 📁 Project Structure

```
automaton-arsip-dev/
├── app/                    # Core application modules
│   ├── ai_parser.py       # AI document analysis
│   ├── drive_manager.py   # Google Drive operations
│   ├── notifier.py        # WhatsApp notifications
│   ├── watcher.py         # File monitoring
│   ├── config.py          # Configuration management
│   └── main.py            # Main orchestrator
├── templates/              # Web interface templates
├── scripts/               # Setup and utility scripts
├── docs/                  # Documentation
├── docker-compose.yml     # WAHA Docker setup
├── start.py              # Startup script
├── cli_interface.py      # Enhanced CLI
├── web_app.py            # Web application
└── requirements.txt      # Python dependencies
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Folder Configuration
WATCH_FOLDER=D:/Source File

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

### Document Categories

The system automatically categorizes documents based on filename patterns:
- **Akta**: akta, pendirian, perubahan
- **NIB**: nib, nomor induk berusaha
- **NPWP**: npwp, nomor pokok wajib pajak
- **KTP Pengurus**: ktp, pengurus
- **IATA**: iata, iata license
- **Pajak**: pajak, perpajakan
- **Bank Garansi**: bank garansi, guarantee

## 🌐 Web Interface

Features a modern, responsive web dashboard with:
- 📊 Real-time system status
- 🎯 Drag-and-drop file upload
- 🤖 AI text analysis
- 📁 File management
- 📱 WhatsApp notifications
- 📈 Statistics dashboard

## 💻 CLI Interface

Powerful command-line interface with:
- 🎨 Colored menu system
- 📁 Interactive file selection
- 🤖 AI-powered analysis
- 📊 Real-time monitoring
- 🔍 Document completeness checking

## 📱 WhatsApp Notifications

Automated WhatsApp notifications for:
- ✅ Successful file uploads
- ⚠️ Processing errors
- 📊 Document completeness updates
- 🚨 System alerts

## 🔍 Document Categories

The system automatically detects document types from filenames:
- Legal documents (Akta, NIB, NPWP)
- Business licenses (IATA, SIUP)
- Financial documents (Pajak, Bank Garansi)
- Personal documents (KTP Pengurus)

## 🛠️ Development

### Running Tests
```bash
# Test individual components
python -m app.ai_parser
python -m app.drive_manager
python -m app.notifier
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m app.main --mode interactive
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `/docs` folder
- Review the configuration examples

---

**Made with ❤️ for automating legal document workflows**
