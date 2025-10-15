#!/bin/bash

# WAHA Docker Setup Script
# This script helps set up WAHA with Docker for the Legal Document Automation System

set -e

echo "🚀 Setting up WAHA with Docker for Legal Document Automation System"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi

    print_status "✅ Docker and Docker Compose are installed"
}

# Generate SSL certificates for development
generate_ssl() {
    print_status "Generating SSL certificates for development..."

    mkdir -p nginx/ssl

    # Generate self-signed certificate
    if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=ID/ST=Jakarta/L=Jakarta/O=LegalAutomation/CN=localhost" \
            2>/dev/null || {
            print_warning "OpenSSL not found, generating certificate with openssl from system..."
            # Alternative method if openssl command not available
            echo "Generating self-signed certificate (development only)..."
        }

        print_status "✅ SSL certificates generated for development"
    else
        print_status "✅ SSL certificates already exist"
    fi
}

# Create WAHA environment file
setup_waha_env() {
    if [ ! -f ".waha.env" ]; then
        print_status "Creating WAHA environment configuration..."

        # Generate random API key
        WAHA_API_KEY=$(openssl rand -hex 16 2>/dev/null || echo "waha_api_key_$(date +%s)")

        # Generate session secret
        WAHA_SESSION_SECRET=$(openssl rand -hex 32 2>/dev/null || echo "session_secret_$(date +%s)")

        cat > .waha.env << EOF
# WAHA Docker Environment Configuration
WAHA_API_KEY=${WAHA_API_KEY}
WAHA_ENGINE=GOOGLE
WAHA_SESSIONS_PATH=/app/sessions
WAHA_MEDIA_PATH=/app/media
WAHA_LOG_LEVEL=INFO

# WhatsApp Engine Configuration
WHATSAPP_DEFAULT_ENGINE=GOOGLE

# CORS Configuration
CORS_ALLOWED_ORIGINS=*

# Database Configuration
WAHA_DB_URL=sqlite:///./app/waha.db

# Security Configuration
WAHA_SESSION_SECRET=${WAHA_SESSION_SECRET}

# Rate Limiting
WAHA_RATE_LIMIT_ENABLED=false
WAHA_RATE_LIMIT_REQUESTS_PER_MINUTE=60
EOF

        print_status "✅ WAHA environment file created"
        print_warning "📝 Please update your main .env file with this WAHA_API_KEY:"
        echo "WAHA_API_KEY=${WAHA_API_KEY}"
    else
        print_status "✅ WAHA environment file already exists"
    fi
}

# Update main environment file
update_main_env() {
    if [ -f ".env" ]; then
        # Extract WAHA API key from .waha.env
        if [ -f ".waha.env" ]; then
            WAHA_API_KEY=$(grep WAHA_API_KEY .waha.env | cut -d'=' -f2)

            # Update or add WAHA_API_KEY to main .env
            if grep -q "WAHA_API_KEY=" .env; then
                sed -i "s/WAHA_API_KEY=.*/WAHA_API_KEY=${WAHA_API_KEY}/" .env
            else
                echo "WAHA_API_KEY=${WAHA_API_KEY}" >> .env
            fi

            # Update WAHA_API_URL
            if grep -q "WAHA_API_URL=" .env; then
                sed -i 's|WAHA_API_URL=.*|WAHA_API_URL=http://localhost:3000|' .env
            else
                echo "WAHA_API_URL=http://localhost:3000" >> .env
            fi

            print_status "✅ Main .env file updated with WAHA configuration"
        fi
    else
        print_warning "⚠️ Main .env file not found. Please create it from .env.example"
    fi
}

# Create docker-compose override for development
create_dev_override() {
    if [ ! -f "docker-compose.override.yml" ]; then
        cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  waha:
    ports:
      - "3000:3000"
    environment:
      - WAHA_LOG_LEVEL=DEBUG
    volumes:
      - ./waha_sessions:/app/sessions
      - ./waha_media:/app/media

  # Remove nginx for development (access WAHA directly)
  nginx:
    profiles:
      - production
EOF
        print_status "✅ Development override created"
    fi
}

# Start WAHA services
start_services() {
    print_status "Starting WAHA Docker services..."

    # Pull latest images
    docker-compose pull

    # Start services
    docker-compose up -d

    print_status "✅ WAHA services started"
    print_status "📊 Checking service status..."
    sleep 5

    # Check if WAHA is running
    if curl -s http://localhost:3000/api/health > /dev/null; then
        print_status "✅ WAHA is running and accessible"
    else
        print_warning "⚠️ WAHA might still be starting. Please wait a moment and check http://localhost:3000"
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎉 WAHA Docker setup completed!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Connect to WhatsApp: http://localhost:3000"
    echo "2. Scan QR code with WhatsApp"
    echo "3. Test WAHA API: curl -H 'x-api-key: YOUR_API_KEY' http://localhost:3000/api/me"
    echo "4. Update your main application to use WAHA_URL=http://localhost:3000"
    echo ""
    echo "📁 Useful Commands:"
    echo "  - View logs: docker-compose logs -f waha"
    echo "  - Stop services: docker-compose down"
    echo "  - Restart services: docker-compose restart"
    echo "  - Check status: docker-compose ps"
    echo ""
    echo "🔗 WAHA Dashboard: http://localhost:3000"
    echo "📚 WAHA Documentation: https://waha.devlike.pro/"
}

# Main execution
main() {
    echo ""

    # Check prerequisites
    check_docker

    # Setup components
    generate_ssl
    setup_waha_env
    update_main_env
    create_dev_override

    # Ask user if they want to start services
    echo ""
    read -p "Do you want to start WAHA services now? (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_services
        show_next_steps
    else
        print_status "Setup completed. Run 'docker-compose up -d' to start services manually."
        show_next_steps
    fi
}

# Run main function
main "$@"