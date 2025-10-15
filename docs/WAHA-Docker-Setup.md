# WAHA Docker Setup Guide

Guide lengkap untuk setup WAHA (WhatsApp HTTP API) menggunakan Docker untuk Legal Document Automation System.

## 🐋 Docker Setup (Recommended)

Docker setup adalah metode yang disarankan karena:
- ✅ Konsisten di semua platform
- ✅ Mudah diinstall dan konfigurasi
- ✅ Otomatis handle dependencies
- ✅ Persistent data dengan volumes
- ✅ Mudah backup dan restore

## 📋 Prerequisites

1. **Docker Desktop** (Windows/Mac) atau **Docker Engine** (Linux)
2. **Docker Compose** (biasanya sudah termasuk di Docker Desktop)
3. Port 3000, 6379, 80, 443 harus tersedia

## 🚀 Quick Start

### Windows
```cmd
# Jalankan setup script otomatis
.\scripts\setup-waha-docker.bat
```

### Linux/Mac
```bash
# Jalankan setup script otomatis
chmod +x scripts/setup-waha-docker.sh
./scripts/setup-waha-docker.sh
```

Setup script akan:
- ✅ Check Docker installation
- ✅ Generate SSL certificates
- ✅ Create environment configuration
- ✅ Update main .env file
- ✅ Start WAHA services
- ✅ Show next steps

## 🔧 Manual Setup

### 1. Environment Configuration

Copy dan edit environment file:
```bash
cp .waha.env.example .waha.env
```

Edit `.waha.env`:
```env
WAHA_API_KEY=your_secure_api_key_here
WAHA_ENGINE=GOOGLE
WAHA_LOG_LEVEL=INFO

# WhatsApp Configuration
WHATSAPP_DEFAULT_ENGINE=GOOGLE

# Security
WAHA_SESSION_SECRET=your_session_secret_here
```

### 2. Start Services

```bash
# Pull latest images
docker-compose pull

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Connect WhatsApp

1. Buka browser: http://localhost:3000
2. Scan QR code dengan WhatsApp
3. Tunggu hingga connection established

### 4. Test API

```bash
# Test dengan API key
curl -H "x-api-key: YOUR_API_KEY" http://localhost:3000/api/me

# Test health check
curl http://localhost:3000/api/health
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80)    │───▶│   WAHA (3000)   │───▶│   Redis (6379)  │
│  Reverse Proxy  │    │  WhatsApp API   │    │     Cache       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
    SSL/HTTPS              Sessions/Media           Data Storage
```

## 📁 Docker Volumes

- `waha_sessions`: WhatsApp session data
- `waha_media`: Media files (images, documents)
- `waha_data`: Application data
- `redis_data`: Redis cache data
- `nginx_logs`: Nginx access/error logs

## 🔧 Configuration Details

### WAHA Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WAHA_API_KEY` | API authentication key | Auto-generated |
| `WAHA_ENGINE` | WhatsApp engine type | GOOGLE |
| `WAHA_LOG_LEVEL` | Logging verbosity | INFO |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | * |
| `WAHA_DB_URL` | Database connection | SQLite |
| `WAHA_RATE_LIMIT_ENABLED` | Enable rate limiting | false |

### Docker Services

#### WAHA Service
- **Image**: `devlikeapro/waha`
- **Port**: 3000
- **Health Check**: `/api/health`
- **Restart Policy**: unless-stopped

#### Redis Service
- **Image**: `redis:7-alpine`
- **Port**: 6379
- **Persistence**: Enabled
- **Restart Policy**: unless-stopped

#### Nginx Service
- **Image**: `nginx:alpine`
- **Ports**: 80, 443
- **SSL**: Self-signed certificates
- **Reverse Proxy**: WAHA + Redis

## 🔍 Troubleshooting

### Common Issues

#### 1. WAHA Container Not Starting
```bash
# Check logs
docker-compose logs waha

# Check if port is available
netstat -an | findstr 3000

# Restart services
docker-compose restart waha
```

#### 2. WhatsApp Connection Failed
```bash
# Check WAHA logs for connection errors
docker-compose logs -f waha

# Verify WAHA is accessible
curl http://localhost:3000/api/health

# Restart WAHA service
docker-compose restart waha
```

#### 3. SSL Certificate Issues
```bash
# Regenerate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=ID/ST=Jakarta/L=Jakarta/O=LegalAutomation/CN=localhost"

# Restart Nginx
docker-compose restart nginx
```

#### 4. Permission Issues
```bash
# Check volume permissions
docker-compose exec waha ls -la /app/sessions

# Fix permissions (if needed)
sudo chown -R 1000:1000 ./waha_sessions
sudo chown -R 1000:1000 ./waha_media
```

### Debug Commands

```bash
# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f waha
docker-compose logs -f nginx
docker-compose logs -f redis

# Execute commands in container
docker-compose exec waha bash
docker-compose exec redis redis-cli

# Check container status
docker-compose ps

# Inspect container
docker-compose inspect waha
```

## 🔐 Security Configuration

### Production Setup

Untuk production, tambahkan konfigurasi berikut:

#### 1. Environment Variables
```env
# Production WAHA configuration
WAHA_LOG_LEVEL=WARNING
WAHA_RATE_LIMIT_ENABLED=true
WAHA_RATE_LIMIT_REQUESTS_PER_MINUTE=30
CORS_ALLOWED_ORIGINS=https://yourdomain.com
WAHA_SESSION_SECRET=very_secure_random_string_here
```

#### 2. SSL Certificates
```bash
# Use production SSL certificates
# Let's Encrypt atau commercial certificates
cp /path/to/production/cert.pem nginx/ssl/cert.pem
cp /path/to/production/key.pem nginx/ssl/key.pem
```

#### 3. Firewall Configuration
```bash
# Allow only necessary ports
# - 80: HTTP (redirect to HTTPS)
# - 443: HTTPS
# - 3000: WAHA (internal only)
```

## 📊 Monitoring

### Health Checks

```bash
# WAHA health check
curl http://localhost:3000/api/health

# System health check
curl http://localhost/health

# Docker health status
docker-compose ps
```

### Log Monitoring

```bash
# Monitor all logs
docker-compose logs -f

# Monitor specific patterns
docker-compose logs -f waha | grep ERROR
docker-compose logs -f waha | grep "WhatsApp"
```

## 🔄 Backup & Restore

### Backup Data
```bash
# Backup WAHA data
docker run --rm -v waha_sessions:/data -v $(pwd):/backup alpine tar czf /backup/waha_sessions_backup.tar.gz -C /data .

# Backup Redis data
docker run --rm -v redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .

# Backup configuration
cp .waha.env .waha.env.backup
cp docker-compose.yml docker-compose.yml.backup
```

### Restore Data
```bash
# Restore WAHA data
docker run --rm -v waha_sessions:/data -v $(pwd):/backup alpine tar xzf /backup/waha_sessions_backup.tar.gz -C /data

# Stop and restart services
docker-compose down
docker-compose up -d
```

## 🚀 Scaling

### High Availability Setup

Untuk production dengan high availability:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  waha:
    image: devlikeapro/waha
    deploy:
      replicas: 2
    environment:
      - WAHA_REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    deploy:
      replicas: 1

  nginx:
    image: nginx:alpine
    deploy:
      replicas: 1
    depends_on:
      - waha
```

## 📚 API Usage

### Send Message
```bash
curl -X POST http://localhost:3000/api/sendText \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver": "6281234567890",
    "message": "Hello from WAHA!"
  }'
```

### Check Status
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  http://localhost:3000/api/sessions/default/status
```

## 🔗 Links

- [WAHA Documentation](https://waha.devlike.pro/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/)

---

**🤖 Generated with Claude Code**

*AI-powered legal document automation system*