"""
Clean up project for GitHub repository
Remove sensitive and temporary files
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up project for GitHub upload"""

    print("Cleaning up project for GitHub...")

    # Files to remove (sensitive or temporary)
    files_to_remove = [
        'credentials.json',  # OAuth credentials - sensitive
        'token.json',        # OAuth tokens - sensitive
        '.env',              # Environment variables - sensitive
        'service_account.json',  # Service account credentials - sensitive
        'service-automaton.json',  # Service account credentials - sensitive
        '.waha.env',         # WAHA environment - sensitive
        'debug_file_selection.py',  # Debug script
        'debug_google_drive.py',   # Debug script
        'setup_oauth.py',           # Setup script
        'setup_shared_drive.py',   # Setup script
        'enable_oauth.py',          # Update script
        'OAUTH_SETUP.md',           # Temporary setup guide
        'OAUTH_COMPLETE.md',        # Temporary completion guide
        'QUICK_FIX.md',             # Temporary fix guide
        'test_basic.py',            # Test scripts
        'test_simple.py',           # Test scripts
        'test_file_processing.py',  # Test scripts
        'requirements_ui.txt',      # Duplicate requirements
    ]

    # Directories to remove
    dirs_to_remove = [
        'temp_uploads',      # Temporary upload directory
        'logs',              # Log files
        '.claude',           # Claude cache
        '__pycache__',       # Python cache
    ]

    # Remove files
    removed_files = 0
    for file_name in files_to_remove:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"   [REMOVED] {file_name}")
                removed_files += 1
            except Exception as e:
                print(f"   [ERROR] Could not remove {file_name}: {e}")

    # Remove directories
    removed_dirs = 0
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"   [REMOVED] {dir_name}/")
                removed_dirs += 1
            except Exception as e:
                print(f"   [ERROR] Could not remove {dir_name}: {e}")

    # Remove Python cache files recursively
    python_cache_removed = 0
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in root:
            continue

        for file in files:
            if file.endswith('.pyc') or file.endswith('.pyo'):
                try:
                    os.remove(os.path.join(root, file))
                    python_cache_removed += 1
                except:
                    pass

    if python_cache_removed > 0:
        print(f"   [REMOVED] {python_cache_removed} Python cache files")

    print(f"\n[SUCCESS] Cleanup complete!")
    print(f"   Files removed: {removed_files}")
    print(f"   Directories removed: {removed_dirs}")
    print(f"   Cache files removed: {python_cache_removed}")

def create_github_readme():
    """Create GitHub README"""

    readme_content = """# 🤖 Legal Document Automation System

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
"""

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("   [CREATED] GitHub README.md")

def create_gitignore():
    """Create .gitignore file"""

    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment Variables
.env
credentials.json
token.json
service_account.json
service-automaton.json
.waha.env

# Logs
logs/
*.log

# Temporary Files
temp_uploads/
temp/
.tmp/

# OS
.DS_Store
Thumbs.db
Desktop.ini

# Cache
.cache/
.pytest_cache/

# Claude
.claude/
"""

    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)

    print("   [CREATED] .gitignore")

def create_license():
    """Create MIT license"""

    license_content = """MIT License

Copyright (c) 2025 Legal Document Automation System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    with open('LICENSE', 'w') as f:
        f.write(license_content)

    print("   [CREATED] LICENSE")

def main():
    """Main cleanup function"""
    print("Preparing Legal Document Automation System for GitHub")
    print("=" * 60)

    cleanup_project()
    print()
    create_github_readme()
    create_gitignore()
    create_license()

    print("\n" + "=" * 60)
    print("[SUCCESS] Project ready for GitHub!")
    print("=" * 60)
    print("Next steps:")
    print("1. Initialize Git repository:")
    print("   git init")
    print("2. Add files:")
    print("   git add .")
    print("3. Commit changes:")
    print("   git commit -m 'Initial commit: Legal Document Automation System'")
    print("4. Create GitHub repository: automaton-arsip-dev")
    print("5. Push to GitHub:")
    print("   git remote add origin https://github.com/yourusername/automaton-arsip-dev.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print()
    print("Your project is ready to share with the world!")

if __name__ == "__main__":
    main()