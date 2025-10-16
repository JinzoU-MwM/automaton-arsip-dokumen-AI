# WAHA 401 Unauthorized Error - Quick Fix

## ❌ Error: WAHA API error: 401 - {"message":"Unauthorized","statusCode":401}

This error means WAHA API is rejecting requests. Here are the solutions:

## 🔧 Solution 1: Check if WAHA is Running

```bash
# Check if WAHA is running
curl http://localhost:3000/api/sessions
```

If you get connection refused, WAHA is not running.

## 🚀 Solution 2: Start WAHA (Recommended Method)

### Option A - Docker (Easiest)
```bash
# Create WAHA directory
mkdir waha && cd waha

# Create docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  waha:
    image: devlikeapro/waha
    ports:
      - "3000:3000"
    environment:
      - WAHA_API_KEY=berhasil123
    volumes:
      - ./sessions:/app/sessions
EOF

# Start WAHA
docker-compose up -d
```

### Option B - Without Docker
```bash
# Install Node.js dependencies
npm install -g @waha/waha

# Start WAHA
waha serve --port 3000
```

## 📱 Solution 3: Connect WhatsApp

1. **Open WAHA Interface**: http://localhost:3000
2. **Scan QR Code** with WhatsApp:
   - Open WhatsApp on phone
   - Settings > Linked Devices
   - Scan QR code
3. **Verify Session**: Look for "WORKING" status

## 🔑 Solution 4: Configure API Key

WAHA might require API key. The system is configured to use: `berhasil123`

Update your WAHA environment:
```bash
# For Docker - Add to docker-compose.yml
environment:
  - WAHA_API_KEY=berhasil123

# For manual start
export WAHA_API_KEY=berhasil123
waha serve --port 3000
```

## 🧪 Solution 5: Test the Fix

After WAHA is running, test with:
```bash
curl http://localhost:3000/api/sessions
```

Should return something like:
```json
[{"id":"session1","status":"WORKING","phone":"+628123456789"}]
```

## 🔄 Test in Your System

1. Go to http://localhost:5000
2. Click "Test Notification"
3. Should show success message

## 📋 Complete Working Setup

```bash
# 1. Start WAHA with API key
cd waha
docker-compose up -d

# 2. Verify WAHA is running
curl http://localhost:3000/api/sessions

# 3. Connect WhatsApp (scan QR at localhost:3000)

# 4. Test notifications in your web interface
```

## ✅ Expected Result

Once fixed, WhatsApp notifications will work:
```
Dokumen Kekurangan BG PIHK PT PT CONTOH INDONESIA per 16/10/2025

1. SKT / SKF (Fiskal)
2. Nomor Telepon Direktur dan Nama Ibu Kandung
3. Sertifikat Akreditasi PPIU
4. Lampiran Manifest 1000 Jamaah
```

## 🆘 If Still Not Working

1. **Check WAHA logs**: `docker-compose logs waha`
2. **Verify port 3000**: `netstat -an | grep 3000`
3. **Restart WAHA**: `docker-compose restart`
4. **Contact support**: WAHA GitHub issues

---

**Your system is configured correctly - just need to start WAHA properly!**