# Legal Document Automation System - Production Deployment

## 🚀 System Overview

**Production Ready Legal Document Automation System** with Indonesian WhatsApp notifications for missing documents.

### ✅ Features Ready for Production:
- **Automatic WhatsApp Notifications** in Indonesian format
- **Checklist Evaluation** for BG PIHK PT, BG PPIU PT, Laporan Keuangan
- **AI Document Classification** with OCR support
- **Real-time Processing** and automatic alerts
- **Web Dashboard** for management
- **Google Drive Integration** for document storage

## 📁 Production File Structure

```
automaton-arsip-dokumen+AI/
├── .claude/                           # Claude configuration (preserved)
├── .git/                              # Git repository
├── app/                               # Core application modules
├── templates/                         # HTML templates
├── final_web_app.py                   # Main web application
├── whatsapp_notifier.py               # WhatsApp notification system
├── start_production.py                # Production startup script
├── requirements.txt                   # Python dependencies
├── .env.production                    # Production environment config
├── credentials.json                   # Google Drive credentials
├── token.json                         # Google Drive auth token
├── README.md                          # Project documentation
├── LICENSE                            # License file
└── DEPLOYMENT.md                      # This deployment guide
```

## 🛠️ Deployment Steps

### 1. System Requirements
- Python 3.8+
- 4GB RAM minimum
- 10GB storage
- Docker (for WAHA WhatsApp integration)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure WhatsApp (WAHA)
```bash
# Clone and run WAHA for WhatsApp integration
git clone https://github.com/devlikeapro/waha.git
cd waha
docker-compose up -d

# Scan QR code with WhatsApp at http://localhost:3000
```

### 4. Configure Environment
```bash
# Copy and edit production configuration
cp .env.production .env

# Edit .env with your settings:
ADMIN_WHATSAPP_NUMBER=+628123456789  # Your WhatsApp number
WATCH_FOLDER=D:/Download Legalitas   # Document upload folder
```

### 5. Start Production Server
```bash
python start_production.py
```

Server will be available at: **http://localhost:5000**

## 📱 WhatsApp Message Format (Indonesian)

### Automatic Missing Documents Notification:
```
Dokumen Kekurangan BG PIHK PT PT INDONESIA MAJU per 16/10/2025

1. SKT / SKF (Fiskal)
2. Nomor Telepon Direktur dan Nama Ibu Kandung
3. Sertifikat Akreditasi PPIU
4. Lampiran Manifest 1000 Jamaah
```

## 🔧 Configuration Options

### Environment Variables:
- `ADMIN_WHATSAPP_NUMBER` - Target WhatsApp number
- `WATCH_FOLDER` - Document monitoring folder
- `WAHA_API_URL` - WAHA API endpoint
- `OLLAMA_MODEL` - AI model for document processing

### Checklist Types:
- **BG PIHK PT** (11 required documents)
- **BG PPIU PT** (9 required documents)
- **Laporan Keuangan** (15 required documents)

## 🔒 Security Considerations

1. **Google Drive Credentials**: Keep `credentials.json` secure
2. **Environment Variables**: Use strong, unique values
3. **Network**: Consider firewall rules for production
4. **HTTPS**: Use reverse proxy (nginx) for SSL

## 📊 Monitoring

### System Health:
- Web interface: http://localhost:5000
- WhatsApp status: Test notifications in web interface
- Document processing: Automatic background monitoring

### Logs:
- Application logs: Console output
- WhatsApp delivery: Real-time feedback
- Document processing: Automatic error reporting

## 🚨 Troubleshooting

### WhatsApp Not Working:
1. Check WAHA is running: http://localhost:3000
2. Verify WhatsApp is connected in WAHA interface
3. Test with web interface notification button

### Documents Not Processing:
1. Check WATCH_FOLDER path is correct
2. Verify file formats are supported
3. Check Google Drive authorization

### Server Not Starting:
1. Verify all required files are present
2. Check Python dependencies are installed
3. Ensure ports 5000 and 3000 are available

## 🔄 Maintenance

### Regular Tasks:
1. **Monitor WhatsApp** connectivity
2. **Update document** categories as needed
3. **Backup Google Drive** credentials
4. **Check system logs** for errors

### Updates:
1. **Update dependencies**: `pip install -r requirements.txt --upgrade`
2. **Restart services**: Stop and restart production server
3. **Test notifications**: Verify WhatsApp after updates

## 📞 Support

- **Web Interface**: http://localhost:5000
- **System Status**: Built-in health checks
- **WhatsApp**: Real-time delivery confirmation

---

## ✅ Deployment Complete!

Your Legal Document Automation System is now running in production mode with:
- **Indonesian WhatsApp notifications** automatically sent for missing documents
- **Real-time checklist evaluation** for legal document requirements
- **AI-powered document classification** and processing
- **Web dashboard** for management and monitoring

**Server Running**: http://localhost:5000
**WhatsApp Integration**: Ready (once WAHA is configured)
**Document Processing**: Active and monitoring

🎉 **System is ready for production use!**