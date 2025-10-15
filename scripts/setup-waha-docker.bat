@echo off
REM WAHA Docker Setup Script for Windows
REM This script helps set up WAHA with Docker for the Legal Document Automation System

echo 🚀 Setting up WAHA with Docker for Legal Document Automation System
echo ================================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo Visit: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are installed

REM Create directories
if not exist "nginx\ssl" mkdir nginx\ssl
if not exist "waha_sessions" mkdir waha_sessions
if not exist "waha_media" mkdir waha_media

REM Generate SSL certificates (if OpenSSL is available)
openssl version >nul 2>&1
if %errorlevel% equ 0 (
    echo Generating SSL certificates for development...
    if not exist "nginx\ssl\cert.pem" (
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx\ssl\key.pem -out nginx\ssl\cert.pem -subj "/C=ID/ST=Jakarta/L=Jakarta/O=LegalAutomation/CN=localhost" >nul 2>&1
        if %errorlevel% equ 0 (
            echo ✅ SSL certificates generated
        ) else (
            echo ⚠️ Could not generate SSL certificates, but continuing...
        )
    ) else (
        echo ✅ SSL certificates already exist
    )
) else (
    echo ⚠️ OpenSSL not found, SSL certificates will be generated automatically by Docker
)

REM Create WAHA environment file if it doesn't exist
if not exist ".waha.env" (
    echo Creating WAHA environment configuration...

    REM Generate random API key (simple method for Windows)
    set /a rand1=%random% %% 10000
    set /a rand2=%random% %% 10000
    set WAHA_API_KEY=waha_api_key_%rand1%_%rand2%

    REM Generate session secret
    set /a rand3=%random% %% 100000
    set WAHA_SESSION_SECRET=session_secret_%rand3%

    (
        echo # WAHA Docker Environment Configuration
        echo WAHA_API_KEY=%WAHA_API_KEY%
        echo WAHA_ENGINE=GOOGLE
        echo WAHA_SESSIONS_PATH=/app/sessions
        echo WAHA_MEDIA_PATH=/app/media
        echo WAHA_LOG_LEVEL=INFO
        echo.
        echo # WhatsApp Engine Configuration
        echo WHATSAPP_DEFAULT_ENGINE=GOOGLE
        echo.
        echo # CORS Configuration
        echo CORS_ALLOWED_ORIGINS=*
        echo.
        echo # Database Configuration
        echo WAHA_DB_URL=sqlite:///./app/waha.db
        echo.
        echo # Security Configuration
        echo WAHA_SESSION_SECRET=%WAHA_SESSION_SECRET%
        echo.
        echo # Rate Limiting
        echo WAHA_RATE_LIMIT_ENABLED=false
        echo WAHA_RATE_LIMIT_REQUESTS_PER_MINUTE=60
    ) > .waha.env

    echo ✅ WAHA environment file created
    echo 📝 Please update your main .env file with this WAHA_API_KEY:
    echo WAHA_API_KEY=%WAHA_API_KEY%
) else (
    echo ✅ WAHA environment file already exists
)

REM Update main environment file if it exists
if exist ".env" (
    echo ✅ Updating main .env file with WAHA configuration...

    REM Extract WAHA API key from .waha.env (simple method)
    for /f "tokens=2 delims==" %%a in ('findstr "WAHA_API_KEY" .waha.env') do set WAHA_KEY=%%a

    REM Add WAHA configuration to .env if not present
    findstr /C:"WAHA_API_KEY=" .env >nul 2>&1
    if %errorlevel% neq 0 (
        echo WAHA_API_KEY=%WAHA_KEY% >> .env
        echo WAHA_API_URL=http://localhost:3000 >> .env
        echo ✅ Added WAHA configuration to .env
    ) else (
        echo ✅ WAHA configuration already exists in .env
    )
) else (
    echo ⚠️ Main .env file not found. Please create it from .env.example
)

REM Create development override
if not exist "docker-compose.override.yml" (
    echo Creating development override...
    (
        echo version: '3.8'
        echo.
        echo services:
        echo   waha:
        echo     ports:
        echo       - "3000:3000"
        echo     environment:
        echo       - WAHA_LOG_LEVEL=DEBUG
        echo     volumes:
        echo       - ./waha_sessions:/app/sessions
        echo       - ./waha_media:/app/media
        echo.
        echo   # Remove nginx for development ^(access WAHA directly^)
        echo   nginx:
        echo     profiles:
        echo       - production
    ) > docker-compose.override.yml
    echo ✅ Development override created
)

REM Ask user if they want to start services
echo.
set /p start_services="Do you want to start WAHA services now? (y/N): "

if /i "%start_services%"=="y" (
    echo.
    echo Starting WAHA Docker services...

    REM Pull latest images
    docker-compose pull

    REM Start services
    docker-compose up -d

    echo ✅ WAHA services started
    echo 📊 Waiting for services to be ready...
    timeout /t 10 /nobreak >nul

    echo.
    echo 🎉 WAHA Docker setup completed!
    echo.
    echo 📋 Next Steps:
    echo 1. Connect to WhatsApp: http://localhost:3000
    echo 2. Scan QR code with WhatsApp
    echo 3. Test WAHA API: curl -H "x-api-key: YOUR_API_KEY" http://localhost:3000/api/me
    echo 4. Update your main application to use WAHA_URL=http://localhost:3000
    echo.
    echo 📁 Useful Commands:
    echo   - View logs: docker-compose logs -f waha
    echo   - Stop services: docker-compose down
    echo   - Restart services: docker-compose restart
    echo   - Check status: docker-compose ps
    echo.
    echo 🔗 WAHA Dashboard: http://localhost:3000
    echo 📚 WAHA Documentation: https://waha.devlike.pro/
) else (
    echo.
    echo ✅ Setup completed. Run 'docker-compose up -d' to start services manually.
    echo 📋 Next Steps:
    echo 1. Start services: docker-compose up -d
    echo 2. Connect to WhatsApp: http://localhost:3000
    echo 3. Scan QR code with WhatsApp
    echo.
    echo 🔗 WAHA Dashboard: http://localhost:3000
)

echo.
pause